"""Catalog discovery: a proposal document, never preparation or adoption."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from caplab.catalog.projection import NATIVE_FIELDS, CatalogSelectionError, Projection
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.subject_identity import CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256

SCHEMA = "caplab-catalog-discovery/1"


def load_native_policy(path: Path) -> dict[str, Any]:
    """Read a policy file that must be the digest-pinned native-agent-systems contract."""

    try:
        policy = json.loads(Path(path).read_bytes())
        digest = sha256_hex(canonical_json(policy))
    except (OSError, ValueError) as error:
        raise CatalogSelectionError("catalog_native_policy_unreadable") from error
    if digest != CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256:
        raise CatalogSelectionError("catalog_native_policy_digest_mismatch")
    return policy


def admitted(tuple_: Mapping[str, Any], policy: Mapping[str, Any]) -> bool:
    """True when the closed policy already lists this exact native tuple."""

    systems = policy.get("systems")
    return isinstance(systems, Mapping) and any(
        isinstance(system, Mapping) and all(system.get(f) == tuple_[f] for f in NATIVE_FIELDS)
        for system in systems.values()
    )


def discover(
    projection: Projection,
    *,
    policy: Mapping[str, Any] | None = None,
    sweep_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe what the catalog offers this consumer, with explicit evidence limits."""

    document = projection.document
    native = projection.part("native_agent_systems")["content"]
    excluded = {e.get("key"): e.get("reason") for e in native["excluded"] if isinstance(e, dict)}
    entries = []
    for entry in document["entries"]:
        tuple_ = native["systems"].get(entry["key"])
        if tuple_ is None:
            status, reason = "not_native_eligible", excluded.get(entry["key"], "no_native_tuple")
        elif policy is None:
            status, reason = "policy_not_supplied", None
        elif admitted(tuple_, policy):
            status, reason = "admitted", None
        else:
            status, reason = "not_admitted", "closed_native_policy_lists_no_such_tuple"
        entries.append(
            {
                # A Striatum declaration ID for the advisory lane, never a public bnd- identity.
                "declaration_id": entry["key"],
                **{
                    field: entry.get(field)
                    for field in ("origin", "route_id", "account_id", "effort", "profile_id",
                                  "family", "billing", "model", "model_source", "enabled")
                },
                "native": {"status": status, "reason": reason, "tuple": tuple_},
            }
        )
    population = {
        field: list(projection.part("sweep_population")["content"][field])
        for field in ("supervised_only_runtimes", "afk_eligible_runtimes")
    }
    warnings = list(document.get("warnings") or [])
    if sweep_config is not None:
        try:
            current = set(sweep_config["population"]["supervised_only_runtimes"])
        except (KeyError, TypeError) as error:
            raise CatalogSelectionError("catalog_sweep_config_invalid") from error
        dropped = sorted(current - set(population["supervised_only_runtimes"]))
        if dropped:
            warnings.append(
                {
                    "code": "population_would_drop_supervised_runtime",
                    "detail": "supervised-only in the sweep config but not in this population: "
                    + ", ".join(dropped),
                }
            )
    return {
        "schema_version": SCHEMA,
        "status": "proposal",
        "authority": {"preparation": False, "adoption": False, "qualification": False,
                      "execution": False},
        "catalog": {
            "release_id": document["release_id"],
            "projection_id": document["projection_id"],
            "overlay_sha256": document["overlay_sha256"],
            "host": document["host"],
            "release_file_sha256": sha256_hex(projection.release_bytes),
            "overlay_file_sha256": sha256_hex(projection.overlay_bytes),
            "projection_output_sha256": sha256_hex(projection.output_bytes),
            "quartermaster_argv": list(projection.command),
        },
        "native_policy": None if policy is None else {
            "sha256": CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256},
        "entries": entries,
        "rejected": list(document.get("rejected") or []),
        "warnings": warnings,
        # Restated for review only; the advisory sweep configuration is never modified here.
        "population": {**population, "applied": False},
        "sweep_challengers": list(projection.part("sweep_challengers")["content"].get("challengers") or []),
    }
