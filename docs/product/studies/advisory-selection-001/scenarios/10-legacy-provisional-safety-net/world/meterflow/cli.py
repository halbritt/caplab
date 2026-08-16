"""Command-line entry point.  Ops cron calls this on the 30th of the month."""

import argparse
from datetime import date

from .statement import generate_statements


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="meterflow",
        description="Generate monthly billing statements from a readings export.",
    )
    parser.add_argument("tariff", help="tariff JSON file")
    parser.add_argument("readings", help="monthly meter readings CSV export")
    parser.add_argument("out_dir", help="directory to write statements into")
    parser.add_argument(
        "--as-of",
        dest="as_of",
        default=None,
        metavar="YYYY-MM-DD",
        help="statement date (defaults to today; pass one to re-run a past month)",
    )
    args = parser.parse_args(argv)

    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    generate_statements(args.tariff, args.readings, args.out_dir, as_of=as_of)


if __name__ == "__main__":
    main()
