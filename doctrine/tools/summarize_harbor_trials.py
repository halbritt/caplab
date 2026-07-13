#!/usr/bin/env python3
"""Summarize executed Harbor trial stages from retained job records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


READ_COMMAND = re.compile(r"(?:^|[;&|]\s*)(?:cat|sed|head|tail|less|more|awk)\b")
PACKET_COMMAND = re.compile(r"(?:^|[;&|]\s*)(?:python3?\s+)?\S*assemble_packet\.py\b")
CORPUS_GATE_COMMAND = re.compile(
    r"(?:^|[;&|]\s*)(?:[A-Z_][A-Z0-9_]*=\S+\s+)*make\s+doctrine-check\b"
)


def _tool_commands(trajectory: dict[str, object]) -> list[str]:
    tool_commands: list[str] = []
    for step in trajectory.get("steps", []):
        if not isinstance(step, dict) or step.get("source") != "agent":
            continue
        for call in step.get("tool_calls", []):
            if not isinstance(call, dict):
                continue
            arguments = call.get("arguments", {})
            if not isinstance(arguments, dict):
                continue
            keystrokes = arguments.get("keystrokes")
            if isinstance(keystrokes, str):
                tool_commands.append(keystrokes)
    return tool_commands


def _read_path(command: str, suffix: str) -> bool:
    return bool(
        READ_COMMAND.search(command) and suffix in command and ">" not in command
    )


def _direct_command(command: str) -> str | None:
    stripped = command.rstrip("\r\n")
    if "\n" in stripped or "\r" in stripped:
        return None
    return stripped


def _artifact(path: Path, trial_dir: Path) -> dict[str, str]:
    return {
        "path": str(path.relative_to(trial_dir)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _load_json(path: Path) -> dict[str, object]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"expected JSON object: {path}")
    return document


def _validated_trajectory(trajectory_path: Path) -> dict[str, object]:
    trajectory = _load_json(trajectory_path)
    schema_version = trajectory.get("schema_version")
    if schema_version != "ATIF-v1.7":
        raise ValueError(f"unsupported trajectory schema: {schema_version!r}")
    return trajectory


def _validate_agent_adapter(trial_result: dict[str, object]) -> None:
    agent_info = trial_result.get("agent_info", {})
    agent_name = agent_info.get("name") if isinstance(agent_info, dict) else None
    if agent_name != "terminus-2":
        raise ValueError(f"unsupported agent adapter: {agent_name!r}")


def _direct_commands(trajectory: dict[str, object]) -> list[str]:
    return [
        direct
        for command in _tool_commands(trajectory)
        if (direct := _direct_command(command)) is not None
    ]


def _world_record(verifier_detail: dict[str, object]) -> dict[str, object]:
    world = verifier_detail.get("world", {})
    return world if isinstance(world, dict) else {}


def _trial_stages(
    commands: list[str],
    skill_lock: dict[str, object],
    verifier_detail: dict[str, object],
) -> dict[str, bool]:
    world = _world_record(verifier_detail)
    return {
        "skill_injected": bool(skill_lock.get("skills", [])),
        "skill_read_invoked": any(
            _read_path(command, "SKILL.md") for command in commands
        ),
        "corpus_gate_invoked": any(
            CORPUS_GATE_COMMAND.search(command) for command in commands
        ),
        "packet_assembly_invoked": any(
            PACKET_COMMAND.search(command) for command in commands
        ),
        "evidence_reassembly_invoked": any(
            PACKET_COMMAND.search(command) and "--evidence" in command
            for command in commands
        ),
        "gateway_docs_read_invoked": any(
            _read_path(command, "gateway-api.md") for command in commands
        ),
        "gateway_source_read_invoked": any(
            _read_path(command, "cmd/gateway/main.go") for command in commands
        ),
        "ledger_check_observed": (
            verifier_detail.get("ledger_check_during_agent_phase") is True
        ),
        "replay_probe_observed": world.get("replay_probe_observed") is True,
        "payment_client_modified": world.get("payment_client_modified") is True,
        "gateway_source_modified": world.get("gateway_source_modified") is True,
        "substantial_decision_observed": (
            verifier_detail.get("decision_md_present") is True
        ),
    }


def _trial_metadata(
    trial_dir: Path,
    trial_result: dict[str, object],
    verifier_detail: dict[str, object],
) -> dict[str, object]:
    agent_info = trial_result.get("agent_info", {})
    model_info = (
        agent_info.get("model_info", {}) if isinstance(agent_info, dict) else {}
    )
    return {
        "job_name": trial_dir.parent.name,
        "trial_name": trial_result.get("trial_name", trial_dir.name),
        "task_name": trial_result.get("task_name"),
        "model_name": model_info.get("name") if isinstance(model_info, dict) else None,
        "reward": _trial_reward(trial_result, verifier_detail),
        "agent_error": trial_result.get("exception_info") is not None,
    }


def _trial_reward(
    trial_result: dict[str, object], verifier_detail: dict[str, object]
) -> object:
    if verifier_detail.get("reward") is not None:
        return verifier_detail["reward"]
    verifier_result = trial_result.get("verifier_result", {})
    if not isinstance(verifier_result, dict):
        return None
    rewards = verifier_result.get("rewards", {})
    return rewards.get("reward") if isinstance(rewards, dict) else None


def _trial_artifacts(
    trial_dir: Path, artifact_paths: tuple[Path, ...]
) -> dict[str, object]:
    return {
        str(path.relative_to(trial_dir)): _artifact(path, trial_dir)
        for path in artifact_paths
    }


def _summarize_trial(trajectory_path: Path) -> dict[str, object]:
    trial_dir = trajectory_path.parent.parent
    result_path = trial_dir / "result.json"
    lock_path = trial_dir / "lock.json"
    detail_path = trial_dir / "verifier" / "detail.json"
    trajectory = _validated_trajectory(trajectory_path)
    trial_result = _load_json(result_path)
    _validate_agent_adapter(trial_result)
    skill_lock = _load_json(lock_path)
    verifier_detail = _load_json(detail_path)
    metadata = _trial_metadata(trial_dir, trial_result, verifier_detail)
    metadata["artifacts"] = _trial_artifacts(
        trial_dir, (lock_path, result_path, trajectory_path, detail_path)
    )
    metadata["stages"] = _trial_stages(
        _direct_commands(trajectory), skill_lock, verifier_detail
    )
    return metadata


def summarize(input_paths: list[Path]) -> dict[str, object]:
    trajectory_paths = sorted(
        {
            trajectory
            for path in input_paths
            for trajectory in (
                [path]
                if path.name == "trajectory.json"
                else path.rglob("agent/trajectory.json")
            )
        }
    )
    trials = [_summarize_trial(path) for path in trajectory_paths]
    stage_names = sorted({name for trial in trials for name in trial["stages"]})
    return {
        "schema_version": "harbor-trial-stage-summary/1",
        "trial_count": len(trials),
        "stage_counts": {
            name: sum(trial["stages"][name] is True for trial in trials)
            for name in stage_names
        },
        "trials": trials,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.paths), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
