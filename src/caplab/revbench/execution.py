"""Authorization-gated native revbench execution and evidence capture."""

from __future__ import annotations

import contextlib
import copy
import json
import os
import selectors
import signal
import stat
import struct
import subprocess
import tempfile
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from caplab.runtime.canonical import canonical_json, sha256_hex

from . import _core
from .codex import (
    CodexAdapterError,
    CodexExecutionBundle,
    CodexJSONLTransportError,
    CodexProcessObservation,
    CodexResponseSchemaError,
    build_live_launch_plan,
    credential_memfd,
    derive_codex_response,
    execution_apparatus_receipt,
    normalized_codex_containment_argv,
    response_derivation_document,
    run_codex_process,
    validate_execution_apparatus_receipt,
)
from .custody import (
    FilesystemLiveExecutionRuntime,
    FreshProcessCapture,
    LiveExecutionCustodyError,
    RecoveredProcessCapture,
    live_effect_id,
    live_process_id,
)

_NATIVE_INPUT_INSTRUCTION = (
    "Review the artifact against the requirement and return exactly one JSON object."
)


@dataclass(frozen=True)
class _ProcessObservation:
    started_at: str
    completed_at: str
    stdout: bytes
    stdout_complete: bool
    stderr: bytes
    stderr_complete: bool
    exit_code: int | None
    termination: str


@dataclass(frozen=True)
class _SandboxPlan:
    adapter_path: str
    adapter_bytes: bytes
    executable_path: str
    executable_bytes: bytes


def _static_elf(payload: bytes) -> bool:
    """Return whether payload is an ELF executable without an interpreter."""

    if len(payload) < 64 or payload[:4] != b"\x7fELF":
        return False
    elf_class = payload[4]
    byte_order = payload[5]
    if byte_order == 1:
        endian = "<"
    elif byte_order == 2:
        endian = ">"
    else:
        return False
    try:
        if elf_class == 2:
            header_offset, entry_size_offset, entry_count_offset = 32, 54, 56
            program_type_size = 4
            program_offset = struct.unpack_from(f"{endian}Q", payload, header_offset)[0]
        elif elf_class == 1:
            header_offset, entry_size_offset, entry_count_offset = 28, 42, 44
            program_type_size = 4
            program_offset = struct.unpack_from(f"{endian}I", payload, header_offset)[0]
        else:
            return False
        entry_size = struct.unpack_from(f"{endian}H", payload, entry_size_offset)[0]
        entry_count = struct.unpack_from(f"{endian}H", payload, entry_count_offset)[0]
    except struct.error:
        return False
    if entry_size < program_type_size or entry_count == 0:
        return False
    end = program_offset + entry_size * entry_count
    if end > len(payload):
        return False
    for index in range(entry_count):
        offset = program_offset + index * entry_size
        try:
            program_type = struct.unpack_from(f"{endian}I", payload, offset)[0]
        except struct.error:
            return False
        if program_type in {2, 3}:  # PT_DYNAMIC or PT_INTERP
            return False
    return True


def _sandbox_directories(executable_path: Path) -> list[str]:
    arguments: list[str] = []
    current = Path("/")
    for part in executable_path.parent.parts[1:]:
        current /= part
        arguments.extend(["--dir", str(current)])
    return arguments


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _terminate_group(process: subprocess.Popen[bytes]) -> None:
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


