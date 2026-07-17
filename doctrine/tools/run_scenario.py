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


def scenario_contract_errors(scenario: object) -> list[str]:
    if not isinstance(scenario, dict):
        return ["scenario_must_be_an_object"]
    if "expected" not in scenario:
        return ["scenario_expected_is_required"]
    expected = scenario["expected"]
    if not isinstance(expected, dict):
        return ["scenario_expected_must_be_an_object"]
    return []


def evaluate_scenario(scenario: object, result_artifact: object) -> list[str]:
    scenario_errors = scenario_contract_errors(scenario)
    if scenario_errors:
        return scenario_errors
    if not isinstance(result_artifact, dict):
        return ["result_must_be_an_object"]
    assert isinstance(scenario, dict)
    expected = scenario["expected"]
    assert isinstance(expected, dict)
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
    except (OSError, json.JSONDecodeError) as error:
        print(f"infrastructure-failure: unable_to_read_scenario: {error}", file=sys.stderr)
        return 2
    infrastructure_errors = scenario_contract_errors(scenario)
    if infrastructure_errors:
        print(
            "\n".join(f"infrastructure-failure: {error}" for error in infrastructure_errors),
            file=sys.stderr,
        )
        return 2

    try:
        result_artifact = load_json(args.result)
    except OSError as error:
        print(f"infrastructure-failure: unable_to_read_result: {error}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"model-failure: invalid_result_json: {error}", file=sys.stderr)
        return 1

    errors = evaluate_scenario(scenario, result_artifact)
    if isinstance(result_artifact, dict):
        errors.extend(validate_artifact(result_artifact))
    if errors:
        print("\n".join(f"model-failure: {error}" for error in errors), file=sys.stderr)
        return 1
    assert isinstance(scenario, dict)
    print(f"model-outcome: scenario passed: {scenario.get('id', args.scenario.name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
