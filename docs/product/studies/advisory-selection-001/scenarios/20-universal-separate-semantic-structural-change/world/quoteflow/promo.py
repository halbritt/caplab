"""Promotional codes. Marketing owns the table; codes are case-insensitive."""

from decimal import Decimal

DISCOUNTS = {
    "WELCOME10": Decimal("0.10"),
    "SAVE15": Decimal("0.15"),
    "BULK20": Decimal("0.20"),
}


class UnknownPromoCode(ValueError):
    pass


def resolve_discount(code: str) -> Decimal:
    try:
        return DISCOUNTS[code.strip().upper()]
    except KeyError:
        raise UnknownPromoCode(code) from None
