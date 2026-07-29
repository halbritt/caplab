import json

import pytest

from worklog.cli import main

RECORDS = [
    {"day": "2026-07-15", "project": "acme", "hours": 3.25, "note": "planning"},
    {"day": "2026-07-18", "project": "birch", "hours": 4.0, "note": "site audit"},
]


def write_log(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in RECORDS), encoding="utf-8")
    return path


def test_report_csv_to_stdout(tmp_path, capsys):
    path = write_log(tmp_path)
    assert main(["report", "--input", str(path), "--format", "csv"]) == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "project,hours,entries,last_day"
    assert "acme" in out


def test_add_then_report(tmp_path, capsys):
    path = write_log(tmp_path)
    assert main(
        [
            "add",
            "--input", str(path),
            "--project", "acme",
            "--hours", "1.5",
            "--day", "2026-07-22",
        ]
    ) == 0
    main(["report", "--input", str(path), "--format", "csv"])
    out = capsys.readouterr().out
    assert "acme,4.75,2,2026-07-22" in out


def test_unknown_format_exits(tmp_path):
    path = write_log(tmp_path)
    with pytest.raises(SystemExit):
        main(["report", "--input", str(path), "--format", "yaml"])
