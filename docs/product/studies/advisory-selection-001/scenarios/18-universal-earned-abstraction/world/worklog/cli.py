"""Command-line interface."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .export import available_formats, render
from .models import Entry
from .store import append_entry, load_entries
from .summary import summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worklog", description="Log time entries and export reports."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="append one entry to the log")
    add.add_argument("--input", required=True, type=Path, help="path to the entry log")
    add.add_argument("--project", required=True)
    add.add_argument("--hours", required=True, type=float)
    add.add_argument("--day", default=date.today().isoformat())
    add.add_argument("--note", default="")

    report = sub.add_parser("report", help="print a per-project summary")
    report.add_argument("--input", required=True, type=Path, help="path to the entry log")
    report.add_argument("--format", default="csv", choices=available_formats())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "add":
        entry = Entry(
            day=date.fromisoformat(args.day),
            project=args.project,
            hours=args.hours,
            note=args.note,
        )
        append_entry(args.input, entry)
        return 0
    columns, rows = summarize(load_entries(args.input))
    sys.stdout.write(render(args.format, columns, rows))
    return 0
