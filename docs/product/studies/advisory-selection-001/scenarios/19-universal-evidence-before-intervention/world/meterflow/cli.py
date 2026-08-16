"""Command-line entry points for meterflow."""

from __future__ import annotations

import argparse

from .events import load_events
from .statements import build_statement


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="meterflow")
    sub = parser.add_subparsers(dest="command", required=True)

    st = sub.add_parser("statement", help="Build one customer's monthly statement")
    st.add_argument("events_file", help="JSONL file of usage events")
    st.add_argument("--customer", required=True, help="customer id, e.g. C042")
    st.add_argument("--month", required=True, help="YYYY-MM")

    args = parser.parse_args(argv)
    events = load_events(args.events_file)
    stmt = build_statement(events, args.customer, args.month)
    print(f"Statement  {stmt.customer_id}  {stmt.month}")
    print(f"  billable hours : {stmt.bucket_count}")
    print(f"  total units    : {stmt.total_units}")
    print(f"  total cost     : ${stmt.total_cost:.2f}")
    return 0
