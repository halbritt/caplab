"""Compare overlapping entries after each capture bundle has been verified."""

import json
from pathlib import PurePosixPath

from caplab.task_capture_verify import _require


def _subtree(entries: list[dict], prefix: str) -> dict[str, str]:
    selected = {}
    for entry in entries:
        path = entry["path"]
        if prefix == ".":
            relative = path
        elif path == prefix:
            relative = "."
        elif path.startswith(prefix + "/"):
            relative = path[len(prefix) + 1 :]
        else:
            continue
        _require(relative not in selected, "duplicate overlap path")
        # Paths have been translated; each copy owns different payload locators.
        selected[relative] = json.dumps(
            {
                key: value
                for key, value in entry.items()
                if key not in ("path", "object")
            },
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    return selected


def compare_verified_capture_overlap(
    *,
    task_after: dict,
    native: dict,
    retained_task: dict,
    retained_runtime: dict,
) -> dict:
    """Borrow verified receipts and compare final source entries without I/O.

    The caller must first verify anchors, every payload, supported receipt
    schemas, source/descriptor linkage and allowances. This function does not
    validate custody or prove quiescence, provenance, or capture completeness.
    """
    _require(
        task_after["source_root"] == retained_task["source_root"],
        "overlap task roots differ",
    )
    task = _subtree(task_after["entries"], ".")
    _require(
        task == _subtree(retained_task["entries"], "."),
        "overlapping entries differ: task",
    )
    runtime = PurePosixPath(retained_runtime["source_root"])
    _require(runtime.is_absolute(), "overlap runtime root is not absolute")
    locations = []
    for location in native["locations"]:
        source = PurePosixPath(location["source"])
        _require(
            source.is_relative_to(runtime) and ".." not in source.parts,
            "native location is outside retained runtime",
        )
        prefix = str(source.relative_to(runtime))
        retained = _subtree(retained_runtime["entries"], prefix)
        selected = _subtree(native["entries"], location["name"])
        if location["status"] == "missing":
            _require(
                not retained and not selected,
                "missing native location exists in retained overlap",
            )
        else:
            _require(
                location["status"] == "retained" and selected and selected == retained,
                "overlapping entries differ: " + location["name"],
            )
        locations.append(
            {
                "name": location["name"],
                "source": location["source"],
                "status": location["status"],
                "entries": len(selected),
            }
        )
    return {
        "schema": "caplab.capture-overlap-comparison/v1",
        "overlapping_entries_agree": True,
        "task_entries": len(task),
        "native_locations": locations,
        "payload_integrity_verified_here": False,
        "native_capture_complete": None,
        "study_eligible": False,
    }
