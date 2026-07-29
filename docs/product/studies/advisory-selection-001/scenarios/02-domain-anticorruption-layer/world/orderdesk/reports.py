"""Nightly operations summary, computed straight off the MERC drop file."""

from __future__ import annotations

import sys

from . import merc_client


def summarize(records) -> dict:
    total = len(records)
    completed = sum(1 for r in records if r["stat_cd"] == "C")
    picking = sum(1 for r in records if r["stat_cd"] == "P")
    open_lines = sum(1 for r in records if r["stat_cd"] == "O")
    units_ordered = sum(r["qty_ord"] for r in records)
    units_shipped = sum(r["qty_shp"] for r in records)
    fill_rate = round(units_shipped / units_ordered, 3) if units_ordered else 1.0
    return {
        "total_lines": total,
        "open_lines": open_lines,
        "picking_lines": picking,
        "completed_lines": completed,
        "units_ordered": units_ordered,
        "units_shipped": units_shipped,
        "fill_rate": fill_rate,
    }


def render(summary: dict) -> str:
    return "\n".join(
        [
            "MERC feed summary",
            f"  lines: {summary['total_lines']} "
            f"(open {summary['open_lines']}, picking {summary['picking_lines']}, "
            f"completed {summary['completed_lines']})",
            f"  units: {summary['units_shipped']} shipped of "
            f"{summary['units_ordered']} ordered "
            f"(fill rate {summary['fill_rate']:.1%})",
        ]
    )


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: python3 -m orderdesk.reports FEED_FILE")
        raise SystemExit(2)
    print(render(summarize(merc_client.fetch_feed(argv[0]))))


if __name__ == "__main__":
    main()
