"""Verified logical payload accounting for retained task and native bundles."""

from contextlib import ExitStack
import hashlib
from pathlib import Path

from caplab.codex_events import parse_native_json
from caplab.native_collection import COLLECTION_INTENT_SCHEMAS, COLLECTION_SCHEMAS
from caplab.native_collection_verify import _host_path, verify_native_collection
from caplab.task_capture_verify import CaptureVerificationError, _Reader, _digest, _open, _require, verify_task_capture


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
                                    COLLECTION_SCHEMAS)
        intent = reader.receipt(native_root, "intent.json", collection["intent_sha256"],
                                COLLECTION_INTENT_SCHEMAS)
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
            **({"runtime_source": native["runtime_source"]} if "runtime_source" in native else {}),
            "task_capture_complete": task["capture_complete"], "termination": task["termination"],
            "return_code": task["return_code"], "recorded_task_root_agrees": True,
            "executed_invocation_bound": False, "native_capture_complete": None,
            "capture_overhead_seconds": None, "peak_runtime_bytes": None,
            "redaction_seconds": None, "manual_redaction_seconds": None,
            "interpretation": "logical retained occurrences, including duplicate content; symlink target bytes "
            "are metadata already encoded in receipts; missing surfaces are unavailable; excludes allocated "
            "disk use, unreferenced files and runtime peaks; no native execution linkage, cost extrapolation, "
            "task success, blinding or study eligibility is established"}


def _population_input(content: bytes, expected_sha256: str, max_bytes: int, max_slots: int) -> dict:
    _require(isinstance(content, bytes) and len(content) <= max_bytes, "population input exceeds byte allowance or is not bytes")
    _require(hashlib.sha256(content).hexdigest() == _digest(expected_sha256), "population input hash mismatch")
    try:
        data = parse_native_json(content.decode("utf-8"))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise CaptureVerificationError("invalid population JSON") from error
    _require(isinstance(data, dict) and set(data) == {"schema", "cells"}
             and data["schema"] == "caplab.capture-population-input/v1", "invalid population input schema")
    _require(isinstance(data["cells"], list) and data["cells"], "population requires declared cells")
    cells, slots, anchors, paths = set(), set(), set(), set()
    for cell in data["cells"]:
        _require(isinstance(cell, dict) and set(cell) == {"world", "arm", "configured_tuple_id", "slots"},
                 "invalid population cell")
        for field in ("world", "arm", "configured_tuple_id"):
            _require(isinstance(cell[field], str) and cell[field].strip() and "\0" not in cell[field],
                     f"invalid cell {field}")
        key = (cell["world"], cell["arm"], cell["configured_tuple_id"])
        _require(key not in cells, "duplicate population cell")
        cells.add(key)
        _require(isinstance(cell["slots"], list), "cell slots must be an array")
        for slot in cell["slots"]:
            _require(isinstance(slot, dict) and set(slot) == {"slot_id", "task_capture", "native_collection"},
                     "invalid expected slot")
            name = slot["slot_id"]
            _require(isinstance(name, str) and name.strip() and "\0" not in name, "invalid slot ID")
            _require(name not in slots, "duplicate expected slot")
            slots.add(name)
            _require(len(slots) <= max_slots, "population exceeds slot allowance")
            for kind in ("task_capture", "native_collection"):
                anchor = slot[kind]
                if anchor is None:
                    continue
                _require(isinstance(anchor, dict) and set(anchor) == {"custody", "sha256"}, "invalid bundle anchor")
                path = str(_host_path(anchor["custody"], "bundle custody"))
                digest = _digest(anchor["sha256"])
                _require(path not in paths and digest not in anchors, "bundle path or anchor reused across population")
                paths.add(path)
                anchors.add(digest)
    return data


