from datetime import datetime, timedelta, timezone

from opsdigest.eventlog import EventLog
from opsdigest.events import CheckEvent

NOW = datetime(2026, 7, 28, 6, 0, tzinfo=timezone.utc)


def _event(hours_ago, status="warn"):
    return CheckEvent(
        NOW - timedelta(hours=hours_ago), "web-01", "heartbeat", status, "m"
    )


def test_append_and_read_all(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    log.append(_event(2))
    log.append(_event(1))
    assert len(log.read_all()) == 2


def test_read_all_on_missing_file(tmp_path):
    log = EventLog(tmp_path / "missing.jsonl")
    assert log.read_all() == []


def test_read_since_filters_old_events(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    log.append(_event(30))
    log.append(_event(2))
    recent = log.read_since(NOW - timedelta(hours=24))
    assert len(recent) == 1
    assert recent[0].timestamp == NOW - timedelta(hours=2)


def test_prune_drops_only_expired_events(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    log.append(_event(24 * 10))
    log.append(_event(1))
    dropped = log.prune(keep_days=7, now=NOW)
    assert dropped == 1
    assert len(log.read_all()) == 1
