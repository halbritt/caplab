"""Domain records passed between pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Order:
    """One order row as read from the commerce export."""

    order_id: str
    sku: str
    quantity: int
    unit_price: Decimal  # in the order's own currency
    currency: str  # ISO 4217, e.g. "USD"
    placed_at: datetime


@dataclass(frozen=True)
class EnrichedOrder:
    """An order plus the settlement figures the partner needs."""

    order: Order
    fx_rate: Decimal  # home-currency (EUR) per one unit of order currency
    settlement_amount: Decimal  # order total converted to EUR, 2 dp
