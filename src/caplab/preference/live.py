"""Fail-closed live boundary for the authorized preference campaign."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tomllib
import urllib.request
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from caplab.subject_identity import (
    NativeAgentSystemContractError,
    validate_active_native_manifest,
)

from .instrument import load_instrument
from .instrument import render_task


class LivePreferenceContractError(ValueError):
    """The live manifest, attempt ledger, custody, or reveal contract failed."""


_SCHEMA = "caplab.preference.live-manifest/v1"
_STATUSES = {
    "completed",
    "partial",
    "refused",
    "invalid",
    "provider_failure",
    "harness_failure",
    "capture_failure",
    "task_image_failure",
}
_INFRASTRUCTURE = {
    "provider_failure",
    "harness_failure",
    "capture_failure",
    "task_image_failure",
}
_BLIND_VALUES = {"A", "B", "tie", "unjudgeable"}
_IDENTITY_MARKERS = {
    "fable",
    "gpt",
    "openrouter",
    "anthropic",
    "openai",
    "claude",
    "terminus",
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


def _read_json_object(path: Path) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink():
        raise LivePreferenceContractError(f"json_symlink:{path}")
    try:
        content = path.read_bytes()
        value = json.loads(content.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LivePreferenceContractError(f"json_unreadable:{path}:{error}") from error
    if not isinstance(value, dict):
        raise LivePreferenceContractError(f"json_not_object:{path}")
    return value, content


def _project_root(manifest_path: Path) -> Path:
    for candidate in (manifest_path, *manifest_path.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "src" / "caplab").is_dir():
            return candidate
    raise LivePreferenceContractError("project_root_not_found")


def _assert_active_native_manifest(
    manifest: Mapping[str, Any], project_root: Path
) -> None:
    try:
        validate_active_native_manifest(
            project_root / "docs" / "product" / "contracts" / "native-agent-systems.json",
            manifest,
        )
    except NativeAgentSystemContractError as error:
        raise LivePreferenceContractError(str(error)) from error


def load_live_manifest(
    manifest_path: str | os.PathLike[str],
    instrument_path: str | os.PathLike[str],
) -> dict[str, Any]:
    """Load the exact committed live manifest and its model-free instrument."""

    manifest_file = Path(manifest_path)
    instrument_file = Path(instrument_path)
    manifest, _ = _read_json_object(manifest_file)
    if manifest.get("schema") != _SCHEMA or manifest.get("authority") != "adr-0037":
        raise LivePreferenceContractError("invalid_live_manifest_schema_or_authority")
    project_root = _project_root(manifest_file.resolve())
    _assert_active_native_manifest(manifest, project_root)
    expires_at = manifest.get("expires_at")
    if not isinstance(expires_at, str):
        raise LivePreferenceContractError("invalid_live_expiry")
    try:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise LivePreferenceContractError("invalid_live_expiry") from error
    if expiry.tzinfo is None:
        raise LivePreferenceContractError("invalid_live_expiry")
    if datetime.now(UTC) > expiry:
        raise LivePreferenceContractError("live_authorization_expired")
    sealed = dict(manifest)
    manifest_sha256 = sealed.pop("manifest_sha256", None)
    if manifest_sha256 != _digest(sealed):
        raise LivePreferenceContractError("live_manifest_digest_mismatch")
    instrument, instrument_bytes = _read_json_object(instrument_file)
    binding = manifest.get("instrument")
    if not isinstance(binding, dict):
        raise LivePreferenceContractError("invalid_instrument_binding")
    if sha256(instrument_bytes).hexdigest() != binding.get("file_sha256"):
        raise LivePreferenceContractError("instrument_file_digest_mismatch")
    validated_instrument = load_instrument(instrument_file)
    if validated_instrument["design_sha256"] != binding.get("design_sha256"):
        raise LivePreferenceContractError("instrument_design_digest_mismatch")
    if manifest.get("execution_order") != validated_instrument["execution_order"]:
        raise LivePreferenceContractError("execution_order_mismatch")
    if manifest.get("reveal_map") != validated_instrument["reveal_map"]:
        raise LivePreferenceContractError("reveal_map_mismatch")
    subjects = manifest.get("subjects")
    if not isinstance(subjects, dict) or set(subjects) != {"fable", "gpt"}:
        raise LivePreferenceContractError("invalid_live_subjects")
    for subject_id, instrument_subject in validated_instrument["subjects"].items():
        if subjects[subject_id].get("instrument_model_id") != instrument_subject["model_id"]:
            raise LivePreferenceContractError("subject_identity_mismatch")
    if manifest.get("surface") != validated_instrument["subjects"]["fable"]["surface"]:
        raise LivePreferenceContractError("subject_surface_mismatch")
    harness = manifest.get("harness")
    if not isinstance(harness, dict) or harness.get("harbor_version") != "0.18.0":
        raise LivePreferenceContractError("invalid_harbor_identity")
    if harness.get("agent") != "terminus-2" or harness.get("agent_version") != "2.0.0":
        raise LivePreferenceContractError("invalid_agent_identity")
    if (
        harness.get("max_turns") != 8
        or harness.get("max_tokens_per_turn") != 1024
        or harness.get("summarization") is not False
        or harness.get("reasoning_effort") != "default"
        or harness.get("parser") != "json"
    ):
        raise LivePreferenceContractError("invalid_agent_surface")
    limits = manifest.get("limits")
    if not isinstance(limits, dict) or limits != {
        "primary_trials": 12,
        "maximum_replacements": 4,
        "maximum_trials": 16,
        "maximum_completion_tokens_per_trial": 8192,
        "maximum_completion_tokens": 131072,
        "maximum_wall_clock_hours": 12,
        "maximum_usd": "50.00",
    }:
        raise LivePreferenceContractError("invalid_live_limits")
    template_path = project_root / harness["task_template"]
    if template_path.is_symlink() or not template_path.is_dir():
        raise LivePreferenceContractError("task_template_unavailable")
    try:
        template = tomllib.loads((template_path / "task.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise LivePreferenceContractError(f"task_template_unreadable:{error}") from error
    if template.get("environment", {}).get("network_mode") != "no-network":
        raise LivePreferenceContractError("task_network_not_disabled")
    if template.get("agent", {}).get("timeout_sec") != 2700.0:
        raise LivePreferenceContractError("task_timeout_mismatch")
    result = dict(manifest)
    result["_manifest_path"] = manifest_file.resolve()
    result["_instrument_path"] = instrument_file.resolve()
    result["_project_root"] = project_root
    result["_task_template_path"] = template_path.resolve()
    result["_instrument"] = validated_instrument
    return result


def preflight_runtime(manifest: Mapping[str, Any]) -> dict[str, str]:
    """Verify live provider and local harness identities without reading a secret."""

    _assert_active_native_manifest(manifest, Path(manifest["_project_root"]))
    harbor = shutil.which("harbor")
    docker = shutil.which("docker")
    if harbor is None:
        raise LivePreferenceContractError("harbor_unavailable")
    if docker is None:
        raise LivePreferenceContractError("docker_unavailable")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise LivePreferenceContractError("openrouter_credential_unavailable")
    harbor_version = subprocess.run(
        [harbor, "--version"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
        text=True,
    )
    if harbor_version.returncode != 0 or harbor_version.stdout.strip() != manifest["harness"]["harbor_version"]:
        raise LivePreferenceContractError("harbor_version_mismatch")
    shebang = Path(harbor).read_text(encoding="utf-8").splitlines()[0]
    if not shebang.startswith("#!"):
        raise LivePreferenceContractError("harbor_interpreter_unresolved")
    interpreter = shebang[2:]
    source_probe = subprocess.run(
        [
            interpreter,
            "-c",
            "import hashlib,inspect; from pathlib import Path; from harbor.agents.terminus_2 import Terminus2; print(hashlib.sha256(Path(inspect.getfile(Terminus2)).read_bytes()).hexdigest())",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
        text=True,
    )
    if source_probe.returncode != 0 or source_probe.stdout.strip() != manifest["harness"]["agent_source_sha256"]:
        raise LivePreferenceContractError("agent_source_mismatch")
    docker_probe = subprocess.run(
        [docker, "info", "--format", "{{.ServerVersion}}"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
        text=True,
    )
    if docker_probe.returncode != 0 or not docker_probe.stdout.strip():
        raise LivePreferenceContractError("docker_runtime_unavailable")
    try:
        with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as response:
            catalog = json.loads(response.read().decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LivePreferenceContractError(f"provider_catalog_unavailable:{error}") from error
    if not isinstance(catalog, dict) or not isinstance(catalog.get("data"), list):
        raise LivePreferenceContractError("provider_catalog_invalid")
    rows = {row.get("id"): row for row in catalog["data"] if isinstance(row, dict)}
    for subject in manifest["subjects"].values():
        provider_id = subject["provider_route"].removeprefix("openrouter/")
        row = rows.get(provider_id)
        if not isinstance(row, dict):
            raise LivePreferenceContractError(f"provider_subject_unavailable:{provider_id}")
        pricing = row.get("pricing")
        if not isinstance(pricing, dict) or pricing.get("prompt") != subject["prompt_usd_per_token"] or pricing.get("completion") != subject["completion_usd_per_token"]:
            raise LivePreferenceContractError(f"provider_price_drift:{provider_id}")
    return {
        "harbor_version": harbor_version.stdout.strip(),
        "agent_source_sha256": source_probe.stdout.strip(),
        "docker_server_version": docker_probe.stdout.strip(),
        "provider_catalog": "exact-subjects-and-prices-present",
        "credential": "present-not-read",
    }


def harbor_command(
    manifest: Mapping[str, Any],
    *,
    slot_index: int,
    task_path: Path,
    jobs_path: Path,
) -> list[str]:
    """Build the only authorized one-trial Harbor command."""

    order = manifest.get("execution_order")
    if not isinstance(slot_index, int) or isinstance(slot_index, bool) or not isinstance(order, list) or not 0 <= slot_index < len(order):
        raise LivePreferenceContractError("invalid_slot_index")
    task_id, subject_id = order[slot_index].split(":", 1)
    instrument = manifest.get("_instrument")
    if not isinstance(instrument, dict) or task_id not in instrument.get("tasks", {}):
        raise LivePreferenceContractError("live_instrument_not_loaded")
    instruction = instrument["subject_instruction"] + "\n\nTask: " + instrument["tasks"][task_id]["instruction"]
    harness = manifest["harness"]
    return [
        "harbor",
        "exec",
        "--path",
        str(task_path),
        "--no-scan",
        "--instruction",
        instruction,
        "--task-template",
        str(manifest["_task_template_path"]),
        "--artifact",
        "/app",
        "--disable-verification",
        "--env",
        "docker",
        "--agent",
        harness["agent"],
        "--model",
        manifest["subjects"][subject_id]["provider_route"],
        "--agent-kwarg",
        f"max_turns={harness['max_turns']}",
        "--agent-kwarg",
        f"parser_name={harness['parser']}",
        "--agent-kwarg",
        "enable_summarize=false",
        "--agent-kwarg",
        f'llm_kwargs={{"max_tokens":{harness["max_tokens_per_turn"]}}}',
        "--n-attempts",
        "1",
        "--n-concurrent",
        "1",
        "--max-retries",
        "0",
        "--job-name",
        f"caplab-preference-001-s{slot_index + 1:02d}",
        "--jobs-dir",
        str(jobs_path),
        "--quiet",
    ]


def _decimal(raw: object, field: str) -> Decimal:
    if not isinstance(raw, str):
        raise LivePreferenceContractError(f"invalid_decimal:{field}")
    try:
        value = Decimal(raw)
    except InvalidOperation as error:
        raise LivePreferenceContractError(f"invalid_decimal:{field}") from error
    if not value.is_finite() or value < 0:
        raise LivePreferenceContractError(f"invalid_decimal:{field}")
    return value


def assess_attempts(
    manifest: Mapping[str, Any],
    attempts: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Validate an ordered attempt ledger and return its next allowed action."""

    limits = manifest["limits"]
    if len(attempts) > limits["maximum_trials"]:
        raise LivePreferenceContractError("campaign_trial_limit")
    next_slot = 0
    pending_replacement: int | None = None
    replacement_count = 0
    total_tokens = 0
    total_cost = Decimal("0")
    for attempt in attempts:
        if not isinstance(attempt, Mapping):
            raise LivePreferenceContractError("invalid_attempt")
        slot_index = attempt.get("slot_index")
        kind = attempt.get("attempt_kind")
        status = attempt.get("status")
        tokens = attempt.get("completion_tokens")
        if not isinstance(slot_index, int) or isinstance(slot_index, bool):
            raise LivePreferenceContractError("invalid_attempt_slot")
        if status not in _STATUSES:
            raise LivePreferenceContractError("invalid_attempt_status")
        if not isinstance(tokens, int) or isinstance(tokens, bool) or tokens < 0:
            raise LivePreferenceContractError("invalid_completion_tokens")
        if tokens > limits["maximum_completion_tokens_per_trial"]:
            raise LivePreferenceContractError("trial_completion_token_limit")
        cost = _decimal(attempt.get("cost_usd"), "cost_usd")
        if kind == "primary":
            if pending_replacement is not None:
                raise LivePreferenceContractError("unresolved_infrastructure_failure")
            if slot_index != next_slot:
                raise LivePreferenceContractError("primary_order_mismatch")
            if status in _INFRASTRUCTURE:
                pending_replacement = slot_index
            else:
                next_slot += 1
        elif kind == "replacement":
            if pending_replacement != slot_index:
                raise LivePreferenceContractError("replacement_without_infrastructure_failure")
            replacement_count += 1
            if replacement_count > limits["maximum_replacements"]:
                raise LivePreferenceContractError("campaign_replacement_limit")
            if status in _INFRASTRUCTURE:
                raise LivePreferenceContractError("second_infrastructure_failure")
            pending_replacement = None
            next_slot += 1
        else:
            raise LivePreferenceContractError("invalid_attempt_kind")
        total_tokens += tokens
        total_cost += cost
        if total_tokens > limits["maximum_completion_tokens"]:
            raise LivePreferenceContractError("campaign_completion_token_limit")
        if total_cost >= _decimal(limits["maximum_usd"], "maximum_usd"):
            raise LivePreferenceContractError("campaign_cost_limit")
    return {
        "next_slot_index": next_slot,
        "pending_replacement_for": pending_replacement,
        "replacement_count": replacement_count,
        "attempt_count": len(attempts),
        "total_completion_tokens": total_tokens,
        "total_cost_usd": total_cost,
        "complete": next_slot == len(manifest["execution_order"]),
        "stop_reason": None,
    }


