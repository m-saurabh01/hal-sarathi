from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
import uvicorn

from app.routers.public import router as public_router
from app.routers.admin import router as admin_router

app = FastAPI(title="Offline Chatbot", version="2.0")

# CORS: Allow all origins for widget embedding (widget.js calls /ask from external sites)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    # Content Security Policy: self-hosted assets only; allow inline styles used in templates
    resp.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    return resp

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(public_router)
app.include_router(admin_router)

@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "ok"

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
