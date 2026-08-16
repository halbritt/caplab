"""Command-line entry points: record a check result, send the digest, prune."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from .digest import render_digest
from .eventlog import EventLog
from .events import CheckEvent
from .notify import Outbox


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opsdigest")
    sub = parser.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record", help="append one check result to the event log")
    rec.add_argument("--log", required=True)
    rec.add_argument("--host", required=True)
    rec.add_argument("--check", required=True)
    rec.add_argument("--status", required=True)
    rec.add_argument("--message", default="")

    send = sub.add_parser("send", help="render and deliver the morning digest")
    send.add_argument("--log", required=True)
    send.add_argument("--outbox", required=True)
    send.add_argument("--since-hours", type=int, default=24)

    prune = sub.add_parser("prune", help="drop events older than the retention window")
    prune.add_argument("--log", required=True)
    prune.add_argument("--keep-days", type=int, default=90)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = EventLog(args.log)

    if args.command == "record":
        log.append(
            CheckEvent(
                timestamp=datetime.now(timezone.utc),
                host=args.host,
                check=args.check,
                status=args.status,
                message=args.message,
            )
        )
        return 0

    if args.command == "send":
        cutoff = datetime.now(timezone.utc) - timedelta(hours=args.since_hours)
        digest = render_digest(log.read_since(cutoff))
        path = Outbox(args.outbox).deliver(digest)
        print(f"digest delivered: {path}")
        return 0

    if args.command == "prune":
        dropped = log.prune(args.keep_days)
        print(f"pruned {dropped} event(s)")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
