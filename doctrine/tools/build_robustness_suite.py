#!/usr/bin/env python3
"""Strict, offline loading for Doctrine Robustness Laboratory contracts."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from urllib.parse import urldefrag, urljoin

from jsonschema import Draft202012Validator, FormatChecker, RefResolver


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = ROOT / "doctrine" / "evaluations" / "robustness"
SCHEMA_PATHS = {
    "operator": SCHEMA_ROOT / "operator.schema.json",
    "case": SCHEMA_ROOT / "case.schema.json",
    "result": SCHEMA_ROOT / "result.schema.json",
    "human-adjudication": SCHEMA_ROOT / "human-adjudication.schema.json",
}


class ContractError(ValueError):
    """A stable laboratory contract failure."""


def _read_object(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"artifact_read_error: {path}: {error}") from error
    if not isinstance(value, dict):
        raise ContractError(f"artifact_not_object: {path}")
    return value


def _references(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                yield child
            else:
                yield from _references(child)
    elif isinstance(value, list):
        for child in value:
            yield from _references(child)


def validate_schema_registry() -> None:
    """Validate every P1 schema and prove all non-fragment refs are local."""
    schemas = [_read_object(path) for path in SCHEMA_PATHS.values()]
    runtime_paths = sorted((ROOT / "doctrine" / "runtime").glob("*.schema.json"))
    schemas.extend(_read_object(path) for path in runtime_paths)
    known_ids = {schema.get("$id") for schema in schemas}
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str):
            raise ContractError("schema_registry_error: missing $id")
        for reference in _references(schema):
            resolved, _ = urldefrag(urljoin(schema_id, reference))
            if resolved and resolved not in known_ids:
                raise ContractError(f"schema_registry_error: unresolved_ref: {resolved}")


def _offline_resolver(schema: dict[str, object]) -> RefResolver:
    paths = list(SCHEMA_PATHS.values())
    paths.extend(sorted((ROOT / "doctrine" / "runtime").glob("*.schema.json")))
    schemas = [_read_object(path) for path in paths]
    store = {item["$id"]: item for item in schemas if isinstance(item.get("$id"), str)}
    return RefResolver.from_schema(schema, store=store)


def load_artifact(kind: str, path: Path) -> dict[str, object]:
    """Load one supported artifact without network or implicit coercion."""
    schema_path = SCHEMA_PATHS.get(kind)
    if schema_path is None:
        raise ContractError(f"unsupported_artifact_kind: {kind}")
    schema = _read_object(schema_path)
    Draft202012Validator.check_schema(schema)
    artifact = _read_object(path)
    validate_artifact(kind, artifact)
    return artifact


def validate_artifact(kind: str, artifact: dict[str, object]) -> None:
    """Validate an already parsed artifact through the same offline registry."""
    schema_path = SCHEMA_PATHS.get(kind)
    if schema_path is None:
        raise ContractError(f"unsupported_artifact_kind: {kind}")
    schema = _read_object(schema_path)
    errors = sorted(
        Draft202012Validator(
            schema,
            resolver=_offline_resolver(schema),
            format_checker=FormatChecker(),
        ).iter_errors(artifact),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        error = errors[0]
        location = "/" + "/".join(str(part) for part in error.absolute_path)
        raise ContractError(f"schema_validation_error: {kind}:{location}: {error.message}")


def load_case(
    path: Path, *, root: Path, operator_paths: list[Path]
) -> dict[str, object]:
    """Resolve a case against an explicit operator registry and local seed root."""
    case = load_artifact("case", path)
    operators = [load_artifact("operator", item) for item in operator_paths]
    reference = case["operator"]
    assert isinstance(reference, dict)
    identity = (reference["id"], reference["version"])
    if not any((item["id"], item["version"]) == identity for item in operators):
        raise ContractError(f"unresolved_operator: {identity[0]}/{identity[1]}")

    clean_seed = case["clean_seed"]
    assert isinstance(clean_seed, dict)
    locator = clean_seed["locator"]
    assert isinstance(locator, str)
    root = root.resolve()
    seed_path = (root / locator).resolve()
    if root not in seed_path.parents and seed_path != root:
        raise ContractError(f"seed_outside_root: {locator}")
    try:
        digest = hashlib.sha256(seed_path.read_bytes()).hexdigest()
    except OSError as error:
        raise ContractError(f"seed_read_error: {locator}: {error}") from error
    if digest != clean_seed["target_hash"]:
        raise ContractError(f"stale_seed: {locator}")
    return case


def load_result(
    path: Path, *, case_paths: list[Path], operator_paths: list[Path]
) -> dict[str, object]:
    """Resolve a result against explicit case and operator registries."""
    result = load_artifact("result", path)
    cases = [load_artifact("case", item) for item in case_paths]
    if not any(item["id"] == result["case_id"] for item in cases):
        raise ContractError(f"unresolved_case: {result['case_id']}")
    operators = [load_artifact("operator", item) for item in operator_paths]
    identity = (result["operator_id"], result["operator_version"])
    if not any((item["id"], item["version"]) == identity for item in operators):
        raise ContractError(f"unresolved_operator: {identity[0]}/{identity[1]}")
    return result
