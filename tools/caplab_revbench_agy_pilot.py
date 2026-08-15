#!/usr/bin/env python3
"""Run the bounded Gemini 3.7 Flash Revbench engineering pilot through AGY."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence

from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.subject_identity import (
    NativeAgentSystemContractError,
    load_native_agent_system_policy,
    validate_native_agent_systems,
)


ROOT = Path(__file__).resolve().parents[1]
NATIVE_POLICY = ROOT / "docs" / "product" / "contracts" / "native-agent-systems.json"
PILOT_NATIVE_POLICY = (
    ROOT / "docs" / "product" / "contracts" / "native-agent-systems-agy-pilot.json"
)
EFFORTS = ("low", "medium", "high")
EXPECTED_AGY_VERSION = "1.1.13"
EXPECTED_AGY_SHA256 = "416b197e4b38c797c8661098f0af2bb4e1323ffe3c286d5e9b6408cf7d7ee920"
MAX_STREAM_BYTES = 1024 * 1024
PROCESS_TIMEOUT_SECONDS = 150
_UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_JSON_POINTER = re.compile(r"^(?:/(?:[^~/]|~[01])*)*$")

RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "verdict", "anchors"],
    "properties": {
        "schema_version": {"const": "caplab-revbench-native-response/1"},
        "verdict": {"enum": ["clean", "defect"]},
        "anchors": {"type": "array", "items": {"type": "string"}},
    },
}
RESPONSE_SCHEMA_ARGUMENT = canonical_json(RESPONSE_SCHEMA).decode("utf-8")

CASES = (
    {
        "case_id": "case-a",
        "control": {"n": 5},
        "mutant": {"n": 0},
        "oracle": {
            "kind": "json-integer-minimum/1",
            "pointer": "/n",
            "minimum": 1,
        },
        "defect_anchor": "/n",
        "assignment_order": ["control", "mutant"],
    },
    {
        "case_id": "case-b",
        "control": {"label": "b", "limits": {"minimum": 7}},
        "mutant": {"label": "b", "limits": {"minimum": 2}},
        "oracle": {
            "kind": "json-integer-minimum/1",
            "pointer": "/limits/minimum",
            "minimum": 5,
        },
        "defect_anchor": "/limits/minimum",
        "assignment_order": ["mutant", "control"],
    },
)

_CONFIG_SURFACE_KEYS = (
    "allowNonWorkspaceAccess",
    "artifactReviewPolicy",
    "customModelsConfig",
    "disableSlashCommands",
    "enableTelemetry",
    "enableTerminalSandbox",
    "modelProvider",
    "permissions",
    "toolPermission",
    "useG1Credits",
)


class AgyPilotError(ValueError):
    """The requested AGY pilot operation was refused."""


class AgyTransportError(AgyPilotError):
    """AGY did not produce one interpretable terminal envelope."""


class AgyResponseError(AgyPilotError):
    """AGY completed a turn with a response outside the frozen response schema."""


@dataclass(frozen=True)
class DerivedAgyEnvelope:
    raw_response: Any
    conversation_id: str | None
    usage: dict[str, int]
    duration_seconds: float | None


@dataclass(frozen=True)
class DerivedAgyResponse:
    response: dict[str, Any]
    response_bytes: bytes
    conversation_id: str | None
    usage: dict[str, int]
    duration_seconds: float | None


def _timestamp(moment: datetime | None = None) -> str:
    value = moment or datetime.now(UTC)
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _json_object(payload: bytes, role: str) -> dict[str, Any]:
    try:
        value = json.loads(payload, object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise AgyTransportError(f"{role}_envelope_invalid") from error
    if not isinstance(value, dict):
        raise AgyTransportError(f"{role}_envelope_not_object")
    return value


def _validated_response(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, ValueError) as error:
            raise AgyResponseError("response_not_json_object") from error
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "verdict",
        "anchors",
    }:
        raise AgyResponseError("response_shape_invalid")
    if value["schema_version"] != "caplab-revbench-native-response/1":
        raise AgyResponseError("response_schema_version_invalid")
    verdict = value["verdict"]
    anchors = value["anchors"]
    if verdict not in {"clean", "defect"}:
        raise AgyResponseError("response_verdict_invalid")
    if (
        not isinstance(anchors, list)
        or not all(
            isinstance(anchor, str) and _JSON_POINTER.fullmatch(anchor)
            for anchor in anchors
        )
        or anchors != sorted(set(anchors))
    ):
        raise AgyResponseError("response_anchors_invalid")
    if (verdict == "clean" and anchors) or (verdict == "defect" and not anchors):
        raise AgyResponseError("response_verdict_and_anchors_disagree")
    return copy.deepcopy(value)


def _derive_agy_envelope(raw_stdout: bytes) -> DerivedAgyEnvelope:
    envelope = _json_object(raw_stdout, "agy")
    if "response" not in envelope:
        raise AgyTransportError("agy_envelope_response_missing")
    if envelope.get("status", "SUCCESS") != "SUCCESS":
        raise AgyTransportError("agy_envelope_status_not_success")
    conversation_id = envelope.get("conversation_id")
    if conversation_id is not None and not isinstance(conversation_id, str):
        raise AgyTransportError("agy_envelope_conversation_id_invalid")
    raw_usage = envelope.get("usage", {})
    if not isinstance(raw_usage, dict) or any(
        not isinstance(key, str)
        or isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        for key, value in raw_usage.items()
    ):
        raise AgyTransportError("agy_envelope_usage_invalid")
    duration = envelope.get("duration_seconds")
    if duration is None and "duration_ms" in envelope:
        milliseconds = envelope["duration_ms"]
        if isinstance(milliseconds, bool) or not isinstance(milliseconds, (int, float)):
            raise AgyTransportError("agy_envelope_duration_invalid")
        duration = milliseconds / 1000
    if duration is not None and (
        isinstance(duration, bool)
        or not isinstance(duration, (int, float))
        or duration < 0
    ):
        raise AgyTransportError("agy_envelope_duration_invalid")
    return DerivedAgyEnvelope(
        raw_response=copy.deepcopy(envelope["response"]),
        conversation_id=conversation_id,
        usage={key: int(value) for key, value in raw_usage.items()},
        duration_seconds=None if duration is None else float(duration),
    )


def derive_agy_response(raw_stdout: bytes) -> DerivedAgyResponse:
    """Derive one strict Revbench response from AGY print-mode JSON."""

    envelope = _derive_agy_envelope(raw_stdout)
    response = _validated_response(envelope.raw_response)
    return DerivedAgyResponse(
        response=response,
        response_bytes=canonical_json(response),
        conversation_id=envelope.conversation_id,
        usage=envelope.usage,
        duration_seconds=envelope.duration_seconds,
    )


def native_subject(effort: str) -> dict[str, Any]:
    """Return the exact logical AGY subject command for one effort binding."""

    if effort not in EFFORTS:
        raise AgyPilotError("unsupported_effort")
    return {
        "tuple_id": f"agy-gemini-3-7-flash-{effort}",
        "model_id": "gemini-3.7-flash",
        "native_harness_id": "antigravity-cli",
        "effort": effort,
        "command": [
            "agy",
            "--model",
            f"gemini-3.7-flash-{effort}",
            "--effort",
            effort,
            "--mode",
            "plan",
            "--sandbox",
            "--output-format",
            "json",
            "--json-schema",
            RESPONSE_SCHEMA_ARGUMENT,
            "--print-timeout",
            "2m0s",
            "--print",
        ],
        "version_command": ["agy", "--version"],
    }


def load_pilot_native_policy() -> tuple[dict[str, Any], dict[str, Any]]:
    """Enforce the canonical policy before loading the additive pilot tuples."""

    base = load_native_agent_system_policy(NATIVE_POLICY)
    pilot = load_native_agent_system_policy(PILOT_NATIVE_POLICY)
    base_reference = pilot.get("base_policy")
    if not isinstance(base_reference, dict) or base_reference != {
        "path": "docs/product/contracts/native-agent-systems.json",
        "sha256": sha256_hex(NATIVE_POLICY.read_bytes()),
    }:
        raise AgyPilotError("base_native_agent_policy_digest_mismatch")
    if pilot.get("policy") != base.get("policy") or pilot.get(
        "forbidden_proxy_markers"
    ) != base.get("forbidden_proxy_markers"):
        raise AgyPilotError("native_agent_policy_invariant_mismatch")
    return base, pilot


def _ratio(numerator: int, denominator: int) -> dict[str, int]:
    if denominator < 1:
        raise AgyPilotError("metric_denominator_invalid")
    divisor = math.gcd(abs(numerator), denominator)
    return {
        "numerator": numerator // divisor,
        "denominator": denominator // divisor,
    }


def score_attempts(attempts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Compute paired Revbench metrics without pooling effort bindings."""

    cases = {case["case_id"]: case for case in CASES}
    result: dict[str, Any] = {}
    for effort in EFFORTS:
        selected: dict[tuple[str, str], Mapping[str, Any]] = {}
        for attempt in attempts:
            if attempt.get("effort") != effort:
                continue
            key = (str(attempt.get("case_id")), str(attempt.get("arm")))
            if key[0] not in cases or key[1] not in {"control", "mutant"}:
                raise AgyPilotError("attempt_assignment_invalid")
            if key in selected:
                raise AgyPilotError("duplicate_attempt_assignment")
            selected[key] = attempt
        planned = len(CASES) * 2
        attempted = len(selected)
        missing = planned - attempted
        subject_failures = 0
        infrastructure_failures = 0
        excluded = 0
        usable = 0
        usable_pairs = 0
        caught_mutants = 0
        false_alarms = 0
        exact_anchor_calls = 0
        mutant_defect_calls = 0
        conforming = 0
        reported_usage: dict[str, int] = {}
        reported_duration_milliseconds = 0
        reported_duration_count = 0
        conversation_ids = 0
        excluded_cases: list[dict[str, Any]] = []
        for attempt in selected.values():
            disposition = attempt.get("disposition")
            verdict = attempt.get("verdict")
            anchors = attempt.get("anchors")
            usage = attempt.get("usage", {})
            if not isinstance(usage, Mapping) or any(
                not isinstance(key, str)
                or isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
                for key, value in usage.items()
            ):
                raise AgyPilotError("attempt_usage_invalid")
            for key, value in usage.items():
                reported_usage[key] = reported_usage.get(key, 0) + value
            duration = attempt.get("duration_milliseconds")
            if duration is not None:
                if (
                    isinstance(duration, bool)
                    or not isinstance(duration, int)
                    or duration < 0
                ):
                    raise AgyPilotError("attempt_duration_invalid")
                reported_duration_milliseconds += duration
                reported_duration_count += 1
            conversation_id = attempt.get("conversation_id")
            if conversation_id is not None:
                if not isinstance(conversation_id, str):
                    raise AgyPilotError("attempt_conversation_id_invalid")
                conversation_ids += 1
            if disposition == "subject-failure":
                subject_failures += 1
            elif disposition == "infrastructure-failure":
                infrastructure_failures += 1
            elif disposition == "complete" and (
                (verdict == "clean" and anchors == [])
                or (verdict == "defect" and isinstance(anchors, list) and bool(anchors))
            ):
                conforming += 1
            elif disposition != "complete":
                raise AgyPilotError("attempt_disposition_invalid")
        for case in CASES:
            pair = {
                arm: selected.get((case["case_id"], arm))
                for arm in ("control", "mutant")
            }
            eligible: dict[str, bool] = {}
            reasons: list[str] = []
            for arm, attempt in pair.items():
                if attempt is None:
                    eligible[arm] = False
                    reasons.append(f"missing-{arm}")
                elif attempt.get("disposition") != "complete":
                    eligible[arm] = False
                    reasons.append(f"{attempt.get('disposition')}-{arm}")
                elif attempt.get("verdict") not in {"clean", "defect"}:
                    eligible[arm] = False
                    reasons.append(f"invalid-{arm}")
                else:
                    eligible[arm] = True
            if all(eligible.values()):
                usable += 2
                usable_pairs += 1
                control = pair["control"]
                mutant = pair["mutant"]
                assert control is not None and mutant is not None
                if control["verdict"] == "defect":
                    false_alarms += 1
                if mutant["verdict"] == "defect":
                    mutant_defect_calls += 1
                    if mutant["anchors"] == [case["defect_anchor"]]:
                        exact_anchor_calls += 1
                        caught_mutants += 1
            else:
                excluded += sum(1 for arm in ("control", "mutant") if eligible[arm])
                excluded_cases.append(
                    {"case_id": case["case_id"], "reasons": sorted(reasons)}
                )
        metrics: dict[str, Any] = {"conformance_rate": _ratio(conforming, planned)}
        if usable_pairs:
            metrics.update(
                {
                    "catch_rate": _ratio(caught_mutants, usable_pairs),
                    "false_alarm_rate": _ratio(false_alarms, usable_pairs),
                    "discrimination": _ratio(
                        caught_mutants - false_alarms, usable_pairs
                    ),
                }
            )
            if mutant_defect_calls:
                metrics["anchor_hit_rate"] = _ratio(
                    exact_anchor_calls, mutant_defect_calls
                )
        sample_flow = {
            "planned": planned,
            "attempted": attempted,
            "usable": usable,
            "excluded": excluded,
            "missing": missing,
            "subject_failures": subject_failures,
            "infrastructure_failures": infrastructure_failures,
        }
        if attempted + missing != planned:
            raise AgyPilotError("attempt_partition_invalid")
        disposition = (
            "infrastructure-failure"
            if infrastructure_failures
            else "incomplete"
            if missing or subject_failures or excluded
            else "complete"
        )
        result[effort] = {
            "subject": native_subject(effort),
            "disposition": disposition,
            "sample_flow": sample_flow,
            "counts": {
                "usable_pairs": usable_pairs,
                "caught_mutants": caught_mutants,
                "false_alarm_controls": false_alarms,
                "exact_anchor_calls": exact_anchor_calls,
                "mutant_defect_calls": mutant_defect_calls,
                "conforming_attempts": conforming,
            },
            "operational_observations": {
                "reported_usage_totals": dict(sorted(reported_usage.items())),
                "reported_duration_milliseconds_total": (
                    reported_duration_milliseconds
                ),
                "reported_duration_count": reported_duration_count,
                "conversation_id_count": conversation_ids,
            },
            "metrics": metrics,
            "excluded_cases": excluded_cases,
        }
    return result


