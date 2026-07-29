"""Flat-file persistence for orders.

The pilot runs on a single box; a JSON file under data/ stands in for the
real database until the storefront migration lands.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Order, OrderLine, OrderStatus


class OrderStore:
    def __init__(self, orders=None):
        self._orders: dict[str, Order] = {}
        for order in orders or []:
            self._orders[order.order_id] = order

    def add(self, order: Order) -> None:
        self._orders[order.order_id] = order

    def get(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def all(self) -> list[Order]:
        return sorted(self._orders.values(), key=lambda o: o.order_id)

    @classmethod
    def load(cls, path: str | Path) -> "OrderStore":
        payload = json.loads(Path(path).read_text())
        orders = []
        for raw in payload["orders"]:
            lines = [OrderLine(**line) for line in raw["lines"]]
            orders.append(
                Order(
                    order_id=raw["order_id"],
                    customer_email=raw["customer_email"],
                    status=OrderStatus(raw["status"]),
                    lines=lines,
                    carrier=raw.get("carrier"),
                )
            )
        return cls(orders)

    def save(self, path: str | Path) -> None:
        payload = {
            "orders": [
                {
                    "order_id": o.order_id,
                    "customer_email": o.customer_email,
                    "status": o.status.value,
                    "carrier": o.carrier,
                    "lines": [
                        {
                            "sku": line.sku,
                            "description": line.description,
                            "quantity_ordered": line.quantity_ordered,
                            "quantity_shipped": line.quantity_shipped,
                        }
                        for line in o.lines
                    ],
                }
                for o in self.all()
            ]
        }
        Path(path).write_text(json.dumps(payload, indent=2) + "\n")
