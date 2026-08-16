import pytest

from meterd.assignment import shard_of
from meterd.store import MeteringStore


@pytest.fixture()
def store():
    s = MeteringStore(":memory:", shard_count=8)
    yield s
    s.close()


def test_apply_rollup_accumulates(store):
    store.apply_rollup("2026-07-01", "acme", 2.0)
    store.apply_rollup("2026-07-01", "acme", 3.5)
    assert store.rollup_total("2026-07-01", "acme") == pytest.approx(5.5)


def test_rollup_total_missing_is_none(store):
    assert store.rollup_total("2026-07-01", "nobody") is None


def test_events_for_shard_respects_cursor(store):
    shard = shard_of("acme", 8)
    store.add_event("acme", "2026-07-01", 1.0, recorded_at=100.0)
    last = store.add_event("acme", "2026-07-01", 2.0, recorded_at=101.0)

    batch = store.events_for_shard(shard, after_seq=0)
    assert [e.quantity for e in batch] == [1.0, 2.0]

    assert store.events_for_shard(shard, after_seq=last) == []


def test_events_for_shard_up_to_bound(store):
    shard = shard_of("acme", 8)
    store.add_event("acme", "2026-07-01", 1.0, recorded_at=100.0)
    store.add_event("acme", "2026-07-01", 2.0, recorded_at=200.0)

    batch = store.events_for_shard(shard, after_seq=0, up_to=150.0)
    assert [e.quantity for e in batch] == [1.0]
