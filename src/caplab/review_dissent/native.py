"""Native-agent-system contract for the review-dissent calibration."""

from __future__ import annotations

import json
import os
import shlex
import tempfile
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from caplab.codex_events import is_codex_model_reroute, parse_native_json
from caplab.subject_identity import (
    NativeAgentSystemContractError,
    load_native_agent_system_policy,
    validate_native_agent_systems,
)

from .instrument import (
    _mechanical_result,
    _task_files,
    _valid_review,
    load_calibration_instrument,
    render_review_cell,
)


class NativeReviewContractError(ValueError):
    """A native review instrument, trace, or capture violated its seal."""


_SCHEMA = "caplab.review-dissent.native-instrument/v1"
_ORDER = [
    "r03:gpt",
    "r04:fable",
    "r07:fable",
    "r08:gpt",
    "r02:gpt",
    "r01:fable",
    "r06:fable",
    "r05:gpt",
    "r04:gpt",
    "r03:fable",
    "r08:fable",
    "r07:gpt",
    "r01:gpt",
    "r02:fable",
    "r05:fable",
    "r06:gpt",
]
_INFRASTRUCTURE = {
    "provider_failure",
    "harness_failure",
    "capture_failure",
    "task_image_failure",
    "verifier_failure",
}
_SUBJECT_STATUSES = {"completed", "refused", "invalid"}


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _project_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "src/caplab"
        ).is_dir():
            return candidate
    raise NativeReviewContractError("project_root_not_found")


def _bound_file(project_root: Path, binding: object, field: str) -> Path:
    if not isinstance(binding, dict):
        raise NativeReviewContractError(f"invalid_{field}_binding")
    raw_path = binding.get("path")
    if not isinstance(raw_path, str):
        raise NativeReviewContractError(f"invalid_{field}_path")
    relative = PurePosixPath(raw_path)
    if relative.is_absolute() or any(
        part in {"", ".", ".."} for part in relative.parts
    ):
        raise NativeReviewContractError(f"unsafe_{field}_path")
    candidate = project_root
    for part in relative.parts:
        candidate /= part
        if candidate.is_symlink():
            raise NativeReviewContractError(f"unsafe_{field}_path")
    path = candidate.resolve()
    if not path.is_relative_to(project_root) or not path.is_file():
        raise NativeReviewContractError(f"unsafe_{field}_path")
    if sha256(path.read_bytes()).hexdigest() != binding.get("sha256"):
        raise NativeReviewContractError(f"{field}_file_digest_mismatch")
    return path


