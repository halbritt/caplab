"""End-to-end export: read orders, enrich, format, write the feed file."""

from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Iterator

from orderfeed.enrich import enrich_order
from orderfeed.legacy_format import format_row
from orderfeed.models import Order


def read_orders(orders_path: str | Path) -> Iterator[Order]:
    """Yield orders from the commerce CSV export."""
    with open(orders_path, newline="") as fh:
        for rec in csv.DictReader(fh):
            yield Order(
                order_id=rec["order_id"],
                sku=rec["sku"],
                quantity=int(rec["quantity"]),
                unit_price=Decimal(rec["unit_price"]),
                currency=rec["currency"],
                placed_at=datetime.fromisoformat(rec["placed_at"]),
            )


def run_export(
    orders_path: str | Path, rates_path: str | Path, out_path: str | Path
) -> int:
    """Write the FLATFEED v2 file; returns the number of rows written."""
    count = 0
    with open(out_path, "w") as out:
        for order in read_orders(orders_path):
            enriched = enrich_order(order, rates_path)
            out.write(format_row(enriched) + "\n")
            count += 1
    return count
