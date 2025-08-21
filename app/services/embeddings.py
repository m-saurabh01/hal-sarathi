from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Optional, Any
import hashlib

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
        self.data_dir = Path("data")
        self.cache_path = self.data_dir / "embeddings.npz"
        self.model_id = self.model_dir.name
        if HAS_ST and self.model_dir.exists():
            try:
                # Load without internet
                self.model = SentenceTransformer(str(self.model_dir))
                self.enabled = True
            except Exception:
                self.enabled = False

    def _hash_questions(self, questions: List[str]) -> str:
        # Stable hash for cache validation (include count)
        h = hashlib.sha1()
        h.update(str(len(questions)).encode("utf-8"))
        for q in questions:
            h.update(b"\x00")
            h.update(q.encode("utf-8", errors="ignore"))
        return h.hexdigest()

    def _load_cache(self, questions: List[str]) -> bool:
        if not self.enabled or np is None:
            return False
        try:
            import numpy as _np
            if not self.cache_path.exists():
                return False
            with _np.load(self.cache_path, allow_pickle=False) as z:
                cached_hash = str(z.get("hash", ""))
                cached_model = str(z.get("model", ""))
                embs = z["embs"]
            if cached_hash != self._hash_questions(questions) or cached_model != self.model_id:
                return False
            self.q_emb = embs
            return True
        except Exception:
            return False

    def _save_cache(self, embs: Any, questions: List[str]) -> None:
        if not self.enabled or np is None:
            return
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            qh = self._hash_questions(questions)
            np.savez_compressed(self.cache_path, embs=embs, hash=qh, model=self.model_id)
        except Exception:
            pass

    def set_questions(self, questions: List[str]) -> None:
        if not self.enabled or not self.model:
            self.q_emb = None
            return
        # Try cache first
        if self._load_cache(questions):
            return
        # Encode in small batches to keep memory low and cache
        embs = self.model.encode(questions, show_progress_bar=False, batch_size=64, normalize_embeddings=True)
        self.q_emb = embs
        self._save_cache(embs, questions)

    def score_all(self, query: str) -> List[Tuple[int, float]]:
        if not self.enabled or self.q_emb is None or not self.model:
            return []
        q = self.model.encode([query], show_progress_bar=False, normalize_embeddings=True)[0]
        # Cosine similarity with normalized vectors is dot product
        sims = (self.q_emb @ q)
        # Convert to list of (idx, score)
        return sorted([(i, float(sims[i])) for i in range(len(sims))], key=lambda x: -x[1])
