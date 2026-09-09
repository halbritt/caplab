"""Prospective task inventories around a separately authorized, contained process."""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import math
import os
from pathlib import Path
import stat
from typing import Mapping, Sequence

from caplab.process_capture import capture_process, seal_capture_json


TASK_ATTEMPT_SCHEMAS = ("caplab.task-attempt-capture/v1", "caplab.task-attempt-capture/v2")
TASK_INTENT_SCHEMAS = ("caplab.task-capture-intent/v1", "caplab.task-capture-intent/v2")
TASK_INVENTORY_SCHEMAS = ("caplab.task-inventory/v1", "caplab.task-inventory/v2")


class TaskCaptureError(ValueError):
    """Task custody is incomplete and must not be used as an eligible attempt."""


@dataclass(frozen=True)
class TaskCaptureLimits:
    max_stream_bytes: int
    max_task_bytes: int
    max_task_entries: int
    timeout_seconds: float

    def __post_init__(self):
        for name in ("max_stream_bytes", "max_task_bytes", "max_task_entries"):
            if type(getattr(self, name)) is not int or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if (type(self.timeout_seconds) not in (int, float)
                or not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0):
            raise ValueError("timeout_seconds must be positive and finite")


def _source_stat(info: os.stat_result) -> dict:
    return {name: getattr(info, "st_" + name) for name in
            ("dev", "ino", "mode", "nlink", "size", "mtime_ns", "ctime_ns")}


def _unchanged(before: os.stat_result, after: os.stat_result, path: str) -> None:
    if _source_stat(before) != _source_stat(after):
        raise TaskCaptureError(f"source-changed:{path}")


def _names(fd: int, limit: int, overflow_reason: str) -> list[str]:
    names = []
    with os.scandir(fd) as children:
        for child in children:
            if len(names) >= limit:
                raise TaskCaptureError(overflow_reason)
            names.append(child.name)
    return sorted(names)


class _Inventory:
    def __init__(self, output: Path, bytes_left: int, entries_left: int):
        self.output = output
        self.bytes_left = bytes_left
        self.entries_left = entries_left
        self.entries: list[dict] = []
        self.retained_bytes = 0

    def _retain_file(self, parent: int, name: str, before: os.stat_result, relative: str) -> dict:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            opened = os.fstat(fd)
            _unchanged(before, opened, relative)
            if not stat.S_ISREG(opened.st_mode):
                raise TaskCaptureError(f"unsupported-task-object:{relative}")
            destination = f"object-{len(self.entries):08d}"
            digest = hashlib.sha256()
            size = 0
            with (self.output / destination).open("xb") as retained:
                os.fchmod(retained.fileno(), 0o600)
                while True:
                    chunk = os.read(fd, min(65536, self.bytes_left + 1))
                    if not chunk:
                        break
                    prefix = chunk[:self.bytes_left]
                    retained.write(prefix)
                    digest.update(prefix)
                    size += len(prefix)
                    self.retained_bytes += len(prefix)
                    self.bytes_left -= len(prefix)
                    if len(prefix) != len(chunk):
                        retained.flush()
                        os.fsync(retained.fileno())
                        raise TaskCaptureError(f"task-byte-limit:{relative}")
                retained.flush()
                os.fsync(retained.fileno())
            _unchanged(opened, os.fstat(fd), relative)
            _unchanged(opened, os.stat(name, dir_fd=parent, follow_symlinks=False), relative)
            if size != opened.st_size:
                raise TaskCaptureError(f"source-size-changed:{relative}")
            return {"kind": "file", "bytes": size, "sha256": digest.hexdigest(), "object": destination}
        finally:
            os.close(fd)

    def visit(self, parent: int, name: str, relative: str) -> None:
        if self.entries_left == 0:
            raise TaskCaptureError("task-entry-limit")
        self.entries_left -= 1
        before = os.stat(name, dir_fd=parent, follow_symlinks=False)
        entry = {"path": relative, "mode": stat.S_IMODE(before.st_mode),
                 "source_stat": _source_stat(before)}
        self.entries.append(entry)
        if stat.S_ISDIR(before.st_mode):
            entry["kind"] = "directory"
            fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            try:
                _unchanged(before, os.fstat(fd), relative)
                names = _names(fd, self.entries_left, "task-entry-limit")
                for child in names:
                    self.visit(fd, child, child if relative == "." else relative + "/" + child)
                if names != _names(fd, len(names), f"source-entries-changed:{relative}"):
                    raise TaskCaptureError(f"source-entries-changed:{relative}")
                _unchanged(before, os.fstat(fd), relative)
                _unchanged(before, os.stat(name, dir_fd=parent, follow_symlinks=False), relative)
            finally:
                os.close(fd)
        elif stat.S_ISREG(before.st_mode):
            entry.update(self._retain_file(parent, name, before, relative))
        elif stat.S_ISLNK(before.st_mode):
            target = os.fsencode(os.readlink(name, dir_fd=parent))
            if len(target) > self.bytes_left:
                raise TaskCaptureError(f"task-byte-limit:{relative}")
            self.bytes_left -= len(target)
            self.retained_bytes += len(target)
            entry.update(kind="symlink", target_base64=base64.b64encode(target).decode("ascii"), bytes=len(target))
            _unchanged(before, os.stat(name, dir_fd=parent, follow_symlinks=False), relative)
        else:
            raise TaskCaptureError(f"unsupported-task-object:{relative}")


