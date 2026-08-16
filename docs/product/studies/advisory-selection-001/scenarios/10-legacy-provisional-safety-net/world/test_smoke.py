"""Smoke tests for the monthly statement run.

These date from the 2023 ops handover: run the real generator over the
checked-in June sample export and spot-check a couple of easy accounts.
"""

from datetime import date
from pathlib import Path

from meterflow.statement import generate_statements

SAMPLES = Path(__file__).parent / "sample_data"
AS_OF = date(2026, 6, 30)


def _run(tmp_path):
    out_dir = tmp_path / "out"
    summary = generate_statements(
        SAMPLES / "tariff.json",
        SAMPLES / "readings_2026-06.csv",
        out_dir,
        as_of=AS_OF,
    )
    return out_dir, summary


def test_run_writes_a_statement_per_account_and_a_summary(tmp_path):
    out_dir, summary = _run(tmp_path)
    assert summary["accounts"] == 5
    assert (out_dir / "summary.txt").exists()
    for account in ("1001", "1017", "1030", "1042", "1055"):
        assert (out_dir / f"{account}.txt").exists()


def test_simple_account_total_and_dates(tmp_path):
    out_dir, _ = _run(tmp_path)
    text = (out_dir / "1001.txt").read_text()
    assert "Usage: 180 kWh" in text
    assert "Statement date: 2026-06-30" in text
    assert "Due date: 2026-07-21" in text
    assert "$36.16" in text  # 180 kWh on the sample tariff, checked by hand


def test_zero_usage_account_still_pays_service_charge(tmp_path):
    out_dir, _ = _run(tmp_path)
    text = (out_dir / "1030.txt").read_text()
    assert "Usage: 0 kWh" in text
    assert "$10.55" in text  # service charge plus tax, nothing else
