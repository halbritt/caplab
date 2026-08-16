import json
from datetime import datetime

from meterflow.events import UsageEvent, load_events, parse_line


def test_parse_line_roundtrip():
    line = json.dumps(
        {
            "customer_id": "C001",
            "timestamp": "2026-06-04T10:15:00",
            "quantity": 12.5,
            "meter": "api-calls",
        }
    )
    ev = parse_line(line)
    assert ev == UsageEvent("C001", datetime(2026, 6, 4, 10, 15), 12.5, "api-calls")


def test_meter_defaults_when_absent():
    ev = parse_line(
        '{"customer_id": "C001", "timestamp": "2026-06-04T10:15:00", "quantity": 3.0}'
    )
    assert ev.meter == "default"


def test_load_events_skips_blank_lines(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"customer_id": "C001", "timestamp": "2026-06-04T10:15:00", "quantity": 1.0}\n'
        "\n"
        '{"customer_id": "C002", "timestamp": "2026-06-04T11:20:00", "quantity": 2.5}\n'
    )
    events = load_events(path)
    assert [ev.customer_id for ev in events] == ["C001", "C002"]
    assert events[1].quantity == 2.5
