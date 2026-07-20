"""Fail-closed live boundary for the authorized development calibration."""

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

from .instrument import load_calibration_instrument, render_review_cell


class LiveReviewContractError(ValueError):
    """The live manifest, attempt ledger, or custody contract failed."""


_SCHEMA = "caplab.review-dissent.live-manifest/v1"
_ORDER = [
    "r03:gpt", "r04:fable", "r07:fable", "r08:gpt",
    "r02:gpt", "r01:fable", "r06:fable", "r05:gpt",
    "r04:gpt", "r03:fable", "r08:fable", "r07:gpt",
    "r01:gpt", "r02:fable", "r05:fable", "r06:gpt",
]
_SUBJECT_STATUSES = {"completed", "refused", "invalid"}
_INFRASTRUCTURE = {
    "provider_failure", "harness_failure", "capture_failure",
    "task_image_failure", "verifier_failure",
}
_STATUSES = _SUBJECT_STATUSES | _INFRASTRUCTURE


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink():
        raise LiveReviewContractError(f"json_symlink:{path}")
    try:
        content = path.read_bytes()
        value = json.loads(content.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LiveReviewContractError(f"json_unreadable:{path}:{error}") from error
    if not isinstance(value, dict):
        raise LiveReviewContractError(f"json_not_object:{path}")
    return value, content


def _project_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "src" / "caplab").is_dir():
            return candidate
    raise LiveReviewContractError("project_root_not_found")


def _validate_sealed(document: dict[str, Any], field: str, error: str) -> None:
    sealed = dict(document)
    claimed = sealed.pop(field, None)
    if claimed != _digest(sealed):
        raise LiveReviewContractError(error)


def _decimal(raw: object, field: str) -> Decimal:
    if not isinstance(raw, str):
        raise LiveReviewContractError(f"invalid_decimal:{field}")
    try:
        value = Decimal(raw)
    except InvalidOperation as error:
        raise LiveReviewContractError(f"invalid_decimal:{field}") from error
    if not value.is_finite() or value < 0:
        raise LiveReviewContractError(f"invalid_decimal:{field}")
    return value


