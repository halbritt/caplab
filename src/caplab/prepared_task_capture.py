"""Link a selected task input to a supervised capture before workload release."""

from pathlib import Path
import json

from caplab.task_input import _input, _content_hash, materialize_task_input
from caplab.task_capture import TASK_INVENTORY_SCHEMAS
from caplab.task_capture_verify import _require, _Reader, _open


def read_task_selection(selection, *, max_task_bytes=None, max_task_entries=None):
    """Verify selected custody and return its parsed receipt and inventory.

    Caller owns the selection's independent anchor and stable private ancestry.
    No original task source is read; the returned dictionaries are newly parsed.
    """
    _require(
        isinstance(selection, dict)
        and set(selection) == {"custody", "input_sha256", "max_receipt_bytes"},
        "invalid prepared task selection",
    )
    _require(isinstance(selection["custody"], str), "invalid task custody path")
    _require(
        type(selection["max_receipt_bytes"]) is int
        and selection["max_receipt_bytes"] > 0,
        "invalid prepared task receipt allowance",
    )
    custody = Path(selection["custody"])
    _require(
        custody.is_absolute()
        and str(custody) == selection["custody"]
        and custody.resolve() == custody,
        "task custody path must be canonical and absolute",
    )
    if max_task_bytes is not None or max_task_entries is not None:
        _require(
            type(max_task_bytes) is int
            and max_task_bytes > 0
            and type(max_task_entries) is int
            and max_task_entries > 0,
            "invalid task input ceilings",
        )
        with _open(None, custody, directory=True) as fd:
            receipt = _Reader(selection["max_receipt_bytes"]).receipt(
                fd, "input.json", selection["input_sha256"], "caplab.task-input/v1"
            )
        _require(
            type(receipt.get("max_task_bytes")) is int
            and 0 < receipt["max_task_bytes"] <= max_task_bytes
            and type(receipt.get("max_task_entries")) is int
            and 0 < receipt["max_task_entries"] <= max_task_entries,
            "prepared task input allowance exceeds ceiling",
        )
    with _input(custody, selection["input_sha256"], selection["max_receipt_bytes"]) as (
        _,
        _,
        receipt,
        inventory,
        _,
    ):
        return receipt, inventory


def verify_prepared_before(selection, before, link, *, expected_before_sha256):
    """Check an anchored link against an independently verified before receipt.

    Caller first verifies before payloads, schema, anchor and descriptor linkage.
    This function verifies selected input payloads and compares content identity;
    it does not establish workload blocking, timing or independent acceptance.
    """
    receipt, _ = read_task_selection(selection)
    expected = {
        "schema": "caplab.prepared-task-before/v1",
        "input_sha256": selection["input_sha256"],
        "before_inventory_sha256": expected_before_sha256,
        "materialization": {
            "schema": "caplab.task-input-materialization/v1",
            "input_sha256": selection["input_sha256"],
            "task_content_sha256": receipt["task_content_sha256"],
            "destination_identity": before["descriptor_identity"],
            "materialized_bytes": receipt["retained_task_bytes"],
            "materialized_entries": receipt["retained_task_entries"],
            "tree_verified": True,
            "study_eligible": False,
        },
    }
    _require(
        json.dumps(link, sort_keys=True, allow_nan=False)
        == json.dumps(expected, sort_keys=True),
        "prepared task link differs",
    )
    _require(
        _content_hash(before["entries"]) == receipt["task_content_sha256"],
        "prepared task differs from before capture",
    )
    return {
        "schema": "caplab.prepared-task-before-inspection/v1",
        "input_sha256": selection["input_sha256"],
        "task_content_sha256": receipt["task_content_sha256"],
        "before_inventory_sha256": expected_before_sha256,
        "prepared_content_agrees": True,
        "study_eligible": False,
    }


def capture_prepared_before(
    selection, recorder, descriptor, *, expected_device, expected_inode
):
    """Materialize and capture blocked work; caller seals the link before release.

    Borrow the recorder and descriptor. On error preserve partial effects and
    propagate; the caller must close the recorder and refuse workload release.
    """
    read_task_selection(selection)
    materialization = materialize_task_input(
        Path(selection["custody"]),
        descriptor,
        expected_input_sha256=selection["input_sha256"],
        expected_device=expected_device,
        expected_inode=expected_inode,
        max_receipt_bytes=selection["max_receipt_bytes"],
    )
    before_sha = recorder.capture_before(
        descriptor, expected_device=expected_device, expected_inode=expected_inode
    )
    link = {
        "schema": "caplab.prepared-task-before/v1",
        "input_sha256": selection["input_sha256"],
        "before_inventory_sha256": before_sha,
        "materialization": materialization,
    }
    with _open(None, recorder.output_dir / "before", directory=True) as fd:
        before = _Reader(selection["max_receipt_bytes"]).receipt(
            fd, "inventory.json", before_sha, TASK_INVENTORY_SCHEMAS
        )
    verify_prepared_before(selection, before, link, expected_before_sha256=before_sha)
    return link
