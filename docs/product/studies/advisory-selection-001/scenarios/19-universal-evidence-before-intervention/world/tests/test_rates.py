from datetime import datetime
from decimal import Decimal

import pytest

from orderfeed import rates

RATES_CSV = """currency,valid_from,rate
USD,2026-01-01,0.9100
USD,2026-03-01,0.9250
GBP,2026-01-01,1.1700
JPY,2026-02-15,0.006200
"""


@pytest.fixture()
def rates_file(tmp_path):
    p = tmp_path / "rates.csv"
    p.write_text(RATES_CSV)
    return p


def test_snapshot_picks_newest_effective_row(rates_file):
    snap = rates.rates_as_of(rates_file, datetime(2026, 3, 15, 12, 30, 5))
    assert snap["USD"] == Decimal("0.9250")
    assert snap["GBP"] == Decimal("1.1700")


def test_snapshot_ignores_rows_not_yet_effective(rates_file):
    snap = rates.rates_as_of(rates_file, datetime(2026, 2, 10, 9, 0, 0))
    assert snap["USD"] == Decimal("0.9100")  # March row not effective yet
    assert "JPY" not in snap  # first JPY row is 2026-02-15


def test_snapshot_effective_from_its_own_day(rates_file):
    snap = rates.rates_as_of(rates_file, datetime(2026, 3, 1, 0, 0, 1))
    assert snap["USD"] == Decimal("0.9250")


def test_convert_quantizes_to_cents(rates_file):
    snap = rates.rates_as_of(rates_file, datetime(2026, 3, 15, 8, 0, 0))
    assert rates.convert(Decimal("19.99"), "USD", snap) == Decimal("18.49")


def test_convert_unknown_currency_raises(rates_file):
    snap = rates.rates_as_of(rates_file, datetime(2026, 3, 15, 8, 0, 0))
    with pytest.raises(rates.RateLookupError):
        rates.convert(Decimal("10.00"), "XXX", snap)
