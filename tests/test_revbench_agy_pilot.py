from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from caplab.runtime.canonical import canonical_json
from caplab.subject_identity import (
    validate_native_agent_systems,
)
from tools import caplab_revbench_agy_pilot as agy_pilot


ROOT = Path(__file__).resolve().parents[1]


class AgyNativeSubjectTests(unittest.TestCase):
    def test_policy_registers_three_exact_gemini_37_flash_effort_bindings(self) -> None:
        base_policy, policy = agy_pilot.load_pilot_native_policy()
        self.assertEqual(base_policy["policy"], "native-harness-required")
        self.assertEqual(
            policy["base_policy"]["sha256"],
            hashlib.sha256(
                (ROOT / "docs/product/contracts/native-agent-systems.json").read_bytes()
            ).hexdigest(),
        )
        subjects = {
            effort: agy_pilot.native_subject(effort) for effort in agy_pilot.EFFORTS
        }
        validate_native_agent_systems(policy, subjects)
        self.assertEqual(
            [subjects[effort]["tuple_id"] for effort in agy_pilot.EFFORTS],
            [
                "agy-gemini-3-7-flash-low",
                "agy-gemini-3-7-flash-medium",
                "agy-gemini-3-7-flash-high",
            ],
        )

        changed = copy.deepcopy(subjects["high"])
        changed["command"][2] = "gemini-3.7-flash-low"
        with self.assertRaisesRegex(ValueError, "command_tuple_mismatch"):
            validate_native_agent_systems(policy, {"changed": changed})

    def test_review_command_is_plan_sandboxed_and_has_no_slash_mode_conflict(
        self,
    ) -> None:
        subject = agy_pilot.native_subject("medium")
        command = subject["command"]
        self.assertIn("--mode", command)
        self.assertIn("plan", command)
        self.assertIn("--sandbox", command)
        self.assertIn("--json-schema", command)
        self.assertNotIn("--disable-slash-commands", command)
        self.assertEqual(command[-1], "--print")


class AgyResponseTests(unittest.TestCase):
    def test_derives_result_from_agy_structured_output_not_response_text(self) -> None:
        envelope = {
            "status": "SUCCESS",
            "response": (
                '```json\n{"anchors":[],"schema_version":'
                '"caplab-revbench-native-response/1","verdict":"clean"}\n'
                '```\n{"anchors":[],"schema_version":'
                '"caplab-revbench-native-response/1","verdict":"clean"}\n'
            ),
            "structured_output": {
                "anchors": [],
                "schema_version": "caplab-revbench-native-response/1",
                "verdict": "clean",
            },
            "json_schema": agy_pilot.RESPONSE_SCHEMA,
            "conversation_id": "conversation-structured",
            "usage": {"total_tokens": 23},
            "duration_ms": 250,
        }
        derived = agy_pilot.derive_agy_response(canonical_json(envelope) + b"\n")
        self.assertEqual(derived.response["verdict"], "clean")
        self.assertEqual(derived.response["anchors"], [])

    def test_derives_strict_response_and_usage_from_one_agy_envelope(self) -> None:
        envelope = {
            "response": (
                '{"anchors":["/n"],"schema_version":'
                '"caplab-revbench-native-response/1","verdict":"defect"}\n'
            ),
            "structured_output": {
                "schema_version": "caplab-revbench-native-response/1",
                "verdict": "defect",
                "anchors": ["/n"],
            },
            "json_schema": agy_pilot.RESPONSE_SCHEMA,
            "conversation_id": "conversation-1",
            "usage": {"input_tokens": 42, "output_tokens": 7},
            "duration_ms": 1250,
        }
        derived = agy_pilot.derive_agy_response(canonical_json(envelope) + b"\n")
        self.assertEqual(derived.response["verdict"], "defect")
        self.assertEqual(derived.response["anchors"], ["/n"])
        self.assertEqual(derived.conversation_id, "conversation-1")
        self.assertEqual(derived.usage["input_tokens"], 42)

    def test_distinguishes_transport_and_subject_response_failures(self) -> None:
        with self.assertRaisesRegex(agy_pilot.AgyTransportError, "envelope"):
            agy_pilot.derive_agy_response(b"not-json\n")
        invalid = {
            "response": (
                '{"anchors":["/n"],"schema_version":'
                '"caplab-revbench-native-response/1","verdict":"clean"}\n'
            ),
            "structured_output": {
                "schema_version": "caplab-revbench-native-response/1",
                "verdict": "clean",
                "anchors": ["/n"],
            },
            "json_schema": agy_pilot.RESPONSE_SCHEMA,
        }
        with self.assertRaisesRegex(agy_pilot.AgyResponseError, "disagree"):
            agy_pilot.derive_agy_response(canonical_json(invalid) + b"\n")

    def test_refuses_an_agy_envelope_with_a_different_enforced_schema(self) -> None:
        envelope = {
            "status": "SUCCESS",
            "response": "{}\n",
            "structured_output": {},
            "json_schema": {"type": "object"},
        }
        with self.assertRaisesRegex(
            agy_pilot.AgyTransportError, "json_schema_mismatch"
        ):
            agy_pilot.derive_agy_response(canonical_json(envelope) + b"\n")


