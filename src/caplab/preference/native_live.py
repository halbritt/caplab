"""Externally contained launch construction for native preference subjects."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from .native import (
    NativePreferenceContractError,
    build_native_invocation,
    load_native_instrument,
    render_native_task,
)


class NativePreferenceLiveContractError(ValueError):
    """The native live manifest or containment boundary is invalid."""


_CLAUDE_BINARY = Path("/home/halbritt/.local/share/claude/versions/2.1.215")
_CLAUDE_CONFIG = Path(
    "/home/halbritt/.local/share/striatum/harness-config/claude-code"
)
_CODEX_MODULE = Path("/home/halbritt/.npm-global/lib/node_modules/@openai/codex")
_CODEX_CONFIG = Path("/home/halbritt/.local/share/striatum/harness-config/codex")
_CODEX_AUTH = Path("/home/halbritt/.codex/auth.json")
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SUBJECT_STATUSES = {"completed", "refused", "invalid"}
_INFRASTRUCTURE_STATUSES = {
    "provider_failure",
    "harness_failure",
    "capture_failure",
    "task_image_failure",
    "verifier_failure",
}
_STATUSES = _SUBJECT_STATUSES | _INFRASTRUCTURE_STATUSES


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def load_native_live_manifest(
    manifest_path: str | os.PathLike[str], instrument_path: str | os.PathLike[str]
) -> dict[str, Any]:
    """Load an authorized native campaign and its content-addressed instrument."""

    manifest_file = Path(manifest_path)
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NativePreferenceLiveContractError(f"native_live_unreadable:{error}") from error
    if not isinstance(manifest, dict) or manifest.get("schema") != "caplab.preference.native-live-manifest/v1":
        raise NativePreferenceLiveContractError("invalid_native_live_schema")
    if manifest.get("status") != "active" or manifest.get("authority") not in {
        "adr-0041",
        "adr-0042",
    }:
        raise NativePreferenceLiveContractError("native_live_not_authorized")
    try:
        expires_at = datetime.fromisoformat(
            str(manifest.get("expires_at")).replace("Z", "+00:00")
        )
    except ValueError as error:
        raise NativePreferenceLiveContractError("invalid_native_live_expiry") from error
    if expires_at.tzinfo is None or datetime.now(UTC) > expires_at:
        raise NativePreferenceLiveContractError("native_live_authorization_expired")
    sealed = dict(manifest)
    claimed = sealed.pop("manifest_sha256", None)
    if claimed != sha256(_canonical(sealed)).hexdigest():
        raise NativePreferenceLiveContractError("native_live_manifest_digest_mismatch")
    instrument_file = Path(instrument_path)
    if sha256(instrument_file.read_bytes()).hexdigest() != manifest.get("instrument", {}).get("file_sha256"):
        raise NativePreferenceLiveContractError("native_live_instrument_file_mismatch")
    instrument = load_native_instrument(instrument_file)
    if instrument["design_sha256"] != manifest["instrument"].get("design_sha256"):
        raise NativePreferenceLiveContractError("native_live_instrument_design_mismatch")
    containment = manifest.get("containment")
    source_path = containment.get("source_path") if isinstance(containment, dict) else None
    if not isinstance(source_path, str) or Path(source_path).is_absolute():
        raise NativePreferenceLiveContractError("invalid_native_live_containment_source")
    try:
        source_file = (_PROJECT_ROOT / source_path).resolve(strict=True)
    except OSError as error:
        raise NativePreferenceLiveContractError(
            f"native_live_containment_source_unreadable:{error}"
        ) from error
    if not source_file.is_relative_to(_PROJECT_ROOT) or not source_file.is_file():
        raise NativePreferenceLiveContractError("invalid_native_live_containment_source")
    if sha256(source_file.read_bytes()).hexdigest() != containment.get("source_sha256"):
        raise NativePreferenceLiveContractError("native_live_containment_source_mismatch")
    result = dict(manifest)
    result["_instrument"] = instrument
    result["_manifest_path"] = manifest_file.resolve()
    result["_verified_manifest_sha256"] = manifest["manifest_sha256"]
    return result


def _system_mounts() -> list[str]:
    command: list[str] = []
    for path in ("/usr", "/bin", "/lib", "/lib64"):
        if Path(path).exists():
            command.extend(["--ro-bind", path, path])
    for path in (
        "/etc/hosts",
        "/etc/resolv.conf",
        "/etc/nsswitch.conf",
        "/etc/passwd",
        "/etc/group",
        "/etc/ssl/certs",
    ):
        if Path(path).exists():
            command.extend(["--ro-bind", path, path])
    return command


def _sandbox_native_command(command: list[str]) -> list[str]:
    replacements = {
        f"CLAUDE_CONFIG_DIR={_CLAUDE_CONFIG}": "CLAUDE_CONFIG_DIR=/harness-config/claude-code",
        f"CODEX_HOME={_CODEX_CONFIG}": "CODEX_HOME=/harness-config/codex",
    }
    return [replacements.get(token, token) for token in command]


def _contained_command(root: Path, native_command: list[str]) -> list[str]:
    if f"CLAUDE_CONFIG_DIR={_CLAUDE_CONFIG}" in native_command:
        harness_mounts = [
            "--ro-bind",
            str(_CLAUDE_BINARY),
            "/opt/claude",
            "--symlink",
            "/opt/claude",
            "/toolbin/claude",
            "--dir",
            "/harness-config",
            "--bind",
            str(_CLAUDE_CONFIG),
            "/harness-config/claude-code",
        ]
    elif f"CODEX_HOME={_CODEX_CONFIG}" in native_command:
        harness_mounts = [
            "--ro-bind",
            str(_CODEX_MODULE),
            "/opt/codex",
            "--symlink",
            "/opt/codex/bin/codex.js",
            "/toolbin/codex",
            "--dir",
            "/harness-config",
            "--dir",
            "/harness-config/codex",
            "--bind",
            str(_CODEX_AUTH),
            "/harness-config/codex/auth.json",
            "--ro-bind",
            str(_CODEX_CONFIG / "config.toml"),
            "/harness-config/codex/config.toml",
            "--ro-bind",
            str(_CODEX_CONFIG / "models_cache.json"),
            "/harness-config/codex/models_cache.json",
        ]
    else:
        raise NativePreferenceLiveContractError("unknown_native_harness_command")
    return [
        "/usr/bin/bwrap",
        "--unshare-all",
        "--share-net",
        "--die-with-parent",
        "--new-session",
        "--clearenv",
        *_system_mounts(),
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--tmpfs",
        "/tmp",
        "--dir",
        "/toolbin",
        "--dir",
        "/opt",
        *harness_mounts,
        "--bind",
        str(root),
        "/work",
        "--chdir",
        "/work",
        "--setenv",
        "HOME",
        "/tmp/home",
        "--setenv",
        "PATH",
        "/toolbin:/usr/bin:/bin",
        "--setenv",
        "LANG",
        "C.UTF-8",
        "--",
        *_sandbox_native_command(native_command),
    ]


def _task_root(task_root: str | os.PathLike[str]) -> Path:
    root = Path(task_root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise NativePreferenceContractError("unsafe_live_task_root")
    return root


def build_contained_invocation(
    instrument: dict[str, Any],
    subject_id: str,
    task_id: str,
    task_root: str | os.PathLike[str],
) -> dict[str, Any]:
    """Build a native invocation inside a task-only bubblewrap namespace."""

    root = _task_root(task_root)
    native = build_native_invocation(instrument, subject_id, task_id, Path("/work"))
    command = _contained_command(root, native["command"])
    return {**native, "cwd": root, "command": command}


def build_contained_version_probe(
    instrument: dict[str, Any], subject_id: str, task_root: str | os.PathLike[str]
) -> dict[str, Any]:
    """Build the tuple's no-inference version probe in the live namespace."""

    root = _task_root(task_root)
    subject = instrument.get("agent_systems", {}).get(subject_id)
    if not isinstance(subject, dict):
        raise NativePreferenceContractError("unknown_subject")
    return {
        "subject_id": subject_id,
        "tuple_id": subject["tuple_id"],
        "cwd": root,
        "command": _contained_command(root, list(subject["version_command"])),
    }


