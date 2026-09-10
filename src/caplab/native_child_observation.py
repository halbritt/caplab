"""Own bounded child readiness and freeze/thaw independently of provider behavior."""

import errno
import math
import os
from pathlib import Path
import re
import time

from caplab.native_child_process import (
    FrozenNativeChildEvidence,
    _executable_identity,
    _file_object,
    _kernel_bytes,
    _kernel_fields,
    _process,
    observe_frozen_native_child,
)
from caplab.task_capture_verify import _identity, _open, _require


class NativeChildObservationError(ValueError):
    """Failed observation with a bounded record for the caller's guarded custody."""

    def __init__(self, record):
        super().__init__(record["error_code"])
        self.record = record


def inspect_supervisor_child_observation(
    record,
    *,
    expected_parent_pid,
    expected_supervisor_pid,
    not_before_monotonic_ns,
    not_after_monotonic_ns,
):
    """Check an independently retained record; caller anchors bytes and image/trace links."""
    _require(
        type(record) is dict
        and set(record)
        == {
            "schema",
            "profile",
            "supervisor_pid",
            "timeout_seconds",
            "poll_interval_seconds",
            "poll_count",
            "clock",
            "observation",
            "binding_complete",
            "study_eligible",
        },
        "invalid supervisor observation record",
    )
    _require(
        record["schema"] == "caplab.supervisor-child-observation/v1"
        and record["profile"] == "supervisor-poll/v1"
        and type(record["supervisor_pid"]) is int
        and record["supervisor_pid"] == expected_supervisor_pid
        and record["binding_complete"] is False
        and record["study_eligible"] is False,
        "supervisor observation identity differs",
    )
    _require(
        type(record["timeout_seconds"]) in (int, float)
        and 0 < record["timeout_seconds"] <= 30
        and record["poll_interval_seconds"] == 0.01
        and type(record["poll_count"]) is int
        and record["poll_count"] > 0,
        "supervisor observation bounds differ",
    )
    observed = record["observation"]
    _require(
        type(observed) is dict
        and observed.get("schema") == "caplab.frozen-native-child-observation/v1"
        and observed.get("parent_pid") == expected_parent_pid
        and observed.get("live_child_executable_observed") is True,
        "supervisor child identity differs",
    )
    keys = (
        "started_monotonic_ns",
        "candidate_seen_monotonic_ns",
        "freeze_requested_monotonic_ns",
        "frozen_monotonic_ns",
        "thaw_requested_monotonic_ns",
        "thawed_monotonic_ns",
        "finished_monotonic_ns",
    )
    clock = record["clock"]
    _require(
        type(clock) is dict and set(clock) == set(keys),
        "invalid supervisor observation clock",
    )
    ordered = (
        [not_before_monotonic_ns]
        + [clock[k] for k in keys[:4]]
        + [observed["started_monotonic_ns"], observed["finished_monotonic_ns"]]
        + [clock[k] for k in keys[4:]]
        + [not_after_monotonic_ns]
    )
    _require(
        all(type(v) is int and v > 0 for v in ordered) and ordered == sorted(ordered),
        "supervisor observation clock differs",
    )
    _require(
        clock["frozen_monotonic_ns"] - clock["freeze_requested_monotonic_ns"]
        <= 2 * 10**9
        and clock["thawed_monotonic_ns"] - clock["thaw_requested_monotonic_ns"]
        <= 2 * 10**9,
        "supervisor freeze transition exceeded bound",
    )
    return {
        "profile": record["profile"],
        "provider_signal_required": False,
        "wait_nanoseconds": clock["candidate_seen_monotonic_ns"]
        - clock["started_monotonic_ns"],
        "pause_nanoseconds": clock["thawed_monotonic_ns"]
        - clock["freeze_requested_monotonic_ns"],
        "observation_nanoseconds": clock["finished_monotonic_ns"]
        - clock["started_monotonic_ns"],
    }


def _write_freeze(group, value):
    fd = os.open(
        "cgroup.freeze", os.O_WRONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=group
    )
    try:
        _require(os.write(fd, value) == len(value), "incomplete freeze command")
    finally:
        os.close(fd)


def _await_freeze(group, value):
    deadline = time.monotonic() + 2
    while _kernel_fields(group, "cgroup.events").get(b"frozen") != value:
        if time.monotonic() >= deadline:
            raise TimeoutError("owned cgroup transition timed out")
        time.sleep(0.01)


