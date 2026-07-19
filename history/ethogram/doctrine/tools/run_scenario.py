#!/usr/bin/env python3
"""Replay one doctrine scenario against a result artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_assertions import validate_artifact


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def assertion_expectation_errors(
    expected: dict[str, object], result_artifact: dict[str, object]
) -> list[str]:
    assertions = result_artifact.get("assertions", [])
    assertion_types = {
        assertion.get("type")
        for assertion in assertions
        if isinstance(assertion, dict)
    }
    missing = [
        f"missing_assertion_type: {assertion_type}"
        for assertion_type in expected.get("required_assertion_types", [])
        if assertion_type not in assertion_types
    ]
    forbidden = [
        f"forbidden_assertion_type: {assertion_type}"
        for assertion_type in expected.get("forbidden_assertion_types", [])
        if assertion_type in assertion_types
    ]
    return missing + forbidden


def retrieval_expectation_errors(
    expected: dict[str, object], result_artifact: dict[str, object]
) -> list[str]:
    retrieved_ids = set(result_artifact.get("retrieved_evidence_ids", []))
    missing = [
        f"missing_retrieval: {evidence_id}"
        for evidence_id in expected.get("required_retrieval_ids", [])
        if evidence_id not in retrieved_ids
    ]
    forbidden = [
        f"forbidden_retrieval: {evidence_id}"
        for evidence_id in expected.get("forbidden_retrieval_ids", [])
        if evidence_id in retrieved_ids
    ]
    return missing + forbidden


def evaluate_scenario(scenario: object, result_artifact: object) -> list[str]:
    if not isinstance(scenario, dict) or not isinstance(result_artifact, dict):
        return ["scenario_and_result_must_be_objects"]

    expected = scenario.get("expected", {})
    if not isinstance(expected, dict):
        return ["scenario_expected_must_be_an_object"]
    return assertion_expectation_errors(
        expected, result_artifact
    ) + retrieval_expectation_errors(expected, result_artifact)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a result artifact against a doctrine scenario."
    )
    parser.add_argument("scenario", type=Path)
    parser.add_argument("result", type=Path)
    args = parser.parse_args()

    try:
        scenario = load_json(args.scenario)
        result_artifact = load_json(args.result)
    except (OSError, json.JSONDecodeError) as error:
        print(f"unable_to_read_scenario: {error}", file=sys.stderr)
        return 2

    errors = evaluate_scenario(scenario, result_artifact)
    if isinstance(result_artifact, dict):
        errors.extend(validate_artifact(result_artifact))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"scenario passed: {scenario.get('id', args.scenario.name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