def _population_totals(rows: list[dict]) -> dict:
    available = [row["byte_report"] for row in rows if row["byte_report"] is not None]
    payload = sum(report["retained_logical_payload_bytes"] for report in available)
    receipts = sum(report["verified_receipt_bytes"] for report in available)
    unavailable = len(rows) - len(available)
    return {"expected_slots": len(rows), "available_pair_slots": len(available),
            "unavailable_pair_slots": unavailable,
            "available_pair_logical_payload_bytes": payload,
            "available_pair_receipt_bytes": receipts,
            "all_slot_pair_logical_payload_bytes": None if unavailable else payload,
            "all_slot_pair_receipt_bytes": None if unavailable else receipts}


def build_capture_population_report(
    policy_path: Path, content: bytes, *, expected_input_sha256: str,
    max_input_bytes: int, max_slots: int, max_receipt_bytes: int,
) -> dict:
    """Inspect the declared population; absent anchors do not imply unused slots.

    Parse and validate all input before bundle reads. Every supplied anchor is
    verified, even when its counterpart is absent. The caller owns the input
    anchor, population completeness, authorization and stable private custody.
    Receipt allowances apply separately to each invoked existing verifier.
    """
    for name, value in (("input byte", max_input_bytes), ("slot", max_slots), ("receipt byte", max_receipt_bytes)):
        _require(type(value) is int and value > 0, f"{name} allowance must be a positive integer")
    data = _population_input(content, expected_input_sha256, max_input_bytes, max_slots)
    cells, all_rows = [], []
    for cell in data["cells"]:
        rows = []
        for slot in cell["slots"]:
            task, native = slot["task_capture"], slot["native_collection"]
            byte_report = task_inspection = native_inspection = None
            missing = [kind for kind in ("task_capture", "native_collection") if slot[kind] is None]
            try:
                if not missing:
                    byte_report = build_capture_byte_report(policy_path, Path(task["custody"]), Path(native["custody"]),
                        expected_attempt_sha256=task["sha256"], expected_collection_sha256=native["sha256"],
                        max_receipt_bytes=max_receipt_bytes)
                    observed_tuple = byte_report["configured_tuple_id"]
                else:
                    if task is not None:
                        task_inspection = verify_task_capture(Path(task["custody"]),
                            expected_attempt_sha256=task["sha256"], max_receipt_bytes=max_receipt_bytes)
                    if native is not None:
                        native_inspection = verify_native_collection(policy_path, Path(native["custody"]),
                            expected_collection_sha256=native["sha256"], max_receipt_bytes=max_receipt_bytes)
                    observed_tuple = native_inspection["configured_tuple_id"] if native_inspection else None
                if observed_tuple is not None:
                    _require(observed_tuple == cell["configured_tuple_id"], "collection configured tuple differs from cell")
            except CaptureVerificationError as error:
                raise CaptureVerificationError(f"slot {slot['slot_id']!r}: {error}") from error
            rows.append({**slot, "pair_available": not missing, "anchors_not_supplied": missing,
                         "byte_report": byte_report, "task_inspection": task_inspection,
                         "native_inspection": native_inspection})
        cells.append({key: cell[key] for key in ("world", "arm", "configured_tuple_id")}
                     | {"slots": rows, "totals": _population_totals(rows)})
        all_rows.extend(rows)
    return {"schema": "caplab.capture-population-report/v1", "input_sha256": expected_input_sha256,
            "input_bytes": len(content), "cells": cells, "totals": _population_totals(all_rows),
            "population_assignment_verified": False, "study_eligibility_established": False,
            "interpretation": "Expected slots and cell labels are caller-declared. Every supplied bundle anchor "
            "is verified; absent anchors do not establish no launch or a failure cause. Pair totals cover "
            "only available bundle pairs and count retained logical occurrences, not runtime or total disk "
            "cost. Partial component inspections are separate and not included in pair totals. All-slot "
            "pair totals remain null if any pair is unavailable. No native execution, representative cost, "
            "precision, blinding, study eligibility or reviewer capability is established."}
