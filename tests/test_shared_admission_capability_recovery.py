"""Capability transport faults over genuine custody, SDK and native processes."""

import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from caplab.revbench import shared_admission as shared
from caplab.revbench.custody import LiveExecutionCustodyError
from caplab.revbench.execution import _terminal_custody_capture
import tests.test_shared_admission as prior
import tests.test_shared_admission_review as review


@unittest.skipUnless(prior.CLI, "set CAPLAB_TEST_SHARED_QM to the installed SDK")
class CapabilityRecoveryTests(unittest.TestCase):
    setUp = prior.SharedAdmissionTests.setUp
    plan = prior.SharedAdmissionTests.plan
    claim = prior.SharedAdmissionTests.claim
    run_process = prior.SharedAdmissionTests.run_process
    snapshot = review.ReviewRegressionTests.snapshot

    def exercise(self, target, failure="timeout"):
        self.clocks.close()
        subprocess.run([
            prior.CLI, "admission", "configure", "--home", self.document["home"],
            "--home-id", self.document["home_id"],
            "--policy", self.document["policy_path"],
        ], check=True, capture_output=True)
        plan, argv, logical = self.plan(["/bin/sleep", "0.3"], bind_root=True)
        session, capture = self.claim(plan)
        current = {"verb": None, "fired": False}
        call = shared.ProcessAdmission._call
        run = subprocess.run

        def operation(gate, verb, **fields):
            current["verb"] = verb
            return call(gate, verb, **fields)

        def transport(command, *args, **kwargs):
            if (command[1:3] == ["admission", "capabilities"]
                    and current["verb"] == target and not current["fired"]):
                current["fired"] = True
                if failure == "timeout":
                    raise subprocess.TimeoutExpired(command, 10)
                if failure == "oserror":
                    raise OSError("test transport unavailable")
                if failure == "nonzero":
                    return subprocess.CompletedProcess(command, 1, b"", b"busy")
                if failure == "invalid_json":
                    return subprocess.CompletedProcess(command, 0, b"{", b"")
                raise AssertionError(failure)
            return run(command, *args, **kwargs)

        with mock.patch.object(shared.ProcessAdmission, "_call", operation), \
                mock.patch.object(subprocess, "run", transport):
            observation = self.run_process(capture, plan, argv, logical)
            _terminal_custody_capture(session, plan, capture, self.enrollment)
        self.assertTrue(current["fired"], target)
        terminal = session.claim_process(plan)
        self.assertIsNotNone(terminal.completion)
        prechild = target in {"reserve", "prepare-launch"}
        self.assertEqual(observation.invocation_state,
                         "not-invoked" if prechild else "invoked")
        self.assertEqual(observation.termination,
                         "preflight-refused" if prechild else "exited")
        if not prechild:
            self.assertEqual(observation.exit_code, 0)
        self.enrollment.reconcile_session(session)
        snap = self.snapshot()
        if target == "reserve":
            self.assertEqual(snap["allocations"], {})
        else:
            self.assertEqual(snap["pools"]["fixture-pool"], {
                "slots": 0, "windows": {"fixture-window": {
                    "spent": 0 if prechild else 1, "outstanding": 0}}})
        records = snap["records"]
        self.enrollment.reconcile_session(session)
        self.assertEqual(self.snapshot()["records"], records)
        self.assertTrue(list(capture.custody_root.glob("shared-control-fault-*.json")))

    def test_capability_timeout_before_reserve_closes_native_right(self):
        self.exercise("reserve")

    def test_capability_timeout_before_prepare_returns_unused_capacity(self):
        self.exercise("prepare-launch")

    def test_capability_timeout_after_creation_preserves_native_completion(self):
        self.exercise("record-launch")

    def test_capability_timeout_before_close_is_recoverable(self):
        self.exercise("close-launch")

    def test_capability_timeout_before_status_is_recoverable(self):
        self.exercise("status")

    def test_capability_timeout_before_settle_is_recoverable(self):
        self.exercise("settle")

    def test_capability_oserror_is_recoverable(self):
        self.exercise("prepare-launch", "oserror")

    def test_capability_nonzero_exit_is_recoverable(self):
        self.exercise("record-launch", "nonzero")

    def test_capability_invalid_json_is_recoverable(self):
        self.exercise("record-launch", "invalid_json")

    def test_valid_changed_capability_identity_remains_a_pin_error(self):
        self.clocks.close()
        plan, argv, _ = self.plan()
        _, capture = self.claim(plan)
        run = subprocess.run

        def changed(command, *args, **kwargs):
            reply = run(command, *args, **kwargs)
            if command[1:3] == ["admission", "capabilities"]:
                body = json.loads(reply.stdout)
                body["source_tree_sha256"] = "sha256:" + "0" * 64
                return subprocess.CompletedProcess(command, 0,
                                                   json.dumps(body).encode(), b"")
            return reply

        with mock.patch.object(subprocess, "run", changed):
            with self.assertRaisesRegex(LiveExecutionCustodyError, "sdk_pin_changed"):
                self.enrollment.capture(capture).prepare(argv)
        self.assertFalse(capture._closed)
        self.assertFalse(Path(self.document["home"]).exists())