class AgyPilotScoringTests(unittest.TestCase):
    def test_correction_rederives_attempt_from_retained_structured_output(self) -> None:
        recorded = {
            "effort": "low",
            "tuple_id": "agy-gemini-3-7-flash-low",
            "case_id": "case-a",
            "arm": "control",
            "assignment_index": 0,
            "disposition": "subject-failure",
            "verdict": "invalid",
            "anchors": [],
            "conversation_id": None,
            "usage": {},
            "duration_milliseconds": None,
        }
        envelope = {
            "status": "SUCCESS",
            "response": "```json\n{}\n```\n{}\n",
            "structured_output": {
                "anchors": [],
                "schema_version": "caplab-revbench-native-response/1",
                "verdict": "clean",
            },
            "json_schema": agy_pilot.RESPONSE_SCHEMA,
            "conversation_id": "corrected-conversation",
            "usage": {"total_tokens": 23},
            "duration_ms": 250,
        }
        corrected = agy_pilot.correct_attempt_projection(
            recorded, canonical_json(envelope) + b"\n"
        )
        self.assertEqual(corrected["disposition"], "complete")
        self.assertEqual(corrected["verdict"], "clean")
        self.assertEqual(corrected["conversation_id"], "corrected-conversation")
        self.assertEqual(corrected["usage"], {"total_tokens": 23})
        self.assertEqual(corrected["duration_milliseconds"], 250)

    def test_real_fake_process_is_captured_before_attempt_completion(self) -> None:
        fake_source = (
            """#!/usr/bin/python3
import json
import sys

native_input = json.loads(sys.argv[-1])
pointer = native_input["requirement"]["pointer"]
minimum = native_input["requirement"]["minimum"]
value = native_input["artifact"]
for part in pointer.split("/")[1:]:
    value = value[part]
response = {
    "schema_version": "caplab-revbench-native-response/1",
    "verdict": "clean" if value >= minimum else "defect",
    "anchors": [] if value >= minimum else [pointer],
}
print(json.dumps({
    "status": "SUCCESS",
    "response": json.dumps(response, separators=(",", ":")) + "\\n",
    "structured_output": response,
    "json_schema": json.loads('''%s'''),
    "conversation_id": "fake-conversation",
    "usage": {"total_tokens": 11},
    "duration_seconds": 0.01,
}, separators=(",", ":")))
"""
            % agy_pilot.RESPONSE_SCHEMA_ARGUMENT
        )
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fake_agy = workspace / "agy"
            fake_agy.write_text(fake_source, encoding="utf-8")
            fake_agy.chmod(0o700)
            plan = {
                "plan_id": "test-plan",
                "agy_executable": {
                    "sha256": hashlib.sha256(fake_agy.read_bytes()).hexdigest()
                },
            }
            authorization = {"authorization_id": "test-authorization"}
            attempt = agy_pilot._run_attempt(
                workspace=workspace,
                agy=fake_agy,
                plan=plan,
                authorization=authorization,
                effort="low",
                case=agy_pilot.CASES[0],
                arm="mutant",
                assignment_index=0,
            )
            self.assertEqual(attempt["disposition"], "complete")
            self.assertEqual(attempt["verdict"], "defect")
            self.assertEqual(attempt["anchors"], ["/n"])
            self.assertEqual(attempt["assignment_index"], 0)
            attempt_directory = workspace / "attempts" / "low" / "case-a-0-mutant"
            self.assertTrue((attempt_directory / "intent.json").is_file())
            self.assertTrue((attempt_directory / "stdout.bin").is_file())
            completion = json.loads(
                (attempt_directory / "completion.json").read_bytes()
            )
            self.assertEqual(completion["attempt"], attempt)
            stdout = attempt_directory / "stdout.bin"
            stdout.chmod(0o600)
            stdout.write_bytes(b"tampered")
            with self.assertRaisesRegex(
                agy_pilot.AgyPilotError, "retained_stream_identity_mismatch"
            ):
                agy_pilot._run_attempt(
                    workspace=workspace,
                    agy=fake_agy,
                    plan=plan,
                    authorization=authorization,
                    effort="low",
                    case=agy_pilot.CASES[0],
                    arm="mutant",
                    assignment_index=0,
                )

    def test_process_output_limit_stops_and_preserves_only_bounded_prefix(self) -> None:
        fake_source = """#!/usr/bin/python3
import sys
sys.stdout.write("x" * 1048704)
"""
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fake_agy = workspace / "agy"
            fake_agy.write_text(fake_source, encoding="utf-8")
            fake_agy.chmod(0o700)
            plan = {"plan_id": "test-plan"}
            authorization = {"authorization_id": "test-authorization"}
            attempt = agy_pilot._run_attempt(
                workspace=workspace,
                agy=fake_agy,
                plan=plan,
                authorization=authorization,
                effort="low",
                case=agy_pilot.CASES[0],
                arm="control",
                assignment_index=0,
            )
            self.assertEqual(attempt["disposition"], "infrastructure-failure")
            attempt_directory = workspace / "attempts" / "low" / "case-a-0-control"
            self.assertEqual(
                (attempt_directory / "stdout.bin").stat().st_size,
                agy_pilot.MAX_STREAM_BYTES,
            )
            completion = json.loads(
                (attempt_directory / "completion.json").read_bytes()
            )
            self.assertEqual(completion["termination"], "stdout-limit")
            self.assertFalse(completion["stdout_complete"])

    def test_subject_failure_retains_transport_metadata_for_accounting(self) -> None:
        fake_source = (
            """#!/usr/bin/python3
import json
print(json.dumps({
    "status": "SUCCESS",
    "response": "not one JSON object",
    "structured_output": "not one JSON object",
    "json_schema": json.loads('''%s'''),
    "conversation_id": "failed-response-conversation",
    "usage": {"total_tokens": 23},
    "duration_seconds": 0.25,
}, separators=(",", ":")))
"""
            % agy_pilot.RESPONSE_SCHEMA_ARGUMENT
        )
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fake_agy = workspace / "agy"
            fake_agy.write_text(fake_source, encoding="utf-8")
            fake_agy.chmod(0o700)
            attempt = agy_pilot._run_attempt(
                workspace=workspace,
                agy=fake_agy,
                plan={"plan_id": "test-plan"},
                authorization={"authorization_id": "test-authorization"},
                effort="low",
                case=agy_pilot.CASES[0],
                arm="control",
                assignment_index=0,
            )
            self.assertEqual(attempt["disposition"], "subject-failure")
            self.assertEqual(attempt["conversation_id"], "failed-response-conversation")
            self.assertEqual(attempt["usage"], {"total_tokens": 23})
            self.assertEqual(attempt["duration_milliseconds"], 250)

    def test_scores_each_effort_separately_and_keeps_failures_visible(self) -> None:
        attempts = []
        for effort in agy_pilot.EFFORTS:
            for case in agy_pilot.CASES:
                attempts.extend(
                    [
                        {
                            "effort": effort,
                            "case_id": case["case_id"],
                            "arm": "control",
                            "disposition": "complete",
                            "verdict": "clean",
                            "anchors": [],
                        },
                        {
                            "effort": effort,
                            "case_id": case["case_id"],
                            "arm": "mutant",
                            "disposition": "complete",
                            "verdict": "defect",
                            "anchors": [case["defect_anchor"]],
                        },
                    ]
                )
        scored = agy_pilot.score_attempts(attempts)
        self.assertEqual(set(scored), set(agy_pilot.EFFORTS))
        for effort in agy_pilot.EFFORTS:
            self.assertEqual(scored[effort]["sample_flow"]["planned"], 4)
            self.assertEqual(
                scored[effort]["metrics"]["catch_rate"],
                {"numerator": 1, "denominator": 1},
            )
            self.assertEqual(
                scored[effort]["metrics"]["false_alarm_rate"],
                {"numerator": 0, "denominator": 1},
            )
            self.assertEqual(
                scored[effort]["operational_observations"],
                {
                    "reported_usage_totals": {},
                    "reported_duration_milliseconds_total": 0,
                    "reported_duration_count": 0,
                    "conversation_id_count": 0,
                },
            )

        attempts[0]["disposition"] = "infrastructure-failure"
        attempts[0]["verdict"] = "invalid"
        attempts[0]["anchors"] = []
        rescored = agy_pilot.score_attempts(attempts)
        self.assertEqual(rescored["low"]["sample_flow"]["infrastructure_failures"], 1)
        self.assertEqual(rescored["low"]["sample_flow"]["usable"], 2)
        self.assertEqual(rescored["medium"]["sample_flow"]["usable"], 4)

    def test_one_shot_attempt_custody_refuses_relaunch_after_intent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            attempt = Path(directory) / "attempt"
            identity = {
                "schema_version": "caplab-revbench-agy-attempt-intent/1",
                "attempt_id": "test-attempt",
            }
            agy_pilot.record_attempt_intent(attempt, identity)
            self.assertEqual(
                hashlib.sha256((attempt / "intent.json").read_bytes()).hexdigest(),
                hashlib.sha256(canonical_json(identity) + b"\n").hexdigest(),
            )
            with self.assertRaisesRegex(agy_pilot.AgyPilotError, "already_claimed"):
                agy_pilot.record_attempt_intent(attempt, identity)


if __name__ == "__main__":
    unittest.main()
