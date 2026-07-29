from datetime import datetime, timedelta, timezone

from opsdigest.digest import render_digest
from opsdigest.events import CheckEvent

NOW = datetime(2026, 7, 28, 6, 0, tzinfo=timezone.utc)


def _event(check, status, host="web-01", minutes_ago=30, message="m"):
    return CheckEvent(
        NOW - timedelta(minutes=minutes_ago), host, check, status, message
    )


def test_digest_has_date_header():
    digest = render_digest([], now=NOW)
    assert "2026-07-28" in digest.splitlines()[0]


def test_all_clear_when_nothing_reportable():
    digest = render_digest([_event("heartbeat", "ok")], now=NOW)
    assert "All clear" in digest


def test_failures_and_warnings_are_reported():
    digest = render_digest(
        [
            _event("nightly_backup", "crit", host="db-01", message="pg_dump exited 1"),
            _event("io_latency", "warn", host="storage-03"),
        ],
        now=NOW,
    )
    assert "db-01" in digest
    assert "nightly_backup" in digest
    assert "storage-03" in digest
    assert "io_latency" in digest


def test_healthy_results_are_not_listed():
    digest = render_digest(
        [
            _event("heartbeat", "ok", host="web-02"),
            _event("io_latency", "warn", host="storage-03"),
        ],
        now=NOW,
    )
    assert "web-02" not in digest
