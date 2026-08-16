import time

import pytest

from meterd.config import load_fleet
from meterd.store import MeteringStore
from meterd.worker import run_cycle

HOSTS = ("meter-prod-a", "meter-prod-b")

QUANTITIES = {
    "acme": 3.0,
    "globex": 1.5,
    "initech": 4.0,
    "umbrella": 2.25,
    "stark-labs": 7.0,
}


@pytest.fixture()
def store():
    s = MeteringStore(":memory:", shard_count=8)
    yield s
    s.close()


@pytest.fixture()
def cfg():
    return load_fleet()


def seed(store, day):
    past = time.time() - 600.0
    for customer, quantity in QUANTITIES.items():
        store.add_event(customer, day, quantity, recorded_at=past)


def run_fleet(store, cfg, state_dir):
    """One nightly pass across the whole fleet; returns events folded."""
    return sum(
        run_cycle(store, cfg, hostname=host, state_dir=state_dir).events
        for host in HOSTS
    )


def test_cycle_folds_every_customer(store, cfg, tmp_path):
    day = "2026-07-01"
    seed(store, day)

    folded = run_fleet(store, cfg, tmp_path)

    assert folded == len(QUANTITIES)
    for customer, quantity in QUANTITIES.items():
        assert store.rollup_total(day, customer) == pytest.approx(quantity)


def test_repeat_cycles_do_not_recount(store, cfg, tmp_path):
    day = "2026-07-01"
    seed(store, day)

    run_fleet(store, cfg, tmp_path)
    folded_again = run_fleet(store, cfg, tmp_path)

    assert folded_again == 0
    for customer, quantity in QUANTITIES.items():
        assert store.rollup_total(day, customer) == pytest.approx(quantity)


def test_new_events_fold_incrementally(store, cfg, tmp_path):
    day = "2026-07-01"
    seed(store, day)
    run_fleet(store, cfg, tmp_path)

    store.add_event("acme", day, 2.0, recorded_at=time.time() - 600.0)
    folded = run_fleet(store, cfg, tmp_path)

    assert folded == 1
    assert store.rollup_total(day, "acme") == pytest.approx(QUANTITIES["acme"] + 2.0)
