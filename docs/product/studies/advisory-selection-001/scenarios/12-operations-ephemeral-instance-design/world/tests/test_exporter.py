import csv

import pytest

from meterd.exporter import write_daily_export
from meterd.store import MeteringStore


@pytest.fixture()
def store():
    s = MeteringStore(":memory:", shard_count=8)
    yield s
    s.close()


def test_export_writes_sorted_totals(store, tmp_path):
    day = "2026-07-01"
    store.apply_rollup(day, "globex", 1.5)
    store.apply_rollup(day, "acme", 3.0)
    store.apply_rollup(day, "acme", 0.5)

    out_path = write_daily_export(store, day, tmp_path)

    assert out_path.name == "usage-2026-07-01.csv"
    with open(out_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    assert rows == [
        ["customer", "total"],
        ["acme", "3.500"],
        ["globex", "1.500"],
    ]


def test_export_skips_other_days(store, tmp_path):
    store.apply_rollup("2026-07-01", "acme", 3.0)
    store.apply_rollup("2026-07-02", "acme", 9.0)

    out_path = write_daily_export(store, "2026-07-01", tmp_path)

    with open(out_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    assert rows == [["customer", "total"], ["acme", "3.000"]]
