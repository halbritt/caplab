"""Per-shard progress markers.

For each shard it owns, a worker records the highest event sequence it
has folded into the rollups, so the next cycle resumes where this one
stopped. Markers are small JSON files under the worker's state
directory.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_STATE_DIR = "/var/lib/meterd/state"


def _marker_path(state_dir: str | Path, hostname: str, shard: int) -> Path:
    return Path(state_dir) / hostname / f"shard-{shard:02d}.json"


def load(state_dir: str | Path, hostname: str, shard: int) -> int:
    """Last folded sequence for (hostname, shard); 0 if none recorded."""
    try:
        with open(_marker_path(state_dir, hostname, shard), encoding="utf-8") as fh:
            return int(json.load(fh)["seq"])
    except FileNotFoundError:
        return 0


def save(state_dir: str | Path, hostname: str, shard: int, seq: int) -> None:
    """Record *seq* as the last folded sequence for (hostname, shard)."""
    path = _marker_path(state_dir, hostname, shard)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"seq": int(seq)}), encoding="utf-8")
    os.replace(tmp, path)
