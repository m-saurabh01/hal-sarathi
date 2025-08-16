from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class AskRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

class AskResponse(BaseModel):
    reply: str
    suggestions: Optional[List[str]] = None

class KBItem(BaseModel):
    id: str
    question: str
    answer: str
    keywords: List[str] = []
    tags: List[str] = []
    updated_at: datetime

class UploadPreview(BaseModel):
    added: int
    updated: int
    removed: int
    errors: List[str] = []

class UnmatchedEntry(BaseModel):
    timestamp: datetime
    query: str
    top_suggestions: List[str] = []
    source: str = "user"
