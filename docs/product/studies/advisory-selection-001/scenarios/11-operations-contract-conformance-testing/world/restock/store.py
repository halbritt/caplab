"""SQLite-backed store for the last-synced availability snapshot."""

import sqlite3

from restock.models import AvailabilityRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS availability (
    sku              TEXT NOT NULL,
    warehouse        TEXT NOT NULL,
    quantity         INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    discount_pct     REAL NOT NULL,
    restock_eta      TEXT,
    PRIMARY KEY (sku, warehouse)
)
"""


class InventoryStore:
    def __init__(self, path: str = ":memory:"):
        self._conn = sqlite3.connect(path)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def get(self, sku: str, warehouse: str) -> AvailabilityRecord | None:
        row = self._conn.execute(
            "SELECT sku, warehouse, quantity, unit_price_cents, discount_pct, restock_eta"
            " FROM availability WHERE sku = ? AND warehouse = ?",
            (sku, warehouse),
        ).fetchone()
        if row is None:
            return None
        return AvailabilityRecord(
            sku=row[0],
            warehouse=row[1],
            quantity=row[2],
            unit_price_cents=row[3],
            discount_pct=row[4],
            restock_eta=row[5],
        )

    def upsert(self, record: AvailabilityRecord) -> str:
        """Insert or update one record; returns 'added', 'updated', or 'unchanged'."""
        existing = self.get(record.sku, record.warehouse)
        if existing == record:
            return "unchanged"
        self._conn.execute(
            "INSERT INTO availability"
            " (sku, warehouse, quantity, unit_price_cents, discount_pct, restock_eta)"
            " VALUES (?, ?, ?, ?, ?, ?)"
            " ON CONFLICT (sku, warehouse) DO UPDATE SET"
            " quantity = excluded.quantity,"
            " unit_price_cents = excluded.unit_price_cents,"
            " discount_pct = excluded.discount_pct,"
            " restock_eta = excluded.restock_eta",
            (
                record.sku,
                record.warehouse,
                record.quantity,
                record.unit_price_cents,
                record.discount_pct,
                record.restock_eta,
            ),
        )
        self._conn.commit()
        return "updated" if existing is not None else "added"

    def skus_for_warehouse(self, warehouse: str) -> set[str]:
        rows = self._conn.execute(
            "SELECT sku FROM availability WHERE warehouse = ?", (warehouse,)
        )
        return {row[0] for row in rows}

    def delete(self, sku: str, warehouse: str) -> None:
        self._conn.execute(
            "DELETE FROM availability WHERE sku = ? AND warehouse = ?", (sku, warehouse)
        )
        self._conn.commit()
