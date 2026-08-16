"""Nightly rollup worker.

Each fleet host owns a fixed slice of the shard space (see
``deploy/fleet.toml``) and walks its shards' event logs, folding new
events into the ``rollups`` table. A systemd timer runs one cycle per
night on every worker.
"""

from __future__ import annotations

import logging
import os
import socket
import time
from dataclasses import dataclass

from meterd import assignment, watermark
from meterd.config import FleetConfig, load_fleet
from meterd.store import MeteringStore

log = logging.getLogger("meterd.worker")

# Let in-flight ingest writes land before we aggregate a batch.
GRACE_SECONDS = 120.0


@dataclass(frozen=True)
class CycleReport:
    hostname: str
    shards: tuple[int, ...]
    events: int


def run_cycle(
    store: MeteringStore,
    cfg: FleetConfig,
    *,
    hostname: str | None = None,
    state_dir: str | os.PathLike[str] | None = None,
    now: float | None = None,
) -> CycleReport:
    """Run one rollup cycle for this host and return what it did."""
    hostname = hostname or socket.gethostname()
    state_dir = state_dir if state_dir is not None else watermark.DEFAULT_STATE_DIR
    now = time.time() if now is None else now
    cutoff = now - GRACE_SECONDS

    owned = assignment.shards_for(hostname, cfg)
    total_events = 0
    for shard in owned:
        cursor = watermark.load(state_dir, hostname, shard)
        batch = store.events_for_shard(shard, after_seq=cursor, up_to=cutoff)
        if not batch:
            continue
        sums: dict[tuple[str, str], float] = {}
        for event in batch:
            key = (event.day, event.customer)
            sums[key] = sums.get(key, 0.0) + event.quantity
        for (day, customer), delta in sums.items():
            store.apply_rollup(day, customer, delta)
        watermark.save(state_dir, hostname, shard, batch[-1].seq)
        total_events += len(batch)

    log.info(
        "cycle complete host=%s shards=%s events=%d",
        hostname,
        list(owned),
        total_events,
    )
    return CycleReport(hostname=hostname, shards=tuple(owned), events=total_events)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    cfg = load_fleet(os.environ.get("METERD_FLEET_FILE"))
    store = MeteringStore(
        os.environ.get("METERD_DB", "/srv/meterd/meter.db"),
        shard_count=cfg.shard_count,
    )
    try:
        run_cycle(store, cfg, state_dir=os.environ.get("METERD_STATE_DIR"))
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
