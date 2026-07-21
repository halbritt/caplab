import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from caplab.review_dissent.training_experiment import (
    TrainingExperimentContractError,
    load_training_execution,
    load_training_experiment,
)


ROOT = Path(__file__).resolve().parents[1]
TRAINING_ROOT = ROOT / "docs/product/training/caplab-review-dissent-local-qwen-r1"
MANIFEST = TRAINING_ROOT / "training-experiment.json"
EXECUTION = TRAINING_ROOT / "training-execution.json"
RESULT = TRAINING_ROOT / "training-result.json"
RETRY_ROOT = ROOT / "docs/product/training/caplab-review-dissent-local-qwen-r2"
RETRY_MANIFEST = RETRY_ROOT / "training-experiment.json"
RETRY_EXECUTION = RETRY_ROOT / "training-execution.json"
RETRY_EXECUTION_Q2 = RETRY_ROOT / "training-execution-q2.json"
RETRY_EXECUTION_Q3 = RETRY_ROOT / "training-execution-q3.json"
RETRY_EXECUTION_Q4 = RETRY_ROOT / "training-execution-q4.json"
RETRY_EXECUTION_Q5 = RETRY_ROOT / "training-execution-q5.json"


class TrainingExperimentTests(unittest.TestCase):
    def test_committed_experiment_is_zero_authority_and_native_harness_bound(self) -> None:
        experiment = load_training_experiment(MANIFEST, ROOT)
        self.assertEqual(experiment["base_checkpoint"]["repository"], "Qwen/Qwen3.6-27B")
        self.assertEqual(experiment["method"]["name"], "qlora-sft")
        self.assertEqual(experiment["method"]["optimizer_steps_max"], 12)
        self.assertEqual(experiment["evaluation"]["heldout_cells"], 8)
        self.assertEqual(experiment["authorization"]["training_attempts"], 0)

    def test_loader_does_not_open_heldout_content(self) -> None:
        original_open = Path.open

        def guarded_open(path: Path, *args, **kwargs):
            if path.name == "heldout.json":
                raise AssertionError("preregistration loader opened heldout content")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded_open):
            load_training_experiment(MANIFEST, ROOT)

    def test_retry_preregistration_preserves_science_and_adds_host_qualification(self) -> None:
        original = load_training_experiment(MANIFEST, ROOT)
        retry = load_training_experiment(RETRY_MANIFEST, ROOT)

        self.assertEqual(retry["experiment_id"], "caplab-review-dissent-qwen27b-qlora-r2")
        self.assertEqual(retry["authority"], "adr-0053")
        for field in ("base_checkpoint", "training_data", "method", "toolchain", "evaluation", "success"):
            self.assertEqual(retry[field], original[field])
        self.assertEqual(retry["authorization"], original["authorization"])
        self.assertEqual(
            retry["predecessor"],
            {
                "experiment_id": "caplab-review-dissent-qwen27b-qlora-r1",
                "result_sha256": "f65262006596a2553a02e57f06c442002e3a993b5117879edde43904b17ae705",
                "disposition": "infrastructure-failed-training-attempt-consumed",
            },
        )
        self.assertEqual(retry["host_qualification"]["no_update_seconds"], 60)
        self.assertEqual(retry["host_qualification"]["distinct_fleet_heartbeats_min"], 4)
        self.assertEqual(retry["host_qualification"]["remote_pulse_ttl_seconds"], 45)
        self.assertEqual(
            retry["host_qualification"]["process_containment"],
            "windows-job-object-kill-on-close",
        )

    def test_drift_and_execution_authority_fail_closed(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relative_manifest = root / "manifest.json"
            for binding in (
                manifest["training_data"],
                manifest["evaluation"],
            ):
                path_key = "path" if "path" in binding else "general_controls_path"
                source = ROOT / binding[path_key]
                target = root / binding[path_key]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())

            manifest["authorization"]["training_attempts"] = 1
            relative_manifest.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                TrainingExperimentContractError, "execution_authority_not_zero"
            ):
                load_training_experiment(relative_manifest, root)

            manifest["authorization"]["training_attempts"] = 0
            manifest["training_data"]["file_sha256"] = "0" * 64
            relative_manifest.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                TrainingExperimentContractError, "training_data_sha256_mismatch"
            ):
                load_training_experiment(relative_manifest, root)

    def test_execution_authority_binds_sources_host_and_effect_ceiling(self) -> None:
        execution = load_training_execution(
            EXECUTION,
            ROOT,
            now=datetime(2026, 7, 20, 23, 45, tzinfo=UTC),
        )
        self.assertEqual(execution["host"]["name"], "peecee")
        self.assertEqual(execution["host"]["gpu_fleet_model"], "marker")
        self.assertEqual(execution["permitted_effects"]["training_attempts"], 1)
        self.assertEqual(execution["permitted_effects"]["paid_usd"], "0")

    def test_execution_loader_does_not_open_heldout_content(self) -> None:
        original_open = Path.open

        def guarded_open(path: Path, *args, **kwargs):
            if path.name == "heldout.json":
                raise AssertionError("execution loader opened heldout content")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded_open):
            load_training_execution(
                EXECUTION,
                ROOT,
                now=datetime(2026, 7, 20, 23, 45, tzinfo=UTC),
            )

    def test_retry_execution_authority_binds_qualification_and_containment(self) -> None:
        execution = load_training_execution(
            RETRY_EXECUTION_Q5,
            ROOT,
            now=datetime(2026, 7, 21, 4, 0, tzinfo=UTC),
        )
        self.assertEqual(execution["schema"], "caplab.training.execution-authorization/v6")
        self.assertEqual(execution["authority"], "adr-0058")
        self.assertEqual(execution["experiment_id"], "caplab-review-dissent-qwen27b-qlora-r2")
        self.assertEqual(execution["permitted_effects"]["host_qualification_runs"], 1)
        self.assertEqual(execution["permitted_effects"]["training_attempts"], 1)
        self.assertEqual(execution["containment"]["remote_pulse_ttl_seconds"], 45)
        self.assertEqual(
            execution["containment"]["windows_process_tree"],
            "job-object-kill-on-close",
        )
        self.assertTrue(execution["containment"]["training_requires_qualification_acceptance"])
        self.assertFalse(execution["permitted_effects"]["install_packages"])
        self.assertFalse(execution["permitted_effects"]["download_checkpoint"])
        self.assertEqual(execution["permitted_effects"]["gpu_fleet_leases"], 4)
        self.assertEqual(
            execution["capacity_coordination"]["temporary_resident_unload"],
            "qwen3-vl:8b",
        )
        self.assertEqual(
            execution["fleet_status_correction"]["accepted_active_lease_statuses"],
            ["routable", "probationary"],
        )
        self.assertEqual(
            execution["launch_correction"],
            {
                "powershell_execution_policy": "Bypass",
                "digest_implementation": "System.Security.Cryptography.SHA256",
                "scope": "child-process-only",
                "host_policy_mutation": False,
            },
        )

    def test_failed_result_cannot_be_mistaken_for_a_tuned_candidate(self) -> None:
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            result["status"],
            "infrastructure-failed-training-attempt-consumed",
        )
        self.assertEqual(result["training"]["attempts_consumed"], 1)
        self.assertFalse(result["training"]["final_adapter_sealed"])
        self.assertEqual(
            result["training"]["partial_checkpoint"]["status"],
            "partial-unsealed-not-a-candidate",
        )
        self.assertEqual(result["evaluation"]["heldout_status"], "sealed-unopened")
        self.assertEqual(result["evaluation"]["heldout_calls"], 0)
        self.assertEqual(result["evaluation"]["native_harness_calls"], 0)


if __name__ == "__main__":
    unittest.main()
