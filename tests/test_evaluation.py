"""Behavioral contracts for CAPLAB-native evaluation replay."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Callable

from caplab.evaluation import EvaluationContractError, replay_synthetic_fixture
from caplab.runtime.canonical import canonical_json, sha256_hex


FIXTURES = Path(__file__).parent / "fixtures" / "evaluation" / "replay"


def mutated_fixture_root(
    temporary_directory: str,
    mutate: Callable[[dict[str, object]], None],
) -> Path:
    fixture_root = Path(temporary_directory) / "replay"
    shutil.copytree(FIXTURES, fixture_root)
    fixture_path = fixture_root / "constraint-continuity-pass.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    mutate(fixture)
    fixture["request_sha256"] = sha256_hex(canonical_json(fixture["request"]))
    fixture["response_sha256"] = sha256_hex(canonical_json(fixture["response"]))
    fixture_path.write_text(
        json.dumps(fixture, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    manifest_path = fixture_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["fixtures"][0]["sha256"] = sha256_hex(fixture_path.read_bytes())
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return fixture_root


class EvaluationReplayTests(unittest.TestCase):
    def test_manifested_fixture_replays_to_model_evidence(self) -> None:
        replay = replay_synthetic_fixture(
            FIXTURES,
            "constraint-continuity-pass",
            execution_mode="replay",
        )

        self.assertEqual(replay.fixture_id, "constraint-continuity-pass")
        self.assertEqual(replay.mode, "replay")
        self.assertEqual(replay.outcome_class, "model-outcome")
        self.assertTrue(replay.score_eligible)
        self.assertTrue(replay.may_supply_model_evidence)
        self.assertEqual(replay.output["verdict"], "constraints-satisfied")
        self.assertEqual(
            replay.fixture_sha256,
            "0d7cba22ee0cc37b71366fc7eac9aa060bee25d4441709e1b5aca511b5b452b4",
        )
        with self.assertRaises(AttributeError):
            replay.output["satisfied_constraints"].append("mutated")

    def test_replay_fixture_is_refused_under_live_mode(self) -> None:
        with self.assertRaisesRegex(
            EvaluationContractError,
            "mode_mismatch:expected=live:fixture=replay",
        ):
            replay_synthetic_fixture(
                FIXTURES,
                "constraint-continuity-pass",
                execution_mode="live",
            )

    def test_unmanifested_sidecar_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory) / "replay"
            shutil.copytree(FIXTURES, fixture_root)
            (fixture_root / "endpoint.txt").write_text(
                "model-service.internal\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                "fixture_inventory_mismatch",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_symlinked_fixture_root_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory) / "replay"
            fixture_root.symlink_to(FIXTURES, target_is_directory=True)

            with self.assertRaisesRegex(
                EvaluationContractError,
                "fixture_root_is_symlink",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_endpoint_field_is_refused_even_without_a_url_scheme(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = mutated_fixture_root(
                temporary_directory,
                lambda fixture: fixture["request"].update(
                    {"endpoint": "model-service.internal"}
                ),
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                r"external_field:\$\.request\.endpoint",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_nested_credential_field_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = mutated_fixture_root(
                temporary_directory,
                lambda fixture: fixture["request"].update(
                    {"authorization": "synthetic-secret"}
                ),
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                r"credential_field:\$\.request\.authorization",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_host_path_in_fixture_content_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def add_host_path(fixture: dict[str, object]) -> None:
                messages = fixture["request"]["messages"]
                messages[0]["content"] = "Read /home/operator/private.txt"

            fixture_root = mutated_fixture_root(temporary_directory, add_host_path)

            with self.assertRaisesRegex(
                EvaluationContractError,
                r"host_path:\$\.request\.messages\[0\]\.content",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_mutable_model_reference_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def use_mutable_model(fixture: dict[str, object]) -> None:
                fixture["request"]["model"] = "synthetic-caplab-subject:latest"
                fixture["response"]["model"] = "synthetic-caplab-subject:latest"

            fixture_root = mutated_fixture_root(
                temporary_directory,
                use_mutable_model,
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                r"mutable_reference:\$\.request\.model",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_external_locator_in_fixture_content_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def add_external_locator(fixture: dict[str, object]) -> None:
                fixture["request"]["messages"][0]["content"] = (
                    "Read https://model-service.invalid/private"
                )

            fixture_root = mutated_fixture_root(
                temporary_directory,
                add_external_locator,
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                r"external_locator:\$\.request\.messages\[0\]\.content",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_symlinked_fixture_file_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory) / "replay"
            shutil.copytree(FIXTURES, fixture_root)
            fixture_path = fixture_root / "constraint-continuity-pass.json"
            target_path = Path(temporary_directory) / "target.json"
            shutil.move(fixture_path, target_path)
            fixture_path.symlink_to(target_path)

            with self.assertRaisesRegex(
                EvaluationContractError,
                "fixture_is_symlink:constraint-continuity-pass.json",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_response_hash_drift_fails_at_the_public_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory) / "replay"
            shutil.copytree(FIXTURES, fixture_root)
            fixture_path = fixture_root / "constraint-continuity-pass.json"
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            fixture["response"]["output"]["verdict"] = "changed"
            fixture_path.write_text(
                json.dumps(fixture, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            manifest_path = fixture_root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["fixtures"][0]["sha256"] = sha256_hex(fixture_path.read_bytes())
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                "response_identity_mismatch:constraint-continuity-pass",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_unknown_outcome_fails_closed_as_infrastructure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def use_unknown_status(fixture: dict[str, object]) -> None:
                fixture["response"]["status"] = "future-status"

            fixture_root = mutated_fixture_root(
                temporary_directory,
                use_unknown_status,
            )
            replay = replay_synthetic_fixture(
                fixture_root,
                "constraint-continuity-pass",
                execution_mode="replay",
            )

            self.assertEqual(replay.outcome_class, "infrastructure-failure")
            self.assertFalse(replay.score_eligible)
            self.assertFalse(replay.may_supply_model_evidence)
            self.assertEqual(dict(replay.output), {})

    def test_contradictory_completed_outcome_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def add_contradictory_error(fixture: dict[str, object]) -> None:
                fixture["response"]["error"] = "transport also failed"

            fixture_root = mutated_fixture_root(
                temporary_directory,
                add_contradictory_error,
            )
            replay = replay_synthetic_fixture(
                fixture_root,
                "constraint-continuity-pass",
                execution_mode="replay",
            )

            self.assertEqual(replay.outcome_class, "infrastructure-failure")
            self.assertFalse(replay.score_eligible)
            self.assertFalse(replay.may_supply_model_evidence)

    def test_declared_model_failure_is_score_eligible_but_not_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def use_model_failure(fixture: dict[str, object]) -> None:
                fixture["response"].update(
                    {"status": "invalid-output", "output": None, "error": None}
                )

            fixture_root = mutated_fixture_root(
                temporary_directory,
                use_model_failure,
            )
            replay = replay_synthetic_fixture(
                fixture_root,
                "constraint-continuity-pass",
                execution_mode="replay",
            )

            self.assertEqual(replay.outcome_class, "model-failure")
            self.assertTrue(replay.score_eligible)
            self.assertFalse(replay.may_supply_model_evidence)

    def test_declared_transport_failure_is_not_score_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def use_transport_failure(fixture: dict[str, object]) -> None:
                fixture["response"].update(
                    {
                        "status": "transport-error",
                        "output": None,
                        "error": "synthetic transport failure",
                    }
                )

            fixture_root = mutated_fixture_root(
                temporary_directory,
                use_transport_failure,
            )
            replay = replay_synthetic_fixture(
                fixture_root,
                "constraint-continuity-pass",
                execution_mode="replay",
            )

            self.assertEqual(replay.outcome_class, "infrastructure-failure")
            self.assertFalse(replay.score_eligible)
            self.assertFalse(replay.may_supply_model_evidence)

    def test_not_run_outcome_remains_not_evaluated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def use_not_run(fixture: dict[str, object]) -> None:
                fixture["response"].update(
                    {"status": "not-run", "output": None, "error": None}
                )

            fixture_root = mutated_fixture_root(temporary_directory, use_not_run)
            replay = replay_synthetic_fixture(
                fixture_root,
                "constraint-continuity-pass",
                execution_mode="replay",
            )

            self.assertEqual(replay.outcome_class, "not-evaluated")
            self.assertFalse(replay.score_eligible)
            self.assertFalse(replay.may_supply_model_evidence)

    def test_unknown_execution_mode_is_refused_before_fixture_matching(self) -> None:
        with self.assertRaisesRegex(
            EvaluationContractError,
            "unknown_execution_mode:preview",
        ):
            replay_synthetic_fixture(
                FIXTURES,
                "constraint-continuity-pass",
                execution_mode="preview",
            )

    def test_unknown_fixture_identifier_is_a_contract_error(self) -> None:
        with self.assertRaisesRegex(
            EvaluationContractError,
            "unknown_fixture:missing",
        ):
            replay_synthetic_fixture(
                FIXTURES,
                "missing",
                execution_mode="replay",
            )

    def test_non_synthetic_model_identity_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            def use_external_model(fixture: dict[str, object]) -> None:
                fixture["request"]["model"] = "provider-model-2026-07"
                fixture["response"]["model"] = "provider-model-2026-07"

            fixture_root = mutated_fixture_root(
                temporary_directory,
                use_external_model,
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                "non_synthetic_model:provider-model-2026-07",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_manifest_schema_version_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory) / "replay"
            shutil.copytree(FIXTURES, fixture_root)
            manifest_path = fixture_root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["schema_version"] = "future-manifest/9"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                "unsupported_manifest_schema:future-manifest/9",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_fixture_must_declare_fresh_synthetic_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = mutated_fixture_root(
                temporary_directory,
                lambda fixture: fixture["provenance"].update(
                    {"captured_from_live": True}
                ),
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                "fixture_is_not_fresh_synthetic:constraint-continuity-pass",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )

    def test_manifest_path_cannot_escape_fixture_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory) / "replay"
            shutil.copytree(FIXTURES, fixture_root)
            manifest_path = fixture_root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["fixtures"][0]["path"] = "../target.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                EvaluationContractError,
                r"unsafe_fixture_path:\.\./target.json",
            ):
                replay_synthetic_fixture(
                    fixture_root,
                    "constraint-continuity-pass",
                    execution_mode="replay",
                )


if __name__ == "__main__":
    unittest.main()
