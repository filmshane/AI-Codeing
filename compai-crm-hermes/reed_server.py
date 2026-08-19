#!/usr/bin/env python3
"""Hermes-backed CRM agent (Reed). Replaces eve on :2000."""
from __future__ import annotations

import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

import psycopg2
from psycopg2.extras import RealDictCursor

PORT = int(os.environ.get("AGENT_PORT", "2000"))
DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5432/crm",
).replace("?schema=public", "")
SECRET = os.environ.get("AGENT_BRIDGE_SECRET", "").strip()
LLM_BASE = os.environ.get("HERMES_LLM_BASE", "http://127.0.0.1:8645/v1").rstrip("/")
LLM_MODEL = os.environ.get("HERMES_LLM_MODEL", "grok-4.20-reasoning")
PROMPT = Path("/opt/compai-crm-hermes/reed.system.md").read_text()

VISIBLE = {"brand", "portrait"}


def utcnow():
    return datetime.now(timezone.utc)


def db():
    return psycopg2.connect(DSN)


def authorised(handler: BaseHTTPRequestHandler) -> bool:
    if not SECRET:
        return False
    header = handler.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return False
    got = header[7:].encode()
    exp = SECRET.encode()
    if len(got) != len(exp):
        return False
    acc = 0
    for a, b in zip(got, exp):
        acc |= a ^ b
    return acc == 0


def claim_tasks(limit: int = 8) -> list[dict]:
    sql = """
    UPDATE "agentTask" t
    SET "leasedUntil" = NOW() + interval '5 minutes',
        attempts = attempts + 1,
        "startedAt" = COALESCE("startedAt", NOW())
    WHERE t.id IN (
      SELECT id FROM "agentTask"
      WHERE "finishedAt" IS NULL
        AND "dueAt" <= NOW()
        AND ("leasedUntil" IS NULL OR "leasedUntil" < NOW())
        AND attempts < 8
      ORDER BY priority DESC, "dueAt" ASC
      LIMIT %s
      FOR UPDATE SKIP LOCKED
    )
    RETURNING *
    """
    with db() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.commit()
    return rows


def finish_task(task_id: str, outcome: str, session_id: str | None) -> None:
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "agentTask"
            SET "finishedAt" = NOW(), outcome = %s, "sessionId" = %s, "leasedUntil" = NULL
            WHERE id = %s
            """,
            (outcome[:500], session_id, task_id),
        )
        conn.commit()


def ask_reed(task: dict) -> dict:
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": "Decide this CRM task. Do not invent facts.\n"
                + json.dumps(
                    {
                        "id": task.get("id"),
                        "kind": task.get("kind"),
                        "reason": task.get("reason"),
                        "subject": task.get("subject"),
                        "contactId": task.get("contactId"),
                        "companyId": task.get("companyId"),
                        "dealId": task.get("dealId"),
                        "budget": task.get("budget"),
                        "attempts": task.get("attempts"),
                    },
                    default=str,
                ),
            },
        ],
        "temperature": 0.1,
    }
    req = Request(
        f"{LLM_BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer local"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode())
        text = body["choices"][0]["message"]["content"]
    except Exception as exc:
        return {"decision": "hold", "why": f"llm error: {exc}", "kind": "none"}
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0:
        return {"decision": "hold", "why": "model returned no JSON", "kind": "none"}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"decision": "hold", "why": "invalid JSON from model", "kind": "none"}


def drain() -> dict:
    claimed = claim_tasks()
    results = []
    for task in claimed:
        kind = task.get("kind") or ""
        session_id = f"hermes-{uuid.uuid4().hex[:16]}"
        if kind in VISIBLE:
            finish_task(task["id"], "visible-lane: no model decision", session_id)
            results.append({"id": task["id"], "kind": kind, "decision": "skip"})
            continue
        decision = ask_reed(task)
        outcome = json.dumps(decision, default=str)[:500]
        finish_task(task["id"], outcome, session_id)
        results.append({"id": task["id"], "kind": kind, "decision": decision.get("decision")})
    return {"claimed": len(claimed), "results": results}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[reed]", self.address_string(), fmt % args)

    def _json(self, code: int, obj: dict) -> None:
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/health", "/eve/v1/health"):
            self._json(200, {"ok": True, "agent": "reed", "backend": "hermes"})
            return
        if path == "/eve/v1/info":
            self._json(
                200,
                {
                    "name": "reed",
                    "framework": "hermes",
                    "model": LLM_MODEL,
                    "diagnostics": 0,
                    "tools": ["read_crm_history", "record_fact", "schedule_recheck"],
                    "note": "eve replaced by Hermes Reed",
                },
            )
            return
        if path == "/internal/crm/dispatch-health":
            if not authorised(self):
                self._json(401, {"error": "unauthorized"})
                return
            self._json(200, {"ok": True, "inflight": False})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path in (
            "/internal/crm/dispatch",
            "/internal/crm/agent-dispatch",
            "/internal/crm/builder-dispatch",
        ):
            if not authorised(self):
                self._json(401, {"error": "unauthorized"})
                return
            result = drain()
            self._json(200, result)
            return
        if path.startswith("/eve/v1/session"):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode() or "{}")
            except json.JSONDecodeError:
                body = {}
            msg = body.get("message") or body.get("text") or "What should I work on next?"
            fake_task = {
                "id": "chat",
                "kind": "requested",
                "reason": msg,
                "subject": body.get("subject"),
            }
            decision = ask_reed(fake_task)
            self._json(200, {"agent": "reed", "decision": decision})
            return
        self._json(404, {"error": "not found"})


def loop():
    while True:
        try:
            drain()
        except Exception as exc:
            print("[reed] drain", exc)
        time.sleep(30)


def main():
    print(f"[reed] hermes CRM agent on :{PORT} model={LLM_MODEL}")
    threading.Thread(target=loop, daemon=True).start()
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
