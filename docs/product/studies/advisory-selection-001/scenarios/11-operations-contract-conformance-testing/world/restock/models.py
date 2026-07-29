"""Domain records shared by the client, store, and sync layers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AvailabilityRecord:
    sku: str
    quantity: int
    unit_price_cents: int
    warehouse: str
    discount_pct: float
    restock_eta: str | None
