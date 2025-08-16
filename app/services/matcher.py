from __future__ import annotations
import math
import re
from typing import List, Tuple
try:
    from rapidfuzz import fuzz  # type: ignore
    def _fuzzy_ratio(a: str, b: str) -> float:
        return fuzz.token_sort_ratio(a, b) / 100.0
except Exception:
    import difflib
    def _normalize_for_token_sort(s: str) -> str:
        return " ".join(sorted(s.lower().split()))
    def _fuzzy_ratio(a: str, b: str) -> float:
        # Approximate token_sort_ratio using difflib on sorted tokens
        return difflib.SequenceMatcher(None, _normalize_for_token_sort(a), _normalize_for_token_sort(b)).ratio()

# Lightweight tokenizer
WORD_RE = re.compile(r"[\w']+")

class Matcher:
    def __init__(self, questions: List[str], keywords: List[List[str]]):
        self.questions = questions
        self.keywords = [set(kw) for kw in keywords]
        # Precompute bag-of-words for BM25-like scoring without external deps
        self.docs = [self._tokenize(q) for q in questions]
        self.df = {}
        for doc in self.docs:
            for t in set(doc):
                self.df[t] = self.df.get(t, 0) + 1
        self.N = len(self.docs)
        self.avgdl = sum(len(d) for d in self.docs) / max(1, self.N)
        self.k1, self.b = 1.5, 0.75

    def _tokenize(self, text: str) -> List[str]:
        return [t.lower() for t in WORD_RE.findall(text.lower())]

    def bm25_score(self, query: str, idx: int) -> float:
        q_terms = self._tokenize(query)
        score = 0.0
        doc = self.docs[idx]
        dl = len(doc) or 1
        for term in set(q_terms):
            df = self.df.get(term, 0)
            if df == 0:
                continue
            idf = math.log(1 + (self.N - df + 0.5) / (df + 0.5))
            tf = doc.count(term)
            score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return score

    def score_all(self, query: str) -> List[Tuple[int, float]]:
        scores = []
        for i, q in enumerate(self.questions):
            exact = 1.0 if query.strip().lower() == q.strip().lower() else 0.0
            kw_hit = 0.5 if any(k in query.lower() or query.lower() in k for k in self.keywords[i]) else 0.0
            fuzzy = _fuzzy_ratio(query, q)
            bm25 = self.bm25_score(query, i)
            # Weighted blend (tunable)
            blended = max(exact, 0.55 * fuzzy + 0.35 * (bm25 / 5.0) + 0.10 * kw_hit)
            scores.append((i, blended))
        return sorted(scores, key=lambda x: -x[1])
