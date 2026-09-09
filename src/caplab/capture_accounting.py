"""Verified logical payload accounting for retained task and native bundles."""

from contextlib import ExitStack
from pathlib import Path

from caplab.native_collection_verify import verify_native_collection
from caplab.task_capture_verify import CaptureVerificationError, _Reader, _open, _require, verify_task_capture


def _surface(name: str, entries: list[dict], *, status: str = "retained") -> dict:
    present = status == "retained"
    files = sum(e["bytes"] for e in entries if e["kind"] == "file")
    links = sum(e["bytes"] for e in entries if e["kind"] == "symlink")
    return {"surface": name, "status": status,
            "entries": len(entries) if present else None,
            "file_bytes": files if present else None,
            "symlink_target_bytes": links if present else None,
            "logical_payload_bytes": files + links if present else None}


def build_capture_byte_report(
    policy_path: Path, task_custody: Path, collection_custody: Path, *,
    expected_attempt_sha256: str, expected_collection_sha256: str, max_receipt_bytes: int,
) -> dict:
    """Verify and count retained payload occurrences without reading live sources.

    Each bundle verification and the combined metadata reread has a separate
    max_receipt_bytes allowance. Caller supplies independent anchors, quiescent
    custody and trusted stable parents, as required by the underlying verifiers.
    """
    task = verify_task_capture(task_custody, expected_attempt_sha256=expected_attempt_sha256,
                               max_receipt_bytes=max_receipt_bytes)
    native = verify_native_collection(policy_path, collection_custody,
        expected_collection_sha256=expected_collection_sha256, max_receipt_bytes=max_receipt_bytes)
    reader = _Reader(max_receipt_bytes)
    with ExitStack() as stack:
        task_root = stack.enter_context(_open(None, task_custody, directory=True))
        native_root = stack.enter_context(_open(None, collection_custody, directory=True))
        attempt = reader.receipt(task_root, "attempt.json", expected_attempt_sha256,
                                 "caplab.task-attempt-capture/v1")
        task_intent = reader.receipt(task_root, "intent.json", attempt["intent_sha256"],
                                     "caplab.task-capture-intent/v1")
        collection = reader.receipt(native_root, "collection.json", expected_collection_sha256,
                                    "caplab.native-output-collection/v1")
        intent = reader.receipt(native_root, "intent.json", collection["intent_sha256"],
                                "caplab.native-collection-intent/v1")
        preparation = reader.receipt(native_root, "preparation.json", intent["preparation_sha256"],
                                     "caplab.native-runtime-preparation/v1")
        try:
            recorded_task = preparation["mounts"]["task"]["source"]
        except (KeyError, TypeError) as error:
            raise CaptureVerificationError("preparation lacks task source") from error
        _require(task_intent["cwd"] == recorded_task, "captured task differs from prepared task")
        surfaces = []
        for phase in ("before", "after"):
            folder = stack.enter_context(_open(task_root, phase, directory=True))
            inventory = reader.receipt(folder, "inventory.json", attempt[f"{phase}_inventory_sha256"],
                                       "caplab.task-inventory/v1")
            surfaces.append(_surface(f"task/{phase}", inventory["entries"]))
        for name, stream in sorted(attempt["process"]["streams"].items()):
            row = _surface(f"process/{name}", [{"kind": "file", "bytes": stream["bytes"]}])
            row["eof"] = stream["eof"]
            surfaces.append(row)
        for location in collection["locations"]:
            name = location["name"]
            entries = [e for e in collection["entries"] if e["path"].split("/", 1)[0] == name]
            surfaces.append(_surface(f"native/{name}", entries, status=location["status"]))
    files = sum(row["file_bytes"] or 0 for row in surfaces)
    links = sum(row["symlink_target_bytes"] or 0 for row in surfaces)
    _require(files + links == task["retained_task_bytes"] + task["retained_stream_bytes"]
             + native["retained_artifact_bytes"], "surface totals differ from verified bundles")
    return {"schema": "caplab.capture-byte-report/v1",
            "attempt_sha256": expected_attempt_sha256, "collection_sha256": expected_collection_sha256,
            "configured_tuple_id": native["configured_tuple_id"],
            "invocation_sha256": native["invocation_sha256"],
            "surfaces": surfaces, "retained_file_bytes": files,
            "retained_symlink_target_bytes": links, "retained_logical_payload_bytes": files + links,
            "verified_receipt_bytes": task["verified_receipt_bytes"] + native["verified_receipt_bytes"],
            "missing_locations": native["missing_locations"],
            "task_capture_complete": task["capture_complete"], "termination": task["termination"],
            "return_code": task["return_code"], "recorded_task_root_agrees": True,
            "executed_invocation_bound": False, "native_capture_complete": None,
            "capture_overhead_seconds": None, "peak_runtime_bytes": None,
            "redaction_seconds": None, "manual_redaction_seconds": None,
            "interpretation": "logical retained occurrences, including duplicate content; symlink target bytes "
            "are metadata already encoded in receipts; missing surfaces are unavailable; excludes allocated "
            "disk use, unreferenced files and runtime peaks; no native execution linkage, cost extrapolation, "
            "task success, blinding or study eligibility is established"}
