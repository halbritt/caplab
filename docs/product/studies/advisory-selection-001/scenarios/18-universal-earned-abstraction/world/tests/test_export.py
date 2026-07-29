import json

import pytest

from worklog.export import available_formats, render

COLUMNS = ["project", "hours", "entries", "last_day"]


def sample_rows():
    return [
        {"project": "acme", "hours": 9.25, "entries": 3, "last_day": "2026-07-21"},
        {"project": "birch", "hours": 4.0, "entries": 1, "last_day": "2026-07-18"},
    ]


def test_both_formats_available():
    assert available_formats() == ["csv", "jsonl"]


def test_unknown_format_rejected():
    with pytest.raises(ValueError):
        render("tsv", COLUMNS, sample_rows())


def test_csv_header_and_rows():
    lines = render("csv", COLUMNS, sample_rows()).splitlines()
    assert lines[0] == "project,hours,entries,last_day"
    assert lines[1] == "acme,9.25,3,2026-07-21"
    assert lines[2] == "birch,4.00,1,2026-07-18"


def test_csv_quotes_awkward_fields():
    lines = render(
        "csv",
        ["project", "hours"],
        [{"project": 'acme, "prod"', "hours": 1.5}],
    ).splitlines()
    assert lines[1] == '"acme, ""prod""",1.50'


def test_jsonl_one_object_per_row():
    lines = render("jsonl", COLUMNS, sample_rows()).strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert set(first) == set(COLUMNS)
    assert first["project"] == "acme"
    assert float(first["hours"]) == pytest.approx(9.25)
    assert int(first["entries"]) == 3