def load_live_manifest(manifest_path: str | os.PathLike[str], study_root: str | os.PathLike[str]) -> dict[str, Any]:
    """Load the exact live manifest without opening held-out content."""

    manifest_file = Path(manifest_path)
    root = Path(study_root)
    manifest, _ = _read_json(manifest_file)
    if manifest.get("schema") != _SCHEMA or manifest.get("authority") != "adr-0038":
        raise LiveReviewContractError("invalid_live_manifest_schema_or_authority")
    expires_at = manifest.get("expires_at")
    try:
        expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
    except ValueError as error:
        raise LiveReviewContractError("invalid_live_expiry") from error
    if expiry.tzinfo is None or datetime.now(UTC) > expiry:
        raise LiveReviewContractError("live_authorization_expired")
    _validate_sealed(manifest, "manifest_sha256", "live_manifest_digest_mismatch")
    instrument = load_calibration_instrument(root)
    binding = manifest.get("instrument")
    if not isinstance(binding, dict) or binding != {
        "design_sha256": instrument["design_sha256"],
        "development_sha256": instrument["artifacts"]["development"]["sha256"],
        "heldout_seal_sha256": instrument["heldout_seal"]["sha256"],
    }:
        raise LiveReviewContractError("instrument_binding_mismatch")
    if manifest.get("execution_order") != _ORDER:
        raise LiveReviewContractError("execution_order_mismatch")
    if any(item.split(":", 1)[0] not in instrument["cells"] for item in _ORDER):
        raise LiveReviewContractError("execution_cell_mismatch")
    subjects = manifest.get("subjects")
    expected_routes = {"fable": "openrouter/anthropic/claude-fable-5", "gpt": "openrouter/openai/gpt-5.6-terra"}
    if not isinstance(subjects, dict) or set(subjects) != set(expected_routes):
        raise LiveReviewContractError("invalid_live_subjects")
    if any(subjects[key].get("provider_route") != route for key, route in expected_routes.items()):
        raise LiveReviewContractError("subject_identity_mismatch")
    if manifest.get("surface") != {
        "memory": "fresh", "tools": "task-local", "external_network": False,
        "wall_clock_minutes": 45, "output_tokens": 8192,
    }:
        raise LiveReviewContractError("invalid_subject_surface")
    harness = manifest.get("harness")
    if not isinstance(harness, dict) or any((
        harness.get("harbor_version") != "0.18.0",
        harness.get("agent") != "terminus-2",
        harness.get("agent_version") != "2.0.0",
        harness.get("parser") != "json",
        harness.get("max_turns") != 8,
        harness.get("max_tokens_per_turn") != 1024,
        harness.get("reasoning_effort") != "default",
        harness.get("summarization") is not False,
    )):
        raise LiveReviewContractError("invalid_agent_surface")
    limits = manifest.get("limits")
    if limits != {
        "primary_trials": 16, "maximum_replacements": 4, "maximum_trials": 20,
        "maximum_completion_tokens_per_trial": 8192,
        "maximum_completion_tokens": 163840,
        "maximum_wall_clock_hours": 12, "maximum_usd": "25.00",
    }:
        raise LiveReviewContractError("invalid_live_limits")
    project_root = _project_root(manifest_file.resolve())
    template = project_root / harness["task_template"]
    if template.is_symlink() or not template.is_dir():
        raise LiveReviewContractError("task_template_unavailable")
    try:
        task_template = tomllib.loads((template / "task.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise LiveReviewContractError(f"task_template_unreadable:{error}") from error
    if task_template.get("environment", {}).get("network_mode") != "no-network":
        raise LiveReviewContractError("task_network_not_disabled")
    if task_template.get("agent", {}).get("timeout_sec") != 2700.0:
        raise LiveReviewContractError("task_timeout_mismatch")
    result = dict(manifest)
    result["_project_root"] = project_root
    result["_task_template_path"] = template.resolve()
    result["_instrument"] = instrument
    result["_study_root"] = root.resolve()
    return result


def preflight_runtime(manifest: Mapping[str, Any]) -> dict[str, str]:
    """Verify exact local and provider identities without printing a secret."""

    harbor = shutil.which("harbor")
    docker = shutil.which("docker")
    if harbor is None or docker is None:
        raise LiveReviewContractError("live_runtime_unavailable")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise LiveReviewContractError("openrouter_credential_unavailable")
    harbor_probe = subprocess.run([harbor, "--version"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False, text=True)
    if harbor_probe.returncode or harbor_probe.stdout.strip() != manifest["harness"]["harbor_version"]:
        raise LiveReviewContractError("harbor_version_mismatch")
    shebang = Path(harbor).read_text(encoding="utf-8").splitlines()[0]
    if not shebang.startswith("#!"):
        raise LiveReviewContractError("harbor_interpreter_unresolved")
    source_probe = subprocess.run([
        shebang[2:], "-c",
        "import hashlib,inspect; from pathlib import Path; from harbor.agents.terminus_2 import Terminus2; print(hashlib.sha256(Path(inspect.getfile(Terminus2)).read_bytes()).hexdigest())",
    ], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False, text=True)
    if source_probe.returncode or source_probe.stdout.strip() != manifest["harness"]["agent_source_sha256"]:
        raise LiveReviewContractError("agent_source_mismatch")
    docker_probe = subprocess.run([docker, "info", "--format", "{{.ServerVersion}}"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False, text=True)
    if docker_probe.returncode or not docker_probe.stdout.strip():
        raise LiveReviewContractError("docker_runtime_unavailable")
    try:
        with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as response:
            catalog = json.loads(response.read().decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LiveReviewContractError(f"provider_catalog_unavailable:{error}") from error
    if not isinstance(catalog, dict) or not isinstance(catalog.get("data"), list):
        raise LiveReviewContractError("provider_catalog_invalid")
    rows = {row.get("id"): row for row in catalog["data"] if isinstance(row, dict)}
    for subject in manifest["subjects"].values():
        provider_id = subject["provider_route"].removeprefix("openrouter/")
        row = rows.get(provider_id)
        pricing = row.get("pricing") if isinstance(row, dict) else None
        if not isinstance(pricing, dict):
            raise LiveReviewContractError(f"provider_subject_unavailable:{provider_id}")
        if pricing.get("prompt") != subject["prompt_usd_per_token"] or pricing.get("completion") != subject["completion_usd_per_token"]:
            raise LiveReviewContractError(f"provider_price_drift:{provider_id}")
    return {
        "harbor_version": harbor_probe.stdout.strip(),
        "agent_source_sha256": source_probe.stdout.strip(),
        "docker_server_version": docker_probe.stdout.strip(),
        "provider_catalog": "exact-subjects-and-prices-present",
        "credential": "present-not-read",
    }


def harbor_command(manifest: Mapping[str, Any], *, slot_index: int, task_path: Path, jobs_path: Path) -> list[str]:
    """Build the only authorized one-trial Harbor command."""

    if not isinstance(slot_index, int) or isinstance(slot_index, bool) or not 0 <= slot_index < len(_ORDER):
        raise LiveReviewContractError("invalid_slot_index")
    cell_id, subject_id = manifest["execution_order"][slot_index].split(":", 1)
    cell = manifest["_instrument"]["cells"].get(cell_id)
    if not isinstance(cell, dict) or cell.get("split") != "development":
        raise LiveReviewContractError("nondevelopment_cell")
    harness = manifest["harness"]
    return [
        "harbor", "exec", "--path", str(task_path), "--no-scan",
        "--instruction", manifest["_instrument"]["subject_instruction"],
        "--task-template", str(manifest["_task_template_path"]),
        "--artifact", "/app", "--disable-verification", "--env", "docker",
        "--agent", harness["agent"], "--model", manifest["subjects"][subject_id]["provider_route"],
        "--agent-kwarg", f"max_turns={harness['max_turns']}",
        "--agent-kwarg", f"parser_name={harness['parser']}",
        "--agent-kwarg", "enable_summarize=false",
        "--agent-kwarg", f'llm_kwargs={{"max_tokens":{harness["max_tokens_per_turn"]}}}',
        "--n-attempts", "1", "--n-concurrent", "1", "--max-retries", "0",
        "--job-name", f"caplab-review-dissent-001-s{slot_index + 1:02d}",
        "--jobs-dir", str(jobs_path), "--quiet",
    ]


def assess_attempts(manifest: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate ordered accounting and return the next permitted action."""

    limits = manifest["limits"]
    if len(attempts) > limits["maximum_trials"]:
        raise LiveReviewContractError("campaign_trial_limit")
    next_slot = 0
    pending: int | None = None
    replacements = 0
    tokens = 0
    cost = Decimal("0")
    for attempt in attempts:
        slot = attempt.get("slot_index")
        kind = attempt.get("attempt_kind")
        status = attempt.get("status")
        trial_tokens = attempt.get("completion_tokens")
        if not isinstance(slot, int) or isinstance(slot, bool) or status not in _STATUSES:
            raise LiveReviewContractError("invalid_attempt")
        if not isinstance(trial_tokens, int) or isinstance(trial_tokens, bool) or trial_tokens < 0:
            raise LiveReviewContractError("invalid_completion_tokens")
        if trial_tokens > limits["maximum_completion_tokens_per_trial"]:
            raise LiveReviewContractError("trial_completion_token_limit")
        trial_cost = _decimal(attempt.get("cost_usd"), "cost_usd")
        if kind == "primary":
            if pending is not None:
                raise LiveReviewContractError("unresolved_infrastructure_failure")
            if slot != next_slot:
                raise LiveReviewContractError("primary_order_mismatch")
            if status in _INFRASTRUCTURE:
                pending = slot
            else:
                next_slot += 1
        elif kind == "replacement":
            if pending != slot:
                raise LiveReviewContractError("replacement_without_infrastructure_failure")
            replacements += 1
            if replacements > limits["maximum_replacements"]:
                raise LiveReviewContractError("campaign_replacement_limit")
            if status in _INFRASTRUCTURE:
                raise LiveReviewContractError("second_infrastructure_failure")
            pending = None
            next_slot += 1
        else:
            raise LiveReviewContractError("invalid_attempt_kind")
        tokens += trial_tokens
        cost += trial_cost
        if tokens > limits["maximum_completion_tokens"]:
            raise LiveReviewContractError("campaign_completion_token_limit")
        if cost >= _decimal(limits["maximum_usd"], "maximum_usd"):
            raise LiveReviewContractError("campaign_cost_limit")
    return {
        "next_slot_index": next_slot, "pending_replacement_for": pending,
        "replacement_count": replacements, "attempt_count": len(attempts),
        "total_completion_tokens": tokens, "total_cost_usd": cost,
        "complete": next_slot == len(manifest["execution_order"]),
    }


def custody_tree_manifest(root: str | os.PathLike[str]) -> dict[str, Any]:
    """Hash every regular file below one custody root."""

    custody_root = Path(root)
    if custody_root.is_symlink() or not custody_root.is_dir():
        raise LiveReviewContractError("invalid_custody_root")
    files: list[dict[str, Any]] = []
    for path in sorted(custody_root.rglob("*")):
        if path.is_symlink():
            raise LiveReviewContractError(f"custody_symlink:{path.relative_to(custody_root).as_posix()}")
        if path.is_file():
            content = path.read_bytes()
            files.append({"path": path.relative_to(custody_root).as_posix(), "size": len(content), "sha256": sha256(content).hexdigest()})
    result = {"schema": "caplab.review-dissent.custody-tree/v1", "files": files}
    result["tree_sha256"] = _digest(result)
    return result


def _exclusive_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(_canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def _exclusive_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def prepare_trial(manifest: Mapping[str, Any], *, slot_index: int, attempt_kind: str, prior_attempts: Sequence[Mapping[str, Any]]) -> tuple[Path, list[str]]:
    """Render and seal the next development trial before its provider call."""

    state = assess_attempts(manifest, prior_attempts)
    if state["complete"]:
        raise LiveReviewContractError("campaign_already_complete")
    pending = state["pending_replacement_for"]
    if pending is None:
        if attempt_kind != "primary" or slot_index != state["next_slot_index"]:
            raise LiveReviewContractError("next_action_mismatch")
    elif attempt_kind != "replacement" or slot_index != pending:
        raise LiveReviewContractError("next_action_mismatch")
    attempt_number = len(prior_attempts) + 1
    root = Path(manifest["storage"]["raw_custody_root"])
    if root.is_symlink():
        raise LiveReviewContractError("raw_custody_root_symlink")
    attempt_root = root / "attempts" / f"a{attempt_number:02d}-s{slot_index + 1:02d}-{attempt_kind}"
    if attempt_root.exists() or attempt_root.is_symlink():
        raise LiveReviewContractError("attempt_custody_exists")
    cell_id, subject_id = manifest["execution_order"][slot_index].split(":", 1)
    public_task_id = manifest["_instrument"]["cells"][cell_id]["public_task_id"]
    task_root = attempt_root / "input" / public_task_id
    render_review_cell(manifest["_instrument"], cell_id, task_root)
    command = harbor_command(manifest, slot_index=slot_index, task_path=task_root, jobs_path=attempt_root / "harbor")
    launch = {
        "schema": "caplab.review-dissent.live-launch/v1", "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"], "attempt_number": attempt_number,
        "slot_index": slot_index, "attempt_kind": attempt_kind, "cell_id": cell_id,
        "public_task_id": public_task_id, "subject_id": subject_id,
        "provider_route": manifest["subjects"][subject_id]["provider_route"],
        "input_tree": custody_tree_manifest(attempt_root / "input"), "command": command,
        "launched_at": datetime.now(UTC).isoformat(),
    }
    launch["launch_sha256"] = _digest(launch)
    _exclusive_json(attempt_root / "launch.json", launch)
    return attempt_root, command


def execute_trial(manifest: Mapping[str, Any], *, slot_index: int, attempt_kind: str, prior_attempts: Sequence[Mapping[str, Any]]) -> Path:
    """Execute exactly one trial and preserve its command output."""

    preflight_runtime(manifest)
    attempt_root, command = prepare_trial(manifest, slot_index=slot_index, attempt_kind=attempt_kind, prior_attempts=prior_attempts)
    started = datetime.now(UTC)
    try:
        completed = subprocess.run(command, cwd=manifest["_project_root"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=manifest["surface"]["wall_clock_minutes"] * 60 + 900, check=False)
        return_code: int | None = completed.returncode
        stdout, stderr, timed_out = completed.stdout, completed.stderr, False
    except subprocess.TimeoutExpired as error:
        return_code = None
        stdout, stderr, timed_out = error.stdout or b"", error.stderr or b"", True
    _exclusive_bytes(attempt_root / "harbor.stdout", stdout)
    _exclusive_bytes(attempt_root / "harbor.stderr", stderr)
    finished = datetime.now(UTC)
    completion = {
        "schema": "caplab.review-dissent.live-completion/v1", "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"], "started_at": started.isoformat(),
        "finished_at": finished.isoformat(), "duration_seconds": format((finished - started).total_seconds(), ".6f"),
        "return_code": return_code, "timed_out": timed_out,
        "stdout_sha256": sha256(stdout).hexdigest(), "stderr_sha256": sha256(stderr).hexdigest(),
    }
    completion["completion_sha256"] = _digest(completion)
    _exclusive_json(attempt_root / "completion.json", completion)
    return attempt_root


def load_custody_attempts(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Derive accounting only from sealed raw-custody observations."""

    attempts_root = Path(manifest["storage"]["raw_custody_root"]) / "attempts"
    if not attempts_root.exists():
        return []
    if attempts_root.is_symlink() or not attempts_root.is_dir():
        raise LiveReviewContractError("invalid_attempts_custody")
    directories = sorted(path for path in attempts_root.iterdir() if path.is_dir())
    if any(path.is_symlink() for path in directories):
        raise LiveReviewContractError("attempt_custody_symlink")
    attempts: list[dict[str, Any]] = []
    for expected_number, root in enumerate(directories, 1):
        launch, _ = _read_json(root / "launch.json")
        completion, _ = _read_json(root / "completion.json")
        observation_path = root / "observation.json"
        if not observation_path.is_file():
            raise LiveReviewContractError(f"unclassified_attempt:{root.name}")
        observation, _ = _read_json(observation_path)
        _validate_sealed(launch, "launch_sha256", "launch_digest_mismatch")
        _validate_sealed(completion, "completion_sha256", "completion_digest_mismatch")
        _validate_sealed(observation, "observation_sha256", "observation_digest_mismatch")
        if launch.get("attempt_number") != expected_number or observation.get("attempt_number") != expected_number:
            raise LiveReviewContractError("attempt_number_mismatch")
        if launch.get("manifest_sha256") != manifest["manifest_sha256"] or observation.get("manifest_sha256") != manifest["manifest_sha256"]:
            raise LiveReviewContractError("attempt_manifest_mismatch")
        raw_path = observation.get("source_result_path")
        relative = PurePosixPath(str(raw_path))
        if not isinstance(raw_path, str) or relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise LiveReviewContractError("attempt_result_path_invalid")
        source = Path(manifest["storage"]["raw_custody_root"]).joinpath(*relative.parts)
        if source.is_symlink() or not source.is_file() or sha256(source.read_bytes()).hexdigest() != observation.get("source_result_sha256"):
            raise LiveReviewContractError("attempt_result_unavailable_or_changed")
        attempts.append({key: observation[key] for key in ("slot_index", "attempt_kind", "status", "completion_tokens", "cost_usd")})
    assess_attempts(manifest, attempts)
    return attempts


def record_observation(manifest: Mapping[str, Any], *, attempt_root: str | os.PathLike[str], status: str) -> dict[str, Any]:
    """Bind an explicit outcome class to measured metrics and raw artifacts."""

    supplied = Path(attempt_root)
    if supplied.is_symlink():
        raise LiveReviewContractError("attempt_outside_custody")
    root = supplied.resolve()
    custody = Path(manifest["storage"]["raw_custody_root"]).resolve()
    if root.parent != custody / "attempts" or status not in _STATUSES:
        raise LiveReviewContractError("attempt_outside_custody_or_invalid_status")
    launch, _ = _read_json(root / "launch.json")
    completion, _ = _read_json(root / "completion.json")
    _validate_sealed(launch, "launch_sha256", "launch_digest_mismatch")
    _validate_sealed(completion, "completion_sha256", "completion_digest_mismatch")
    results: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted((root / "harbor").rglob("result.json")):
        value, _ = _read_json(path)
        if "agent_result" in value and "trial_name" in value:
            results.append((path, value))
    if len(results) != 1:
        raise LiveReviewContractError("harbor_trial_result_ambiguous")
    result_path, result = results[0]
    agent_result = result.get("agent_result")
    if not isinstance(agent_result, dict):
        raise LiveReviewContractError("harbor_agent_result_missing")
    tokens = agent_result.get("n_output_tokens")
    if not isinstance(tokens, int) or isinstance(tokens, bool) or tokens < 0:
        raise LiveReviewContractError("measured_completion_tokens_missing")
    exception = result.get("exception_info") is not None or completion.get("return_code") != 0 or completion.get("timed_out") is True
    raw_cost = agent_result.get("cost_usd")
    if raw_cost is None and exception and tokens == 0:
        cost = Decimal("0")
    elif not isinstance(raw_cost, (int, float, str)) or isinstance(raw_cost, bool):
        raise LiveReviewContractError("measured_cost_missing")
    else:
        cost = _decimal(str(raw_cost), "cost_usd")
    if exception and status not in _INFRASTRUCTURE:
        raise LiveReviewContractError("infrastructure_result_misclassified")
    if not exception and status in _INFRASTRUCTURE:
        raise LiveReviewContractError("subject_result_misclassified")
    artifact_root = result_path.parent / "artifacts" / "app"
    if not artifact_root.is_dir():
        raise LiveReviewContractError("harbor_artifact_missing")
    result_bytes = result_path.read_bytes()
    observation = {
        "schema": "caplab.review-dissent.live-observation/v1", "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"], "attempt_number": launch["attempt_number"],
        "slot_index": launch["slot_index"], "attempt_kind": launch["attempt_kind"], "status": status,
        "completion_tokens": tokens, "cost_usd": format(cost, "f"),
        "source_result_path": result_path.relative_to(custody).as_posix(),
        "source_result_sha256": sha256(result_bytes).hexdigest(),
        "artifact_tree": custody_tree_manifest(artifact_root), "recorded_at": datetime.now(UTC).isoformat(),
    }
    observation["observation_sha256"] = _digest(observation)
    _exclusive_json(root / "observation.json", observation)
    return observation


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m caplab.review_dissent.live")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--study-root", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    commands.add_parser("preflight")
    run = commands.add_parser("run")
    run.add_argument("--slot-index", required=True, type=int)
    run.add_argument("--attempt-kind", required=True, choices=("primary", "replacement"))
    observe = commands.add_parser("observe")
    observe.add_argument("--attempt-root", required=True, type=Path)
    observe.add_argument("--status", required=True, choices=tuple(sorted(_STATUSES)))
    args = parser.parse_args(argv)
    manifest = load_live_manifest(args.manifest, args.study_root)
    if args.command == "validate":
        print(json.dumps({"campaign_id": manifest["campaign_id"], "manifest_sha256": manifest["manifest_sha256"]}, sort_keys=True))
        return 0
    if args.command == "preflight":
        print(json.dumps(preflight_runtime(manifest), sort_keys=True))
        return 0
    if args.command == "observe":
        print(json.dumps(record_observation(manifest, attempt_root=args.attempt_root, status=args.status), sort_keys=True))
        return 0
    attempt_root = execute_trial(manifest, slot_index=args.slot_index, attempt_kind=args.attempt_kind, prior_attempts=load_custody_attempts(manifest))
    print(attempt_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
