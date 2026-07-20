"""Content-addressed synthetic evaluation replay."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from caplab.runtime.canonical import canonical_json, sha256_hex


MANIFEST_SCHEMA = "caplab-evaluation-replay-manifest/1"
FIXTURE_SCHEMA = "caplab-evaluation-replay-fixture/1"
MANIFEST_KEYS = frozenset({"schema_version", "fixtures"})
ENTRY_KEYS = frozenset({"id", "path", "sha256"})
FIXTURE_KEYS = frozenset(
    {
        "schema_version",
        "id",
        "mode",
        "provenance",
        "request",
        "request_sha256",
        "response",
        "response_sha256",
    }
)
REQUEST_KEYS = frozenset({"model", "messages", "max_tokens"})
RESPONSE_KEYS = frozenset({"model", "status", "output", "error"})
PROVENANCE_KEYS = frozenset({"kind", "captured_from_live"})
EXTERNAL_FIELDS = frozenset(
    {
        "base_url",
        "dependency",
        "dependencies",
        "endpoint",
        "host",
        "image",
        "ref",
        "repository",
        "revision",
        "uri",
        "url",
    }
)
SECRET_FIELDS = frozenset({"api_key", "authorization", "password", "secret", "token"})
HOST_PATH = re.compile(
    r"(?:^|[\s\"'])(?:/(?:home|tmp|var|etc|opt|srv)/|~/|[a-z]:\\)",
    re.IGNORECASE,
)
MUTABLE_REFERENCE = re.compile(
    r"(?:^|[:/@-])(?:head|latest|main|master)$",
    re.IGNORECASE,
)
EXTERNAL_LOCATOR = re.compile(r"(?:https?|ssh|git|s3)://", re.IGNORECASE)
SYNTHETIC_MODEL = re.compile(r"^synthetic-[a-z0-9-]+-v[1-9][0-9]*$")
SAFE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class EvaluationContractError(ValueError):
    """A replay input cannot cross the CAPLAB evaluation boundary."""


@dataclass(frozen=True, slots=True)
class EvaluationReplay:
    fixture_id: str
    fixture_sha256: str
    request_sha256: str
    response_sha256: str
    mode: str
    outcome_class: str
    score_eligible: bool
    may_supply_model_evidence: bool
    output: Mapping[str, Any]


def _read_object(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise EvaluationContractError(f"document_is_symlink:{path.name}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise EvaluationContractError(f"missing_document:{path.name}") from error
    except UnicodeDecodeError as error:
        raise EvaluationContractError(f"invalid_encoding:{path.name}") from error
    except json.JSONDecodeError as error:
        raise EvaluationContractError(f"invalid_json:{path.name}") from error
    except OSError as error:
        raise EvaluationContractError(f"unreadable_document:{path.name}") from error
    if not isinstance(document, dict):
        raise EvaluationContractError(f"document_is_not_object:{path.name}")
    return document


def _walk(value: Any, location: str = "$") -> Iterator[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            yield child_location, key, child
            yield from _walk(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{location}[{index}]")


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    return value


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: frozenset[str],
    location: str,
) -> None:
    if set(value) != expected:
        raise EvaluationContractError(
            f"invalid_shape:{location}:"
            f"missing={sorted(expected - set(value))}:"
            f"extra={sorted(set(value) - expected)}"
        )


def _validate_manifest(manifest: Mapping[str, Any]) -> list[dict[str, str]]:
    _require_exact_keys(manifest, MANIFEST_KEYS, "manifest")
    if manifest["schema_version"] != MANIFEST_SCHEMA:
        raise EvaluationContractError(
            f"unsupported_manifest_schema:{manifest['schema_version']}"
        )
    fixtures = manifest["fixtures"]
    if not isinstance(fixtures, list) or not fixtures:
        raise EvaluationContractError("invalid_manifest_fixtures")
    entries: list[dict[str, str]] = []
    for index, item in enumerate(fixtures):
        if not isinstance(item, dict):
            raise EvaluationContractError(f"invalid_manifest_entry:{index}")
        _require_exact_keys(item, ENTRY_KEYS, f"manifest.fixtures[{index}]")
        fixture_id, path, digest = item["id"], item["path"], item["sha256"]
        if not isinstance(fixture_id, str) or not SAFE_ID.fullmatch(fixture_id):
            raise EvaluationContractError(f"unsafe_fixture_id:{fixture_id}")
        if not isinstance(path, str) or path != f"{fixture_id}.json":
            raise EvaluationContractError(f"unsafe_fixture_path:{path}")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise EvaluationContractError(f"invalid_fixture_sha256:{fixture_id}")
        entries.append(item)
    if len({entry["id"] for entry in entries}) != len(entries):
        raise EvaluationContractError("duplicate_fixture_id")
    if len({entry["path"] for entry in entries}) != len(entries):
        raise EvaluationContractError("duplicate_fixture_path")
    return entries


def _select_entry(
    fixture_root: Path,
    entries: list[dict[str, str]],
    fixture_id: str,
) -> dict[str, str]:
    declared_paths = {entry["path"] for entry in entries}
    discovered_paths = {
        path.name for path in fixture_root.iterdir() if path.name != "manifest.json"
    }
    if discovered_paths != declared_paths:
        raise EvaluationContractError(
            "fixture_inventory_mismatch:"
            f"declared={sorted(declared_paths)}:discovered={sorted(discovered_paths)}"
        )
    entry = next((item for item in entries if item["id"] == fixture_id), None)
    if entry is None:
        raise EvaluationContractError(f"unknown_fixture:{fixture_id}")
    return entry


def _validate_messages(messages: Any, fixture_id: str) -> None:
    if not isinstance(messages, list) or not messages:
        raise EvaluationContractError(f"invalid_messages:{fixture_id}")
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise EvaluationContractError(f"invalid_message:{fixture_id}:{index}")
        _require_exact_keys(message, frozenset({"role", "content"}), f"message[{index}]")
        if message["role"] not in {"system", "user", "assistant"}:
            raise EvaluationContractError(f"invalid_message_role:{fixture_id}:{index}")
        if not isinstance(message["content"], str) or not message["content"]:
            raise EvaluationContractError(f"invalid_message_content:{fixture_id}:{index}")


def _validate_fixture(fixture: Mapping[str, Any], fixture_id: str) -> None:
    _require_exact_keys(fixture, FIXTURE_KEYS, "fixture")
    if fixture["schema_version"] != FIXTURE_SCHEMA:
        raise EvaluationContractError(
            f"unsupported_fixture_schema:{fixture['schema_version']}"
        )
    if fixture["id"] != fixture_id:
        raise EvaluationContractError(f"fixture_id_mismatch:{fixture_id}")
    if fixture["mode"] != "replay":
        raise EvaluationContractError(f"unsupported_fixture_mode:{fixture['mode']}")
    provenance = fixture["provenance"]
    if not isinstance(provenance, dict):
        raise EvaluationContractError(f"invalid_provenance:{fixture_id}")
    _require_exact_keys(provenance, PROVENANCE_KEYS, "fixture.provenance")
    if provenance != {"kind": "synthetic", "captured_from_live": False}:
        raise EvaluationContractError(f"fixture_is_not_fresh_synthetic:{fixture_id}")
    request, response = fixture["request"], fixture["response"]
    if not isinstance(request, dict) or not isinstance(response, dict):
        raise EvaluationContractError(f"invalid_request_or_response:{fixture_id}")
    _require_exact_keys(request, REQUEST_KEYS, "fixture.request")
    _require_exact_keys(response, RESPONSE_KEYS, "fixture.response")
    _validate_messages(request["messages"], fixture_id)
    if not isinstance(request["max_tokens"], int) or request["max_tokens"] <= 0:
        raise EvaluationContractError(f"invalid_max_tokens:{fixture_id}")
    for name in ("request_sha256", "response_sha256"):
        if not isinstance(fixture[name], str) or not SHA256.fullmatch(fixture[name]):
            raise EvaluationContractError(f"invalid_{name}:{fixture_id}")


def _validate_hygiene(fixture: Mapping[str, Any]) -> None:
    for location, key, value in _walk(fixture):
        if key.lower() in EXTERNAL_FIELDS:
            raise EvaluationContractError(f"external_field:{location}")
        if key.lower() in SECRET_FIELDS:
            raise EvaluationContractError(f"credential_field:{location}")
        if isinstance(value, str) and HOST_PATH.search(value):
            raise EvaluationContractError(f"host_path:{location}")
        if (
            key.lower() == "model"
            and isinstance(value, str)
            and MUTABLE_REFERENCE.search(value)
        ):
            raise EvaluationContractError(f"mutable_reference:{location}")
        if isinstance(value, str) and EXTERNAL_LOCATOR.search(value):
            raise EvaluationContractError(f"external_locator:{location}")


def _validate_identities(fixture: Mapping[str, Any], fixture_id: str) -> None:
    try:
        request_identity = sha256_hex(canonical_json(fixture["request"]))
        response_identity = sha256_hex(canonical_json(fixture["response"]))
    except ValueError as error:
        raise EvaluationContractError(f"noncanonical_fixture:{fixture_id}") from error
    if request_identity != fixture["request_sha256"]:
        raise EvaluationContractError(f"request_identity_mismatch:{fixture_id}")
    if response_identity != fixture["response_sha256"]:
        raise EvaluationContractError(f"response_identity_mismatch:{fixture_id}")
    request_model = fixture["request"]["model"]
    response_model = fixture["response"]["model"]
    if request_model != response_model:
        raise EvaluationContractError(f"response_model_mismatch:{fixture_id}")
    if not isinstance(request_model, str) or not SYNTHETIC_MODEL.fullmatch(request_model):
        raise EvaluationContractError(f"non_synthetic_model:{request_model}")


def _classify_response(
    response: Mapping[str, Any],
) -> tuple[str, bool, bool, Mapping[str, Any]]:
    status = response.get("status")
    output = response.get("output")
    error = response.get("error")
    if status == "completed" and isinstance(output, dict) and error is None:
        return "model-outcome", True, True, output
    if status in {"invalid-output", "refused"} and output is None and error is None:
        return "model-failure", True, False, {}
    if status == "not-run" and output is None and error is None:
        return "not-evaluated", False, False, {}
    return "infrastructure-failure", False, False, {}


def replay_synthetic_fixture(
    fixture_root: Path,
    fixture_id: str,
    *,
    execution_mode: str,
) -> EvaluationReplay:
    """Replay one manifested synthetic response without making a model call."""

    if execution_mode not in {"live", "replay"}:
        raise EvaluationContractError(f"unknown_execution_mode:{execution_mode}")
    if fixture_root.is_symlink():
        raise EvaluationContractError(f"fixture_root_is_symlink:{fixture_root}")
    if not fixture_root.is_dir():
        raise EvaluationContractError(f"fixture_root_is_not_directory:{fixture_root}")
    manifest = _read_object(fixture_root / "manifest.json")
    entry = _select_entry(fixture_root, _validate_manifest(manifest), fixture_id)
    fixture_path = fixture_root / entry["path"]
    if fixture_path.is_symlink():
        raise EvaluationContractError(f"fixture_is_symlink:{fixture_path.name}")
    try:
        fixture_bytes = fixture_path.read_bytes()
    except OSError as error:
        raise EvaluationContractError(f"unreadable_fixture:{fixture_id}") from error
    if sha256_hex(fixture_bytes) != entry["sha256"]:
        raise EvaluationContractError(f"fixture_identity_mismatch:{fixture_id}")
    try:
        fixture = json.loads(fixture_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvaluationContractError(f"invalid_json:{fixture_path.name}") from error
    if not isinstance(fixture, dict):
        raise EvaluationContractError(f"fixture_is_not_object:{fixture_id}")
    _validate_hygiene(fixture)
    _validate_fixture(fixture, fixture_id)
    if fixture["mode"] != execution_mode:
        raise EvaluationContractError(
            f"mode_mismatch:expected={execution_mode}:fixture={fixture['mode']}"
        )
    _validate_identities(fixture, fixture_id)
    outcome, eligible, evidence, output = _classify_response(fixture["response"])
    return EvaluationReplay(
        fixture_id=fixture_id,
        fixture_sha256=sha256_hex(fixture_bytes),
        request_sha256=fixture["request_sha256"],
        response_sha256=fixture["response_sha256"],
        mode=execution_mode,
        outcome_class=outcome,
        score_eligible=eligible,
        may_supply_model_evidence=evidence,
        output=_freeze(output),
    )