def load_native_review_instrument(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load development cells and native tuples without opening held-out bytes."""

    instrument_path = Path(path)
    try:
        instrument = json.loads(instrument_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NativeReviewContractError(f"native_instrument_unreadable:{error}") from error
    if not isinstance(instrument, dict) or instrument.get("schema") != _SCHEMA:
        raise NativeReviewContractError("invalid_native_instrument_schema")
    sealed = dict(instrument)
    claimed = sealed.pop("design_sha256", None)
    if claimed != _digest(sealed):
        raise NativeReviewContractError("native_instrument_digest_mismatch")
    if instrument.get("call_budget") != {
        "authorized_calls": 0,
        "authorized_usd": 0,
    }:
        raise NativeReviewContractError("native_calls_not_authorized")
    if instrument.get("execution_order") != _ORDER:
        raise NativeReviewContractError("native_execution_order_mismatch")

    project_root = _project_root(instrument_path.resolve())
    policy_path = _bound_file(
        project_root, instrument.get("native_agent_policy"), "native_agent_policy"
    )
    base_path = _bound_file(
        project_root, instrument.get("base_instrument"), "base_instrument"
    )
    try:
        policy = load_native_agent_system_policy(policy_path)
        validate_native_agent_systems(policy, instrument.get("agent_systems", {}))
    except NativeAgentSystemContractError as error:
        raise NativeReviewContractError(str(error)) from error

    calibration = load_calibration_instrument(base_path.parent)
    binding = instrument["base_instrument"]
    expected_binding = {
        "design_sha256": calibration["design_sha256"],
        "development_sha256": calibration["artifacts"]["development"]["sha256"],
        "heldout_seal_sha256": calibration["heldout_seal"]["sha256"],
    }
    if any(binding.get(key) != value for key, value in expected_binding.items()):
        raise NativeReviewContractError("base_instrument_binding_mismatch")
    expected_slots = {
        f"{cell_id}:{subject_id}"
        for cell_id in calibration["cells"]
        for subject_id in ("fable", "gpt")
    }
    if set(_ORDER) != expected_slots:
        raise NativeReviewContractError("native_execution_population_mismatch")
    result = dict(instrument)
    result["worlds"] = calibration["worlds"]
    result["cells"] = calibration["cells"]
    result["subject_instruction"] = calibration["subject_instruction"]
    result["human_criteria"] = calibration["human_criteria"]
    result["heldout_seal"] = calibration["heldout_seal"]
    result["_project_root"] = project_root
    result["_base_design_sha256"] = calibration["design_sha256"]
    return result


def _exclusive_json(path: Path, value: object) -> None:
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(_canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def render_native_review_cell(
    instrument: Mapping[str, Any],
    cell_id: str,
    destination: str | os.PathLike[str],
) -> dict[str, str]:
    """Render one development cell and add the native instrument seal."""

    base_seal = render_review_cell(instrument, cell_id, destination)
    root = Path(destination)
    native_seal = {
        "schema": "caplab.review-dissent.native-render/v1",
        "study_id": instrument["study_id"],
        "native_instrument_design_sha256": instrument["design_sha256"],
        "base_instrument_design_sha256": instrument["_base_design_sha256"],
        "cell_id": cell_id,
        "public_task_id": instrument["cells"][cell_id]["public_task_id"],
        "task_image_sha256": base_seal["task_image_sha256"],
    }
    _exclusive_json(root / ".caplab-native-review-task.json", native_seal)
    return {
        "cell_id": cell_id,
        "task_image_sha256": base_seal["task_image_sha256"],
        "native_render_sha256": _digest(native_seal),
    }


def build_native_review_invocation(
    instrument: Mapping[str, Any],
    subject_id: str,
    cell_id: str,
    task_root: str | os.PathLike[str],
) -> dict[str, Any]:
    """Build one native review invocation without launching it."""

    subject = instrument.get("agent_systems", {}).get(subject_id)
    cell = instrument.get("cells", {}).get(cell_id)
    if not isinstance(subject, dict):
        raise NativeReviewContractError("unknown_native_subject")
    if not isinstance(cell, dict) or cell.get("split") != "development":
        raise NativeReviewContractError("unknown_development_cell")
    root = Path(task_root)
    prompt = (
        instrument["subject_instruction"]
        + "\n\nThe task directory is /work. Read TASK.md, ACCEPTANCE.md, "
        "AUTHOR_HANDOFF.md, the target, and relevant tests using fresh evidence. "
        "Write /work/REVIEW.json as exactly one JSON object with keys verdict, "
        "findings, and summary. Each finding must have severity, criterion, path, "
        "and summary. Do not edit any other task file. Your final message may only "
        "briefly report that the review artifact was written."
    )
    command = list(subject["command"])
    if subject["native_harness_id"] == "codex":
        command.extend(["-C", str(root), prompt])
    elif subject["native_harness_id"] == "claude-code":
        command.append(prompt)
    else:
        raise NativeReviewContractError("unknown_native_harness")
    return {
        "subject_id": subject_id,
        "tuple_id": subject["tuple_id"],
        "native_harness_id": subject["native_harness_id"],
        "cell_id": cell_id,
        "cwd": root,
        "command": command,
    }


def _normalize_observed_path(raw: object, available: set[str]) -> str | None:
    if not isinstance(raw, str):
        return None
    value = raw.strip().replace("\\", "/")
    if value.startswith("/work/"):
        value = value[6:]
    elif value.startswith("./"):
        value = value[2:]
    return value if value in available else None


def _command_reads(command: str, available: set[str]) -> set[str]:
    markers = ("cat ", "sed ", "head ", "tail ", "less ", "grep ", "rg ", "open(")
    if not any(marker in command for marker in markers):
        return set()
    observed: set[str] = set()
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    for path in available:
        variants = {path, f"./{path}", f"/work/{path}"}
        if any(variant in tokens for variant in variants) or any(
            variant in command for variant in variants
        ):
            observed.add(path)
    return observed


def observed_reads_from_native_jsonl(
    subject_id: str, content: bytes, available_paths: list[str]
) -> list[str]:
    """Extract conservative file-read evidence from native harness events."""

    if subject_id not in {"fable", "gpt"}:
        raise NativeReviewContractError("unknown_native_subject")
    available = set(available_paths)
    observed: set[str] = set()
    events = _native_events(content)
    for event in events:
        if subject_id == "fable" and event.get("type") == "assistant":
            message = event.get("message", {})
            for block in message.get("content", []) if isinstance(message, dict) else []:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                payload = block.get("input", {})
                if block.get("name") == "Read" and isinstance(payload, dict):
                    path = _normalize_observed_path(payload.get("file_path"), available)
                    if path:
                        observed.add(path)
                elif block.get("name") == "Bash" and isinstance(payload, dict):
                    command = payload.get("command")
                    if isinstance(command, str):
                        observed.update(_command_reads(command, available))
        elif subject_id == "gpt" and event.get("type") in {
            "item.started",
            "item.completed",
        }:
            item = event.get("item", {})
            if isinstance(item, dict) and item.get("type") == "command_execution":
                command = item.get("command")
                if isinstance(command, str):
                    observed.update(_command_reads(command, available))
    return [path for path in available_paths if path in observed]


def _native_events(content: bytes) -> list[dict[str, Any]]:
    try:
        lines = content.decode("utf-8").split("\n")
        if lines[-1] == "":
            lines.pop()
        events = [parse_native_json(line) for line in lines]
    except (UnicodeError, ValueError) as error:
        raise NativeReviewContractError("native_trace_not_jsonl") from error
    if not all(isinstance(event, dict) for event in events):
        raise NativeReviewContractError("native_trace_event_not_object")
    return events


def _native_fallback_markers(message: Mapping[str, Any], line: int, source: str) -> list[dict]:
    """Read explicit native markers only, never strings or nested tool payloads."""
    markers = []
    blocks = message.get("content")
    for index, block in enumerate(blocks if isinstance(blocks, list) else []):
        if isinstance(block, dict) and block.get("type") == "fallback":
            original, fallback = block.get("from"), block.get("to")
            markers.append({"line": line, "source": source + ".content", "index": index,
                            "original_model": original.get("model") if isinstance(original, dict) else None,
                            "fallback_model": fallback.get("model") if isinstance(fallback, dict) else None})
    usage = message.get("usage")
    iterations = usage.get("iterations") if isinstance(usage, dict) else None
    for index, iteration in enumerate(iterations if isinstance(iterations, list) else []):
        if isinstance(iteration, dict) and iteration.get("type") == "fallback_message":
            markers.append({"line": line, "source": source + ".usage.iterations", "index": index,
                            "original_model": None, "fallback_model": iteration.get("model")})
    return markers


def _native_session_evidence(events: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    observations, errors = [], []
    root_id = None
    child_types = {"assistant", "user", "stream_event", "tool_progress"}
    for line, event in enumerate(events, 1):
        parent = event.get("parent_tool_use_id")
        child = (event.get("type") in child_types and isinstance(parent, str) and bool(parent.strip()))
        if parent is not None and not child:
            errors.append({"line": line, "reason": "invalid-session-scope"})
        if "session_id" not in event:
            continue
        session = event["session_id"]
        observations.append({"line": line, "session_id": session, "parent_tool_use_id": parent})
        if not isinstance(session, str) or not session.strip():
            errors.append({"line": line, "reason": "invalid-session-id"})
        elif not child:
            if root_id is not None and session != root_id:
                errors.append({"line": line, "reason": "conflicting-root-session-id"})
            else:
                root_id = session
    return observations, errors


def assess_native_review_model(subject: Mapping[str, Any], content: bytes) -> dict[str, Any]:
    """Assess native-reported model agreement, not full Binding attestation."""
    result: dict[str, Any] = {
        "schema": "caplab.review-dissent.native-model-identity/v1",
        "native_stdout_sha256": sha256(content).hexdigest(),
        "configured_model_id": subject["model_id"],
        "native_harness_id": subject["native_harness_id"],
        "status": "model-unverified",
        "reason": "required-model-evidence-unavailable",
        "initialization_models": [],
        "response_models": [],
        "fallbacks": [],
        "usage_models": [],
        "claim_ceiling": "native-reported model fields only; full Binding unverified",
    }
    try:
        events = _native_events(content)
    except NativeReviewContractError:
        result["reason"] = "native-trace-invalid"
        return result
    if subject["native_harness_id"] == "codex":
        reroutes = [
            {"line": line, "item_id": event["item"].get("id"),
             "message": event["item"]["message"], "source": "item.completed.error"}
            for line, event in enumerate(events, 1) if is_codex_model_reroute(event)
        ]
        if reroutes:
            result["reroutes"] = reroutes
            result["status"] = "model-mismatch"
            result["reason"] = "native-model-reroute"
        return result
    if subject["native_harness_id"] != "claude-code":
        return result
    session_ids, session_errors = _native_session_evidence(events)
    if session_ids:
        result["session_ids"] = session_ids
    if session_errors:
        result["session_errors"] = session_errors
    terminals = []
    stream_models, stream_errors = [], []
    for line, event in enumerate(events, 1):
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            result["initialization_models"].append({"line": line, "model": event.get("model")})
        elif kind == "assistant":
            message = event.get("message")
            model = message.get("model") if isinstance(message, dict) else None
            result["response_models"].append({"line": line, "model": model})
            if isinstance(message, dict):
                result["fallbacks"].extend(_native_fallback_markers(message, line, "assistant.message"))
        elif kind == "stream_event":
            partial = event.get("event")
            if not isinstance(partial, dict) or not isinstance(partial.get("type"), str) or not partial["type"].strip():
                stream_errors.append({"line": line, "reason": "invalid-stream-event-envelope"})
                continue
            if partial["type"] == "message_start":
                message = partial.get("message")
                model = message.get("model") if isinstance(message, dict) else None
                stream_models.append({"line": line, "model": model})
                if isinstance(message, dict):
                    result["fallbacks"].extend(_native_fallback_markers(message, line, "stream_event.message"))
            elif partial["type"] == "content_block_start":
                block = partial.get("content_block")
                if not isinstance(block, dict) or not isinstance(block.get("type"), str) or not block["type"].strip():
                    stream_errors.append({"line": line, "reason": "invalid-content-block-start"})
                    continue
                markers = _native_fallback_markers({"content": [block]}, line, "stream_event")
                for marker in markers:
                    marker.update(source="stream_event.content_block", index=partial.get("index"))
                result["fallbacks"].extend(markers)
            elif partial["type"] == "message_delta":
                result["fallbacks"].extend(_native_fallback_markers(partial, line, "stream_event"))
        elif kind == "system" and event.get("subtype") == "model_refusal_fallback":
            result["fallbacks"].append({
                "line": line, "original_model": event.get("original_model"),
                "fallback_model": event.get("fallback_model"),
            })
        elif kind == "result":
            terminals.append((line, event))
            result["fallbacks"].extend(_native_fallback_markers({"usage": event.get("usage")}, line, "result"))
            usage = event.get("modelUsage")
            if isinstance(usage, dict):
                result["usage_models"].append({"line": line, "models": sorted(usage)})
    initial = result["initialization_models"]
    responses = result["response_models"]
    if stream_models:
        result["stream_models"] = stream_models
    if stream_errors:
        result["stream_errors"] = stream_errors
    models = [entry["model"] for entry in initial + responses + stream_models]
    mismatch = any(
        isinstance(model, str) and model.strip() and model != subject["model_id"]
        for model in models
    )
    if result["fallbacks"] or mismatch:
        result.update(status="model-mismatch", reason="native-model-substitution-or-mismatch")
    elif session_errors:
        result.update(status="model-unverified", reason="native-session-evidence-invalid")
    elif (
        content.endswith(b"\n")
        and len(initial) == 1 and initial[0]["line"] == 1
        and not stream_errors
        and responses and all(model == subject["model_id"] for model in models)
        and len(terminals) == 1 and terminals[0][0] == len(events)
        and terminals[0][1].get("subtype") == "success"
        and terminals[0][1].get("is_error") is False
    ):
        result.update(status="native-model-match", reason="captured-model-fields-agree")
    return result


def _snapshot_task(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    excluded = {
        "REVIEW.json",
        ".caplab-review-task.json",
        ".caplab-native-review-task.json",
    }
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise NativeReviewContractError("native_task_symlink")
        relative = path.relative_to(root).as_posix()
        if path.is_file() and relative not in excluded:
            result[relative] = sha256(path.read_bytes()).hexdigest()
    return result


def _expected_snapshot(instrument: Mapping[str, Any], cell_id: str) -> dict[str, str]:
    return {
        path: sha256(content.encode("utf-8")).hexdigest()
        for path, content in sorted(_task_files(instrument, cell_id).items())
    }


def build_native_review_capture(
    instrument: Mapping[str, Any],
    *,
    cell_id: str,
    subject_id: str,
    task_root: str | os.PathLike[str],
    native_jsonl: bytes,
    status: str,
    observation_sha256: str,
    campaign_manifest_sha256: str,
) -> dict[str, Any]:
    """Normalize and mechanically grade one sealed native review attempt."""

    cell = instrument.get("cells", {}).get(cell_id)
    subject = instrument.get("agent_systems", {}).get(subject_id)
    if not isinstance(cell, dict) or not isinstance(subject, dict):
        raise NativeReviewContractError("unknown_native_capture_identity")
    if status not in _SUBJECT_STATUSES | _INFRASTRUCTURE:
        raise NativeReviewContractError("invalid_native_capture_status")
    root = Path(task_root)
    if root.is_symlink() or not root.is_dir():
        raise NativeReviewContractError("native_task_capture_unavailable")
    expected = _expected_snapshot(instrument, cell_id)
    observed = _snapshot_task(root)
    preserved = expected == observed
    available_paths = list(expected)
    model_identity = assess_native_review_model(subject, native_jsonl)
    model_eligible = model_identity["status"] == "native-model-match"
    observed_reads = observed_reads_from_native_jsonl(
        subject_id, native_jsonl, available_paths
    )
    review: object = None
    review_path = root / "REVIEW.json"
    if review_path.is_symlink():
        raise NativeReviewContractError("native_review_symlink")
    if review_path.is_file():
        try:
            review = json.loads(review_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            review = None
    _, mechanical = _mechanical_result(
        oracle=cell["oracle"],
        status=status if model_eligible else "invalid",
        review=review,
        observed_reads=observed_reads,
        preserved=preserved,
    )
    if status in _INFRASTRUCTURE:
        outcome = "infrastructure"
    elif not model_eligible:
        outcome = "identity-unavailable"
    elif status == "invalid" or status == "completed" and not _valid_review(review):
        outcome = "subject-invalid"
    else:
        outcome = "subject-outcome"
    subject_seal = _digest(
        {
            "study_id": instrument["study_id"],
            "native_instrument_design_sha256": instrument["design_sha256"],
            "cell_id": cell_id,
            "subject_id": subject_id,
            "tuple_id": subject["tuple_id"],
            "native_harness_id": subject["native_harness_id"],
            "model_id": subject["model_id"],
            "effort": subject["effort"],
        }
    )
    capture = {
        "schema": "caplab.review-dissent.native-capture/v2",
        "study_id": instrument["study_id"],
        "native_instrument_design_sha256": instrument["design_sha256"],
        "base_instrument_design_sha256": instrument["_base_design_sha256"],
        "cell_id": cell_id,
        "public_task_id": cell["public_task_id"],
        "subject_id": subject_id,
        "subject_seal": subject_seal,
        "model_identity": model_identity,
        "campaign_manifest_sha256": campaign_manifest_sha256,
        "observation_sha256": observation_sha256,
        "execution_mode": "native-live",
        "status": status,
        "outcome": outcome,
        "review": review if _valid_review(review) else None,
        "observed_reads": observed_reads,
        "preservation": {
            "expected_sha256": _digest(expected),
            "observed_sha256": _digest(observed),
            "preserved": preserved,
        },
        "mechanical": mechanical,
        "human_disposition": None,
    }
    capture["capture_sha256"] = _digest(capture)
    return capture
