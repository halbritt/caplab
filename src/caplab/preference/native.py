"""Model-free contract for CAPLAB's corrected native-agent preference study."""

from __future__ import annotations

import json
import os
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

from caplab.subject_identity import (
    NativeAgentSystemContractError,
    load_native_agent_system_policy,
    validate_native_agent_systems,
)

from .instrument import (
    _assert_no_identity_leak,
    _diff,
    _evaluate,
    _snapshot,
    load_instrument,
)


class NativePreferenceContractError(ValueError):
    """The corrected preference instrument does not bind native agent systems."""


_SCHEMA = "caplab.preference.native-instrument/v1"


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _project_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "src/caplab").is_dir():
            return candidate
    raise NativePreferenceContractError("project_root_not_found")


def _bound_file(root: Path, binding: object, field: str) -> Path:
    if not isinstance(binding, dict):
        raise NativePreferenceContractError(f"invalid_{field}_binding")
    relative = binding.get("path")
    if not isinstance(relative, str):
        raise NativePreferenceContractError(f"invalid_{field}_path")
    relative_path = PurePosixPath(relative)
    if relative_path.is_absolute() or any(part in {"", ".", ".."} for part in relative_path.parts):
        raise NativePreferenceContractError(f"unsafe_{field}_path")
    candidate = root
    for part in relative_path.parts:
        candidate /= part
        if candidate.is_symlink():
            raise NativePreferenceContractError(f"unsafe_{field}_path")
    path = candidate.resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise NativePreferenceContractError(f"unsafe_{field}_path")
    if sha256(path.read_bytes()).hexdigest() != binding.get("sha256", binding.get("file_sha256")):
        raise NativePreferenceContractError(f"{field}_file_digest_mismatch")
    return path


