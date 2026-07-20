"""Live-runner contract for the authorized review-dissent calibration."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caplab.review_dissent.live import (
    LiveReviewContractError,
    _digest,
    assess_attempts,
    harbor_command,
    load_live_manifest,
    prepare_trial,
    record_observation,
)
from caplab.review_dissent.instrument import load_calibration_instrument


ROOT = Path(__file__).parents[1]
STUDY = ROOT / "docs" / "product" / "studies" / "review-dissent-001"
MANIFEST = STUDY / "live-manifest.json"


class ReviewDissentLiveTests(unittest.TestCase):
    def setUp(self) -> None:
        # Load withdrawn bytes only for unit coverage of pure historical
        # accounting/custody helpers; production loading remains fail closed.
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.manifest["_project_root"] = ROOT
        self.manifest["_task_template_path"] = ROOT / self.manifest["harness"]["task_template"]
        self.manifest["_instrument"] = load_calibration_instrument(STUDY)
        self.manifest["_study_root"] = STUDY

    def test_withdrawn_proxy_manifest_cannot_cross_live_boundary(self) -> None:
        with self.assertRaisesRegex(
            LiveReviewContractError, "live_authorization_withdrawn"
        ):
            load_live_manifest(MANIFEST, STUDY)

    def test_historical_proxy_command_shape_remains_reproducible_for_forensics(self) -> None:
        command = harbor_command(
            self.manifest,
            slot_index=0,
            task_path=Path("/tmp/review"),
            jobs_path=Path("/tmp/jobs"),
        )
        self.assertIn("openrouter/openai/gpt-5.6-terra", command)
        self.assertIn("max_turns=8", command)
        self.assertIn('llm_kwargs={"max_tokens":1024}', command)
        self.assertFalse(any(value.startswith("reasoning_effort=") for value in command))
        self.assertEqual(command[command.index("--max-retries") + 1], "0")
        self.assertNotIn("--upload", command)

    def test_accounting_requires_frozen_order_and_infrastructure_only_replacement(self) -> None:
        attempts = [
            {"slot_index": 0, "attempt_kind": "primary", "status": "provider_failure", "completion_tokens": 0, "cost_usd": "0"},
            {"slot_index": 0, "attempt_kind": "replacement", "status": "completed", "completion_tokens": 100, "cost_usd": "0.1"},
            {"slot_index": 1, "attempt_kind": "primary", "status": "invalid", "completion_tokens": 50, "cost_usd": "0.1"},
        ]
        state = assess_attempts(self.manifest, attempts)
        self.assertEqual(state["next_slot_index"], 2)
        self.assertEqual(state["replacement_count"], 1)
        attempts[0]["status"] = "invalid"
        with self.assertRaisesRegex(LiveReviewContractError, "replacement_without_infrastructure_failure"):
            assess_attempts(self.manifest, attempts)

    def test_direct_prepare_cannot_bypass_withdrawn_manifest_loader(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = dict(self.manifest)
            manifest["storage"] = dict(self.manifest["storage"])
            manifest["storage"]["raw_custody_root"] = temporary_directory
            with self.assertRaisesRegex(
                LiveReviewContractError, "live_authorization_withdrawn"
            ):
                prepare_trial(
                    manifest,
                    slot_index=0,
                    attempt_kind="primary",
                    prior_attempts=[],
                )
            self.assertEqual(list(Path(temporary_directory).iterdir()), [])

    def test_zero_token_rejected_provider_request_records_zero_cost(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = dict(self.manifest)
            manifest["storage"] = dict(self.manifest["storage"])
            manifest["storage"]["raw_custody_root"] = temporary_directory
            attempt_root = Path(temporary_directory) / "attempts" / "a01-s01-primary"
            result_root = attempt_root / "harbor" / "trial"
            artifact_root = result_root / "artifacts" / "app"
            artifact_root.mkdir(parents=True)
            (artifact_root / "REVIEW.json").write_text("{}\n", encoding="utf-8")
            launch = {"attempt_number": 1, "slot_index": 0, "attempt_kind": "primary", "manifest_sha256": manifest["manifest_sha256"]}
            launch["launch_sha256"] = _digest(launch)
            completion = {"return_code": 0, "timed_out": False}
            completion["completion_sha256"] = _digest(completion)
            result = {"trial_name": "trial", "agent_result": {"n_output_tokens": 0, "cost_usd": None}, "exception_info": {"exception_type": "APIError"}}
            (attempt_root / "launch.json").write_text(json.dumps(launch), encoding="utf-8")
            (attempt_root / "completion.json").write_text(json.dumps(completion), encoding="utf-8")
            (result_root / "result.json").write_text(json.dumps(result), encoding="utf-8")
            observation = record_observation(manifest, attempt_root=attempt_root, status="provider_failure")
            self.assertEqual(observation["completion_tokens"], 0)
            self.assertEqual(observation["cost_usd"], "0")


if __name__ == "__main__":
    unittest.main()
