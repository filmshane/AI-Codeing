from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from .config import LLM_API_KEY, LLM_BASE, LLM_MODEL, ROOT, business, hours_summary, transfer_available

OPS_PROMPT = ROOT / "agents" / "morgan" / "morgan.ops.system.md"
TEXT_PROMPT = ROOT / "agents" / "fpi-text" / "fpi-text.system.md"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_knowledge",
            "description": (
                "Search the seller FAQ / objection database (RealKingKhang KB). "
                "Use for scam, trust, realtor, process, fees, timeline, title, and similar doubts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "n_results": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_hours",
            "description": "Return configured business hours.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_faq",
            "description": "Search local receptionist FAQ notes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_message",
            "description": "Store a callback message after the caller confirmed name and phone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "caller_name": {"type": "string"},
                    "callback_phone": {"type": "string"},
                    "reason": {"type": "string"},
                    "window": {"type": "string"},
                },
                "required": ["caller_name", "callback_phone", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_lead",
            "description": "Submit a website lead after name, phone, and AI-call consent are confirmed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                    "address": {"type": "string"},
                    "message": {"type": "string"},
                    "ai_call_consent": {"type": "string"},
                    "call_preference": {"type": "string"},
                },
                "required": ["name", "phone", "ai_call_consent"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_transfer",
            "description": "Request a human transfer. Only succeeds if transfer_number is configured.",
            "parameters": {
                "type": "object",
                "properties": {"reason": {"type": "string"}},
                "required": ["reason"],
            },
        },
    },
]


def system_prompt() -> str:
    biz = business()
    body = OPS_PROMPT.read_text(encoding="utf-8")
    extra = (
        f"\n\n# Runtime\n"
        f"Company: {biz.get('company_name')}\n"
        f"Hours: {hours_summary()}\n"
        f"Transfer available: {'yes' if transfer_available() else 'no'}\n"
    )
    return body + extra


def text_system_prompt() -> str:
    biz = business()
    body = TEXT_PROMPT.read_text(encoding="utf-8") if TEXT_PROMPT.is_file() else system_prompt()
    extra = (
        f"\n\n# Runtime\n"
        f"Company: {biz.get('company_name')}\n"
        f"Agent: {biz.get('agent_name')}\n"
        f"Hours: {hours_summary()}\n"
        f"Channel: website text chat\n"
    )
    return body + extra


def complete(messages: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "tools": TOOLS,
        "temperature": 0.3,
    }
    with httpx.Client(timeout=90.0) as client:
        r = client.post(
            f"{LLM_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
    return data["choices"][0]["message"]


def search_kb(query: str) -> str:
    q = (query or "").lower()
    hits: list[str] = []
    kb = Path(__file__).resolve().parents[1] / "kb"
    for path in sorted(kb.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if any(tok in text.lower() for tok in q.split() if len(tok) > 2) or not q:
            hits.append(f"{path.name}: {text.strip()}")
    return "\n---\n".join(hits[:4]) or "No matching FAQ."
