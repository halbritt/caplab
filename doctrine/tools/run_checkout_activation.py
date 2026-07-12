#!/usr/bin/env python3
"""Execute the preregistered checkout-retries activation order."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARBOR_ROOT = ROOT / "doctrine/evaluations/robustness/harbor"
ORDER = HARBOR_ROOT / "tasks/checkout-retries-activation-order.csv"
FLEET_RUNNER = Path("/home/halbritt/git/gpu-fleet/bin/gpu-fleet-run")
FLEET_PICKER = Path("/home/halbritt/git/gpu-fleet/pick_slot.py")
ENDPOINT_TOKEN = "@@GPU_FLEET_ENDPOINT_URL@@"
MODEL_TOKEN = "@@GPU_FLEET_SERVED_MODEL@@"

SUBJECTS = {
    "27b": {"model": "qwen3.6:27b", "max_context": 32768},
    "35b": {"model": "qwen3.6-35b-a3b", "max_context": 262144},
}


@dataclass(frozen=True)
class Trial:
    sequence: int
    block: int
    subject: str
    task: str
    condition: str

    @property
    def job_name(self):
        return (
            f"activation-s{self.sequence:02d}-b{self.block}-"
            f"{self.subject}-{self.task}-{self.condition}"
        )


def load_order(path=ORDER):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return [
            Trial(
                sequence=int(row["sequence"]),
                block=int(row["block"]),
                subject=row["subject"],
                task=row["task"],
                condition=row["condition"],
            )
            for row in csv.DictReader(stream)
        ]


def _agent_arguments(trial):
    subject = SUBJECTS[trial.subject]
    model_info = (
        f'{{"max_input_tokens":{subject["max_context"]},"max_output_tokens":8192,'
        '"input_cost_per_token":0,"output_cost_per_token":0}'
    )
    arguments = [
        "-a",
        "terminus-2",
        "-m",
        f"openai/{MODEL_TOKEN}",
        "--ak",
        f"api_base={ENDPOINT_TOKEN}",
        "--ak",
        "temperature=0.6",
        "--ak",
        'llm_kwargs={"top_p":0.95,"presence_penalty":0,"max_tokens":8192}',
        "--ak",
        'llm_call_kwargs={"extra_body":{"top_k":20,"min_p":0}}',
        "--ak",
        f"model_info={model_info}",
    ]
    if trial.condition == "forced":
        arguments.extend(
            [
                "--skill",
                str(HARBOR_ROOT / "experimental-skills/verification-compact/doctrine"),
                "--extra-instruction-path",
                str(HARBOR_ROOT / "conditions/verification-compact-forced.md"),
            ]
        )
    return arguments


def trial_command(trial, jobs_dir):
    subject = SUBJECTS[trial.subject]
    task_path = HARBOR_ROOT / "tasks" / f"checkout-retries-{trial.task}"
    return [
        str(FLEET_RUNNER),
        "--model",
        subject["model"],
        "--max-context",
        str(subject["max_context"]),
        "--job",
        trial.job_name,
        "--timeout",
        "2400",
        "--",
        "harbor",
        "run",
        "-p",
        str(task_path),
        *_agent_arguments(trial),
        "--agent-timeout-multiplier",
        "2",
        "--n-attempts",
        "1",
        "--n-concurrent",
        "1",
        "--n-concurrent-agents",
        "1",
        "--max-retries",
        "0",
        "--jobs-dir",
        str(jobs_dir),
        "--job-name",
        trial.job_name,
        "--quiet",
        "--yes",
    ]


def selected_trials(order, first, limit):
    selected = [trial for trial in order if trial.sequence >= first]
    return selected if limit is None else selected[:limit]


def route_is_ready(trial):
    subject = SUBJECTS[trial.subject]
    completed = subprocess.run(
        [
            "python3",
            str(FLEET_PICKER),
            "--model",
            subject["model"],
            "--max-context",
            str(subject["max_context"]),
            "--job",
            trial.job_name,
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return bool(json.loads(completed.stdout))


def wait_for_route(trial, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if route_is_ready(trial):
            return True
        time.sleep(5)
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-dir", type=Path, required=True)
    parser.add_argument("--first-sequence", type=int, default=1)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args(argv)
    args.jobs_dir.mkdir(parents=True, exist_ok=True)

    environment = dict(os.environ)
    environment.setdefault("OPENAI_API_KEY", "sk-local-noauth")
    trials = selected_trials(load_order(), args.first_sequence, args.limit)
    for trial in trials:
        if not wait_for_route(trial):
            print(f"activation: route did not recover for {trial.job_name}", flush=True)
            return 75
        print(f"activation: starting {trial.job_name}", flush=True)
        completed = subprocess.run(
            trial_command(trial, args.jobs_dir),
            cwd=ROOT,
            env=environment,
            check=False,
        )
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
