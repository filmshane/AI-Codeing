from __future__ import annotations

import base64
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response

from .config import (
    ELEVENLABS_AGENT_ID,
    LLM_BASE,
    LLM_MODEL,
    STT_MODEL,
    TTS_MODEL,
    TOOL_SECRET,
    business,
    current_voice_id,
)
from .db import init_db, recent_messages
from .leads import take_website_lead
from .llm_proxy import forward_chat_completions
from .loop import run_audio_turn, run_site_chat_turn, run_text_turn
from .stt import transcribe
from .studio import apply_voice, list_voices, studio_ok
from .tts import synthesize

app = FastAPI(title="Morgan Receptionist", version="1.1.0")
WEBSITE = Path(__file__).resolve().parents[1] / "website"


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    biz = business()
    return {
        "ok": True,
        "service": "voice-receptionist",
        "agent": biz.get("agent_name"),
        "company": biz.get("company_name"),
        "stt": {"provider": "elevenlabs", "model": STT_MODEL},
        "tts": {"provider": "elevenlabs", "model": TTS_MODEL, "voice_id": current_voice_id()},
        "llm": {"base": LLM_BASE, "model": LLM_MODEL, "bridge": "/api/v1/chat/completions"},
        "elevenlabs_agent_id": ELEVENLABS_AGENT_ID or None,
        "bind": "127.0.0.1:8793",
        "widget_placement": "top-right",
        "text_agent": "fpi-text",
        "faq": True,
    }


@app.post("/api/stt")
async def api_stt(file: UploadFile = File(...)) -> dict:
    audio = await file.read()
    text = transcribe(audio, filename=file.filename or "audio.wav")
    return {"text": text}


@app.post("/api/tts")
async def api_tts(text: str = Form(...), voice_id: str | None = Form(default=None)) -> Response:
    audio = synthesize(text, voice_id=voice_id)
    return Response(content=audio, media_type="audio/mpeg")


@app.post("/api/loop/text")
async def api_loop_text(payload: dict) -> dict:
    user_text = str(payload.get("text") or "").strip()
    if not user_text:
        return JSONResponse({"error": "text required"}, status_code=400)
    return run_text_turn(user_text, session_id=payload.get("session_id"))


@app.post("/api/chat")
async def api_site_chat(payload: dict) -> dict:
    user_text = str(payload.get("text") or payload.get("message") or "").strip()
    if not user_text:
        return JSONResponse({"ok": False, "error": "text required"}, status_code=400)
    result = run_site_chat_turn(
        user_text,
        session_id=payload.get("session_id"),
        history=payload.get("history") or [],
    )
    return {
        "ok": True,
        "session_id": result["session_id"],
        "reply": result["assistant_text"],
        "tools": [t.get("name") for t in result.get("tools") or []],
    }


@app.post("/api/loop/turn")
async def api_loop_turn(
    file: UploadFile = File(...),
    session_id: str | None = Form(default=None),
) -> dict:
    audio = await file.read()
    result = run_audio_turn(audio, filename=file.filename or "audio.wav", session_id=session_id)
    audio_b64 = base64.b64encode(result.pop("audio")).decode("ascii")
    result["audio_mpeg_base64"] = audio_b64
    return result


@app.get("/api/messages")
def api_messages() -> dict:
    return {"messages": recent_messages()}


@app.post("/api/tools/take_lead")
async def api_take_lead(request: Request, x_morgan_tool_secret: str | None = Header(default=None)) -> dict:
    if not TOOL_SECRET or x_morgan_tool_secret != TOOL_SECRET:
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    try:
        payload = await request.json()
    except Exception:
        form = await request.form()
        payload = dict(form)
    return take_website_lead(payload)


@app.get("/api/studio/voices")
def api_studio_voices(request: Request) -> dict:
    if not studio_ok(request):
        return JSONResponse({"error": "studio is LAN-only"}, status_code=401)
    return {"voices": list_voices(), "active": current_voice_id()}


@app.post("/api/studio/voice")
async def api_studio_voice(request: Request) -> dict:
    if not studio_ok(request):
        return JSONResponse({"error": "studio is LAN-only"}, status_code=401)
    body = await request.json()
    try:
        return apply_voice(str(body.get("voice_id") or ""))
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@app.post("/api/v1/chat/completions")
async def api_morgan_llm(request: Request):
    return await forward_chat_completions(request)


@app.get("/studio")
@app.get("/studio/")
def studio_page() -> FileResponse:
    return FileResponse(WEBSITE / "studio.html")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEBSITE / "index.html")
