"""Lease-pulse supervision for one remote Windows training process tree."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol


PULSE_SCHEMA = "caplab.training.remote-pulse/v1"
IDENTITY_SCHEMA = "caplab.training.remote-process-identity/v1"
OUTCOME_SCHEMA = "caplab.training.remote-process-outcome/v1"
TEMPFAIL = 75


class SupervisorContractError(ValueError):
    """The remote supervision contract is incomplete or has drifted."""


@dataclass(frozen=True)
class SupervisorConfig:
    pulse_path: Path
    identity_path: Path
    outcome_path: Path
    lease_id: str
    host_boot_id: str
    ttl_seconds: float
    poll_seconds: float
    command: tuple[str, ...]


class Process(Protocol):
    pid: int

    def poll(self) -> int | None: ...


class Runtime(Protocol):
    def clock(self) -> float: ...

    def sleep(self, seconds: float) -> None: ...

    def launch_contained(self, command: tuple[str, ...]) -> Process: ...

    def terminate(self, process: Process) -> None: ...

    def close(self) -> None: ...


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _exclusive_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(_canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def _read_pulse(path: Path, expected_lease_id: str) -> int:
    try:
        pulse = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SupervisorContractError("pulse_unreadable") from error
    if pulse.get("schema") != PULSE_SCHEMA:
        raise SupervisorContractError("pulse_schema_mismatch")
    if pulse.get("lease_id") != expected_lease_id:
        raise SupervisorContractError("pulse_lease_mismatch")
    sequence = pulse.get("sequence")
    if not isinstance(sequence, int) or sequence < 0:
        raise SupervisorContractError("pulse_sequence_invalid")
    return sequence


def _outcome(config: SupervisorConfig, status: str, exit_code: int | None) -> dict[str, object]:
    return {
        "schema": OUTCOME_SCHEMA,
        "lease_id": config.lease_id,
        "host_boot_id": config.host_boot_id,
        "status": status,
        "child_exit_code": exit_code,
        "recorded_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


def run_supervised(config: SupervisorConfig, runtime: Runtime) -> int:
    """Run one command in a kill-on-close tree while a matching pulse advances."""
    if not config.command:
        raise SupervisorContractError("command_required")
    if config.poll_seconds <= 0 or config.ttl_seconds <= config.poll_seconds:
        raise SupervisorContractError("pulse_timing_invalid")

    last_sequence = _read_pulse(config.pulse_path, config.lease_id)
    last_advance = runtime.clock()
    process = runtime.launch_contained(config.command)
    try:
        _exclusive_json(config.identity_path, {
            "schema": IDENTITY_SCHEMA,
            "lease_id": config.lease_id,
            "host_boot_id": config.host_boot_id,
            "supervisor_pid": os.getpid(),
            "child_pid": process.pid,
            "command_sha256": hashlib.sha256(_canonical(config.command)).hexdigest(),
            "started_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        })
        while True:
            exit_code = process.poll()
            if exit_code is not None:
                status = "completed" if exit_code == 0 else "child-failed"
                _exclusive_json(config.outcome_path, _outcome(config, status, exit_code))
                return exit_code

            runtime.sleep(config.poll_seconds)
            try:
                sequence = _read_pulse(config.pulse_path, config.lease_id)
            except SupervisorContractError:
                runtime.terminate(process)
                _exclusive_json(
                    config.outcome_path,
                    _outcome(config, "invalid-remote-pulse-tree-terminated", None),
                )
                return TEMPFAIL
            now = runtime.clock()
            if sequence < last_sequence:
                runtime.terminate(process)
                _exclusive_json(
                    config.outcome_path,
                    _outcome(config, "remote-pulse-regressed-tree-terminated", None),
                )
                return TEMPFAIL
            if sequence > last_sequence:
                last_sequence = sequence
                last_advance = now
            if now - last_advance > config.ttl_seconds:
                runtime.terminate(process)
                _exclusive_json(
                    config.outcome_path,
                    _outcome(config, "remote-pulse-expired-tree-terminated", None),
                )
                return TEMPFAIL
    finally:
        runtime.close()


class WindowsJobRuntime:
    """Own a Windows Job Object whose close kills the entire child tree."""

    _KILL_ON_JOB_CLOSE = 0x00002000
    _EXTENDED_LIMIT_INFORMATION = 9

    def __init__(self) -> None:
        if os.name != "nt":
            raise RuntimeError("windows_job_runtime_requires_windows")
        from ctypes import wintypes

        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self._kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        self._kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        self._kernel32.SetInformationJobObject.restype = wintypes.BOOL
        self._kernel32.AssignProcessToJobObject.argtypes = [
            wintypes.HANDLE,
            wintypes.HANDLE,
        ]
        self._kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        self._kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self._kernel32.TerminateJobObject.restype = wintypes.BOOL
        self._kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self._kernel32.CloseHandle.restype = wintypes.BOOL
        self._job: int | None = None

    def clock(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def _raise_last_error(self, operation: str) -> None:
        raise OSError(ctypes.get_last_error(), operation)

    def launch_contained(self, command: tuple[str, ...]) -> subprocess.Popen:
        from ctypes import wintypes

        class BasicLimitInformation(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class IoCounters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in (
                "ReadOperationCount",
                "WriteOperationCount",
                "OtherOperationCount",
                "ReadTransferCount",
                "WriteTransferCount",
                "OtherTransferCount",
            )]

        class ExtendedLimitInformation(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", BasicLimitInformation),
                ("IoInfo", IoCounters),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        job = self._kernel32.CreateJobObjectW(None, None)
        if not job:
            self._raise_last_error("CreateJobObjectW")
        self._job = job
        limits = ExtendedLimitInformation()
        limits.BasicLimitInformation.LimitFlags = self._KILL_ON_JOB_CLOSE
        if not self._kernel32.SetInformationJobObject(
            job,
            self._EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            self.close()
            self._raise_last_error("SetInformationJobObject")

        gate = Path(os.environ.get("TEMP", ".")) / f"caplab-job-gate-{uuid.uuid4().hex}"
        bootstrap = (
            sys.executable,
            "-c",
            "import pathlib,subprocess,sys,time;"
            "p=pathlib.Path(sys.argv[1]);"
            "exec('while not p.exists():\\n time.sleep(0.05)');"
            "p.unlink();"
            "raise SystemExit(subprocess.call(sys.argv[2:]))",
            str(gate),
            *command,
        )
        process = subprocess.Popen(bootstrap)
        if not self._kernel32.AssignProcessToJobObject(job, int(process._handle)):
            process.kill()
            process.wait()
            self.close()
            self._raise_last_error("AssignProcessToJobObject")
        try:
            gate.write_bytes(b"assigned\n")
        except OSError:
            process.kill()
            process.wait()
            self.close()
            raise
        return process

    def terminate(self, _process: Process) -> None:
        if self._job is not None and not self._kernel32.TerminateJobObject(self._job, TEMPFAIL):
            self._raise_last_error("TerminateJobObject")

    def close(self) -> None:
        if self._job is not None:
            if not self._kernel32.CloseHandle(self._job):
                self._raise_last_error("CloseHandle")
            self._job = None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pulse", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--outcome", type=Path, required=True)
    parser.add_argument("--lease-id", required=True)
    parser.add_argument("--host-boot-id", required=True)
    parser.add_argument("--ttl-seconds", type=float, required=True)
    parser.add_argument("--poll-seconds", type=float, default=2)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    try:
        return run_supervised(
            SupervisorConfig(
                pulse_path=args.pulse,
                identity_path=args.identity,
                outcome_path=args.outcome,
                lease_id=args.lease_id,
                host_boot_id=args.host_boot_id,
                ttl_seconds=args.ttl_seconds,
                poll_seconds=args.poll_seconds,
                command=tuple(command),
            ),
            WindowsJobRuntime(),
        )
    except Exception as error:
        print(f"caplab-training-supervisor: {type(error).__name__}: {error}", file=sys.stderr)
        return 70


if __name__ == "__main__":
    raise SystemExit(main())
