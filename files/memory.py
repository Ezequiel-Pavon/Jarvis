"""Persistent conversation memory backed by SQLite.

Keeps the last N exchanges so the assistant has short-term context
across turns, and stores everything so it can be inspected or
exported later.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from config import CONFIG

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


@contextmanager
def _connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


class Memory:
    def __init__(self, db_path: Path = CONFIG.memory_db, context_turns: int = 10):
        self.db_path = db_path
        self.context_turns = context_turns
        with _connection(self.db_path) as conn:
            conn.execute(SCHEMA)

    def add(self, role: str, content: str) -> None:
        with _connection(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (role, content, created_at) VALUES (?, ?, ?)",
                (role, content, datetime.utcnow().isoformat()),
            )

    def recent(self) -> list[dict]:
        """Return the last `context_turns` exchanges, oldest first."""
        with _connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content FROM conversations "
                "ORDER BY id DESC LIMIT ?",
                (self.context_turns * 2,),
            ).fetchall()
        rows.reverse()
        return [{"role": role, "content": content} for role, content in rows]

    def clear(self) -> None:
        with _connection(self.db_path) as conn:
            conn.execute("DELETE FROM conversations")