def _exclusive_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(_canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def _exclusive_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())


def custody_tree_manifest(root: str | os.PathLike[str]) -> dict[str, Any]:
    """Content-identify every regular file under one attempt tree."""

    tree_root = Path(root)
    if tree_root.is_symlink() or not tree_root.is_dir():
        raise NativePreferenceLiveContractError("invalid_native_custody_tree")
    files: list[dict[str, Any]] = []
    for path in sorted(tree_root.rglob("*")):
        if path.is_symlink():
            raise NativePreferenceLiveContractError(
                f"native_custody_symlink:{path.relative_to(tree_root).as_posix()}"
            )
        if path.is_file():
            content = path.read_bytes()
            files.append(
                {
                    "path": path.relative_to(tree_root).as_posix(),
                    "size": len(content),
                    "sha256": sha256(content).hexdigest(),
                }
            )
    result = {"schema": "caplab.preference.native-custody-tree/v1", "files": files}
    result["tree_sha256"] = _digest(result)
    return result


def assess_native_attempts(
    manifest: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Validate ordered native attempt accounting and derive the next action."""

    limits = manifest.get("limits", {})
    maximum_trials = limits.get("maximum_trials")
    maximum_replacements = limits.get("maximum_replacements")
    maximum_seconds = limits.get("maximum_wall_clock_hours", 0) * 3600
    if not isinstance(maximum_trials, int) or len(attempts) > maximum_trials:
        raise NativePreferenceLiveContractError("native_campaign_trial_limit")
    order = manifest.get("_instrument", {}).get("execution_order")
    if not isinstance(order, list):
        raise NativePreferenceLiveContractError("native_execution_order_unavailable")
    next_slot = 0
    pending_replacement: int | None = None
    replacement_count = 0
    total_seconds = 0.0
    stop_reason: str | None = None
    for attempt in attempts:
        if stop_reason is not None:
            raise NativePreferenceLiveContractError("native_attempt_after_stop")
        slot_index = attempt.get("slot_index")
        kind = attempt.get("attempt_kind")
        status = attempt.get("status")
        duration = attempt.get("duration_seconds")
        if not isinstance(slot_index, int) or isinstance(slot_index, bool):
            raise NativePreferenceLiveContractError("invalid_native_attempt_slot")
        if status not in _STATUSES:
            raise NativePreferenceLiveContractError("invalid_native_attempt_status")
        try:
            seconds = float(duration)
        except (TypeError, ValueError) as error:
            raise NativePreferenceLiveContractError("invalid_native_attempt_duration") from error
        if seconds < 0:
            raise NativePreferenceLiveContractError("invalid_native_attempt_duration")
        if kind == "primary":
            if pending_replacement is not None:
                raise NativePreferenceLiveContractError("unresolved_native_infrastructure_failure")
            if slot_index != next_slot:
                raise NativePreferenceLiveContractError("native_primary_order_mismatch")
            if status in _INFRASTRUCTURE_STATUSES:
                pending_replacement = slot_index
            else:
                next_slot += 1
        elif kind == "replacement":
            if pending_replacement != slot_index:
                raise NativePreferenceLiveContractError("native_replacement_without_failure")
            replacement_count += 1
            if not isinstance(maximum_replacements, int) or replacement_count > maximum_replacements:
                raise NativePreferenceLiveContractError("native_campaign_replacement_limit")
            if status in _INFRASTRUCTURE_STATUSES:
                stop_reason = "second_native_infrastructure_failure"
            else:
                pending_replacement = None
                next_slot += 1
        else:
            raise NativePreferenceLiveContractError("invalid_native_attempt_kind")
        total_seconds += seconds
        if total_seconds >= maximum_seconds:
            stop_reason = "native_campaign_wall_clock_limit"
    complete = next_slot == len(order)
    if not complete and len(attempts) >= maximum_trials:
        stop_reason = stop_reason or "native_campaign_trial_limit"
    if (
        not complete
        and pending_replacement is not None
        and replacement_count >= maximum_replacements
    ):
        stop_reason = stop_reason or "native_campaign_replacement_limit"
    return {
        "next_slot_index": next_slot,
        "pending_replacement_for": pending_replacement,
        "replacement_count": replacement_count,
        "attempt_count": len(attempts),
        "duration_seconds": format(total_seconds, ".6f"),
        "complete": complete,
        "stop_reason": stop_reason,
    }


def prepare_native_trial(
    manifest: dict[str, Any], *, slot_index: int, attempt_kind: str,
    prior_attempts: Sequence[Mapping[str, Any]] = (),
    observed_versions: Mapping[str, str] | None = None,
) -> tuple[Path, list[str]]:
    """Render and seal one native attempt; never launch an unapproved manifest."""

    if (
        manifest.get("status") != "active"
        or manifest.get("authority") not in {"adr-0041", "adr-0042"}
        or manifest.get("_verified_manifest_sha256") != manifest.get("manifest_sha256")
    ):
        raise NativePreferenceLiveContractError("native_live_not_authorized")
    instrument = manifest.get("_instrument")
    order = instrument.get("execution_order") if isinstance(instrument, dict) else None
    if not isinstance(order, list) or not isinstance(slot_index, int) or not 0 <= slot_index < len(order):
        raise NativePreferenceLiveContractError("invalid_native_live_slot")
    if attempt_kind not in {"primary", "replacement"}:
        raise NativePreferenceLiveContractError("invalid_native_attempt_kind")
    state = assess_native_attempts(manifest, prior_attempts)
    if state["complete"]:
        raise NativePreferenceLiveContractError("native_campaign_already_complete")
    if state["stop_reason"] is not None:
        raise NativePreferenceLiveContractError(
            f"native_campaign_stopped:{state['stop_reason']}"
        )
    if state["pending_replacement_for"] is None:
        if attempt_kind != "primary" or slot_index != state["next_slot_index"]:
            raise NativePreferenceLiveContractError("native_next_action_mismatch")
    elif attempt_kind != "replacement" or slot_index != state["pending_replacement_for"]:
        raise NativePreferenceLiveContractError("native_next_action_mismatch")
    task_id, subject_id = order[slot_index].split(":", 1)
    custody_root = Path(manifest["storage"]["raw_custody_root"])
    if custody_root.is_symlink():
        raise NativePreferenceLiveContractError("native_custody_root_symlink")
    attempt_number = len(prior_attempts) + 1
    attempt_root = custody_root / "attempts" / f"a{attempt_number:02d}-s{slot_index + 1:02d}-{attempt_kind}"
    if attempt_root.exists() or attempt_root.is_symlink():
        raise NativePreferenceLiveContractError("native_attempt_custody_exists")
    task_root = attempt_root / "input" / task_id
    render_native_task(instrument, task_id, task_root)
    invocation = build_contained_invocation(instrument, subject_id, task_id, task_root.resolve())
    launch = {
        "schema": "caplab.preference.native-launch/v1",
        "campaign_id": manifest.get("campaign_id"),
        "manifest_sha256": manifest.get("manifest_sha256"),
        "attempt_number": attempt_number,
        "slot_index": slot_index,
        "attempt_kind": attempt_kind,
        "task_id": task_id,
        "subject_id": subject_id,
        "tuple_id": invocation["tuple_id"],
        "input_tree": custody_tree_manifest(attempt_root / "input"),
        "observed_versions": dict(observed_versions or manifest.get("runtime_versions", {})),
        "command": invocation["command"],
        "launched_at": datetime.now(UTC).isoformat(),
    }
    launch["launch_sha256"] = _digest(launch)
    _exclusive_json(attempt_root / "launch.json", launch)
    return attempt_root, invocation["command"]


def preflight_native_runtime(manifest: Mapping[str, Any]) -> dict[str, str]:
    """Verify exact native harness and containment versions without inference."""

    instrument = manifest.get("_instrument")
    if not isinstance(instrument, dict):
        raise NativePreferenceLiveContractError("native_live_instrument_not_loaded")
    expected = manifest.get("runtime_versions")
    if not isinstance(expected, dict):
        raise NativePreferenceLiveContractError("native_runtime_versions_missing")
    observed: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="caplab-native-preflight-") as directory:
        root = Path(directory).resolve()
        for subject_id, version_key in (("fable", "claude-code"), ("gpt", "codex")):
            probe = build_contained_version_probe(instrument, subject_id, root)
            completed = subprocess.run(
                probe["command"], cwd=root, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False,
            )
            value = completed.stdout.decode("utf-8", errors="replace").strip()
            if completed.returncode != 0 or value != expected.get(version_key):
                raise NativePreferenceLiveContractError(f"native_runtime_version_mismatch:{version_key}")
            observed[version_key] = value
    bwrap = subprocess.run(
        ["/usr/bin/bwrap", "--version"], stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False,
    )
    value = bwrap.stdout.decode("utf-8", errors="replace").strip()
    if bwrap.returncode != 0 or value != expected.get("bubblewrap"):
        raise NativePreferenceLiveContractError("native_runtime_version_mismatch:bubblewrap")
    observed["bubblewrap"] = value
    auth_commands = {
        "claude-code": [
            "/usr/bin/env",
            f"CLAUDE_CONFIG_DIR={_CLAUDE_CONFIG}",
            "claude",
            "auth",
            "status",
        ],
        "codex": [
            "/usr/bin/env",
            f"CODEX_HOME={_CODEX_CONFIG}",
            "codex",
            "login",
            "status",
        ],
    }
    with tempfile.TemporaryDirectory(
        prefix="caplab-native-auth-preflight-"
    ) as directory:
        root = Path(directory).resolve()
        claude_auth = subprocess.run(
            _contained_command(root, auth_commands["claude-code"]),
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        try:
            claude_status = json.loads(claude_auth.stdout.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise NativePreferenceLiveContractError(
                "native_auth_status_invalid:claude-code"
            ) from error
        if (
            claude_auth.returncode != 0
            or not isinstance(claude_status, dict)
            or claude_status.get("loggedIn") is not True
            or claude_status.get("authMethod") != "claude.ai"
            or claude_status.get("apiProvider") != "firstParty"
            or claude_status.get("subscriptionType") != "max"
        ):
            raise NativePreferenceLiveContractError(
                "native_auth_status_mismatch:claude-code"
            )
        observed["claude-code-auth"] = "claude.ai:firstParty:max"
        codex_auth = subprocess.run(
            _contained_command(root, auth_commands["codex"]),
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        if codex_auth.returncode != 0 or codex_auth.stderr.decode(
            "utf-8", errors="replace"
        ).strip() != "Logged in using ChatGPT":
            raise NativePreferenceLiveContractError(
                "native_auth_status_mismatch:codex"
            )
        observed["codex-auth"] = "ChatGPT"
    return observed


def _read_json(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise NativePreferenceLiveContractError(f"native_json_symlink:{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NativePreferenceLiveContractError(f"native_json_unreadable:{path}:{error}") from error
    if not isinstance(value, dict):
        raise NativePreferenceLiveContractError(f"native_json_not_object:{path}")
    return value


def _validate_sealed(document: dict[str, Any], field: str, error: str) -> None:
    sealed = dict(document)
    claimed = sealed.pop(field, None)
    if claimed != _digest(sealed):
        raise NativePreferenceLiveContractError(error)


def _native_result(subject_id: str, content: bytes) -> tuple[str, dict[str, int]]:
    """Extract the final native agent message and measured usage from JSONL."""

    events: list[dict[str, Any]] = []
    try:
        for line in content.decode("utf-8").splitlines():
            if line.strip():
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError("event_not_object")
                events.append(event)
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise NativePreferenceLiveContractError("native_output_not_jsonl") from error
    text = ""
    usage: dict[str, int] = {}
    if subject_id == "fable":
        results = [event for event in events if event.get("type") == "result"]
        if len(results) != 1 or results[0].get("is_error") is True:
            raise NativePreferenceLiveContractError("native_result_unavailable")
        text = results[0].get("result", "")
        raw_usage = results[0].get("usage", {})
    elif subject_id == "gpt":
        messages = [
            event.get("item", {}).get("text")
            for event in events
            if event.get("type") == "item.completed"
            and event.get("item", {}).get("type") == "agent_message"
        ]
        turns = [event for event in events if event.get("type") == "turn.completed"]
        if not messages or not turns:
            raise NativePreferenceLiveContractError("native_result_unavailable")
        text = messages[-1]
        raw_usage = turns[-1].get("usage", {})
    else:
        raise NativePreferenceLiveContractError("unknown_subject")
    if not isinstance(text, str) or not text.strip() or not isinstance(raw_usage, dict):
        raise NativePreferenceLiveContractError("native_result_unavailable")
    for key, value in raw_usage.items():
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            usage[str(key)] = value
    return text, usage


def _failure_status(stdout: bytes, stderr: bytes, timed_out: bool) -> str:
    if timed_out:
        return "harness_failure"
    encoded = (stdout + b"\n" + stderr).decode("utf-8", errors="replace").casefold()
    provider_markers = (
        "authentication", "unauthorized", "rate limit", "usage limit", "credit",
        "billing", "model_not_found", "model not found", "overloaded", "capacity",
    )
    return "provider_failure" if any(marker in encoded for marker in provider_markers) else "harness_failure"


def execute_native_trial(
    manifest: dict[str, Any], *, slot_index: int, attempt_kind: str,
    prior_attempts: Sequence[Mapping[str, Any]],
) -> Path:
    """Execute and seal exactly one contained native attempt."""

    versions = preflight_native_runtime(manifest)
    attempt_root, command = prepare_native_trial(
        manifest, slot_index=slot_index, attempt_kind=attempt_kind,
        prior_attempts=prior_attempts, observed_versions=versions,
    )
    started = datetime.now(UTC)
    try:
        completed = subprocess.run(
            command, cwd=attempt_root / "input" / manifest["_instrument"]["execution_order"][slot_index].split(":", 1)[0],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=manifest["limits"]["trial_wall_clock_minutes"] * 60, check=False,
        )
        return_code: int | None = completed.returncode
        stdout, stderr, timed_out = completed.stdout, completed.stderr, False
    except subprocess.TimeoutExpired as error:
        return_code = None
        stdout, stderr, timed_out = error.stdout or b"", error.stderr or b"", True
    _exclusive_bytes(attempt_root / "native.stdout", stdout)
    _exclusive_bytes(attempt_root / "native.stderr", stderr)
    finished = datetime.now(UTC)
    completion = {
        "schema": "caplab.preference.native-completion/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "launch_sha256": _read_json(attempt_root / "launch.json")["launch_sha256"],
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
    record_native_observation(manifest, attempt_root=attempt_root)
    return attempt_root


def record_native_observation(
    manifest: Mapping[str, Any], *, attempt_root: str | os.PathLike[str]
) -> dict[str, Any]:
    """Classify one completed native attempt and seal its captured result."""

    root = Path(attempt_root).resolve()
    custody_root = Path(manifest["storage"]["raw_custody_root"]).resolve()
    if root.parent != custody_root / "attempts":
        raise NativePreferenceLiveContractError("native_attempt_outside_custody")
    launch = _read_json(root / "launch.json")
    completion = _read_json(root / "completion.json")
    _validate_sealed(launch, "launch_sha256", "native_launch_digest_mismatch")
    _validate_sealed(completion, "completion_sha256", "native_completion_digest_mismatch")
    stdout = (root / "native.stdout").read_bytes()
    stderr = (root / "native.stderr").read_bytes()
    if sha256(stdout).hexdigest() != completion.get("stdout_sha256") or sha256(stderr).hexdigest() != completion.get("stderr_sha256"):
        raise NativePreferenceLiveContractError("native_capture_digest_mismatch")
    final_text = ""
    usage: dict[str, int] = {}
    if completion.get("return_code") == 0 and completion.get("timed_out") is False:
        try:
            final_text, usage = _native_result(launch["subject_id"], stdout)
            status = "completed"
        except NativePreferenceLiveContractError:
            reported = _failure_status(stdout, stderr, False)
            status = "provider_failure" if reported == "provider_failure" else "capture_failure"
    else:
        status = _failure_status(stdout, stderr, completion.get("timed_out") is True)
    observation = {
        "schema": "caplab.preference.native-observation/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "launch_sha256": launch["launch_sha256"],
        "completion_sha256": completion["completion_sha256"],
        "attempt_number": launch["attempt_number"],
        "slot_index": launch["slot_index"],
        "attempt_kind": launch["attempt_kind"],
        "subject_id": launch["subject_id"],
        "tuple_id": launch["tuple_id"],
        "status": status,
        "usage": usage,
        "final_text_sha256": sha256(final_text.encode("utf-8")).hexdigest() if final_text else None,
        "output_path": (root / "native.stdout").relative_to(custody_root).as_posix(),
        "output_sha256": sha256(stdout).hexdigest(),
        "task_tree": custody_tree_manifest(root / "input"),
        "duration_seconds": completion["duration_seconds"],
        "recorded_at": datetime.now(UTC).isoformat(),
    }
    observation["observation_sha256"] = _digest(observation)
    _exclusive_json(root / "observation.json", observation)
    return observation


def load_native_custody_attempts(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Load accounting only from complete, digest-bound native custody."""

    attempts_root = Path(manifest["storage"]["raw_custody_root"]) / "attempts"
    if not attempts_root.exists():
        return []
    if attempts_root.is_symlink() or not attempts_root.is_dir():
        raise NativePreferenceLiveContractError("invalid_native_attempts_custody")
    directories = sorted(path for path in attempts_root.iterdir() if path.is_dir())
    attempts: list[dict[str, Any]] = []
    for expected_number, root in enumerate(directories, start=1):
        if root.is_symlink():
            raise NativePreferenceLiveContractError("native_attempt_custody_symlink")
        launch = _read_json(root / "launch.json")
        completion = _read_json(root / "completion.json")
        observation = _read_json(root / "observation.json")
        _validate_sealed(launch, "launch_sha256", "native_launch_digest_mismatch")
        _validate_sealed(completion, "completion_sha256", "native_completion_digest_mismatch")
        _validate_sealed(observation, "observation_sha256", "native_observation_digest_mismatch")
        if launch.get("attempt_number") != expected_number or observation.get("attempt_number") != expected_number:
            raise NativePreferenceLiveContractError("native_attempt_number_mismatch")
        if launch.get("manifest_sha256") != manifest["manifest_sha256"] or observation.get("manifest_sha256") != manifest["manifest_sha256"]:
            raise NativePreferenceLiveContractError("native_attempt_manifest_mismatch")
        if completion.get("launch_sha256") != launch.get("launch_sha256"):
            raise NativePreferenceLiveContractError("native_completion_launch_mismatch")
        if observation.get("launch_sha256") != launch.get("launch_sha256") or observation.get("completion_sha256") != completion.get("completion_sha256"):
            raise NativePreferenceLiveContractError("native_observation_lineage_mismatch")
        relative = observation.get("output_path")
        if not isinstance(relative, str):
            raise NativePreferenceLiveContractError("native_output_path_invalid")
        relative_path = PurePosixPath(relative)
        if relative_path.is_absolute() or any(part in {"", ".", ".."} for part in relative_path.parts):
            raise NativePreferenceLiveContractError("native_output_path_invalid")
        output = Path(manifest["storage"]["raw_custody_root"]).joinpath(
            *relative_path.parts
        )
        if output.is_symlink() or not output.is_file() or sha256(output.read_bytes()).hexdigest() != observation.get("output_sha256"):
            raise NativePreferenceLiveContractError("native_output_digest_mismatch")
        if custody_tree_manifest(root / "input") != observation.get("task_tree"):
            raise NativePreferenceLiveContractError("native_task_tree_mismatch")
        attempts.append(
            {
                "slot_index": observation["slot_index"],
                "attempt_kind": observation["attempt_kind"],
                "status": observation["status"],
                "duration_seconds": observation["duration_seconds"],
            }
        )
    assess_native_attempts(manifest, attempts)
    return attempts


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m caplab.preference.native_live")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--instrument", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    commands.add_parser("preflight")
    run = commands.add_parser("run")
    run.add_argument("--slot-index", required=True, type=int)
    run.add_argument("--attempt-kind", required=True, choices=("primary", "replacement"))
    observe = commands.add_parser("observe")
    observe.add_argument("--attempt-root", required=True, type=Path)
    args = parser.parse_args(argv)
    manifest = load_native_live_manifest(args.manifest, args.instrument)
    if args.command == "validate":
        print(json.dumps({"campaign_id": manifest["campaign_id"], "manifest_sha256": manifest["manifest_sha256"]}, sort_keys=True))
        return 0
    if args.command == "preflight":
        print(json.dumps(preflight_native_runtime(manifest), sort_keys=True))
        return 0
    if args.command == "observe":
        print(json.dumps(record_native_observation(manifest, attempt_root=args.attempt_root), sort_keys=True))
        return 0
    attempts = load_native_custody_attempts(manifest)
    root = execute_native_trial(
        manifest, slot_index=args.slot_index, attempt_kind=args.attempt_kind,
        prior_attempts=attempts,
    )
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
