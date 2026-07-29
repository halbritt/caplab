"""Dataclasses shared by the quoting modules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Parcel:
    weight_kg: Decimal
    length_cm: int = 0
    width_cm: int = 0
    height_cm: int = 0
    destination_postcode: str = ""


@dataclass(frozen=True)
class Quote:
    service: str
    transport: Decimal
    surcharges: Decimal
    discount: Decimal
    total: Decimal

    def breakdown(self) -> str:
        lines = [
            f"{self.service} transport {self.transport:>9}",
            f"surcharges         {self.surcharges:>9}",
        ]
        if self.discount:
            lines.append(f"promo discount    -{self.discount:>9}")
        lines.append(f"total              {self.total:>9}")
        return "\n".join(lines)
