"""Seller FAQ retrieval: Chroma first, keyword fallback on faq_entries.jsonl."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

FAQ_CANDIDATES = [
    Path("/home/shanem/wholesale-voice-agent/kb/realkingkhang-seller-faq"),
    Path("/home/shanem/FPI-Corp/Alex/FAQ"),
    Path.home() / "FPI-Corp/Alex/FAQ",
]
SKILL_SCRIPTS = Path.home() / ".hermes/skills/research/realkingkhang-seller-faq-kb/scripts"


def faq_root() -> Path | None:
    for p in FAQ_CANDIDATES:
        if (p / "faq_entries.jsonl").is_file():
            return p
    return None


def _load_entries(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    fp = root / "faq_entries.jsonl"
    for line in fp.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _keyword(root: Path, query: str, top: int) -> list[dict[str, Any]]:
    entries = _load_entries(root)
    terms = [t for t in re.split(r"\W+", (query or "").lower()) if len(t) > 2]

    def score(e: dict[str, Any]) -> int:
        blob = " ".join(
            [
                str(e.get("seller_question_or_complaint") or ""),
                str(e.get("voice_agent_answer") or ""),
                str(e.get("category") or ""),
            ]
        ).lower()
        return sum(1 for t in terms if t in blob)

    ranked = sorted(entries, key=score, reverse=True)
    hits = [e for e in ranked if score(e) > 0][:top]
    return hits or ranked[:top]


def _chroma(root: Path, query: str, top: int) -> list[dict[str, Any]] | None:
    import sys

    if SKILL_SCRIPTS.is_dir():
        sys.path.insert(0, str(SKILL_SCRIPTS))
    try:
        from track_and_index_chroma import query_chroma  # type: ignore
    except Exception:
        return None
    try:
        res = query_chroma(root, query, top=top, collection="seller_faq")
    except Exception:
        return None
    by_id = {str(e.get("id")): e for e in _load_entries(root)}
    out: list[dict[str, Any]] = []
    for r in res.get("results") or []:
        full = by_id.get(str(r.get("id")))
        out.append(full or r)
    return out or None


def retrieve_knowledge(query: str, top: int = 5) -> dict[str, Any]:
    root = faq_root()
    if root is None:
        return {"ok": False, "error": "FAQ database not found", "results": []}
    hits = _chroma(root, query, top)
    backend = "chroma"
    if hits is None:
        hits = _keyword(root, query, top)
        backend = "keyword"
    slim = []
    for e in hits[:top]:
        slim.append(
            {
                "id": e.get("id"),
                "category": e.get("category"),
                "question": e.get("seller_question_or_complaint"),
                "answer": e.get("voice_agent_answer"),
                "do_not_say": e.get("do_not_say") or [],
            }
        )
    return {"ok": True, "backend": backend, "root": str(root), "count": len(slim), "results": slim}
