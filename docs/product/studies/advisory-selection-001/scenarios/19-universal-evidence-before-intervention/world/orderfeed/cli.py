"""Command-line entry point for the nightly partner export.

Example:
    python3 -m orderfeed.cli --orders data/orders_sample.csv \
        --rates data/reference_rates.csv --out /tmp/feed.txt
"""

from __future__ import annotations

import argparse
import sys
import time

from orderfeed.pipeline import run_export


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="orderfeed")
    parser.add_argument("--orders", required=True, help="orders CSV from commerce")
    parser.add_argument("--rates", required=True, help="treasury reference-rate CSV")
    parser.add_argument("--out", required=True, help="feed file to write")
    args = parser.parse_args(argv)

    started = time.monotonic()
    count = run_export(args.orders, args.rates, args.out)
    elapsed = time.monotonic() - started
    print(f"wrote {count} rows to {args.out} in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
