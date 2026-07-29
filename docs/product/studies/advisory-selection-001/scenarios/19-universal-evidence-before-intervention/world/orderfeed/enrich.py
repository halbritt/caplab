"""Per-order settlement enrichment."""

from __future__ import annotations

from pathlib import Path

from orderfeed import rates
from orderfeed.models import EnrichedOrder, Order


def enrich_order(order: Order, rates_path: str | Path) -> EnrichedOrder:
    """Attach the effective FX rate and the EUR settlement amount."""
    snapshot = rates.rates_as_of(rates_path, order.placed_at)
    if order.currency not in snapshot:
        raise rates.RateLookupError(order.currency)
    total = order.unit_price * order.quantity
    return EnrichedOrder(
        order=order,
        fx_rate=snapshot[order.currency],
        settlement_amount=rates.convert(total, order.currency, snapshot),
    )
