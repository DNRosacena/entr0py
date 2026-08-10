"""
entr0py.core.session
~~~~~~~~~~~~~~~~~~~~
SQLite-backed scan session management via aiosqlite.

Schema
------
  sessions   (id, name, created_at, scope_json)
  scan_runs  (id, session_id, module_slug, opts_json,
              started_at, finished_at, status, output_path)
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator

import aiosqlite

from entr0py.core.paths import SESSIONS_DB

_DB_PATH = SESSIONS_DB

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    created_at TEXT    NOT NULL,
    scope_json TEXT    NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS scan_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL REFERENCES sessions(id),
    module_slug TEXT    NOT NULL,
    opts_json   TEXT    NOT NULL DEFAULT '{}',
    started_at  TEXT    NOT NULL,
    finished_at TEXT,
    status      TEXT    NOT NULL DEFAULT 'running',   -- running|completed|failed
    output_path TEXT
);
"""


@asynccontextmanager
async def _db() -> AsyncIterator[aiosqlite.Connection]:
    """Open a connection, ensure the schema, and close on exit.

    Used as ``async with _db() as db:`` — the context manager starts the
    aiosqlite worker thread exactly once (doing both ``await aiosqlite.connect``
    *and* ``async with await …`` double-starts it → "threads can only be started once").
    """
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(_DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.executescript(_SCHEMA)
        await conn.commit()
        yield conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

async def create_session(name: str, scope: list[str] | None = None) -> int:
    async with _db() as db:
        cur = await db.execute(
            "INSERT INTO sessions (name, created_at, scope_json) VALUES (?,?,?)",
            (name, _now(), json.dumps(scope or [])),
        )
        await db.commit()
        return cur.lastrowid  # type: ignore[return-value]


async def list_sessions() -> list[dict[str, Any]]:
    async with _db() as db:
        cur = await db.execute("SELECT * FROM sessions ORDER BY created_at DESC")
        return [dict(row) for row in await cur.fetchall()]


async def get_session(session_id: int) -> dict[str, Any] | None:
    async with _db() as db:
        cur = await db.execute("SELECT * FROM sessions WHERE id=?", (session_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def update_scope(session_id: int, scope: list[str]) -> None:
    async with _db() as db:
        await db.execute(
            "UPDATE sessions SET scope_json=? WHERE id=?",
            (json.dumps(scope), session_id),
        )
        await db.commit()


# ---------------------------------------------------------------------------
# Scan run CRUD
# ---------------------------------------------------------------------------

async def start_run(session_id: int, module_slug: str, opts: dict[str, Any]) -> int:
    async with _db() as db:
        cur = await db.execute(
            "INSERT INTO scan_runs (session_id, module_slug, opts_json, started_at) VALUES (?,?,?,?)",
            (session_id, module_slug, json.dumps(opts), _now()),
        )
        await db.commit()
        return cur.lastrowid  # type: ignore[return-value]


async def finish_run(
    run_id: int,
    status: str = "completed",
    output_path: str | None = None,
) -> None:
    async with _db() as db:
        await db.execute(
            "UPDATE scan_runs SET finished_at=?, status=?, output_path=? WHERE id=?",
            (_now(), status, output_path, run_id),
        )
        await db.commit()


async def list_runs(session_id: int) -> list[dict[str, Any]]:
    async with _db() as db:
        cur = await db.execute(
            "SELECT * FROM scan_runs WHERE session_id=? ORDER BY started_at DESC",
            (session_id,),
        )
        return [dict(row) for row in await cur.fetchall()]
