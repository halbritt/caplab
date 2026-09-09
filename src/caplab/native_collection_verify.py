"""Read-only integrity and consistency checks for anchored native collections."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from caplab.native_collection import COLLECTION_INTENT_SCHEMAS, COLLECTION_SCHEMAS
from caplab.native_runtime import _validated_invocation
from caplab.task_capture_verify import CaptureVerificationError, _Reader, _count, _digest, _inventory, _open, _require


def _host_path(value, label: str) -> PurePosixPath:
    _require(isinstance(value, str) and value.startswith("/") and value != "/"
             and not value.startswith("//") and "\0" not in value, f"invalid {label}")
    path = PurePosixPath(value)
    _require(str(path) == value and ".." not in path.parts, f"invalid {label}")
    return path


def _selection(policy_path: Path, intent: dict, preparation: dict, invocation: dict) -> tuple[dict, dict]:
    try:
        plan = _validated_invocation(policy_path, invocation, preparation.get("invocation_sha256"))
    except ValueError as error:
        raise CaptureVerificationError("invalid collection invocation") from error
    _require(intent.get("invocation_sha256") == plan["invocation_sha256"], "intent invocation differs")
    _require(intent.get("invocation_file_sha256") == preparation.get("invocation_file_sha256"),
             "invocation file links differ")
    source = _host_path(intent.get("source_root"), "collection source root")
    runtime = source / "runtime"
    expected = {name: str(runtime / PurePosixPath(path).relative_to(plan["runtime_root"]))
                for name, path in plan["capture_locations"].items()}
    _require(preparation.get("custody_root") == str(source) and preparation.get("runtime_root") == str(runtime),
             "preparation roots differ from intent")
    _require(preparation.get("capture_paths") == expected, "prepared paths differ from invocation")
    if intent["schema"] == COLLECTION_INTENT_SCHEMAS[1]:
        descriptor = intent.get("runtime_source")
        _require(isinstance(descriptor, dict) and set(descriptor) == {"kind", "namespace_root", "device", "inode"},
                 "invalid descriptor runtime source")
        _require(descriptor["kind"] == "directory-descriptor" and descriptor["namespace_root"] == plan["runtime_root"],
                 "descriptor namespace differs from invocation")
        _count(descriptor["device"], "descriptor device")
        _require(_count(descriptor["inode"], "descriptor inode") > 0, "invalid descriptor inode")
        expected = dict(plan["capture_locations"])
    else:
        _require("runtime_source" not in intent, "v1 intent cannot assert descriptor provenance")
    _require(intent.get("capture_paths") == expected, "selected paths differ from invocation")
    return plan, expected


def _locations(collection: dict, expected: dict) -> dict:
    locations = collection.get("locations")
    _require(isinstance(locations, list) and len(locations) == len(expected), "invalid selected location count")
    statuses = {}
    for location in locations:
        _require(isinstance(location, dict), "invalid selected location")
        name, status = location.get("name"), location.get("status")
        _require(isinstance(name, str) and name in expected and name not in statuses,
                 "unknown or repeated selected location")
        _require(status in ("retained", "missing"), "invalid selected location status")
        kind = "directory" if name.endswith("_search_root") else "file"
        _require(location == {"name": name, "status": status, "source": expected[name], "expected_kind": kind},
                 "selected location metadata differs")
        statuses[name] = status
    _require(list(statuses) == sorted(expected), "selected locations must be sorted")
    _require(collection.get("missing_locations") == [name for name, status in statuses.items() if status == "missing"],
             "missing location summary differs")
    return statuses


def _entries(objects: int, collection: dict, intent: dict, statuses: dict) -> tuple[int, int]:
    entries = collection.get("entries")
    _require(isinstance(entries, list), "invalid native inventory")
    max_entries = _count(intent.get("max_entries"), "entry limit")
    max_bytes = _count(intent.get("max_artifact_bytes"), "artifact byte limit")
    _require(max_entries > 0 and max_bytes > 0, "collection limits must be positive")
    _require(len(entries) <= max_entries, "native inventory exceeds entry limit")
    roots = {}
    for entry in entries:
        _require(isinstance(entry, dict) and isinstance(entry.get("path"), str), "invalid native entry")
        path = entry["path"]
        name = path.split("/", 1)[0]
        _require(name in statuses and statuses[name] == "retained", "entry belongs to absent or unselected location")
        if path == name:
            roots[name] = entry.get("kind")
    for name, status in statuses.items():
        if status == "retained":
            kind = "directory" if name.endswith("_search_root") else "file"
            _require(roots.get(name) == kind, "selected root is absent or has wrong kind")
    # The existing tree verifier owns path, object, symlink and quota invariants.
    # Its synthetic parent is local metadata and consumes no retained entry.
    projected = {"source_root": intent["source_root"], "retained_bytes": collection.get("retained_artifact_bytes"),
                 "entries": [{"path": ".", "kind": "directory", "mode": 0}] + entries}
    byte_count, entry_count = _inventory(objects, projected, cwd=intent["source_root"],
                                        bytes_left=max_bytes, entries_left=max_entries + 1)
    _require(_count(collection.get("retained_entries"), "native entry count") == entry_count - 1,
             "native entry count differs")
    return byte_count, entry_count - 1


def verify_native_collection(
    policy_path: Path, custody: Path, *, expected_collection_sha256: str, max_receipt_bytes: int,
) -> dict:
    """Verify retained bytes without source reads, native interpretation or writes.

    Caller retains the independent collection digest and supplies quiescent
    custody with trusted stable parents. The receipt allowance covers all four
    JSON files; referenced payload bounds come from the anchored intent.
    """
    _digest(expected_collection_sha256)
    _require(type(max_receipt_bytes) is int and max_receipt_bytes > 0, "invalid receipt byte limit")
    custody = Path(custody)
    _require(custody.is_absolute() and custody.parent.resolve() == custody.parent,
             "custody must have an absolute resolved parent")
    reader = _Reader(max_receipt_bytes)
    with _open(None, custody, directory=True) as root:
        collection = reader.receipt(root, "collection.json", expected_collection_sha256,
                                    COLLECTION_SCHEMAS)
        intent = reader.receipt(root, "intent.json", collection.get("intent_sha256"),
                                COLLECTION_INTENT_SCHEMAS)
        _require(COLLECTION_SCHEMAS.index(collection["schema"]) == COLLECTION_INTENT_SCHEMAS.index(intent["schema"]),
                 "collection and intent versions differ")
        remaining_before = reader.remaining
        preparation = reader.receipt(root, "preparation.json", intent.get("preparation_sha256"),
                                     "caplab.native-runtime-preparation/v1")
        invocation = reader.receipt(root, "invocation.json", preparation.get("invocation_file_sha256"),
                                    "caplab.native-capture-invocation/v1")
        input_limit = _count(intent.get("max_receipt_bytes"), "source receipt byte limit")
        _require(input_limit > 0 and remaining_before - reader.remaining <= input_limit,
                 "source receipts exceed collection intent allowance")
        plan, expected = _selection(policy_path, intent, preparation, invocation)
        statuses = _locations(collection, expected)
        _require(collection.get("native_identity_verified") is False
                 and "native_capture_complete" in collection and collection["native_capture_complete"] is None,
                 "raw collection asserts native verification or completeness")
        with _open(root, "objects", directory=True) as objects:
            byte_count, entry_count = _entries(objects, collection, intent, statuses)
    return {"schema": "caplab.native-collection-inspection/v1", "collection_sha256": expected_collection_sha256,
            "integrity_verified": True, "invocation_sha256": plan["invocation_sha256"],
            "configured_tuple_id": plan["base_subject"]["tuple_id"], "profile_sha256": plan["profile_sha256"],
            "retained_artifact_bytes": byte_count, "retained_entries": entry_count,
            "verified_receipt_bytes": max_receipt_bytes - reader.remaining,
            "missing_locations": collection["missing_locations"], "native_identity_verified": False,
            **({"runtime_source": intent["runtime_source"]} if "runtime_source" in intent else {}),
            "native_capture_complete": None,
            "interpretation": "retained byte integrity and selection consistency only; no native linkage or eligibility"}
