"""Application operations for trackd.

Every public method is a single unit of work: it opens its own connection,
performs its reads and writes, and releases the connection. This mirrors
production, where each scanner-gateway request is handled independently.
"""

from __future__ import annotations

from typing import Any, Callable
import sqlite3

from trackd.db import connect
from trackd.errors import (
    DuplicateShipmentError,
    InvalidStatusError,
    UnknownShipmentError,
)
from trackd.repository import ShipmentRepository

REGISTERED = "registered"

VALID_STATUSES = (
    "in_transit",
    "out_for_delivery",
    "delivered",
    "exception",
    "returned",
)


class TrackingService:
    def __init__(
        self,
        connection_factory: Callable[[], sqlite3.Connection] = connect,
    ) -> None:
        self._connect = connection_factory

    def register_shipment(self, tracking_id: str, carrier: str, origin: str) -> None:
        conn = self._connect()
        try:
            repo = ShipmentRepository(conn)
            if repo.get_shipment(tracking_id) is not None:
                raise DuplicateShipmentError(
                    f"shipment {tracking_id!r} is already registered"
                )
            repo.insert_shipment(tracking_id, carrier, origin)
            conn.commit()
        finally:
            conn.close()

    def record_scan(self, tracking_id: str, status: str, location: str) -> int:
        if status not in VALID_STATUSES:
            raise InvalidStatusError(
                f"status {status!r} is not one of {', '.join(VALID_STATUSES)}"
            )
        conn = self._connect()
        try:
            repo = ShipmentRepository(conn)
            if repo.get_shipment(tracking_id) is None:
                raise UnknownShipmentError(f"no shipment {tracking_id!r}")
            return repo.insert_scan(tracking_id, status, location)
        finally:
            conn.close()

    def latest_status(self, tracking_id: str) -> str:
        conn = self._connect()
        try:
            repo = ShipmentRepository(conn)
            if repo.get_shipment(tracking_id) is None:
                raise UnknownShipmentError(f"no shipment {tracking_id!r}")
            event = repo.latest_event(tracking_id)
            return event["status"] if event is not None else REGISTERED
        finally:
            conn.close()

    def scan_history(self, tracking_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            repo = ShipmentRepository(conn)
            if repo.get_shipment(tracking_id) is None:
                raise UnknownShipmentError(f"no shipment {tracking_id!r}")
            return [dict(row) for row in repo.events_for(tracking_id)]
        finally:
            conn.close()

    def shipment_summary(self, tracking_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            repo = ShipmentRepository(conn)
            shipment = repo.get_shipment(tracking_id)
            if shipment is None:
                raise UnknownShipmentError(f"no shipment {tracking_id!r}")
            event = repo.latest_event(tracking_id)
            return {
                "tracking_id": shipment["tracking_id"],
                "carrier": shipment["carrier"],
                "origin": shipment["origin"],
                "status": event["status"] if event is not None else REGISTERED,
                "last_location": event["location"] if event is not None else None,
                "last_scanned_at": event["scanned_at"] if event is not None else None,
            }
        finally:
            conn.close()

    def network_snapshot(self) -> dict[str, int]:
        """Shipment counts keyed by each shipment's most recent status."""
        conn = self._connect()
        try:
            repo = ShipmentRepository(conn)
            return {row["status"]: row["n"] for row in repo.status_counts()}
        finally:
            conn.close()
