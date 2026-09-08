"""Capture custody regressions using local files and a fake native process."""

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
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


ANSWER = '{"C1":true,"SCOPE":true}'
MESSAGE = json.dumps({"type": "item.completed", "item": {
    "id": "answer-1", "type": "agent_message", "text": ANSWER,
}}) + "\n"
EVENTS = ('{"type":"thread.started","thread_id":"thread-123"}\n'
          '{"type":"turn.started"}\n' + MESSAGE + '{"type":"turn.completed"}\n')


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

    def score(self, *, custody_failure=False, process_error=None,
              native_output=(EVENTS.encode(), b""), native_return_code=0,
              last_message_bytes=ANSWER.encode()):
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
            if process_error is not None:
                raise process_error
            last_message = Path(command[command.index("--output-last-message") + 1])
            last_message.write_bytes(last_message_bytes)
            if custody_failure:
                (last_message.parent / "rollout.jsonl").mkdir()
            stdout, stderr = native_output
            if kwargs.get("text"):
                stdout, stderr = stdout.decode(), stderr.decode()
            return subprocess.CompletedProcess(command, native_return_code, stdout, stderr)

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
        self.assertFalse(record["validated"])
        self.assertNotIn("attestation", record)

    def test_rater_rejects_failed_or_incomplete_event_evidence(self):
        base = self.root
        streams = (
            EVENTS.replace('{"type":"turn.completed"}\n', ''),
            EVENTS.replace('turn.completed', 'turn.failed'),
            EVENTS + '{"type":"turn.started"}\n',
            EVENTS + '{"type":',
            EVENTS.replace('{"type":"turn.started"}\n', ''),
            EVENTS + '{"type":"thread.started","thread_id":"other"}\n',
            EVENTS.replace('"type":"turn.completed"', '"type":"turn.failed","type":"turn.completed"'),
            EVENTS.replace('{"type":"turn.completed"}',
                           '{"type":"notice","rate_limit_info":{"status":"rejected"}}\n{"type":"turn.completed"}'),
        )
        for index, stream in enumerate(streams):
            with self.subTest(stream=stream):
                self.root = base / str(index)
                _, success, _ = self.score(native_output=(stream.encode(), b""))
                self.assertFalse(success)
                slot = self.root / "out/scores/slot-1"
                record = json.loads((slot / "attempt-001/record.json").read_text())
                self.assertFalse(record["validated"])
                self.assertFalse((slot / "accepted.json").exists())
                self.assertEqual((slot / "attempt-001/events.jsonl").read_bytes(), stream.encode())

    def test_recovery_cannot_accept_a_failed_native_turn(self):
        attempt = self.root / "attempt"
        attempt.mkdir()
        (attempt / "record.json").write_text(json.dumps({
            "return_code": 0, "model": "gpt-5.6-luna", "effort": "low",
            "diff_sha256": self.entry["diff_sha256"], "prompt_sha256": "a" * 64,
        }))
        (attempt / "last-message.txt").write_text('{"C1":true,"SCOPE":true}')
        (attempt / "events.jsonl").write_text(EVENTS.replace("turn.completed", "turn.failed"))
        accepted = self.root / "accepted.json"
        with patch.object(RATER, "_find_rollout", return_value=self.source):
            with self.assertRaises(CalibrationError):
                RATER._recover_completed_attempt(attempt, accepted, self.entry, "gpt-5.6-luna", "low")
        self.assertFalse(accepted.exists())
        self.assertFalse((attempt / "recovery.json").exists())

    def test_rater_judgment_must_agree_with_final_native_message(self):
        base = self.root
        streams = (
            EVENTS.replace('true', 'false', 1),
            EVENTS.replace(MESSAGE, ''),
            EVENTS.replace('agent_message', 'command_execution'),
            EVENTS.replace(MESSAGE, MESSAGE + MESSAGE.replace('true', 'false', 1).replace('answer-1', 'answer-2')),
            EVENTS.replace('"text":', '"unrecognized_text":'),
        )
        for index, capture in enumerate(streams):
            with self.subTest(capture=capture):
                self.root = base / str(index)
                self.assertFalse(self.score(native_output=(capture.encode(), b""))[1])
                slot = self.root / "out/scores/slot-1"
                self.assertFalse((slot / "accepted.json").exists())
                record = json.loads((slot / "attempt-001/record.json").read_text())
                self.assertFalse(record["validated"])

    def test_recovery_cannot_admit_a_different_sidecar_answer(self):
        attempt = self.root / "attempt"
        attempt.mkdir()
        (attempt / "record.json").write_text(json.dumps({
            "return_code": 0, "model": "gpt-5.6-luna", "effort": "low",
            "diff_sha256": self.entry["diff_sha256"], "prompt_sha256": "a" * 64,
        }))
        (attempt / "last-message.txt").write_text(ANSWER)
        (attempt / "events.jsonl").write_text(EVENTS.replace('true', 'false', 1))
        accepted = self.root / "accepted.json"
        with patch.object(RATER, "_find_rollout", return_value=self.source):
            with self.assertRaises(CalibrationError):
                RATER._recover_completed_attempt(attempt, accepted, self.entry, "gpt-5.6-luna", "low")
        self.assertFalse(accepted.exists())
        self.assertFalse((attempt / "recovery.json").exists())

    def test_matching_boolean_answers_retain_their_derivation(self):
        sidecar = b' { "SCOPE": true, "C1": true }\n'
        self.assertTrue(self.score(last_message_bytes=sidecar)[1])
        slot = self.root / "out/scores/slot-1"
        record = json.loads((slot / "attempt-001/record.json").read_text())
        accepted = json.loads((slot / "accepted.json").read_text())
        derived = accepted["judgment_derivation"]
        self.assertEqual(accepted["judgment"], {"C1": True, "SCOPE": True})
        self.assertEqual(derived, record["judgment_derivation"])
        self.assertEqual(derived["selected_event_index"], 2)
        self.assertEqual(derived["selected_item_id"], "answer-1")
        self.assertEqual(derived["events_sha256"], record["events_sha256"])
        self.assertEqual(derived["extracted_text_sha256"], hashlib.sha256(ANSWER.encode()).hexdigest())
        self.assertEqual(derived["last_message_sha256"], hashlib.sha256(sidecar).hexdigest())
        self.assertEqual(record["last_message_sha256"], derived["last_message_sha256"])
        self.assertEqual(derived["sidecar_comparison"], "exact-code-booleans/1")

    def test_ambiguous_or_invalid_answer_files_do_not_produce_judgments(self):
        base = self.root
        for index, answer in enumerate((b'{"C1":false,"C1":true,"SCOPE":true}', b'\xff', b'not-json')):
            with self.subTest(answer=answer):
                self.root = base / str(index)
                self.assertFalse(self.score(last_message_bytes=answer)[1])
                slot = self.root / "out/scores/slot-1"
                self.assertFalse((slot / "accepted.json").exists())
                self.assertEqual((slot / "attempt-001/last-message.txt").read_bytes(), answer)
                self.assertFalse(json.loads((slot / "attempt-001/record.json").read_text())["validated"])

    def test_ambiguous_native_answer_is_not_resolved_by_a_valid_sidecar(self):
        message = json.dumps({"type": "item.completed", "item": {
            "type": "agent_message", "id": "answer-1",
            "text": '{"C1":false,"C1":true,"SCOPE":true}',
        }}) + "\n"
        self.assertFalse(self.score(native_output=(EVENTS.replace(MESSAGE, message).encode(), b""))[1])
        self.assertFalse((self.root / "out/scores/slot-1/accepted.json").exists())

    def test_matching_recovery_records_derivation_without_rewriting_original(self):
        attempt = self.root / "attempt"
        attempt.mkdir()
        original = json.dumps({
            "return_code": 0, "model": "gpt-5.6-luna", "effort": "low",
            "diff_sha256": self.entry["diff_sha256"], "prompt_sha256": "a" * 64,
            "accepted": False,
        }).encode()
        (attempt / "record.json").write_bytes(original)
        (attempt / "last-message.txt").write_text(ANSWER)
        (attempt / "events.jsonl").write_text(EVENTS)
        accepted_path = self.root / "accepted.json"
        with patch.object(RATER, "_find_rollout", return_value=self.source):
            self.assertTrue(RATER._recover_completed_attempt(
                attempt, accepted_path, self.entry, "gpt-5.6-luna", "low"
            ))
        accepted = json.loads(accepted_path.read_text())
        recovery = json.loads((attempt / "recovery.json").read_text())
        self.assertEqual(accepted["judgment_derivation"], recovery["judgment_derivation"])
        self.assertEqual(recovery["judgment_derivation"]["events_sha256"], hashlib.sha256(EVENTS.encode()).hexdigest())
        self.assertEqual((attempt / "record.json").read_bytes(), original)

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

    def ladder(self, *, custody_failure=False, process_error=None):
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
                if process_error is not None:
                    raise process_error
                attempt = next((self.root / "campaign/attempts").iterdir())
                if custody_failure:
                    # Occupy the destination so neither copying nor exclusive creation succeeds.
                    (attempt / "rollout.jsonl").mkdir()
                stdout, stderr = (EVENTS, "") if kwargs.get("text") else (EVENTS.encode(), b"")
                return subprocess.CompletedProcess(command, 0, stdout, stderr)
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
        return result, episode, episode_path.parent

    def test_ladder_custody_failure_cannot_leave_a_successful_pin(self):
        result, episode, _ = self.ladder(custody_failure=True)
        self.assertEqual(result, 1)
        self.assertEqual(episode["disposition"], "infrastructure")
        self.assertFalse(episode["pin_ok"])
        self.assertIsNone(episode["attempted"])
        self.assertIsNone(episode["attested_model"])

    def test_real_timeout_bytes_are_retained_with_rater_failure_record(self):
        stdout = EVENTS.encode() + b'{"partial":"\xe2'
        stderr = b"native diagnostic\xff"
        command = [sys.executable, "-c", (
            f"import os,time; os.write(1, {stdout!r}); "
            f"os.write(2, {stderr!r}); time.sleep(60)"
        )]
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            subprocess.run(command, capture_output=True, text=True, timeout=1)
        self.assertEqual(caught.exception.stdout, stdout)
        self.assertEqual(caught.exception.stderr, stderr)
        _, success, reason = self.score(process_error=caught.exception)
        self.assertFalse(success)
        self.assertIn("timed out", reason)
        slot = self.root / "out/scores/slot-1"
        attempt = slot / "attempt-001"
        self.assertEqual((attempt / "events.jsonl").read_bytes(), stdout)
        self.assertEqual((attempt / "stderr.txt").read_bytes(), stderr)
        record = json.loads((attempt / "record.json").read_text())
        self.assertTrue(record["timed_out"])
        self.assertEqual(record["return_code"], 124)
        self.assertFalse(record["validated"])
        self.assertEqual(record["events_sha256"], hashlib.sha256(stdout).hexdigest())
        self.assertEqual(record["stderr_sha256"], hashlib.sha256(stderr).hexdigest())
        self.assertFalse((slot / "accepted.json").exists())

    def test_ladder_timeout_retains_partial_bytes_and_infrastructure_disposition(self):
        stdout = EVENTS.encode() + b'{"partial":"\xe2'
        stderr = b"native diagnostic\xff"
        error = subprocess.TimeoutExpired(["fixture"], 10, output=stdout, stderr=stderr)
        result, episode, attempt = self.ladder(process_error=error)
        self.assertEqual(result, 1)
        self.assertEqual((attempt / "native.stdout").read_bytes(), stdout)
        self.assertEqual((attempt / "native.stderr").read_bytes(), stderr)
        self.assertTrue(episode["timed_out"])
        self.assertEqual(episode["rc"], 124)
        self.assertEqual(episode["disposition"], "infrastructure")
        self.assertIn("timed out", episode["infra_reason"])
        self.assertIsNone(episode["attempted"])

    def test_rater_timeout_without_output_records_empty_streams(self):
        error = subprocess.TimeoutExpired(["fixture"], 10)
        self.assertFalse(self.score(process_error=error)[1])
        attempt = self.root / "out/scores/slot-1/attempt-001"
        self.assertEqual((attempt / "events.jsonl").read_bytes(), b"")
        self.assertEqual((attempt / "stderr.txt").read_bytes(), b"")
        self.assertTrue(json.loads((attempt / "record.json").read_text())["timed_out"])

    def test_normal_binary_capture_preserves_native_bytes(self):
        stdout = EVENTS.replace("\n", "\r\n").encode()
        stderr = "diagnostic café\r\n".encode()
        self.assertTrue(self.score(native_output=(stdout, stderr))[1])
        attempt = self.root / "out/scores/slot-1/attempt-001"
        self.assertEqual((attempt / "events.jsonl").read_bytes(), stdout)
        self.assertEqual((attempt / "stderr.txt").read_bytes(), stderr)
        record = json.loads((attempt / "record.json").read_text())
        self.assertFalse(record["timed_out"])
        self.assertTrue(record["validated"])

    def test_invalid_utf8_cannot_be_accepted_or_recovered(self):
        stdout = EVENTS.encode() + b"\xff"
        self.assertFalse(self.score(native_output=(stdout, b""))[1])
        slot = self.root / "out/scores/slot-1"
        attempt = slot / "attempt-001"
        self.assertEqual((attempt / "events.jsonl").read_bytes(), stdout)
        self.assertFalse(RATER._recover_completed_attempt(
            attempt, slot / "accepted.json", self.entry, "gpt-5.6-luna", "low"
        ))
        self.assertFalse((slot / "accepted.json").exists())
        self.assertFalse((attempt / "recovery.json").exists())

    def test_exit_124_is_not_reported_as_an_observed_timeout(self):
        _, success, reason = self.score(native_return_code=124)
        self.assertFalse(success)
        self.assertEqual(reason, "Codex exited 124")
        attempt = self.root / "out/scores/slot-1/attempt-001"
        record = json.loads((attempt / "record.json").read_text())
        self.assertFalse(record["timed_out"])

    def test_ladder_timeout_without_output_still_records_an_attempt(self):
        error = subprocess.TimeoutExpired(["fixture"], 10)
        result, episode, attempt = self.ladder(process_error=error)
        self.assertEqual(result, 1)
        self.assertTrue(episode["timed_out"])
        self.assertFalse(episode["pin_ok"])
        self.assertIsNone(episode["attempted"])
        self.assertEqual((attempt / "native.stdout").read_bytes(), b"")
        self.assertEqual((attempt / "native.stderr").read_bytes(), b"")


if __name__ == "__main__":
    unittest.main()