def _inventory(root: Path, output: Path, bytes_left: int, entries_left: int) -> tuple[dict, str]:
    output.mkdir(mode=0o700)
    started_at = datetime.now(UTC).isoformat()
    inventory = _Inventory(output, bytes_left, entries_left)
    parent = os.open(root.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        inventory.visit(parent, root.name, ".")
    finally:
        os.close(parent)
    receipt = {"schema": "caplab.task-inventory/v1", "source_root": str(root),
               "started_at": started_at, "finished_at": datetime.now(UTC).isoformat(),
               "retained_bytes": inventory.retained_bytes,
               "entries": sorted(inventory.entries, key=lambda e: e["path"])}
    digest = seal_capture_json(output, "inventory.json", receipt)
    return receipt, digest


def _changes(before: dict, after: dict) -> list[dict]:
    old = {e["path"]: e for e in before["entries"]}
    new = {e["path"]: e for e in after["entries"]}
    changes = []
    for path in sorted(old.keys() | new.keys()):
        if path not in old:
            changes.append({"path": path, "change": "added"})
        elif path not in new:
            changes.append({"path": path, "change": "deleted"})
        else:
            fields = [field for field in ("kind", "mode", "bytes", "sha256", "target_base64")
                      if old[path].get(field) != new[path].get(field)]
            if fields:
                changes.append({"path": path, "change": "modified", "fields": fields})
    return changes


def capture_task_attempt(
    command: Sequence[str], *, task_root: Path, environment: Mapping[str, str],
    output_dir: Path, limits: TaskCaptureLimits,
) -> dict:
    """Retain quiescent task trees around an owned process; no native eligibility claim."""
    if isinstance(command, (str, bytes)) or not command:
        raise ValueError("command must be a nonempty argument sequence")
    command, environment = list(command), dict(environment)
    if not isinstance(limits, TaskCaptureLimits):
        raise ValueError("limits must be TaskCaptureLimits")
    task_root, output_dir = Path(task_root), Path(output_dir)
    if (not task_root.is_absolute() or task_root.resolve() != task_root
            or not task_root.is_dir() or task_root == Path("/")):
        raise ValueError("task_root must be an absolute resolved directory below root")
    if (not output_dir.is_absolute() or output_dir.parent.resolve() != output_dir.parent
            or output_dir.is_relative_to(task_root)):
        raise ValueError("output_dir must have a resolved parent outside the task tree")
    output_dir.mkdir(mode=0o700)
    intent = {"schema": "caplab.task-capture-intent/v1", "command": list(command),
              "cwd": str(task_root), "environment": dict(environment), "limits": asdict(limits)}
    intent_digest = seal_capture_json(output_dir, "intent.json", intent)
    phase = "before"
    try:
        before, before_digest = _inventory(task_root, output_dir / "before",
                                           limits.max_task_bytes, limits.max_task_entries)
        if len(before["entries"]) == limits.max_task_entries:
            raise TaskCaptureError("task-entry-limit:no-final-root-allowance")
        phase = "process"
        process = capture_process(command, cwd=task_root, environment=environment,
                                  output_dir=output_dir / "process", max_stream_bytes=limits.max_stream_bytes,
                                  timeout_seconds=limits.timeout_seconds)
        phase = "after"
        after, after_digest = _inventory(task_root, output_dir / "after",
                                         limits.max_task_bytes - before["retained_bytes"],
                                         limits.max_task_entries - len(before["entries"]))
    except TaskCaptureError as error:
        reason = str(error)
        seal_capture_json(output_dir, "failure.json", {
            "schema": "caplab.task-capture-failure/v1", "phase": phase,
            "intent_sha256": intent_digest, "reason": reason,
            "truncated": reason.startswith(("task-byte-limit", "task-entry-limit")),
        })
        raise
    receipt = {"schema": "caplab.task-attempt-capture/v1", "intent_sha256": intent_digest,
               "before_inventory_sha256": before_digest, "after_inventory_sha256": after_digest,
               "process_capture_sha256": hashlib.sha256((output_dir / "process/capture.json").read_bytes()).hexdigest(),
               "retained_task_bytes": before["retained_bytes"] + after["retained_bytes"],
               "retained_task_entries": len(before["entries"]) + len(after["entries"]),
               "process": process, "changes": _changes(before, after),
               "capture_complete": process["streams_complete"],
               "interpretation": "observed final task changes; no intermediate-write, containment, native identity or eligibility claim"}
    seal_capture_json(output_dir, "attempt.json", receipt)
    return receipt
