"""2025 rate card constants. Source of truth: docs/pricing-rules.md."""

from decimal import Decimal

STANDARD_FLAGFALL = Decimal("4.95")
STANDARD_PER_KG = Decimal("1.10")

EXPRESS_FLAGFALL = Decimal("9.90")
EXPRESS_PER_KG = Decimal("2.35")
EXPRESS_HANDLING = Decimal("3.00")

MAX_WEIGHT_KG = Decimal("30")
