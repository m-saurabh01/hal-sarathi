# HAL Sarathi Chatbot

A lightweight, offline-first Q&A chatbot built with FastAPI. Features an **embeddable widget** that can be added to any website with a single script tag.

## Features

- 🔌 **Embeddable Widget** – Drop-in `<hal-chatbot>` custom element with Shadow DOM isolation
- 🛠️ **Admin Dashboard** – Upload/manage knowledge base via CSV/XLSX
- 🔍 **Smart Matching** – BM25 + fuzzy matching + optional semantic embeddings
- 🔒 **Privacy-First** – Fully offline, no external API calls
- 📝 **Markdown Support** – Bot responses support bold, italic, code, links, and lists
- ✨ **Modern UX** – Typewriter effect, breathing animation, greeting bubble

---

## Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 2. Start the Server

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

### 3. Access the App

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Widget demo page |
| http://127.0.0.1:8000/admin | Admin dashboard |

Default admin credentials: `admin` / `admin123` (set `ADMIN_USER`/`ADMIN_PASS` env vars to change).

---

## Embedding the Widget

Add the chatbot to any website with two lines of HTML:

```html
<script src="https://your-server.com/static/js/widget.js"></script>
<hal-chatbot endpoint="https://your-server.com"></hal-chatbot>
```

### Widget Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `endpoint` | Yes | Base URL of your HAL Sarathi server |

### Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>My Website</title>
</head>
<body>
  <h1>Welcome to My Site</h1>
  
  <!-- HAL Sarathi Chatbot Widget -->
  <script src="http://127.0.0.1:8000/static/js/widget.js"></script>
  <hal-chatbot endpoint="http://127.0.0.1:8000"></hal-chatbot>
</body>
</html>
```

The widget appears as a floating button in the bottom-right corner with:
- Breathing animation effect
- Periodic greeting bubble popup
- Full chat panel with typewriter responses

---

## Knowledge Base Upload

### Supported Formats
- CSV (`.csv`)
- Excel (`.xlsx`)

### Required Columns
| Column | Required | Description |
|--------|----------|-------------|
| `question` | ✅ | The question text |
| `answer` | ✅ | The answer text (supports Markdown) |
| `id` | ❌ | Unique identifier (auto-generated if omitted) |
| `keywords` | ❌ | Semicolon or comma-separated keywords |
| `tags` | ❌ | Semicolon or comma-separated tags |

### Import Modes

- **Replace** (default): Completely replaces existing KB
- **Append**: Merges with existing KB, updates matching entries

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ask` | Ask a question |
| `GET` | `/samples` | Get sample questions |
| `GET` | `/health` | Health check |
| `POST` | `/admin/upload` | Upload KB file |
| `GET` | `/admin/unmatched` | View unmatched queries |

### Ask Endpoint

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I reset my password?"}'
```

Response:
```json
{
  "reply": "To reset your password, go to Settings > Security > Reset Password.",
  "suggestions": ["How to change email?", "Account settings help"]
}
```

---

## Project Structure

```
OfflineChatbot/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── models/
│   │   └── schemas.py      # Pydantic models
│   ├── routers/
│   │   ├── admin.py        # Admin endpoints
│   │   └── public.py       # Public endpoints
│   ├── services/
│   │   ├── auth.py         # HTTP Basic auth
│   │   ├── data.py         # KB load/save
│   │   ├── embeddings.py   # Semantic embeddings
│   │   ├── logging.py      # Query logging
│   │   └── matcher.py      # BM25 + fuzzy matching
│   ├── static/
│   │   ├── css/            # Stylesheets
│   │   ├── img/            # Images and logos
│   │   └── js/
│   │       ├── widget.js   # Embeddable widget
│   │       ├── admin.js    # Admin UI logic
│   │       └── user.js     # Standalone UI logic
│   └── templates/
│       ├── admin.html      # Admin dashboard
│       ├── user.html       # Standalone chat UI
│       └── widget-demo.html # Widget demo page
├── data/
│   ├── data.json           # Knowledge base
│   ├── embeddings.npz      # Cached embeddings
│   ├── unmatched.csv       # Logged unmatched queries
│   └── backups/            # KB backups
└── all-MiniLM-L6-v2-optimized/  # Local embedding model
```

---

## Security & Privacy

- ✅ CORS configured for widget embedding
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ No outbound network calls at runtime
- ✅ PII sanitization before logging unmatched queries
- ✅ Admin routes protected with HTTP Basic auth

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_USER` | `admin` | Admin username |
| `ADMIN_PASS` | `admin123` | Admin password |

---

## Development

For detailed architecture, code flow, and extension guides, see [DEV.md](./DEV.md).

---

## License

MIT License
