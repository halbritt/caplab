"""Read-only integrity checks for anchored task captures; no admission authority."""

from __future__ import annotations

import base64
from contextlib import ExitStack, contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from caplab.codex_events import parse_native_json
from caplab.task_capture import TaskCaptureLimits, _changes


class CaptureVerificationError(ValueError):
    """The retained bundle cannot support a consistent inspection report."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CaptureVerificationError(message)


def _count(value, label: str) -> int:
    _require(type(value) is int and value >= 0, f"invalid {label}")
    return value


def _digest(value) -> str:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
             "invalid SHA-256")
    return value


@contextmanager
def _open(parent: int | None, name: str | Path, *, directory: bool = False):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    if directory:
        flags |= os.O_DIRECTORY
    fd = os.open(name, flags, dir_fd=parent)
    try:
        _require((stat.S_ISDIR if directory else stat.S_ISREG)(os.fstat(fd).st_mode),
                 "custody object has unsupported type")
        yield fd
    finally:
        os.close(fd)


def _identity(info):
    return tuple(getattr(info, "st_" + key) for key in
                 ("dev", "ino", "mode", "nlink", "size", "mtime_ns", "ctime_ns"))


def _read_file(parent: int, name: str, limit: int, *, retain: bool) -> tuple[bytes, int, str]:
    digest, chunks, size = hashlib.sha256(), [], 0
    with _open(parent, name) as fd:
        before = _identity(os.fstat(fd))
        _require(os.fstat(fd).st_size <= limit, "custody file exceeds byte allowance")
        while True:
            chunk = os.read(fd, min(65536, limit - size + 1))
            if not chunk:
                break
            size += len(chunk)
            _require(size <= limit, "custody file exceeds byte allowance")
            digest.update(chunk)
            if retain:
                chunks.append(chunk)
        _require(before == _identity(os.fstat(fd)) == _identity(
            os.stat(name, dir_fd=parent, follow_symlinks=False)), "custody file changed during read")
    return b"".join(chunks), size, digest.hexdigest()


class _Reader:
    def __init__(self, receipt_bytes: int):
        self.remaining = receipt_bytes

    def receipt(self, parent: int, name: str, expected: str, schema: str | tuple[str, ...]) -> dict:
        expected = _digest(expected)
        raw, size, digest = _read_file(parent, name, self.remaining, retain=True)
        self.remaining -= size
        _require(digest == expected, f"receipt hash mismatch: {name}")
        try:
            document = parse_native_json(raw.decode("utf-8"))
        except (ValueError, UnicodeError, RecursionError) as error:
            raise CaptureVerificationError(f"invalid receipt JSON: {name}") from error
        schemas = (schema,) if isinstance(schema, str) else schema
        _require(isinstance(document, dict) and document.get("schema") in schemas,
                 f"unsupported receipt schema: {name}")
        return document


def _payload(parent: int, name: str, entry: dict) -> None:
    expected = _digest(entry.get("sha256"))
    size = _count(entry.get("bytes"), "payload bytes")
    _, observed_size, observed_digest = _read_file(parent, name, size, retain=False)
    _require(size == observed_size and expected == observed_digest, "payload size or hash mismatch")


def _inventory(parent: int, receipt: dict, *, cwd: str, bytes_left: int, entries_left: int) -> tuple[int, int]:
    _require(receipt.get("source_root") == cwd, "inventory source root differs from intent")
    entries = receipt.get("entries")
    _require(isinstance(entries, list) and 0 < len(entries) <= entries_left,
             "invalid inventory entry count")
    paths, objects, total = {}, set(), 0
    for entry in entries:
        _require(isinstance(entry, dict), "invalid inventory entry")
        path, kind = entry.get("path"), entry.get("kind")
        _require(isinstance(path, str) and path and "\0" not in path and
                 (path == "." or all(part not in ("", ".", "..") for part in path.split("/"))),
                 "invalid inventory path")
        _require(path not in paths, "duplicate inventory path")
        _require(kind in ("directory", "file", "symlink"), "unsupported inventory kind")
        mode = _count(entry.get("mode"), "inventory mode")
        _require(mode <= 0o7777, "invalid inventory mode")
        paths[path] = kind
        if kind == "directory":
            _require(not any(key in entry for key in ("bytes", "sha256", "object", "target_base64")),
                     "directory has payload fields")
            continue
        total += _count(entry.get("bytes"), "inventory bytes")
        _require(total <= bytes_left, "inventory exceeds task byte limit")
        if kind == "file":
            name = entry.get("object")
            _require(isinstance(name, str) and re.fullmatch(r"object-[0-9]{8,}", name) is not None,
                     "invalid inventory object locator")
            _require(name not in objects and "target_base64" not in entry,
                     "duplicate object or inconsistent file fields")
            objects.add(name)
            _payload(parent, name, entry)
        else:
            _require("sha256" not in entry and "object" not in entry, "symlink has file fields")
            try:
                encoded = entry.get("target_base64")
                _require(isinstance(encoded, str), "invalid link target")
                target = base64.b64decode(encoded, validate=True)
            except ValueError as error:
                raise CaptureVerificationError("invalid link target") from error
            _require(len(target) == entry["bytes"] and target and b"\0" not in target and
                     base64.b64encode(target).decode("ascii") == encoded, "invalid link target")
    _require(list(paths) == sorted(paths) and paths.get(".") == "directory",
             "inventory must be sorted with a directory root")
    for path in paths:
        if path != ".":
            parent_path = path.rpartition("/")[0] or "."
            _require(paths.get(parent_path) == "directory", "inventory parent is absent or not a directory")
    _require(_count(receipt.get("retained_bytes"), "retained inventory bytes") == total,
             "inventory byte count mismatch")
    return total, len(entries)


def _process(parent: int, receipt: dict, limits: TaskCaptureLimits) -> None:
    _require(_count(receipt.get("max_stream_bytes"), "stream limit") == limits.max_stream_bytes,
             "stream limit differs from intent")
    timeout = receipt.get("timeout_seconds")
    _require(type(timeout) in (int, float) and timeout == limits.timeout_seconds,
             "process timeout differs from intent")
    _require(type(receipt.get("return_code")) is int, "invalid process return code")
    termination, complete = receipt.get("termination"), receipt.get("streams_complete")
    _require(termination in ("exited", "timeout", "byte-limit") and type(complete) is bool,
             "invalid process completion fields")
    streams = receipt.get("streams")
    _require(isinstance(streams, dict) and set(streams) == {"stdout", "stderr"}, "invalid stream inventory")
    total, eof = 0, []
    for name, entry in streams.items():
        _require(isinstance(entry, dict) and entry.get("path") == "native." + name,
                 "invalid stream locator")
        _require(type(entry.get("eof")) is bool, "invalid stream EOF")
        eof.append(entry["eof"])
        total += _count(entry.get("bytes"), "stream bytes")
        _require(total <= limits.max_stream_bytes, "streams exceed byte limit")
        _payload(parent, "native." + name, entry)
    _require(_count(receipt.get("retained_stream_bytes"), "retained stream bytes") == total,
             "stream byte count mismatch")
    _require(complete == (termination == "exited" and all(eof)), "inconsistent stream completeness")
    _require(termination != "exited" or complete, "exited capture lacks EOF")
    _require(termination != "byte-limit" or total == limits.max_stream_bytes,
             "byte-limit capture lacks full prefix")


def verify_task_capture(
    custody: Path, *, expected_attempt_sha256: str, max_receipt_bytes: int,
) -> dict:
    """Check anchored bytes and summaries without opening source paths or executing intent.

    The caller retains the independent attempt digest, bounds combined JSON bytes,
    and supplies quiescent custody with trusted stable parents. Payload read bounds
    come from the anchored capture limits. OSError and CaptureVerificationError
    propagate; success checks integrity, not eligibility or publication history.
    """
    _digest(expected_attempt_sha256)
    _require(type(max_receipt_bytes) is int and max_receipt_bytes > 0, "invalid receipt byte limit")
    custody = Path(custody)
    _require(custody.is_absolute() and custody.parent.resolve() == custody.parent,
             "custody must have an absolute resolved parent")
    reader = _Reader(max_receipt_bytes)
    with ExitStack() as stack:
        root = stack.enter_context(_open(None, custody, directory=True))
        attempt = reader.receipt(root, "attempt.json", expected_attempt_sha256, "caplab.task-attempt-capture/v1")
        intent = reader.receipt(root, "intent.json", attempt.get("intent_sha256"), "caplab.task-capture-intent/v1")
        try:
            limits = TaskCaptureLimits(**intent["limits"])
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            raise CaptureVerificationError("invalid capture limits") from error
        cwd = intent.get("cwd")
        _require(isinstance(cwd, str) and cwd.startswith("/") and "\0" not in cwd, "invalid intent cwd")
        before_fd, after_fd, process_fd = [stack.enter_context(_open(root, name, directory=True))
                                          for name in ("before", "after", "process")]
        before = reader.receipt(before_fd, "inventory.json", attempt.get("before_inventory_sha256"),
                                "caplab.task-inventory/v1")
        after = reader.receipt(after_fd, "inventory.json", attempt.get("after_inventory_sha256"),
                               "caplab.task-inventory/v1")
        process = reader.receipt(process_fd, "capture.json", attempt.get("process_capture_sha256"),
                                 "caplab.process-capture/v1")
        _require(json.dumps(attempt.get("process"), sort_keys=True) == json.dumps(process, sort_keys=True),
                 "embedded process differs from linked receipt")
        before_bytes, before_entries = _inventory(before_fd, before, cwd=cwd,
            bytes_left=limits.max_task_bytes, entries_left=limits.max_task_entries)
        after_bytes, after_entries = _inventory(after_fd, after, cwd=cwd,
            bytes_left=limits.max_task_bytes - before_bytes, entries_left=limits.max_task_entries - before_entries)
        _process(process_fd, process, limits)
        _require(_count(attempt.get("retained_task_bytes"), "task bytes") == before_bytes + after_bytes,
                 "attempt task byte count mismatch")
        _require(_count(attempt.get("retained_task_entries"), "task entries") == before_entries + after_entries,
                 "attempt task entry count mismatch")
        changes = _changes(before, after)
        _require(attempt.get("changes") == changes, "attempt change summary mismatch")
        _require(type(attempt.get("capture_complete")) is bool and
                 attempt["capture_complete"] == process["streams_complete"], "attempt completeness mismatch")
    return {"schema": "caplab.task-capture-inspection/v1", "attempt_sha256": expected_attempt_sha256,
            "integrity_verified": True, "capture_complete": attempt["capture_complete"],
            "termination": process["termination"], "return_code": process["return_code"],
            "retained_task_bytes": before_bytes + after_bytes,
            "retained_task_entries": before_entries + after_entries,
            "retained_stream_bytes": process["retained_stream_bytes"],
            "verified_receipt_bytes": max_receipt_bytes - reader.remaining, "changes": changes,
            "interpretation": "byte integrity and summary consistency only; no eligibility or task-success decision"}
