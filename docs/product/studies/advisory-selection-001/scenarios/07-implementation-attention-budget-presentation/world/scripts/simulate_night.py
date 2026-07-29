#!/usr/bin/env python3
"""Recreate a typical night of check traffic and render the morning digest.

Writes demo/events.jsonl and demo/digest-<date>.txt under the repo root,
then prints where they are and how big the digest came out.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from opsdigest.digest import render_digest  # noqa: E402
from opsdigest.eventlog import EventLog  # noqa: E402
from opsdigest.events import CheckEvent  # noqa: E402
from opsdigest.notify import Outbox  # noqa: E402

HOSTS = ["web-01", "web-02", "app-01", "app-02", "db-01", "storage-03"]


def main() -> None:
    demo = ROOT / "demo"
    log_path = demo / "events.jsonl"
    if log_path.exists():
        log_path.unlink()
    log = EventLog(log_path)

    start = datetime.now(timezone.utc).replace(
        hour=20, minute=0, second=0, microsecond=0
    ) - timedelta(days=1)
    minute = timedelta(minutes=1)

    # Twelve hours of overnight checks, one pass per minute. storage-03 and
    # app-02 have been flapping on io latency all night, exactly as they did
    # for real last week.
    for i in range(12 * 60):
        ts = start + i * minute
        log.append(
            CheckEvent(ts, "storage-03", "io_latency", "warn",
                       "p99 read latency 480ms exceeds 250ms threshold")
        )
        log.append(
            CheckEvent(ts, "app-02", "io_latency", "warn",
                       "p99 read latency 310ms exceeds 250ms threshold")
        )
        if i % 15 == 0:
            for host in HOSTS:
                log.append(CheckEvent(ts, host, "heartbeat", "ok", "up"))
        if i == 460:
            log.append(
                CheckEvent(ts, "db-01", "nightly_backup", "crit",
                           "pg_dump exited 1: could not write to /backups "
                           "(No space left on device)")
            )
        if i == 463:
            log.append(
                CheckEvent(ts, "app-01", "queue_depth", "warn",
                           "job queue depth 1200 above limit 1000")
            )

    events = log.read_all()
    digest = render_digest(events)
    delivered = Outbox(demo).deliver(digest)

    digest_lines = digest.splitlines()
    crit_at = next(
        (i for i, line in enumerate(digest_lines, start=1) if "[CRIT]" in line),
        None,
    )
    print(f"simulated {len(events)} events -> {log_path}")
    print(f"digest written to {delivered} ({len(digest_lines)} lines)")
    if crit_at is not None:
        print(f"the [CRIT] line is at line {crit_at} of the digest")


if __name__ == "__main__":
    main()
