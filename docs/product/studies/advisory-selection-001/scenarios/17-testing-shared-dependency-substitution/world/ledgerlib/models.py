"""Value objects shared across ledgerlib."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ledgerlib.errors import CurrencyMismatchError


@dataclass(frozen=True)
class Money:
    """An amount in minor units (cents) of a single currency."""

    cents: int
    currency: str = "USD"

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise CurrencyMismatchError(
                f"cannot add {other.currency} to {self.currency}"
            )
        return Money(self.cents + other.cents, self.currency)

    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        return cls(0, currency)

    def __str__(self) -> str:
        sign = "-" if self.cents < 0 else ""
        magnitude = abs(self.cents)
        return f"{sign}{magnitude // 100}.{magnitude % 100:02d} {self.currency}"


@dataclass(frozen=True)
class Account:
    account_id: str
    name: str
    currency: str = "USD"


@dataclass(frozen=True)
class Posting:
    posting_id: int
    account_id: str
    amount: Money
    category: str
    posted_on: date
    memo: str = ""


@dataclass(frozen=True)
class Statement:
    """All postings for one calendar month, in date order."""

    year: int
    month: int
    lines: tuple[Posting, ...]

    @property
    def total(self) -> Money:
        if not self.lines:
            return Money.zero()
        total = Money.zero(self.lines[0].amount.currency)
        for line in self.lines:
            total = total + line.amount
        return total
