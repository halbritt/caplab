"""Core records for the OrderDesk pilot.

OrderDesk tracks customer orders for the KeebSupply storefront and keeps
customers informed as the warehouse works through them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class OrderStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


@dataclass
class OrderLine:
    sku: str
    description: str
    quantity_ordered: int
    quantity_shipped: int = 0

    @property
    def outstanding(self) -> int:
        return max(self.quantity_ordered - self.quantity_shipped, 0)


@dataclass
class Order:
    order_id: str
    customer_email: str
    status: OrderStatus = OrderStatus.OPEN
    lines: list[OrderLine] = field(default_factory=list)
    carrier: str | None = None

    def line_for(self, sku: str) -> OrderLine | None:
        for line in self.lines:
            if line.sku == sku:
                return line
        return None
