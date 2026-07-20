"""Deterministic qualification surface for ``caplab-preference-001``.

This module deliberately has no model, provider, network, subprocess, or
credential integration.  It renders frozen synthetic inputs, captures canned
attempts, applies mechanical oracles, and emits identity-checked blind packets.
"""

from __future__ import annotations

import difflib
import json
import os
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


class PreferenceContractError(ValueError):
    """The frozen study contract or a model-free attempt was unsafe."""


_SCHEMA = "caplab.preference.instrument/v1"
_TASK_SCHEMA = "caplab.preference.task/v1"
_SUBJECTS = {"fable", "gpt"}
_STATUSES = {
    "completed": "complete",
    "partial": "partial",
    "refused": "declined",
    "invalid": "invalid",
    "provider_failure": "infrastructure",
    "harness_failure": "infrastructure",
    "capture_failure": "infrastructure",
    "task_image_failure": "infrastructure",
}
_INFRASTRUCTURE = {
    "provider_failure",
    "harness_failure",
    "capture_failure",
    "task_image_failure",
}
_LEAK_MARKERS = (
    "anthropic",
    "claude",
    "fable",
    "openai",
    "gpt",
    "gpt-5.6",
    "terminus",
)
_EXECUTION_ORDER = [
    "P04:gpt",
    "P01:fable",
    "P06:fable",
    "P03:gpt",
    "P02:gpt",
    "P05:fable",
    "P01:gpt",
    "P04:fable",
    "P05:gpt",
    "P02:fable",
    "P03:fable",
    "P06:gpt",
]
_REVEAL_MAP = {
    "P01": {"A": "gpt", "B": "fable"},
    "P02": {"A": "fable", "B": "gpt"},
    "P03": {"A": "gpt", "B": "fable"},
    "P04": {"A": "fable", "B": "gpt"},
    "P05": {"A": "gpt", "B": "fable"},
    "P06": {"A": "fable", "B": "gpt"},
}


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _load_json_object(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise PreferenceContractError("instrument_is_symlink")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PreferenceContractError(f"instrument_unreadable:{error}") from error
    if not isinstance(value, dict):
        raise PreferenceContractError("instrument_not_object")
    return value


def _safe_relative_path(raw: object) -> PurePosixPath:
    if not isinstance(raw, str) or not raw or "\\" in raw or "\x00" in raw:
        raise PreferenceContractError("unsafe_task_path")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise PreferenceContractError(f"unsafe_task_path:{raw}")
    return path


def _validate_task(task_id: str, task: object) -> None:
    if not isinstance(task, dict) or task.get("schema") != _TASK_SCHEMA:
        raise PreferenceContractError(f"invalid_task_schema:{task_id}")
    if task.get("id") != task_id:
        raise PreferenceContractError(f"task_id_mismatch:{task_id}")
    start_files = task.get("start_files")
    if not isinstance(start_files, dict) or not start_files:
        raise PreferenceContractError(f"missing_start_files:{task_id}")
    for raw_path, content in start_files.items():
        _safe_relative_path(raw_path)
        if not isinstance(content, str):
            raise PreferenceContractError(f"non_text_start_file:{task_id}:{raw_path}")
    constraints = task.get("constraints")
    if not isinstance(constraints, list) or len(constraints) < 8:
        raise PreferenceContractError(f"insufficient_constraints:{task_id}")
    surfaces: set[str] = set()
    constraint_ids: set[str] = set()
    for constraint in constraints:
        if not isinstance(constraint, dict):
            raise PreferenceContractError(f"invalid_constraint:{task_id}")
        constraint_id = constraint.get("id")
        surface = constraint.get("surface")
        oracle = constraint.get("oracle")
        if not isinstance(constraint_id, str) or constraint_id in constraint_ids:
            raise PreferenceContractError(f"invalid_constraint_id:{task_id}")
        if not isinstance(surface, str) or not surface:
            raise PreferenceContractError(f"invalid_constraint_surface:{task_id}:{constraint_id}")
        if not isinstance(oracle, dict) or oracle.get("kind") not in {
            "equals",
            "absent",
            "contains",
            "unchanged",
        }:
            raise PreferenceContractError(f"invalid_oracle:{task_id}:{constraint_id}")
        if oracle.get("path") != "$handoff":
            _safe_relative_path(oracle.get("path"))
        constraint_ids.add(constraint_id)
        surfaces.add(surface)
    if len(surfaces) < 4:
        raise PreferenceContractError(f"insufficient_constraint_surfaces:{task_id}")
    contract = {
        "schema": task["schema"],
        "id": task["id"],
        "instruction": task.get("instruction"),
        "start_files": start_files,
        "constraints": constraints,
    }
    if task.get("contract_sha256") != _digest(contract):
        raise PreferenceContractError(f"task_contract_digest_mismatch:{task_id}")


def load_instrument(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load and validate the frozen, model-free study instrument."""

    instrument = _load_json_object(Path(path))
    if instrument.get("schema") != _SCHEMA:
        raise PreferenceContractError("invalid_instrument_schema")
    if instrument.get("study_id") != "caplab-preference-001":
        raise PreferenceContractError("wrong_study_id")
    harness = instrument.get("harness")
    if harness != {"name": "terminus-2", "version": "2.0.0"}:
        raise PreferenceContractError("unresolved_harness")
    subjects = instrument.get("subjects")
    if not isinstance(subjects, dict) or set(subjects) != _SUBJECTS:
        raise PreferenceContractError("invalid_subjects")
    if {subjects[key].get("model_id") for key in _SUBJECTS} != {
        "claude-fable-5",
        "gpt-5.6-terra",
    }:
        raise PreferenceContractError("unresolved_model_identity")
    surfaces = [_canonical(subjects[key].get("surface")) for key in sorted(_SUBJECTS)]
    if len(set(surfaces)) != 1:
        raise PreferenceContractError("unequal_subject_surface")
    surface = subjects["fable"].get("surface")
    if not isinstance(surface, dict) or set(surface) != {
        "external_network",
        "memory",
        "output_tokens",
        "tools",
        "wall_clock_minutes",
    } or surface.get("output_tokens") != 8192:
        raise PreferenceContractError("invalid_subject_surface")
    if surface.get("wall_clock_minutes") != 45 or surface.get("external_network") is not False:
        raise PreferenceContractError("invalid_subject_surface")
    budget = instrument.get("call_budget")
    if not isinstance(budget, dict) or budget.get("authorized_calls") != 0 or budget.get("authorized_usd") != 0:
        raise PreferenceContractError("model_calls_not_authorized")
    instruction = instrument.get("subject_instruction")
    if not isinstance(instruction, str) or instrument.get("subject_instruction_sha256") != sha256(instruction.encode("utf-8")).hexdigest():
        raise PreferenceContractError("subject_instruction_digest_mismatch")
    order = instrument.get("execution_order")
    if order != _EXECUTION_ORDER:
        raise PreferenceContractError("invalid_execution_order")
    reveal = instrument.get("reveal_map")
    if reveal != _REVEAL_MAP:
        raise PreferenceContractError("invalid_reveal_map")
    tasks = instrument.get("tasks")
    if not isinstance(tasks, dict) or set(tasks) != set(reveal):
        raise PreferenceContractError("invalid_task_population")
    for task_id, task in tasks.items():
        _validate_task(task_id, task)
    sealed = dict(instrument)
    design_sha256 = sealed.pop("design_sha256", None)
    if design_sha256 != _digest(sealed):
        raise PreferenceContractError("instrument_design_digest_mismatch")
    return instrument


def _exclusive_text_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def _refuse_symlink_components(path: Path) -> None:
    for component in (path, *path.parents):
        if component.is_symlink():
            raise PreferenceContractError(f"symlinked_path_component:{component}")


def render_task(instrument: Mapping[str, Any], task_id: str, destination: str | os.PathLike[str]) -> dict[str, str]:
    """Render one fresh synthetic task without invoking an agent or tool."""

    if task_id not in instrument.get("tasks", {}):
        raise PreferenceContractError(f"unknown_task:{task_id}")
    root = Path(destination)
    _refuse_symlink_components(root.parent)
    if root.exists() or root.is_symlink():
        raise PreferenceContractError("destination_exists")
    root.mkdir(parents=True, mode=0o700)
    task = instrument["tasks"][task_id]
    for raw_path, content in sorted(task["start_files"].items()):
        _exclusive_text_write(root.joinpath(*_safe_relative_path(raw_path).parts), content)
    seal = {
        "schema": "caplab.preference.render/v1",
        "study_id": instrument["study_id"],
        "instrument_design_sha256": instrument["design_sha256"],
        "task_id": task_id,
        "task_contract_sha256": task["contract_sha256"],
    }
    _exclusive_text_write(root / ".caplab-task.json", json.dumps(seal, sort_keys=True, separators=(",", ":")) + "\n")
    return {"task_id": task_id, "task_contract_sha256": task["contract_sha256"]}


def _snapshot(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise PreferenceContractError(f"task_symlink:{path.relative_to(root).as_posix()}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative != ".caplab-task.json":
                files[relative] = path.read_text(encoding="utf-8")
    return files


def _diff(before: Mapping[str, str], after: Mapping[str, str]) -> str:
    lines: list[str] = []
    for name in sorted(set(before) | set(after)):
        lines.extend(
            difflib.unified_diff(
                before.get(name, "").splitlines(keepends=True),
                after.get(name, "").splitlines(keepends=True),
                fromfile=f"a/{name}",
                tofile=f"b/{name}",
            )
        )
    return "".join(lines)


def _evaluate(task: Mapping[str, Any], before: Mapping[str, str], after: Mapping[str, str], handoff: str) -> dict[str, list[str]]:
    satisfied: list[str] = []
    missed: list[str] = []
    for constraint in task["constraints"]:
        oracle = constraint["oracle"]
        path = oracle["path"]
        actual = handoff if path == "$handoff" else after.get(path)
        kind = oracle["kind"]
        passed = (
            (kind == "equals" and actual == oracle.get("value"))
            or (kind == "contains" and isinstance(actual, str) and oracle.get("value") in actual)
            or (kind == "absent" and path not in after)
            or (kind == "unchanged" and path in before and actual == before[path])
        )
        (satisfied if passed else missed).append(constraint["id"])
    return {"satisfied": satisfied, "missed": missed}


def _subject_seal(instrument: Mapping[str, Any], task_id: str, subject_id: str) -> str:
    return _digest(
        {
            "study_id": instrument["study_id"],
            "instrument_design_sha256": instrument["design_sha256"],
            "task_id": task_id,
            "task_contract_sha256": instrument["tasks"][task_id]["contract_sha256"],
            "subject_id": subject_id,
            "model_id": instrument["subjects"][subject_id]["model_id"],
            "harness": instrument["harness"],
            "surface": instrument["subjects"][subject_id]["surface"],
            "subject_instruction_sha256": instrument["subject_instruction_sha256"],
        }
    )


def run_canned_attempt(
    instrument: Mapping[str, Any],
    *,
    task_id: str,
    subject_id: str,
    attempt: Mapping[str, Any],
    destination: str | os.PathLike[str],
) -> dict[str, Any]:
    """Capture and mechanically classify a canned, non-inference attempt."""

    if attempt.get("mode") != "canned":
        raise PreferenceContractError("model_calls_not_authorized")
    if subject_id not in _SUBJECTS or subject_id not in instrument.get("subjects", {}):
        raise PreferenceContractError("unknown_subject")
    status = attempt.get("status")
    if status not in _STATUSES:
        raise PreferenceContractError("unknown_attempt_status")
    final_files = attempt.get("final_files")
    handoff = attempt.get("handoff")
    if not isinstance(final_files, dict) or not isinstance(handoff, str):
        raise PreferenceContractError("invalid_canned_attempt")
    render_task(instrument, task_id, destination)
    root = Path(destination)
    before = _snapshot(root)
    for raw_path, content in sorted(final_files.items()):
        path = _safe_relative_path(raw_path)
        if not isinstance(content, str):
            raise PreferenceContractError("non_text_final_file")
        target = root.joinpath(*path.parts)
        if target.is_symlink():
            raise PreferenceContractError(f"task_symlink:{raw_path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="")
    after = _snapshot(root)
    mechanical = _evaluate(instrument["tasks"][task_id], before, after, handoff)
    outcome = _STATUSES[status]
    if status == "completed" and mechanical["missed"]:
        outcome = "partial"
    return {
        "schema": "caplab.preference.capture/v1",
        "task_id": task_id,
        "instrument_design_sha256": instrument["design_sha256"],
        "task_contract_sha256": instrument["tasks"][task_id]["contract_sha256"],
        "subject_seal": _subject_seal(instrument, task_id, subject_id),
        "execution_mode": "canned",
        "outcome": outcome,
        "replacement_eligible": status in _INFRASTRUCTURE,
        "mechanical": mechanical,
        "diff": _diff(before, after),
        "handoff": handoff,
        "human_disposition": None,
    }


def _assert_no_identity_leak(value: object) -> None:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).casefold()
    for marker in _LEAK_MARKERS:
        if marker in encoded:
            raise PreferenceContractError(f"identity_leak:{marker}")


def build_blinded_packet(
    instrument: Mapping[str, Any],
    task_id: str,
    captures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a blind pair packet, refusing rather than redacting leaks."""

    if set(captures) != _SUBJECTS:
        raise PreferenceContractError("incomplete_pair")
    reveal = instrument["reveal_map"][task_id]
    candidates: dict[str, Any] = {}
    for alias in ("A", "B"):
        subject_id = reveal[alias]
        capture = captures[subject_id]
        if (
            capture.get("task_id") != task_id
            or capture.get("instrument_design_sha256") != instrument["design_sha256"]
            or capture.get("task_contract_sha256") != instrument["tasks"][task_id]["contract_sha256"]
            or capture.get("subject_seal") != _subject_seal(instrument, task_id, subject_id)
            or capture.get("human_disposition") is not None
        ):
            raise PreferenceContractError(f"capture_identity_mismatch:{alias}")
        candidate = {
            "outcome": capture.get("outcome"),
            "mechanical": capture.get("mechanical"),
            "diff": capture.get("diff"),
            "handoff": capture.get("handoff"),
        }
        _assert_no_identity_leak(candidate)
        candidates[alias] = candidate
    packet = {
        "schema": "caplab.preference.blind-packet/v1",
        "study_id": instrument["study_id"],
        "pair_id": task_id,
        "task_instruction": instrument["tasks"][task_id]["instruction"],
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


def assess_study_state(captures: list[Mapping[str, Any]], *, blinding_breach: bool = False) -> dict[str, Any]:
    """Apply frozen replacement and preference-adjudication stop rules."""

    replacements = sum(bool(capture.get("replacement")) for capture in captures)
    infrastructure_replacements = sum(
        bool(capture.get("replacement")) and capture.get("outcome") == "infrastructure"
        for capture in captures
    )
    if replacements != infrastructure_replacements:
        raise PreferenceContractError("replacement_for_subject_outcome")
    invalid_pairs = {
        str(capture.get("task_id"))
        for capture in captures
        if capture.get("outcome") == "invalid"
    }
    reasons: list[str] = []
    if replacements > 4:
        reasons.append("replacement_ceiling_exceeded")
    if len(invalid_pairs) > 1:
        reasons.append("more_than_one_invalid_pair")
    if blinding_breach:
        reasons.append("blinding_breach")
    return {
        "replacement_count": replacements,
        "invalid_pair_count": len(invalid_pairs),
        "preference_adjudication_allowed": not reasons,
        "stop_reasons": reasons,
    }
