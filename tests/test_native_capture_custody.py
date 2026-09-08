"""Capture custody regressions using local files and a fake native process."""

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from caplab.artifact_rater import CalibrationError, preserve_rollout_attestation


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RATER = load_script("caplab-artifact-rater")
LADDER = load_script("caplab-ladder-subject")


def rollout(model="gpt-5.6-luna"):
    return ("\n".join(json.dumps(event) for event in [
        {"type": "session_meta", "payload": {"id": "thread-123", "cli_version": "0.146.0"}},
        {"type": "turn_context", "payload": {"model": model, "effort": "low"}},
    ]) + "\n").encode()


EVENTS = '{"type":"thread.started","thread_id":"thread-123"}\n{"type":"turn.completed"}\n'


class NativeCaptureCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source.jsonl"
        self.source.write_bytes(rollout())
        self.entry = {
            "slot": "slot-1", "scenario": "scenario-1", "code_ids": ["C1", "SCOPE"],
            "diff_sha256": hashlib.sha256(b"+changed\n").hexdigest(),
        }

    def score(self, *, custody_failure=False):
        diff = self.root / "campaign/attempts/slot-1/diff.patch"
        diff.parent.mkdir(parents=True)
        diff.write_bytes(b"+changed\n")
        codes = self.root / "scenarios/scenario-1/codes.json"
        codes.parent.mkdir(parents=True)
        codes.write_text(json.dumps({"codes": [
            {"id": key, "positive": "fixture", "negative_space": "fixture"}
            for key in self.entry["code_ids"]
        ]}))

        def native(command, **kwargs):
            last_message = Path(command[command.index("--output-last-message") + 1])
            last_message.write_text('{"C1":true,"SCOPE":true}')
            if custody_failure:
                (last_message.parent / "rollout.jsonl").mkdir()
            return subprocess.CompletedProcess(command, 0, EVENTS, "")

        with patch.object(RATER.subprocess, "run", side_effect=native), patch.object(
            RATER, "_find_rollout", return_value=self.source
        ):
            return RATER._score_entry(
                self.entry,
                {"campaign_root": str(self.root / "campaign"),
                 "scenario_root": str(self.root / "scenarios")},
                self.root / "out", "gpt-5.6-luna", "low", 10,
            )

    def test_rater_retains_the_snapshot_supporting_its_attestation(self):
        original_read = Path.read_bytes

        def changing_source(path):
            data = original_read(path)
            if path == self.source:
                self.source.write_bytes(rollout("different-model"))
            return data

        with patch.object(Path, "read_bytes", changing_source):
            self.assertTrue(self.score()[1])
        attempt = self.root / "out/scores/slot-1/attempt-001"
        record = json.loads((attempt / "record.json").read_text())
        retained = (attempt / "rollout.jsonl").read_bytes()
        self.assertEqual(retained, rollout())
        attestation = record["attestation"]
        self.assertEqual(attestation["rollout_sha256"], hashlib.sha256(retained).hexdigest())
        self.assertEqual(attestation["custody_rollout_sha256"], attestation["rollout_sha256"])

    def test_recovery_refuses_existing_custody_that_differs_from_source(self):
        attempt = self.root / "attempt"
        attempt.mkdir()
        (attempt / "record.json").write_text(json.dumps({
            "return_code": 0, "model": "gpt-5.6-luna", "effort": "low",
            "diff_sha256": self.entry["diff_sha256"], "prompt_sha256": "a" * 64,
        }))
        (attempt / "last-message.txt").write_text('{"C1":true,"SCOPE":true}')
        (attempt / "events.jsonl").write_text(EVENTS)
        retained = rollout("different-model")
        (attempt / "rollout.jsonl").write_bytes(retained)
        accepted = self.root / "accepted.json"
        with patch.object(RATER, "_find_rollout", return_value=self.source):
            with self.assertRaises(CalibrationError):
                RATER._recover_completed_attempt(
                    attempt, accepted, self.entry, "gpt-5.6-luna", "low"
                )
        self.assertFalse(accepted.exists())
        self.assertFalse((attempt / "recovery.json").exists())
        self.assertEqual((attempt / "rollout.jsonl").read_bytes(), retained)

    def test_rater_custody_failure_cannot_publish_an_accepted_judgment(self):
        _, success, reason = self.score(custody_failure=True)
        self.assertFalse(success)
        self.assertIn("cannot preserve rollout", reason)
        slot = self.root / "out/scores/slot-1"
        self.assertFalse((slot / "accepted.json").exists())
        record = json.loads((slot / "attempt-001/record.json").read_text())
        self.assertFalse(record["accepted"])
        self.assertNotIn("attestation", record)

    def test_preservation_is_private_and_reuses_only_identical_custody(self):
        custody = self.root / "retained.jsonl"
        first = preserve_rollout_attestation(self.source, custody, "thread-123")
        before = custody.stat()
        second = preserve_rollout_attestation(self.source, custody, "thread-123")
        self.assertEqual(first, second)
        self.assertEqual(custody.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(custody.stat().st_mode & 0o077, 0)
        self.assertEqual(first["rollout_path"], str(custody))
        self.assertEqual(first["source_rollout_path"], str(self.source))
        self.source.write_bytes(rollout("different-model"))
        with self.assertRaises(CalibrationError):
            preserve_rollout_attestation(self.source, custody, "thread-123")
        self.assertEqual(custody.read_bytes(), rollout())

    def test_invalid_capture_is_retained_without_attestation(self):
        self.source.write_bytes(rollout() + b'{"type":')
        custody = self.root / "retained.jsonl"
        with self.assertRaises(CalibrationError):
            preserve_rollout_attestation(self.source, custody, "thread-123")
        self.assertEqual(custody.read_bytes(), self.source.read_bytes())

    def test_linked_custody_is_not_reused_or_overwritten(self):
        custody = self.root / "retained.jsonl"
        custody.symlink_to(self.source)
        with self.assertRaises(CalibrationError):
            preserve_rollout_attestation(self.source, custody, "thread-123")
        self.assertTrue(custody.is_symlink())
        self.assertEqual(self.source.read_bytes(), rollout())

    def test_partial_write_cannot_attest_or_be_replaced_on_retry(self):
        custody = self.root / "retained.jsonl"
        fdopen = os.fdopen

        class InterruptedWriter:
            def __init__(self, descriptor, mode):
                self.output = fdopen(descriptor, mode)

            def __enter__(self):
                return self

            def write(self, data):
                self.output.write(data[:10])
                raise OSError("fixture disk full")

            def __exit__(self, *args):
                self.output.close()

        with patch("caplab.artifact_rater.os.fdopen", InterruptedWriter):
            with self.assertRaisesRegex(CalibrationError, "fixture disk full"):
                preserve_rollout_attestation(self.source, custody, "thread-123")
        self.assertEqual(custody.read_bytes(), rollout()[:10])
        with self.assertRaises(CalibrationError):
            preserve_rollout_attestation(self.source, custody, "thread-123")
        self.assertEqual(custody.read_bytes(), rollout()[:10])

    def test_ladder_custody_failure_cannot_leave_a_successful_pin(self):
        scenario = self.root / "scenarios/scenario-1"
        (scenario / "world").mkdir(parents=True)
        (scenario / "TASK.md").write_text("Local fixture task")
        policy = self.root / "policy.json"
        policy.write_text("{}")
        arguments = argparse.Namespace(
            scenario="scenario-1", arm="none", model="gpt-5.6-luna", effort="low",
            trial=1, replacement=None, campaign_root=self.root / "campaign",
            scenario_root=self.root / "scenarios", policy=policy, tuple_policy=policy,
            timeout=10,
        )

        def native(command, **kwargs):
            if command[:2] == ["codex", "--version"]:
                return subprocess.CompletedProcess(command, 0, "codex-cli 0.146.0", "")
            if command[:2] == ["codex", "exec"]:
                attempt = next((self.root / "campaign/attempts").iterdir())
                # Occupy the destination so neither a copy nor exclusive creation can succeed.
                (attempt / "rollout.jsonl").mkdir()
                return subprocess.CompletedProcess(command, 0, EVENTS, "")
            return subprocess.CompletedProcess(command, 0, "", "")

        def git(world, *args, **kwargs):
            return "a.py\n" if "--name-only" in args else "+changed\n"

        with patch.object(LADDER, "validate_ladder_subject"), patch.object(
            LADDER, "_run_git", side_effect=git
        ), patch.object(LADDER.subprocess, "run", side_effect=native), patch.object(
            LADDER, "_find_rollout", return_value=self.source
        ):
            result = LADDER._run_historical_ladder_attempt(arguments)
        episode_path = next((self.root / "campaign/attempts").glob("*/episode.json"))
        episode = json.loads(episode_path.read_text())
        self.assertEqual(result, 1)
        self.assertEqual(episode["disposition"], "infrastructure")
        self.assertFalse(episode["pin_ok"])
        self.assertIsNone(episode["attempted"])
        self.assertIsNone(episode["attested_model"])


if __name__ == "__main__":
    unittest.main()
