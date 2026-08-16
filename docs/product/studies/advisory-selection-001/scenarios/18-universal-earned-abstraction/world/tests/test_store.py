import json
from datetime import date

import pytest

from worklog.models import Entry
from worklog.store import StoreError, append_entry, load_entries


def test_round_trip(tmp_path):
    path = tmp_path / "log.jsonl"
    entry = Entry(day=date(2026, 7, 20), project="acme", hours=2.5, note="pairing")
    append_entry(path, entry)
    append_entry(path, Entry(day=date(2026, 7, 21), project="birch", hours=1.0))
    loaded = load_entries(path)
    assert loaded[0] == entry
    assert [e.project for e in loaded] == ["acme", "birch"]


def test_blank_lines_and_comments_skipped(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text(
        "\n# imported from the old sheet\n"
        + json.dumps({"day": "2026-07-01", "project": "acme", "hours": 1}) + "\n\n",
        encoding="utf-8",
    )
    assert len(load_entries(path)) == 1


def test_invalid_line_reports_position(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text(
        '{"day": "2026-07-01", "project": "acme", "hours": 1}\nnot json\n',
        encoding="utf-8",
    )
    with pytest.raises(StoreError, match=":2"):
        load_entries(path)
