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
from typing import Mapping, Sequence


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


def capture_process(
    command: Sequence[str], *, cwd: Path, environment: Mapping[str, str],
    output_dir: Path, max_stream_bytes: int, timeout_seconds: float,
) -> dict:
    """Retain stdout/stderr under one limit; this does not authorize execution.

    The caller owns launch authorization, external containment, reserved storage,
    and a trusted private parent for output_dir. No existing directory is reused.
    A receipt means the capture operation ended, not that the task succeeded.
    Exceptions leave raw prefixes without a final receipt and propagate.
    """
    if type(max_stream_bytes) is not int or max_stream_bytes <= 0:
        raise ValueError("max_stream_bytes must be a positive integer")
    if (type(timeout_seconds) not in (int, float)
            or not math.isfinite(timeout_seconds) or timeout_seconds <= 0):
        raise ValueError("timeout_seconds must be positive and finite")
    if not command or isinstance(command, (str, bytes)) or not command[0] or any(
            not isinstance(arg, str) or "\0" in arg for arg in command):
        raise ValueError("command must be a nonempty argument sequence")
    if not isinstance(environment, Mapping) or any(
            not isinstance(k, str) or not isinstance(v, str) or not k
            or "=" in k or "\0" in k or "\0" in v for k, v in environment.items()):
        raise ValueError("environment must be an explicit string mapping")
    cwd, output_dir = Path(cwd), Path(output_dir)
    if not cwd.is_absolute() or not cwd.is_dir():
        raise ValueError("cwd must be an absolute existing directory")
    if not output_dir.is_absolute() or output_dir.parent.resolve() != output_dir.parent:
        raise ValueError("output_dir must have an absolute resolved parent")
    output_dir.mkdir(mode=0o700)
    streams = {name: {"bytes": 0, "digest": hashlib.sha256(),
                      "eof": False, "first_receipt_monotonic_ns": None,
                      "last_receipt_monotonic_ns": None}
               for name in ("stdout", "stderr")}
    started = time.monotonic_ns()
    started_at = datetime.now(UTC).isoformat()
    deadline = time.monotonic() + timeout_seconds
    total = 0
    termination = "exited"
    with ExitStack() as stack:
        descriptors = {}
        for name in streams:
            fd = os.open(output_dir / ("native." + name),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            stack.callback(os.close, fd)
            descriptors[name] = fd
        selector = stack.enter_context(selectors.DefaultSelector())
        process = subprocess.Popen(list(command), cwd=cwd, env=dict(environment),
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        try:
            for name in streams:
                pipe = stack.enter_context(getattr(process, name))
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
                        streams[name]["eof"] = True
                        selector.unregister(key.fileobj)
                        continue
                    now = time.monotonic_ns()
                    info = streams[name]
                    if info["first_receipt_monotonic_ns"] is None:
                        info["first_receipt_monotonic_ns"] = now
                    info["last_receipt_monotonic_ns"] = now
                    retained = data[:max_stream_bytes - total]
                    _write_all(descriptors[name], retained)
                    info["digest"].update(retained)
                    info["bytes"] += len(retained)
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
        pending = output_dir / ".capture.pending"
        fd = os.open(pending,
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        stack.callback(os.close, fd)
        _write_all(fd, (json.dumps(receipt, sort_keys=True) + "\n").encode("utf-8"))
        os.fsync(fd)
        final = output_dir / "capture.json"
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
    return receipt
