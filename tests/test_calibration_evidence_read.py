"""Calibration must consume the published rater and preserved evidence it names."""

import argparse
import hashlib
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from caplab.artifact_rater import CalibrationError
import test_native_capture_custody as capture_fixtures

RATER = capture_fixtures.RATER


class CalibrationEvidenceReadTests(unittest.TestCase):
    def setUp(self):
        self.fixture = capture_fixtures.NativeCaptureCustodyTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.fixture.entry["code_ids"] = ["C1", "C2", "SCOPE"]
        self.judgment = {"C1": True, "C2": False, "SCOPE": True}
        self.fixture.entry["old_judgment"] = self.judgment
        self.answer = json.dumps(self.judgment)
        message = json.dumps({"type": "item.completed", "item": {
            "type": "agent_message", "id": "answer-1", "text": self.answer,
        }}) + "\n"
        self.events = capture_fixtures.EVENTS.replace(capture_fixtures.MESSAGE, message).encode()
        self.assertTrue(self.fixture.score(native_output=(self.events, b""), last_message_bytes=self.answer.encode())[1])
        self.slot = self.root / "out/scores/slot-1"
        self.accepted = self.slot / "accepted.json"
        self.attempt = self.slot / "attempt-001"
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(json.dumps({"entries": [self.fixture.entry]}))
        self.arguments = argparse.Namespace(
            manifest=self.manifest, output_root=self.root / "out", model="gpt-5.6-luna", effort="low"
        )

    def test_evaluation_rejects_a_different_rater_label(self):
        self.arguments.model = "different-model"
        with self.assertRaises(CalibrationError):
            RATER.command_evaluate(self.arguments)
        self.assertFalse((self.root / "out/calibration-result.json").exists())

    def test_evaluation_rejects_wrong_published_scenario_and_diff(self):
        original = json.loads(self.accepted.read_text())
        for key, value in (("scenario", "different-scenario"), ("diff_sha256", "0" * 64),
                           ("slot", "different-slot"), ("effort", "high")):
            with self.subTest(key=key):
                self.accepted.write_text(json.dumps({**original, key: value}))
                with self.assertRaises(CalibrationError):
                    RATER.command_evaluate(self.arguments)

    def test_evaluation_and_cache_reject_changed_capture(self):
        (self.attempt / "events.jsonl").write_bytes(self.events + b'{"partial":')
        with self.assertRaises(CalibrationError):
            RATER.command_evaluate(self.arguments)
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            with self.assertRaises(CalibrationError):
                RATER._score_entry(self.fixture.entry, {}, self.root / "out", "gpt-5.6-luna", "low", 10)

    def test_evaluation_rejects_ambiguous_rollout_even_with_updated_hashes(self):
        rollout = self.attempt / "rollout.jsonl"
        raw = rollout.read_bytes().replace(b'"model":', b'"model":"another-model","model":')
        rollout.write_bytes(raw)
        record_path = self.attempt / "record.json"
        record = json.loads(record_path.read_text())
        digest = hashlib.sha256(raw).hexdigest()
        record["attestation"]["rollout_sha256"] = digest
        record["attestation"]["custody_rollout_sha256"] = digest
        record_path.write_text(json.dumps(record))
        accepted = json.loads(self.accepted.read_text())
        accepted["attempt_record_sha256"] = hashlib.sha256(record_path.read_bytes()).hexdigest()
        self.accepted.write_text(json.dumps(accepted))
        before = self.snapshot()
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")):
            with self.assertRaisesRegex(CalibrationError, "malformed rollout JSON"):
                RATER.command_evaluate(self.arguments)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / "out/calibration-result.json").exists())

    def test_evaluation_requires_the_supporting_record(self):
        (self.attempt / "record.json").unlink()
        with self.assertRaises((CalibrationError, OSError)):
            RATER.command_evaluate(self.arguments)
        self.assertFalse((self.root / "out/calibration-result.json").exists())

    def evaluate(self):
        with redirect_stdout(io.StringIO()):
            status = RATER.command_evaluate(self.arguments)
        return status, json.loads((self.root / "out/calibration-result.json").read_text())

    def snapshot(self):
        return {str(path.relative_to(self.slot)): path.read_bytes()
                for path in self.slot.rglob("*") if path.is_file()}

    def test_verified_results_retain_input_hashes_without_changing_evidence(self):
        before = self.snapshot()
        with patch.object(RATER.subprocess, "run", side_effect=AssertionError("unexpected native call")), patch.object(
            RATER, "_find_rollout", side_effect=AssertionError("unexpected live source lookup")
        ):
            status, result = self.evaluate()
            self.assertEqual(RATER._score_entry(
                self.fixture.entry, {}, self.root / "out", "gpt-5.6-luna", "low", 10,
            ), ("slot-1", True, "already accepted"))
            self.assertEqual(self.evaluate(), (status, result))
        self.assertEqual(status, 0)
        self.assertTrue(result["passed"])
        self.assertEqual(result["schema_version"], "caplab-rater-calibration-result/2")
        self.assertEqual(result["input_evidence"], {
            "schema_version": "caplab-calibration-inputs/1",
            "manifest_sha256": hashlib.sha256(self.manifest.read_bytes()).hexdigest(),
            "judgments": [{"slot": "slot-1", **{
                key: hashlib.sha256(before[path]).hexdigest() for key, path in (
                    ("published_sha256", "accepted.json"),
                    ("attempt_record_sha256", "attempt-001/record.json"),
                    ("events_sha256", "attempt-001/events.jsonl"),
                    ("rollout_sha256", "attempt-001/rollout.jsonl"),
                )
            }}],
        })
        self.assertEqual(self.snapshot(), before)

    def legacy(self, recovered=False):
        record = json.loads((self.attempt / "record.json").read_text())
        record["schema_version"] = "caplab-artifact-rater-attempt/1"
        del record["validated"], record["judgment_candidate"], record["judgment_derivation"]
        record["accepted"] = not recovered
        accepted = json.loads(self.accepted.read_text())
        del accepted["attempt_record_sha256"], accepted["judgment_derivation"]
        if recovered:
            accepted["recovered_from_preserved_attempt"] = True
            receipt = {key: record.pop(key) for key in ("thread_id", "attestation", "last_message_sha256")}
        raw = json.dumps(record).encode()
        (self.attempt / "record.json").write_bytes(raw)
        if recovered:
            receipt.update({"schema_version": "caplab-artifact-rater-recovery/1",
                            "original_record_sha256": hashlib.sha256(raw).hexdigest()})
            (self.attempt / "recovery.json").write_text(json.dumps(receipt))
        self.accepted.write_text(json.dumps(accepted))

    def test_legacy_original_acceptance_is_verified_read_only(self):
        self.legacy()
        before = self.snapshot()
        with patch.object(RATER, "_find_rollout", side_effect=AssertionError("unexpected live lookup")):
            self.assertEqual(self.evaluate()[0], 0)
        self.assertEqual(self.snapshot(), before)

    def test_legacy_recovery_is_verified_from_custody_and_linked(self):
        self.legacy(recovered=True)
        self.fixture.source.unlink()
        before = self.snapshot()
        with patch.object(RATER, "_find_rollout", side_effect=AssertionError("unexpected live lookup")):
            status, result = self.evaluate()
        self.assertEqual(status, 0)
        self.assertEqual(result["input_evidence"]["judgments"][0]["recovery_sha256"],
                         hashlib.sha256(before["attempt-001/recovery.json"]).hexdigest())
        self.assertEqual(self.snapshot(), before)

    def test_legacy_recovery_refuses_wrong_or_missing_proof(self):
        self.legacy(recovered=True)
        receipt_path = self.attempt / "recovery.json"
        receipt = json.loads(receipt_path.read_text())
        for key, value in (("original_record_sha256", "0" * 64), ("schema_version", "unknown"),
                           ("thread_id", "wrong-thread"), ("last_message_sha256", "0" * 64),
                           ("judgment_derivation", {})):
            with self.subTest(key=key):
                receipt_path.write_text(json.dumps({**receipt, key: value}))
                with self.assertRaises(CalibrationError):
                    self.evaluate()
        receipt_path.unlink()
        with self.assertRaises(OSError):
            self.evaluate()

    def test_new_publication_cannot_drop_its_record_link(self):
        accepted = json.loads(self.accepted.read_text())
        del accepted["attempt_record_sha256"]
        self.accepted.write_text(json.dumps(accepted))
        with self.assertRaises(CalibrationError):
            self.evaluate()

    def test_record_hash_alone_cannot_override_conflicting_attempt_identity(self):
        record_path = self.attempt / "record.json"
        original_record = json.loads(record_path.read_text())
        original_accepted = json.loads(self.accepted.read_text())
        for key, value in (("model", "wrong-model"), ("slot", "wrong-slot"),
                           ("last_message_sha256", "0" * 64)):
            with self.subTest(key=key):
                raw = json.dumps({**original_record, key: value}).encode()
                record_path.write_bytes(raw)
                self.accepted.write_text(json.dumps({**original_accepted,
                    "attempt_record_sha256": hashlib.sha256(raw).hexdigest()}))
                with self.assertRaises(CalibrationError):
                    self.evaluate()

    def test_legacy_without_acceptance_cannot_be_evaluated(self):
        self.legacy()
        path = self.attempt / "record.json"
        record = json.loads(path.read_text())
        record["accepted"] = False
        path.write_text(json.dumps(record))
        with self.assertRaises(CalibrationError):
            self.evaluate()

    def test_existing_result_is_not_replaced_for_a_changed_manifest(self):
        self.evaluate()
        path = self.root / "out/calibration-result.json"
        before = path.read_bytes()
        self.manifest.write_bytes(self.manifest.read_bytes() + b"\n")
        with self.assertRaises(CalibrationError):
            self.evaluate()
        self.assertEqual(path.read_bytes(), before)

    def test_evidence_documents_refuse_duplicate_keys(self):
        before = self.snapshot()
        for path in (self.accepted, self.attempt / "record.json", self.manifest):
            with self.subTest(path=path.name):
                raw = path.read_bytes()
                path.write_bytes(raw[:-1] + b', "schema_version":"ambiguous", "schema_version":"ambiguous"}')
                with self.assertRaises(CalibrationError):
                    self.evaluate()
                path.write_bytes(raw)
        self.assertEqual(self.snapshot(), before)

    def test_evaluation_refuses_attempt_path_traversal(self):
        original = json.loads(self.accepted.read_text())
        for attempt in ("../attempt-001", "attempt-001/../../other", "/attempt-001", None):
            with self.subTest(attempt=attempt):
                self.accepted.write_text(json.dumps({**original, "attempt": attempt}))
                with self.assertRaises(CalibrationError):
                    self.evaluate()

    def test_evaluation_refuses_corrupted_supporting_files(self):
        for name in ("last-message.txt", "rollout.jsonl", "prompt.txt", "schema.json", "stderr.txt"):
            with self.subTest(name=name):
                path = self.attempt / name
                before = path.read_bytes()
                path.write_bytes(before + b"corruption")
                with self.assertRaises(CalibrationError):
                    self.evaluate()
                path.write_bytes(before)


if __name__ == "__main__":
    unittest.main()
