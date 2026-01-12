# Developer Guide

Technical documentation for the HAL Sarathi Chatbot codebase.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                  │
├──────────────────┬──────────────────┬───────────────────────────┤
│   Widget         │   Standalone UI  │   Admin Dashboard         │
│   (widget.js)    │   (user.html)    │   (admin.html)            │
│   Shadow DOM     │                  │                           │
└────────┬─────────┴────────┬─────────┴─────────────┬─────────────┘
         │                  │                       │
         └──────────────────┴───────────────────────┘
                            │
                      POST /ask
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      FastAPI Server                              │
├─────────────────────────────────────────────────────────────────┤
│  main.py                                                         │
│  ├── CORS / Security Headers / Static Files                     │
│  ├── public.py  → /, /ask, /samples, /health                    │
│  └── admin.py   → /admin, /admin/upload, /admin/unmatched       │
├─────────────────────────────────────────────────────────────────┤
│  Services Layer                                                  │
│  ├── matcher.py     → BM25 + fuzzy scoring                      │
│  ├── embeddings.py  → Semantic similarity (optional)            │
│  ├── data.py        → KB CRUD + backups                         │
│  ├── logging.py     → Unmatched query logging                   │
│  └── auth.py        → HTTP Basic authentication                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Widget Architecture

The widget (`widget.js`) is a self-contained Web Component:

```javascript
// Usage
<script src="/static/js/widget.js"></script>
<hal-chatbot endpoint="http://localhost:8000"></hal-chatbot>
```

### Key Features

| Feature | Implementation |
|---------|----------------|
| **Isolation** | Shadow DOM prevents style conflicts |
| **Typewriter** | Character-by-character response rendering |
| **Markdown** | Inline parser for bold, italic, code, links, lists |
| **Animations** | CSS keyframes for breathing effect and typing dots |
| **Greeting** | Periodic popup bubble (30s interval) |

### Widget Class Structure

```javascript
class HALChatbot extends HTMLElement {
  // Lifecycle
  connectedCallback()     // Initialize on DOM attach
  
  // Properties
  _ep                     // Endpoint URL
  _isOpen                 // Panel visibility state
  
  // UI Methods
  _render()               // Build Shadow DOM
  _toggle()               // Open/close panel
  _send()                 // Send message to API
  _addMsg(role, text)     // Add message bubble
  _typeMsg(bubble, text)  // Typewriter effect
  
  // Helpers
  _md(text)               // Markdown parser
  _logo()                 // Logo URL builder
  _avatar()               // User avatar URL
}
```

---

## Data Flow

### Ask Request Flow

```
User Input
    │
    ▼
POST /ask { message }
    │
    ▼
┌───────────────────┐
│   Matcher.score_all()
│   • Tokenize query
│   • BM25-style scoring
│   • Fuzzy matching boost
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   EmbeddingsService (optional)
│   • Cosine similarity
│   • Score blending
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   Threshold Logic
│   • High (≥0.78): Direct answer
│   • Medium (≥0.6): Suggestions
│   • Low (<0.6): Log unmatched
└─────────┬─────────┘
          │
          ▼
Response { reply, suggestions[] }
```

### KB Upload Flow

```
Admin uploads CSV/XLSX
    │
    ▼
POST /admin/upload
    │
    ▼
┌───────────────────┐
│   DataService.upsert_from_rows()
│   • Validate columns
│   • Normalize IDs
│   • Deduplicate
│   • Merge keywords/tags
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   DataService.save_kb()
│   • Create backup
│   • Write data.json
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   public.set_data()
│   • Reload matcher
│   • Rebuild embeddings index
└─────────┴─────────┘
```

---

## File Reference

### Core Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, CORS, security headers, static mount |
| `app/routers/public.py` | User-facing routes: `/`, `/ask`, `/samples` |
| `app/routers/admin.py` | Admin routes: `/admin`, `/admin/upload` |
| `app/services/matcher.py` | BM25 + fuzzy matching algorithm |
| `app/services/embeddings.py` | Local sentence-transformers integration |
| `app/services/data.py` | KB load/save, validation, backups |
| `app/services/logging.py` | PII-sanitized unmatched logging |
| `app/services/auth.py` | HTTP Basic auth for admin |
| `app/models/schemas.py` | Pydantic request/response models |

