"""Data access for trackd.

Repositories are thin: they run SQL on the connection they are given and
never manage transactions. The caller that opened the connection owns the
unit of work and decides when it is finalized.
"""

from __future__ import annotations

import sqlite3


class ShipmentRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # -- shipments ---------------------------------------------------------

    def insert_shipment(self, tracking_id: str, carrier: str, origin: str) -> None:
        self._conn.execute(
            "INSERT INTO shipments (tracking_id, carrier, origin) VALUES (?, ?, ?)",
            (tracking_id, carrier, origin),
        )

    def get_shipment(self, tracking_id: str) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT tracking_id, carrier, origin, registered_at"
            " FROM shipments WHERE tracking_id = ?",
            (tracking_id,),
        ).fetchone()

    # -- scan events -------------------------------------------------------

    def insert_scan(self, tracking_id: str, status: str, location: str) -> int:
        cursor = self._conn.execute(
            "INSERT INTO scan_events (tracking_id, status, location) VALUES (?, ?, ?)",
            (tracking_id, status, location),
        )
        return int(cursor.lastrowid)

    def events_for(self, tracking_id: str) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT event_id, tracking_id, status, location, scanned_at"
            " FROM scan_events WHERE tracking_id = ?"
            " ORDER BY event_id",
            (tracking_id,),
        ).fetchall()

    def latest_event(self, tracking_id: str) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT event_id, tracking_id, status, location, scanned_at"
            " FROM scan_events WHERE tracking_id = ?"
            " ORDER BY event_id DESC LIMIT 1",
            (tracking_id,),
        ).fetchone()

    def status_counts(self) -> list[sqlite3.Row]:
        """Shipment counts grouped by each shipment's most recent status."""
        return self._conn.execute(
            """
            SELECT COALESCE(e.status, 'registered') AS status,
                   COUNT(*)                          AS n
              FROM shipments s
              LEFT JOIN scan_events e
                ON e.tracking_id = s.tracking_id
               AND e.event_id = (
                       SELECT MAX(event_id)
                         FROM scan_events
                        WHERE tracking_id = s.tracking_id
                   )
             GROUP BY COALESCE(e.status, 'registered')
            """
        ).fetchall()
