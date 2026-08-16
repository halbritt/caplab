"""SQLite-backed store of catalog items."""

from __future__ import annotations

import json
import sqlite3
import time

_SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price_cents INTEGER NOT NULL DEFAULT 0,
    tags        TEXT NOT NULL DEFAULT '[]',
    updated_at  REAL NOT NULL
);
"""

_FIELDS = {"name", "description", "price_cents", "tags"}


class ItemNotFound(KeyError):
    """Raised when an item id is absent from the store."""


class CatalogStore:
    """Owns the `items` table. Callers get plain dicts back."""

    def __init__(self, path: str = ":memory:"):
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)

    def create(
        self,
        item_id: str,
        name: str,
        description: str = "",
        price_cents: int = 0,
        tags=(),
    ) -> dict:
        try:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO items (id, name, description, price_cents, tags, updated_at)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (item_id, name, description, price_cents,
                     json.dumps(list(tags)), time.time()),
                )
        except sqlite3.IntegrityError:
            raise ValueError(f"item already exists: {item_id}") from None
        return self.get(item_id)

    def update(self, item_id: str, **fields) -> dict:
        unknown = set(fields) - _FIELDS
        if unknown:
            raise ValueError(f"unknown fields: {sorted(unknown)}")
        if not fields:
            return self.get(item_id)
        pairs = sorted(fields.items())
        assignments = ", ".join([f"{key} = ?" for key, _ in pairs] + ["updated_at = ?"])
        values = [json.dumps(list(v)) if k == "tags" else v for k, v in pairs]
        args = [*values, time.time(), item_id]
        with self._conn:
            cur = self._conn.execute(
                f"UPDATE items SET {assignments} WHERE id = ?", args
            )
            if cur.rowcount == 0:
                raise ItemNotFound(item_id)
        return self.get(item_id)

    def delete(self, item_id: str) -> None:
        with self._conn:
            cur = self._conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
            if cur.rowcount == 0:
                raise ItemNotFound(item_id)

    def get(self, item_id: str) -> dict:
        row = self._conn.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if row is None:
            raise ItemNotFound(item_id)
        return self._to_item(row)

    def all_items(self) -> list[dict]:
        rows = self._conn.execute("SELECT * FROM items").fetchall()
        return sorted((self._to_item(r) for r in rows), key=lambda i: i["id"])

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def _to_item(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "price_cents": row["price_cents"],
            "tags": json.loads(row["tags"]),
            "updated_at": row["updated_at"],
        }
