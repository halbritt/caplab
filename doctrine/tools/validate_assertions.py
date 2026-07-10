#!/usr/bin/env python3
"""Validate typed assertion artifacts against repository epistemic rules."""

from __future__ import annotations

import argparse
import collections
import json
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
ARTIFACT_VERSIONS = {"assertion-artifact/1", "scenario-result/1"}
REQUIRED_FIELDS = {
    "observation": ("evidence",),
    "inference": ("depends_on", "rivals"),
    "recommendation": ("alternatives", "tradeoffs"),
    "decision": ("depends_on", "owner", "authority"),
    "authorization": ("depends_on", "owner", "authority", "scope"),
    "execution": ("depends_on",),
    "verification": ("depends_on", "criteria", "evidence"),
    "acceptance": ("depends_on", "owner", "authority"),
}
REQUIRED_PREDECESSORS = {
    "execution": "authorization",
    "verification": "execution",
    "acceptance": "verification",
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
    required_type = REQUIRED_PREDECESSORS.get(assertion_type)
    if required_type is None:
        return []
    dependencies = [
        assertions_by_id.get(dependency_id)
        for dependency_id in assertion.get("depends_on", [])
    ]
    if any(entry and entry.get("type") == required_type for entry in dependencies):
        return []
    label = assertion_label(assertion, index)
    return [f"assertion[{label}]: {assertion_type}_requires_{required_type}_dependency"]


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


def reference_errors(
    assertions: list[object], assertions_by_id: dict[str, dict[str, object]]
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
    return errors


def validate_artifact(artifact: object) -> list[str]:
    if not isinstance(artifact, dict):
        return ["artifact_must_be_an_object"]
    errors = []
    if artifact.get("schema_version") not in ARTIFACT_VERSIONS:
        errors.append("unsupported_schema_version")
    assertions = artifact.get("assertions")
    if not isinstance(assertions, list):
        return errors + ["assertions_must_be_an_array"]
    assertions_by_id = assertion_index(assertions)
    errors.extend(reference_errors(assertions, assertions_by_id))
    for index, assertion in enumerate(assertions):
        errors.extend(assertion_errors(assertion, index, assertions_by_id))
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
