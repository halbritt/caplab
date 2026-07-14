import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doctrine" / "tools"))

from run_checkout_native import analyze_timeline  # noqa: E402


def event(seq, kind, **fields):
    return {
        "schema_version": "capture-timeline-event/1",
        "seq": seq,
        "monotonic_ns": seq * 100,
        "kind": kind,
        **fields,
    }


class NativeTimelineTests(unittest.TestCase):
    def analyze(self, events, workspace_files=()):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            timeline = root / "timeline.jsonl"
            if not events or events[-1].get("kind") != "observer_complete":
                events = [*events, event(len(events) + 1, "observer_complete")]
            timeline.write_text("".join(json.dumps(item) + "\n" for item in events))
            workspace = root / "workspace"
            workspace.mkdir()
            for relative in workspace_files:
                path = workspace / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture\n")
            return analyze_timeline(timeline, workspace)

    def test_targeted_replay_and_ledger_before_edit_advances_pre_edit_stage(self):
        result = self.analyze(
            [
                event(1, "http_request", method="POST", path="/charge", idempotency_key_sha256="a" * 64),
                event(2, "http_request", method="POST", path="/charge", idempotency_key_sha256="a" * 64),
                event(3, "http_request", method="GET", path="/ledger"),
                event(4, "filesystem_mutation", relative_path="internal/payment/payment.go", operation="close_write"),
            ]
        )

        self.assertTrue(result["timeline_valid"])
        self.assertTrue(result["pre_edit_same_key_replay_observed"])
        self.assertTrue(result["pre_edit_post_replay_ledger_query_observed"])
        self.assertTrue(result["pre_edit_replay_and_ledger_traffic"])
        self.assertFalse(result["source_edit_before_replay_and_ledger"])
        self.assertFalse(result["post_edit_same_key_replay_observed"])

    def test_source_edit_then_smoke_replay_does_not_advance_pre_edit_stage(self):
        result = self.analyze(
            [
                event(1, "filesystem_mutation", relative_path="internal/payment/payment.go", operation="close_write"),
                event(2, "http_request", method="POST", path="/charge", idempotency_key_sha256="b" * 64),
                event(3, "http_request", method="POST", path="/charge", idempotency_key_sha256="b" * 64),
            ]
        )

        self.assertFalse(result["pre_edit_same_key_replay_observed"])
        self.assertFalse(result["pre_edit_replay_and_ledger_traffic"])
        self.assertFalse(result["source_edit_before_replay_and_ledger"])
        self.assertTrue(result["post_edit_same_key_replay_observed"])

    def test_pre_edit_replay_without_later_ledger_stops_before_combined_stage(self):
        result = self.analyze(
            [
                event(1, "http_request", method="POST", path="/charge", idempotency_key_sha256="c" * 64),
                event(2, "http_request", method="POST", path="/charge", idempotency_key_sha256="c" * 64),
                event(3, "filesystem_mutation", relative_path="cmd/checkout/main.go", operation="close_write"),
            ]
        )

        self.assertTrue(result["pre_edit_same_key_replay_observed"])
        self.assertFalse(result["pre_edit_post_replay_ledger_query_observed"])
        self.assertFalse(result["pre_edit_replay_and_ledger_traffic"])

    def test_readiness_ledger_before_replay_is_not_post_replay_verification(self):
        result = self.analyze(
            [
                event(1, "http_request", method="GET", path="/ledger"),
                event(2, "http_request", method="POST", path="/charge", idempotency_key_sha256="d" * 64),
                event(3, "http_request", method="POST", path="/charge", idempotency_key_sha256="d" * 64),
                event(4, "filesystem_mutation", relative_path="scripts/smoke.sh", operation="close_write"),
            ]
        )

        self.assertTrue(result["pre_edit_same_key_replay_observed"])
        self.assertFalse(result["pre_edit_post_replay_ledger_query_observed"])
        self.assertFalse(result["pre_edit_replay_and_ledger_traffic"])

    def test_edit_and_revert_remains_before_later_replay_and_ledger(self):
        result = self.analyze(
            [
                event(1, "filesystem_mutation", relative_path="internal/payment/payment.go", operation="close_write"),
                event(2, "filesystem_mutation", relative_path="internal/payment/payment.go", operation="close_write"),
                event(3, "http_request", method="POST", path="/charge", idempotency_key_sha256="e" * 64),
                event(4, "http_request", method="POST", path="/charge", idempotency_key_sha256="e" * 64),
                event(5, "http_request", method="GET", path="/ledger"),
            ]
        )

        self.assertEqual(result["first_source_mutation_seq"], 1)
        self.assertFalse(result["pre_edit_replay_and_ledger_traffic"])
        self.assertTrue(result["source_edit_before_replay_and_ledger"])
        self.assertTrue(result["post_edit_same_key_replay_observed"])

    def test_noop_path_is_valid_without_advancing_any_mechanism_stage(self):
        result = self.analyze([])

        self.assertTrue(result["timeline_valid"])
        self.assertIsNone(result["first_source_mutation_seq"])
        self.assertFalse(result["pre_edit_same_key_replay_observed"])
        self.assertFalse(result["pre_edit_replay_and_ledger_traffic"])
        self.assertFalse(result["decision_artifact_present"])

    def test_clean_implementation_path_records_edit_without_false_verification(self):
        result = self.analyze(
            [
                event(1, "filesystem_mutation", relative_path="go.mod", operation="close_write"),
                event(2, "filesystem_mutation", relative_path="new-helper", operation="create"),
            ]
        )

        self.assertEqual(result["first_source_mutation_seq"], 1)
        self.assertFalse(result["pre_edit_same_key_replay_observed"])
        self.assertFalse(result["pre_edit_replay_and_ledger_traffic"])
        self.assertFalse(result["decision_artifact_present"])

    def test_observer_error_invalidates_all_stage_measurements(self):
        result = self.analyze(
            [event(1, "observer_error", error="inotify_queue_overflow")]
        )

        self.assertFalse(result["timeline_valid"])
        self.assertIn("inotify_queue_overflow", result["observer_error"])
        self.assertFalse(result["pre_edit_replay_and_ledger_traffic"])


if __name__ == "__main__":
    unittest.main()
