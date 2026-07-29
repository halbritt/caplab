"""The metering database.

In production this is ``meter.db`` on the shared volume mounted on every
worker — all instances see the same data. Ingest appends usage events;
the nightly worker folds them into per-day, per-customer rollups. The
sqlite backend here mirrors that schema and is what the tests run
against.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass

from meterd.assignment import shard_of

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    customer    TEXT    NOT NULL,
    shard       INTEGER NOT NULL,
    day         TEXT    NOT NULL,
    quantity    REAL    NOT NULL,
    recorded_at REAL    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_shard_seq ON events (shard, seq);

CREATE TABLE IF NOT EXISTS rollups (
    day        TEXT NOT NULL,
    customer   TEXT NOT NULL,
    total      REAL NOT NULL,
    updated_at REAL NOT NULL,
    PRIMARY KEY (day, customer)
);
"""


@dataclass(frozen=True)
class Event:
    seq: int
    customer: str
    shard: int
    day: str
    quantity: float
    recorded_at: float


class MeteringStore:
    """Thin data-access layer over the metering database."""

    def __init__(self, path: str = ":memory:", *, shard_count: int = 8) -> None:
        self.shard_count = shard_count
        self._conn = sqlite3.connect(path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- events ---------------------------------------------------------

    def add_event(
        self,
        customer: str,
        day: str,
        quantity: float,
        recorded_at: float | None = None,
    ) -> int:
        """Append one usage event (this is what ingest calls)."""
        if recorded_at is None:
            recorded_at = time.time()
        shard = shard_of(customer, self.shard_count)
        cur = self._conn.execute(
            "INSERT INTO events (customer, shard, day, quantity, recorded_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (customer, shard, day, quantity, recorded_at),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def events_for_shard(
        self,
        shard: int,
        *,
        after_seq: int = 0,
        up_to: float | None = None,
    ) -> list[Event]:
        """Events in *shard* newer than *after_seq*, oldest first.

        *up_to* optionally bounds ``recorded_at``.
        """
        sql = (
            "SELECT seq, customer, shard, day, quantity, recorded_at"
            " FROM events WHERE shard = ? AND seq > ?"
        )
        params: list[object] = [shard, after_seq]
        if up_to is not None:
            sql += " AND recorded_at <= ?"
            params.append(up_to)
        sql += " ORDER BY seq"
        rows = self._conn.execute(sql, params).fetchall()
        return [Event(*row) for row in rows]

    # -- rollups --------------------------------------------------------

    def apply_rollup(
        self,
        day: str,
        customer: str,
        delta: float,
        updated_at: float | None = None,
    ) -> None:
        """Fold *delta* into the (day, customer) rollup."""
        if updated_at is None:
            updated_at = time.time()
        self._conn.execute(
            "INSERT INTO rollups (day, customer, total, updated_at)"
            " VALUES (?, ?, ?, ?)"
            " ON CONFLICT (day, customer) DO UPDATE SET"
            "   total = total + excluded.total,"
            "   updated_at = excluded.updated_at",
            (day, customer, delta, updated_at),
        )
        self._conn.commit()

    def rollup_total(self, day: str, customer: str) -> float | None:
        row = self._conn.execute(
            "SELECT total FROM rollups WHERE day = ? AND customer = ?",
            (day, customer),
        ).fetchone()
        return None if row is None else float(row[0])

    def rollups_for_day(self, day: str) -> list[tuple[str, float]]:
        rows = self._conn.execute(
            "SELECT customer, total FROM rollups WHERE day = ? ORDER BY customer",
            (day,),
        ).fetchall()
        return [(str(c), float(t)) for c, t in rows]
