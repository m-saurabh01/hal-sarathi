from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from app.models.schemas import AskRequest
from app.services.data import DataService
from app.services.matcher import Matcher
from app.services.logging import LogService
from app.services.embeddings import EmbeddingsService

router = APIRouter()

# Load data and matcher on module import; simple hot-swap via set_data
_kb_items = DataService.load_kb()
_questions = [it.question for it in _kb_items]
_keywords = [it.keywords for it in _kb_items]
_matcher = Matcher(_questions, _keywords) if _kb_items else None
_embed = EmbeddingsService()
if _embed.enabled:
    _embed.set_questions(_questions)


def set_data():
    global _kb_items, _questions, _keywords, _matcher
    _kb_items = DataService.load_kb()
    _questions = [it.question for it in _kb_items]
    _keywords = [it.keywords for it in _kb_items]
    _matcher = Matcher(_questions, _keywords) if _kb_items else None
    if _embed.enabled:
        _embed.set_questions(_questions)


@router.get("/", response_class=HTMLResponse)
async def user_ui():
    html = Path("app/templates/user.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@router.post("/ask")
async def ask(payload: AskRequest):
    if not _matcher:
        return JSONResponse({"reply": "Knowledge base is empty. Please try later.", "suggestions": []})

    ranked = _matcher.score_all(payload.message)
    # Optional semantic blend
    if _embed.enabled:
        sem = _embed.score_all(payload.message)
        sem_map = {i: s for i, s in sem}
        # Blend lexical and semantic (tunable)
        blended = []
        for i, s in ranked:
            ss = sem_map.get(i, 0.0)
            blended.append((i, 0.6 * s + 0.4 * ss))
        ranked = sorted(blended, key=lambda x: -x[1])

    top_idx, top_score = ranked[0]
    top_pairs = [(i, score) for i, score in ranked[:5]]
    top_questions = [(_kb_items[i].question, score) for i, score in top_pairs]
    MIN_SUGGESTION_SCORE = 0.4

    # thresholds with graceful fallbacks
    if top_score >= 0.78:
        reply = _kb_items[top_idx].answer
        # Exclude the top question and filter by relevance
        suggestions = [q for (q, s) in top_questions if q != _kb_items[top_idx].question and s >= MIN_SUGGESTION_SCORE]
    elif top_score >= 0.6:
        # Prefer suggestions when available; otherwise provide the best answer
        rel = [q for (q, s) in top_questions if s >= MIN_SUGGESTION_SCORE]
        if rel:
            reply = "I found similar questions. Please choose one."
            suggestions = rel
        else:
            reply = _kb_items[top_idx].answer
            suggestions = []
    else:
        rel = [q for (q, s) in top_questions if s >= MIN_SUGGESTION_SCORE]
        if rel:
            reply = "I found similar questions. Please choose one."
            suggestions = rel
        else:
            reply = "Sorry, I couldn't find a good match. Please rephrase your question."
            suggestions = []
        LogService.log_unmatched(payload.message, [q for q, _ in top_questions])

    LogService.log_matched(payload.message, [(q, s) for (q, s) in top_questions])
    return JSONResponse({"reply": reply, "suggestions": suggestions or []})


@router.get("/samples")
async def samples():
    # Provide first N KB questions as samples (stable and always available)
    top = [q for q in _questions[:8]]
    return JSONResponse({"samples": top})