def load_native_instrument(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load a zero-call instrument whose subjects are native harness tuples."""

    instrument_path = Path(path)
    try:
        instrument = json.loads(instrument_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NativePreferenceContractError(f"instrument_unreadable:{error}") from error
    if not isinstance(instrument, dict) or instrument.get("schema") != _SCHEMA:
        raise NativePreferenceContractError("invalid_native_instrument_schema")
    sealed = dict(instrument)
    claimed = sealed.pop("design_sha256", None)
    if claimed != sha256(_canonical(sealed)).hexdigest():
        raise NativePreferenceContractError("native_instrument_digest_mismatch")
    budget = instrument.get("call_budget")
    if budget != {"authorized_calls": 0, "authorized_usd": 0}:
        raise NativePreferenceContractError("model_calls_not_authorized")

    root = _project_root(instrument_path.resolve())
    policy_path = _bound_file(root, instrument.get("native_agent_policy"), "native_agent_policy")
    task_bank_path = _bound_file(root, instrument.get("task_bank"), "task_bank")
    try:
        policy = load_native_agent_system_policy(policy_path)
        validate_native_agent_systems(policy, instrument.get("agent_systems", {}))
    except NativeAgentSystemContractError as error:
        raise NativePreferenceContractError(str(error)) from error
    task_bank = load_instrument(task_bank_path)
    if task_bank["design_sha256"] != instrument["task_bank"].get("design_sha256"):
        raise NativePreferenceContractError("task_bank_design_mismatch")
    admitted_fields = instrument["task_bank"].get("admitted_fields")
    if admitted_fields != ["subject_instruction", "subject_instruction_sha256", "tasks"]:
        raise NativePreferenceContractError("invalid_task_bank_projection")
    task_projection = {field: task_bank[field] for field in admitted_fields}
    task_projection["source_design_sha256"] = task_bank["design_sha256"]
    reveal_map = instrument.get("reveal_map")
    order = instrument.get("execution_order")
    if not isinstance(reveal_map, dict) or set(reveal_map) != set(task_bank["tasks"]):
        raise NativePreferenceContractError("invalid_native_reveal_map")
    expected_slots = {
        f"{task_id}:{subject_id}"
        for task_id in reveal_map
        for subject_id in ("fable", "gpt")
    }
    if not isinstance(order, list) or len(order) != 12 or set(order) != expected_slots:
        raise NativePreferenceContractError("invalid_native_execution_order")
    if any(
        not isinstance(mapping, dict)
        or set(mapping) != {"A", "B"}
        or set(mapping.values()) != {"fable", "gpt"}
        for mapping in reveal_map.values()
    ):
        raise NativePreferenceContractError("invalid_native_reveal_map")
    result = dict(instrument)
    result["_project_root"] = root
    result["_task_bank"] = task_projection
    return result


def _safe_relative_path(raw: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise NativePreferenceContractError(f"unsafe_task_path:{raw}")
    return path


def _exclusive_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def render_native_task(
    instrument: dict[str, Any], task_id: str, destination: str | os.PathLike[str]
) -> dict[str, str]:
    """Render a fresh task bank entry under the corrected native-study seal."""

    task = instrument.get("_task_bank", {}).get("tasks", {}).get(task_id)
    if not isinstance(task, dict):
        raise NativePreferenceContractError("unknown_task")
    root = Path(destination)
    if root.exists() or root.is_symlink():
        raise NativePreferenceContractError("task_destination_exists")
    root.mkdir(parents=True, mode=0o700)
    for raw_path, content in sorted(task["start_files"].items()):
        relative = _safe_relative_path(raw_path)
        _exclusive_text(root.joinpath(*relative.parts), content)
    seal = {
        "schema": "caplab.preference.native-render/v1",
        "study_id": instrument["study_id"],
        "instrument_design_sha256": instrument["design_sha256"],
        "task_id": task_id,
        "task_contract_sha256": task["contract_sha256"],
    }
    _exclusive_text(
        root / ".caplab-task.json",
        json.dumps(seal, sort_keys=True, separators=(",", ":")) + "\n",
    )
    return {"task_id": task_id, "task_contract_sha256": task["contract_sha256"]}


def build_native_invocation(
    instrument: dict[str, Any],
    subject_id: str,
    task_id: str,
    task_root: str | os.PathLike[str],
) -> dict[str, Any]:
    """Build one native CLI invocation without launching it."""

    subject = instrument.get("agent_systems", {}).get(subject_id)
    task_bank = instrument.get("_task_bank", {})
    task = task_bank.get("tasks", {}).get(task_id)
    if not isinstance(subject, dict):
        raise NativePreferenceContractError("unknown_subject")
    if not isinstance(task, dict):
        raise NativePreferenceContractError("unknown_task")
    root = Path(task_root)
    prompt = (
        task_bank["subject_instruction"]
        + "\n\nTask: "
        + task["instruction"]
        + "\n\nWork only inside the supplied task directory. Your final message is the $handoff artifact."
    )
    command = list(subject["command"])
    if subject["native_harness_id"] == "codex":
        command.extend(["-C", str(root), prompt])
    elif subject["native_harness_id"] == "claude-code":
        command.append(prompt)
    else:
        raise NativePreferenceContractError("unknown_native_harness")
    return {
        "subject_id": subject_id,
        "tuple_id": subject["tuple_id"],
        "native_harness_id": subject["native_harness_id"],
        "cwd": root,
        "command": command,
    }


def _native_subject_seal(
    instrument: dict[str, Any], task_id: str, subject_id: str
) -> str:
    subject = instrument["agent_systems"][subject_id]
    task = instrument["_task_bank"]["tasks"][task_id]
    return sha256(
        _canonical(
            {
                "study_id": instrument["study_id"],
                "instrument_design_sha256": instrument["design_sha256"],
                "task_id": task_id,
                "task_contract_sha256": task["contract_sha256"],
                "subject_id": subject_id,
                "tuple_id": subject["tuple_id"],
                "native_harness_id": subject["native_harness_id"],
                "model_id": subject["model_id"],
                "effort": subject["effort"],
            }
        )
    ).hexdigest()


def build_native_capture(
    instrument: dict[str, Any], *, task_id: str, subject_id: str,
    task_root: str | os.PathLike[str], handoff: str,
    observation_sha256: str, campaign_manifest_sha256: str,
) -> dict[str, Any]:
    """Normalize one completed native attempt under the corrected seal."""

    task = instrument.get("_task_bank", {}).get("tasks", {}).get(task_id)
    if not isinstance(task, dict) or subject_id not in instrument.get("agent_systems", {}):
        raise NativePreferenceContractError("unknown_native_capture_identity")
    if not isinstance(handoff, str) or not handoff.strip():
        raise NativePreferenceContractError("native_handoff_missing")
    root = Path(task_root)
    if root.is_symlink() or not root.is_dir():
        raise NativePreferenceContractError("native_task_capture_unavailable")
    before = dict(task["start_files"])
    after = _snapshot(root)
    mechanical = _evaluate(task, before, after, handoff)
    return {
        "schema": "caplab.preference.native-capture/v1",
        "task_id": task_id,
        "instrument_design_sha256": instrument["design_sha256"],
        "task_contract_sha256": task["contract_sha256"],
        "subject_seal": _native_subject_seal(instrument, task_id, subject_id),
        "campaign_manifest_sha256": campaign_manifest_sha256,
        "observation_sha256": observation_sha256,
        "execution_mode": "native-live",
        "outcome": "complete" if not mechanical["missed"] else "partial",
        "replacement_eligible": False,
        "mechanical": mechanical,
        "diff": _diff(before, after),
        "handoff": handoff,
        "human_disposition": None,
    }


def build_native_blinded_packet(
    instrument: dict[str, Any], task_id: str,
    captures: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build one identity-free pair from corrected native captures."""

    if set(captures) != {"fable", "gpt"}:
        raise NativePreferenceContractError("incomplete_native_pair")
    candidates: dict[str, Any] = {}
    for alias in ("A", "B"):
        subject_id = instrument["reveal_map"][task_id][alias]
        capture = captures[subject_id]
        task = instrument["_task_bank"]["tasks"][task_id]
        if (
            capture.get("task_id") != task_id
            or capture.get("instrument_design_sha256") != instrument["design_sha256"]
            or capture.get("task_contract_sha256") != task["contract_sha256"]
            or capture.get("subject_seal")
            != _native_subject_seal(instrument, task_id, subject_id)
            or capture.get("human_disposition") is not None
        ):
            raise NativePreferenceContractError(
                f"native_capture_identity_mismatch:{alias}"
            )
        candidate = {
            "outcome": capture["outcome"],
            "mechanical": capture["mechanical"],
            "diff": capture["diff"],
            "handoff": capture["handoff"],
        }
        _assert_no_identity_leak(candidate)
        candidates[alias] = candidate
    packet = {
        "schema": "caplab.preference.native-blind-packet/v1",
        "study_id": instrument["study_id"],
        "instrument_design_sha256": instrument["design_sha256"],
        "pair_id": task_id,
        "task_instruction": instrument["_task_bank"]["tasks"][task_id]["instruction"],
        "candidates": candidates,
        "adjudication": {
            "selection": None,
            "allowed_selections": ["A", "B", "tie", "unjudgeable"],
            "reasons": [
                "more complete requested effect",
                "better mandatory-constraint coverage",
                "safer authority and preservation behavior",
                "better evidence and failure handling",
                "clearer, more accurate handoff",
                "presentation preference only",
            ],
        },
    }
    _assert_no_identity_leak(packet)
    return packet
