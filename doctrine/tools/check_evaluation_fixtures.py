#!/usr/bin/env python3
"""Validate Books-owned hermetic evaluation replay fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterator

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = ROOT / "doctrine/evaluations/replay-fixtures"
FIXTURE_SCHEMA = ROOT / "doctrine/evaluations/replay-fixture.schema.json"
MANIFEST_SCHEMA = ROOT / "doctrine/evaluations/replay-manifest.schema.json"
MUTABLE_REFERENCES = {"*", "head", "latest", "main", "master", "tip", "trunk"}
MUTABLE_REFERENCE_SUFFIX = re.compile(
    r"[:/@](?:head|latest|main|master|tip|trunk)$", re.IGNORECASE
)
EXTERNAL_LOCATOR = re.compile(r"[a-z][a-z0-9+.-]*://", re.IGNORECASE)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s\"'])(?:/home/|/tmp/|/var/|/etc/|/opt/|/srv/|~/)")
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?:^|[\s\"'])[a-z]:\\", re.IGNORECASE)
SECRET_KEYS = {"api_key", "authorization", "password", "secret", "token"}
EXTERNAL_FIELDS = {
    "base_url",
    "dependencies",
    "dependency",
    "endpoint",
    "host",
    "image",
    "ref",
    "repository",
    "revision",
    "uri",
    "url",
}
SYNTHETIC_MODEL = re.compile(r"^synthetic-[a-z0-9-]+-v[0-9]+$")


class FixtureError(ValueError):
    pass


def _read_object(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise FixtureError(f"not_a_json_object:{path}")
    return document


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _walk(value: Any, location: str = "$") -> Iterator[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            yield child_location, key, child
            yield from _walk(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_location = f"{location}[{index}]"
            yield from _walk(child, child_location)


def validate_fixture_document(document: dict[str, Any]) -> None:
    schema = _read_object(FIXTURE_SCHEMA)
    jsonschema.Draft202012Validator(schema).validate(document)
    for location, key, value in _walk(document):
        normalized_key = key.lower()
        if normalized_key in EXTERNAL_FIELDS:
            raise FixtureError(f"external_field:{location}")
        if normalized_key in SECRET_KEYS:
            raise FixtureError(f"credential_field:{location}")
        if not isinstance(value, str):
            continue
        normalized_value = value.strip().lower()
        if (
            EXTERNAL_LOCATOR.search(value)
            or ABSOLUTE_PATH.search(value)
            or WINDOWS_ABSOLUTE_PATH.search(value)
        ):
            raise FixtureError(f"external_locator:{location}")
        if "${" in value or "$home" in normalized_value:
            raise FixtureError(f"environment_dependency:{location}")
        if (
            (
                normalized_key in {"model", "version"}
                and normalized_value in MUTABLE_REFERENCES
            )
            or MUTABLE_REFERENCE_SUFFIX.search(normalized_value)
        ):
            raise FixtureError(f"mutable_reference:{location}")
    request_model = document["request"].get("model")
    response_model = document["response"].get("model")
    if not isinstance(request_model, str) or not SYNTHETIC_MODEL.fullmatch(
        request_model
    ):
        raise FixtureError("external_model:$.request.model")
    if response_model != request_model:
        raise FixtureError("response_model_mismatch")
    for field in ("request", "response"):
        expected = document[f"{field}_sha256"]
        actual = _canonical_sha256(document[field])
        if actual != expected:
            raise FixtureError(
                f"{field}_sha256_mismatch:expected={expected}:actual={actual}"
            )


def load_catalog(root: Path = DEFAULT_ROOT) -> dict[str, dict[str, Any]]:
    if root.is_symlink():
        raise FixtureError(f"fixture_root_is_symlink:{root}")
    root = root.resolve()
    if not root.is_dir():
        raise FixtureError(f"fixture_root_missing:{root}")
    entries = list(root.iterdir())
    symlinks = sorted(path.name for path in entries if path.is_symlink())
    if symlinks:
        raise FixtureError(f"fixture_is_symlink:{symlinks}")
    non_files = sorted(path.name for path in entries if not path.is_file())
    if non_files:
        raise FixtureError(f"fixture_inventory_mismatch:non_files={non_files}")
    manifest_path = root / "manifest.json"
    manifest = _read_object(manifest_path)
    jsonschema.Draft202012Validator(_read_object(MANIFEST_SCHEMA)).validate(manifest)
    discovered = {path.name for path in entries if path != manifest_path}
    declared = {entry["path"] for entry in manifest["fixtures"]}
    if discovered != declared:
        raise FixtureError(
            f"fixture_inventory_mismatch:declared={sorted(declared)}:"
            f"discovered={sorted(discovered)}"
        )
    catalog: dict[str, dict[str, Any]] = {}
    for entry in manifest["fixtures"]:
        path = root / entry["path"]
        if path.is_symlink():
            raise FixtureError(f"fixture_is_symlink:{entry['path']}")
        if _sha256_file(path) != entry["sha256"]:
            raise FixtureError(f"fixture_file_sha256_mismatch:{entry['path']}")
        document = _read_object(path)
        validate_fixture_document(document)
        if document["id"] != entry["id"]:
            raise FixtureError(f"fixture_id_mismatch:{entry['path']}")
        if document["id"] in catalog:
            raise FixtureError(f"duplicate_fixture_id:{document['id']}")
        catalog[document["id"]] = document
    return catalog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.root)
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError, FixtureError) as exc:
        print(f"evaluation fixture hygiene error: {exc}", file=sys.stderr)
        return 1
    print(f"evaluation fixture hygiene passed: {len(catalog)} fixture(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
