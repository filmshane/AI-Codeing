from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import DATA_DIR

DB_PATH = DATA_DIR / "reception.db"


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with connect() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                caller_name TEXT,
                callback_phone TEXT,
                reason TEXT,
                window TEXT,
                source TEXT
            );
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                session_id TEXT,
                user_text TEXT,
                assistant_text TEXT
            );
            """
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_message(**fields: Any) -> int:
    with connect() as con:
        cur = con.execute(
            """
            INSERT INTO messages (created_at, caller_name, callback_phone, reason, window, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                now_iso(),
                fields.get("caller_name"),
                fields.get("callback_phone"),
                fields.get("reason"),
                fields.get("window"),
                fields.get("source", "desk-loop"),
            ),
        )
        return int(cur.lastrowid)


def save_turn(session_id: str, user_text: str, assistant_text: str) -> None:
    with connect() as con:
        con.execute(
            """
            INSERT INTO turns (created_at, session_id, user_text, assistant_text)
            VALUES (?, ?, ?, ?)
            """,
            (now_iso(), session_id, user_text, assistant_text),
        )


def recent_messages(limit: int = 20) -> list[dict]:
    with connect() as con:
        rows = con.execute(
            "SELECT * FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
