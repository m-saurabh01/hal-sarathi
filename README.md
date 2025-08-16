# Offline Chatbot (Lightweight)

A minimal FastAPI app with two frontends (user + admin), semantic-ish matching via BM25+fuzzy, admin CSV upload, and unmatched logging.

## Features
- User chat UI (no JS frameworks)
- Admin dashboard with CSV upload and unmatched viewer
- Matching: exact + keywords + BM25-style + RapidFuzz blend
- Unmatched logging to `data/unmatched.csv`
- Security headers and same-origin CORS

## Run

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 for user UI.
Open http://127.0.0.1:8000/admin (HTTP Basic: admin/admin123) for admin.

## Upload format
CSV with headers: `id,question,answer,keywords,tags`
- keywords: semicolon-separated
- tags: semicolon-separated

## Notes
- To keep it lightweight we support CSV only. Export Excel as CSV.
- Set ADMIN_USER and ADMIN_PASS env vars to change admin credentials.