### Frontend Files

| File | Purpose |
|------|---------|
| `app/static/js/widget.js` | Embeddable widget (Web Component) |
| `app/static/js/user.js` | Standalone chat UI logic |
| `app/static/js/admin.js` | Admin dashboard logic |
| `app/static/css/main.css` | Shared styles (admin + standalone) |
| `app/templates/widget-demo.html` | Widget embedding demo |
| `app/templates/user.html` | Standalone chat page |
| `app/templates/admin.html` | Admin dashboard |

### Data Files

| File | Purpose |
|------|---------|
| `data/data.json` | Knowledge base |
| `data/embeddings.npz` | Pre-computed embeddings cache |
| `data/unmatched.csv` | Logged unmatched queries |
| `data/backups/` | Timestamped KB backups |

---

## Matching Algorithm

### Scoring Pipeline

1. **Tokenization**: Lowercase, split on non-alphanumeric
2. **BM25-style Scoring**: Term frequency × inverse document frequency
3. **Keyword Boost**: +0.15 for keyword matches
4. **Fuzzy Boost**: RapidFuzz similarity for near-matches
5. **Semantic Blend** (optional): Cosine similarity with embeddings

### Thresholds

| Score Range | Action |
|-------------|--------|
| ≥ 0.78 | Return answer directly + suggestions |
| ≥ 0.60 | Offer suggestions, fallback to top answer |
| < 0.60 | Log as unmatched, ask to rephrase |

---

## API Reference

### POST /ask

Ask a question.

**Request:**
```json
{ "message": "How do I reset my password?" }
```

**Response:**
```json
{
  "reply": "Go to Settings > Security > Reset Password.",
  "suggestions": ["Change email", "Account help"]
}
```

### GET /samples

Get sample questions for UI.

**Response:**
```json
{ "samples": ["How to login?", "Reset password", "Contact support"] }
```

### POST /admin/upload

Upload KB file (requires auth).

**Form Data:**
- `file`: CSV or XLSX file
- `mode`: `replace` (default) or `append`

**Response:**
```json
{
  "status": "ok",
  "stats": { "added": 10, "updated": 2, "removed": 0 }
}
```

### GET /admin/unmatched

Preview unmatched queries (requires auth).

---

## Extending the Chatbot

### Adding a New Service

1. Create file in `app/services/`
2. Add initialization in `main.py` or router
3. Update `set_data()` in `public.py` if data-dependent

### Customizing the Widget

Key CSS classes (minified names):

| Class | Element |
|-------|---------|
| `.tr` | Floating trigger button |
| `.pn` | Chat panel |
| `.hd` | Panel header |
| `.ms` | Messages container |
| `.mg` | Message bubble |
| `.mg.bt` | Bot message |
| `.mg.us` | User message |
| `.gr` | Greeting bubble |

### Adding Feedback

To add thumbs up/down:

1. Add buttons to bot message template in widget
2. Create `POST /feedback` endpoint
3. Log feedback to `data/feedback.csv`

---

## Testing

```bash
# Run tests
pytest tests/

# Test matcher
python -m pytest tests/test_matcher.py -v
```

### Test Coverage Areas

- [ ] Matcher scoring accuracy
- [ ] DataService validation
- [ ] KB upload deduplication
- [ ] API endpoints
- [ ] Widget rendering (browser tests)

---

## Performance Considerations

- **Embeddings**: Pre-computed at startup, ~2-3s for 1000 items
- **Matching**: O(n) where n = KB size; fast for <10k items
- **Widget**: ~12KB minified, no external dependencies
- **Backups**: Created on every KB update

---

## Troubleshooting

### Widget not appearing

1. Check console for CORS errors
2. Verify `endpoint` attribute is correct
3. Ensure `/static/js/widget.js` is accessible

### Matching not accurate

1. Add more keywords to KB entries
2. Ensure questions are unique and descriptive
3. Enable semantic embeddings for better results

### Admin upload fails

1. Check file format (CSV/XLSX only)
2. Verify required columns exist
3. Check for duplicate explicit IDs

---

## Code Style

- Python 3.10+
- PEP 8 / Black formatting
- Pydantic for all IO models
- ISO 8601 timestamps with Z suffix

