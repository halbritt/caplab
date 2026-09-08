"""Tests for native subject continuation of the advisory ladder."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from caplab.ladder_subject import (
    NativeSubjectError,
    classify_subject_attempt,
    subject_slot,
    validate_ladder_subject,
)


ROOT = Path(__file__).resolve().parents[1]


class LadderSubjectTests(unittest.TestCase):
    def test_all_ladder_tuples_validate_as_native_codex_systems(self) -> None:
        policy = ROOT / "docs/product/contracts/native-agent-systems.json"
        tuple_policy = (
            ROOT
            / "docs/product/studies/advisory-selection-001/native-agent-systems.json"
        )
        for model in ("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"):
            for effort in ("low", "medium", "high", "xhigh"):
                command = [
                    "codex",
                    "exec",
                    "-m",
                    model,
                    "-c",
                    f"model_reasoning_effort={effort}",
                ]
                validate_ladder_subject(
                    policy,
                    tuple_policy,
                    model,
                    effort,
                    command,
                    observed_harness_version="codex-cli 0.146.0",
                )

    def test_ladder_subject_rejects_harness_version_drift(self) -> None:
        with self.assertRaisesRegex(
            NativeSubjectError, "native_harness_version_mismatch"
        ):
            validate_ladder_subject(
                ROOT / "docs/product/contracts/native-agent-systems.json",
                ROOT
                / "docs/product/studies/advisory-selection-001/native-agent-systems.json",
                "gpt-5.6-luna",
                "low",
                [
                    "codex",
                    "exec",
                    "-m",
                    "gpt-5.6-luna",
                    "-c",
                    "model_reasoning_effort=low",
                ],
                observed_harness_version="codex-cli 0.147.0",
            )

    def test_ladder_subject_rejects_a_different_admitted_command_profile(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            NativeSubjectError, "native_ladder_command_mismatch"
        ):
            validate_ladder_subject(
                ROOT / "docs/product/contracts/native-agent-systems.json",
                ROOT
                / "docs/product/studies/advisory-selection-001/native-agent-systems.json",
                "gpt-5.6-luna",
                "low",
                [
                    "codex",
                    "exec",
                    "-m",
                    "gpt-5.6-luna",
                    "-c",
                    "model_reasoning_effort=low",
                    "--sandbox",
                    "workspace-write",
                    "--skip-git-repo-check",
                    "--ephemeral",
                    "--json",
                ],
                observed_harness_version="codex-cli 0.146.0",
            )

    def test_completed_ladder_launcher_refuses_before_custody_or_model_call(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign = root / "campaign"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/caplab-ladder-subject.py"),
                    "--campaign-root",
                    str(campaign),
                    "--scenario-root",
                    str(root / "scenarios"),
                    "--policy",
                    str(ROOT / "docs/product/contracts/native-agent-systems.json"),
                    "--tuple-policy",
                    str(
                        ROOT
                        / "docs/product/studies/advisory-selection-001/native-agent-systems.json"
                    ),
                    "--scenario",
                    "closed-campaign-probe",
                    "--arm",
                    "none",
                    "--model",
                    "gpt-5.6-luna",
                    "--effort",
                    "low",
                    "--trial",
                    "1",
                ],
                capture_output=True,
                check=False,
                text=True,
                timeout=30,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertIn("native_ladder_execution_closed", completed.stderr)
            self.assertFalse(campaign.exists())

    def test_unknown_effort_fails_before_an_attempt_path_is_needed(self) -> None:
        with self.assertRaises(NativeSubjectError):
            validate_ladder_subject(
                ROOT / "docs/product/contracts/native-agent-systems.json",
                ROOT
                / "docs/product/studies/advisory-selection-001/native-agent-systems.json",
                "gpt-5.6-luna",
                "max",
                [
                    "codex",
                    "exec",
                    "-m",
                    "gpt-5.6-luna",
                    "-c",
                    "model_reasoning_effort=max",
                ],
            )

    def test_replacement_slots_preserve_the_failed_logical_trial(self) -> None:
        self.assertEqual(
            subject_slot("02-example", "none", "gpt-5.6-terra", "low", 1, 1),
            "02-example--none--terra-low--t1r1",
        )
        self.assertEqual(
            subject_slot("02-example", "injection", "gpt-5.6-sol", "high", 3),
            "02-example--injection--sol-high--t3",
        )

    def test_disposition_requires_completion_success_and_attestation(self) -> None:
        completed = "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "abc"}),
                json.dumps({"type": "turn.started"}),
                json.dumps({"type": "turn.completed", "usage": {}}),
            ]
        ) + "\n"
        self.assertEqual(
            classify_subject_attempt(completed, 0, ["a.py"], pin_ok=True),
            ("behavioural-attempt", None),
        )
        self.assertEqual(
            classify_subject_attempt(completed, 0, [], pin_ok=True),
            ("behavioural-no-attempt", None),
        )
        disposition, reason = classify_subject_attempt(
            '{"type":"turn.failed","error":{"message":"capacity"}}',
            1,
            [],
            pin_ok=True,
        )
        self.assertEqual(disposition, "infrastructure")
        self.assertIn("turn.failed", reason)
        self.assertEqual(
            classify_subject_attempt(completed, 0, ["a.py"], pin_ok=False),
            ("infrastructure", "native tuple attestation mismatch"),
        )

    def test_byte_events_require_utf8_and_object_records(self) -> None:
        completed = (b'{"type":"thread.started","thread_id":"abc"}\n'
                     b'{"type":"turn.started"}\n{"type":"turn.completed"}\n')
        self.assertEqual(
            classify_subject_attempt(completed, 0, ["a.py"], pin_ok=True),
            ("behavioural-attempt", None),
        )
        for invalid in (completed + b"\xe2", completed + b"null\n", completed + b"[]\n"):
            with self.subTest(invalid=invalid):
                disposition, reason = classify_subject_attempt(invalid, 0, ["a.py"], pin_ok=True)
                self.assertEqual(disposition, "infrastructure")
                self.assertIn("event stream", reason)

    def test_completion_does_not_hide_later_activity_or_malformed_records(self) -> None:
        completed = ('{"type":"thread.started","thread_id":"abc"}\n'
                     '{"type":"turn.started"}\n{"type":"turn.completed"}\n')
        for invalid in (completed + '{"type":"turn.started"}\n', completed + '{"type":',
                        completed + '{"type":"thread.started","thread_id":"other"}\n'):
            with self.subTest(invalid=invalid):
                disposition, _ = classify_subject_attempt(invalid, 0, ["a.py"], pin_ok=True)
                self.assertEqual(disposition, "infrastructure")


if __name__ == "__main__":
    unittest.main()
