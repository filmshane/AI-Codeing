from __future__ import annotations

import json
from typing import Any

import httpx

from .config import SEND_PHP_URL
from .db import save_message


def take_website_lead(payload: dict[str, Any]) -> dict[str, Any]:
    name = str(payload.get("name") or payload.get("caller_name") or "").strip()
    phone = str(payload.get("phone") or payload.get("callback_phone") or "").strip()
    address = str(payload.get("address") or "").strip()
    reason = str(payload.get("message") or payload.get("reason") or "Website Morgan lead. Request callback.")
    consent = str(payload.get("ai_call_consent") or "").strip().lower()
    pref = str(payload.get("call_preference") or "short_call_now").strip()
    if not name or not phone:
        return {"ok": False, "error": "name and phone are required"}
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 10:
        return {"ok": False, "error": "phone must have at least 10 digits"}
    if consent in {"yes", "true", "y"}:
        consent = "yes"
    mid = save_message(
        caller_name=name,
        callback_phone=phone,
        reason=reason,
        window=pref,
        source=str(payload.get("source") or "website_morgan"),
    )
    source = str(payload.get("source") or "website_morgan").strip() or "website_morgan"
    email_default = "chat-lead@firstpropertyinvestment.us" if source == "website_chatbot" else "morgan-lead@firstpropertyinvestment.us"
    form = {
        "name": name,
        "phone": phone,
        "email": str(payload.get("email") or email_default),
        "address": address or "Not provided yet",
        "message": reason,
        "ai_call_consent": consent or "",
        "call_preference": pref,
        "source": source,
    }
    forwarded = False
    forward_error = ""
    try:
        with httpx.Client(timeout=15.0, follow_redirects=False, verify=False) as client:
            r = client.post(SEND_PHP_URL, data=form)
            forwarded = r.status_code in {200, 302, 303}
            if not forwarded:
                forward_error = f"send.php status {r.status_code}"
    except Exception as exc:
        forward_error = str(exc)
    return {
        "ok": True,
        "message_id": mid,
        "forwarded_to_inbox": forwarded,
        "forward_error": forward_error or None,
    }