def custody_tree_manifest(root: str | os.PathLike[str]) -> dict[str, Any]:
    """Hash every regular file under one raw-custody tree."""

    custody_root = Path(root)
    if custody_root.is_symlink() or not custody_root.is_dir():
        raise LivePreferenceContractError("invalid_custody_root")
    files: list[dict[str, Any]] = []
    for path in sorted(custody_root.rglob("*")):
        if path.is_symlink():
            raise LivePreferenceContractError(f"custody_symlink:{path.relative_to(custody_root).as_posix()}")
        if path.is_file():
            content = path.read_bytes()
            files.append(
                {
                    "path": path.relative_to(custody_root).as_posix(),
                    "size": len(content),
                    "sha256": sha256(content).hexdigest(),
                }
            )
    result = {"schema": "caplab.preference.custody-tree/v1", "files": files}
    result["tree_sha256"] = _digest(result)
    return result


def _exclusive_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(_canonical(value) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def _exclusive_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def prepare_trial(
    manifest: Mapping[str, Any],
    *,
    slot_index: int,
    attempt_kind: str,
    prior_attempts: Sequence[Mapping[str, Any]],
) -> tuple[Path, list[str]]:
    """Create one fresh raw-custody attempt and its exact Harbor command."""

    _assert_active_native_manifest(manifest, Path(manifest["_project_root"]))
    state = assess_attempts(manifest, prior_attempts)
    if state["complete"]:
        raise LivePreferenceContractError("campaign_already_complete")
    if state["pending_replacement_for"] is None:
        if attempt_kind != "primary" or slot_index != state["next_slot_index"]:
            raise LivePreferenceContractError("next_action_mismatch")
    elif attempt_kind != "replacement" or slot_index != state["pending_replacement_for"]:
        raise LivePreferenceContractError("next_action_mismatch")
    attempt_number = len(prior_attempts) + 1
    root = Path(manifest["storage"]["raw_custody_root"])
    if root.is_symlink():
        raise LivePreferenceContractError("raw_custody_root_symlink")
    attempt_root = root / "attempts" / f"a{attempt_number:02d}-s{slot_index + 1:02d}-{attempt_kind}"
    if attempt_root.exists() or attempt_root.is_symlink():
        raise LivePreferenceContractError("attempt_custody_exists")
    task_id, subject_id = manifest["execution_order"][slot_index].split(":", 1)
    task_root = attempt_root / "input" / task_id
    render_task(manifest["_instrument"], task_id, task_root)
    command = harbor_command(
        manifest,
        slot_index=slot_index,
        task_path=task_root,
        jobs_path=attempt_root / "harbor",
    )
    launch = {
        "schema": "caplab.preference.live-launch/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "attempt_number": attempt_number,
        "slot_index": slot_index,
        "attempt_kind": attempt_kind,
        "task_id": task_id,
        "subject_id": subject_id,
        "provider_route": manifest["subjects"][subject_id]["provider_route"],
        "input_tree": custody_tree_manifest(attempt_root / "input"),
        "command": command,
        "launched_at": datetime.now(UTC).isoformat(),
    }
    launch["launch_sha256"] = _digest(launch)
    _exclusive_json(attempt_root / "launch.json", launch)
    return attempt_root, command


def execute_trial(
    manifest: Mapping[str, Any],
    *,
    slot_index: int,
    attempt_kind: str,
    prior_attempts: Sequence[Mapping[str, Any]],
) -> Path:
    """Execute exactly one prepared trial and preserve command output."""

    preflight_runtime(manifest)
    attempt_root, command = prepare_trial(
        manifest,
        slot_index=slot_index,
        attempt_kind=attempt_kind,
        prior_attempts=prior_attempts,
    )
    started = datetime.now(UTC)
    try:
        completed = subprocess.run(
            command,
            cwd=manifest["_project_root"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=manifest["surface"]["wall_clock_minutes"] * 60 + 900,
            check=False,
        )
        return_code: int | None = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        timed_out = False
    except subprocess.TimeoutExpired as error:
        return_code = None
        stdout = error.stdout or b""
        stderr = error.stderr or b""
        timed_out = True
    _exclusive_bytes(attempt_root / "harbor.stdout", stdout)
    _exclusive_bytes(attempt_root / "harbor.stderr", stderr)
    finished = datetime.now(UTC)
    completion = {
        "schema": "caplab.preference.live-completion/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_seconds": format((finished - started).total_seconds(), ".6f"),
        "return_code": return_code,
        "timed_out": timed_out,
        "stdout_sha256": sha256(stdout).hexdigest(),
        "stderr_sha256": sha256(stderr).hexdigest(),
    }
    completion["completion_sha256"] = _digest(completion)
    _exclusive_json(attempt_root / "completion.json", completion)
    return attempt_root


def _validate_sealed(document: dict[str, Any], digest_field: str, error: str) -> None:
    sealed = dict(document)
    claimed = sealed.pop(digest_field, None)
    if claimed != _digest(sealed):
        raise LivePreferenceContractError(error)


def load_custody_attempts(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Derive campaign accounting only from sealed raw-custody observations."""

    attempts_root = Path(manifest["storage"]["raw_custody_root"]) / "attempts"
    if not attempts_root.exists():
        return []
    if attempts_root.is_symlink() or not attempts_root.is_dir():
        raise LivePreferenceContractError("invalid_attempts_custody")
    attempt_directories = sorted(path for path in attempts_root.iterdir() if path.is_dir())
    if any(path.is_symlink() for path in attempt_directories):
        raise LivePreferenceContractError("attempt_custody_symlink")
    attempts: list[dict[str, Any]] = []
    for expected_number, attempt_root in enumerate(attempt_directories, start=1):
        launch, _ = _read_json_object(attempt_root / "launch.json")
        observation_path = attempt_root / "observation.json"
        if not observation_path.is_file():
            raise LivePreferenceContractError(f"unclassified_attempt:{attempt_root.name}")
        completion, _ = _read_json_object(attempt_root / "completion.json")
        observation, _ = _read_json_object(observation_path)
        _validate_sealed(launch, "launch_sha256", "launch_digest_mismatch")
        _validate_sealed(completion, "completion_sha256", "completion_digest_mismatch")
        _validate_sealed(observation, "observation_sha256", "observation_digest_mismatch")
        if launch.get("attempt_number") != expected_number or observation.get("attempt_number") != expected_number:
            raise LivePreferenceContractError("attempt_number_mismatch")
        if launch.get("manifest_sha256") != manifest["manifest_sha256"] or observation.get("manifest_sha256") != manifest["manifest_sha256"]:
            raise LivePreferenceContractError("attempt_manifest_mismatch")
        raw_result_path = observation.get("source_result_path")
        if not isinstance(raw_result_path, str):
            raise LivePreferenceContractError("attempt_result_path_invalid")
        relative_result = PurePosixPath(raw_result_path)
        if relative_result.is_absolute() or any(part in {"", ".", ".."} for part in relative_result.parts):
            raise LivePreferenceContractError("attempt_result_path_invalid")
        source_result = Path(manifest["storage"]["raw_custody_root"]).joinpath(*relative_result.parts)
        if source_result.is_symlink() or not source_result.is_file():
            raise LivePreferenceContractError("attempt_result_unavailable")
        if sha256(source_result.read_bytes()).hexdigest() != observation.get("source_result_sha256"):
            raise LivePreferenceContractError("attempt_result_digest_mismatch")
        attempts.append(
            {
                "slot_index": observation["slot_index"],
                "attempt_kind": observation["attempt_kind"],
                "status": observation["status"],
                "completion_tokens": observation["completion_tokens"],
                "cost_usd": observation["cost_usd"],
            }
        )
    assess_attempts(manifest, attempts)
    return attempts


def record_observation(
    manifest: Mapping[str, Any],
    *,
    attempt_root: str | os.PathLike[str],
    status: str,
) -> dict[str, Any]:
    """Bind one explicit outcome class to Harbor metrics and preserved artifacts."""

    supplied_root = Path(attempt_root)
    if supplied_root.is_symlink():
        raise LivePreferenceContractError("attempt_outside_custody")
    root = supplied_root.resolve()
    custody_root = Path(manifest["storage"]["raw_custody_root"]).resolve()
    if root.parent != custody_root / "attempts":
        raise LivePreferenceContractError("attempt_outside_custody")
    if status not in _STATUSES:
        raise LivePreferenceContractError("invalid_attempt_status")
    launch, _ = _read_json_object(root / "launch.json")
    completion, _ = _read_json_object(root / "completion.json")
    _validate_sealed(launch, "launch_sha256", "launch_digest_mismatch")
    _validate_sealed(completion, "completion_sha256", "completion_digest_mismatch")
    trial_results: list[tuple[Path, dict[str, Any]]] = []
    for result_path in sorted((root / "harbor").rglob("result.json")):
        value, _ = _read_json_object(result_path)
        if "agent_result" in value and "trial_name" in value:
            trial_results.append((result_path, value))
    if len(trial_results) != 1:
        raise LivePreferenceContractError("harbor_trial_result_ambiguous")
    result_path, result = trial_results[0]
    agent_result = result.get("agent_result")
    if not isinstance(agent_result, dict):
        raise LivePreferenceContractError("harbor_agent_result_missing")
    completion_tokens = agent_result.get("n_output_tokens")
    cost = agent_result.get("cost_usd")
    if not isinstance(completion_tokens, int) or isinstance(completion_tokens, bool) or completion_tokens < 0:
        raise LivePreferenceContractError("measured_completion_tokens_missing")
    exception_present = result.get("exception_info") is not None or completion.get("return_code") != 0 or completion.get("timed_out") is True
    if cost is None and exception_present and completion_tokens == 0:
        cost_decimal = Decimal("0")
    elif not isinstance(cost, (int, float, str)) or isinstance(cost, bool):
        raise LivePreferenceContractError("measured_cost_missing")
    else:
        cost_decimal = _decimal(str(cost), "cost_usd")
    if exception_present and status not in _INFRASTRUCTURE:
        raise LivePreferenceContractError("infrastructure_result_misclassified")
    if not exception_present and status in _INFRASTRUCTURE:
        raise LivePreferenceContractError("subject_result_misclassified")
    artifact_root = result_path.parent / "artifacts" / "app"
    if not artifact_root.is_dir():
        raise LivePreferenceContractError("harbor_artifact_missing")
    result_bytes = result_path.read_bytes()
    observation = {
        "schema": "caplab.preference.live-observation/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "attempt_number": launch["attempt_number"],
        "slot_index": launch["slot_index"],
        "attempt_kind": launch["attempt_kind"],
        "status": status,
        "completion_tokens": completion_tokens,
        "cost_usd": format(cost_decimal, "f"),
        "source_result_path": result_path.relative_to(custody_root).as_posix(),
        "source_result_sha256": sha256(result_bytes).hexdigest(),
        "artifact_tree": custody_tree_manifest(artifact_root),
        "recorded_at": datetime.now(UTC).isoformat(),
    }
    observation["observation_sha256"] = _digest(observation)
    _exclusive_json(root / "observation.json", observation)
    return observation


def main(argv: Sequence[str] | None = None) -> int:
    """Validate the manifest or execute one explicitly selected next trial."""

    parser = argparse.ArgumentParser(prog="python -m caplab.preference.live")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--instrument", required=True, type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    subparsers.add_parser("preflight")
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--slot-index", required=True, type=int)
    run_parser.add_argument("--attempt-kind", required=True, choices=("primary", "replacement"))
    observe_parser = subparsers.add_parser("observe")
    observe_parser.add_argument("--attempt-root", required=True, type=Path)
    observe_parser.add_argument("--status", required=True, choices=tuple(sorted(_STATUSES)))
    args = parser.parse_args(argv)
    manifest = load_live_manifest(args.manifest, args.instrument)
    if args.command == "validate":
        print(json.dumps({"campaign_id": manifest["campaign_id"], "manifest_sha256": manifest["manifest_sha256"]}, sort_keys=True))
        return 0
    if args.command == "preflight":
        print(json.dumps(preflight_runtime(manifest), sort_keys=True))
        return 0
    if args.command == "observe":
        print(json.dumps(record_observation(manifest, attempt_root=args.attempt_root, status=args.status), sort_keys=True))
        return 0
    attempts = load_custody_attempts(manifest)
    attempt_root = execute_trial(
        manifest,
        slot_index=args.slot_index,
        attempt_kind=args.attempt_kind,
        prior_attempts=attempts,
    )
    print(attempt_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def _assert_blind(value: object) -> None:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).casefold()
    for marker in _IDENTITY_MARKERS:
        if marker in encoded:
            raise LivePreferenceContractError(f"blind_identity_leak:{marker}")


def freeze_dispositions(
    manifest: Mapping[str, Any],
    packets: Mapping[str, Mapping[str, Any]],
    decisions: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Freeze six criterion-level delegated judgments without the reveal map."""

    expected = set(manifest["reveal_map"])
    if set(packets) != expected or set(decisions) != expected:
        raise LivePreferenceContractError("incomplete_dispositions")
    criteria = set(manifest["blind_criteria"])
    frozen_decisions: dict[str, Any] = {}
    packet_hashes: dict[str, str] = {}
    for task_id in sorted(expected):
        packet = packets[task_id]
        decision = decisions[task_id]
        _assert_blind(packet)
        _assert_blind(decision)
        if decision.get("preferred_alias") not in _BLIND_VALUES:
            raise LivePreferenceContractError("invalid_preferred_alias")
        criterion_values = decision.get("criteria")
        if not isinstance(criterion_values, Mapping) or set(criterion_values) != criteria:
            raise LivePreferenceContractError("invalid_disposition_criteria")
        if any(value not in _BLIND_VALUES for value in criterion_values.values()):
            raise LivePreferenceContractError("invalid_criterion_disposition")
        if not isinstance(decision.get("rationale"), str) or not decision["rationale"].strip():
            raise LivePreferenceContractError("missing_disposition_rationale")
        if decision.get("uncertainty") not in {"low", "medium", "high"}:
            raise LivePreferenceContractError("invalid_disposition_uncertainty")
        packet_hashes[task_id] = _digest(packet)
        frozen_decisions[task_id] = dict(decision)
    result = {
        "schema": "caplab.preference.blind-dispositions/v1",
        "campaign_id": manifest["campaign_id"],
        "authority": "repository-owner delegation through adr-0026 exercised by primary-agent",
        "manifest_sha256": manifest["manifest_sha256"],
        "packet_sha256": packet_hashes,
        "dispositions": frozen_decisions,
        "status": "frozen-before-reveal",
    }
    _assert_blind(result)
    result["freeze_sha256"] = _digest(result)
    return result


def reveal_dispositions(
    manifest: Mapping[str, Any],
    frozen: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the preregistered reveal map only after all dispositions freeze."""

    sealed = dict(frozen)
    freeze_sha256 = sealed.pop("freeze_sha256", None)
    if freeze_sha256 != _digest(sealed):
        raise LivePreferenceContractError("disposition_freeze_digest_mismatch")
    expected = set(manifest["reveal_map"])
    if frozen.get("status") != "frozen-before-reveal" or set(frozen.get("dispositions", {})) != expected:
        raise LivePreferenceContractError("incomplete_dispositions")
    pairs: dict[str, Any] = {}
    for task_id in sorted(expected):
        decision = frozen["dispositions"][task_id]
        preferred_alias = decision["preferred_alias"]
        preferred_subject = (
            manifest["reveal_map"][task_id][preferred_alias]
            if preferred_alias in {"A", "B"}
            else preferred_alias
        )
        pairs[task_id] = {
            "preferred_alias": preferred_alias,
            "preferred_subject": preferred_subject,
            "criteria": decision["criteria"],
            "rationale": decision["rationale"],
            "uncertainty": decision["uncertainty"],
        }
    result = {
        "schema": "caplab.preference.revealed-dispositions/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "freeze_sha256": freeze_sha256,
        "pairs": pairs,
    }
    result["reveal_sha256"] = _digest(result)
    return result
