"""Bounded cgroup accounting observations, separate from capture-overhead inference."""

from copy import deepcopy
import json
import os
from pathlib import Path
import re
import time

from caplab.task_capture_verify import _open, _read_file, _require

_FILES = ("cgroup.type", "cpu.stat", "memory.current", "memory.peak", "cgroup.events")
_MAXIMUM = 16384


def _count(value):
    _require(type(value) is int and 0 <= value < 2**64, "invalid resource count")
    return value


def _group(value):
    _require(
        type(value) is dict and set(value) == {"path", "device", "inode"},
        "invalid resource cgroup identity",
    )
    path = value["path"]
    _require(
        type(path) is str and 0 < len(path) <= 4096 and "\x00" not in path,
        "invalid resource cgroup path",
    )
    parsed = Path(path)
    _require(
        parsed.is_absolute()
        and str(parsed) == path
        and ".." not in parsed.parts
        and parsed != Path("/sys/fs/cgroup")
        and parsed.is_relative_to("/sys/fs/cgroup"),
        "resource path must name a non-root cgroup",
    )
    _require(
        _count(value["device"]) > 0 and _count(value["inode"]) > 0,
        "invalid resource cgroup inode",
    )


def _integer(raw):
    _require(
        re.fullmatch(r"[0-9]+\n", raw) is not None, "invalid scalar resource counter"
    )
    return _count(int(raw))


def _fields(raw):
    pairs = [line.split() for line in raw.splitlines()]
    _require(
        1 <= len(pairs) <= 256
        and all(
            len(row) == 2
            and re.fullmatch(r"[a-z][a-z0-9_.]*", row[0])
            and re.fullmatch(r"[0-9]+", row[1])
            for row in pairs
        ),
        "invalid keyed resource counters",
    )
    result = {key: _count(int(value)) for key, value in pairs}
    _require(len(result) == len(pairs), "duplicate resource counter")
    return result


def _values(raw):
    _require(
        type(raw) is dict and set(raw) == set(_FILES), "invalid resource raw inventory"
    )
    for value in raw.values():
        _require(
            type(value) is str and value.isascii() and 0 < len(value) <= _MAXIMUM,
            "resource raw field exceeds allowance or is not ASCII",
        )
    _require(raw["cgroup.type"] == "domain\n", "resource cgroup must be a domain")
    cpu, events = _fields(raw["cpu.stat"]), _fields(raw["cgroup.events"])
    _require(
        {"usage_usec", "user_usec", "system_usec"} <= set(cpu),
        "required CPU counter missing",
    )
    _require(
        {"populated", "frozen"} <= set(events)
        and all(events[k] in (0, 1) for k in ("populated", "frozen")),
        "required cgroup event missing or invalid",
    )
    return {
        "cpu_usage_usec": cpu["usage_usec"],
        "cpu_user_usec": cpu["user_usec"],
        "cpu_system_usec": cpu["system_usec"],
        "memory_current_bytes": _integer(raw["memory.current"]),
        "memory_peak_bytes": _integer(raw["memory.peak"]),
        "populated": events["populated"],
        "frozen": events["frozen"],
    }


def _snapshot(value):
    _require(
        type(value) is dict
        and set(value)
        == {
            "schema",
            "cgroup",
            "kernel_release",
            "started_monotonic_ns",
            "finished_monotonic_ns",
            "raw",
            "values",
            "study_eligible",
        },
        "invalid resource observation",
    )
    _require(
        value["schema"] == "caplab.cgroup-resource-observation/v1"
        and value["study_eligible"] is False,
        "unsupported resource observation",
    )
    _group(value["cgroup"])
    _require(
        type(value["kernel_release"]) is str
        and 0 < len(value["kernel_release"]) <= 256
        and "\x00" not in value["kernel_release"],
        "invalid resource kernel release",
    )
    _require(
        0
        < _count(value["started_monotonic_ns"])
        <= _count(value["finished_monotonic_ns"]),
        "invalid resource observation interval",
    )
    expected = _values(value["raw"])
    _require(
        json.dumps(value["values"], sort_keys=True)
        == json.dumps(expected, sort_keys=True),
        "resource raw and parsed values disagree",
    )


