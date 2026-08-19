from __future__ import annotations

import json
import logging

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from .config import LLM_BASE, LLM_MODEL, env

log = logging.getLogger("morgan.llm_proxy")


def llm_gate_token() -> str:
    return env("MORGAN_LLM_BEARER")


def authorized(request: Request) -> bool:
    expected = llm_gate_token()
    if not expected:
        return False
    auth = request.headers.get("authorization") or ""
    custom = request.headers.get("x-morgan-llm-bearer") or ""
    if custom == expected:
        return True
    if auth == f"Bearer {expected}":
        return True
    return False


async def forward_chat_completions(request: Request):
    if not authorized(request):
        auth = request.headers.get("authorization") or ""
        prefix = auth[:16] + "…" if len(auth) > 16 else auth
        names = sorted(h.lower() for h in request.headers.keys())
        log.warning(
            "llm unauthorized from %s auth=%r headers=%s",
            request.client.host if request.client else "?",
            prefix,
            names,
        )
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    raw = await request.body()
    try:
        payload = json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JSONResponse({"error": "invalid json"}, status_code=400)
    payload["model"] = LLM_MODEL
    # ElevenLabs custom LLM requires SSE.
    payload["stream"] = True
    url = f"{LLM_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": "Bearer local",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(120.0, connect=10.0)
    client = httpx.AsyncClient(timeout=timeout)
    req = client.build_request("POST", url, headers=headers, json=payload)
    try:
        resp = await client.send(req, stream=True)
    except Exception as exc:
        await client.aclose()
        log.error("proxy upstream: %s", exc)
        return JSONResponse({"error": f"proxy upstream: {exc}"}, status_code=502)

    log.info(
        "llm stream %s model=%s messages=%s",
        resp.status_code,
        LLM_MODEL,
        len(payload.get("messages") or []),
    )

    async def gen():
        try:
            async for chunk in resp.aiter_bytes():
                yield chunk
        finally:
            await resp.aclose()
            await client.aclose()

    return StreamingResponse(
        gen(),
        status_code=resp.status_code,
        media_type="text/event-stream",
    )
