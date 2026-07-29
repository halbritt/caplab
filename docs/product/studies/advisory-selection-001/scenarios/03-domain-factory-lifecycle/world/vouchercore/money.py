"""Monetary values for the voucher service."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from vouchercore.errors import CurrencyMismatch, InvalidAmount

SUPPORTED_CURRENCIES = frozenset({"EUR", "GBP", "USD"})

_CENTS = Decimal("0.01")


class Money:
    """An amount in a single currency.

    Production code obtains instances through :meth:`MoneyFactory.create`,
    which normalises and validates the inputs.
    """

    __slots__ = ("amount", "currency")

    def __init__(self, amount: Decimal, currency: str) -> None:
        self.amount = amount
        self.currency = currency

    def plus(self, other: "Money") -> "Money":
        self._require_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def minus(self, other: "Money") -> "Money":
        self._require_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def is_zero(self) -> bool:
        return self.amount == 0

    def _require_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise CurrencyMismatch(
                f"cannot combine {self.currency} with {other.currency}"
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __repr__(self) -> str:
        return f"Money({self.amount!s} {self.currency})"


class MoneyFactory:
    """Creation point for :class:`Money`; the validation lives here."""

    @staticmethod
    def create(amount: object, currency: str) -> Money:
        try:
            value = Decimal(str(amount)).quantize(_CENTS, rounding=ROUND_HALF_UP)
        except InvalidOperation as exc:
            raise InvalidAmount(f"not a monetary amount: {amount!r}") from exc
        if value < 0:
            raise InvalidAmount("amount must not be negative")
        code = currency.strip().upper()
        if code not in SUPPORTED_CURRENCIES:
            raise InvalidAmount(f"unsupported currency: {currency!r}")
        return Money(value, code)
