"""SQLite-backed storage for short links.

All queries are parameterized. Each operation opens a short-lived
connection so the module is safe to use from FastAPI's threadpool.
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

DEFAULT_DB_PATH = os.environ.get("SHORTENER_DB", "shortener.db")


@dataclass
class Link:
    code: str
    url: str
    created_at: str
    hits: int


class DuplicateCodeError(Exception):
    """Raised when inserting a code that already exists."""


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _resolve(db_path: Optional[str]) -> str:
    """Return the given path, or the current module default.

    Resolved at call time (not as a default-argument value) so tests can
    monkeypatch ``DEFAULT_DB_PATH`` and have it take effect.
    """
    return db_path if db_path is not None else DEFAULT_DB_PATH


def init_db(db_path: Optional[str] = None) -> None:
    """Create the links table if it does not already exist."""
    db_path = _resolve(db_path)
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                code TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                hits INTEGER NOT NULL DEFAULT 0
            )
            """
        )


def create_link(code: str, url: str, db_path: Optional[str] = None) -> Link:
    """Insert a new link. Raises DuplicateCodeError if the code exists."""
    db_path = _resolve(db_path)
    created_at = datetime.now(timezone.utc).isoformat()
    try:
        with _connect(db_path) as conn:
            conn.execute(
                "INSERT INTO links (code, url, created_at, hits) VALUES (?, ?, ?, 0)",
                (code, url, created_at),
            )
    except sqlite3.IntegrityError as exc:
        raise DuplicateCodeError(code) from exc
    return Link(code=code, url=url, created_at=created_at, hits=0)


def get_link(code: str, db_path: Optional[str] = None) -> Optional[Link]:
    """Return the link for ``code`` or None if it does not exist."""
    db_path = _resolve(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT code, url, created_at, hits FROM links WHERE code = ?",
            (code,),
        ).fetchone()
    if row is None:
        return None
    return Link(**dict(row))


def list_links(db_path: Optional[str] = None) -> list[Link]:
    """Return all links ordered by creation time (newest first)."""
    db_path = _resolve(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT code, url, created_at, hits FROM links ORDER BY created_at DESC"
        ).fetchall()
    return [Link(**dict(row)) for row in rows]


def delete_link(code: str, db_path: Optional[str] = None) -> bool:
    """Delete the link for ``code``. Returns True if a row was removed."""
    db_path = _resolve(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM links WHERE code = ?", (code,))
        return cur.rowcount > 0


def record_hit(code: str, db_path: Optional[str] = None) -> None:
    """Increment the hit counter for ``code`` (no-op if missing)."""
    db_path = _resolve(db_path)
    with _connect(db_path) as conn:
        conn.execute("UPDATE links SET hits = hits + 1 WHERE code = ?", (code,))
