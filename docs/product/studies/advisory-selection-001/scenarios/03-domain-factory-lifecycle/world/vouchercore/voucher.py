"""The voucher aggregate and its state changes."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from vouchercore.errors import (
    CurrencyMismatch,
    InsufficientBalance,
    InvalidVoucher,
)
from vouchercore.money import Money


class VoucherStatus(str, Enum):
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    VOID = "void"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Voucher:
    """A prepaid gift voucher.

    Instances are assembled by :class:`vouchercore.factory.VoucherFactory`,
    which fills the fields in and checks the result.
    """

    def __init__(self) -> None:
        self.voucher_id: str | None = None
        self.code: str | None = None
        self.balance: Money | None = None
        self.status: VoucherStatus | None = None
        self.issued_at: datetime | None = None
        self.expires_at: datetime | None = None
        self.pending_events: list[dict] = []

    def record_event(self, kind: str, **details: str) -> None:
        self.pending_events.append(
            {"kind": kind, "at": utcnow().isoformat(), "details": details}
        )

    def redeem(self, amount: Money) -> Money:
        if self.status is not VoucherStatus.ACTIVE:
            raise InvalidVoucher(f"voucher {self.code} is {self.status.value}")
        if self.expires_at is not None and utcnow() > self.expires_at:
            raise InvalidVoucher(f"voucher {self.code} has expired")
        if amount.currency != self.balance.currency:
            raise CurrencyMismatch(
                f"voucher {self.code} is denominated in {self.balance.currency}"
            )
        if amount.amount > self.balance.amount:
            raise InsufficientBalance(
                f"voucher {self.code} holds {self.balance.amount}, "
                f"cannot redeem {amount.amount}"
            )
        self.balance = self.balance.minus(amount)
        if self.balance.is_zero():
            self.status = VoucherStatus.EXHAUSTED
        self.record_event(
            "redeemed", amount=str(amount.amount), currency=amount.currency
        )
        return self.balance