def read_cgroup_resources(cgroup_path: Path) -> dict:
    """Read an owned domain cgroup without resetting counters or moving processes.

    Caller owns cgroup provenance/lifetime and excludes deletion, replacement,
    counter resets and outside migrations. Sequential reads are not atomic.
    All files are required; an unavailable observation is never zero usage.
    """
    path = Path(cgroup_path)
    _require(
        path.is_absolute()
        and path.resolve() == path
        and path != Path("/sys/fs/cgroup")
        and path.is_relative_to("/sys/fs/cgroup"),
        "cgroup must be a resolved non-root kernel path",
    )
    started = time.monotonic_ns()
    with _open(None, path, directory=True) as group:
        info = os.fstat(group)
        identity = {"path": str(path), "device": info.st_dev, "inode": info.st_ino}
        raw = {
            name: _read_file(group, name, _MAXIMUM, retain=True)[0].decode("ascii")
            for name in _FILES
        }
        current = path.stat()
        _require(
            (current.st_dev, current.st_ino) == (info.st_dev, info.st_ino),
            "resource cgroup identity changed",
        )
        result = {
            "schema": "caplab.cgroup-resource-observation/v1",
            "cgroup": identity,
            "kernel_release": os.uname().release,
            "started_monotonic_ns": started,
            "finished_monotonic_ns": time.monotonic_ns(),
            "raw": raw,
            "values": _values(raw),
            "study_eligible": False,
        }
    _snapshot(result)
    return result


def verify_cgroup_resource_interval(
    before: dict, after: dict, *, expected_cgroup: dict
) -> dict:
    """Check anchored retained snapshots; no live kernel origin or overhead claim.

    CPU deltas cover reads somewhere within the two observation intervals.
    Memory peak is the ending lifetime/accounted peak, not a subtraction of peaks.
    Neither quantity isolates native processes from helpers charged to that group.
    """
    _group(expected_cgroup)
    for value in (before, after):
        _snapshot(value)
        _require(
            value["cgroup"] == expected_cgroup,
            "resource cgroup differs from independent identity",
        )
    _require(
        before["kernel_release"] == after["kernel_release"],
        "resource kernel release changed",
    )
    _require(
        before["finished_monotonic_ns"] <= after["started_monotonic_ns"],
        "resource intervals overlap or reverse",
    )
    deltas = {}
    for field in ("usage", "user", "system"):
        start, finish = (
            before["values"]["cpu_" + field + "_usec"],
            after["values"]["cpu_" + field + "_usec"],
        )
        _require(finish >= start, "resource CPU counter decreased")
        deltas[field] = finish - start
    _require(
        after["values"]["memory_peak_bytes"] >= before["values"]["memory_peak_bytes"],
        "resource memory peak decreased",
    )
    return {
        "schema": "caplab.cgroup-resource-interval/v1",
        "status": "verified-retained-consistency",
        "cgroup": deepcopy(expected_cgroup),
        "kernel_release": before["kernel_release"],
        "cpu_delta_usec": deltas,
        "accounted_memory_peak_bytes": after["values"]["memory_peak_bytes"],
        "before_memory_peak_bytes": before["values"]["memory_peak_bytes"],
        "before_memory_current_bytes": before["values"]["memory_current_bytes"],
        "after_memory_current_bytes": after["values"]["memory_current_bytes"],
        "observation_interval_ns": {
            "minimum": after["started_monotonic_ns"] - before["finished_monotonic_ns"],
            "maximum": after["finished_monotonic_ns"] - before["started_monotonic_ns"],
        },
        "kernel_origin_verified": False,
        "incremental_capture_overhead_seconds": None,
        "native_process_only_usage": False,
        "study_eligible": False,
    }
