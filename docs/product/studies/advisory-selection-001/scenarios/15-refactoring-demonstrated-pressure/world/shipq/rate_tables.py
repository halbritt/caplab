"""Negotiated base rates. Values current as of the 2026-04 rate card."""

# (carrier, zone) -> price per billable kg
BASE_RATE_PER_KG = {
    ("DPX", 1): 4.20,
    ("DPX", 2): 5.10,
    ("DPX", 3): 6.80,
    ("ARO", 1): 3.90,
    ("ARO", 2): 4.75,
    ("ARO", 3): 6.20,
}

# floor applied to the subtotal before surcharges
MINIMUM_CHARGE = {
    "DPX": 9.50,
    "ARO": 8.75,
}
