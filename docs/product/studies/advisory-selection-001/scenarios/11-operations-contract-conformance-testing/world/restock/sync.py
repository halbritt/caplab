"""Reconcile one warehouse's supplier availability into the local store."""

from dataclasses import dataclass

from restock.store import InventoryStore
from restock.supplier_client import SupplierClient


@dataclass(frozen=True)
class SyncSummary:
    warehouse: str
    added: int
    updated: int
    unchanged: int
    removed: int


def sync_warehouse(client: SupplierClient, store: InventoryStore, warehouse: str) -> SyncSummary:
    records = client.fetch_availability(warehouse)
    listed: set[str] = set()
    added = updated = unchanged = 0
    for record in records:
        listed.add(record.sku)
        outcome = store.upsert(record)
        if outcome == "added":
            added += 1
        elif outcome == "updated":
            updated += 1
        else:
            unchanged += 1
    removed = 0
    for sku in store.skus_for_warehouse(warehouse) - listed:
        store.delete(sku, warehouse)
        removed += 1
    return SyncSummary(
        warehouse=warehouse,
        added=added,
        updated=updated,
        unchanged=unchanged,
        removed=removed,
    )
