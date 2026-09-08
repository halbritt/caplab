"""Bounded raw custody for the output paths of one prepared native runtime."""

from __future__ import annotations

from contextlib import ExitStack
from datetime import UTC, datetime
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat

from caplab.codex_events import parse_native_json
from caplab.native_runtime import _validated_invocation
from caplab.process_capture import seal_capture_json
from caplab.task_capture import _Inventory, _unchanged
from caplab.task_capture_verify import _digest, _open, _read_file


class NativeCollectionError(ValueError):
    """Selected native outputs cannot support a sealed collection."""


def _receipt(parent: int, name: str, expected: str, schema: str, limit: int) -> tuple[dict, bytes]:
    _digest(expected)
    raw, _, digest = _read_file(parent, name, limit, retain=True)
    if digest != expected:
        raise NativeCollectionError(f"receipt-hash-mismatch:{name}")
    try:
        document = parse_native_json(raw.decode("utf-8"))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise NativeCollectionError(f"invalid-receipt:{name}") from error
    if not isinstance(document, dict) or document.get("schema") != schema:
        raise NativeCollectionError(f"invalid-receipt-schema:{name}")
    return document, raw


def _retain_receipt(path: Path, raw: bytes) -> None:
    with path.open("xb") as output:
        os.fchmod(output.fileno(), 0o600)
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())


def _collect_location(runtime_fd: int, relative: PurePosixPath, name: str,
                      expected_kind: str, inventory: _Inventory) -> bool:
    with ExitStack() as stack:
        parent, ancestors = runtime_fd, []
        for component in relative.parts[:-1]:
            try:
                fd = stack.enter_context(_open(parent, component, directory=True))
            except FileNotFoundError:
                return False
            ancestors.append((parent, component, fd, os.fstat(fd)))
            parent = fd
        try:
            observed = os.stat(relative.name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            return False
        predicate = stat.S_ISDIR if expected_kind == "directory" else stat.S_ISREG
        if not predicate(observed.st_mode):
            raise NativeCollectionError(f"unexpected-selected-object:{name}")
        inventory.visit(parent, relative.name, name)
        _unchanged(observed, os.stat(relative.name, dir_fd=parent, follow_symlinks=False), name)
        for parent_fd, component, fd, before in reversed(ancestors):
            _unchanged(before, os.fstat(fd), name)
            _unchanged(before, os.stat(component, dir_fd=parent_fd, follow_symlinks=False), name)
    return True


def collect_native_outputs(
    policy_path: Path, preparation_root: Path, *, expected_preparation_sha256: str,
    output_dir: Path, max_receipt_bytes: int, max_artifact_bytes: int, max_entries: int,
) -> dict:
    """Retain planned paths after writers stop; no native parsing or eligibility.

    The caller supplies an independent preparation anchor, quiescent source, and
    trusted stable host parents. Partial state survives failure; never retry into
    that output root. Byte/entry limits bound retention, not blocked filesystem time.
    """
    for value in (max_receipt_bytes, max_artifact_bytes, max_entries):
        if type(value) is not int or value <= 0:
            raise NativeCollectionError("limits-must-be-positive-integers")
    _digest(expected_preparation_sha256)
    preparation_root, output_dir = Path(preparation_root), Path(output_dir)
    if (not preparation_root.is_absolute() or preparation_root == Path("/")
            or preparation_root.resolve() != preparation_root):
        raise NativeCollectionError("preparation-root-must-be-resolved")
    if (not output_dir.is_absolute() or output_dir.parent.resolve() != output_dir.parent
            or output_dir.is_relative_to(preparation_root) or preparation_root.is_relative_to(output_dir)):
        raise NativeCollectionError("output-must-be-outside-preparation-with-resolved-parent")
    with _open(None, preparation_root, directory=True) as root:
        preparation, preparation_raw = _receipt(root, "preparation.json", expected_preparation_sha256,
            "caplab.native-runtime-preparation/v1", max_receipt_bytes)
        invocation, invocation_raw = _receipt(root, "invocation.json", preparation.get("invocation_file_sha256"),
            "caplab.native-capture-invocation/v1", max_receipt_bytes - len(preparation_raw))
        plan = _validated_invocation(policy_path, invocation, preparation.get("invocation_sha256"))
        runtime = preparation_root / "runtime"
        selected = {name: PurePosixPath(path).relative_to(plan["runtime_root"])
                    for name, path in plan["capture_locations"].items()}
        expected_paths = {name: str(runtime / path) for name, path in selected.items()}
        if (preparation.get("custody_root") != str(preparation_root)
                or preparation.get("runtime_root") != str(runtime)
                or preparation.get("capture_paths") != expected_paths):
            raise NativeCollectionError("preparation-layout-differs-from-plan")
        try:
            task = Path(preparation["mounts"]["task"]["source"])
        except (KeyError, TypeError) as error:
            raise NativeCollectionError("invalid-preparation-task-root") from error
        if (not task.is_absolute() or ".." in task.parts or output_dir.is_relative_to(task)
                or task.is_relative_to(output_dir)):
            raise NativeCollectionError("output-must-be-outside-task")
        with _open(root, "runtime", directory=True) as runtime_fd:
            runtime_before = os.fstat(runtime_fd)
            output_dir.mkdir(mode=0o700)
            output_dir.chmod(0o700)
            _retain_receipt(output_dir / "preparation.json", preparation_raw)
            _retain_receipt(output_dir / "invocation.json", invocation_raw)
            intent = {"schema": "caplab.native-collection-intent/v1",
                      "preparation_sha256": expected_preparation_sha256,
                      "invocation_file_sha256": hashlib.sha256(invocation_raw).hexdigest(),
                      "invocation_sha256": plan["invocation_sha256"], "source_root": str(preparation_root),
                      "capture_paths": expected_paths, "max_receipt_bytes": max_receipt_bytes,
                      "max_artifact_bytes": max_artifact_bytes, "max_entries": max_entries}
            intent_digest = seal_capture_json(output_dir, "intent.json", intent)
            payload = output_dir / "objects"
            payload.mkdir(mode=0o700)
            inventory = _Inventory(payload, max_artifact_bytes, max_entries)
            locations, started = [], datetime.now(UTC).isoformat()
            for name, relative in sorted(selected.items()):
                kind = "directory" if name.endswith("_search_root") else "file"
                present = _collect_location(runtime_fd, relative, name, kind, inventory)
                locations.append({"name": name, "source": expected_paths[name], "expected_kind": kind,
                                  "status": "retained" if present else "missing"})
            _unchanged(runtime_before, os.fstat(runtime_fd), "runtime")
            _unchanged(runtime_before, os.stat("runtime", dir_fd=root, follow_symlinks=False), "runtime")
            with _open(None, payload, directory=True) as fd:
                os.fsync(fd)
            receipt = {"schema": "caplab.native-output-collection/v1", "intent_sha256": intent_digest,
                       "started_at": started, "finished_at": datetime.now(UTC).isoformat(),
                       "locations": locations, "entries": sorted(inventory.entries, key=lambda e: e["path"]),
                       "retained_artifact_bytes": inventory.retained_bytes,
                       "retained_entries": len(inventory.entries),
                       "missing_locations": [item["name"] for item in locations if item["status"] == "missing"],
                       "native_identity_verified": False, "native_capture_complete": None,
                       "interpretation": "raw planned-path custody only; no session linkage, native completeness or eligibility"}
            seal_capture_json(output_dir, "collection.json", receipt)
            return receipt
