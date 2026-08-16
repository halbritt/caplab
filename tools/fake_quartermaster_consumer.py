#!/usr/bin/env python3
"""Offline contract consumer for a CAPLAB qualification export.

This deliberately imports no product code.  It models the smallest downstream
boundary: authenticate the public schemas and identities, validate one closed
claim series, and project facts without choosing a current claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import unicodedata
from pathlib import Path
from typing import Any


CATALOG_VERSION = "caplab-qualification-schema-catalog/1"
CLAIM_SCHEMA_ID = "https://caplab.local/contracts/qualification-claim-v1.schema.json"
EXPORT_SCHEMA_ID = "https://caplab.local/contracts/qualification-export-v1.schema.json"
CONTENT_REF_KEYS = {
    "kind",
    "schema",
    "media_type",
    "sha256",
    "byte_count",
    "locator",
    "registration_ref",
    "custody",
}


class ConsumerError(ValueError):
    """The supplied public contract or export failed closed."""


def _deny_network(event: str, _arguments: tuple[Any, ...]) -> None:
    if event.startswith(("socket.", "http.client.", "urllib.")):
        raise RuntimeError("network_disabled")


sys.addaudithook(_deny_network)


def _normalize(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        raise ConsumerError("floating_point_not_identity_safe")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise ConsumerError("normalized_object_key_collision")
            normalized[normalized_key] = _normalize(item)
        return normalized
    raise ConsumerError("unsupported_json_value")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        _normalize(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _object_from_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    normalized_keys: set[str] = set()
    for key, value in pairs:
        normalized_key = unicodedata.normalize("NFC", key)
        if key in result or normalized_key in normalized_keys:
            raise ConsumerError("duplicate_json_key")
        result[key] = value
        normalized_keys.add(normalized_key)
    return result


def _invalid_constant(_value: str) -> None:
    raise ConsumerError("non_finite_json_number")


def _decode(payload: bytes, label: str) -> Any:
    try:
        decoded = json.loads(
            payload,
            object_pairs_hook=_object_from_pairs,
            parse_constant=_invalid_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ConsumerError(f"invalid_json:{label}") from error
    return _normalize(decoded)


def _require_real_directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise ConsumerError(f"unreadable_directory:{label}") from error
    if not stat.S_ISDIR(metadata.st_mode):
        raise ConsumerError(f"not_real_directory:{label}")


def _read_regular(path: Path, label: str) -> bytes:
    _require_real_directory(path.parent, f"{label}_parent")
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ConsumerError(f"unreadable_file:{label}") from error
    with os.fdopen(descriptor, "rb", closefd=True) as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ConsumerError(f"not_regular_file:{label}")
        return stream.read()


class SchemaSet:
    def __init__(self, catalog_path: Path) -> None:
        catalog_payload = _read_regular(catalog_path, "schema_catalog")
        catalog = _decode(catalog_payload, "schema_catalog")
        if (
            not isinstance(catalog, dict)
            or set(catalog) != {"schema_version", "resources"}
            or catalog.get("schema_version") != CATALOG_VERSION
            or not isinstance(catalog.get("resources"), list)
        ):
            raise ConsumerError("schema_catalog_shape_invalid")
        self.by_id: dict[str, dict[str, Any]] = {}
        self.by_path: dict[str, dict[str, Any]] = {}
        self.hashes: dict[str, str] = {}
        for entry in catalog["resources"]:
            self._load_entry(catalog_path.parent, entry)
        if CLAIM_SCHEMA_ID not in self.by_id or EXPORT_SCHEMA_ID not in self.by_id:
            raise ConsumerError("required_schema_missing")

    def _load_entry(self, directory: Path, entry: Any) -> None:
        if not isinstance(entry, dict) or set(entry) != {"id", "path", "sha256"}:
            raise ConsumerError("schema_catalog_entry_invalid")
        resource_id = entry["id"]
        filename = entry["path"]
        digest = entry["sha256"]
        if (
            not isinstance(resource_id, str)
            or not resource_id
            or not isinstance(filename, str)
            or Path(filename).name != filename
            or not _is_hex(digest, 64)
            or resource_id in self.by_id
            or filename in self.by_path
        ):
            raise ConsumerError("schema_catalog_entry_invalid")
        payload = _read_regular(directory / filename, f"schema:{filename}")
        if _sha256(payload) != digest:
            raise ConsumerError(f"schema_hash_mismatch:{filename}")
        document = _decode(payload, f"schema:{filename}")
        if not isinstance(document, dict) or document.get("$id") != resource_id:
            raise ConsumerError(f"schema_id_mismatch:{filename}")
        self.by_id[resource_id] = document
        self.by_path[filename] = document
        self.hashes[resource_id] = digest

    def resolve(
        self,
        reference: str,
        current_document: dict[str, Any],
    ) -> tuple[dict[str, Any] | bool, dict[str, Any]]:
        location, separator, fragment = reference.partition("#")
        if location:
            document = self.by_path.get(location) or self.by_id.get(location)
            if document is None:
                raise ConsumerError(f"unknown_schema_reference:{location}")
        else:
            document = current_document
        target: Any = document
        if separator and fragment:
            if not fragment.startswith("/"):
                raise ConsumerError("unsupported_schema_fragment")
            for raw_part in fragment[1:].split("/"):
                part = raw_part.replace("~1", "/").replace("~0", "~")
                if not isinstance(target, dict) or part not in target:
                    raise ConsumerError("missing_schema_fragment")
                target = target[part]
        if not isinstance(target, (dict, bool)):
            raise ConsumerError("schema_reference_not_schema")
        return target, document


def _is_hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def _same(left: Any, right: Any) -> bool:
    try:
        return _canonical(left) == _canonical(right)
    except (ConsumerError, TypeError, ValueError):
        return False


def _matches(
    instance: Any,
    schema: dict[str, Any] | bool,
    schemas: SchemaSet,
    document: dict[str, Any],
) -> bool:
    try:
        _validate(instance, schema, schemas, document, "candidate")
    except ConsumerError:
        return False
    return True


def _validate(
    instance: Any,
    schema: dict[str, Any] | bool,
    schemas: SchemaSet,
    document: dict[str, Any],
    path: str,
) -> None:
    if schema is False:
        raise ConsumerError(f"schema_false:{path}")
    if schema is True:
        return
    if "$ref" in schema:
        referenced, referenced_document = schemas.resolve(schema["$ref"], document)
        _validate(instance, referenced, schemas, referenced_document, path)
    for subschema in schema.get("allOf", []):
        _validate(instance, subschema, schemas, document, path)
    if "oneOf" in schema:
        matches = sum(
            _matches(instance, subschema, schemas, document)
            for subschema in schema["oneOf"]
        )
        if matches != 1:
            raise ConsumerError(f"one_of_failed:{path}")
    if "not" in schema and _matches(instance, schema["not"], schemas, document):
        raise ConsumerError(f"not_failed:{path}")
    if "if" in schema:
        branch = (
            "then" if _matches(instance, schema["if"], schemas, document) else "else"
        )
        if branch in schema:
            _validate(instance, schema[branch], schemas, document, path)
    if "const" in schema and not _same(instance, schema["const"]):
        raise ConsumerError(f"const_failed:{path}")
    if "enum" in schema and not any(_same(instance, item) for item in schema["enum"]):
        raise ConsumerError(f"enum_failed:{path}")
    expected_type = schema.get("type")
    if expected_type is not None and not _has_type(instance, expected_type):
        raise ConsumerError(f"type_failed:{path}")
    if isinstance(instance, dict):
        required = schema.get("required", [])
        if any(key not in instance for key in required):
            raise ConsumerError(f"required_property_missing:{path}")
        if len(instance) < schema.get("minProperties", 0):
            raise ConsumerError(f"min_properties_failed:{path}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unexpected = set(instance).difference(properties)
            if unexpected:
                raise ConsumerError(f"additional_property:{path}")
        elif isinstance(schema.get("additionalProperties"), dict):
            for key in set(instance).difference(properties):
                _validate(
                    instance[key],
                    schema["additionalProperties"],
                    schemas,
                    document,
                    f"{path}.{key}",
                )
        for key, property_schema in properties.items():
            if key in instance:
                _validate(
                    instance[key],
                    property_schema,
                    schemas,
                    document,
                    f"{path}.{key}",
                )
        if "propertyNames" in schema:
            for key in instance:
                _validate(
                    key,
                    schema["propertyNames"],
                    schemas,
                    document,
                    f"{path}.property-name",
                )
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            raise ConsumerError(f"min_items_failed:{path}")
        if schema.get("uniqueItems"):
            encoded = [_canonical(item) for item in instance]
            if len(set(encoded)) != len(encoded):
                raise ConsumerError(f"unique_items_failed:{path}")
        if "items" in schema:
            for index, item in enumerate(instance):
                _validate(
                    item,
                    schema["items"],
                    schemas,
                    document,
                    f"{path}[{index}]",
                )
        if "contains" in schema:
            match_count = sum(
                _matches(item, schema["contains"], schemas, document)
                for item in instance
            )
            if match_count < schema.get("minContains", 1):
                raise ConsumerError(f"contains_failed:{path}")
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            raise ConsumerError(f"min_length_failed:{path}")
        pattern = schema.get("pattern")
        if pattern is not None and re.search(pattern, instance) is None:
            raise ConsumerError(f"pattern_failed:{path}")
    if (
        isinstance(instance, int)
        and not isinstance(instance, bool)
        and "minimum" in schema
        and instance < schema["minimum"]
    ):
        raise ConsumerError(f"minimum_failed:{path}")


def _has_type(instance: Any, expected: str) -> bool:
    return {
        "null": instance is None,
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "integer": isinstance(instance, int) and not isinstance(instance, bool),
    }.get(expected, False)


def _schema_version(document: dict[str, Any]) -> str:
    try:
        value = document["properties"]["schema_version"]["const"]
    except (KeyError, TypeError) as error:
        raise ConsumerError("schema_version_missing") from error
    if not isinstance(value, str) or not value:
        raise ConsumerError("schema_version_invalid")
    return value


def _verify_content_locators(value: Any) -> None:
    if isinstance(value, dict):
        if set(value) == CONTENT_REF_KEYS:
            digest = value["sha256"]
            expected = f"objects/sha256/{digest[:2]}/{digest}"
            if value["locator"] != expected:
                raise ConsumerError("content_locator_hash_mismatch")
        for child in value.values():
            _verify_content_locators(child)
    elif isinstance(value, list):
        for child in value:
            _verify_content_locators(child)


def _verify_identities_and_graph(export: dict[str, Any]) -> None:
    body = {key: value for key, value in export.items() if key != "export_id"}
    if export["export_id"] != f"export-{_sha256(_canonical(body))}":
        raise ConsumerError("export_id_mismatch")
    claims = export["claims"]
    claim_ids = [claim["claim_id"] for claim in claims]
    if claim_ids != sorted(claim_ids):
        raise ConsumerError("claims_not_sorted")
    if len(set(claim_ids)) != len(claim_ids):
        raise ConsumerError("duplicate_claim_id")
    by_id = {claim["claim_id"]: claim for claim in claims}
    selected_binding = export["selection"]["binding_id"]
    selected_capability = export["selection"]["capability"]
    for claim in claims:
        for prior_id in claim["supersedes"]:
            if prior_id == claim["claim_id"]:
                raise ConsumerError("self_supersession")
            prior = by_id.get(prior_id)
            if prior is None:
                raise ConsumerError("dangling_supersession")
            if prior["binding"]["binding_id"] != claim["binding"][
                "binding_id"
            ] or not _same(prior["capability"], claim["capability"]):
                raise ConsumerError("cross_scope_supersession")
    active: set[str] = set()
    complete: set[str] = set()

    def visit(claim_id: str) -> None:
        if claim_id in complete:
            return
        if claim_id in active:
            raise ConsumerError("supersession_cycle")
        active.add(claim_id)
        for prior_id in by_id[claim_id]["supersedes"]:
            visit(prior_id)
        active.remove(claim_id)
        complete.add(claim_id)

    for claim_id in claim_ids:
        visit(claim_id)
    for claim in claims:
        binding = claim["binding"]
        binding_body = {
            key: value for key, value in binding.items() if key != "binding_id"
        }
        if binding["binding_id"] != f"bnd-{_sha256(_canonical(binding_body))}":
            raise ConsumerError("binding_id_mismatch")
        claim_body = {
            key: value
            for key, value in claim.items()
            if key not in {"claim_id", "generated_at"}
        }
        if claim["claim_id"] != f"claim-{_sha256(_canonical(claim_body))}":
            raise ConsumerError("claim_id_mismatch")
        if binding["binding_id"] != selected_binding:
            raise ConsumerError("claim_binding_selection_mismatch")
        if not _same(claim["capability"], selected_capability):
            raise ConsumerError("claim_capability_selection_mismatch")
    _verify_content_locators(export)


def consume(export_path: Path, catalog_path: Path) -> list[dict[str, Any]]:
    schemas = SchemaSet(catalog_path)
    export_payload = _read_regular(export_path, "export")
    export = _decode(export_payload, "export")
    if not isinstance(export, dict):
        raise ConsumerError("export_not_object")
    if export_payload != _canonical(export) + b"\n":
        raise ConsumerError("export_not_canonical")
    export_schema = schemas.by_id[EXPORT_SCHEMA_ID]
    _validate(export, export_schema, schemas, export_schema, "export")
    expected_schema_refs = {
        "claim": {
            "schema_version": _schema_version(schemas.by_id[CLAIM_SCHEMA_ID]),
            "sha256": schemas.hashes[CLAIM_SCHEMA_ID],
        },
        "export": {
            "schema_version": _schema_version(export_schema),
            "sha256": schemas.hashes[EXPORT_SCHEMA_ID],
        },
    }
    if not _same(export["schemas"], expected_schema_refs):
        raise ConsumerError("export_schema_reference_mismatch")
    _verify_identities_and_graph(export)
    return [
        {
            "claim_id": claim["claim_id"],
            "binding_id": claim["binding"]["binding_id"],
            "capability": claim["capability"],
            "status": claim["qualification"]["status"],
            "supersedes": claim["supersedes"],
            "evidence": claim["evidence"],
        }
        for claim in export["claims"]
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    return parser


def main(arguments: list[str] | None = None) -> int:
    options = _parser().parse_args(arguments)
    try:
        projection = consume(options.export, options.catalog)
    except ConsumerError as error:
        sys.stderr.buffer.write(_canonical({"error": str(error)}) + b"\n")
        return 3
    sys.stdout.buffer.write(_canonical(projection) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
