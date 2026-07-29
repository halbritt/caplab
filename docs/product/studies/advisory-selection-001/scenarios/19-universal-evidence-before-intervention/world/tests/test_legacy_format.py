from datetime import datetime
from decimal import Decimal

from orderfeed.legacy_format import format_row
from orderfeed.models import EnrichedOrder, Order


def _enriched(**overrides):
    order_kwargs = dict(
        order_id="ORD-9001",
        sku="WIDGET-STD",
        quantity=3,
        unit_price=Decimal("9.00"),
        currency="USD",
        placed_at=datetime(2026, 7, 27, 21, 14, 5),
    )
    order_kwargs.update(
        {k: v for k, v in overrides.items() if k in order_kwargs}
    )
    return EnrichedOrder(
        order=Order(**order_kwargs),
        fx_rate=overrides.get("fx_rate", Decimal("0.9123")),
        settlement_amount=overrides.get("settlement_amount", Decimal("24.63")),
    )


def test_row_layout_is_byte_exact():
    # The partner rejects the whole batch on any layout drift, so this is
    # pinned byte for byte.
    row = format_row(_enriched())
    assert row == (
        "ORD-9001    |WIDGET-STD      |3    |USD|"
        "0.9123    |24.63         |2026-07-27 21:14:05"
    )


def test_pipes_and_backslashes_are_escaped():
    row = format_row(_enriched(sku="A|B\\C"))
    fields = row.split("|")
    # sku field is escaped, so splitting on raw pipes yields the escaped
    # pieces "A\|B\\C" spread across the padded 16-char cell.
    assert "A\\|B\\\\C" in row
    assert row.startswith("ORD-9001    |")
    assert len(fields) > 7  # escaped pipe adds an apparent field


def test_overlong_values_are_truncated_to_column_width():
    row = format_row(_enriched(order_id="ORD-2026-0001234567"))
    assert row.split("|")[0] == "ORD-2026-000"


def test_embedded_newlines_become_spaces():
    row = format_row(_enriched(sku="TWO\nLINES"))
    assert "\n" not in row
    assert "TWO LINES" in row
