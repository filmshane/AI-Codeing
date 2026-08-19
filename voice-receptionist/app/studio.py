from __future__ import annotations

import os
import re
from pathlib import Path

import httpx
import yaml

import ipaddress

from .config import (
    ALEX_AGENT_ID,
    ELEVENLABS_API_BASE,
    ELEVENLABS_API_KEY,
    ELEVENLABS_AGENT_ID,
    ROOT,
    current_voice_id,
    reload_business,
    reload_dotenv,
)

LAN_NETS = (
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
)


def client_ip(request) -> str:
    forwarded = (request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "")


def studio_ok(request=None, token: str | None = None) -> bool:
    # ElevenLabs key is already on the server. No visitor token.
    # Studio is LAN/localhost only.
    if request is None:
        return False
    raw = client_ip(request)
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError:
        return False
    return any(ip in net for net in LAN_NETS)


def list_voices() -> list[dict]:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    with httpx.Client(timeout=30.0) as client:
        r = client.get(
            f"{ELEVENLABS_API_BASE}/v1/voices",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
        )
        r.raise_for_status()
        data = r.json()
    out = []
    for v in data.get("voices") or []:
        labels = v.get("labels") or {}
        gender = (labels.get("gender") or "").lower()
        hq = v.get("high_quality_base_model_ids") or []
        category = (v.get("category") or "").lower()
        use_case = (labels.get("use_case") or "").lower()
        if gender != "female":
            continue
        if not hq:
            continue
        if category not in {"premade", "professional"}:
            continue
        if use_case in {"characters_animation"}:
            continue
        rank = 0
        if category == "professional":
            rank += 30
        if use_case in {"informative_educational", "conversational"}:
            rank += 10
        if "professional" in (v.get("name") or "").lower():
            rank += 5
        out.append(
            {
                "voice_id": v.get("voice_id"),
                "name": v.get("name"),
                "gender": labels.get("gender"),
                "accent": labels.get("accent"),
                "preview_url": v.get("preview_url"),
                "category": category,
                "use_case": use_case,
                "active": v.get("voice_id") == current_voice_id(),
                "_rank": rank,
            }
        )
    out.sort(key=lambda x: (-x["_rank"], x["name"] or ""))
    for row in out:
        row.pop("_rank", None)
    return out


def _set_env_key(key: str, value: str) -> None:
    path = ROOT / ".env"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{key}={value}")
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def apply_voice(voice_id: str) -> dict:
    vid = (voice_id or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9]{10,64}", vid):
        raise ValueError("invalid voice id")
    agent_id = ELEVENLABS_AGENT_ID or os.environ.get("ELEVENLABS_AGENT_ID", "")
    if not agent_id or agent_id == ALEX_AGENT_ID:
        raise RuntimeError("refusing to change Alex or an unset agent")
    with httpx.Client(timeout=45.0) as client:
        r = client.patch(
            f"{ELEVENLABS_API_BASE}/v1/convai/agents/{agent_id}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={"conversation_config": {"tts": {"voice_id": vid}}},
        )
        r.raise_for_status()
    _set_env_key("ELEVENLABS_VOICE_ID", vid)
    biz_path = ROOT / "config" / "business.yaml"
    biz = yaml.safe_load(biz_path.read_text(encoding="utf-8")) or {}
    biz["voice_id"] = vid
    biz_path.write_text(yaml.safe_dump(biz, sort_keys=False), encoding="utf-8")
    reload_dotenv()
    reload_business()
    return {"ok": True, "voice_id": vid, "agent_id": agent_id}
