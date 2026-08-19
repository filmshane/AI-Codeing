from __future__ import annotations

import json
from typing import Any

from .config import business, hours_summary, transfer_available
from .faq_retrieve import retrieve_knowledge
from .leads import take_website_lead
from .llm import search_kb


def dispatch(name: str, args: dict[str, Any]) -> str:
    if name == "get_hours":
        return json.dumps({"hours": hours_summary(), "timezone": business().get("timezone")})
    if name == "lookup_faq":
        local = search_kb(str(args.get("query") or ""))
        faq = retrieve_knowledge(str(args.get("query") or ""), top=int(args.get("n_results") or 4))
        return json.dumps({"local_kb": local, "seller_faq": faq})
    if name == "retrieve_knowledge":
        return json.dumps(retrieve_knowledge(str(args.get("query") or ""), top=int(args.get("n_results") or 5)))
    if name == "take_message":
        result = take_website_lead(
            {
                "name": args.get("caller_name"),
                "phone": args.get("callback_phone"),
                "message": args.get("reason"),
                "call_preference": args.get("window"),
                "ai_call_consent": "yes",
            }
        )
        return json.dumps(result)
    if name == "take_lead":
        return json.dumps(take_website_lead(args))
    if name == "request_transfer":
        if not transfer_available():
            return json.dumps(
                {
                    "ok": False,
                    "reason": "No transfer number configured. Take a message instead.",
                }
            )
        return json.dumps(
            {
                "ok": True,
                "transfer_number": business().get("transfer_number"),
                "note": "Desk loop cannot place a PSTN transfer. Tell the caller a human will follow up, or use Phase 3 phone path.",
            }
        )
    return json.dumps({"ok": False, "error": f"unknown tool {name}"})
