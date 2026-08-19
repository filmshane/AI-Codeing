from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import business, hours_summary, transfer_available
from app.db import init_db
from app.tools import dispatch

init_db()


def test_hours_configured():
    text = hours_summary()
    assert "monday" in text.lower() or "Monday" in text or "9:00" in text


def test_transfer_default_off():
    assert transfer_available() is False
    assert business()["agent_name"] == "Morgan"


def test_take_message_writes():
    result = dispatch(
        "take_message",
        {
            "caller_name": "Test Caller",
            "callback_phone": "+15551234567",
            "reason": "unit test",
            "window": "tomorrow morning",
        },
    )
    assert "message_id" in result


def test_retrieve_knowledge_objections():
    from app.faq_retrieve import retrieve_knowledge

    res = retrieve_knowledge("seller thinks this is a scam", top=3)
    assert res.get("ok") is True
    assert res.get("count", 0) >= 1
    first = (res.get("results") or [{}])[0]
    assert first.get("answer") or first.get("question")


def test_text_prompt_imported():
    from app.llm import TEXT_PROMPT, text_system_prompt

    assert TEXT_PROMPT.is_file()
    body = text_system_prompt()
    assert "retrieve_knowledge" in body
    assert "take_lead" in body
    assert "Imported chatbot" in body
