"""Fleet configuration.

``deploy/fleet.toml`` records the shard count and which worker host owns
which shards. Provisioning appends a host entry when a worker is imaged.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_FLEET_FILE = Path(__file__).resolve().parent.parent / "deploy" / "fleet.toml"


@dataclass(frozen=True)
class FleetConfig:
    shard_count: int
    assignments: dict[str, tuple[int, ...]]


def load_fleet(path: str | Path | None = None) -> FleetConfig:
    """Parse the fleet file (the checked-in one by default)."""
    fleet_file = Path(path) if path else DEFAULT_FLEET_FILE
    with open(fleet_file, "rb") as fh:
        raw = tomllib.load(fh)
    shard_count = int(raw["shards"]["count"])
    assignments = {
        host: tuple(int(s) for s in shards)
        for host, shards in raw.get("assignments", {}).items()
    }
    return FleetConfig(shard_count=shard_count, assignments=assignments)
