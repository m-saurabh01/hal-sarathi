from __future__ import annotations
import json
from pathlib import Path
from typing import List, Tuple, Dict
import uuid
import unicodedata
import re
from datetime import datetime
from pydantic import BaseModel
from app.models.schemas import KBItem

DATA_DIR = Path("data")
KB_PATH = DATA_DIR / "data.json"
BACKUP_DIR = DATA_DIR / "backups"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

class DataService:
    @staticmethod
    def _norm_question(text: str) -> str:
        # Normalize Unicode, collapse whitespace, lowercase
        t = unicodedata.normalize("NFKC", (text or "").strip())
        t = re.sub(r"\s+", " ", t)
        return t.lower()

    @staticmethod
    def _gen_id_from_question(question: str, current_ids: Dict[str, KBItem]) -> str:
        """Deterministic, lite ID generator with legacy-compat.
        - If an existing legacy ID (lowercased question) exists, reuse it to avoid breaking updates.
        - Else, use UUIDv5 (namespace URL) of normalized question; return short hex.
        """
        legacy = DataService._norm_question(question)
        if legacy in current_ids:
            return legacy
        u = uuid.uuid5(uuid.NAMESPACE_URL, legacy)
        return f"q_{u.hex[:16]}"  # 64-bit equivalent; short and robust
    @staticmethod
    def load_kb() -> List[KBItem]:
        if not KB_PATH.exists():
            return []
        with KB_PATH.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        items: List[KBItem] = []
        for it in raw:
            # tolerate legacy without timestamps
            updated_at = it.get("updated_at") or datetime.utcnow().isoformat()
            items.append(KBItem(
                id=str(it.get("id") or DataService._norm_question(it["question"])),
                question=it["question"],
                answer=it["answer"],
                keywords=it.get("keywords", []),
                tags=it.get("tags", []),
                updated_at=datetime.fromisoformat(updated_at.replace("Z",""))
            ))
        return items

    @staticmethod
    def save_kb(items: List[KBItem]) -> None:
        if KB_PATH.exists():
            ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            KB_PATH.replace(BACKUP_DIR / f"data-{ts}.json")
        serial = [
            {
                "id": it.id,
                "question": it.question,
                "answer": it.answer,
                "keywords": it.keywords,
                "tags": it.tags,
                "updated_at": it.updated_at.isoformat() + "Z",
            } for it in items
        ]
        KB_PATH.write_text(json.dumps(serial, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def upsert_from_rows(rows: List[Dict[str, str]], mode: str = "replace") -> Tuple[List[KBItem], Dict[str, int], List[str]]:
        """Validate rows and produce a KB list.
        mode: 'replace' (default) replaces the KB with uploaded rows;
              'append' merges uploaded rows into existing KB (no removals).
        Returns: (items, stats, errors)
        """
        mode = (mode or "replace").lower().strip()
        if mode not in {"replace", "append"}:
            mode = "replace"

        current = {it.id: it for it in DataService.load_kb()}
        errors: List[str] = []
        items_by_id: Dict[str, KBItem] = {}
        dedup_count = 0

        def split_multi(val: str) -> List[str]:
            raw = re.split(r"[;,]", val or "")
            return [s.strip() for s in raw if len(s.strip()) > 2]

        for idx, r in enumerate(rows, start=1):
            q = (r.get("question") or "").strip()
            a = (r.get("answer") or "").strip()
            provided_id = (r.get("id") or "").strip()
            if not q or not a:
                errors.append(f"Row {idx}: question/answer required")
                continue
            _id = provided_id or DataService._gen_id_from_question(q, current)

            kws = split_multi(r.get("keywords") or "")[:20]
            tags = [s.strip() for s in re.split(r"[;,]", r.get("tags") or "") if s.strip()][:10]

            if _id in items_by_id:
                # If uploader provided an explicit id, treat duplicate as error
                if provided_id:
                    errors.append(f"Row {idx}: duplicate id {_id}")
                    continue
                # Otherwise, auto-dedupe: last row wins; merge keywords/tags (unique, order preserved)
                prev = items_by_id[_id]
                dedup_count += 1
                merged_kws = list(dict.fromkeys((prev.keywords or []) + kws))[:20]
                merged_tags = list(dict.fromkeys((prev.tags or []) + tags))[:10]
                items_by_id[_id] = KBItem(
                    id=_id,
                    question=q,
                    answer=a or prev.answer,
                    keywords=merged_kws,
                    tags=merged_tags,
                    updated_at=datetime.utcnow(),
                )
            else:
                items_by_id[_id] = KBItem(
                    id=_id,
                    question=q,
                    answer=a,
                    keywords=kws,
                    tags=tags,
                    updated_at=datetime.utcnow(),
                )

        if mode == "replace":
            items: List[KBItem] = list(items_by_id.values())
            stats = {
                "added": sum(1 for it in items if it.id not in current),
                "updated": sum(1 for it in items if it.id in current),
                "removed": max(0, len(current) - len(items)),
                "deduplicated": dedup_count,
            }
            return items, stats, errors
        else:  # append/merge
            merged: Dict[str, KBItem] = {k: v for k, v in current.items()}
            added_cnt = 0
            updated_cnt = 0

            for _id, new_item in items_by_id.items():
                if _id in merged:
                    prev = merged[_id]
                    # Merge: uploaded answer replaces; merge keywords/tags unique
                    merged_kws = list(dict.fromkeys((prev.keywords or []) + (new_item.keywords or [])))[:20]
                    merged_tags = list(dict.fromkeys((prev.tags or []) + (new_item.tags or [])))[:10]
                    merged[_id] = KBItem(
                        id=_id,
                        question=new_item.question or prev.question,
                        answer=new_item.answer or prev.answer,
                        keywords=merged_kws,
                        tags=merged_tags,
                        updated_at=datetime.utcnow(),
                    )
                    updated_cnt += 1
                else:
                    merged[_id] = KBItem(
                        id=_id,
                        question=new_item.question,
                        answer=new_item.answer,
                        keywords=new_item.keywords,
                        tags=new_item.tags,
                        updated_at=datetime.utcnow(),
                    )
                    added_cnt += 1

            items = list(merged.values())
            stats = {
                "added": added_cnt,
                "updated": updated_cnt,
                "removed": 0,
                "deduplicated": dedup_count,
            }
            return items, stats, errors
