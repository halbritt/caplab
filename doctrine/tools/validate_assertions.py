#!/usr/bin/env python3
"""Validate typed assertion artifacts against repository epistemic rules."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path


ASSERTION_TYPES = {
    "observation",
    "inference",
    "recommendation",
    "decision",
    "authorization",
    "execution",
    "verification",
    "acceptance",
}
ARTIFACT_VERSIONS = {
    "assertion-artifact/1",
    "assertion-artifact/2",
    "scenario-result/1",
    "scenario-result/2",
    "decision-receipt/2",
}
REQUIRED_FIELDS = {
    "observation": ("evidence",),
    "inference": ("depends_on", "rivals"),
    "recommendation": ("alternatives", "tradeoffs"),
    "decision": ("depends_on", "owner", "authority"),
    "authorization": ("depends_on", "owner", "authority", "scope"),
    "execution": ("depends_on", "scope"),
    "verification": ("depends_on", "criteria", "evidence"),
    "acceptance": ("depends_on", "owner", "authority"),
}
REQUIRED_PREDECESSORS = {
    "inference": (("observation", "inference"), "observation_or_inference"),
    "recommendation": (("observation", "inference"), "observation_or_inference"),
    "decision": (("recommendation",), "recommendation"),
    "authorization": (("decision",), "decision"),
    "execution": (("authorization",), "authorization"),
    "verification": (("execution",), "execution"),
    "acceptance": (("verification",), "verification"),
}
RECEIPT_STATUS_ASSERTION = {
    "recommended": "recommendation",
    "decided": "decision",
    "authorized": "authorization",
    "executed": "execution",
    "verified": "verification",
    "accepted": "acceptance",
}


def assertion_label(assertion: dict[str, object], index: int) -> object:
    return assertion.get("id", index)


def required_field_errors(assertion: dict[str, object], index: int) -> list[str]:
    assertion_type = assertion.get("type")
    label = assertion_label(assertion, index)
    return [
        f"assertion[{label}]: {assertion_type}_requires_{field}"
        for field in REQUIRED_FIELDS.get(assertion_type, ())
        if not assertion.get(field)
    ]


def predecessor_error(
    assertion: dict[str, object],
    index: int,
    assertions_by_id: dict[str, dict[str, object]],
) -> list[str]:
    assertion_type = assertion.get("type")
    rule = REQUIRED_PREDECESSORS.get(assertion_type)
    if rule is None:
        return []
    required_types, diagnostic_name = rule
    dependencies = [
        assertions_by_id.get(dependency_id)
        for dependency_id in assertion.get("depends_on", [])
    ]
    if any(entry and entry.get("type") in required_types for entry in dependencies):
        return []
    label = assertion_label(assertion, index)
    return [
        f"assertion[{label}]: {assertion_type}_requires_{diagnostic_name}_dependency"
    ]


def assertion_errors(
    assertion: object,
    index: int,
    assertions_by_id: dict[str, dict[str, object]],
) -> list[str]:
    if not isinstance(assertion, dict):
        return [f"assertion[{index}]: assertion_must_be_an_object"]
    label = assertion_label(assertion, index)
    assertion_type = assertion.get("type")
    errors = []
    if not assertion.get("id"):
        errors.append(f"assertion[{label}]: assertion_requires_id")
    if not assertion.get("text"):
        errors.append(f"assertion[{label}]: assertion_requires_text")
    if assertion_type not in ASSERTION_TYPES:
        errors.append(
            f"assertion[{label}]: unsupported_assertion_type: {assertion_type}"
        )
        return errors
    errors.extend(required_field_errors(assertion, index))
    errors.extend(predecessor_error(assertion, index, assertions_by_id))
    return errors


def assertion_index(assertions: list[object]) -> dict[str, dict[str, object]]:
    return {
        assertion["id"]: assertion
        for assertion in assertions
        if isinstance(assertion, dict) and isinstance(assertion.get("id"), str)
    }


def execution_scope_errors(
    assertions: list[object], assertions_by_id: dict[str, dict[str, object]]
) -> list[str]:
    """Require execution scope to be a subset of its direct authorization."""
    errors: list[str] = []
    for assertion in assertions:
        if not isinstance(assertion, dict) or assertion.get("type") != "execution":
            continue
        authorized_scope: set[str] = set()
        for dependency_id in assertion.get("depends_on", []):
            dependency = assertions_by_id.get(dependency_id)
            if dependency and dependency.get("type") == "authorization":
                authorized_scope.update(dependency.get("scope", []))
        for item in assertion.get("scope", []):
            if item not in authorized_scope:
                errors.append(f"execution_scope_exceeds_authorization: {item}")
    return errors


def lineage_errors(assertions_by_id: dict[str, dict[str, object]]) -> list[str]:
    """Reject dependency cycles and require every derived assertion to reach evidence."""
    errors: list[str] = []
    visited: set[str] = set()
    active: list[str] = []

    def visit(assertion_id: str) -> None:
        if assertion_id in active:
            start = active.index(assertion_id)
            cycle = active[start:] + [assertion_id]
            diagnostic = "dependency_cycle: " + " -> ".join(cycle)
            if diagnostic not in errors:
                errors.append(diagnostic)
            return
        if assertion_id in visited:
            return
        active.append(assertion_id)
        assertion = assertions_by_id[assertion_id]
        for dependency_id in assertion.get("depends_on", []):
            if dependency_id in assertions_by_id:
                visit(dependency_id)
        active.pop()
        visited.add(assertion_id)

    for assertion_id in sorted(assertions_by_id):
        visit(assertion_id)

    grounded_cache: dict[str, bool] = {}

    def reaches_observation(assertion_id: str, path: set[str]) -> bool:
        if assertion_id in grounded_cache:
            return grounded_cache[assertion_id]
        if assertion_id in path:
            return False
        assertion = assertions_by_id[assertion_id]
        if assertion.get("type") == "observation":
            grounded_cache[assertion_id] = True
            return True
        next_path = path | {assertion_id}
        grounded = any(
            reaches_observation(dependency_id, next_path)
            for dependency_id in assertion.get("depends_on", [])
            if dependency_id in assertions_by_id
        )
        grounded_cache[assertion_id] = grounded
        return grounded

    for assertion_id, assertion in assertions_by_id.items():
        if assertion.get("type") != "observation" and not reaches_observation(
            assertion_id, set()
        ):
            errors.append(f"assertion[{assertion_id}]: lineage_has_no_observation")
    return errors


def receipt_errors(
    artifact: dict[str, object],
    assertions: list[object],
    evidence_ids: set[str] | None,
) -> list[str]:
    if artifact.get("schema_version") != "decision-receipt/2":
        return []
    errors: list[str] = []
    status = artifact.get("status")
    required_type = RECEIPT_STATUS_ASSERTION.get(status)
    assertion_types = {
        assertion.get("type") for assertion in assertions if isinstance(assertion, dict)
    }
    if required_type and required_type not in assertion_types:
        errors.append(f"receipt_status_requires_{required_type}_assertion")

    boundary = artifact.get("authority_boundary")
    if not isinstance(boundary, dict):
        errors.append("receipt_requires_authority_boundary")
        boundary = {}
    if status in {"decided", "authorized", "executed", "verified", "accepted"}:
        if not boundary.get("owner"):
            errors.append(f"{status}_receipt_requires_owner")
        if not boundary.get("authority_source"):
            errors.append(f"{status}_receipt_requires_authority_source")
    authorized_scope = set(boundary.get("authorized_scope", []))
    if status in {"authorized", "executed", "verified", "accepted"}:
        for item in artifact.get("scope", []):
            if item not in authorized_scope:
                errors.append(f"receipt_scope_exceeds_authority: {item}")
    if status in {"verified", "accepted"} and not artifact.get("verification_criteria"):
        errors.append(f"{status}_receipt_requires_verification_criteria")
    for alternative in artifact.get("alternatives", []):
        if not isinstance(alternative, dict):
            continue
        for evidence_id in alternative.get("evidence", []):
            if evidence_ids is not None and evidence_id not in evidence_ids:
                errors.append(f"unknown_evidence: {evidence_id}")
    return errors


def reference_errors(
    assertions: list[object],
    assertions_by_id: dict[str, dict[str, object]],
    evidence_ids: set[str] | None = None,
) -> list[str]:
    assertion_ids = [
        assertion.get("id")
        for assertion in assertions
        if isinstance(assertion, dict) and isinstance(assertion.get("id"), str)
    ]
    errors = [
        f"duplicate_assertion_id: {assertion_id}"
        for assertion_id, count in collections.Counter(assertion_ids).items()
        if count > 1
    ]
    dependencies = [
        dependency_id
        for assertion in assertions
        if isinstance(assertion, dict)
        for dependency_id in assertion.get("depends_on", [])
    ]
    errors.extend(
        f"unknown_dependency: {dependency_id}"
        for dependency_id in dependencies
        if dependency_id not in assertions_by_id
    )
    if evidence_ids is not None:
        evidence_references = [
            evidence_id
            for assertion in assertions
            if isinstance(assertion, dict)
            for evidence_id in assertion.get("evidence", [])
        ]
        errors.extend(
            f"unknown_evidence: {evidence_id}"
            for evidence_id in evidence_references
            if evidence_id not in evidence_ids
        )
    return errors


def evidence_registry_errors(
    artifact: dict[str, object], external_evidence_ids: set[str] | None
) -> tuple[list[str], set[str] | None]:
    """Validate strict v2 evidence records and return their resolvable IDs."""
    if artifact.get("schema_version") not in {
        "assertion-artifact/2",
        "scenario-result/2",
        "decision-receipt/2",
    }:
        return [], external_evidence_ids
    records = artifact.get("evidence")
    if not isinstance(records, list):
        return ["evidence_must_be_an_array"], set(external_evidence_ids or ())
    errors: list[str] = []
    evidence_ids = set(external_evidence_ids or ())
    record_ids: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"evidence[{index}]: evidence_must_be_an_object")
            continue
        evidence_id = record.get("id")
        if not isinstance(evidence_id, str) or not evidence_id:
            errors.append(f"evidence[{index}]: evidence_requires_id")
            continue
        record_ids.append(evidence_id)
        evidence_ids.add(evidence_id)
        for field in (
            "schema_version",
            "evidence_class",
            "summary",
            "provenance",
        ):
            if not record.get(field):
                errors.append(f"evidence[{evidence_id}]: evidence_requires_{field}")
        if record.get("schema_version") not in {None, "evidence-record/1"}:
            errors.append(f"evidence[{evidence_id}]: unsupported_evidence_version")
        evidence_class = record.get("evidence_class")
        if (
            not isinstance(evidence_class, str)
            or re.fullmatch(r"evidence-[a-z0-9-]+", evidence_class) is None
        ):
            errors.append(f"evidence[{evidence_id}]: invalid_evidence_class")
        if not isinstance(record.get("summary"), str):
            errors.append(f"evidence[{evidence_id}]: evidence_summary_must_be_string")
        provenance = record.get("provenance", [])
        if not isinstance(provenance, list):
            errors.append(
                f"evidence[{evidence_id}]: evidence_requires_provenance_array"
            )
        else:
            for provenance_index, item in enumerate(provenance):
                if not isinstance(item, dict) or not item.get("locator"):
                    errors.append(
                        f"evidence[{evidence_id}].provenance[{provenance_index}]: "
                        "provenance_requires_locator"
                    )
    errors.extend(
        f"duplicate_evidence_id: {evidence_id}"
        for evidence_id, count in collections.Counter(record_ids).items()
        if count > 1
    )
    return errors, evidence_ids


def validate_artifact(
    artifact: object, external_evidence_ids: set[str] | None = None
) -> list[str]:
    if not isinstance(artifact, dict):
        return ["artifact_must_be_an_object"]
    errors = []
    if artifact.get("schema_version") not in ARTIFACT_VERSIONS:
        errors.append("unsupported_schema_version")
    assertions = artifact.get("assertions")
    if not isinstance(assertions, list):
        return errors + ["assertions_must_be_an_array"]
    evidence_errors, evidence_ids = evidence_registry_errors(
        artifact, external_evidence_ids
    )
    errors.extend(evidence_errors)
    assertions_by_id = assertion_index(assertions)
    errors.extend(reference_errors(assertions, assertions_by_id, evidence_ids))
    for index, assertion in enumerate(assertions):
        errors.extend(assertion_errors(assertion, index, assertions_by_id))
    errors.extend(execution_scope_errors(assertions, assertions_by_id))
    if artifact.get("schema_version") in {
        "assertion-artifact/2",
        "scenario-result/2",
        "decision-receipt/2",
    }:
        errors.extend(lineage_errors(assertions_by_id))
    errors.extend(receipt_errors(artifact, assertions, evidence_ids))
    return errors


def read_artifact(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an artifact containing typed assertions."
    )
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()

    try:
        artifact = read_artifact(args.artifact)
    except (OSError, json.JSONDecodeError) as error:
        print(f"unable_to_read_artifact: {error}", file=sys.stderr)
        return 2

    errors = validate_artifact(artifact)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"valid: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
