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
)


class NativePreferenceLiveContractError(ValueError):
    """The native live manifest or containment boundary is invalid."""


_CLAUDE_BINARY = Path("/home/halbritt/.local/share/claude/versions/2.1.215")
_CLAUDE_CONFIG = Path(
    "/home/halbritt/.local/share/striatum/harness-config/claude-code"
)
_CODEX_MODULE = Path("/home/halbritt/.npm-global/lib/node_modules/@openai/codex")
_CODEX_CONFIG = Path("/home/halbritt/.local/share/striatum/harness-config/codex")


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
    result = dict(manifest)
    result["_instrument"] = instrument
    result["_manifest_path"] = manifest_file.resolve()
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
