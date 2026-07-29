"""Status file writer consumed by the dashboard and ``upmonctl status``."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


def write_status(path: str | Path, jobs, *, clock=time.time) -> None:
    """Atomically write the current job snapshots to ``path``."""
    payload = {
        "generated_at": clock(),
        "jobs": [job.snapshot() for job in jobs],
    }
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)
