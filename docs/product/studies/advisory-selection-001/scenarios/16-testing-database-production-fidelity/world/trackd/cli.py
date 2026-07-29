"""Command line front end used by the scanner gateways."""

from __future__ import annotations

import argparse
import sys

from trackd.db import connect
from trackd.errors import TrackdError
from trackd.schema import apply_schema
from trackd.service import TrackingService


def _ensure_schema() -> None:
    conn = connect()
    try:
        apply_schema(conn)
    finally:
        conn.close()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trackd", description="Parcel scan tracking for the warehouse gateway"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("register", help="register a new shipment")
    p.add_argument("tracking_id")
    p.add_argument("--carrier", required=True)
    p.add_argument("--origin", required=True)

    p = sub.add_parser("scan", help="record a scan event")
    p.add_argument("tracking_id")
    p.add_argument("status")
    p.add_argument("location")

    p = sub.add_parser("status", help="show the current status of a shipment")
    p.add_argument("tracking_id")

    p = sub.add_parser("history", help="list every scan for a shipment")
    p.add_argument("tracking_id")

    sub.add_parser("snapshot", help="shipment counts by current status")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    _ensure_schema()
    service = TrackingService()
    try:
        if args.command == "register":
            service.register_shipment(args.tracking_id, args.carrier, args.origin)
            print(f"registered {args.tracking_id}")
        elif args.command == "scan":
            event_id = service.record_scan(args.tracking_id, args.status, args.location)
            print(f"recorded scan {event_id} for {args.tracking_id}")
        elif args.command == "status":
            summary = service.shipment_summary(args.tracking_id)
            line = f"{summary['tracking_id']}: {summary['status']}"
            if summary["last_location"] is not None:
                line += f" @ {summary['last_location']} ({summary['last_scanned_at']})"
            print(line)
        elif args.command == "history":
            for event in service.scan_history(args.tracking_id):
                print(f"{event['scanned_at']}  {event['status']:<17} {event['location']}")
        elif args.command == "snapshot":
            for status, count in sorted(service.network_snapshot().items()):
                print(f"{status:<17} {count}")
    except TrackdError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
