from datetime import datetime, timezone

import pytest

from opsdigest.events import CheckEvent


def _event(**overrides):
    base = dict(
        timestamp=datetime(2026, 7, 28, 3, 40, tzinfo=timezone.utc),
        host="db-01",
        check="nightly_backup",
        status="crit",
        message="pg_dump exited 1",
    )
    base.update(overrides)
    return CheckEvent(**base)


def test_json_round_trip():
    event = _event()
    assert CheckEvent.from_json(event.to_json()) == event


def test_message_defaults_to_empty():
    event = CheckEvent.from_json(
        '{"ts":"2026-07-28T03:40:00+00:00","host":"web-01",'
        '"check":"heartbeat","status":"ok"}'
    )
    assert event.message == ""


def test_unknown_status_rejected():
    with pytest.raises(ValueError):
        _event(status="broken")


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        _event(timestamp=datetime(2026, 7, 28, 3, 40))
