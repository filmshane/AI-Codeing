from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


@lru_cache(maxsize=1)
def business() -> dict:
    path = ROOT / "config" / "business.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data


def hours_summary() -> str:
    hours = business().get("hours") or {}
    parts = [f"{day} {val}" for day, val in hours.items()]
    return "; ".join(parts) if parts else "Hours are not configured."


def transfer_available() -> bool:
    return bool(str(business().get("transfer_number") or "").strip())


ELEVENLABS_API_KEY = env("ELEVENLABS_API_KEY")
ELEVENLABS_API_BASE = env("ELEVENLABS_API_BASE", "https://api.elevenlabs.io")
ELEVENLABS_AGENT_ID = env("ELEVENLABS_AGENT_ID")
STT_MODEL = env("ELEVENLABS_STT_MODEL", "scribe_v2")
TTS_MODEL = env("ELEVENLABS_TTS_MODEL", "eleven_flash_v2_5")
LLM_BASE = env("LLM_BASE_URL", "http://127.0.0.1:8645/v1")
LLM_MODEL = env("LLM_MODEL", "grok-4.20-reasoning")
LLM_API_KEY = env("LLM_API_KEY", "local")
BIND_HOST = env("BIND_HOST", "127.0.0.1")
BIND_PORT = int(env("BIND_PORT", "8793"))
DATA_DIR = Path(env("DATA_DIR", str(ROOT / "data")))
STUDIO_TOKEN = env("MORGAN_STUDIO_TOKEN")
TOOL_SECRET = env("MORGAN_TOOL_SECRET")
SEND_PHP_URL = env("SEND_PHP_URL", "https://firstpropertyinvestment.us/send.php")
ALEX_AGENT_ID = "agent_3101kzw4yn2fehvtcdn131x9yj56"


def reload_business() -> None:
    business.cache_clear()


def current_voice_id() -> str:
    reload_dotenv()
    vid = env("ELEVENLABS_VOICE_ID") or str(business().get("voice_id") or "XrExE9yKIg1WjnnlVkGX")
    return vid


def reload_dotenv() -> None:
    load_dotenv(ROOT / ".env", override=True)
