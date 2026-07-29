"""Money-string parsing for bank CSV exports.

The banks are not consistent with each other: thousands separators, currency
symbols, parenthesised negatives, and the occasional trailing ``CR``/``DR``
marker all appear in the wild. Everything is normalised to integer cents so
the ledger never does float arithmetic.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

_CURRENCY = re.compile(r"[€$£]")
_TRAILER = re.compile(r"\s*(CR|DR)\s*$", re.IGNORECASE)


def parse_amount(text: str | None) -> int:
    """Parse a bank-export amount string into integer cents.

    Raises ValueError if the string is not a recognisable amount.
    """
    if text is None:
        raise ValueError("amount is missing")
    raw = text.strip()
    if not raw:
        raise ValueError("amount is empty")

    negative = False
    trailer = _TRAILER.search(raw)
    if trailer:
        negative = trailer.group(1).upper() == "DR"
        raw = raw[: trailer.start()].strip()

    raw = _CURRENCY.sub("", raw).strip()
    if raw.startswith("(") and raw.endswith(")"):
        negative = True
        raw = raw[1:-1].strip()
    raw = raw.replace(",", "")

    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"unrecognisable amount: {text!r}") from exc

    cents = int((value.copy_abs() * 100).to_integral_value())
    return -cents if negative or value < 0 else cents
