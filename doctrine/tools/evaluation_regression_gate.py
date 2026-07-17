#!/usr/bin/env python3
"""Build and compare deterministic Books evaluation-composition snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema


SNAPSHOT_SCHEMA = "books-evaluation-snapshot/1"
CONFIG_SCHEMA = "books-evaluation-gate-config/1"
DEFAULT_BASELINE = Path("doctrine/evaluations/baselines/repository.json")
DEFAULT_CONFIG = Path("doctrine/evaluations/regression-gate.json")
SNAPSHOT_SCHEMA_PATH = Path("doctrine/evaluations/snapshot.schema.json")
CONFIG_SCHEMA_PATH = Path("doctrine/evaluations/regression-gate.schema.json")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return value


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _validate(document: dict[str, Any], schema_path: Path) -> None:
    jsonschema.Draft202012Validator(_read_json(schema_path)).validate(document)


def _score(count: int, passed: int) -> dict[str, float | int]:
    return {"count": count, "value": passed / count if count else 0.0}


def _contract_error(command: list[str], root: Path) -> str | None:
    process = subprocess.run(
        command, cwd=root, text=True, capture_output=True, check=False
    )
    if process.returncode == 0:
        return None
    return process.stderr.strip() or process.stdout.strip() or f"exit {process.returncode}"


def _suite(
    case_ids: list[str], kinds: Counter[str], errors: list[str]
) -> dict[str, Any]:
    return {
        "case_ids": sorted(case_ids),
        "kind_counts": dict(sorted(kinds.items())),
        "scores": {
            "contract_pass_rate": _score(
                len(case_ids), max(0, len(case_ids) - len(errors))
            )
        },
        "errors": sorted(errors),
    }


def _canary_suite(root: Path, evaluation_root: Path) -> dict[str, Any]:
    canary_ids: list[str] = []
    canary_kinds: Counter[str] = Counter()
    canary_errors: list[str] = []
    scenario_paths = (evaluation_root / "fixtures").glob("*/scenario.json")
    for scenario_path in sorted(scenario_paths):
        try:
            scenario = _read_json(scenario_path)
            case_id = str(scenario["id"])
            granted = bool(scenario.get("authority", {}).get("authorization_granted"))
            result_path = scenario_path.with_name("result.json")
            canary_ids.append(case_id)
            canary_kinds["authority-granted" if granted else "authority-withheld"] += 1
            error = _contract_error(
                [
                    sys.executable,
                    str(root / "doctrine/tools/run_scenario.py"),
                    str(scenario_path),
                    str(result_path),
                ],
                root,
            )
            if error:
                canary_errors.append(f"{case_id}: {error}")
        except (OSError, ValueError, KeyError, jsonschema.ValidationError) as exc:
            canary_errors.append(f"{scenario_path.relative_to(root)}: {exc}")
    return _suite(canary_ids, canary_kinds, canary_errors)


def _robustness_suite(root: Path, evaluation_root: Path) -> dict[str, Any]:
    robustness_ids: list[str] = []
    robustness_kinds: Counter[str] = Counter()
    robustness_errors: list[str] = []
    case_paths = (evaluation_root / "robustness" / "cases").glob("*.json")
    for case_path in sorted(case_paths):
        try:
            case = _read_json(case_path)
            robustness_ids.append(str(case["id"]))
            robustness_kinds[str(case["operator"]["id"])] += 1
            error = _contract_error(
                [
                    sys.executable,
                    str(root / "doctrine/tools/run_robustness_case.py"),
                    str(case_path),
                ],
                root,
            )
            if error:
                robustness_errors.append(f"{case['id']}: {error}")
        except (OSError, ValueError, KeyError, jsonschema.ValidationError) as exc:
            robustness_errors.append(f"{case_path.relative_to(root)}: {exc}")
    return _suite(robustness_ids, robustness_kinds, robustness_errors)


def _skill_suite(root: Path, evaluation_root: Path) -> dict[str, Any]:
    skill_ids: list[str] = []
    skill_kinds: Counter[str] = Counter()
    skill_errors: list[str] = []
    case_paths = (evaluation_root / "robustness" / "skill-cases").glob("*.json")
    for case_path in sorted(case_paths):
        try:
            case = _read_json(case_path)
            _validate(
                case,
                evaluation_root / "robustness" / "skill-eval-case.schema.json",
            )
            skill_ids.append(str(case["id"]))
            skill_kinds[str(case["oracle"]["detection_boundary"])] += 1
        except (OSError, ValueError, KeyError, jsonschema.ValidationError) as exc:
            skill_errors.append(f"{case_path.relative_to(root)}: {exc}")
    return _suite(skill_ids, skill_kinds, skill_errors)


def _queue_suite(root: Path, evaluation_root: Path) -> tuple[str, dict[str, Any]]:
    queue_path = evaluation_root / "gold" / "queue.json"
    coverage_path = evaluation_root / "gold" / "coverage.json"
    queue_ids: list[str] = []
    queue_kinds: Counter[str] = Counter()
    queue_errors: list[str] = []
    corpus_identity = "unavailable"
    queue_scores: dict[str, dict[str, float | int]] = {}
    try:
        queue = _read_json(queue_path)
        coverage = _read_json(coverage_path)
        _validate(queue, evaluation_root / "gold" / "queue.schema.json")
        for record in queue["records"]:
            queue_ids.append(str(record["id"]))
            queue_kinds[str(record["candidate"]["kind"])] += 1
        required_count = sum(len(values) for values in coverage["required"].values())
        covered_count = sum(len(values) for values in coverage["covered"].values())
        queue_scores["queue_coverage"] = _score(required_count, covered_count)
        corpus_identity = _canonical_sha256(queue["generation"]["input_sha256"])
    except (OSError, ValueError, KeyError, TypeError, jsonschema.ValidationError) as exc:
        queue_errors.append(f"{queue_path.relative_to(root)}: {exc}")

    queue_suite = _suite(queue_ids, queue_kinds, queue_errors)
    queue_suite["scores"].update(queue_scores)
    return corpus_identity, queue_suite


def build_snapshot(root: Path) -> dict[str, Any]:
    evaluation_root = root / "doctrine" / "evaluations"
    corpus_identity, queue_suite = _queue_suite(root, evaluation_root)
    return {
        "schema_version": SNAPSHOT_SCHEMA,
        "corpus_identity": corpus_identity,
        "suites": {
            "canaries": _canary_suite(root, evaluation_root),
            "entailment-queue": queue_suite,
            "robustness": _robustness_suite(root, evaluation_root),
            "skill-a-b": _skill_suite(root, evaluation_root),
        },
    }


def compare_snapshots(
    candidate: dict[str, Any], baseline: dict[str, Any], config: dict[str, Any]
) -> list[str]:
    violations: list[str] = []
    if candidate.get("schema_version") != SNAPSHOT_SCHEMA:
        violations.append(f"candidate schema must be {SNAPSHOT_SCHEMA}")
    if baseline.get("schema_version") != SNAPSHOT_SCHEMA:
        violations.append(f"baseline schema must be {SNAPSHOT_SCHEMA}")
    if config.get("schema_version") != CONFIG_SCHEMA:
        violations.append(f"config schema must be {CONFIG_SCHEMA}")
    if candidate.get("corpus_identity") != baseline.get("corpus_identity"):
        violations.append("corpus identity differs from baseline")

    candidate_suites = candidate.get("suites", {})
    baseline_suites = baseline.get("suites", {})
    for suite_name, baseline_suite in sorted(baseline_suites.items()):
        candidate_suite = candidate_suites.get(suite_name)
        if not isinstance(candidate_suite, dict):
            violations.append(f"missing suite: {suite_name}")
            continue
        removed = sorted(
            set(baseline_suite.get("case_ids", []))
            - set(candidate_suite.get("case_ids", []))
        )
        if removed:
            violations.append(f"{suite_name}: removed case IDs: {', '.join(removed)}")
        baseline_kind_counts = baseline_suite.get("kind_counts", {})
        for kind, baseline_count in sorted(baseline_kind_counts.items()):
            candidate_count = candidate_suite.get("kind_counts", {}).get(kind, 0)
            if candidate_count < baseline_count:
                violations.append(
                    f"{suite_name}: {kind} coverage shrank "
                    f"from {baseline_count} to {candidate_count}"
                )
        for error in candidate_suite.get("errors", []):
            violations.append(f"{suite_name}: run error: {error}")
        for score_name, rule in sorted(config.get("score_rules", {}).items()):
            baseline_score = baseline_suite.get("scores", {}).get(score_name)
            if baseline_score is None:
                continue
            candidate_score = candidate_suite.get("scores", {}).get(score_name)
            if candidate_score is None:
                violations.append(f"{suite_name}: missing score: {score_name}")
                continue
            value = float(candidate_score["value"])
            baseline_value = float(baseline_score["value"])
            floor = float(rule["absolute_floor"])
            tolerance = float(rule["baseline_tolerance"])
            if value < floor:
                violations.append(
                    f"{suite_name}: {score_name} {value:.6f} "
                    f"is below floor {floor:.6f}"
                )
            if value < baseline_value - tolerance:
                violations.append(
                    f"{suite_name}: {score_name} {value:.6f} regressed from {baseline_value:.6f} "
                    f"beyond tolerance {tolerance:.6f}"
                )
    return violations


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot_parser = subparsers.add_parser(
        "snapshot", help="write a review candidate snapshot"
    )
    snapshot_parser.add_argument("--root", type=Path, default=Path("."))
    snapshot_parser.add_argument("--out", type=Path, required=True)
    check_parser = subparsers.add_parser(
        "check", help="compare the repository to its committed baseline"
    )
    check_parser.add_argument("--root", type=Path, default=Path("."))
    check_parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    check_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    check_parser.add_argument(
        "--results",
        type=Path,
        help="normalized aggregate snapshot to check instead of inspecting the repository",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if args.command == "snapshot":
        _write_json(args.out, build_snapshot(root))
        print(f"wrote review candidate: {args.out}")
        return 0

    baseline_path = (
        args.baseline if args.baseline.is_absolute() else root / args.baseline
    )
    config_path = args.config if args.config.is_absolute() else root / args.config
    candidate = _read_json(args.results) if args.results else build_snapshot(root)
    baseline = _read_json(baseline_path)
    config = _read_json(config_path)
    _validate(candidate, root / SNAPSHOT_SCHEMA_PATH)
    _validate(baseline, root / SNAPSHOT_SCHEMA_PATH)
    _validate(config, root / CONFIG_SCHEMA_PATH)
    violations = compare_snapshots(candidate, baseline, config)
    if violations:
        for violation in violations:
            print(f"VIOLATION: {violation}", file=sys.stderr)
        return 1
    print("evaluation regression gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