def _real_directory(path: Path, role: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise AgyPilotError(f"{role}_unavailable") from error
    if not stat.S_ISDIR(metadata.st_mode) or path.is_symlink():
        raise AgyPilotError(f"{role}_must_be_real_directory")


def _write_exclusive(path: Path, payload: bytes, mode: int = 0o440) -> None:
    _real_directory(path.parent, "output_parent")
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, mode)
    except FileExistsError as error:
        raise AgyPilotError("output_exists") from error
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(payload)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        parent_descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
    except OSError as error:
        raise AgyPilotError("output_write_failed") from error


def _fsync_directory(path: Path) -> None:
    _real_directory(path, "sync_directory")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        raise AgyPilotError("directory_sync_failed") from error


def _write_document(path: Path, document: Mapping[str, Any]) -> None:
    _write_exclusive(path, canonical_json(document) + b"\n")


def _read_document(path: Path, role: str) -> dict[str, Any]:
    try:
        metadata = path.lstat()
        payload = path.read_bytes()
        document = json.loads(payload, object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise AgyPilotError(f"{role}_invalid") from error
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise AgyPilotError(f"{role}_must_be_real_file")
    if not isinstance(document, dict) or payload != canonical_json(document) + b"\n":
        raise AgyPilotError(f"{role}_not_canonical")
    return document


def _read_bytes(path: Path, role: str) -> bytes:
    try:
        metadata = path.lstat()
        payload = path.read_bytes()
    except OSError as error:
        raise AgyPilotError(f"{role}_invalid") from error
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise AgyPilotError(f"{role}_must_be_real_file")
    return payload


def _ensure_child_directory(parent: Path, name: str) -> Path:
    _real_directory(parent, "directory_parent")
    path = parent / name
    try:
        path.mkdir(mode=0o750)
    except FileExistsError:
        _real_directory(path, "directory")
    return path


def record_attempt_intent(directory: Path, identity: Mapping[str, Any]) -> None:
    """Durably claim one attempt before the provider-capable process starts."""

    try:
        directory.mkdir(mode=0o750)
    except FileExistsError as error:
        raise AgyPilotError("attempt_already_claimed") from error
    _write_document(directory / "intent.json", identity)
    _fsync_directory(directory.parent)


def _pilot_environment() -> dict[str, str]:
    home = os.environ.get("HOME")
    if home != "/home/halbritt":
        raise AgyPilotError("agy_owner_home_drift")
    return {
        "HOME": home,
        "PATH": "/nonexistent",
        "LANG": "C.UTF-8",
        "AGY_CLI_HIDE_ACCOUNT_INFO": "1",
    }


def _run_read_only(
    argv: Sequence[str], *, cwd: Path
) -> subprocess.CompletedProcess[bytes]:
    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            env=_pilot_environment(),
            check=False,
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise AgyPilotError("agy_preflight_failed") from error
    if completed.returncode != 0:
        raise AgyPilotError("agy_preflight_failed")
    return completed


def _resolve_agy() -> Path:
    value = shutil.which(
        "agy", path="/home/halbritt/.local/bin:/usr/local/bin:/usr/bin:/bin"
    )
    if value is None:
        raise AgyPilotError("agy_executable_unavailable")
    path = Path(os.path.abspath(value))
    try:
        metadata = path.lstat()
        payload = path.read_bytes()
    except OSError as error:
        raise AgyPilotError("agy_executable_unavailable") from error
    if (
        not stat.S_ISREG(metadata.st_mode)
        or path.is_symlink()
        or metadata.st_mode & 0o111 == 0
    ):
        raise AgyPilotError("agy_executable_invalid")
    if sha256_hex(payload) != EXPECTED_AGY_SHA256:
        raise AgyPilotError("agy_executable_drift")
    return path


def _slash_envelope(agy: Path, command: str, cwd: Path) -> dict[str, Any]:
    completed = _run_read_only(
        [str(agy), "--output-format", "json", "--print", command], cwd=cwd
    )
    envelope = _json_object(completed.stdout, f"agy_{command[1:]}")
    usage = envelope.get("usage")
    if not isinstance(usage, dict) or usage.get("total_tokens") != 0:
        raise AgyPilotError("agy_slash_preflight_used_model_tokens")
    if envelope.get("conversation_id") != "" or envelope.get("num_turns") != 0:
        raise AgyPilotError("agy_slash_preflight_started_conversation")
    return envelope


def _preflight_snapshot(agy: Path, cwd: Path) -> dict[str, Any]:
    version = _run_read_only([str(agy), "--version"], cwd=cwd)
    if version.stdout != f"{EXPECTED_AGY_VERSION}\n".encode() or version.stderr:
        raise AgyPilotError("agy_version_drift")
    models = _run_read_only([str(agy), "models"], cwd=cwd)
    model_ids = [
        line.split("\t", 1)[0]
        for line in models.stdout.decode("utf-8").splitlines()
        if line.strip()
    ]
    required = {f"gemini-3.7-flash-{effort}" for effort in EFFORTS}
    if not required.issubset(model_ids):
        raise AgyPilotError("agy_required_models_unavailable")
    plugins = _run_read_only([str(agy), "plugin", "list"], cwd=cwd)
    if plugins.stdout != b"No imported plugins.\n":
        raise AgyPilotError("agy_plugin_surface_not_empty")
    config_envelope = _slash_envelope(agy, "/config", cwd)
    skills_envelope = _slash_envelope(agy, "/skills", cwd)
    config = config_envelope.get("command", {}).get("data", {}).get("config")
    skills = skills_envelope.get("command", {}).get("data", {}).get("skills")
    if not isinstance(config, dict) or not isinstance(skills, list):
        raise AgyPilotError("agy_customization_surface_invalid")
    config_surface = {
        key: copy.deepcopy(config.get(key)) for key in _CONFIG_SURFACE_KEYS
    }
    skill_surface: list[dict[str, Any]] = []
    for skill in skills:
        if not isinstance(skill, dict) or not all(
            key in skill
            for key in ("name", "description", "builtin", "model_invocable")
        ):
            raise AgyPilotError("agy_skill_surface_invalid")
        skill_surface.append(
            {
                key: copy.deepcopy(skill[key])
                for key in ("name", "description", "builtin", "model_invocable")
            }
        )
    skill_surface.sort(key=lambda item: item["name"])
    return {
        "agy_version_stdout_sha256": sha256_hex(version.stdout),
        "model_catalog_sha256": sha256_hex(models.stdout),
        "model_ids": model_ids,
        "plugin_list_sha256": sha256_hex(plugins.stdout),
        "config_surface": config_surface,
        "config_surface_sha256": sha256_hex(canonical_json(config_surface)),
        "skill_surface": skill_surface,
        "skill_surface_sha256": sha256_hex(canonical_json(skill_surface)),
    }


def _workspace(raw: Path, *, create: bool) -> Path:
    path = Path(os.path.abspath(raw))
    if path == Path("/"):
        raise AgyPilotError("workspace_root_refused")
    _real_directory(path.parent, "workspace_parent")
    if create:
        if path.exists() or path.is_symlink():
            raise AgyPilotError("workspace_exists")
        path.mkdir(mode=0o750)
    else:
        _real_directory(path, "workspace")
    return path


def prepare_workspace(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace, create=True)
    agy = _resolve_agy()
    base_policy, policy = load_pilot_native_policy()
    subjects = {effort: native_subject(effort) for effort in EFFORTS}
    validate_native_agent_systems(policy, subjects)
    snapshot = _preflight_snapshot(agy, workspace)
    plan_identity = {
        "schema_version": "caplab-revbench-agy-pilot-plan/1",
        "decision_authority": "adr-0064",
        "purpose": "engineering shakedown of paired Revbench review behavior",
        "population": "two repository-owned synthetic integer-minimum cases",
        "created_at": _timestamp(),
        "base_native_policy_sha256": sha256_hex(canonical_json(base_policy)),
        "pilot_native_policy_sha256": sha256_hex(canonical_json(policy)),
        "pilot_contract_file_sha256": sha256_hex(PILOT_NATIVE_POLICY.read_bytes()),
        "pilot_runner_sha256": sha256_hex(Path(__file__).read_bytes()),
        "agy_executable": {
            "path": str(agy),
            "sha256": EXPECTED_AGY_SHA256,
            "byte_count": agy.stat().st_size,
            "format": "dynamic-elf-host-runtime",
            "version": EXPECTED_AGY_VERSION,
        },
        "preflight": snapshot,
        "subjects": subjects,
        "cases": list(CASES),
        "call_budget": {
            "model_calls": len(EFFORTS) * len(CASES) * 2,
            "attempts_per_binding": len(CASES) * 2,
            "retries": 0,
            "execution": "sequential",
        },
        "runtime_limits": {
            "process_timeout_seconds": PROCESS_TIMEOUT_SECONDS,
            "max_stdout_bytes": MAX_STREAM_BYTES,
            "max_stderr_bytes": MAX_STREAM_BYTES,
            "working_directory": "empty-per-attempt",
            "environment": _pilot_environment(),
            "provider_route": "AGY signed-in configured route",
            "route_resolution": "configured-route",
        },
        "known_limits": [
            "AGY authentication and conversation persistence remain in its global owner account",
            "AGY is dynamically linked and uses the observed host runtime",
            "AGY telemetry is enabled in the observed global configuration",
            "AGY built-in skills remain present even though the task does not invoke them",
            "provider request identity and server-side retry behavior are unavailable",
            "the synthetic two-case population is an adapter shakedown, not broad coding capability",
        ],
        "non_claims": [
            "qualification",
            "acceptance",
            "deployment selection",
            "general model ranking",
            "performance or cost superiority",
        ],
        "excluded_preflight_residue": {
            "conversation_id": "226088f2-aa57-47ee-bf62-360b4e57d3e9",
            "token_count": 15999,
            "reason": "slash expansion was disabled, so /model became a literal prompt",
            "study_denominator": "excluded",
        },
    }
    plan = {
        "plan_id": "agy-pilot-plan-" + sha256_hex(canonical_json(plan_identity)),
        **plan_identity,
    }
    _write_document(workspace / "pilot-plan.json", plan)
    print(f"prepared: {workspace}")
    print("model_calls: 0")
    print("next: authorize")
    return 0


def authorize_workspace(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace, create=False)
    plan = _read_document(workspace / "pilot-plan.json", "pilot_plan")
    _validate_plan(plan)
    now = datetime.now(UTC).replace(microsecond=0)
    valid_until = now + timedelta(seconds=args.valid_for_seconds)
    identity = {
        "schema_version": "caplab-revbench-agy-pilot-authorization/1",
        "effect": "twelve-native-agy-model-calls-and-offline-scoring",
        "authorized_by": args.authorized_by,
        "source": args.source,
        "plan_id": plan["plan_id"],
        "plan_sha256": sha256_hex(canonical_json(plan)),
        "model_call_limit": plan["call_budget"]["model_calls"],
        "valid_from": _timestamp(now),
        "valid_until": _timestamp(valid_until),
        "qualification_authority": "not delegated",
        "acceptance_authority": "not delegated",
    }
    authorization = {
        "authorization_id": "agy-pilot-auth-" + sha256_hex(canonical_json(identity)),
        **identity,
    }
    _write_document(workspace / "authorization.json", authorization)
    print(f"authorized: {authorization['authorization_id']}")
    print("model_calls: 0")
    print("next: execute")
    return 0


def _validate_authority(
    plan: Mapping[str, Any],
    authorization: Mapping[str, Any],
    *,
    require_current: bool = True,
) -> None:
    identity = copy.deepcopy(dict(authorization))
    authorization_id = identity.pop("authorization_id", None)
    if authorization_id != "agy-pilot-auth-" + sha256_hex(canonical_json(identity)):
        raise AgyPilotError("authorization_id_invalid")
    if (
        authorization.get("schema_version")
        != "caplab-revbench-agy-pilot-authorization/1"
        or authorization.get("effect")
        != "twelve-native-agy-model-calls-and-offline-scoring"
        or authorization.get("qualification_authority") != "not delegated"
        or authorization.get("acceptance_authority") != "not delegated"
    ):
        raise AgyPilotError("authorization_schema_invalid")
    if authorization.get("plan_id") != plan.get("plan_id") or authorization.get(
        "plan_sha256"
    ) != sha256_hex(canonical_json(plan)):
        raise AgyPilotError("authorization_plan_mismatch")
    if authorization.get("model_call_limit") != 12:
        raise AgyPilotError("authorization_call_budget_mismatch")
    now = _timestamp()
    valid_from = authorization.get("valid_from")
    valid_until = authorization.get("valid_until")
    if not isinstance(valid_from, str) or not isinstance(valid_until, str):
        raise AgyPilotError("authorization_time_invalid")
    if (
        _UTC_TIMESTAMP.fullmatch(valid_from) is None
        or _UTC_TIMESTAMP.fullmatch(valid_until) is None
        or valid_from > valid_until
    ):
        raise AgyPilotError("authorization_time_invalid")
    if require_current and not valid_from <= now <= valid_until:
        raise AgyPilotError("authorization_not_current")


def _validate_plan(plan: Mapping[str, Any]) -> None:
    identity = copy.deepcopy(dict(plan))
    plan_id = identity.pop("plan_id", None)
    if plan_id != "agy-pilot-plan-" + sha256_hex(canonical_json(identity)):
        raise AgyPilotError("pilot_plan_id_invalid")
    if (
        plan.get("schema_version") != "caplab-revbench-agy-pilot-plan/1"
        or plan.get("decision_authority") != "adr-0064"
        or plan.get("call_budget")
        != {
            "model_calls": 12,
            "attempts_per_binding": 4,
            "retries": 0,
            "execution": "sequential",
        }
        or plan.get("cases") != list(CASES)
        or plan.get("subjects")
        != {effort: native_subject(effort) for effort in EFFORTS}
    ):
        raise AgyPilotError("pilot_plan_contract_invalid")
    base_policy, pilot_policy = load_pilot_native_policy()
    if plan.get("base_native_policy_sha256") != sha256_hex(
        canonical_json(base_policy)
    ) or plan.get("pilot_native_policy_sha256") != sha256_hex(
        canonical_json(pilot_policy)
    ):
        raise AgyPilotError("pilot_plan_native_policy_drift")
    if plan.get("pilot_contract_file_sha256") != sha256_hex(
        PILOT_NATIVE_POLICY.read_bytes()
    ):
        raise AgyPilotError("pilot_plan_contract_file_drift")
    if plan.get("pilot_runner_sha256") != sha256_hex(Path(__file__).read_bytes()):
        raise AgyPilotError("pilot_plan_runner_drift")


def _verify_runtime(plan: Mapping[str, Any], agy: Path, cwd: Path) -> None:
    if sha256_hex(agy.read_bytes()) != plan["agy_executable"]["sha256"]:
        raise AgyPilotError("agy_executable_drift")
    if _preflight_snapshot(agy, cwd) != plan["preflight"]:
        raise AgyPilotError("agy_runtime_surface_drift")


def _native_input(case: Mapping[str, Any], arm: str) -> dict[str, Any]:
    return {
        "schema_version": "caplab-revbench-native-input/1",
        "instruction": (
            "Review the artifact against the requirement and return exactly one "
            "JSON object. Do not use tools, inspect files, or modify state."
        ),
        "requirement": copy.deepcopy(case["oracle"]),
        "artifact": copy.deepcopy(case[arm]),
        "response_schema_version": "caplab-revbench-native-response/1",
    }


def _attempt_projection(
    *,
    effort: str,
    case: Mapping[str, Any],
    arm: str,
    assignment_index: int,
    disposition: str,
    verdict: str,
    anchors: list[str],
    conversation_id: str | None,
    usage: Mapping[str, int],
    duration_milliseconds: int | None,
) -> dict[str, Any]:
    return {
        "effort": effort,
        "tuple_id": f"agy-gemini-3-7-flash-{effort}",
        "case_id": case["case_id"],
        "arm": arm,
        "assignment_index": assignment_index,
        "disposition": disposition,
        "verdict": verdict,
        "anchors": anchors,
        "conversation_id": conversation_id,
        "usage": dict(usage),
        "duration_milliseconds": duration_milliseconds,
    }


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def _run_bounded_process(
    argv: Sequence[str], *, cwd: Path
) -> tuple[bytes, bool, bytes, bool, int | None, str]:
    """Capture bounded stream prefixes and reap the complete process group."""

    try:
        process = subprocess.Popen(
            list(argv),
            cwd=cwd,
            env=_pilot_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            start_new_session=True,
        )
    except OSError:
        return b"", True, b"", True, None, "spawn-failure"
    assert process.stdout is not None and process.stderr is not None
    selector = selectors.DefaultSelector()
    streams = {
        process.stdout.fileno(): (process.stdout, "stdout"),
        process.stderr.fileno(): (process.stderr, "stderr"),
    }
    for stream, name in streams.values():
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ, name)
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    complete = {"stdout": True, "stderr": True}
    termination = "exited"
    deadline = time.monotonic() + PROCESS_TIMEOUT_SECONDS
    killed = False
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0 and not killed:
                termination = "timeout"
                killed = True
                _terminate_process_group(process)
            events = selector.select(
                max(0.0, min(remaining, 0.1)) if not killed else 0.1
            )
            for key, _ in events:
                name = key.data
                try:
                    chunk = os.read(key.fd, 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                available = MAX_STREAM_BYTES - len(buffers[name])
                buffers[name].extend(chunk[: max(available, 0)])
                if len(chunk) > max(available, 0) and complete[name]:
                    complete[name] = False
                    if not killed:
                        termination = f"{name}-limit"
                        killed = True
                        _terminate_process_group(process)
        if process.poll() is None:
            process.wait()
    finally:
        selector.close()
        if process.poll() is None:
            _terminate_process_group(process)
    return (
        bytes(buffers["stdout"]),
        complete["stdout"],
        bytes(buffers["stderr"]),
        complete["stderr"],
        process.returncode,
        termination,
    )


def _retained_attempt(
    *,
    attempt_directory: Path,
    plan: Mapping[str, Any],
    authorization: Mapping[str, Any],
    effort: str,
    case: Mapping[str, Any],
    arm: str,
    assignment_index: int,
) -> dict[str, Any]:
    _real_directory(attempt_directory, "attempt_directory")
    completion_path = attempt_directory / "completion.json"
    if not completion_path.exists():
        raise AgyPilotError("attempt_uncertain_no_relaunch")
    intent = _read_document(attempt_directory / "intent.json", "attempt_intent")
    completion = _read_document(completion_path, "attempt_completion")
    expected_intent = {
        "authorization_id": authorization["authorization_id"],
        "plan_id": plan["plan_id"],
        "effort": effort,
        "tuple_id": f"agy-gemini-3-7-flash-{effort}",
        "case_id": case["case_id"],
        "arm": arm,
        "assignment_index": assignment_index,
    }
    if any(intent.get(field) != value for field, value in expected_intent.items()):
        raise AgyPilotError("retained_attempt_identity_mismatch")
    intent_identity = copy.deepcopy(intent)
    attempt_id = intent_identity.pop("attempt_id", None)
    if attempt_id != "agy-attempt-" + sha256_hex(canonical_json(intent_identity)):
        raise AgyPilotError("retained_attempt_id_invalid")
    completion_identity = copy.deepcopy(completion)
    completion_id = completion_identity.pop("completion_id", None)
    if (
        completion_id
        != "agy-completion-" + sha256_hex(canonical_json(completion_identity))
        or completion.get("attempt_id") != attempt_id
    ):
        raise AgyPilotError("retained_completion_id_invalid")
    for stream in ("stdout", "stderr"):
        payload = _read_bytes(attempt_directory / f"{stream}.bin", stream)
        if completion.get(f"{stream}_sha256") != sha256_hex(payload) or completion.get(
            f"{stream}_byte_count"
        ) != len(payload):
            raise AgyPilotError("retained_stream_identity_mismatch")
    attempt = completion.get("attempt")
    if not isinstance(attempt, dict) or any(
        attempt.get(field) != value
        for field, value in expected_intent.items()
        if field not in {"authorization_id", "plan_id"}
    ):
        raise AgyPilotError("retained_attempt_projection_mismatch")
    return copy.deepcopy(attempt)


def _run_attempt(
    *,
    workspace: Path,
    agy: Path,
    plan: Mapping[str, Any],
    authorization: Mapping[str, Any],
    effort: str,
    case: Mapping[str, Any],
    arm: str,
    assignment_index: int,
) -> dict[str, Any]:
    attempts_directory = _ensure_child_directory(workspace, "attempts")
    effort_directory = _ensure_child_directory(attempts_directory, effort)
    attempt_directory = effort_directory / (
        f"{case['case_id']}-{assignment_index}-{arm}"
    )
    if attempt_directory.exists() or attempt_directory.is_symlink():
        return _retained_attempt(
            attempt_directory=attempt_directory,
            plan=plan,
            authorization=authorization,
            effort=effort,
            case=case,
            arm=arm,
            assignment_index=assignment_index,
        )
    subject = native_subject(effort)
    native_input = _native_input(case, arm)
    prompt = canonical_json(native_input).decode("utf-8")
    identity = {
        "schema_version": "caplab-revbench-agy-attempt-intent/1",
        "authorization_id": authorization["authorization_id"],
        "plan_id": plan["plan_id"],
        "effort": effort,
        "tuple_id": subject["tuple_id"],
        "case_id": case["case_id"],
        "arm": arm,
        "assignment_index": assignment_index,
        "logical_command": subject["command"],
        "prompt_sha256": sha256_hex(prompt.encode()),
        "claimed_at": _timestamp(),
    }
    intent = {
        "attempt_id": "agy-attempt-" + sha256_hex(canonical_json(identity)),
        **identity,
    }
    record_attempt_intent(attempt_directory, intent)
    runtime_directory = attempt_directory / "runtime"
    runtime_directory.mkdir(mode=0o750)
    argv = [str(agy), *subject["command"][1:], prompt]
    started_at = _timestamp()
    started_monotonic = time.monotonic()
    stdout, stdout_complete, stderr, stderr_complete, exit_code, termination = (
        _run_bounded_process(argv, cwd=runtime_directory)
    )
    completed_at = _timestamp()
    wall_milliseconds = round((time.monotonic() - started_monotonic) * 1000)
    _write_exclusive(attempt_directory / "stdout.bin", stdout)
    _write_exclusive(attempt_directory / "stderr.bin", stderr)
    disposition = "infrastructure-failure"
    verdict = "invalid"
    anchors: list[str] = []
    conversation_id = None
    usage: dict[str, int] = {}
    duration_milliseconds = None
    if termination == "exited" and exit_code != 0:
        termination = "exited-nonzero"
    if termination == "exited" and exit_code == 0:
        try:
            envelope = _derive_agy_envelope(stdout)
        except AgyTransportError:
            pass
        else:
            conversation_id = envelope.conversation_id
            usage = envelope.usage
            duration_milliseconds = (
                None
                if envelope.duration_seconds is None
                else round(envelope.duration_seconds * 1000)
            )
            try:
                response = _validated_response(envelope.raw_response)
            except AgyResponseError:
                disposition = "subject-failure"
            else:
                disposition = "complete"
                verdict = response["verdict"]
                anchors = response["anchors"]
    attempt = _attempt_projection(
        effort=effort,
        case=case,
        arm=arm,
        assignment_index=assignment_index,
        disposition=disposition,
        verdict=verdict,
        anchors=anchors,
        conversation_id=conversation_id,
        usage=usage,
        duration_milliseconds=duration_milliseconds,
    )
    completion_identity = {
        "schema_version": "caplab-revbench-agy-attempt-completion/1",
        "attempt_id": intent["attempt_id"],
        "started_at": started_at,
        "completed_at": completed_at,
        "wall_milliseconds": wall_milliseconds,
        "exit_code": exit_code,
        "termination": termination,
        "stdout_sha256": sha256_hex(stdout),
        "stdout_byte_count": len(stdout),
        "stdout_complete": stdout_complete,
        "stderr_sha256": sha256_hex(stderr),
        "stderr_byte_count": len(stderr),
        "stderr_complete": stderr_complete,
        "runtime_directory_entries": sorted(
            path.relative_to(runtime_directory).as_posix()
            for path in runtime_directory.rglob("*")
        ),
        "attempt": attempt,
    }
    completion = {
        "completion_id": "agy-completion-"
        + sha256_hex(canonical_json(completion_identity)),
        **completion_identity,
    }
    _write_document(attempt_directory / "completion.json", completion)
    return attempt


def execute_workspace(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace, create=False)
    if (workspace / "execution.json").exists():
        raise AgyPilotError("execution_already_sealed")
    plan = _read_document(workspace / "pilot-plan.json", "pilot_plan")
    authorization = _read_document(workspace / "authorization.json", "authorization")
    _validate_plan(plan)
    _validate_authority(plan, authorization)
    agy = _resolve_agy()
    attempts: list[dict[str, Any]] = []
    stop_reason = None
    started_at = _timestamp()
    for effort in EFFORTS:
        _verify_runtime(plan, agy, workspace)
        for case in CASES:
            for assignment_index, arm in enumerate(case["assignment_order"]):
                if _timestamp() > authorization["valid_until"]:
                    stop_reason = "authorization-expired"
                    break
                attempt = _run_attempt(
                    workspace=workspace,
                    agy=agy,
                    plan=plan,
                    authorization=authorization,
                    effort=effort,
                    case=case,
                    arm=arm,
                    assignment_index=assignment_index,
                )
                attempts.append(attempt)
                print(
                    f"attempt: {effort} {case['case_id']} {arm} "
                    f"{attempt['disposition']}"
                )
                if attempt["disposition"] == "infrastructure-failure":
                    stop_reason = "infrastructure-failure"
                    break
            if stop_reason is not None:
                break
        if stop_reason is not None:
            break
    execution_identity = {
        "schema_version": "caplab-revbench-agy-pilot-execution/1",
        "plan_id": plan["plan_id"],
        "authorization_id": authorization["authorization_id"],
        "started_at": started_at,
        "observed_at": _timestamp(),
        "status": "complete" if len(attempts) == 12 else "stopped",
        "stop_reason": stop_reason,
        "attempts": attempts,
    }
    execution = {
        "execution_id": "agy-pilot-execution-"
        + sha256_hex(canonical_json(execution_identity)),
        **execution_identity,
    }
    _write_document(workspace / "execution.json", execution)
    print(f"execution: {execution['execution_id']}")
    print(f"recorded_attempts: {len(attempts)}")
    print("next: score")
    return 0 if execution["status"] == "complete" else 2


def score_workspace(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace, create=False)
    plan = _read_document(workspace / "pilot-plan.json", "pilot_plan")
    authorization = _read_document(workspace / "authorization.json", "authorization")
    execution = _read_document(workspace / "execution.json", "execution")
    _validate_plan(plan)
    _validate_authority(plan, authorization, require_current=False)
    if execution.get("plan_id") != plan.get("plan_id"):
        raise AgyPilotError("execution_plan_mismatch")
    if execution.get("authorization_id") != authorization.get("authorization_id"):
        raise AgyPilotError("execution_authorization_mismatch")
    execution_identity = copy.deepcopy(execution)
    execution_id = execution_identity.pop("execution_id", None)
    if execution_id != "agy-pilot-execution-" + sha256_hex(
        canonical_json(execution_identity)
    ):
        raise AgyPilotError("execution_id_invalid")
    assignments = [
        (effort, case, assignment_index, arm)
        for effort in EFFORTS
        for case in CASES
        for assignment_index, arm in enumerate(case["assignment_order"])
    ]
    attempts = execution.get("attempts")
    if not isinstance(attempts, list) or len(attempts) > len(assignments):
        raise AgyPilotError("execution_attempts_invalid")
    retained_attempts = []
    for effort, case, assignment_index, arm in assignments[: len(attempts)]:
        retained_attempts.append(
            _retained_attempt(
                attempt_directory=(
                    workspace
                    / "attempts"
                    / effort
                    / f"{case['case_id']}-{assignment_index}-{arm}"
                ),
                plan=plan,
                authorization=authorization,
                effort=effort,
                case=case,
                arm=arm,
                assignment_index=assignment_index,
            )
        )
    if retained_attempts != attempts:
        raise AgyPilotError("execution_attempt_projection_mismatch")
    scores = score_attempts(retained_attempts)
    identity = {
        "schema_version": "caplab-revbench-agy-pilot-observation/1",
        "observed_at": execution["observed_at"],
        "plan_id": plan["plan_id"],
        "execution_id": execution["execution_id"],
        "population": plan["population"],
        "bindings": scores,
        "interpretation_boundary": (
            "descriptive engineering pilot only; not a CAPLAB Measurement, "
            "qualification Claim, acceptance, or general capability ranking"
        ),
    }
    observation = {
        "observation_id": "agy-pilot-observation-"
        + sha256_hex(canonical_json(identity)),
        **identity,
    }
    _write_document(workspace / "observation.json", observation)
    for effort in EFFORTS:
        metrics = scores[effort]["metrics"]
        print(
            f"{effort}: disposition={scores[effort]['disposition']} "
            f"attempted={scores[effort]['sample_flow']['attempted']} "
            f"usable={scores[effort]['sample_flow']['usable']} "
            f"metrics={json.dumps(metrics, sort_keys=True, separators=(',', ':'))}"
        )
    print("qualification: not performed")
    print("acceptance: not performed")
    return 0


def inspect_workspace(args: argparse.Namespace) -> int:
    workspace = _workspace(args.workspace, create=False)
    plan = _read_document(workspace / "pilot-plan.json", "pilot_plan")
    print(f"workspace: {workspace}")
    print(f"plan: {plan['plan_id']}")
    for name in ("authorization.json", "execution.json", "observation.json"):
        path = workspace / name
        print(f"{name}: {'present' if path.exists() else 'absent'}")
    observation_path = workspace / "observation.json"
    if observation_path.exists():
        observation = _read_document(observation_path, "observation")
        for effort in EFFORTS:
            binding = observation["bindings"][effort]
            print(
                f"{effort}: {binding['disposition']} "
                f"{json.dumps(binding['metrics'], sort_keys=True, separators=(',', ':'))}"
            )
    print("qualification: not performed")
    print("acceptance: not performed")
    return 0


def _bounded_seconds(value: str) -> int:
    try:
        seconds = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if not 300 <= seconds <= 3600:
        raise argparse.ArgumentTypeError("must be between 300 and 3600")
    return seconds


def _nonempty(value: str) -> str:
    if not value or value != value.strip():
        raise argparse.ArgumentTypeError("must be nonempty without outer whitespace")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the bounded native-AGY Gemini 3.7 Flash Revbench pilot."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("workspace", type=Path)
    prepare_parser.set_defaults(operation=prepare_workspace)
    authorize_parser = subparsers.add_parser("authorize")
    authorize_parser.add_argument("workspace", type=Path)
    authorize_parser.add_argument("--authorized-by", required=True, type=_nonempty)
    authorize_parser.add_argument("--source", required=True, type=_nonempty)
    authorize_parser.add_argument(
        "--valid-for-seconds", required=True, type=_bounded_seconds
    )
    authorize_parser.set_defaults(operation=authorize_workspace)
    execute_parser = subparsers.add_parser("execute")
    execute_parser.add_argument("workspace", type=Path)
    execute_parser.set_defaults(operation=execute_workspace)
    score_parser = subparsers.add_parser("score")
    score_parser.add_argument("workspace", type=Path)
    score_parser.set_defaults(operation=score_workspace)
    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("workspace", type=Path)
    inspect_parser.set_defaults(operation=inspect_workspace)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.operation(args)
    except (
        AgyPilotError,
        NativeAgentSystemContractError,
        OSError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
