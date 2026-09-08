"""Fresh persistent host layout for a separately authorized native adapter."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import re

from caplab.native_capture_invocation import NativeCaptureContext, _digest, build_native_capture_invocation
from caplab.process_capture import _write_all, seal_capture_json


class NativeRuntimeError(ValueError):
    """A runtime cannot be prepared under the supplied invocation and paths."""


def _validated_invocation(policy_path: Path, invocation: dict, expected: str) -> dict:
    if not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
        raise NativeRuntimeError("invalid_expected_invocation_digest")
    try:
        if not isinstance(invocation, dict):
            raise ValueError("invocation is not an object")
        unsigned = {key: value for key, value in invocation.items() if key != "invocation_sha256"}
        if invocation.get("invocation_sha256") != expected or _digest(unsigned) != expected:
            raise ValueError("invocation digest differs")
        rebuilt = build_native_capture_invocation(policy_path, invocation["base_subject"]["tuple_id"],
            context=NativeCaptureContext(invocation["cwd"], invocation["runtime_root"],
                                         invocation["command"][-1].encode("utf-8"), invocation["session_id"]))
        if _digest(rebuilt) != _digest(invocation):
            raise ValueError("invocation differs from canonical builder")
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as error:
        raise NativeRuntimeError("invalid_native_capture_invocation") from error
    return rebuilt


def _sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def prepare_native_runtime(
    policy_path: Path, invocation: dict, *, expected_invocation_sha256: str,
    task_root: Path, output_dir: Path,
) -> dict:
    """Create fresh private runtime and sealed inputs; never seed credentials or launch.

    Caller supplies trusted stable host parents, a task root, and an independent
    invocation digest. Failure leaves partial custody and propagates. The returned
    mount map is prospective and grants no execution, containment or replay claim.
    """
    plan = _validated_invocation(policy_path, invocation, expected_invocation_sha256)
    task_root, output_dir = Path(task_root), Path(output_dir)
    if (not task_root.is_absolute() or task_root == Path("/") or task_root.resolve() != task_root
            or not task_root.is_dir()):
        raise NativeRuntimeError("task_root_must_be_resolved_directory")
    if (not output_dir.is_absolute() or output_dir.parent.resolve() != output_dir.parent
            or output_dir.is_relative_to(task_root) or task_root.is_relative_to(output_dir)):
        raise NativeRuntimeError("runtime_custody_must_be_outside_task_with_resolved_parent")
    output_dir.mkdir(mode=0o700)
    output_dir.chmod(0o700)
    plan_digest = seal_capture_json(output_dir, "invocation.json", plan)
    prompt = plan["command"][-1].encode("utf-8")
    fd = os.open(output_dir / "prompt.bin", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        _write_all(fd, prompt)
        os.fsync(fd)
    finally:
        os.close(fd)
    harness = plan["base_subject"]["native_harness_id"]
    directories = ["runtime", "runtime/home"]
    directories += (["runtime/codex", "runtime/codex/sessions", "runtime/codex/log"]
                    if harness == "codex" else ["runtime/claude", "runtime/claude/projects"])
    for relative in directories:
        path = output_dir / relative
        path.mkdir(mode=0o700)
        path.chmod(0o700)
    for relative in reversed(directories):
        _sync_directory(output_dir / relative)
    runtime = output_dir / "runtime"
    receipt = {"schema": "caplab.native-runtime-preparation/v1",
               "invocation_sha256": expected_invocation_sha256,
               "invocation_file_sha256": plan_digest,
               "prompt_sha256": hashlib.sha256(prompt).hexdigest(), "prompt_bytes": len(prompt),
               "custody_root": str(output_dir), "runtime_root": str(runtime),
               "directories": directories,
               "mounts": {"task": {"source": str(task_root), "destination": plan["cwd"], "access": "rw"},
                          "runtime": {"source": str(runtime), "destination": plan["runtime_root"], "access": "rw"}},
               "capture_paths": {name: str(runtime / PurePosixPath(path).relative_to(plan["runtime_root"]))
                                 for name, path in plan["capture_locations"].items()},
               "execution_authorized": False, "binding_complete": False,
               "interpretation": "private host layout prepared; no namespace, native launch, capture or containment verification"}
    seal_capture_json(output_dir, "preparation.json", receipt)
    return receipt
