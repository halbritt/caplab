"""Configured-subject attribution must stop at an explicit native reroute."""

import copy
from hashlib import sha256
import json
import unittest

from caplab.artifact_rater import CalibrationError, derive_artifact_judgment
from caplab.codex_events import final_codex_message, require_completed_codex_turn
from caplab.ladder_subject import classify_subject_attempt
from caplab.review_dissent.native import assess_native_review_model
from caplab.revbench.codex import CodexJSONLTransportError, derive_codex_response
import test_codex_final_message_link as final_fixtures
import test_review_dissent_native as review_fixtures


MARKER = {"type": "item.completed", "item": {
    "type": "error", "id": "warning",
    "message": "model rerouted: gpt-5.6-terra -> another-model (HighRisk)",
}}
SUBJECT = {"model_id": "gpt-5.6-terra", "native_harness_id": "codex"}
RESPONSE = {"schema_version": "caplab-revbench-native-response/1",
            "verdict": "clean", "anchors": []}


def stream(text, markers=()):
    events = [{"type": "thread.started", "thread_id": "synthetic-root"},
              {"type": "turn.started"}, *markers,
              {"type": "item.completed", "item": {
                  "type": "agent_message", "id": "answer", "text": text}},
              {"type": "turn.completed"}]
    return ("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n").encode()


class CodexModelRerouteTests(unittest.TestCase):
    def test_reroute_blocks_matching_artifact_judgment(self):
        text = '{"C1": true}'
        with self.assertRaisesRegex(CalibrationError, "model reroute"):
            derive_artifact_judgment(stream(text, [MARKER]), text.encode(), ["C1"])

    def test_revbench_reroute_is_transport_failure_even_with_invalid_response(self):
        for text in (json.dumps(RESPONSE), "invalid response"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(CodexJSONLTransportError, "codex_jsonl_model_reroute"):
                    derive_codex_response(stream(text, [MARKER]))

    def test_reroute_is_infrastructure_even_with_a_passing_pin_and_task_write(self):
        result = classify_subject_attempt(stream("answer", [MARKER]), 0, ["changed.py"], pin_ok=True)
        self.assertEqual(result, ("infrastructure", "native event stream reports model reroute"))

    def test_reroute_preserves_completed_turn_and_final_message_observations(self):
        text = "café\u2028answer\n"
        content = stream(text, [MARKER])
        self.assertEqual(require_completed_codex_turn(content), "synthetic-root")
        self.assertEqual(final_codex_message(content).text.encode(), text.encode())

    def test_review_identity_retains_each_raw_marker_without_parsing_model_names(self):
        second = copy.deepcopy(MARKER)
        second["item"].pop("id")
        second["item"]["message"] = "model rerouted: "
        content = stream("answer", [MARKER, second])
        result = assess_native_review_model(SUBJECT, content)
        self.assertEqual(result["status"], "model-mismatch")
        self.assertEqual(result["reason"], "native-model-reroute")
        self.assertEqual(result["configured_model_id"], SUBJECT["model_id"])
        self.assertEqual(result["native_stdout_sha256"], sha256(content).hexdigest())
        self.assertEqual(result["reroutes"], [
            {"line": 3, "item_id": "warning", "message": MARKER["item"]["message"],
             "source": "item.completed.error"},
            {"line": 4, "item_id": None, "message": "model rerouted: ",
             "source": "item.completed.error"},
        ])
        self.assertEqual(result["response_models"], [])

    def test_marker_without_item_id_still_blocks_attribution(self):
        marker = copy.deepcopy(MARKER); marker["item"].pop("id")
        with self.assertRaisesRegex(CodexJSONLTransportError, "model_reroute"):
            derive_codex_response(stream(json.dumps(RESPONSE), [marker]))

    def test_generic_warnings_and_quoted_markers_preserve_nonreroute_behavior(self):
        variants = [
            {"type": "item.completed", "item": {"type": "error", "message": "ordinary warning"}},
            {"type": "item.completed", "item": {"type": "error", "message": None}},
            {"type": "item.completed", "item": {"type": "error", "message": "quoted model rerouted: a -> b"}},
            {"type": "item.started", "item": MARKER["item"]},
            {"type": "item.completed", "item": {"type": "command_execution", "message": MARKER["item"]["message"]}},
            {"type": "item.completed", "item": {"type": "agent_message", "id": "quote", "text": MARKER["item"]["message"]}},
        ]
        for marker in variants:
            with self.subTest(marker=marker):
                text = '{"C1": true}'
                content = stream(text, [marker])
                self.assertEqual(derive_artifact_judgment(content, text.encode(), ["C1"])["judgment"], {"C1": True})
                self.assertEqual(derive_codex_response(stream(json.dumps(RESPONSE), [marker])).response, RESPONSE)
                self.assertEqual(classify_subject_attempt(content, 0, ["changed.py"], pin_ok=True), ("behavioural-attempt", None))
                identity = assess_native_review_model(SUBJECT, content)
                self.assertEqual(identity["status"], "model-unverified")
                self.assertNotIn("reroutes", identity)

    def test_review_capture_withholds_score_and_preserves_assignment_and_execution(self):
        fixture = review_fixtures.NativeReviewDissentTests(); fixture.setUp()
        content = stream("answer", [MARKER])
        baseline, _ = fixture.capture_stream(stream("answer"), subject="gpt")
        capture, _ = fixture.capture_stream(content, subject="gpt")
        self.assertEqual(capture["model_identity"]["status"], "model-mismatch")
        self.assertEqual(capture["outcome"], "identity-unavailable")
        self.assertIsNone(capture["mechanical"]["score"])
        self.assertEqual(capture["subject_seal"], baseline["subject_seal"])
        self.assertEqual(capture["status"], "completed")

    def test_claude_assessment_does_not_interpret_codex_envelopes(self):
        fixture = review_fixtures.NativeReviewDissentTests(); fixture.setUp()
        baseline, _ = fixture.capture_stream(fixture.model_stream())
        events = fixture.model_stream(); events.insert(1, MARKER)
        capture, _ = fixture.capture_stream(events)
        self.assertEqual(capture["model_identity"]["status"], baseline["model_identity"]["status"])
        self.assertNotIn("reroutes", capture["model_identity"])

    def test_final_file_agreement_does_not_erase_reroute_or_attest_execution(self):
        fixture = final_fixtures.CodexFinalMessageLinkTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        events = final_fixtures.events(); events.insert(2, MARKER)
        fixture.build(stdout=final_fixtures.jsonl(events))
        report = fixture.link()
        self.assertTrue(report["final_message_agrees"])
        self.assertIs(report["root_link"]["executed_invocation_bound"], False)
        self.assertIsNone(report["root_link"]["native_capture_complete"])
        self.assertEqual(assess_native_review_model(SUBJECT, final_fixtures.jsonl(events))["status"], "model-mismatch")


if __name__ == "__main__":
    unittest.main()
