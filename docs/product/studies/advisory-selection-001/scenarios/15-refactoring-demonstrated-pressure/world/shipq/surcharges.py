"""Surcharge math, shared by quoting and invoicing.

Since 0.4.1 both paths call apply_surcharges(); before that each kept its own
copy, and the remote-area fee was silently missing from invoices for months.
"""

FUEL_PCT = 0.065  # fuel adjustment, reviewed quarterly
REMOTE_ZONES = frozenset({3})
REMOTE_AREA_FEE = 11.00


def apply_surcharges(subtotal: float, zone: int) -> float:
    total = subtotal * (1 + FUEL_PCT)
    if zone in REMOTE_ZONES:
        total += REMOTE_AREA_FEE
    return round(total, 2)
