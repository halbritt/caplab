"""Deterministic CAPLAB evaluation snapshots."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence as SequenceABC
from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex

from .replay import EvaluationReplay


SNAPSHOT_SCHEMA = "caplab-evaluation-snapshot/1"
POLICY_SCHEMA = "caplab-evaluation-gate-policy/1"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SnapshotContractError(ValueError):
    """A snapshot input violates the CAPLAB evaluation contract."""


@dataclass(frozen=True, slots=True)
class EvaluationScenario:
    scenario_id: str
    kind: str
    replay: EvaluationReplay


@dataclass(frozen=True, slots=True)
class EvaluationGateResult:
    passed: bool
    candidate_sha256: str
    baseline_sha256: str
    policy_sha256: str
    violations: tuple[str, ...]


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    return value


def _canonical_sha256(value: Any, label: str) -> str:
    try:
        return sha256_hex(canonical_json(value))
    except CanonicalizationError as error:
        raise SnapshotContractError(f"noncanonical_{label}") from error


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: frozenset[str],
    location: str,
) -> None:
    if set(value) != expected:
        raise SnapshotContractError(
            f"invalid_shape:{location}:"
            f"missing={sorted(expected - set(value))}:"
            f"extra={sorted(set(value) - expected)}"
        )


def _as_sequence(value: Any, location: str) -> Sequence[Any]:
    if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
        raise SnapshotContractError(f"invalid_sequence:{location}")
    return value


def _ratio(value: Any, location: str) -> Fraction:
    if not isinstance(value, Mapping):
        raise SnapshotContractError(f"invalid_ratio:{location}")
    _require_exact_keys(value, frozenset({"numerator", "denominator"}), location)
    numerator, denominator = value["numerator"], value["denominator"]
    if (
        not isinstance(numerator, int)
        or isinstance(numerator, bool)
        or not isinstance(denominator, int)
        or isinstance(denominator, bool)
        or denominator <= 0
        or numerator < 0
        or numerator > denominator
    ):
        raise SnapshotContractError(f"invalid_ratio:{location}")
    return Fraction(numerator, denominator)


def _validate_snapshot(snapshot: Mapping[str, Any], label: str) -> None:
    expected = frozenset(
        {"schema_version", "corpus_sha256", "scenarios", "kind_counts", "scores", "errors"}
    )
    _require_exact_keys(snapshot, expected, label)
    if snapshot["schema_version"] != SNAPSHOT_SCHEMA:
        raise SnapshotContractError(
            f"unsupported_snapshot_schema:{label}:{snapshot['schema_version']}"
        )
    if not isinstance(snapshot["corpus_sha256"], str) or not SHA256.fullmatch(
        snapshot["corpus_sha256"]
    ):
        raise SnapshotContractError(f"invalid_corpus_sha256:{label}")
    scenarios = _as_sequence(snapshot["scenarios"], f"{label}.scenarios")
    if not scenarios:
        raise SnapshotContractError(f"snapshot_requires_scenario:{label}")
    _validate_scenario_records(scenarios, snapshot, label)
    errors = _as_sequence(snapshot["errors"], f"{label}.errors")
    if any(not isinstance(error, str) or not error for error in errors):
        raise SnapshotContractError(f"invalid_snapshot_error:{label}")
    if len(set(errors)) != len(errors):
        raise SnapshotContractError(f"duplicate_snapshot_error:{label}")


def _validate_scenario_records(
    scenarios: Sequence[Any],
    snapshot: Mapping[str, Any],
    label: str,
) -> None:
    expected = frozenset(
        {
            "id",
            "kind",
            "fixture_sha256",
            "outcome_class",
            "score_eligible",
            "may_supply_model_evidence",
        }
    )
    ids: list[str] = []
    kinds: Counter[str] = Counter()
    score_eligible = 0
    model_evidence = 0
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, Mapping):
            raise SnapshotContractError(f"invalid_scenario:{label}:{index}")
        _require_exact_keys(scenario, expected, f"{label}.scenarios[{index}]")
        scenario_id, kind = scenario["id"], scenario["kind"]
        if not isinstance(scenario_id, str) or not SAFE_NAME.fullmatch(scenario_id):
            raise SnapshotContractError(f"invalid_scenario_id:{label}:{index}")
        if not isinstance(kind, str) or not SAFE_NAME.fullmatch(kind):
            raise SnapshotContractError(f"invalid_scenario_kind:{label}:{index}")
        if not isinstance(scenario["fixture_sha256"], str) or not SHA256.fullmatch(
            scenario["fixture_sha256"]
        ):
            raise SnapshotContractError(f"invalid_fixture_sha256:{label}:{index}")
        if not isinstance(scenario["outcome_class"], str) or scenario[
            "outcome_class"
        ] not in {
            "model-outcome",
            "model-failure",
            "infrastructure-failure",
            "not-evaluated",
        }:
            raise SnapshotContractError(f"invalid_outcome_class:{label}:{index}")
        if type(scenario["score_eligible"]) is not bool or type(
            scenario["may_supply_model_evidence"]
        ) is not bool:
            raise SnapshotContractError(f"invalid_scenario_flags:{label}:{index}")
        if scenario["may_supply_model_evidence"] and not scenario["score_eligible"]:
            raise SnapshotContractError(f"contradictory_scenario_flags:{label}:{index}")
        ids.append(scenario_id)
        kinds[kind] += 1
        score_eligible += scenario["score_eligible"]
        model_evidence += scenario["may_supply_model_evidence"]
    if ids != sorted(ids) or len(set(ids)) != len(ids):
        raise SnapshotContractError(f"noncanonical_scenario_inventory:{label}")
    _validate_snapshot_aggregates(snapshot, kinds, score_eligible, model_evidence, label)


def _validate_snapshot_aggregates(
    snapshot: Mapping[str, Any],
    kinds: Counter[str],
    score_eligible: int,
    model_evidence: int,
    label: str,
) -> None:
    if snapshot["kind_counts"] != dict(sorted(kinds.items())):
        raise SnapshotContractError(f"kind_count_mismatch:{label}")
    scores = snapshot["scores"]
    if not isinstance(scores, Mapping):
        raise SnapshotContractError(f"invalid_scores:{label}")
    expected_scores = {
        "model_evidence_rate": model_evidence,
        "score_eligibility_rate": score_eligible,
    }
    if set(scores) != set(expected_scores):
        raise SnapshotContractError(f"invalid_score_inventory:{label}")
    for name, numerator in expected_scores.items():
        ratio = _ratio(scores[name], f"{label}.scores.{name}")
        if ratio != Fraction(numerator, len(snapshot["scenarios"])):
            raise SnapshotContractError(f"score_mismatch:{label}:{name}")


def _validate_policy(policy: Mapping[str, Any]) -> None:
    expected = frozenset(
        {"schema_version", "baseline_sha256", "decision", "required_kind_counts", "score_rules"}
    )
    _require_exact_keys(policy, expected, "policy")
    if policy["schema_version"] != POLICY_SCHEMA:
        raise SnapshotContractError(
            f"unsupported_policy_schema:{policy['schema_version']}"
        )
    if not isinstance(policy["baseline_sha256"], str) or not SHA256.fullmatch(
        policy["baseline_sha256"]
    ):
        raise SnapshotContractError("invalid_policy_baseline_sha256")
    decision = policy["decision"]
    if not isinstance(decision, Mapping):
        raise SnapshotContractError("invalid_policy_decision")
    _require_exact_keys(
        decision,
        frozenset({"id", "decided_by", "authority"}),
        "policy.decision",
    )
    if any(not isinstance(value, str) or not value for value in decision.values()):
        raise SnapshotContractError("invalid_policy_decision")
    counts = policy["required_kind_counts"]
    if not isinstance(counts, Mapping) or not counts:
        raise SnapshotContractError("invalid_required_kind_counts")
    for kind, count in counts.items():
        if not isinstance(kind, str) or not SAFE_NAME.fullmatch(kind):
            raise SnapshotContractError(f"invalid_required_kind:{kind}")
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise SnapshotContractError(f"invalid_required_kind_count:{kind}")
    rules = policy["score_rules"]
    if not isinstance(rules, Mapping) or not rules:
        raise SnapshotContractError("invalid_score_rules")
    for score_name, rule in rules.items():
        if score_name not in {"model_evidence_rate", "score_eligibility_rate"}:
            raise SnapshotContractError(f"unknown_score_rule:{score_name}")
        if not isinstance(rule, Mapping):
            raise SnapshotContractError(f"invalid_score_rule:{score_name}")
        _require_exact_keys(
            rule,
            frozenset({"absolute_floor", "max_baseline_drop"}),
            f"policy.score_rules.{score_name}",
        )
        _ratio(rule["absolute_floor"], f"policy.score_rules.{score_name}.absolute_floor")
        _ratio(
            rule["max_baseline_drop"],
            f"policy.score_rules.{score_name}.max_baseline_drop",
        )


def _scenario_record(scenario: EvaluationScenario) -> dict[str, Any]:
    if not isinstance(scenario.scenario_id, str) or not SAFE_NAME.fullmatch(
        scenario.scenario_id
    ):
        raise SnapshotContractError(f"invalid_scenario_id:{scenario.scenario_id}")
    if not isinstance(scenario.kind, str) or not SAFE_NAME.fullmatch(scenario.kind):
        raise SnapshotContractError(f"invalid_scenario_kind:{scenario.kind}")
    if not isinstance(scenario.replay, EvaluationReplay):
        raise SnapshotContractError(f"invalid_scenario_replay:{scenario.scenario_id}")
    return {
        "id": scenario.scenario_id,
        "kind": scenario.kind,
        "fixture_sha256": scenario.replay.fixture_sha256,
        "outcome_class": scenario.replay.outcome_class,
        "score_eligible": scenario.replay.score_eligible,
        "may_supply_model_evidence": scenario.replay.may_supply_model_evidence,
    }


def build_evaluation_snapshot(
    *,
    corpus_sha256: str,
    scenarios: Sequence[EvaluationScenario],
    errors: Sequence[str] = (),
) -> Mapping[str, Any]:
    """Build one immutable aggregate from already-replayed synthetic scenarios."""

    if not isinstance(corpus_sha256, str) or not SHA256.fullmatch(corpus_sha256):
        raise SnapshotContractError(f"invalid_corpus_sha256:{corpus_sha256}")
    if not scenarios:
        raise SnapshotContractError("snapshot_requires_scenario")
    records: list[dict[str, Any]] = []
    kind_counts: Counter[str] = Counter()
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, EvaluationScenario):
            raise SnapshotContractError(f"invalid_evaluation_scenario:{index}")
        record = _scenario_record(scenario)
        kind_counts[record["kind"]] += 1
        records.append(record)
    records.sort(key=lambda item: item["id"])
    scenario_ids = [record["id"] for record in records]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise SnapshotContractError("duplicate_scenario_id")
    if any(not isinstance(error, str) or not error for error in errors):
        raise SnapshotContractError("invalid_snapshot_error")
    normalized_errors = sorted(set(errors))
    count = len(records)
    snapshot = {
        "schema_version": SNAPSHOT_SCHEMA,
        "corpus_sha256": corpus_sha256,
        "scenarios": records,
        "kind_counts": dict(sorted(kind_counts.items())),
        "scores": {
            "model_evidence_rate": {
                "numerator": sum(item["may_supply_model_evidence"] for item in records),
                "denominator": count,
            },
            "score_eligibility_rate": {
                "numerator": sum(item["score_eligible"] for item in records),
                "denominator": count,
            },
        },
        "errors": normalized_errors,
    }
    return _freeze(snapshot)


def _identity_violations(
    candidate: Mapping[str, Any],
    baseline: Mapping[str, Any],
    policy: Mapping[str, Any],
    baseline_sha256: str,
) -> list[str]:
    violations: list[str] = []
    if policy["baseline_sha256"] != baseline_sha256:
        violations.append("policy_baseline_identity_mismatch")
    if candidate["corpus_sha256"] != baseline["corpus_sha256"]:
        violations.append("corpus_identity_mismatch")
    if baseline["errors"]:
        violations.append("baseline_contains_run_errors")
    candidate_by_id = {item["id"]: item for item in candidate["scenarios"]}
    for baseline_scenario in baseline["scenarios"]:
        scenario_id = baseline_scenario["id"]
        candidate_scenario = candidate_by_id.get(scenario_id)
        if candidate_scenario is None:
            violations.append(f"removed_scenario:{scenario_id}")
            continue
        for identity_field in ("kind", "fixture_sha256"):
            if candidate_scenario[identity_field] != baseline_scenario[identity_field]:
                violations.append(f"substituted_scenario:{scenario_id}:{identity_field}")
    return violations


def _coverage_violations(
    candidate: Mapping[str, Any],
    baseline: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> list[str]:
    required_counts = dict(baseline["kind_counts"])
    for kind, count in policy["required_kind_counts"].items():
        required_counts[kind] = max(required_counts.get(kind, 0), count)
    violations = []
    for kind, count in sorted(required_counts.items()):
        candidate_count = candidate["kind_counts"].get(kind, 0)
        if candidate_count < count:
            violations.append(f"coverage_shrank:{kind}:{count}:{candidate_count}")
    violations.extend(f"run_error:{error}" for error in candidate["errors"])
    return violations


def _score_violations(
    candidate: Mapping[str, Any],
    baseline: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> list[str]:
    violations: list[str] = []
    for score_name, rule in sorted(policy["score_rules"].items()):
        candidate_score = _ratio(
            candidate["scores"][score_name], f"candidate.scores.{score_name}"
        )
        baseline_score = _ratio(
            baseline["scores"][score_name], f"baseline.scores.{score_name}"
        )
        floor = _ratio(
            rule["absolute_floor"],
            f"policy.score_rules.{score_name}.absolute_floor",
        )
        tolerance = _ratio(
            rule["max_baseline_drop"],
            f"policy.score_rules.{score_name}.max_baseline_drop",
        )
        if candidate_score < floor:
            violations.append(f"absolute_floor_failed:{score_name}")
        if candidate_score < baseline_score - tolerance:
            violations.append(f"baseline_regression:{score_name}")
    return violations


def compare_evaluation_snapshots(
    *,
    candidate: Mapping[str, Any],
    baseline: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> EvaluationGateResult:
    """Compare one candidate to the separately approved baseline and policy."""

    for label, document in (
        ("candidate", candidate),
        ("baseline", baseline),
        ("policy", policy),
    ):
        if not isinstance(document, Mapping):
            raise SnapshotContractError(f"document_is_not_object:{label}")
    _validate_snapshot(candidate, "candidate")
    _validate_snapshot(baseline, "baseline")
    _validate_policy(policy)
    candidate_sha256 = _canonical_sha256(candidate, "candidate")
    baseline_sha256 = _canonical_sha256(baseline, "baseline")
    policy_sha256 = _canonical_sha256(policy, "policy")
    violations = _identity_violations(candidate, baseline, policy, baseline_sha256)
    violations.extend(_coverage_violations(candidate, baseline, policy))
    violations.extend(_score_violations(candidate, baseline, policy))
    normalized = tuple(sorted(set(violations)))
    return EvaluationGateResult(
        passed=not normalized,
        candidate_sha256=candidate_sha256,
        baseline_sha256=baseline_sha256,
        policy_sha256=policy_sha256,
        violations=normalized,
    )
