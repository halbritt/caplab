#!/usr/bin/env python3
"""Summarize executed trial stages from retained job records.

Two trial layouts are accepted, both fail-closed on unknown formats:
Harbor jobs (terminus-2 agent, ATIF-v1.7 trajectory) and native
workspace-capture trials (trial.json with schema native-capture-trial/1,
whose runtime_events field names how executed commands can be read from
capture/runtime.log)."""

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
    metadata["adapter"] = "harbor"
    metadata["artifacts"] = _trial_artifacts(
        trial_dir, (lock_path, result_path, trajectory_path, detail_path)
    )
    metadata["stages"] = _trial_stages(
        _direct_commands(trajectory), skill_lock, verifier_detail
    )
    return metadata


_BASH_WRAPPER = re.compile(r"^/(?:usr/)?bin/(?:ba)?sh\s+-[a-z]*c\s+")


def _unwrap_shell(command: str) -> str:
    """Strip codex's `/bin/bash -lc '<cmd>'` wrapper so the read/gate
    regexes, which anchor at start-of-string or after a shell separator,
    see the actual command rather than the wrapper's own argv."""
    match = _BASH_WRAPPER.match(command)
    if not match:
        return command
    inner = command[match.end():].strip()
    if len(inner) >= 2 and inner[0] == inner[-1] and inner[0] in "'\"":
        inner = inner[1:-1]
    return inner


def _native_commands(trial_record: dict[str, object], runtime_log: Path) -> list[str]:
    """Executed commands per the trial's declared runtime_events format.

    Faking a supported format would subvert the fail-closed design the same
    way faking terminus-2 metadata would; formats are declared by the
    runner from the declaration it dispatched, never sniffed. codex emits a
    command as an item.started then an item.completed with the same id; only
    the completed event is counted, so a command is never double-read.
    """
    events_format = trial_record.get("runtime_events")
    if events_format == "none":
        return []
    if events_format != "codex-jsonl":
        raise ValueError(f"unsupported runtime_events format: {events_format!r}")
    if not runtime_log.is_file():
        # A capture that failed before writing runtime.log has no executed
        # commands to read; the trial still counts, with its verifier-derived
        # world stages, rather than crashing the whole summary.
        return []
    commands: list[str] = []
    for line in runtime_log.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "command_execution":
            command = item.get("command")
            if isinstance(command, str):
                commands.append(_unwrap_shell(command))
    return commands


def _summarize_native_trial(record_path: Path) -> dict[str, object]:
    trial_dir = record_path.parent
    trial_record = _load_json(record_path)
    schema_version = trial_record.get("schema_version")
    if schema_version != "native-capture-trial/1":
        raise ValueError(f"unsupported native trial schema: {schema_version!r}")
    detail_path = trial_dir / "verifier" / "detail.json"
    runtime_log = trial_dir / "capture" / "runtime.log"
    verifier_detail = _load_json(detail_path) if detail_path.is_file() else {}
    provenance = trial_record.get("provenance", {})
    metadata = {
        "adapter": "native-capture",
        "job_name": trial_dir.parent.name,
        "trial_name": trial_dir.name,
        "task_name": trial_record.get("task_name"),
        "model_name": provenance.get("backend_id") if isinstance(provenance, dict) else None,
        "reward": trial_record.get("reward"),
        "agent_error": trial_record.get("capture_exit") not in (0, 3),
        "artifacts": _trial_artifacts(
            trial_dir,
            tuple(p for p in (record_path, detail_path, runtime_log) if p.is_file()),
        ),
        "stages": _trial_stages(
            [
                direct
                for command in _native_commands(trial_record, runtime_log)
                if (direct := _direct_command(command)) is not None
            ],
            {},  # native conditions are bare: no skill injection surface
            verifier_detail,
        ),
    }
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
    native_record_paths = sorted(
        {
            record
            for path in input_paths
            for record in (
                [path] if path.name == "trial.json" else path.rglob("trial.json")
            )
        }
    )
    trials = [_summarize_trial(path) for path in trajectory_paths] + [
        _summarize_native_trial(path) for path in native_record_paths
    ]
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
