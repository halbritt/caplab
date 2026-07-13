#!/usr/bin/env python3
"""Execute one preregistered checkout-retries frontier-screen trial.

Default mode dry-renders the exact Harbor command without any network or
model call. ``--execute`` performs the preregistered drift checks (task
content hash, live provider price, credential presence) and then launches
exactly one sequence. Preparation and dry-rendering never authorize a paid
inference request.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "doctrine/evaluations/robustness/harbor/tasks"
ORDER = TASKS / "checkout-retries-frontier-order.csv"

SUBJECTS = {
    "terra": {"model": "openrouter/openai/gpt-5.6-terra", "alias": "openai/gpt-5.6-terra"},
    "fable5": {"model": "openrouter/anthropic/claude-fable-5", "alias": "anthropic/claude-fable-5"},
}
# Observed 2026-07-13 from the live OpenRouter catalog; --execute re-fetches
# and refuses to run on any drift.
PINNED_PRICES = {
    "openai/gpt-5.6-terra": {"prompt": 2.5e-06, "completion": 1.5e-05},
    "anthropic/claude-fable-5": {"prompt": 1e-05, "completion": 5e-05},
}
MAX_TOKENS = 8192


def load_order() -> list[dict[str, str]]:
    lines = ORDER.read_text(encoding="utf-8").strip().splitlines()
    header = lines[0].split(",")
    return [dict(zip(header, line.split(","))) for line in lines[1:]]


def task_content_hash() -> str:
    task = TASKS / "checkout-retries-m1"
    digest = hashlib.sha256()
    for path in sorted(task.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(task).as_posix().encode())
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def build_command(trial: dict[str, str], jobs_dir: str) -> list[str]:
    subject = SUBJECTS[trial["subject"]]
    name = f"frontier-s{int(trial['sequence']):02d}-{trial['subject']}-{trial['task']}-{trial['condition']}"
    return [
        "harbor", "run",
        "-p", str(TASKS / f"checkout-retries-{trial['task']}"),
        "-a", "terminus-2",
        "-m", subject["model"],
        "--ak", f'llm_kwargs={{"max_tokens": {MAX_TOKENS}}}',
        "--agent-timeout-multiplier", "2",
        "-o", jobs_dir,
        "--job-name", name,
        "-q", "-y",
    ]


def live_prices(alias: str) -> dict[str, float]:
    with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as response:
        catalog = json.load(response)
    for model in catalog["data"]:
        if model["id"] == alias:
            pricing = model["pricing"]
            return {"prompt": float(pricing["prompt"]), "completion": float(pricing["completion"])}
    raise SystemExit(f"model absent from live catalog: {alias}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence", type=int, required=True)
    parser.add_argument("--jobs-dir", required=True)
    parser.add_argument("--expect-task-hash")
    parser.add_argument("--execute", action="store_true")
    arguments = parser.parse_args()

    trials = {int(t["sequence"]): t for t in load_order()}
    trial = trials[arguments.sequence]
    subject = SUBJECTS[trial["subject"]]
    command = build_command(trial, arguments.jobs_dir)
    current_hash = task_content_hash()

    print(f"sequence {arguments.sequence}: subject={subject['alias']} task=checkout-retries-{trial['task']} condition={trial['condition']}")
    print(f"task content hash: {current_hash}")
    print(f"command: {' '.join(command)}")
    print(f"sampling sent: max_tokens={MAX_TOKENS}; all other parameters are provider defaults (temperature/top_p unsupported on both subjects)")

    if not arguments.execute:
        print("dry render only; no model call was made")
        return 0

    if arguments.expect_task_hash and arguments.expect_task_hash != current_hash:
        raise SystemExit(f"task hash drift: expected {arguments.expect_task_hash}")
    live = live_prices(subject["alias"])
    if live != PINNED_PRICES[subject["alias"]]:
        raise SystemExit(f"price drift for {subject['alias']}: pinned {PINNED_PRICES[subject['alias']]}, live {live}")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY absent")
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
