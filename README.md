# Offline Chatbot

A lightweight, offline-first Q&A chatbot built with FastAPI. It ships with:

- A user-friendly chat UI (Bootstrap + vanilla JS)
- An admin dashboard for uploading/updating a knowledge base (CSV/XLSX)
- A local matching engine (BM25-ish + fuzzy, optional semantic embeddings)
- Privacy-minded logging of unmatched questions to improve coverage

This document explains what the app does and provides a complete setup guide for a fully offline PC. For deep architecture docs, file-by-file explanations, and API references, see the Developer Guide:

→ Developer Guide: [DEV.md](./DEV.md)

---

## What it does

1) You upload a knowledge base (KB) of questions and answers in CSV or Excel (.xlsx). Each row has a question, answer, and optional keywords/tags.

2) The user asks a question in the web UI. The backend computes similarity using keywords, BM25-style lexical scoring, fuzzy matching (RapidFuzz), and (optionally) local semantic embeddings. It returns a reply and relevant suggestions when confidence is moderate.

3) If there’s no good match, the anonymous, sanitized query goes to `data/unmatched.csv` so you can enrich the KB later.

---

## Fully offline setup (macOS/Windows/Linux)

Prereqs (no Internet required after you have these files locally):
- Python 3.10+ installer or preinstalled Python
- This repository (source code)
- Python wheels for dependencies (optional but recommended for zero-Internet install)
- Optional: local sentence-transformers model folder if you want semantic matching (we include a MiniLM layout example)

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows PowerShell
```

### 2) Install dependencies

Offline option A (modern pip can install from local wheels):
```bash
pip install --no-index --find-links ./wheels -r requirements.txt
```

Online or pre-cached option:
```bash
pip install -r requirements.txt
```

### 3) Optional: local semantic embeddings

If you have a local model directory (e.g., `all-MiniLM-L6-v2-optimized/`), the app will try to load it. If missing, it runs in lexical/fuzzy mode only—no network calls are made.

### 4) Start the app

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open:
- User UI: http://127.0.0.1:8000/
- Admin UI: http://127.0.0.1:8000/admin

Default admin credentials: `admin` / `admin123` (set ADMIN_USER/ADMIN_PASS to change).

---

## Upload format

Headers (case-insensitive):
- Required: `question`, `answer`
- Optional: `id`, `keywords`, `tags`

Notes:
- keywords/tags support semicolons or commas (e.g., `reset; password, login`).
- When `id` is omitted, it is derived from the question. Repeated questions in the same sheet are auto-deduplicated (last wins; keywords/tags merged). If you need distinct entries, supply unique `id`s.
- Uploading creates a timestamped backup of `data/data.json` in `data/backups/` and hot-reloads the KB.

---

## Security & privacy

- Strict same-origin CORS, security headers, and CSP (adjusted to allow Bootstrap CDN unless you self-host it).
- No outbound network calls at runtime (semantic model loads locally if present).
- Unmatched logs are sanitized to remove emails/phone numbers before writing to `data/unmatched.csv`.

---

## Troubleshooting

- Blank page in embedded browser: hard refresh, or open in your default browser.
- No matches: check `data/data.json` format and ensure `question`/`answer` values exist.
- XLSX upload error: ensure openpyxl is installed; otherwise export as CSV.

For implementation details and extension points, see the Developer Guide → [DEV.md](./DEV.md).
