from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
from typing import List
import re

DATA_DIR = Path("data")
UNMATCHED_CSV = DATA_DIR / "unmatched.csv"
MATCHED_LOG = DATA_DIR / "matched.log"

DATA_DIR.mkdir(parents=True, exist_ok=True)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?\d[\s-]?){7,15}\b")

class LogService:
    @staticmethod
    def sanitize(text: str) -> str:
        text = EMAIL_RE.sub("[email]", text)
        text = PHONE_RE.sub("[phone]", text)
        return text

    @staticmethod
    def log_unmatched(query: str, suggestions: List[str]) -> None:
        UNMATCHED_CSV.parent.mkdir(parents=True, exist_ok=True)
        write_header = not UNMATCHED_CSV.exists()
        with UNMATCHED_CSV.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["timestamp", "query", "top_suggestions"]) 
            w.writerow([datetime.utcnow().isoformat() + "Z", LogService.sanitize(query), " | ".join(suggestions[:5])])

    @staticmethod
    def log_matched(input_text: str, scored: List[tuple[str, float]]):
        MATCHED_LOG.parent.mkdir(parents=True, exist_ok=True)
        with MATCHED_LOG.open("a", encoding="utf-8") as f:
            f.write(f"\nInput: {LogService.sanitize(input_text)}\n")
            for q, s in sorted(scored, key=lambda x: -x[1]):
                f.write(f"  {q} — {s:.3f}\n")
