"""Behavioral contracts for CAPLAB evaluation snapshots and defect records."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caplab.evaluation import (
    DefectLedgerError,
    EvaluationScenario,
    SnapshotContractError,
    build_evaluation_snapshot,
    compare_evaluation_snapshots,
    load_defect_ledger,
    record_defect_disposition,
    record_defect_inference,
    record_gate_observation,
    replay_synthetic_fixture,
)
from caplab.runtime.canonical import canonical_json, sha256_hex


REPLAY_FIXTURES = Path(__file__).parent / "fixtures" / "evaluation" / "replay"
PRODUCT_EVALUATION = Path(__file__).parents[1] / "docs" / "product" / "evaluation"
BASELINE_PATH = PRODUCT_EVALUATION / "synthetic-replay-baseline-v1.json"
POLICY_PATH = PRODUCT_EVALUATION / "synthetic-replay-policy-v1.json"
CORPUS_SHA256 = "c30c179d6d1b2aa5b575557a4e0365b3bc70e422b61874c720318acc3c56ecc9"


def passing_snapshot_and_policy() -> tuple[dict[str, object], dict[str, object]]:
    return (
        json.loads(BASELINE_PATH.read_text(encoding="utf-8")),
        json.loads(POLICY_PATH.read_text(encoding="utf-8")),
    )


def mutable_copy(value: object) -> dict[str, object]:
    return json.loads(canonical_json(value))


class EvaluationSnapshotTests(unittest.TestCase):
    def test_snapshot_binds_replayed_scenario_identity_outcome_and_coverage(self) -> None:
        replay = replay_synthetic_fixture(
            REPLAY_FIXTURES,
            "constraint-continuity-pass",
            execution_mode="replay",
        )

        snapshot = build_evaluation_snapshot(
            corpus_sha256=CORPUS_SHA256,
            scenarios=(
                EvaluationScenario(
                    scenario_id="constraint-continuity-pass",
                    kind="authority-preservation",
                    replay=replay,
                ),
            ),
        )

        self.assertEqual(snapshot["schema_version"], "caplab-evaluation-snapshot/1")
        self.assertEqual(snapshot["corpus_sha256"], CORPUS_SHA256)
        self.assertEqual(snapshot["kind_counts"], {"authority-preservation": 1})
        self.assertEqual(
            snapshot["scenarios"][0],
            {
                "id": "constraint-continuity-pass",
                "kind": "authority-preservation",
                "fixture_sha256": replay.fixture_sha256,
                "outcome_class": "model-outcome",
                "score_eligible": True,
                "may_supply_model_evidence": True,
            },
        )
        self.assertEqual(
            snapshot["scores"]["model_evidence_rate"],
            {"numerator": 1, "denominator": 1},
        )
        self.assertEqual(snapshot["errors"], ())
        baseline, _ = passing_snapshot_and_policy()
        self.assertEqual(json.loads(canonical_json(snapshot)), baseline)

    def test_identical_approved_snapshot_passes(self) -> None:
        baseline, policy = passing_snapshot_and_policy()

        result = compare_evaluation_snapshots(
            candidate=baseline,
            baseline=baseline,
            policy=policy,
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.violations, ())
        self.assertEqual(
            result.baseline_sha256,
            sha256_hex(canonical_json(baseline)),
        )

    def test_removed_and_substituted_scenarios_are_refused(self) -> None:
        baseline, policy = passing_snapshot_and_policy()
        removed = mutable_copy(baseline)
        removed["scenarios"][0]["id"] = "replacement-scenario"
        substituted = mutable_copy(baseline)
        substituted["scenarios"][0]["fixture_sha256"] = "a" * 64

        removed_result = compare_evaluation_snapshots(
            candidate=removed,
            baseline=baseline,
            policy=policy,
        )
        substituted_result = compare_evaluation_snapshots(
            candidate=substituted,
            baseline=baseline,
            policy=policy,
        )

        self.assertIn(
            "removed_scenario:constraint-continuity-pass",
            removed_result.violations,
        )
        self.assertIn(
            "substituted_scenario:constraint-continuity-pass:fixture_sha256",
            substituted_result.violations,
        )

    def test_coverage_shrinkage_and_run_errors_are_refused(self) -> None:
        baseline, policy = passing_snapshot_and_policy()
        candidate = mutable_copy(baseline)
        candidate["scenarios"][0]["kind"] = "different-kind"
        candidate["kind_counts"] = {"different-kind": 1}
        candidate["errors"] = ["synthetic harness failed"]

        result = compare_evaluation_snapshots(
            candidate=candidate,
            baseline=baseline,
            policy=policy,
        )

        self.assertIn(
            "coverage_shrank:authority-preservation:1:0",
            result.violations,
        )
        self.assertIn("run_error:synthetic harness failed", result.violations)

    def test_floor_failure_and_baseline_regression_are_refused(self) -> None:
        baseline, policy = passing_snapshot_and_policy()
        candidate = mutable_copy(baseline)
        candidate["scenarios"][0].update(
            {
                "outcome_class": "model-failure",
                "may_supply_model_evidence": False,
            }
        )
        candidate["scores"]["model_evidence_rate"] = {
            "numerator": 0,
            "denominator": 1,
        }

        result = compare_evaluation_snapshots(
            candidate=candidate,
            baseline=baseline,
            policy=policy,
        )

        self.assertIn(
            "absolute_floor_failed:model_evidence_rate",
            result.violations,
        )
        self.assertIn(
            "baseline_regression:model_evidence_rate",
            result.violations,
        )

    def test_unapproved_baseline_identity_is_refused(self) -> None:
        baseline, policy = passing_snapshot_and_policy()
        policy["baseline_sha256"] = "b" * 64

        result = compare_evaluation_snapshots(
            candidate=baseline,
            baseline=baseline,
            policy=policy,
        )

        self.assertEqual(result.violations, ("policy_baseline_identity_mismatch",))

    def test_self_inconsistent_aggregate_is_a_contract_error(self) -> None:
        baseline, policy = passing_snapshot_and_policy()
        candidate = mutable_copy(baseline)
        candidate["kind_counts"]["authority-preservation"] = 9

        with self.assertRaisesRegex(
            SnapshotContractError,
            "kind_count_mismatch:candidate",
        ):
            compare_evaluation_snapshots(
                candidate=candidate,
                baseline=baseline,
                policy=policy,
            )


class EvaluationDefectLedgerTests(unittest.TestCase):
    def test_gate_observation_is_digest_bound_append_only_and_idempotent(self) -> None:
        baseline, policy = passing_snapshot_and_policy()
        candidate = mutable_copy(baseline)
        candidate["errors"] = ["synthetic harness failed"]
        result = compare_evaluation_snapshots(
            candidate=candidate,
            baseline=baseline,
            policy=policy,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger_path = Path(temporary_directory) / "defects.jsonl"
            first = record_gate_observation(
                ledger_path,
                result=result,
                recorded_at="2026-07-20T16:00:00Z",
            )
            second = record_gate_observation(
                ledger_path,
                result=result,
                recorded_at="2026-07-20T16:01:00Z",
            )
            events = load_defect_ledger(ledger_path)

            self.assertEqual(first, second)
            self.assertEqual(len(events), 1)
            self.assertEqual(first["assertion_type"], "observation")
            self.assertEqual(first["candidate_sha256"], result.candidate_sha256)
            self.assertEqual(first["violations"], result.violations)
            self.assertTrue(first["event_id"].startswith("obs-"))
            self.assertTrue(first["defect_id"].startswith("gate-"))

    def test_inference_and_disposition_remain_linked_typed_records(self) -> None:
        baseline, policy = passing_snapshot_and_policy()
        candidate = mutable_copy(baseline)
        candidate["errors"] = ["synthetic harness failed"]
        result = compare_evaluation_snapshots(
            candidate=candidate,
            baseline=baseline,
            policy=policy,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger_path = Path(temporary_directory) / "defects.jsonl"
            observation = record_gate_observation(
                ledger_path,
                result=result,
                recorded_at="2026-07-20T16:00:00Z",
            )
            inference = record_defect_inference(
                ledger_path,
                defect_id=observation["defect_id"],
                summary="The synthetic harness error may be local fixture damage.",
                evidence=("gate-result:run_error",),
                rivals=("snapshot comparator defect", "intentional candidate change"),
                inferred_by="primary-agent",
                recorded_at="2026-07-20T16:02:00Z",
            )
            disposition = record_defect_disposition(
                ledger_path,
                defect_id=observation["defect_id"],
                status="deferred",
                rationale="No production evidence depends on the synthetic candidate.",
                decided_by="primary-agent",
                authority="adr-0026",
                recorded_at="2026-07-20T16:03:00Z",
            )
            events = load_defect_ledger(ledger_path)

            self.assertEqual(len(events), 3)
            self.assertEqual(inference["assertion_type"], "inference")
            self.assertEqual(disposition["assertion_type"], "decision")
            self.assertEqual(
                inference["observation_sha256"],
                observation["observation_sha256"],
            )
            self.assertEqual(
                disposition["observation_event_id"],
                observation["event_id"],
            )
            self.assertEqual(disposition["authority"], "adr-0026")

    def test_inference_cannot_precede_its_observation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger_path = Path(temporary_directory) / "defects.jsonl"

            with self.assertRaisesRegex(
                DefectLedgerError,
                "observation_not_found:gate-0000000000000000",
            ):
                record_defect_inference(
                    ledger_path,
                    defect_id="gate-0000000000000000",
                    summary="Unsupported inference.",
                    evidence=("missing",),
                    rivals=("missing observation",),
                    inferred_by="primary-agent",
                    recorded_at="2026-07-20T16:02:00Z",
                )

    def test_tampered_observation_is_detected_without_repair(self) -> None:
        baseline, policy = passing_snapshot_and_policy()
        candidate = mutable_copy(baseline)
        candidate["errors"] = ["synthetic harness failed"]
        result = compare_evaluation_snapshots(
            candidate=candidate,
            baseline=baseline,
            policy=policy,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger_path = Path(temporary_directory) / "defects.jsonl"
            record_gate_observation(
                ledger_path,
                result=result,
                recorded_at="2026-07-20T16:00:00Z",
            )
            event = json.loads(ledger_path.read_text(encoding="utf-8"))
            event["violations"] = ["different violation"]
            ledger_path.write_text(
                json.dumps(event, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                DefectLedgerError,
                "observation_digest_mismatch:1",
            ):
                load_defect_ledger(ledger_path)

    def test_symlinked_ledger_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "target.jsonl"
            target.write_text("", encoding="utf-8")
            ledger_path = Path(temporary_directory) / "defects.jsonl"
            ledger_path.symlink_to(target)

            with self.assertRaisesRegex(
                DefectLedgerError,
                "ledger_path_is_symlink",
            ):
                load_defect_ledger(ledger_path)


if __name__ == "__main__":
    unittest.main()
