from datetime import date

from worklog.models import Entry
from worklog.summary import summarize


def entry(day, project, hours):
    return Entry(day=date.fromisoformat(day), project=project, hours=hours)


def test_aggregates_per_project():
    columns, rows = summarize(
        [
            entry("2026-07-15", "acme", 3.25),
            entry("2026-07-17", "acme", 2.5),
            entry("2026-07-21", "acme", 3.5),
            entry("2026-07-18", "birch", 4.0),
        ]
    )
    assert columns == ["project", "hours", "entries", "last_day"]
    assert rows[0] == {
        "project": "acme",
        "hours": 9.25,
        "entries": 3,
        "last_day": "2026-07-21",
    }
    assert rows[1]["entries"] == 1


def test_projects_sorted_and_hours_rounded():
    _, rows = summarize(
        [
            entry("2026-07-01", "zeta", 0.1),
            entry("2026-07-02", "zeta", 0.2),
            entry("2026-07-03", "alpha", 1.0),
        ]
    )
    assert [r["project"] for r in rows] == ["alpha", "zeta"]
    assert rows[1]["hours"] == 0.3
