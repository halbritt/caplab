"""Configuration loading for upmon.

The config file is JSON: a top-level ``jobs`` array of probe definitions.
Wild values in the file are pulled back into the supported operating band
when jobs are constructed, so a sloppy config cannot take the monitor
outside its limits.
"""

from __future__ import annotations

import json
from pathlib import Path

# Floor on probe frequency.  Probing shared infrastructure faster than this
# has triggered upstream rate-limit bans before (INC-2081), so the band is a
# safety rail, not a preference.
MIN_POLL_INTERVAL = 5.0

# Ceiling: slower than an hour and alerting latency makes the monitor
# useless.
MAX_POLL_INTERVAL = 3600.0

DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 2


def clamp_interval(value: float) -> float:
    """Pull a poll interval into the supported operating band."""
    return min(MAX_POLL_INTERVAL, max(MIN_POLL_INTERVAL, float(value)))


def load_config(path: str | Path) -> dict:
    """Read and lightly check the JSON config file."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if "jobs" not in raw or not isinstance(raw["jobs"], list):
        raise ValueError(f"{path}: config must contain a 'jobs' array")
    return raw


def build_jobs(config: dict) -> list:
    """Construct ProbeJob objects from a parsed config dict."""
    from upmon.probe import ProbeJob

    jobs = []
    for entry in config["jobs"]:
        jobs.append(
            ProbeJob(
                name=entry["name"],
                url=entry["url"],
                poll_interval=entry.get("poll_interval", 60.0),
                timeout=entry.get("timeout", DEFAULT_TIMEOUT),
                retries=entry.get("retries", DEFAULT_RETRIES),
                enabled=entry.get("enabled", True),
            )
        )
    return jobs
