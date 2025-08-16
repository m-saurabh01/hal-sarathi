from __future__ import annotations
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import csv
import io
from typing import List, Dict
from app.services.auth import get_admin
from app.services.data import DataService
from app.routers.public import set_data

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
async def admin_ui(_: str = Depends(get_admin)):
    html = Path("app/templates/admin.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@router.post("/admin/upload")
async def admin_upload(file: UploadFile = File(...), _: str = Depends(get_admin)):
    # Minimal CSV handling; XLSX could be added later with pandas/openpyxl if needed
    name = file.filename or ""
    content = await file.read()
    rows: List[Dict[str, str]] = []

    if name.lower().endswith(".csv"):
        txt = content.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(txt))
        rows = list(reader)
    elif name.lower().endswith(".xlsx"):
        try:
            from openpyxl import load_workbook
        except Exception as e:
            return JSONResponse({"error": "XLSX support not available. Please install openpyxl."}, status_code=400)
        wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        data_iter = ws.iter_rows(values_only=True)
        try:
            header = next(data_iter)
        except StopIteration:
            header = []
        header = [str(h or '').strip().lower() for h in header]
        rows = []
        for r in data_iter:
            row = {header[i]: ('' if v is None else str(v)) for i, v in enumerate(r) if i < len(header)}
            rows.append(row)
    else:
        return JSONResponse({"error": "Unsupported file type. Please upload .csv or .xlsx."}, status_code=400)

    items, stats, errors = DataService.upsert_from_rows(rows)
    if errors:
        return JSONResponse({"errors": errors}, status_code=400)

    DataService.save_kb(items)
    set_data()  # hot-reload
    return JSONResponse({"status": "ok", "stats": stats})


@router.get("/admin/unmatched", response_class=HTMLResponse)
async def admin_unmatched(_: str = Depends(get_admin)):
        p = Path("data/unmatched.csv")
        if not p.exists():
                return HTMLResponse("<div class='container py-4'><div class='alert alert-secondary'>No unmatched queries yet.</div></div>")
        # Light HTML wrapper for readability in browser
        body = p.read_text(encoding="utf-8")
        html = f"""
        <!doctype html><html lang='en'>
        <head>
            <meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
            <title>Unmatched CSV</title>
            <link href='/Users/SA20464227/Downloads/OfflineChatbot/app/static/css/bootstrap.min.css' rel='stylesheet'>
        </head>
        <body class='container py-3'>
            <h1 class='h4 mb-3'>Unmatched Queries (CSV)</h1>
            <pre class='p-3 border rounded bg-light' style='white-space:pre-wrap'>{body}</pre>
        </body></html>
        """
        return HTMLResponse(html)
