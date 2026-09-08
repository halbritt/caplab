"""Synthetic native event evidence, with no model calls or historical captures."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from caplab.review_dissent.native import (
    assess_native_review_model, build_native_review_capture,
    load_native_review_instrument, render_native_review_cell,
)

MODEL = "claude-fable-5"
SUBJECT = {"model_id": MODEL, "native_harness_id": "claude-code"}


def events():
    return [{"type": "system", "subtype": "init", "model": MODEL},
            {"type": "assistant", "message": {"model": MODEL, "content": []}},
            {"type": "result", "subtype": "success", "is_error": False}]


def raw(trace):
    return ("\n".join(json.dumps(e, ensure_ascii=False) for e in trace) + "\n").encode()


def partial(event):
    return {"type": "stream_event", "event": event}


class NativeStreamIdentityTests(unittest.TestCase):
    def assess(self, trace):
        before = copy.deepcopy(trace)
        content = raw(trace)
        result = assess_native_review_model(SUBJECT, content)
        self.assertEqual(trace, before)
        self.assertEqual(result["native_stdout_sha256"], hashlib.sha256(content).hexdigest())
        return result

    def test_partial_model_mismatch_is_not_erased_by_completed_message(self):
        trace = events()
        trace.insert(1, partial({"type": "message_start", "message": {"model": "another-model"}}))
        result = self.assess(trace)
        self.assertEqual(result["status"], "model-mismatch")
        self.assertEqual(result["stream_models"], [{"line": 2, "model": "another-model"}])
        self.assertEqual(result["response_models"], [{"line": 3, "model": MODEL}])

    def test_matching_partial_model_is_separate_from_completed_response(self):
        trace = events()
        trace[1:1] = [partial({"type": "message_start", "message": {"model": MODEL}}),
                      partial({"type": "content_block_delta", "delta": {"type": "text_delta", "text": "résumé\u2028line"}}),
                      partial({"type": "message_stop"})]
        result = self.assess(trace)
        self.assertEqual(result["status"], "native-model-match")
        self.assertEqual(result["stream_models"], [{"line": 2, "model": MODEL}])
        self.assertEqual(len(result["response_models"]), 1)
        del trace[-2]
        self.assertEqual(self.assess(trace)["status"], "model-unverified")

    def test_missing_or_malformed_partial_identity_prevents_match(self):
        partials = [None, [], {}, {"type": "content_block_start"},
                    {"type": "content_block_start", "content_block": []},
                    {"type": "message_start"},
                    {"type": "message_start", "message": []},
                    {"type": "message_start", "message": {"model": None}},
                    {"type": "message_start", "message": {"model": " "}},
                    {"type": "message_start", "message": {"model": 1}}]
        for event in partials:
            with self.subTest(event=event):
                trace = events(); trace.insert(1, partial(event))
                self.assertEqual(self.assess(trace)["status"], "model-unverified")

    def test_fallback_content_and_usage_markers_all_withhold_attribution(self):
        block = {"type": "fallback", "from": {"model": MODEL}, "to": {"model": "another-model"}}
        iteration = {"type": "fallback_message", "model": "another-model"}
        traces = []
        trace = events(); trace[1]["message"]["content"] = [block]; traces.append(trace)
        trace = events(); trace[1]["message"]["usage"] = {"iterations": [iteration]}; traces.append(trace)
        trace = events(); trace.insert(1, partial({"type": "content_block_start", "index": 0, "content_block": block})); traces.append(trace)
        trace = events(); trace.insert(1, partial({"type": "message_delta", "usage": {"iterations": [iteration]}})); traces.append(trace)
        trace = events(); trace.insert(1, partial({"type": "message_start", "message": {"model": MODEL, "usage": {"iterations": [iteration]}}})); traces.append(trace)
        trace = events(); trace[-1]["usage"] = {"iterations": [iteration]}; traces.append(trace)
        for trace in traces:
            with self.subTest(trace=trace):
                result = self.assess(trace)
                self.assertEqual(result["status"], "model-mismatch")
                self.assertEqual(result["fallbacks"][0]["fallback_model"], "another-model")
                self.assertIn("source", result["fallbacks"][0])

    def test_fallback_marker_without_details_still_blocks_and_mismatch_dominates_missing(self):
        trace = events()
        trace.insert(1, partial({"type": "message_start", "message": {}}))
        trace[2]["message"]["content"] = [{"type": "fallback", "from": [], "to": None}]
        result = self.assess(trace)
        self.assertEqual(result["status"], "model-mismatch")
        self.assertIsNone(result["fallbacks"][0]["fallback_model"])

    def test_deltas_tool_input_and_auxiliary_usage_are_not_recursively_interpreted(self):
        trace = events()
        trace[1]["message"]["content"] = [{"type": "tool_use", "name": "Bash", "input": {"type": "fallback", "model": "another-model"}}]
        trace[-1]["modelUsage"] = {"auxiliary-model": {}}
        trace.insert(1, partial({"type": "content_block_delta", "delta": {"type": "text_delta", "text": '"type":"fallback"'}}))
        trace.insert(2, partial({"type": "future_event", "model": "another-model"}))
        result = self.assess(trace)
        self.assertEqual(result["status"], "native-model-match")
        self.assertEqual(result["fallbacks"], [])
        self.assertNotIn("stream_models", result)

    def test_codex_cannot_be_attested_by_claude_partial_fields(self):
        trace = events(); trace.insert(1, partial({"type": "message_start", "message": {"model": MODEL}}))
        result = assess_native_review_model(dict(SUBJECT, native_harness_id="codex-cli"), raw(trace))
        self.assertEqual(result["status"], "model-unverified")
        self.assertNotIn("stream_models", result)

    def test_partial_mismatch_withholds_score_and_preserves_assignment(self):
        instrument = load_native_review_instrument(Path(__file__).parents[1] / "docs/product/studies/review-dissent-001/native-instrument.json")
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory) / "task"
            render_native_review_cell(instrument, "r03", task)
            (task / "REVIEW.json").write_text(json.dumps({"verdict": "needs_revision", "findings": [], "summary": "Synthetic review."}))
            def capture(trace):
                return build_native_review_capture(instrument, cell_id="r03", subject_id="fable", task_root=task,
                    native_jsonl=raw(trace), status="completed", observation_sha256="a"*64, campaign_manifest_sha256="b"*64)
            baseline = capture(events())
            trace = events(); trace.insert(1, partial({"type": "message_start", "message": {"model": "another-model"}}))
            result = capture(trace)
            self.assertIsNotNone(baseline["mechanical"]["score"])
            self.assertIsNone(result["mechanical"]["score"])
            self.assertEqual(result["outcome"], "identity-unavailable")
            self.assertEqual(result["status"], baseline["status"])
            self.assertEqual(result["subject_seal"], baseline["subject_seal"])


if __name__ == "__main__":
    unittest.main()
