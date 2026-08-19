from __future__ import annotations

import httpx

from .config import ELEVENLABS_API_BASE, ELEVENLABS_API_KEY, TTS_MODEL, current_voice_id


def synthesize(text: str, voice_id: str | None = None) -> bytes:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    spoken = (text or "").strip()
    if not spoken:
        raise ValueError("empty text")
    vid = voice_id or current_voice_id()
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            f"{ELEVENLABS_API_BASE}/v1/text-to-speech/{vid}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
            },
            json={
                "text": spoken,
                "model_id": TTS_MODEL,
                "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
            },
        )
        r.raise_for_status()
        return r.content
