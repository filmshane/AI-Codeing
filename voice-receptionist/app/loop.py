from __future__ import annotations

import json
import uuid
from typing import Any

from .db import save_turn
from .llm import complete, system_prompt, text_system_prompt
from .stt import transcribe
from .tools import dispatch
from .tts import synthesize


def _tool_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
    return list(message.get("tool_calls") or [])


def run_text_turn(user_text: str, session_id: str | None = None, history: list[dict] | None = None) -> dict[str, Any]:
    sid = session_id or uuid.uuid4().hex[:12]
    messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt()}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    used = []
    assistant = ""
    for _ in range(4):
        msg = complete(messages)
        calls = _tool_calls(msg)
        if not calls:
            assistant = (msg.get("content") or "").strip()
            break
        messages.append(msg)
        for call in calls:
            fn = call["function"]["name"]
            raw_args = call["function"].get("arguments") or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
            result = dispatch(fn, args)
            used.append({"name": fn, "args": args, "result": result})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id") or fn,
                    "content": result,
                }
            )
    if not assistant:
        assistant = "Sorry, I had trouble with that. Can you say it one more time?"
    save_turn(sid, user_text, assistant)
    return {"session_id": sid, "user_text": user_text, "assistant_text": assistant, "tools": used}


def _clean_history(history: list[dict] | None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in history or []:
        role = str(item.get("role") or "")
        content = str(item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            out.append({"role": role, "content": content})
    return out[-16:]


def run_site_chat_turn(user_text: str, session_id: str | None = None, history: list[dict] | None = None) -> dict[str, Any]:
    sid = session_id or uuid.uuid4().hex[:12]
    messages: list[dict[str, Any]] = [{"role": "system", "content": text_system_prompt()}]
    messages.extend(_clean_history(history))
    messages.append({"role": "user", "content": user_text})

    used = []
    assistant = ""
    for _ in range(5):
        msg = complete(messages)
        calls = _tool_calls(msg)
        if not calls:
            assistant = (msg.get("content") or "").strip()
            break
        messages.append(msg)
        for call in calls:
            fn = call["function"]["name"]
            raw_args = call["function"].get("arguments") or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
            if fn == "take_lead":
                args.setdefault("source", "website_chatbot")
                args.setdefault("message", "Website text-agent lead. Request follow-up.")
            result = dispatch(fn, args)
            used.append({"name": fn, "args": {k: v for k, v in args.items() if k != "phone"}, "result": result})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id") or fn,
                    "content": result,
                }
            )
    if not assistant:
        assistant = "Sorry, I had trouble with that. You can try again or use the form on this page."
    save_turn(sid, user_text, assistant)
    return {"session_id": sid, "user_text": user_text, "assistant_text": assistant, "tools": used}


def run_audio_turn(audio: bytes, filename: str, session_id: str | None = None) -> dict[str, Any]:
    user_text = transcribe(audio, filename=filename)
    if not user_text:
        spoken = "Sorry, I didn’t catch that. Could you say it one more time?"
        audio_out = synthesize(spoken)
        return {
            "session_id": session_id or uuid.uuid4().hex[:12],
            "user_text": "",
            "assistant_text": spoken,
            "audio": audio_out,
            "tools": [],
        }
    result = run_text_turn(user_text, session_id=session_id)
    result["audio"] = synthesize(result["assistant_text"])
    return result
