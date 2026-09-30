"""Check a catalog entry against a complete prospective Revbench spec, then retain it.

A catalog route never becomes a Binding here. The spec already carries the complete
``caplab-binding/1`` and its native command artifacts; this module only verifies that
they describe the tuple, profile home and policy the catalog entry claims, and keeps the
exact catalog bytes next to the manifest through the ledger's registration mechanism.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from caplab.catalog.discovery import admitted
from caplab.catalog.projection import CatalogSelectionError, Projection
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.subject_identity import _unwrap_env

SCHEMA = "caplab-catalog-selection/1"
HOME_VARIABLES = ("CODEX_HOME", "CLAUDE_CONFIG_DIR", "HOME")


@dataclass(frozen=True)
class Selection:
    projection: Projection
    entry: dict[str, Any]
    native: dict[str, Any]
    route: dict[str, Any]
    profile: dict[str, Any]


def select_entry(projection: Projection, key: str) -> Selection:
    entry = next((e for e in projection.document["entries"] if e["key"] == key), None)
    if entry is None:
        raise CatalogSelectionError("catalog_entry_unknown")
    native = projection.part("native_agent_systems")["content"]["systems"].get(key)
    if native is None:
        raise CatalogSelectionError("catalog_entry_not_native_eligible")
    catalog = projection.release["catalog"]
    route = next((r for r in catalog["routes"] if r.get("id") == entry["route_id"]), None)
    profile = next((p for p in catalog["profiles"] if p.get("id") == entry["profile_id"]), None)
    if route is None or profile is None:
        raise CatalogSelectionError("catalog_projection_invalid")
    return Selection(projection, entry, native, route, profile)


def _document(registrar: Any, ref: Mapping[str, Any]) -> Any:
    return json.loads(registrar.resolve(ref))


def validate_against_spec(
    selection: Selection, spec: Mapping[str, Any], registrar: Any
) -> dict[str, Any]:
    """Raise a stable code unless the spec's native artifacts match the catalog entry.

    Call after ``prepare`` has validated the spec: only read-only ledger resolution
    happens here, so every refusal precedes any ledger or custody mutation.
    """

    tuple_, binding = selection.native, spec["binding"]
    if binding["model"]["model_id"] != tuple_["model_id"]:
        raise CatalogSelectionError("catalog_model_mismatch")
    if binding["harness"]["harness_id"] != tuple_["native_harness_id"]:
        raise CatalogSelectionError("catalog_harness_mismatch")
    if binding["reasoning_effort"] != tuple_["effort"]:
        raise CatalogSelectionError("catalog_effort_mismatch")
    policy = _document(registrar, spec["native_system_contract_ref"])
    if not admitted(tuple_, policy):
        raise CatalogSelectionError("catalog_native_tuple_not_admitted")
    assignments, command = _unwrap_env(_document(registrar, binding["harness"]["command_ref"])["argv"])
    tokens = tuple_["required_command_tokens"]
    if command[:1] != [tuple_["executable"]] or command[1 : 1 + len(tokens)] != tokens:
        raise CatalogSelectionError("catalog_command_mismatch")
    probe = _document(registrar, binding["harness"]["version_probe_ref"])
    _, version = _unwrap_env(_document(registrar, probe["command_ref"])["argv"])
    if version != tuple_["version_command"]:
        raise CatalogSelectionError("catalog_version_command_mismatch")
    homes = [a.split("=", 1)[1] for a in assignments if a.split("=", 1)[0] in HOME_VARIABLES]
    expected = selection.profile["config_home"]
    if homes != ([] if expected is None else [expected]):
        raise CatalogSelectionError("catalog_profile_home_mismatch")
    return {
        "binding_id": binding["binding_id"],
        "model_id": binding["model"]["model_id"],
        "harness_id": binding["harness"]["harness_id"],
        "effort": binding["reasoning_effort"],
        "profile_config_home": expected,
        "native_system_contract_sha256": sha256_hex(canonical_json(policy)),
    }


def retain_selection(
    selection: Selection,
    validated: Mapping[str, Any],
    manifest: Mapping[str, Any],
    registrar: Any,
) -> dict[str, Any]:
    """Register the exact catalog bytes and a receipt naming them; returns the receipt ref."""

    projection = selection.projection
    sources = {}
    for name, schema, payload in (
        ("catalog-release", "quartermaster-catalog-release/1", projection.release_bytes),
        ("catalog-overlay", "quartermaster-consumer-overlay/1", projection.overlay_bytes),
        ("catalog-projection", "quartermaster-consumer-projection/1", projection.output_bytes),
    ):
        sources[name.removeprefix("catalog-") + "_ref"] = registrar.register_bytes(
            payload,
            kind=name,
            schema=schema,
            media_type="application/octet-stream",
            registration_id=f"{name}-{sha256_hex(payload)}",
        )
    document = projection.document
    receipt = {
        "schema_version": SCHEMA,
        "status": "validated-against-prepared-spec",
        "projection": {field: document[field] for field in
                       ("document", "projection_id", "release_id", "overlay_sha256", "host", "consumer")},
        "quartermaster_argv": list(projection.command),
        "sources": sources,
        "entry": {
            "declaration_id": selection.entry["key"],
            **{f: selection.entry.get(f) for f in ("origin", "route_id", "account_id", "effort",
                                                   "profile_id", "family", "billing", "model",
                                                   "model_source", "enabled")},
        },
        "native_tuple": dict(selection.native),
        # The catalog's route is configured intent. Nothing here observed a provider route.
        "configured_route": {"resolution": "configured-route", "observed_at": None},
        "validated": dict(validated),
        "manifest": {"experiment_id": manifest["experiment_id"]},
        "disclosures": {
            "binding_constructed_from_catalog": False,
            "account_identity_is_in_binding": False,
            "execution_authorized": False,
            "qualification_or_adoption": False,
        },
    }
    return registrar.register_document(
        receipt,
        kind="catalog-selection",
        schema=SCHEMA,
        registration_id=f"catalog-selection-{sha256_hex(canonical_json(receipt))}",
    )
