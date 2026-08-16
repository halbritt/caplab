from datetime import datetime

from meterflow.events import UsageEvent
from meterflow.rollup import hourly_rollup


def ev(ts, qty, cust="C001"):
    return UsageEvent(cust, ts, qty)


def test_events_land_in_their_hour():
    events = [
        ev(datetime(2026, 6, 4, 10, 15), 2.0),
        ev(datetime(2026, 6, 4, 10, 40), 3.0),
        ev(datetime(2026, 6, 4, 11, 5), 7.0),
    ]
    buckets = hourly_rollup(
        events, datetime(2026, 6, 4, 10), datetime(2026, 6, 4, 12)
    )
    assert [(b.start.hour, b.units) for b in buckets] == [(10, 5.0), (11, 7.0)]


def test_rollup_conserves_total_units():
    events = [
        ev(datetime(2026, 6, 4, h, m), q)
        for h, m, q in [(9, 12, 1.5), (9, 47, 2.0), (13, 30, 4.0), (21, 55, 0.5)]
    ]
    buckets = hourly_rollup(events, datetime(2026, 6, 4), datetime(2026, 6, 5))
    assert sum(b.units for b in buckets) == sum(e.quantity for e in events)


def test_empty_hours_are_omitted():
    events = [ev(datetime(2026, 6, 4, 10, 30), 2.5)]
    buckets = hourly_rollup(events, datetime(2026, 6, 4), datetime(2026, 6, 5))
    assert len(buckets) == 1
    assert buckets[0].start == datetime(2026, 6, 4, 10)
    assert buckets[0].units == 2.5
