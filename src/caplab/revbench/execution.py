"""Authorization-gated native revbench execution and evidence capture."""

from __future__ import annotations

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
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from caplab.runtime.canonical import canonical_json, sha256_hex

from . import _core

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


def execute(
    manifest: Mapping[str, Any],
    execution_authorization_ref: Mapping[str, Any],
    registrar: _core.ArtifactRegistrar,
) -> dict[str, Any]:
    """Execute one sealed revbench manifest under exact registered authority."""

    validated = _core._validate_manifest(manifest, registrar)
    started_at = _timestamp()
    authorization = _core._validate_execution_authorization(
        execution_authorization_ref,
        validated,
        registrar,
        observed_at=started_at,
    )
    if authorization["effect_class"] != "local-fixture":
        raise _core.RevbenchContractError(
            "live native execution requires a separately implemented sealed "
            "harness-bundle and durable streaming-custody adapter"
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