def _ready(group, path, evidence, source_identity):
    membership = ("0::/" + str(path.relative_to("/sys/fs/cgroup")) + "\n").encode()
    _require(
        _file_object(os.fstat(evidence.parent_proc_descriptor))
        == _file_object(Path(f"/proc/{evidence.parent_pid}").stat()),
        "parent descriptor differs",
    )
    _process(evidence.parent_proc_descriptor, evidence.parent_pid, membership)
    rows = _kernel_bytes(group, "cgroup.procs").splitlines()
    _require(
        all(re.fullmatch(rb"[1-9][0-9]*", row) for row in rows),
        "invalid cgroup population",
    )
    pids = [int(row) for row in rows]
    _require(
        len(pids) == len(set(pids)) and len(pids) <= evidence.max_processes,
        "cgroup population exceeds allowance",
    )
    _require(
        evidence.parent_pid in pids and os.getpid() not in pids,
        "cgroup placement differs",
    )
    for pid in pids:
        if pid == evidence.parent_pid:
            continue
        try:
            with _open(None, Path("/proc") / str(pid), directory=True) as proc:
                status = _process(proc, pid, membership)
                if (
                    status["PPid"] == evidence.parent_pid
                    and _executable_identity(proc) == source_identity
                ):
                    return True
        except OSError as error:
            # A disappearing candidate is a readiness race, never identity evidence.
            if error.errno not in (errno.ENOENT, errno.ESRCH):
                raise
    return False


def wait_for_native_child(
    cgroup_path: Path, *, evidence: FrozenNativeChildEvidence, timeout_seconds: float
) -> dict:
    """Borrow parent/source evidence; own one freeze/thaw after a readiness hint.

    Caller owns the leaf cgroup, authenticated parent descriptor, source quiescence
    and exclusion of outside migrations/signals. It must stop the workload on any
    error and guard the returned record before retention. Waiting is at most the
    selected 30 seconds, plus two seconds per freeze transition and bounded image
    reading. No provider message, task instruction or child-ready packet is used.
    A short-lived image may exit before observation; that is unavailable evidence.
    """
    _require(isinstance(evidence, FrozenNativeChildEvidence), "invalid child evidence")
    _require(
        type(timeout_seconds) in (int, float)
        and math.isfinite(timeout_seconds)
        and 0 < timeout_seconds <= 30,
        "invalid child wait timeout",
    )
    _require(
        type(evidence.max_processes) is int and 1 <= evidence.max_processes <= 128,
        "invalid process allowance",
    )
    path = Path(cgroup_path)
    _require(
        path.is_absolute()
        and path.resolve() == path
        and path != Path("/sys/fs/cgroup")
        and path.is_relative_to("/sys/fs/cgroup"),
        "requires resolved non-root cgroup",
    )
    clock = {"started_monotonic_ns": time.monotonic_ns()}
    record = {
        "schema": "caplab.supervisor-child-observation/v1",
        "profile": "supervisor-poll/v1",
        "supervisor_pid": os.getpid(),
        "timeout_seconds": timeout_seconds,
        "poll_interval_seconds": 0.01,
        "poll_count": 0,
        "clock": clock,
        "observation": None,
        "binding_complete": False,
        "study_eligible": False,
    }
    timed_out = False
    try:
        with _open(None, path, directory=True) as group:
            group_identity = _file_object(os.fstat(group))
            _require(
                _kernel_bytes(group, "cgroup.type") == b"domain\n",
                "cgroup must be a domain",
            )
            _require(
                _kernel_fields(group, "cgroup.stat").get(b"nr_descendants") == b"0",
                "cgroup must be a leaf",
            )
            _require(
                _kernel_fields(group, "cgroup.events").get(b"frozen") == b"0",
                "cgroup already frozen",
            )
            source_identity = _identity(Path(evidence.expected_executable).stat())
            deadline = time.monotonic() + timeout_seconds
            while True:
                record["poll_count"] += 1
                if _ready(group, path, evidence, source_identity):
                    clock["candidate_seen_monotonic_ns"] = time.monotonic_ns()
                    break
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    raise TimeoutError("native child readiness timed out")
                time.sleep(min(0.01, remaining))
            _require(
                _file_object(path.stat()) == group_identity, "cgroup identity changed"
            )
            try:
                clock["freeze_requested_monotonic_ns"] = time.monotonic_ns()
                _write_freeze(group, b"1")
                _await_freeze(group, b"1")
                clock["frozen_monotonic_ns"] = time.monotonic_ns()
                record["observation"] = observe_frozen_native_child(
                    path, evidence=evidence
                )
                _require(
                    record["observation"]["cgroup"]["device"]
                    == group_identity["device"]
                    and record["observation"]["cgroup"]["inode"]
                    == group_identity["inode"],
                    "observed cgroup identity differs",
                )
            finally:
                clock["thaw_requested_monotonic_ns"] = time.monotonic_ns()
                _write_freeze(group, b"0")
                _await_freeze(group, b"0")
                clock["thawed_monotonic_ns"] = time.monotonic_ns()
        clock["finished_monotonic_ns"] = time.monotonic_ns()
        return record
    except (OSError, ValueError, TimeoutError):
        clock["finished_monotonic_ns"] = time.monotonic_ns()
        record["error_code"] = (
            "native_child_wait_timed_out"
            if timed_out
            else "native_child_observation_failed"
        )
        raise NativeChildObservationError(record) from None
