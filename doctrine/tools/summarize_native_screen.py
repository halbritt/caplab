#!/usr/bin/env python3
"""Render the per-trial deterministic table for a native-capture screen.

Reads every native-capture trial dir under the given screen directory and
emits the verifier-owned columns the preregistration records — no prose, no
transcript reading. Rewards, world flags, and the decision/ledger fingerprints
come only from the verifier's detail.json; token usage from capture
provenance. A trial whose capture failed before grading is shown with its
capture exit and no reward.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def row(trial_dir: Path) -> dict | None:
    record = load(trial_dir / "trial.json")
    if record.get("schema_version") != "native-capture-trial/1":
        return None
    detail = load(trial_dir / "verifier" / "detail.json")
    world = detail.get("world", {}) if isinstance(detail, dict) else {}
    usage = record.get("provenance", {}).get("token_usage") or {}
    return {
        "trial": trial_dir.name,
        "reward": record.get("reward"),
        "capture_exit": record.get("capture_exit"),
        "timed_out": record.get("timed_out"),
        "verifier_error": record.get("verifier_error"),
        "replay_probe": world.get("replay_probe_observed"),
        "ledger_check": detail.get("ledger_check_during_agent_phase"),
        "client_modified": world.get("payment_client_modified"),
        "gateway_modified": world.get("gateway_source_modified"),
        "fault_dupes": detail.get("fault_duplicate_orders"),
        "decision_md": detail.get("decision_md_present"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("screen_dir", type=Path)
    arguments = parser.parse_args()
    rows = sorted(
        (r for d in arguments.screen_dir.iterdir() if d.is_dir() and (r := row(d))),
        key=lambda r: r["trial"],
    )
    header = [
        "trial", "reward", "replay_probe", "ledger_check", "client_modified",
        "fault_dupes", "decision_md", "input_tokens", "output_tokens",
        "capture_exit",
    ]
    widths = {h: max(len(h), *(len(str(r[h])) for r in rows)) if rows else len(h) for h in header}
    line = "  ".join(h.ljust(widths[h]) for h in header)
    print(line)
    for r in rows:
        print("  ".join(str(r[h]).ljust(widths[h]) for h in header))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
