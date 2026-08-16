from upmon.config import MAX_POLL_INTERVAL, MIN_POLL_INTERVAL
from upmon.probe import ProbeJob


def test_interval_pulled_into_band_at_construction():
    fast = ProbeJob("edge", "https://edge.example/health", poll_interval=1)
    slow = ProbeJob("edge", "https://edge.example/health", poll_interval=999999)
    assert fast.poll_interval == MIN_POLL_INTERVAL
    assert slow.poll_interval == MAX_POLL_INTERVAL


def test_interval_inside_band_kept():
    job = ProbeJob("edge", "https://edge.example/health", poll_interval=42)
    assert job.poll_interval == 42.0


def test_snapshot_uses_public_field_names():
    job = ProbeJob("edge", "https://edge.example/health", poll_interval=30)
    snap = job.snapshot()
    # The dashboard and upmonctl parse exactly these keys.
    assert set(snap) == {
        "name",
        "url",
        "poll_interval",
        "timeout",
        "retries",
        "enabled",
        "consecutive_failures",
    }
    assert not any(key.startswith("_") for key in snap)
    assert snap["poll_interval"] == 30.0


def test_record_result_tracks_failure_streak():
    job = ProbeJob("edge", "https://edge.example/health")
    job.record_result(False)
    job.record_result(False)
    assert job.consecutive_failures == 2
    job.record_result(True)
    assert job.consecutive_failures == 0
