from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Optional, Any

import math

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_ST = True
except Exception:
    HAS_ST = False
    SentenceTransformer = None  # type: ignore
    np = None  # type: ignore


class EmbeddingsService:
    """Optional semantic embeddings using a local sentence-transformers model.
    If dependencies or model are missing, gracefully disables itself.
    """

    def __init__(self, model_dir: str | Path = "all-MiniLM-L6-v2-optimized") -> None:
        self.enabled = False
        self.model_dir = Path(model_dir)
        self.model: Optional[Any] = None
        self.q_emb: Optional[Any] = None
        if HAS_ST and self.model_dir.exists():
            try:
                # Load without internet
                self.model = SentenceTransformer(str(self.model_dir))
                self.enabled = True
            except Exception:
                self.enabled = False

    def set_questions(self, questions: List[str]) -> None:
        if not self.enabled or not self.model:
            self.q_emb = None
            return
        # Encode in small batches to keep memory low
        embs = self.model.encode(questions, show_progress_bar=False, batch_size=64, normalize_embeddings=True)
        self.q_emb = embs

    def score_all(self, query: str) -> List[Tuple[int, float]]:
        if not self.enabled or self.q_emb is None or not self.model:
            return []
        q = self.model.encode([query], show_progress_bar=False, normalize_embeddings=True)[0]
        # Cosine similarity with normalized vectors is dot product
        sims = (self.q_emb @ q)
        # Convert to list of (idx, score)
        return sorted([(i, float(sims[i])) for i in range(len(sims))], key=lambda x: -x[1])