def _run_process(
    argv: Sequence[str],
    stdin: bytes,
    *,
    timeout_seconds: float,
    stdout_limit: int,
    stderr_limit: int,
    environment: Mapping[str, str],
    sandbox: _SandboxPlan,
) -> _ProcessObservation:
    started_at = _timestamp()
    with tempfile.TemporaryDirectory(prefix="caplab-revbench-") as directory:
        if not argv or argv[0] != sandbox.executable_path:
            raise _core.RevbenchContractError(
                "process command does not use the sealed executable"
            )
        private_directory = Path(directory)
        executable_copy = private_directory / "executable"
        executable_copy.write_bytes(sandbox.executable_bytes)
        executable_copy.chmod(0o700)
        try:
            current_adapter_bytes = Path(sandbox.adapter_path).read_bytes()
        except OSError as error:
            raise _core.RevbenchContractError(
                "sandbox adapter became unreadable before process launch"
            ) from error
        if current_adapter_bytes != sandbox.adapter_bytes:
            raise _core.RevbenchContractError(
                "sandbox adapter bytes changed before process launch"
            )
        executable_path = Path(sandbox.executable_path)
        contained_argv = [
            sandbox.adapter_path,
            "--die-with-parent",
            "--unshare-all",
            "--tmpfs",
            "/",
            "--dir",
            "/work",
            "--proc",
            "/proc",
            "--dev",
            "/dev",
            *_sandbox_directories(executable_path),
            "--ro-bind",
            str(executable_copy),
            str(executable_path),
            "--remount-ro",
            "/",
            "--tmpfs",
            "/work",
            "--chdir",
            "/work",
        ]
        contained_argv.extend(["--", *argv])
        try:
            process = subprocess.Popen(
                contained_argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=directory,
                shell=False,
                start_new_session=True,
                env=dict(environment),
            )
        except OSError:
            return _ProcessObservation(
                started_at,
                _timestamp(),
                b"",
                True,
                b"",
                True,
                None,
                "spawn-failure",
            )
        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None
        selector = selectors.DefaultSelector()
        output_streams = {
            process.stdout.fileno(): (process.stdout, "stdout", stdout_limit),
            process.stderr.fileno(): (process.stderr, "stderr", stderr_limit),
        }
        for stream, name, limit in output_streams.values():
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, (name, limit))
        os.set_blocking(process.stdin.fileno(), False)
        selector.register(process.stdin, selectors.EVENT_WRITE, ("stdin", len(stdin)))
        stdin_view = memoryview(stdin)
        stdin_position = 0
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        complete = {"stdout": True, "stderr": True}
        termination = "exited"
        deadline = time.monotonic() + timeout_seconds
        killed = False
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0 and not killed:
                termination = "timeout"
                killed = True
                _terminate_group(process)
            events = selector.select(
                max(0.0, min(remaining, 0.1)) if not killed else 0.1
            )
            for key, _ in events:
                name, limit = key.data
                if name == "stdin":
                    try:
                        written = os.write(key.fd, stdin_view[stdin_position:])
                    except BlockingIOError:
                        written = 0
                    except BrokenPipeError:
                        written = 0
                        try:
                            selector.unregister(key.fileobj)
                        except KeyError:
                            pass
                        key.fileobj.close()
                    stdin_position += written
                    if not key.fileobj.closed and stdin_position == len(stdin):
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                    continue
                stream, _, _ = output_streams[key.fd]
                try:
                    chunk = os.read(key.fd, 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(stream)
                    stream.close()
                    continue
                available = max(0, limit - len(buffers[name]))
                buffers[name].extend(chunk[:available])
                if len(chunk) > available:
                    complete[name] = False
                    if termination == "exited":
                        termination = f"{name}-limit"
                    if not killed:
                        killed = True
                        _terminate_group(process)
            if killed and process.poll() is not None and not events:
                for stream, _, _ in output_streams.values():
                    if not stream.closed:
                        try:
                            selector.unregister(stream)
                        except KeyError:
                            pass
                        stream.close()
                break
        selector.close()
        try:
            exit_code = process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            _terminate_group(process)
            exit_code = process.wait()
        if termination == "exited" and exit_code != 0:
            termination = "exited"
        return _ProcessObservation(
            started_at,
            _timestamp(),
            bytes(buffers["stdout"]),
            complete["stdout"],
            bytes(buffers["stderr"]),
            complete["stderr"],
            exit_code,
            termination,
        )


def _execution_environment(
    binding: Mapping[str, Any], registrar: _core.ArtifactRegistrar
) -> tuple[dict[str, str], _SandboxPlan]:
    runtime = _core._parse_canonical_json_ref(
        binding["configuration"]["runtime_ref"],
        registrar,
        "binding.configuration.runtime_ref",
    )
    runtime = _core._object(
        runtime,
        "binding.configuration.runtime_ref document",
        {
            "schema_version",
            "executable_path",
            "environment_keys",
            "working_directory",
            "network_mode",
            "stdin_mode",
            "stdout_mode",
            "executable_format",
        },
    )
    _core._const(
        runtime["schema_version"],
        "caplab-revbench-execution-runtime/1",
        "binding.configuration.runtime_ref document.schema_version",
    )
    executable_path = Path(
        _core._string(
            runtime["executable_path"],
            "binding.configuration.runtime_ref document.executable_path",
        )
    )
    if not executable_path.is_absolute():
        _core._fail(
            "binding.configuration.runtime_ref", "executable path must be absolute"
        )
    try:
        metadata = executable_path.lstat()
    except OSError as error:
        raise _core.RevbenchContractError("sealed executable is unavailable") from error
    if not stat.S_ISREG(metadata.st_mode):
        _core._fail(
            "binding.configuration.runtime_ref",
            "executable must be a real regular file",
        )
    command = _core._parse_canonical_json_ref(
        binding["harness"]["command_ref"], registrar, "binding.harness.command_ref"
    )
    probe = _core._parse_canonical_json_ref(
        binding["harness"]["version_probe_ref"],
        registrar,
        "binding.harness.version_probe_ref",
    )
    version_command = _core._parse_canonical_json_ref(
        probe["command_ref"],
        registrar,
        "binding.harness.version_probe_ref document.command_ref",
    )
    for path, argv in (
        ("command", command["argv"]),
        ("version command", version_command["argv"]),
    ):
        if not argv or argv[0] != str(executable_path):
            _core._fail(
                f"binding {path}", "does not use the sealed absolute executable"
            )
    executable_ref = binding["harness"]["executable_ref"]
    if executable_ref is None:
        _core._fail(
            "binding.harness.executable_ref",
            "is required for CAPLAB-owned execution",
        )
    expected_bytes = _core._resolve_ref(
        executable_ref, registrar, "binding.harness.executable_ref"
    )
    try:
        observed_bytes = executable_path.read_bytes()
    except OSError as error:
        raise _core.RevbenchContractError("sealed executable is unreadable") from error
    if observed_bytes != expected_bytes:
        _core._fail("binding.harness.executable_ref", "does not match executable bytes")
    if metadata.st_mode & 0o111 == 0:
        _core._fail("binding.harness.executable_ref", "executable mode is absent")
    _core._const(
        runtime["executable_format"],
        "static-elf",
        "binding.configuration.runtime_ref document.executable_format",
    )
    if not _static_elf(expected_bytes):
        _core._fail(
            "binding.harness.executable_ref",
            "must be a self-contained static ELF executable",
        )
    _core._const(
        runtime["working_directory"],
        "temporary-empty",
        "binding.configuration.runtime_ref document.working_directory",
    )
    _core._const(
        runtime["network_mode"],
        "not-required",
        "binding.configuration.runtime_ref document.network_mode",
    )
    _core._const(
        runtime["stdin_mode"],
        "canonical-json",
        "binding.configuration.runtime_ref document.stdin_mode",
    )
    _core._const(
        runtime["stdout_mode"],
        "single-json",
        "binding.configuration.runtime_ref document.stdout_mode",
    )
    keys = _core._array(
        runtime["environment_keys"],
        "binding.configuration.runtime_ref document.environment_keys",
    )
    for index, key in enumerate(keys):
        _core._string(
            key, f"binding.configuration.runtime_ref document.environment_keys[{index}]"
        )
        if "=" in key:
            _core._fail(
                "binding.configuration.runtime_ref document.environment_keys",
                "contains an invalid name",
            )
    _core._sorted_unique(
        keys, "binding.configuration.runtime_ref document.environment_keys"
    )
    if keys:
        _core._fail(
            "binding.configuration.runtime_ref document.environment_keys",
            "must be empty in the sealed local-fixture profile",
        )
    inference = _core._parse_canonical_json_ref(
        binding["configuration"]["inference_ref"],
        registrar,
        "binding.configuration.inference_ref",
    )
    inference = _core._object(
        inference,
        "binding.configuration.inference_ref document",
        {"schema_version", "command_ref"},
    )
    _core._const(
        inference["schema_version"],
        "caplab-revbench-inference/1",
        "binding.configuration.inference_ref document.schema_version",
    )
    if canonical_json(inference["command_ref"]) != canonical_json(
        binding["harness"]["command_ref"]
    ):
        _core._fail(
            "binding.configuration.inference_ref", "does not bind the native command"
        )
    instructions = _core._parse_canonical_json_ref(
        binding["configuration"]["instructions_ref"],
        registrar,
        "binding.configuration.instructions_ref",
    )
    instructions = _core._object(
        instructions,
        "binding.configuration.instructions_ref document",
        {"schema_version", "instruction"},
    )
    _core._const(
        instructions["schema_version"],
        "caplab-revbench-instructions/1",
        "binding.configuration.instructions_ref document.schema_version",
    )
    _core._const(
        instructions["instruction"],
        _NATIVE_INPUT_INSTRUCTION,
        "binding.configuration.instructions_ref document.instruction",
    )
    for surface in ("knowledge", "tools"):
        disabled = _core._parse_canonical_json_ref(
            binding["configuration"][f"{surface}_ref"],
            registrar,
            f"binding.configuration.{surface}_ref",
        )
        disabled = _core._object(
            disabled,
            f"binding.configuration.{surface}_ref document",
            {"schema_version", "surface", "mode"},
        )
        _core._const(
            disabled["schema_version"],
            "caplab-revbench-disabled-surface/1",
            f"binding.configuration.{surface}_ref document.schema_version",
        )
        _core._const(
            disabled["surface"],
            surface,
            f"binding.configuration.{surface}_ref document.surface",
        )
        _core._const(
            disabled["mode"],
            "none",
            f"binding.configuration.{surface}_ref document.mode",
        )
    permissions = _core._parse_canonical_json_ref(
        binding["configuration"]["permissions_ref"],
        registrar,
        "binding.configuration.permissions_ref",
    )
    permissions = _core._object(
        permissions,
        "binding.configuration.permissions_ref document",
        {"schema_version", "environment_keys", "filesystem_mode", "network_mode"},
    )
    _core._const(
        permissions["schema_version"],
        "caplab-revbench-execution-permissions/1",
        "binding.configuration.permissions_ref document.schema_version",
    )
    _core._const(
        permissions["filesystem_mode"],
        "read-only-root-private-cwd",
        "binding.configuration.permissions_ref document.filesystem_mode",
    )
    if canonical_json(permissions["environment_keys"]) != canonical_json(keys):
        _core._fail(
            "binding.configuration.permissions_ref document.environment_keys",
            "does not match runtime allowlist",
        )
    if permissions["network_mode"] != runtime["network_mode"]:
        _core._fail(
            "binding.configuration.permissions_ref document.network_mode",
            "does not match runtime",
        )
    sandbox_document = _core._parse_canonical_json_ref(
        binding["configuration"]["sandbox_ref"],
        registrar,
        "binding.configuration.sandbox_ref",
    )
    sandbox_document = _core._object(
        sandbox_document,
        "binding.configuration.sandbox_ref document",
        {
            "schema_version",
            "adapter_path",
            "adapter_ref",
            "root_filesystem",
            "working_directory",
            "network_mode",
        },
    )
    _core._const(
        sandbox_document["schema_version"],
        "caplab-revbench-execution-sandbox/1",
        "binding.configuration.sandbox_ref document.schema_version",
    )
    _core._const(
        sandbox_document["root_filesystem"],
        "read-only",
        "binding.configuration.sandbox_ref document.root_filesystem",
    )
    _core._const(
        sandbox_document["working_directory"],
        "private-write",
        "binding.configuration.sandbox_ref document.working_directory",
    )
    if sandbox_document["network_mode"] != runtime["network_mode"]:
        _core._fail(
            "binding.configuration.sandbox_ref document.network_mode",
            "does not match runtime",
        )
    adapter_path = Path(
        _core._string(
            sandbox_document["adapter_path"],
            "binding.configuration.sandbox_ref document.adapter_path",
        )
    )
    if not adapter_path.is_absolute():
        _core._fail(
            "binding.configuration.sandbox_ref document.adapter_path",
            "must be absolute",
        )
    try:
        adapter_metadata = adapter_path.lstat()
        adapter_bytes = adapter_path.read_bytes()
    except OSError as error:
        raise _core.RevbenchContractError("sandbox adapter is unavailable") from error
    if not stat.S_ISREG(adapter_metadata.st_mode):
        _core._fail(
            "binding.configuration.sandbox_ref document.adapter_path",
            "must be a real regular file",
        )
    adapter_ref = _core._validate_content_ref(
        sandbox_document["adapter_ref"],
        "binding.configuration.sandbox_ref document.adapter_ref",
        kind="sandbox-executable",
        schema="caplab-native-executable/1",
    )
    if adapter_bytes != _core._resolve_ref(
        adapter_ref,
        registrar,
        "binding.configuration.sandbox_ref document.adapter_ref",
    ):
        _core._fail(
            "binding.configuration.sandbox_ref document.adapter_ref",
            "does not match adapter bytes",
        )
    if adapter_metadata.st_mode & 0o111 == 0:
        _core._fail(
            "binding.configuration.sandbox_ref document.adapter_ref",
            "executable mode is absent",
        )
    environment: dict[str, str] = {}
    return environment, _SandboxPlan(
        str(adapter_path), adapter_bytes, str(executable_path), expected_bytes
    )


def _registered_bytes(
    registrar: _core.ArtifactRegistrar,
    payload: bytes,
    *,
    kind: str,
    schema: str,
    registration_id: str,
) -> dict[str, Any]:
    register = getattr(registrar, "register_bytes", None)
    if register is None:
        raise _core.RevbenchContractError(
            "execution registrar cannot register raw bytes"
        )
    try:
        returned = register(
            payload,
            kind=kind,
            schema=schema,
            media_type="application/octet-stream",
            registration_id=registration_id,
        )
    except Exception as error:
        raise _core.RevbenchContractError(
            f"registration {registration_id!r} failed"
        ) from error
    ref = _core._validate_content_ref(
        returned,
        f"registration {registration_id!r}",
        kind=kind,
        schema=schema,
    )
    if (
        _core._resolve_ref(ref, registrar, f"registration {registration_id!r}")
        != payload
    ):
        _core._fail(f"registration {registration_id!r}", "returned different bytes")
    return copy.deepcopy(dict(ref))


def _registered_document(
    registrar: _core.ArtifactRegistrar,
    document: Mapping[str, Any],
    *,
    kind: str,
    schema: str,
    registration_id: str,
) -> dict[str, Any]:
    return _core._verified_registration(
        registrar,
        copy.deepcopy(dict(document)),
        kind=kind,
        schema=schema,
        registration_id=registration_id,
    )


def _content_id(document: Mapping[str, Any], field: str, prefix: str) -> str:
    identity = copy.deepcopy(dict(document))
    identity.pop(field, None)
    return prefix + sha256_hex(canonical_json(identity))


def _process_refs(
    registrar: _core.ArtifactRegistrar,
    observation: _ProcessObservation,
    *,
    label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    stdout_ref = _registered_bytes(
        registrar,
        observation.stdout,
        kind="native-process-stdout",
        schema="caplab-native-process-stream/1",
        registration_id=f"{label}-stdout",
    )
    stderr_ref = _registered_bytes(
        registrar,
        observation.stderr,
        kind="native-process-stderr",
        schema="caplab-native-process-stream/1",
        registration_id=f"{label}-stderr",
    )
    return stdout_ref, stderr_ref


def _parse_response(payload: bytes) -> dict[str, Any] | None:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate response key")
            result[key] = value
        return result

    try:
        response = json.loads(payload, object_pairs_hook=unique)
    except (UnicodeError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(response, dict) or set(response) != {
        "schema_version",
        "verdict",
        "anchors",
    }:
        return None
    if response["schema_version"] != "caplab-revbench-native-response/1":
        return None
    verdict = response["verdict"]
    anchors = response["anchors"]
    if verdict not in {"clean", "defect"} or not isinstance(anchors, list):
        return None
    try:
        for index, anchor in enumerate(anchors):
            _core._pointer(anchor, f"native response.anchors[{index}]")
        _core._sorted_unique(anchors, "native response.anchors")
    except _core.RevbenchContractError:
        return None
    if (verdict == "clean" and anchors) or (verdict == "defect" and not anchors):
        return None
    return response


def _remaining_timeout(
    authorization: Mapping[str, Any],
    total_deadline: float,
) -> tuple[float, str | None]:
    per_process = authorization["limits"]["timeout_seconds_per_process"]
    remaining_total = total_deadline - time.monotonic()
    valid_until = datetime.strptime(
        authorization["valid_until"], "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=UTC)
    remaining_authority = (valid_until - datetime.now(UTC)).total_seconds()
    remaining, deadline_reason = min(
        (
            (float(per_process), None),
            (remaining_total, "timeout"),
            (remaining_authority, "authorization-expired"),
        ),
        key=lambda candidate: candidate[0],
    )
    if remaining <= 0:
        return 0, deadline_reason or "timeout"
    return remaining, deadline_reason


def _deadline_termination(
    observation: _ProcessObservation, deadline_reason: str | None
) -> _ProcessObservation:
    if observation.termination != "timeout" or deadline_reason is None:
        return observation
    return _ProcessObservation(
        observation.started_at,
        observation.completed_at,
        observation.stdout,
        observation.stdout_complete,
        observation.stderr,
        observation.stderr_complete,
        observation.exit_code,
        deadline_reason,
    )


def _live_bundle(
    binding: Mapping[str, Any],
    apparatus_ref: Mapping[str, Any],
    registrar: _core.ArtifactRegistrar,
) -> tuple[
    CodexExecutionBundle,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    runtime_ref = binding["configuration"]["runtime_ref"]
    runtime = _core._parse_canonical_json_ref(
        runtime_ref, registrar, "binding.configuration.runtime_ref"
    )
    profile_ref = runtime["credential_profile_ref"]
    profile = _core._parse_canonical_json_ref(
        profile_ref,
        registrar,
        "binding.configuration.runtime_ref document.credential_profile_ref",
    )
    command = _core._parse_canonical_json_ref(
        binding["harness"]["command_ref"], registrar, "binding.harness.command_ref"
    )
    probe = _core._parse_canonical_json_ref(
        binding["harness"]["version_probe_ref"],
        registrar,
        "binding.harness.version_probe_ref",
    )
    version_command = _core._parse_canonical_json_ref(
        probe["command_ref"],
        registrar,
        "binding.harness.version_probe_ref document.command_ref",
    )
    adapter_runtime = runtime["adapter_runtime_refs"]
    bundle = CodexExecutionBundle(
        runtime_ref_sha256=runtime_ref["sha256"],
        apparatus_sha256=apparatus_ref["sha256"],
        review_command_ref_sha256=binding["harness"]["command_ref"]["sha256"],
        version_command_ref_sha256=probe["command_ref"]["sha256"],
        credential_profile_id=profile["profile_id"],
        credential_profile_sha256=profile_ref["sha256"],
        executable=_core._resolve_ref(
            runtime["executable_ref"], registrar, "live runtime executable_ref"
        ),
        adapter=_core._resolve_ref(
            runtime["sandbox_adapter_ref"],
            registrar,
            "live runtime sandbox_adapter_ref",
        ),
        adapter_loader=_core._resolve_ref(
            adapter_runtime["loader_ref"],
            registrar,
            "live runtime adapter loader_ref",
        ),
        adapter_libraries=tuple(
            (
                member["name"],
                _core._resolve_ref(
                    member["ref"],
                    registrar,
                    f"live runtime library:{member['name']}",
                ),
            )
            for member in adapter_runtime["library_refs"]
        ),
        ca_certificates=_core._resolve_ref(
            runtime["ca_certificates_ref"],
            registrar,
            "live runtime ca_certificates_ref",
        ),
        resolver=_core._resolve_ref(
            runtime["resolver_ref"], registrar, "live runtime resolver_ref"
        ),
        nsswitch=_core._resolve_ref(
            runtime["nsswitch_ref"], registrar, "live runtime nsswitch_ref"
        ),
        response_schema=_core._resolve_ref(
            runtime["response_schema_ref"],
            registrar,
            "live runtime response_schema_ref",
        ),
        environment=dict(runtime["environment"]),
    )
    return bundle, profile, command, {**dict(probe), "command": version_command}


def _live_effect_scope(
    manifest: Mapping[str, Any],
    authorization: Mapping[str, Any],
    case_id: str,
    arm: str,
    assignment_index: int,
    process_kind: str,
) -> dict[str, Any]:
    return {
        "schema_version": "caplab-revbench-live-effect-scope/1",
        "manifest_sha256": authorization["manifest_ref"]["sha256"],
        "experiment_id": manifest["experiment_id"],
        "binding_id": manifest["binding"]["binding_id"],
        "case_id": case_id,
        "arm": arm,
        "assignment_index": assignment_index,
        "process_kind": process_kind,
    }


def _recovered_observation(
    capture: RecoveredProcessCapture,
) -> CodexProcessObservation:
    if capture.completion is not None:
        completion = capture.completion
        return CodexProcessObservation(
            completion["launch_attempted_at"],
            completion["process_started_at"],
            completion["process_completed_at"],
            completion["completion_recorded_at"],
            capture.stdout,
            completion["stdout_complete"],
            capture.stderr,
            completion["stderr_complete"],
            completion["exit_code"],
            completion["termination"],
            completion["invocation_state"],
        )
    assert capture.recovery is not None
    recovery = capture.recovery
    return CodexProcessObservation(
        None,
        recovery["process_started_at"],
        recovery["process_completed_at"],
        recovery["recovered_at"],
        capture.stdout,
        False,
        capture.stderr,
        False,
        None,
        capture.termination,
        "uncertain",
    )


def _complete_without_launch(
    capture: FreshProcessCapture, termination: str
) -> CodexProcessObservation:
    recorded_at = _timestamp()
    observation = CodexProcessObservation(
        None,
        None,
        None,
        recorded_at,
        b"",
        True,
        b"",
        True,
        None,
        termination,
        "not-invoked",
    )
    capture.complete(
        {
            "schema_version": "caplab-revbench-live-process-completion/1",
            "process_id": capture.intent["process_id"],
            "launch_attempted_at": None,
            "process_started_at": None,
            "process_completed_at": None,
            "completion_recorded_at": recorded_at,
            "stdout_complete": True,
            "stderr_complete": True,
            "exit_code": None,
            "termination": termination,
            "invocation_state": "not-invoked",
        }
    )
    return observation


def _live_process_refs(
    registrar: _core.ArtifactRegistrar,
    observation: CodexProcessObservation,
    *,
    label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        _registered_bytes(
            registrar,
            observation.stdout,
            kind="native-process-stdout",
            schema="caplab-native-process-stream/1",
            registration_id=f"{label}-stdout",
        ),
        _registered_bytes(
            registrar,
            observation.stderr,
            kind="native-process-stderr",
            schema="caplab-native-process-stream/1",
            registration_id=f"{label}-stderr",
        ),
    )


def _terminal_custody_capture(
    session: Any,
    launch_plan: Mapping[str, Any],
    capture: FreshProcessCapture | RecoveredProcessCapture,
) -> RecoveredProcessCapture:
    """Reload the terminal custody record instead of trusting runner projections."""

    if isinstance(capture, RecoveredProcessCapture):
        return capture
    retained = session.claim_process(launch_plan)
    if not isinstance(retained, RecoveredProcessCapture):
        raise LiveExecutionCustodyError("process_completion_not_durable")
    return retained


def _registered_process_receipt(
    registrar: _core.ArtifactRegistrar,
    *,
    execution_intent_ref: Mapping[str, Any],
    sequence_index: int,
    capture: RecoveredProcessCapture,
    stdout_ref: Mapping[str, Any] | None,
    stderr_ref: Mapping[str, Any] | None,
    recovery_ref: Mapping[str, Any] | None,
    stream_disposition: str = "registered",
) -> dict[str, Any]:
    """Register exact custody state linking one process to its launch plan."""

    source = capture.completion if capture.completion is not None else capture.recovery
    if source is None:
        raise LiveExecutionCustodyError("process_terminal_record_missing")
    if capture.completion is not None:
        launch_attempted_at = source["launch_attempted_at"]
        process_started_at = source["process_started_at"]
        process_completed_at = source["process_completed_at"]
        completion_recorded_at = source["completion_recorded_at"]
        exit_code = source["exit_code"]
        stdout_complete = source["stdout_complete"]
        stderr_complete = source["stderr_complete"]
    else:
        launch_attempted_at = None
        process_started_at = source["process_started_at"]
        process_completed_at = source["process_completed_at"]
        completion_recorded_at = source["recovered_at"]
        exit_code = None
        stdout_complete = False
        stderr_complete = False
    if stream_disposition not in {"registered", "privacy-quarantined"}:
        raise LiveExecutionCustodyError("process_stream_disposition_invalid")
    if stream_disposition == "registered":
        if stdout_ref is None or stderr_ref is None:
            raise LiveExecutionCustodyError("process_stream_reference_missing")
    elif stdout_ref is not None or stderr_ref is not None:
        raise LiveExecutionCustodyError("quarantined_process_stream_published")
    receipt: dict[str, Any] = {
        "schema_version": "caplab-revbench-live-process-receipt/1",
        "receipt_id": "",
        "execution_intent_ref": copy.deepcopy(dict(execution_intent_ref)),
        "sequence_index": sequence_index,
        "authorization_id": capture.intent["authorization_id"],
        "effect_id": capture.intent["effect_id"],
        "process_id": capture.intent["process_id"],
        "intent_recorded_at": capture.intent["intent_recorded_at"],
        "launch_plan": copy.deepcopy(capture.intent["launch_plan"]),
        "launch_attempted_at": launch_attempted_at,
        "containment_process_started_at": process_started_at,
        "containment_process_completed_at": process_completed_at,
        "completion_recorded_at": completion_recorded_at,
        "outer_launch_state": capture.invocation_state,
        "termination": capture.termination,
        "exit_code": exit_code,
        "stream_disposition": stream_disposition,
        "stdout_sha256": source["stdout_sha256"],
        "stdout_byte_count": source["stdout_byte_count"],
        "stdout_ref": None if stdout_ref is None else copy.deepcopy(dict(stdout_ref)),
        "stdout_complete": stdout_complete,
        "stderr_sha256": source["stderr_sha256"],
        "stderr_byte_count": source["stderr_byte_count"],
        "stderr_ref": None if stderr_ref is None else copy.deepcopy(dict(stderr_ref)),
        "stderr_complete": stderr_complete,
        "recovery_ref": None
        if recovery_ref is None
        else copy.deepcopy(dict(recovery_ref)),
    }
    receipt["receipt_id"] = _content_id(receipt, "receipt_id", "live-process-receipt-")
    return _registered_document(
        registrar,
        receipt,
        kind="live-process-receipt",
        schema="caplab-revbench-live-process-receipt/1",
        registration_id=receipt["receipt_id"],
    )


def _execute_live_codex(
    manifest: Mapping[str, Any],
    execution_authorization_ref: Mapping[str, Any],
    authorization: Mapping[str, Any],
    registrar: _core.ArtifactRegistrar,
    runtime: FilesystemLiveExecutionRuntime,
    started_at: str,
    started_monotonic: float,
) -> dict[str, Any]:
    """Execute the one pinned Codex provider slice under one-shot custody."""

    if runtime.custody_domain_id != authorization["custody_domain_id"]:
        raise _core.RevbenchContractError(
            "live execution custody domain does not match explicit authorization"
        )
    execution_identity = {
        "schema_version": "caplab-revbench-live-execution-identity/1",
        "authorization_id": authorization["authorization_id"],
        "manifest_sha256": authorization["manifest_ref"]["sha256"],
        "experiment_id": manifest["experiment_id"],
        "binding_id": manifest["binding"]["binding_id"],
        "custody_domain_id": authorization["custody_domain_id"],
    }
    retained_execution_intent = runtime.retained_execution_intent(execution_identity)
    if retained_execution_intent is None:
        # Time gates authorize only a fresh provider-effect intent.  A retained
        # intent is recovered and sealed without renewing or extending it.
        _core._validate_execution_authorization(
            execution_authorization_ref,
            manifest,
            registrar,
            observed_at=started_at,
        )
        try:
            apparatus = copy.deepcopy(dict(execution_apparatus_receipt()))
        except (TypeError, ValueError, CodexAdapterError) as error:
            raise _core.RevbenchContractError(
                "live execution apparatus could not be identified"
            ) from error
        try:
            apparatus = validate_execution_apparatus_receipt(apparatus)
        except CodexAdapterError as error:
            raise _core.RevbenchContractError(
                "live execution apparatus is invalid"
            ) from error
        apparatus_id = apparatus["apparatus_id"]
        apparatus_ref = _registered_document(
            registrar,
            apparatus,
            kind="execution-apparatus-receipt",
            schema="caplab-revbench-execution-apparatus/1",
            registration_id=apparatus_id,
        )
    else:
        apparatus_ref = copy.deepcopy(retained_execution_intent["apparatus_ref"])
    if canonical_json(apparatus_ref) != canonical_json(authorization["apparatus_ref"]):
        raise _core.RevbenchContractError(
            "live execution apparatus does not match explicit authorization"
        )
    bundle, credential_profile, command, probe = _live_bundle(
        manifest["binding"], apparatus_ref, registrar
    )
    expected_version_stdout = _core._resolve_ref(
        probe["stdout_ref"], registrar, "live expected version stdout"
    )
    expected_version_stderr = _core._resolve_ref(
        probe["stderr_ref"], registrar, "live expected version stderr"
    )
    limits = authorization["limits"]
    if retained_execution_intent is None:
        monotonic_execution_deadline = started_monotonic + limits["total_wall_seconds"]
        started = datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=UTC
        )
        authorization_deadline = datetime.strptime(
            authorization["valid_until"], "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=UTC)
        deadline = min(
            authorization_deadline,
            started + timedelta(seconds=limits["total_wall_seconds"]),
        )
        execution_deadline_at = deadline.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        monotonic_execution_deadline = None
        execution_deadline_at = retained_execution_intent["execution_deadline_at"]

    assignments: list[dict[str, Any]] = []
    plans: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        for assignment_index, arm in enumerate(case["assignment_order"]):
            native_input = {
                "schema_version": "caplab-revbench-native-input/1",
                "instruction": _NATIVE_INPUT_INSTRUCTION,
                "requirement": copy.deepcopy(case["oracle"]),
                "artifact": copy.deepcopy(case[arm]["content"]),
                "response_schema_version": "caplab-revbench-native-response/1",
            }
            input_ref = _registered_document(
                registrar,
                native_input,
                kind="native-input",
                schema="caplab-revbench-native-input/1",
                registration_id=(
                    f"live-input-{manifest['experiment_id']}-{case['case_id']}-{arm}"
                ),
            )
            stdin = canonical_json(native_input)
            stdin_ref = _registered_bytes(
                registrar,
                stdin,
                kind="native-process-stdin",
                schema="caplab-native-process-stream/1",
                registration_id=(
                    f"live-stdin-{manifest['experiment_id']}-{case['case_id']}-{arm}"
                ),
            )
            prompt = {
                "schema_version": "caplab-revbench-prompt/1",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": manifest["binding"]["binding_id"],
                "protocol_ref": copy.deepcopy(manifest["protocol"]),
                "rendered_input_ref": input_ref,
            }
            prompt_ref = _registered_document(
                registrar,
                prompt,
                kind="prompt",
                schema="caplab-revbench-prompt/1",
                registration_id=(
                    f"live-prompt-{manifest['experiment_id']}-{case['case_id']}-{arm}"
                ),
            )
            version_scope = _live_effect_scope(
                manifest,
                authorization,
                case["case_id"],
                arm,
                assignment_index,
                "version-probe",
            )
            version_plan = build_live_launch_plan(
                version_scope,
                logical_argv=probe["command"]["argv"],
                normalized_containment_argv=normalized_codex_containment_argv(
                    probe["command"]["argv"]
                ),
                stdin=b"",
                contained_environment={},
                runtime_ref_sha256=bundle.runtime_ref_sha256,
                apparatus_sha256=bundle.apparatus_sha256,
                command_ref_sha256=bundle.version_command_ref_sha256,
                credential_profile_id=bundle.credential_profile_id,
                credential_profile_sha256=bundle.credential_profile_sha256,
                timeout_seconds=limits["timeout_seconds_per_process"],
                execution_deadline_at=execution_deadline_at,
                stdout_limit=limits["max_stdout_bytes_per_process"],
                stderr_limit=limits["max_stderr_bytes_per_process"],
            )
            native_scope = _live_effect_scope(
                manifest,
                authorization,
                case["case_id"],
                arm,
                assignment_index,
                "native-review",
            )
            native_plan = build_live_launch_plan(
                native_scope,
                logical_argv=command["argv"],
                normalized_containment_argv=normalized_codex_containment_argv(
                    command["argv"]
                ),
                stdin=stdin,
                contained_environment=bundle.environment,
                runtime_ref_sha256=bundle.runtime_ref_sha256,
                apparatus_sha256=bundle.apparatus_sha256,
                command_ref_sha256=bundle.review_command_ref_sha256,
                credential_profile_id=bundle.credential_profile_id,
                credential_profile_sha256=bundle.credential_profile_sha256,
                timeout_seconds=limits["timeout_seconds_per_process"],
                execution_deadline_at=execution_deadline_at,
                stdout_limit=limits["max_stdout_bytes_per_process"],
                stderr_limit=limits["max_stderr_bytes_per_process"],
            )
            plans.extend((version_plan, native_plan))
            assignments.append(
                {
                    "case": case,
                    "arm": arm,
                    "assignment_index": assignment_index,
                    "stdin": stdin,
                    "stdin_ref": stdin_ref,
                    "prompt_ref": prompt_ref,
                }
            )

    process_sequence = [
        {
            "effect_id": live_effect_id(plan["effect_scope"]),
            "process_id": live_process_id(plan),
            "launch_plan": plan,
        }
        for plan in plans
    ]
    execution_intent = {
        "schema_version": "caplab-revbench-live-execution-intent/1",
        "authorization_id": authorization["authorization_id"],
        "manifest_sha256": authorization["manifest_ref"]["sha256"],
        "experiment_id": manifest["experiment_id"],
        "binding_id": manifest["binding"]["binding_id"],
        "custody_domain_id": authorization["custody_domain_id"],
        "apparatus_ref": apparatus_ref,
        "intent_recorded_at": started_at,
        "execution_deadline_at": execution_deadline_at,
        "process_sequence": process_sequence,
    }
    attempts: list[dict[str, Any]] = []
    stop_reason: str | None = None
    with (
        runtime.claim_or_resume_execution(
            execution_identity,
            fresh_intent=(
                execution_intent if retained_execution_intent is None else None
            ),
        ) as session,
        contextlib.ExitStack() as credential_stack,
    ):
        if canonical_json(apparatus_ref) != canonical_json(
            session.intent["apparatus_ref"]
        ):
            # Another executor may have won the fresh-claim race.  Recovery is
            # tied exclusively to its durable apparatus and launch sequence.
            apparatus_ref = copy.deepcopy(session.intent["apparatus_ref"])
            bundle, credential_profile, command, probe = _live_bundle(
                manifest["binding"], apparatus_ref, registrar
            )
            expected_version_stdout = _core._resolve_ref(
                probe["stdout_ref"], registrar, "live expected version stdout"
            )
            expected_version_stderr = _core._resolve_ref(
                probe["stderr_ref"], registrar, "live expected version stderr"
            )
        execution_intent_ref = _registered_document(
            registrar,
            session.intent,
            kind="live-execution-intent",
            schema="caplab-revbench-live-execution-intent/1",
            registration_id=(
                "live-execution-intent-" + sha256_hex(canonical_json(session.intent))
            ),
        )
        if session.sealed is not None:
            return copy.deepcopy(session.sealed)
        retained_plans = session.declared_launch_plans()
        retained_by_scope = {
            (
                plan["effect_scope"]["case_id"],
                plan["effect_scope"]["arm"],
                plan["effect_scope"]["process_kind"],
            ): plan
            for plan in retained_plans
        }
        sequence_index_by_process = {
            entry["process_id"]: index
            for index, entry in enumerate(session.intent["process_sequence"])
        }
        process_receipt_refs: list[dict[str, Any]] = []
        credential = None
        if not session.resumed:
            try:
                source = runtime.credential_source(bundle.credential_profile_id)
                if runtime.credential_root is None:
                    raise LiveExecutionCustodyError("credential_root_required")
                credential = credential_stack.enter_context(
                    credential_memfd(
                        source,
                        credential_profile,
                        credential_root=runtime.credential_root,
                    )
                )
            except (CodexAdapterError, LiveExecutionCustodyError):
                # The overall one-shot intent is already durable.  Refuse and
                # seal it before any version or provider-capable subprocess so
                # rotating a malformed credential cannot replay this slot.
                stop_reason = "preflight-refused"

        for assignment in assignments if stop_reason is None else ():
            case = assignment["case"]
            arm = assignment["arm"]
            assignment_index = assignment["assignment_index"]
            version_plan = retained_by_scope[(case["case_id"], arm, "version-probe")]
            try:
                version_capture = session.claim_process(version_plan)
            except LiveExecutionCustodyError as error:
                if session.resumed and "recovery_cannot_launch" in str(error):
                    stop_reason = "executor-interrupted"
                    break
                raise
            if isinstance(version_capture, FreshProcessCapture):
                if monotonic_execution_deadline is None:
                    raise LiveExecutionCustodyError(
                        "live_execution_recovery_cannot_launch"
                    )
                run_codex_process(
                    probe["command"]["argv"],
                    b"",
                    bundle=bundle,
                    capture=version_capture,
                    credential=None,
                    monotonic_deadline=monotonic_execution_deadline,
                )
            version_terminal = _terminal_custody_capture(
                session, version_plan, version_capture
            )
            version_observation = _recovered_observation(version_terminal)
            version_recovery_ref = (
                None
                if version_terminal.recovery is None
                else _registered_document(
                    registrar,
                    version_terminal.recovery,
                    kind="native-process-recovery",
                    schema="caplab-revbench-live-process-recovery/1",
                    registration_id=version_terminal.recovery["process_id"],
                )
            )
            version_stdout_ref, version_stderr_ref = _live_process_refs(
                registrar,
                version_observation,
                label=(
                    f"live-version-{manifest['experiment_id']}-{case['case_id']}-{arm}"
                ),
            )
            version_process_receipt_ref = _registered_process_receipt(
                registrar,
                execution_intent_ref=execution_intent_ref,
                sequence_index=sequence_index_by_process[
                    version_terminal.intent["process_id"]
                ],
                capture=version_terminal,
                stdout_ref=version_stdout_ref,
                stderr_ref=version_stderr_ref,
                recovery_ref=version_recovery_ref,
            )
            process_receipt_refs.append(version_process_receipt_ref)
            matches_expected = (
                version_observation.invocation_state == "invoked"
                and version_observation.termination == "exited"
                and version_observation.exit_code == probe["exit_code"] == 0
                and version_observation.stdout_complete
                and version_observation.stderr_complete
                and version_observation.stdout == expected_version_stdout
                and version_observation.stderr == expected_version_stderr
            )
            version_document: dict[str, Any] = {
                "schema_version": "caplab-live-native-version-observation/1",
                "observation_id": "",
                "execution_authorization_ref": copy.deepcopy(
                    dict(execution_authorization_ref)
                ),
                "apparatus_ref": apparatus_ref,
                "execution_intent_ref": execution_intent_ref,
                "process_receipt_ref": version_process_receipt_ref,
                "experiment_id": manifest["experiment_id"],
                "binding_id": manifest["binding"]["binding_id"],
                "expected_version_probe_ref": copy.deepcopy(
                    manifest["binding"]["harness"]["version_probe_ref"]
                ),
                "command_ref": copy.deepcopy(probe["command_ref"]),
                "intent_recorded_at": version_capture.intent["intent_recorded_at"],
                "launch_attempted_at": version_observation.launch_attempted_at,
                "containment_process_started_at": version_observation.process_started_at,
                "containment_process_completed_at": version_observation.process_completed_at,
                "completion_recorded_at": version_observation.completion_recorded_at,
                "outer_launch_state": version_observation.invocation_state,
                "stdout_ref": version_stdout_ref,
                "stdout_complete": version_observation.stdout_complete,
                "stderr_ref": version_stderr_ref,
                "stderr_complete": version_observation.stderr_complete,
                "exit_code": version_observation.exit_code,
                "termination": version_observation.termination,
                "matches_expected": matches_expected,
                "recovery_ref": version_recovery_ref,
            }
            version_document["observation_id"] = _content_id(
                version_document, "observation_id", "live-version-observation-"
            )
            version_observation_ref = _registered_document(
                registrar,
                version_document,
                kind="live-native-version-observation",
                schema="caplab-live-native-version-observation/1",
                registration_id=version_document["observation_id"],
            )

            # A recovered uncertain version probe has no durable completion.
            # Claiming its paired native review would either overlap an effect
            # whose fate is unknown or deadlock on custody's prior-completion
            # guard.  Preserve the registered recovery/receipt prefix and seal
            # the execution without arming another provider-capable process.
            if version_observation.invocation_state == "uncertain":
                stop_reason = "executor-interrupted"
                break

            native_plan = retained_by_scope[(case["case_id"], arm, "native-review")]
            try:
                native_capture = session.claim_process(native_plan)
            except LiveExecutionCustodyError as error:
                if session.resumed and "recovery_cannot_launch" in str(error):
                    stop_reason = "executor-interrupted"
                    break
                raise
            native_recovery_ref = None
            if isinstance(native_capture, RecoveredProcessCapture):
                if native_capture.recovery is not None:
                    native_recovery_ref = _registered_document(
                        registrar,
                        native_capture.recovery,
                        kind="native-process-recovery",
                        schema="caplab-revbench-live-process-recovery/1",
                        registration_id=native_capture.recovery["process_id"],
                    )
            elif not matches_expected:
                _complete_without_launch(native_capture, "preflight-refused")
            elif credential is None:
                raise LiveExecutionCustodyError("live_execution_recovery_cannot_launch")
            else:
                if monotonic_execution_deadline is None:
                    raise LiveExecutionCustodyError(
                        "live_execution_recovery_cannot_launch"
                    )
                run_codex_process(
                    command["argv"],
                    assignment["stdin"],
                    bundle=bundle,
                    capture=native_capture,
                    credential=credential,
                    monotonic_deadline=monotonic_execution_deadline,
                )

            native_terminal = _terminal_custody_capture(
                session, native_plan, native_capture
            )
            native_observation = _recovered_observation(native_terminal)
            if native_terminal.recovery is not None and native_recovery_ref is None:
                native_recovery_ref = _registered_document(
                    registrar,
                    native_terminal.recovery,
                    kind="native-process-recovery",
                    schema="caplab-revbench-live-process-recovery/1",
                    registration_id=native_terminal.recovery["process_id"],
                )
            quarantined = native_observation.termination == "privacy-quarantine"
            if quarantined:
                stdout_ref = None
                stderr_ref = None
            else:
                stdout_ref, stderr_ref = _live_process_refs(
                    registrar,
                    native_observation,
                    label=(
                        f"live-native-{manifest['experiment_id']}-{case['case_id']}-{arm}"
                    ),
                )
            native_process_receipt_ref = _registered_process_receipt(
                registrar,
                execution_intent_ref=execution_intent_ref,
                sequence_index=sequence_index_by_process[
                    native_terminal.intent["process_id"]
                ],
                capture=native_terminal,
                stdout_ref=stdout_ref,
                stderr_ref=stderr_ref,
                recovery_ref=native_recovery_ref,
                stream_disposition=(
                    "privacy-quarantined" if quarantined else "registered"
                ),
            )
            process_receipt_refs.append(native_process_receipt_ref)
            derived = None
            invalid_response = False
            if (
                native_observation.invocation_state == "invoked"
                and native_observation.termination == "exited"
                and native_observation.exit_code == 0
                and native_observation.stdout_complete
                and native_observation.stderr_complete
            ):
                try:
                    derived = derive_codex_response(native_observation.stdout)
                except CodexResponseSchemaError:
                    invalid_response = True
                except CodexJSONLTransportError:
                    derived = None
            if derived is not None:
                disposition = "complete"
                parse_status = "valid"
                verdict = derived.response["verdict"]
                anchors = derived.response["anchors"]
                derived_response_ref = _registered_bytes(
                    registrar,
                    derived.response_bytes,
                    kind="native-derived-response",
                    schema="caplab-revbench-native-response/1",
                    registration_id=(
                        f"live-derived-{manifest['experiment_id']}-{case['case_id']}-{arm}"
                    ),
                )
                derivation = response_derivation_document(
                    derived, stdout_ref, derived_response_ref
                )
                response_derivation_ref = _registered_document(
                    registrar,
                    derivation,
                    kind="native-response-derivation",
                    schema="caplab-revbench-response-derivation/1",
                    registration_id=(
                        f"live-derivation-{manifest['experiment_id']}-{case['case_id']}-{arm}"
                    ),
                )
            elif invalid_response:
                disposition = "subject-failure"
                parse_status = "invalid-response"
                verdict = "invalid"
                anchors = []
                derived_response_ref = None
                response_derivation_ref = None
            else:
                disposition = "infrastructure-failure"
                parse_status = (
                    "privacy-quarantine" if quarantined else "invalid-transport"
                )
                verdict = "invalid"
                anchors = []
                derived_response_ref = None
                response_derivation_ref = None
            output = {
                "schema_version": "caplab-live-native-output/1",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": manifest["binding"]["binding_id"],
                "raw_stdout_ref": stdout_ref,
                "derived_response_ref": derived_response_ref,
                "response_derivation_ref": response_derivation_ref,
                "parse_status": parse_status,
                "verdict": verdict,
                "anchors": anchors,
            }
            output_ref = _registered_document(
                registrar,
                output,
                kind="live-native-output",
                schema="caplab-live-native-output/1",
                registration_id=(
                    f"live-output-{manifest['experiment_id']}-{case['case_id']}-{arm}"
                ),
            )
            harness_completion = (
                "observed" if derived is not None or invalid_response else "unavailable"
            )
            capture_document: dict[str, Any] = {
                "schema_version": "caplab-live-native-attempt-capture/1",
                "capture_id": "",
                "execution_authorization_ref": copy.deepcopy(
                    dict(execution_authorization_ref)
                ),
                "apparatus_ref": apparatus_ref,
                "execution_intent_ref": execution_intent_ref,
                "process_receipt_ref": native_process_receipt_ref,
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": manifest["binding"]["binding_id"],
                "observed_binding": copy.deepcopy(manifest["binding"]),
                "intent_recorded_at": native_capture.intent["intent_recorded_at"],
                "launch_attempted_at": native_observation.launch_attempted_at,
                "containment_process_started_at": native_observation.process_started_at,
                "containment_process_completed_at": native_observation.process_completed_at,
                "completion_recorded_at": native_observation.completion_recorded_at,
                "outer_launch_state": native_observation.invocation_state,
                "native_harness_completion": harness_completion,
                "provider_request_state": "unavailable",
                "command_ref": copy.deepcopy(
                    manifest["binding"]["harness"]["command_ref"]
                ),
                "version_observation_ref": version_observation_ref,
                "prompt_ref": assignment["prompt_ref"],
                "stdin_ref": assignment["stdin_ref"],
                "stdout_ref": stdout_ref,
                "stdout_complete": native_observation.stdout_complete,
                "stderr_ref": stderr_ref,
                "stderr_complete": native_observation.stderr_complete,
                "output_ref": output_ref,
                "exit_code": native_observation.exit_code,
                "termination": native_observation.termination,
                "recovery_ref": native_recovery_ref,
            }
            capture_document["capture_id"] = _content_id(
                capture_document, "capture_id", "live-capture-"
            )
            capture_ref = _registered_document(
                registrar,
                capture_document,
                kind="live-native-attempt-capture",
                schema="caplab-live-native-attempt-capture/1",
                registration_id=capture_document["capture_id"],
            )
            attestation: dict[str, Any] = {
                "schema_version": "caplab-live-native-attempt-attestation/1",
                "attestation_id": "",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "observed_at": native_observation.completion_recorded_at,
                "observed_binding": copy.deepcopy(manifest["binding"]),
                "native_system_contract_ref": copy.deepcopy(
                    manifest["native_system_contract_ref"]
                ),
                "execution_authorization_ref": copy.deepcopy(
                    dict(execution_authorization_ref)
                ),
                "apparatus_ref": apparatus_ref,
                "version_observation_ref": version_observation_ref,
                "capture_ref": capture_ref,
                "prompt_ref": assignment["prompt_ref"],
                "output_ref": output_ref,
            }
            attestation["attestation_id"] = _content_id(
                attestation, "attestation_id", "live-attestation-"
            )
            attestation_ref = _registered_document(
                registrar,
                attestation,
                kind="live-native-attempt-attestation",
                schema="caplab-live-native-attempt-attestation/1",
                registration_id=attestation["attestation_id"],
            )
            envelope: dict[str, Any] = {
                "schema_version": "caplab-live-native-review-attempt/1",
                "attempt_id": "",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": manifest["binding"]["binding_id"],
                "observed_binding": copy.deepcopy(manifest["binding"]),
                "apparatus_ref": apparatus_ref,
                "attestation_ref": attestation_ref,
                "prompt_ref": assignment["prompt_ref"],
                "disposition": disposition,
                "verdict": verdict,
                "anchors": anchors,
                "output_ref": output_ref,
                "provenance": copy.deepcopy(manifest["provenance"]),
            }
            envelope["attempt_id"] = _content_id(
                envelope, "attempt_id", "live-attempt-"
            )
            attempt_ref = _registered_document(
                registrar,
                envelope,
                kind="attempt",
                schema="caplab-live-native-review-attempt/1",
                registration_id=envelope["attempt_id"],
            )
            attempts.append(
                {
                    key: copy.deepcopy(envelope[key])
                    for key in (
                        "case_id",
                        "arm",
                        "assignment_index",
                        "binding_id",
                        "observed_binding",
                        "attestation_ref",
                        "prompt_ref",
                        "disposition",
                        "verdict",
                        "anchors",
                        "output_ref",
                    )
                }
                | {"attempt_ref": attempt_ref}
            )
            if disposition == "infrastructure-failure":
                stop_reason = (
                    native_observation.termination
                    if native_observation.termination != "exited"
                    else "response-transport-invalid"
                )
                break

        observed_at = session.finalization_recorded_at()
        reviews: dict[str, Any] = {
            "schema_version": "caplab-revbench-reviews/1",
            "execution_id": "",
            "experiment_id": manifest["experiment_id"],
            "execution_authorization_ref": copy.deepcopy(
                dict(execution_authorization_ref)
            ),
            "execution_intent_ref": execution_intent_ref,
            "process_receipt_refs": process_receipt_refs,
            "started_at": session.intent["intent_recorded_at"],
            "observed_at": observed_at,
            "status": "stopped" if stop_reason is not None else "complete",
            "stop_reason": stop_reason,
            "attempts": attempts,
        }
        reviews["execution_id"] = _content_id(reviews, "execution_id", "execution-")
        _registered_document(
            registrar,
            reviews,
            kind="revbench-execution",
            schema="caplab-revbench-reviews/1",
            registration_id=reviews["execution_id"],
        )
        session.seal(reviews)
        return reviews


def execute(
    manifest: Mapping[str, Any],
    execution_authorization_ref: Mapping[str, Any],
    registrar: _core.ArtifactRegistrar,
    *,
    live_runtime: FilesystemLiveExecutionRuntime | None = None,
) -> dict[str, Any]:
    """Execute one sealed revbench manifest under exact registered authority."""

    validated = _core._validate_manifest(manifest, registrar)
    started_monotonic = time.monotonic()
    started_at = _timestamp()
    authorization = _core._validate_execution_authorization(
        execution_authorization_ref, validated, registrar
    )
    if authorization["effect_class"] != "local-fixture":
        if type(live_runtime) is not FilesystemLiveExecutionRuntime:
            raise _core.RevbenchContractError(
                "live native execution requires an explicit durable custody runtime"
            )
        return _execute_live_codex(
            validated,
            execution_authorization_ref,
            authorization,
            registrar,
            live_runtime,
            started_at,
            started_monotonic,
        )
    _core._validate_execution_authorization(
        execution_authorization_ref,
        validated,
        registrar,
        observed_at=started_at,
    )
    environment, sandbox = _execution_environment(validated["binding"], registrar)
    command = _core._parse_canonical_json_ref(
        validated["binding"]["harness"]["command_ref"],
        registrar,
        "binding.harness.command_ref",
    )
    version_probe = _core._parse_canonical_json_ref(
        validated["binding"]["harness"]["version_probe_ref"],
        registrar,
        "binding.harness.version_probe_ref",
    )
    version_command = _core._parse_canonical_json_ref(
        version_probe["command_ref"],
        registrar,
        "binding.harness.version_probe_ref document.command_ref",
    )
    expected_version_stdout = _core._resolve_ref(
        version_probe["stdout_ref"], registrar, "expected version stdout"
    )
    expected_version_stderr = _core._resolve_ref(
        version_probe["stderr_ref"], registrar, "expected version stderr"
    )
    limits = authorization["limits"]
    total_deadline = time.monotonic() + limits["total_wall_seconds"]
    attempts: list[dict[str, Any]] = []
    stop_reason: str | None = None
    for case in validated["cases"]:
        for assignment_index, arm in enumerate(case["assignment_order"]):
            now = _timestamp()
            try:
                _core._validate_execution_authorization(
                    execution_authorization_ref,
                    validated,
                    registrar,
                    observed_at=now,
                )
            except _core.RevbenchContractError:
                stop_reason = "authorization-expired"
                break
            native_input = {
                "schema_version": "caplab-revbench-native-input/1",
                "instruction": _NATIVE_INPUT_INSTRUCTION,
                "requirement": copy.deepcopy(case["oracle"]),
                "artifact": copy.deepcopy(case[arm]["content"]),
                "response_schema_version": "caplab-revbench-native-response/1",
            }
            input_ref = _registered_document(
                registrar,
                native_input,
                kind="native-input",
                schema="caplab-revbench-native-input/1",
                registration_id=f"input-{validated['experiment_id']}-{case['case_id']}-{arm}",
            )
            stdin_bytes = canonical_json(native_input)
            stdin_ref = _registered_bytes(
                registrar,
                stdin_bytes,
                kind="native-process-stdin",
                schema="caplab-native-process-stream/1",
                registration_id=f"stdin-{validated['experiment_id']}-{case['case_id']}-{arm}",
            )
            prompt = {
                "schema_version": "caplab-revbench-prompt/1",
                "experiment_id": validated["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": validated["binding"]["binding_id"],
                "protocol_ref": copy.deepcopy(validated["protocol"]),
                "rendered_input_ref": input_ref,
            }
            prompt_ref = _registered_document(
                registrar,
                prompt,
                kind="prompt",
                schema="caplab-revbench-prompt/1",
                registration_id=f"prompt-{validated['experiment_id']}-{case['case_id']}-{arm}",
            )
            timeout, deadline_reason = _remaining_timeout(authorization, total_deadline)
            if timeout == 0:
                stop_reason = deadline_reason
                break
            version_observation = _run_process(
                version_command["argv"],
                b"",
                timeout_seconds=timeout,
                stdout_limit=limits["max_stdout_bytes_per_process"],
                stderr_limit=limits["max_stderr_bytes_per_process"],
                environment=environment,
                sandbox=sandbox,
            )
            version_observation = _deadline_termination(
                version_observation, deadline_reason
            )
            version_stdout_ref, version_stderr_ref = _process_refs(
                registrar,
                version_observation,
                label=f"version-{validated['experiment_id']}-{case['case_id']}-{arm}",
            )
            matches_expected = (
                version_observation.termination == "exited"
                and version_observation.exit_code == version_probe["exit_code"] == 0
                and version_observation.stdout_complete
                and version_observation.stderr_complete
                and version_observation.stdout == expected_version_stdout
                and version_observation.stderr == expected_version_stderr
            )
            version_document: dict[str, Any] = {
                "schema_version": "caplab-native-version-observation/1",
                "observation_id": "",
                "execution_authorization_ref": copy.deepcopy(
                    dict(execution_authorization_ref)
                ),
                "experiment_id": validated["experiment_id"],
                "binding_id": validated["binding"]["binding_id"],
                "expected_version_probe_ref": copy.deepcopy(
                    validated["binding"]["harness"]["version_probe_ref"]
                ),
                "command_ref": copy.deepcopy(version_probe["command_ref"]),
                "started_at": version_observation.started_at,
                "completed_at": version_observation.completed_at,
                "stdout_ref": version_stdout_ref,
                "stdout_complete": version_observation.stdout_complete,
                "stderr_ref": version_stderr_ref,
                "stderr_complete": version_observation.stderr_complete,
                "exit_code": version_observation.exit_code,
                "termination": version_observation.termination,
                "matches_expected": matches_expected,
            }
            version_document["observation_id"] = _content_id(
                version_document, "observation_id", "version-observation-"
            )
            version_observation_ref = _registered_document(
                registrar,
                version_document,
                kind="native-version-observation",
                schema="caplab-native-version-observation/1",
                registration_id=version_document["observation_id"],
            )
            if matches_expected:
                timeout, deadline_reason = _remaining_timeout(
                    authorization, total_deadline
                )
                if timeout == 0:
                    native_observation = _ProcessObservation(
                        _timestamp(),
                        _timestamp(),
                        b"",
                        True,
                        b"",
                        True,
                        None,
                        deadline_reason or "authorization-expired",
                    )
                else:
                    native_observation = _run_process(
                        command["argv"],
                        stdin_bytes,
                        timeout_seconds=timeout,
                        stdout_limit=limits["max_stdout_bytes_per_process"],
                        stderr_limit=limits["max_stderr_bytes_per_process"],
                        environment=environment,
                        sandbox=sandbox,
                    )
                    native_observation = _deadline_termination(
                        native_observation, deadline_reason
                    )
                native_invoked = timeout != 0
            else:
                preflight_termination = (
                    "authorization-expired"
                    if version_observation.termination == "authorization-expired"
                    else "preflight-refused"
                )
                native_observation = _ProcessObservation(
                    version_observation.started_at,
                    version_observation.completed_at,
                    b"",
                    True,
                    b"",
                    True,
                    None,
                    preflight_termination,
                )
                native_invoked = False
            stdout_ref, stderr_ref = _process_refs(
                registrar,
                native_observation,
                label=f"native-{validated['experiment_id']}-{case['case_id']}-{arm}",
            )
            response = (
                _parse_response(native_observation.stdout)
                if native_observation.termination == "exited"
                and native_observation.exit_code == 0
                and native_observation.stdout_complete
                and native_observation.stderr_complete
                else None
            )
            if response is not None:
                disposition = "complete"
                verdict = response["verdict"]
                anchors = response["anchors"]
                parse_status = "valid"
            elif (
                native_invoked
                and native_observation.termination == "exited"
                and native_observation.exit_code == 0
            ):
                disposition = "subject-failure"
                verdict = "invalid"
                anchors = []
                parse_status = "invalid"
            else:
                disposition = "infrastructure-failure"
                verdict = "invalid"
                anchors = []
                parse_status = "invalid"
            output = {
                "schema_version": "caplab-native-output/1",
                "experiment_id": validated["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": validated["binding"]["binding_id"],
                "raw_stdout_ref": stdout_ref,
                "parse_status": parse_status,
                "verdict": verdict,
                "anchors": anchors,
            }
            output_ref = _registered_document(
                registrar,
                output,
                kind="native-output",
                schema="caplab-native-output/1",
                registration_id=f"output-{validated['experiment_id']}-{case['case_id']}-{arm}",
            )
            capture: dict[str, Any] = {
                "schema_version": "caplab-native-attempt-capture/1",
                "capture_id": "",
                "execution_authorization_ref": copy.deepcopy(
                    dict(execution_authorization_ref)
                ),
                "experiment_id": validated["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": validated["binding"]["binding_id"],
                "observed_binding": copy.deepcopy(validated["binding"]),
                "started_at": version_observation.started_at,
                "completed_at": native_observation.completed_at,
                "command_ref": copy.deepcopy(
                    validated["binding"]["harness"]["command_ref"]
                ),
                "version_observation_ref": version_observation_ref,
                "prompt_ref": prompt_ref,
                "stdin_ref": stdin_ref,
                "stdout_ref": stdout_ref,
                "stdout_complete": native_observation.stdout_complete,
                "stderr_ref": stderr_ref,
                "stderr_complete": native_observation.stderr_complete,
                "output_ref": output_ref,
                "native_invoked": native_invoked,
                "exit_code": native_observation.exit_code,
                "termination": native_observation.termination,
            }
            capture["capture_id"] = _content_id(capture, "capture_id", "capture-")
            capture_ref = _registered_document(
                registrar,
                capture,
                kind="native-attempt-capture",
                schema="caplab-native-attempt-capture/1",
                registration_id=capture["capture_id"],
            )
            attestation: dict[str, Any] = {
                "schema_version": "caplab-native-attempt-attestation/1",
                "attestation_id": "",
                "experiment_id": validated["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "observed_at": native_observation.completed_at,
                "observed_binding": copy.deepcopy(validated["binding"]),
                "native_system_contract_ref": copy.deepcopy(
                    validated["native_system_contract_ref"]
                ),
                "execution_authorization_ref": copy.deepcopy(
                    dict(execution_authorization_ref)
                ),
                "version_observation_ref": version_observation_ref,
                "capture_ref": capture_ref,
                "prompt_ref": prompt_ref,
                "output_ref": output_ref,
            }
            attestation["attestation_id"] = _content_id(
                attestation, "attestation_id", "attestation-"
            )
            attestation_ref = _registered_document(
                registrar,
                attestation,
                kind="native-attempt-attestation",
                schema="caplab-native-attempt-attestation/1",
                registration_id=attestation["attestation_id"],
            )
            envelope: dict[str, Any] = {
                "schema_version": "caplab-native-review-attempt/1",
                "attempt_id": "",
                "experiment_id": validated["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": validated["binding"]["binding_id"],
                "observed_binding": copy.deepcopy(validated["binding"]),
                "attestation_ref": attestation_ref,
                "prompt_ref": prompt_ref,
                "disposition": disposition,
                "verdict": verdict,
                "anchors": anchors,
                "output_ref": output_ref,
                "provenance": copy.deepcopy(validated["provenance"]),
            }
            envelope["attempt_id"] = _content_id(envelope, "attempt_id", "attempt-")
            attempt_ref = _registered_document(
                registrar,
                envelope,
                kind="attempt",
                schema="caplab-native-review-attempt/1",
                registration_id=envelope["attempt_id"],
            )
            attempts.append(
                {
                    key: copy.deepcopy(envelope[key])
                    for key in (
                        "case_id",
                        "arm",
                        "assignment_index",
                        "binding_id",
                        "observed_binding",
                        "attestation_ref",
                        "prompt_ref",
                        "disposition",
                        "verdict",
                        "anchors",
                        "output_ref",
                    )
                }
                | {"attempt_ref": attempt_ref}
            )
            if disposition == "infrastructure-failure":
                stop_reason = (
                    version_observation.termination
                    if not matches_expected
                    and version_observation.termination != "exited"
                    else native_observation.termination
                )
                break
        if stop_reason is not None:
            break
    observed_at = _timestamp()
    identity: dict[str, Any] = {
        "schema_version": "caplab-revbench-reviews/1",
        "execution_id": "",
        "experiment_id": validated["experiment_id"],
        "execution_authorization_ref": copy.deepcopy(dict(execution_authorization_ref)),
        "started_at": started_at,
        "observed_at": observed_at,
        "status": "stopped" if stop_reason is not None else "complete",
        "stop_reason": stop_reason,
        "attempts": attempts,
    }
    identity["execution_id"] = _content_id(identity, "execution_id", "execution-")
    _registered_document(
        registrar,
        identity,
        kind="revbench-execution",
        schema="caplab-revbench-reviews/1",
        registration_id=identity["execution_id"],
    )
    return identity
