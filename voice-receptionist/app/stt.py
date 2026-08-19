from __future__ import annotations

from pathlib import Path

import httpx

from .config import ELEVENLABS_API_BASE, ELEVENLABS_API_KEY, STT_MODEL


def transcribe(audio: bytes, filename: str = "audio.wav") -> str:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    if not audio:
        raise ValueError("empty audio")
    files = {"file": (filename, audio, "application/octet-stream")}
    data = {"model_id": STT_MODEL}
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            f"{ELEVENLABS_API_BASE}/v1/speech-to-text",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            files=files,
            data=data,
        )
        r.raise_for_status()
        payload = r.json()
    return (payload.get("text") or payload.get("transcript") or "").strip()
