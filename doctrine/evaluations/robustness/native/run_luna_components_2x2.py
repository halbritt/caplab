#!/usr/bin/env python3
"""Run one preregistered checkout-retries Luna component slot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
EXPERIMENT_DIR = HERE / "checkout-retries-luna-components-2x2"
EXPERIMENT_PATH = EXPERIMENT_DIR / "experiment.json"
ORDER_PATH = HERE / "checkout-retries-luna-components-2x2-order.csv"
DRIVER = REPO / "doctrine" / "tools" / "run_checkout_native.py"
TASKS = REPO / "doctrine" / "evaluations" / "robustness" / "harbor" / "tasks"
DEFAULT_DECLARATION = Path.home() / "git" / "striatum-next" / "backends" / "codex-luna-max" / "backend.yaml"
DEFAULT_CORPUS = Path("/var/tmp/striatum-bench/corpus-29e067c6")
DEFAULT_CAPTURE = Path("/tmp/striatum-workspace-capture-timeline")
DEFAULT_OUTPUT = Path("/var/tmp/striatum-bench/luna-components-2x2")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_experiment() -> dict[str, object]:
    return json.loads(EXPERIMENT_PATH.read_text())


def load_order() -> list[dict[str, str]]:
    with ORDER_PATH.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if [int(row["sequence"]) for row in rows] != list(range(1, 33)):
        raise SystemExit("order manifest must contain sequences 1 through 32 exactly once")
    return rows


def render_prompt(task: Path, v_level: str, d_level: str) -> bytes:
    base = (task / "instruction.md").read_text()
    v_text = (EXPERIMENT_DIR / "components" / f"{v_level}.md").read_text().rstrip("\n")
    d_text = (EXPERIMENT_DIR / "components" / f"{d_level}.md").read_text().rstrip("\n")
    return (
        base
        + "\n---\n\n## Pre-edit evidence slot\n\n"
        + v_text
        + "\n\n## Decision slot\n\n"
        + d_text
        + "\n"
    ).encode()


def verify_frozen_inputs(
    experiment: dict[str, object],
    row: dict[str, str],
    declaration: Path,
    corpus: Path,
    capture_binary: Path,
) -> tuple[Path, bytes]:
    if sha256_file(ORDER_PATH) != experiment["order_manifest_sha256"]:
        raise SystemExit("order manifest drift")
    for level, expected in experiment["components"].items():
        path = EXPERIMENT_DIR / "components" / f"{level}.md"
        data = path.read_bytes()
        if (
            sha256_bytes(data) != expected["sha256"]
            or len(data) != expected["bytes"]
            or len(data.decode().split()) != expected["words"]
        ):
            raise SystemExit(f"component drift: {level}")
    if sha256_file(declaration) != experiment["subject"]["declaration_sha256"]:
        raise SystemExit("declaration drift")
    if sha256_file(capture_binary) != experiment["capture"]["binary_sha256"]:
        raise SystemExit("capture binary drift")

    task_identity = experiment["tasks"][row["task"]]
    task = TASKS / task_identity["name"]
    prompt = render_prompt(task, row["V"], row["D"])
    expected_prompt = experiment["combined_prompts"][row["condition"]]
    if (
        sha256_bytes(prompt) != expected_prompt["sha256"]
        or len(prompt) != expected_prompt["bytes"]
        or len(prompt.decode().split()) != expected_prompt["words"]
    ):
        raise SystemExit(f"combined prompt drift: {row['condition']}")
    return task, prompt


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def build_metadata(
    experiment: dict[str, object],
    row: dict[str, str],
    attempt: int,
    preregistration_commit: str,
) -> dict[str, object]:
    task_identity = experiment["tasks"][row["task"]]
    return {
        "schema_version": "checkout-retries-luna-components-trial/1",
        "sequence": int(row["sequence"]),
        "attempt": attempt,
        "block": row["block"],
        "task": task_identity["name"],
        "task_content_hash": task_identity["task_content_hash"],
        "condition": row["condition"],
        "V": row["V"],
        "D": row["D"],
        "V_component_sha256": experiment["components"][row["V"]]["sha256"],
        "D_component_sha256": experiment["components"][row["D"]]["sha256"],
        "combined_prompt_sha256": experiment["combined_prompts"][row["condition"]]["sha256"],
        "order_manifest_sha256": experiment["order_manifest_sha256"],
        "experiment_manifest_sha256": sha256_file(EXPERIMENT_PATH),
        "preregistration_commit": preregistration_commit,
        "declaration_sha256": experiment["subject"]["declaration_sha256"],
        "surface_hash": experiment["corpus"]["surface_hash"],
        "capture_binary_sha256": experiment["capture"]["binary_sha256"],
        "observer_commit": experiment["capture"]["observer_commit"],
        "observer_version": experiment["capture"]["observer_version"],
        "backend_id": experiment["subject"]["backend_id"],
        "model": experiment["subject"]["model"],
        "reasoning_effort": experiment["subject"]["reasoning_effort"],
        "runtime_version": experiment["subject"]["runtime_version"],
        "sealed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence", type=int, required=True, choices=range(1, 33))
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--declaration", type=Path, default=DEFAULT_DECLARATION)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--capture-binary", type=Path, default=DEFAULT_CAPTURE)
    parser.add_argument("--timeout", type=int, default=1800)
    arguments = parser.parse_args()
    if arguments.attempt < 1:
        raise SystemExit("attempt must be positive")

    if git_output("status", "--porcelain"):
        raise SystemExit("books preregistration worktree is not clean")
    preregistration_commit = git_output("rev-parse", "HEAD")
    experiment = load_experiment()
    row = load_order()[arguments.sequence - 1]
    task, prompt = verify_frozen_inputs(
        experiment,
        row,
        arguments.declaration.resolve(),
        arguments.corpus.resolve(),
        arguments.capture_binary.resolve(),
    )
    metadata = build_metadata(experiment, row, arguments.attempt, preregistration_commit)

    arguments.output_root.mkdir(parents=True, exist_ok=True)
    trial = arguments.output_root / (
        f"s{arguments.sequence:02d}-{row['block']}-{row['condition']}-attempt{arguments.attempt}"
    )
    if trial.exists():
        raise SystemExit(f"trial already exists: {trial}")

    with tempfile.TemporaryDirectory(prefix=f"luna-2x2-s{arguments.sequence:02d}-") as temporary:
        temporary_path = Path(temporary)
        prompt_path = temporary_path / "prompt.md"
        metadata_path = temporary_path / "trial-metadata.json"
        prompt_path.write_bytes(prompt)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        command = [
            sys.executable,
            str(DRIVER),
            "--task", str(task),
            "--declaration", str(arguments.declaration.resolve()),
            "--corpus", str(arguments.corpus.resolve()),
            "--capture-binary", str(arguments.capture_binary.resolve()),
            "--trial-dir", str(trial),
            "--prompt-file", str(prompt_path),
            "--trial-metadata", str(metadata_path),
            "--confine", "--observe", "--observe-timeline", "--egress",
            "--runtime-events", "codex-jsonl",
            "--expect-task-hash", experiment["tasks"][row["task"]]["task_content_hash"],
            "--timeout", str(arguments.timeout),
            "--runtime-arg=--json",
            "--runtime-arg=--ignore-user-config",
            "--runtime-arg=--dangerously-bypass-approvals-and-sandbox",
            "--runtime-arg=--ephemeral",
        ]
        completed = subprocess.run(command)

    record_path = trial / "trial.json"
    if record_path.is_file():
        record = json.loads(record_path.read_text())
        if record.get("trial_metadata_sha256") != sha256_file(trial / "trial-metadata.json"):
            raise SystemExit("sealed metadata hash mismatch")
        provenance = record.get("provenance") or {}
        if provenance.get("prompt_sha256") != metadata["combined_prompt_sha256"]:
            raise SystemExit("captured prompt hash mismatch")
        if provenance.get("declaration_sha256") != metadata["declaration_sha256"]:
            raise SystemExit("captured declaration hash mismatch")
    print(trial)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
