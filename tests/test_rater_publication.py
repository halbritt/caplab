"""Publication failure tests over disposable native-rater fixtures."""

import hashlib
import json
import unittest
from unittest.mock import patch

from caplab.artifact_rater import CalibrationError
import test_native_capture_custody as capture_fixtures

ANSWER, EVENTS, RATER = capture_fixtures.ANSWER, capture_fixtures.EVENTS, capture_fixtures.RATER


class RaterPublicationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = capture_fixtures.NativeCaptureCustodyTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.slot = self.root / "out/scores/slot-1"
        self.accepted = self.slot / "accepted.json"

    def fail_write(self, filename):
        write = RATER._write_new_json

        def failing(path, value):
            if path.name == filename:
                raise OSError("fixture write failure")
            return write(path, value)

        return patch.object(RATER, "_write_new_json", side_effect=failing)

    def retry(self):
        return RATER._score_entry(
            self.fixture.entry,
            {"campaign_root": str(self.root / "campaign"),
             "scenario_root": str(self.root / "scenarios")},
            self.root / "out", "gpt-5.6-luna", "low", 10,
        )

    def legacy_attempt(self):
        attempt = self.slot / "attempt-001"
        attempt.mkdir(parents=True)
        (attempt / "record.json").write_text(json.dumps({
            "schema_version": "caplab-artifact-rater-attempt/1",
            "return_code": 0, "model": "gpt-5.6-luna", "effort": "low",
            "diff_sha256": self.fixture.entry["diff_sha256"],
            "prompt_sha256": "a" * 64, "accepted": False,
        }))
        (attempt / "events.jsonl").write_text(EVENTS)
        (attempt / "last-message.txt").write_text(ANSWER)
        return attempt

    def test_failed_publication_keeps_validation_without_claiming_acceptance(self):
        with self.fail_write("accepted.json"):
            self.assertFalse(self.fixture.score()[1])
        record = json.loads((self.slot / "attempt-001/record.json").read_text())
        self.assertFalse(record.get("accepted", False))
        self.assertTrue(record["validated"])
        self.assertFalse(self.accepted.exists())
        self.assertEqual(record["judgment_candidate"]["judgment"], {"C1": True, "SCOPE": True})

    def test_failed_record_write_cannot_leave_a_published_judgment(self):
        with self.fail_write("record.json"):
            with self.assertRaises(OSError):
                self.fixture.score()
        self.assertFalse(self.accepted.exists())

    def test_legacy_recovery_receipt_does_not_block_publication_retry(self):
        attempt = self.legacy_attempt()
        with patch.object(RATER, "_find_rollout", return_value=self.fixture.source):
            with self.fail_write("accepted.json"):
                with self.assertRaises(OSError):
                    RATER._recover_completed_attempt(
                        attempt, self.accepted, self.fixture.entry, "gpt-5.6-luna", "low"
                    )
            receipt = (attempt / "recovery.json").read_bytes()
            self.fixture.source.unlink()
            self.assertTrue(RATER._recover_completed_attempt(
                attempt, self.accepted, self.fixture.entry, "gpt-5.6-luna", "low"
            ))
        self.assertEqual((attempt / "recovery.json").read_bytes(), receipt)
        self.assertTrue(self.accepted.is_file())

    def test_recovery_io_failure_stops_before_another_native_call(self):
        with self.fail_write("accepted.json"):
            self.fixture.score()
        with patch.object(RATER, "_recover_completed_attempt", side_effect=OSError("fixture disk full")), patch.object(
            RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")
        ):
            self.assertFalse(self.retry()[1])

    def test_prepared_publication_retries_from_custody_without_a_native_call(self):
        with self.fail_write("accepted.json"):
            self.assertFalse(self.fixture.score()[1])
        record_path = self.slot / "attempt-001/record.json"
        original = record_path.read_bytes()
        self.fixture.source.unlink()
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            self.assertTrue(self.retry()[1])
            self.assertTrue(self.retry()[1])
        accepted = json.loads(self.accepted.read_text())
        self.assertEqual(accepted["attempt_record_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(record_path.read_bytes(), original)
        self.assertEqual(len(list(self.slot.glob("attempt-*"))), 1)

    def test_changed_prepared_evidence_stops_instead_of_calling_again(self):
        with self.fail_write("accepted.json"):
            self.fixture.score()
        (self.slot / "attempt-001/events.jsonl").write_text(EVENTS.replace('true', 'false', 1))
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            self.assertFalse(self.retry()[1])
        self.assertFalse(self.accepted.exists())
        self.assertEqual(len(list(self.slot.glob("attempt-*"))), 1)

    def test_changed_candidate_cannot_be_published_or_trigger_another_call(self):
        with self.fail_write("accepted.json"):
            self.fixture.score()
        path = self.slot / "attempt-001/record.json"
        record = json.loads(path.read_text())
        record["judgment_candidate"]["judgment"]["C1"] = False
        path.write_text(json.dumps(record))
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            self.assertFalse(self.retry()[1])
        self.assertFalse(self.accepted.exists())

    def test_conflicting_legacy_receipt_stops_without_overwrite_or_native_call(self):
        attempt = self.legacy_attempt()
        with patch.object(RATER, "_find_rollout", return_value=self.fixture.source):
            with self.fail_write("accepted.json"):
                with self.assertRaises(OSError):
                    RATER._recover_completed_attempt(
                        attempt, self.accepted, self.fixture.entry, "gpt-5.6-luna", "low"
                    )
        path = attempt / "recovery.json"
        receipt = json.loads(path.read_text())
        receipt["original_record_sha256"] = "0" * 64
        path.write_text(json.dumps(receipt))
        original = path.read_bytes()
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            self.assertFalse(self.retry()[1])
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(self.accepted.exists())

    def test_missing_attempt_record_stops_instead_of_replaying(self):
        with self.fail_write("record.json"):
            with self.assertRaises(OSError):
                self.fixture.score()
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            result = self.retry()
        self.assertFalse(result[1])
        self.assertIn("partial attempt", result[2])
        self.assertFalse(self.accepted.exists())

    def test_unreadable_record_stops_instead_of_replaying(self):
        with self.fail_write("accepted.json"):
            self.fixture.score()
        (self.slot / "attempt-001/record.json").write_bytes(b'{"partial":')
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            self.assertFalse(self.retry()[1])
        self.assertFalse(self.accepted.exists())

    def test_published_marker_requires_its_unchanged_supporting_record(self):
        self.assertTrue(self.fixture.score()[1])
        record_path = self.slot / "attempt-001/record.json"
        record_path.write_bytes(record_path.read_bytes() + b" ")
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            with self.assertRaises(CalibrationError):
                self.retry()

    def test_json_publication_is_complete_before_visibility_and_never_replaces(self):
        target = self.root / "atomic.json"
        link = RATER.os.link
        observed = []

        def inspect_link(source, destination):
            self.assertFalse(target.exists())
            with open(source, "rb") as source_file:
                observed.append(json.loads(source_file.read()))
            return link(source, destination)

        with patch.object(RATER.os, "link", side_effect=inspect_link):
            RATER._write_new_json(target, {"ready": True})
        original = target.read_bytes()
        self.assertEqual(observed, [{"ready": True}])
        with self.assertRaises(FileExistsError):
            RATER._write_new_json(target, {"replacement": True})
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(list(self.root.glob(".atomic.json.*")), [])

    def test_json_flush_failure_leaves_no_marker_or_temporary_file(self):
        target = self.root / "atomic.json"
        with patch.object(RATER.os, "fsync", side_effect=OSError("fixture flush failure")):
            with self.assertRaises(OSError):
                RATER._write_new_json(target, {"ready": True})
        self.assertFalse(target.exists())
        self.assertEqual(list(self.root.glob(".atomic.json.*")), [])


if __name__ == "__main__":
    unittest.main()
