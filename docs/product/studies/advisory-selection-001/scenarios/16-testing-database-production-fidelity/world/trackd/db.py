"""Connection handling for trackd.

Production runs a file-backed SQLite database in WAL mode on the warehouse
gateway. Every request opens its own connection, does its work, and releases
it; there is no pool and no long-lived connection.
"""

from __future__ import annotations

import os
import sqlite3

DEFAULT_URL = "sqlite:///trackd.db"
_SQLITE_PREFIX = "sqlite:///"


def database_url() -> str:
    """The configured database URL (environment override, then default)."""
    return os.environ.get("TRACKD_DATABASE_URL", DEFAULT_URL)


def connect(url: str | None = None) -> sqlite3.Connection:
    """Open a new connection with production pragmas applied.

    Callers own the connection: they decide when the unit of work is
    finalized and when the connection is released.
    """
    url = url or database_url()
    if not url.startswith(_SQLITE_PREFIX):
        raise ValueError(f"unsupported database url: {url!r}")
    path = url[len(_SQLITE_PREFIX):]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
    return conn
