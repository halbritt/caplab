"""Deterministic public export of one exact qualification claim series."""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from caplab.runtime.canonical import canonical_json, sha256_hex

from .ledger import FilesystemQualificationLedger


_CATALOG_FILENAME = "qualification-schema-catalog-v1.json"
_CLAIM_SCHEMA_ID = "https://caplab.local/contracts/qualification-claim-v1.schema.json"
_EXPORT_SCHEMA_ID = "https://caplab.local/contracts/qualification-export-v1.schema.json"
_HEX = frozenset("0123456789abcdef")


class QualificationExportError(ValueError):
    """The selected claim series cannot produce a trustworthy export."""


def build_export(
    ledger: FilesystemQualificationLedger,
    binding_id: str,
    capability: Mapping[str, Any],
    *,
    contracts_directory: Path,
    producer_version: str,
    producer_commit: str,
    claim_validator: Callable[[Mapping[str, Any], Any], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(producer_version, str) or not producer_version:
        raise QualificationExportError("producer_version_invalid")
    if not _is_commit(producer_commit):
        raise QualificationExportError("producer_commit_invalid")
    catalog = _load_catalog(Path(contracts_directory))
    history = ledger.history(
        binding_id,
        capability,
        validator=claim_validator,
    )
    claims = history["claims"]
    if not claims:
        raise QualificationExportError("selected_claim_series_empty")
    for claim in claims:
        _verify_claim_identity(claim)
        if claim["binding"]["binding_id"] != binding_id:
            raise QualificationExportError("claim_binding_selection_mismatch")
        if canonical_json(claim["capability"]) != canonical_json(capability):
            raise QualificationExportError("claim_capability_selection_mismatch")
    claims.sort(key=lambda claim: claim["claim_id"])
    if len({claim["claim_id"] for claim in claims}) != len(claims):
        raise QualificationExportError("duplicate_claim_id")
    claim_schema = catalog[_CLAIM_SCHEMA_ID]
    export_schema = catalog[_EXPORT_SCHEMA_ID]
    body: dict[str, Any] = {
        "schema_version": _schema_version(export_schema["document"]),
        "selection": {
            "binding_id": binding_id,
            "capability": json.loads(canonical_json(capability)),
        },
        "schemas": {
            "claim": {
                "schema_version": _schema_version(claim_schema["document"]),
                "sha256": claim_schema["sha256"],
            },
            "export": {
                "schema_version": _schema_version(export_schema["document"]),
                "sha256": export_schema["sha256"],
            },
        },
        "claims": claims,
        "producer": {
            "product": "caplab",
            "version": producer_version,
            "commit": producer_commit,
        },
    }
    export_id = f"export-{sha256_hex(canonical_json(body))}"
    return json.loads(canonical_json({**body, "export_id": export_id}))


def write_export_exclusive(path: Path, document: Mapping[str, Any]) -> None:
    output = Path(path)
    _require_directory(output.parent, "export_output_parent")
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(output, flags, 0o440)
    except FileExistsError as error:
        raise QualificationExportError("export_output_exists") from error
    except OSError as error:
        raise QualificationExportError("export_output_open_failed") from error
    with os.fdopen(descriptor, "wb", closefd=True) as stream:
        stream.write(canonical_json(document) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    _fsync_directory(output.parent)


def _load_catalog(contracts_directory: Path) -> dict[str, dict[str, Any]]:
    _require_directory(contracts_directory, "contracts_directory")
    catalog_bytes = _read_regular(contracts_directory / _CATALOG_FILENAME)
    try:
        catalog = json.loads(catalog_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise QualificationExportError("schema_catalog_invalid_json") from error
    if (
        not isinstance(catalog, dict)
        or set(catalog) != {"schema_version", "resources"}
        or catalog.get("schema_version") != "caplab-qualification-schema-catalog/1"
        or not isinstance(catalog.get("resources"), list)
    ):
        raise QualificationExportError("schema_catalog_shape_invalid")
    resources: dict[str, dict[str, Any]] = {}
    for entry in catalog["resources"]:
        if not isinstance(entry, dict) or set(entry) != {"id", "path", "sha256"}:
            raise QualificationExportError("schema_catalog_resource_invalid")
        resource_id = entry["id"]
        filename = entry["path"]
        expected_sha256 = entry["sha256"]
        if (
            not isinstance(resource_id, str)
            or not resource_id
            or not isinstance(filename, str)
            or Path(filename).name != filename
            or not _is_sha256(expected_sha256)
            or resource_id in resources
        ):
            raise QualificationExportError("schema_catalog_resource_invalid")
        schema_bytes = _read_regular(contracts_directory / filename)
        observed_sha256 = sha256_hex(schema_bytes)
        if observed_sha256 != expected_sha256:
            raise QualificationExportError(f"schema_catalog_hash_mismatch:{filename}")
        try:
            document = json.loads(schema_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise QualificationExportError(f"schema_invalid_json:{filename}") from error
        if not isinstance(document, dict) or document.get("$id") != resource_id:
            raise QualificationExportError(f"schema_id_mismatch:{filename}")
        resources[resource_id] = {
            "sha256": observed_sha256,
            "document": document,
        }
    if _CLAIM_SCHEMA_ID not in resources or _EXPORT_SCHEMA_ID not in resources:
        raise QualificationExportError("schema_catalog_required_resource_missing")
    return resources


def _verify_claim_identity(claim: Mapping[str, Any]) -> None:
    binding = claim.get("binding")
    if not isinstance(binding, Mapping):
        raise QualificationExportError("claim_binding_invalid")
    binding_body = {key: value for key, value in binding.items() if key != "binding_id"}
    expected_binding_id = f"bnd-{sha256_hex(canonical_json(binding_body))}"
    if binding.get("binding_id") != expected_binding_id:
        raise QualificationExportError("binding_id_mismatch")
    claim_body = {
        key: value
        for key, value in claim.items()
        if key not in {"claim_id", "generated_at"}
    }
    expected_claim_id = f"claim-{sha256_hex(canonical_json(claim_body))}"
    if claim.get("claim_id") != expected_claim_id:
        raise QualificationExportError("claim_id_mismatch")


def _schema_version(schema: Mapping[str, Any]) -> str:
    try:
        version = schema["properties"]["schema_version"]["const"]
    except (KeyError, TypeError) as error:
        raise QualificationExportError("schema_version_contract_missing") from error
    if not isinstance(version, str) or not version:
        raise QualificationExportError("schema_version_contract_invalid")
    return version


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in _HEX for character in value)
    )


def _is_commit(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) in {40, 64}
        and all(character in _HEX for character in value)
    )


def _require_directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise QualificationExportError(f"{label}_unreadable") from error
    if not stat.S_ISDIR(metadata.st_mode):
        raise QualificationExportError(f"{label}_not_real_directory")


def _read_regular(path: Path) -> bytes:
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise QualificationExportError(
            f"schema_file_open_failed:{path.name}"
        ) from error
    with os.fdopen(descriptor, "rb", closefd=True) as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise QualificationExportError(f"schema_file_not_regular:{path.name}")
        return stream.read()


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        raise QualificationExportError(
            "export_output_directory_fsync_failed"
        ) from error
