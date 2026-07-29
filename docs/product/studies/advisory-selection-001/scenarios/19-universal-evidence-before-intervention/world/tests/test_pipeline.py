from datetime import datetime
from decimal import Decimal

import pytest

from orderfeed.pipeline import read_orders, run_export

ORDERS_CSV = """order_id,sku,quantity,unit_price,currency,placed_at
ORD-1,CABLE-2M,2,10.00,USD,2026-07-01 03:15:09
ORD-2,DOCK-PRO,1,199.50,GBP,2026-07-01 03:16:44
ORD-3,MIC-USB,4,45.25,USD,2026-07-01 03:18:02
"""

RATES_CSV = """currency,valid_from,rate
USD,2026-06-30,0.9000
GBP,2026-06-30,1.2000
"""


@pytest.fixture()
def data_files(tmp_path):
    orders = tmp_path / "orders.csv"
    orders.write_text(ORDERS_CSV)
    ratesf = tmp_path / "rates.csv"
    ratesf.write_text(RATES_CSV)
    out = tmp_path / "feed.txt"
    return orders, ratesf, out


def test_read_orders_parses_types(data_files):
    orders, _, _ = data_files
    first = next(read_orders(orders))
    assert first.order_id == "ORD-1"
    assert first.quantity == 2
    assert first.unit_price == Decimal("10.00")
    assert first.placed_at == datetime(2026, 7, 1, 3, 15, 9)


def test_run_export_writes_one_row_per_order(data_files):
    orders, ratesf, out = data_files
    count = run_export(orders, ratesf, out)
    assert count == 3
    lines = out.read_text().splitlines()
    assert len(lines) == 3


def test_run_export_row_content(data_files):
    orders, ratesf, out = data_files
    run_export(orders, ratesf, out)
    first = out.read_text().splitlines()[0]
    # 2 x 10.00 USD at 0.9000 -> 18.00 EUR
    assert first == (
        "ORD-1       |CABLE-2M        |2    |USD|"
        "0.9000    |18.00         |2026-07-01 03:15:09"
    )
