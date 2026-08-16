"""Schema for trackd. All DDL is idempotent."""

from __future__ import annotations

import sqlite3

_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS shipments (
        tracking_id   TEXT PRIMARY KEY,
        carrier       TEXT NOT NULL,
        origin        TEXT NOT NULL,
        registered_at TEXT NOT NULL
            DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS scan_events (
        event_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_id TEXT NOT NULL REFERENCES shipments (tracking_id),
        status      TEXT NOT NULL,
        location    TEXT NOT NULL,
        scanned_at  TEXT NOT NULL
            DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_scan_events_tracking
        ON scan_events (tracking_id, event_id)
    """,
)


def apply_schema(conn: sqlite3.Connection) -> None:
    """Create tables and indexes if they do not exist yet."""
    for statement in _STATEMENTS:
        conn.execute(statement)
    conn.commit()
