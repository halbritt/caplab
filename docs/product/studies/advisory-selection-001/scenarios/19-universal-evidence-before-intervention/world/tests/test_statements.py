from datetime import datetime

from meterflow.events import UsageEvent
from meterflow.statements import build_statement, month_bounds


def ev(cust, ts, qty):
    return UsageEvent(cust, ts, qty)


def test_month_bounds():
    assert month_bounds("2026-06") == (datetime(2026, 6, 1), datetime(2026, 7, 1))


def test_month_bounds_december_rolls_year():
    assert month_bounds("2026-12") == (datetime(2026, 12, 1), datetime(2027, 1, 1))


def test_statement_totals_one_customer():
    events = [
        ev("C001", datetime(2026, 6, 2, 9, 10), 100.0),
        ev("C001", datetime(2026, 6, 2, 9, 50), 150.0),
        ev("C001", datetime(2026, 6, 17, 22, 5), 250.0),
        ev("C002", datetime(2026, 6, 2, 9, 20), 999.0),  # other customer
    ]
    stmt = build_statement(events, "C001", "2026-06")
    assert stmt.total_units == 500.0
    assert stmt.bucket_count == 2
    assert stmt.total_cost == 60.0


def test_events_outside_month_are_excluded():
    events = [
        ev("C001", datetime(2026, 5, 31, 23, 30), 40.0),
        ev("C001", datetime(2026, 6, 1, 0, 30), 10.0),
    ]
    stmt = build_statement(events, "C001", "2026-06")
    assert stmt.total_units == 10.0
