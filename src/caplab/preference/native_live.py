"""Externally contained launch construction for native preference subjects."""

from __future__ import annotations

import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Any

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
_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


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
    if manifest.get("status") != "active" or manifest.get("authority") != "adr-0041":
        raise NativePreferenceLiveContractError("native_live_not_authorized")
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
        "--ro-bind",
        str(_CLAUDE_BINARY),
        "/opt/claude",
        "--ro-bind",
        str(_CODEX_MODULE),
        "/opt/codex",
        "--symlink",
        "/opt/claude",
        "/toolbin/claude",
        "--symlink",
        "/opt/codex/bin/codex.js",
        "/toolbin/codex",
        "--dir",
        "/harness-config",
        "--bind",
        str(_CLAUDE_CONFIG),
        "/harness-config/claude-code",
        "--bind",
        str(_CODEX_CONFIG),
        "/harness-config/codex",
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


def prepare_native_trial(
    manifest: dict[str, Any], *, slot_index: int, attempt_kind: str
) -> tuple[Path, list[str]]:
    """Render and seal one native attempt; never launch an unapproved manifest."""

    if (
        manifest.get("status") != "active"
        or manifest.get("authority") != "adr-0041"
        or manifest.get("_verified_manifest_sha256") != manifest.get("manifest_sha256")
    ):
        raise NativePreferenceLiveContractError("native_live_not_authorized")
    instrument = manifest.get("_instrument")
    order = instrument.get("execution_order") if isinstance(instrument, dict) else None
    if not isinstance(order, list) or not isinstance(slot_index, int) or not 0 <= slot_index < len(order):
        raise NativePreferenceLiveContractError("invalid_native_live_slot")
    if attempt_kind not in {"primary", "replacement"}:
        raise NativePreferenceLiveContractError("invalid_native_attempt_kind")
    task_id, subject_id = order[slot_index].split(":", 1)
    custody_root = Path(manifest["storage"]["raw_custody_root"])
    attempt_root = custody_root / "attempts" / f"s{slot_index + 1:02d}-{attempt_kind}"
    if attempt_root.exists() or attempt_root.is_symlink():
        raise NativePreferenceLiveContractError("native_attempt_custody_exists")
    task_root = attempt_root / "input" / task_id
    render_native_task(instrument, task_id, task_root)
    invocation = build_contained_invocation(instrument, subject_id, task_id, task_root.resolve())
    launch = {
        "schema": "caplab.preference.native-launch/v1",
        "campaign_id": manifest.get("campaign_id"),
        "manifest_sha256": manifest.get("manifest_sha256"),
        "slot_index": slot_index,
        "attempt_kind": attempt_kind,
        "task_id": task_id,
        "subject_id": subject_id,
        "tuple_id": invocation["tuple_id"],
        "command": invocation["command"],
    }
    launch["launch_sha256"] = sha256(_canonical(launch)).hexdigest()
    _exclusive_json(attempt_root / "launch.json", launch)
    return attempt_root, invocation["command"]
