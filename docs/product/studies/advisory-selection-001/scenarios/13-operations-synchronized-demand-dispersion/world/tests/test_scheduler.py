import pytest

from edgeagent.scheduler import next_sync_time, seconds_until


def test_next_sync_is_strictly_in_the_future():
    assert next_sync_time(1_700_000_123.4, 600.0) > 1_700_000_123.4


def test_next_sync_lands_within_the_scheduling_budget():
    now = 1_700_000_123.4
    upcoming = next_sync_time(now, 600.0)
    assert now < upcoming <= now + 1200.0


def test_next_sync_advances_when_called_from_a_later_time():
    first = next_sync_time(1_000.0, 600.0)
    second = next_sync_time(first, 600.0)
    assert second > first


def test_interval_must_be_positive():
    with pytest.raises(ValueError):
        next_sync_time(1_000.0, 0.0)
    with pytest.raises(ValueError):
        next_sync_time(1_000.0, -600.0)


def test_seconds_until_clamps_to_zero_for_late_callers():
    assert seconds_until(10.0, 5.0) == 0.0
    assert seconds_until(5.0, 12.5) == 7.5
