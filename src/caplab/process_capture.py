"""Bounded binary process streams for prospective, separately authorized attempts."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time
from contextlib import ExitStack
from datetime import UTC, datetime
from typing import Callable, Mapping, Sequence

from caplab.capture_quarantine import StreamQuarantine, check_capture_document


class ProcessCaptureQuarantineError(RuntimeError):
    """Guarded output cannot produce a complete raw capture."""


def _write_all(descriptor: int, data: bytes) -> None:
    remaining = memoryview(data)
    while remaining:
        count = os.write(descriptor, remaining)
        if count == 0:
            raise OSError("capture write made no progress")
        remaining = remaining[count:]


def _kill_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def seal_capture_json(output_dir: Path, name: str, receipt: dict) -> str:
    """Publish a named JSON receipt in fresh trusted custody; return its byte hash."""
    pending = output_dir / ("." + name.removesuffix(".json") + ".pending")
    content = (json.dumps(receipt, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        _write_all(fd, content)
        os.fsync(fd)
    finally:
        os.close(fd)
    final = output_dir / name
    os.link(pending, final)
    try:
        pending.unlink()
        for directory in (output_dir, output_dir.parent):
            parent_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(parent_fd)
            finally:
                os.close(parent_fd)
    except BaseException:
        final.unlink()
        raise
    return hashlib.sha256(content).hexdigest()


def capture_process(
    command: Sequence[str], *, cwd: Path, environment: Mapping[str, str],
    output_dir: Path, max_stream_bytes: int, timeout_seconds: float,
    pass_fds: Sequence[int] = (),
    quarantine_factory: Callable[[], StreamQuarantine] | None = None,
) -> dict:
    """Retain stdout/stderr under one limit; this does not authorize execution.

    The caller owns launch authorization, external containment, reserved storage,
    and a trusted private parent for output_dir. No existing directory is reused.
    A receipt means the capture operation ended, not that the task succeeded.
    Exceptions leave raw prefixes without a final receipt and propagate.
    Explicit extra descriptors are borrowed; callers keep them open and stable
    until return. Their contents are not read or added to the receipt here.
    A trusted quarantine factory creates two distinct stream gates. Guarded
    failures abandon buffered overlap and leave no completion receipt; success
    requires exact raw bytes. Gate memory, execution time and secret policy
    remain the caller's responsibility.
    Fresh metadata gates also check the process receipt before publication.
    """
    if type(max_stream_bytes) is not int or max_stream_bytes <= 0:
        raise ValueError("max_stream_bytes must be a positive integer")
    if (type(timeout_seconds) not in (int, float)
            or not math.isfinite(timeout_seconds) or timeout_seconds <= 0):
        raise ValueError("timeout_seconds must be positive and finite")
    if not command or isinstance(command, (str, bytes)):
        raise ValueError("command must be a nonempty argument sequence")
    command = tuple(command)
    if not command or not command[0] or any(
            not isinstance(arg, str) or "\0" in arg for arg in command):
        raise ValueError("command must be a nonempty argument sequence")
    if not isinstance(environment, Mapping):
        raise ValueError("environment must be an explicit string mapping")
    environment = dict(environment)
    if any(
            not isinstance(k, str) or not isinstance(v, str) or not k
            or "=" in k or "\0" in k or "\0" in v for k, v in environment.items()):
        raise ValueError("environment must be an explicit string mapping")
    if not isinstance(pass_fds, Sequence) or isinstance(pass_fds, (str, bytes)):
        raise ValueError("pass_fds must be a sequence of unique open descriptors above 2")
    pass_fds = tuple(pass_fds)
    if (any(type(fd) is not int or fd <= 2 for fd in pass_fds)
            or len(set(pass_fds)) != len(pass_fds)):
        raise ValueError("pass_fds must be a sequence of unique open descriptors above 2")
    # Check before custody opens files that could reuse an already-closed number.
    for fd in pass_fds:
        os.fstat(fd)
    cwd, output_dir = Path(cwd), Path(output_dir)
    if not cwd.is_absolute() or not cwd.is_dir():
        raise ValueError("cwd must be an absolute existing directory")
    if not output_dir.is_absolute() or output_dir.parent.resolve() != output_dir.parent:
        raise ValueError("output_dir must have an absolute resolved parent")
    with ExitStack() as stack:
        gate_cleanup = stack.enter_context(ExitStack())
        gates = {}
        if quarantine_factory is not None:
            if not callable(quarantine_factory):
                raise ValueError("quarantine_factory must be callable")
            for name in ("stdout", "stderr"):
                gate = quarantine_factory()
                if any(gate is prior for prior in gates.values()):
                    raise ValueError("quarantine_factory must create distinct fresh stream gates")
                abandon = getattr(gate, "abandon", None)
                if callable(abandon):
                    gate_cleanup.callback(abandon)
                if (any(not callable(getattr(gate, method, None))
                        for method in ("feed", "finish", "abandon"))
                        or getattr(gate, "quarantined", None) is not False):
                    raise ValueError("quarantine_factory must create distinct fresh stream gates")
                gates[name] = gate
        output_dir.mkdir(mode=0o700)
        streams = {name: {"bytes": 0, "digest": hashlib.sha256(),
                          "eof": False, "first_receipt_monotonic_ns": None,
                          "last_receipt_monotonic_ns": None}
                   for name in ("stdout", "stderr")}
        received = {name: {"bytes": 0, "digest": hashlib.sha256()} for name in gates}
        started = time.monotonic_ns()
        started_at = datetime.now(UTC).isoformat()
        deadline = time.monotonic() + timeout_seconds
        total = 0
        termination = "exited"
        descriptors = {}
        for name in streams:
            fd = os.open(output_dir / ("native." + name),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            stack.callback(os.close, fd)
            descriptors[name] = fd

        def retain(name: str, data: bytes) -> None:
            if gates and (not isinstance(data, bytes)
                          or len(data) > received[name]["bytes"] - streams[name]["bytes"]):
                raise ProcessCaptureQuarantineError("quarantine changed raw stream")
            _write_all(descriptors[name], data)
            streams[name]["digest"].update(data)
            streams[name]["bytes"] += len(data)

        selector = stack.enter_context(selectors.DefaultSelector())
        process = subprocess.Popen(command, cwd=cwd, env=environment,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True,
                                   close_fds=True, pass_fds=pass_fds)
        try:
            pipes = {name: stack.enter_context(getattr(process, name)) for name in streams}
            for name in streams:
                pipe = pipes[name]
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, name)
            while selector.get_map() or process.poll() is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    termination = "timeout"
                    break
                ready = selector.select(min(remaining, 0.05))
                for key, _ in ready:
                    name = key.data
                    data = os.read(key.fd, min(65536, max_stream_bytes - total + 1))
                    if not data:
                        if gates:
                            tail = gates[name].finish()
                            if gates[name].quarantined is not False:
                                raise ProcessCaptureQuarantineError("capture output quarantined")
                            retain(name, tail)
                        streams[name]["eof"] = True
                        selector.unregister(key.fileobj)
                        continue
                    now = time.monotonic_ns()
                    info = streams[name]
                    if info["first_receipt_monotonic_ns"] is None:
                        info["first_receipt_monotonic_ns"] = now
                    info["last_receipt_monotonic_ns"] = now
                    retained = data[:max_stream_bytes - total]
                    if gates:
                        received[name]["bytes"] += len(retained)
                        received[name]["digest"].update(retained)
                    emitted = gates[name].feed(retained) if gates else retained
                    if gates and gates[name].quarantined is not False:
                        raise ProcessCaptureQuarantineError("capture output quarantined")
                    retain(name, emitted)
                    total += len(retained)
                    if len(retained) != len(data):
                        termination = "byte-limit"
                        break
                if termination != "exited":
                    break
        finally:
            # Also stops same-group descendants holding pipes after leader exit.
            _kill_group(process)
            process.wait(timeout=5)
        if gates and termination != "exited":
            raise ProcessCaptureQuarantineError("guarded capture incomplete: " + termination)
        if any(streams[name]["bytes"] != original["bytes"]
               or streams[name]["digest"].digest() != original["digest"].digest()
               for name, original in received.items()):
            raise ProcessCaptureQuarantineError("quarantine changed raw stream")
        gate_cleanup.close()
        for fd in descriptors.values():
            os.fsync(fd)
        receipt = {
            "schema": "caplab.process-capture/v1",
            "termination": termination, "return_code": process.returncode,
            "streams_complete": termination == "exited" and all(
                s["eof"] for s in streams.values()),
            "max_stream_bytes": max_stream_bytes, "retained_stream_bytes": total,
            "timeout_seconds": timeout_seconds,
            "started_at": started_at, "finished_at": datetime.now(UTC).isoformat(),
            "started_monotonic_ns": started, "finished_monotonic_ns": time.monotonic_ns(),
            "streams": {name: {k: v for k, v in info.items() if k != "digest"}
                        | {"sha256": info["digest"].hexdigest(), "path": "native." + name}
                        for name, info in streams.items()},
        }
        check_capture_document(quarantine_factory, receipt)
        seal_capture_json(output_dir, "capture.json", receipt)
    return receipt
