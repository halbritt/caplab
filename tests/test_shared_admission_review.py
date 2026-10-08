"""Review regressions using the deployed public CLI and real host/process clocks."""

import datetime
import json
import subprocess
import time
import unittest
from pathlib import Path
from unittest import mock

from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench import codex, shared_admission as shared
from caplab.revbench.execution import _terminal_custody_capture
from caplab.revbench.custody import LiveExecutionCustodyError
import tests.test_shared_admission as prior


@unittest.skipUnless(prior.CLI, "set CAPLAB_TEST_SHARED_QM to the explicit SDK CLI")
class ReviewRegressionTests(unittest.TestCase):
    setUp = prior.SharedAdmissionTests.setUp
    plan = prior.SharedAdmissionTests.plan
    claim = prior.SharedAdmissionTests.claim
    run_process = prior.SharedAdmissionTests.run_process

    def real_clocks(self):
        self.clocks.close()

    def snapshot(self):
        return json.loads(
            subprocess.check_output(
                [
                    prior.CLI,
                    "admission",
                    "status",
                    "--home",
                    self.document["home"],
                    "--home-id",
                    "fixture-home",
                    "--now",
                    datetime.datetime.now(datetime.UTC)
                    .isoformat(timespec="microseconds")
                    .replace("+00:00", "Z"),
                ]
            )
        )

    def other_reserve(self):
        request = dict(
            request_id="external-clock",
            caller_id="other",
            route_id="terra",
            account_id="codex-main",
            max_slots=1,
            max_launches=1,
            home_id="fixture-home",
            valid_until="2027-01-01T00:00:00Z",
        )
        path = self.root / "other-clock-request.json"
        path.write_bytes(canonical_json(request))
        return json.loads(
            subprocess.check_output(
                [
                    prior.CLI,
                    "admission",
                    "reserve",
                    "--home",
                    self.document["home"],
                    "--home-id",
                    "fixture-home",
                    "--now",
                    datetime.datetime.now(datetime.UTC)
                    .isoformat(timespec="microseconds")
                    .replace("+00:00", "Z"),
                    "--request",
                    str(path),
                    "--holder-id",
                    "other-holder",
                    "--namespace",
                    "surveyor",
                    "--policy",
                    self.paths["policy_path"],
                    "--catalog",
                    self.paths["release_path"],
                    "--observations",
                    self.paths["observations_path"],
                ]
            )
        )

    def test_subsecond_other_consumer_does_not_strand_prechild_admission(self):
        self.real_clocks()
        self.assertEqual(self.other_reserve()["status"], "admitted")
        plan, argv, _ = self.plan()
        _, capture = self.claim(plan)
        gate = self.enrollment.capture(capture)
        self.assertTrue(gate.prepare(argv))
        capture.shared_admission = gate
        codex._complete_before_launch(capture, "preflight-refused")
        snap = self.snapshot()
        own = next(
            a for a in snap["allocations"].values() if a["namespace"] == "caplab"
        )
        self.assertEqual(own["terminal"]["result"]["launched"], 0)
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 1)
        # Even when scheduler latency crosses a second and masks the refusal,
        # retained real transport must preserve the required clock precision.
        transports = [
            json.loads(p.read_bytes())
            for p in capture.custody_root.glob("shared-transport-*.json")
        ]
        self.assertTrue(transports)
        for transport in transports:
            argv = transport["argv"]
            self.assertIn(".", argv[argv.index("--now") + 1])

    def test_real_cross_second_namespace_brackets_settle_without_invented_points(self):
        self.real_clocks()
        plan, argv, logical = self.plan(["/bin/sleep", "1.2"], bind_root=True)
        session, capture = self.claim(plan)
        observation = self.run_process(capture, plan, argv, logical)
        self.assertEqual(observation.exit_code, 0)
        _terminal_custody_capture(session, plan, capture, self.enrollment)
        own = next(iter(self.snapshot()["allocations"].values()))
        self.assertIsNotNone(own["terminal"])
        self.assertEqual(own["terminal"]["result"]["launched"], 1)
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 0)
        attempt = next(iter(own["attempts"].values()))
        for bracket in (
            attempt["evidence"]["created_at"],
            attempt["closure"]["ended_at"],
        ):
            self.assertEqual(bracket["schema"], "quartermaster-time-interval/1")
            self.assertLessEqual(bracket["lower"], bracket["upper"])
            self.assertIn(".", bracket["upper"])
        material = json.loads(
            (capture.custody_root / "shared-admission-creation.json").read_bytes()
        )
        closure = json.loads(
            (
                capture.custody_root / "shared-admission-namespace-closure.json"
            ).read_bytes()
        )
        self.assertEqual(material["before"]["boot_id"], material["after"]["boot_id"])
        self.assertLessEqual(
            material["before"]["monotonic_ns"], material["after"]["monotonic_ns"]
        )
        self.assertEqual(
            attempt["evidence"]["created_at"]["lower"], material["before"]["utc"]
        )
        self.assertEqual(
            attempt["evidence"]["created_at"]["upper"], material["after"]["utc"]
        )
        self.assertEqual(
            attempt["closure"]["ended_at"]["upper"], closure["observed_at"]
        )

    def lose_reply(self, verb):
        original = subprocess.run
        lost = False

        def run(argv, **kwargs):
            nonlocal lost
            reply = original(argv, **kwargs)
            if not lost and argv[0] == prior.CLI and argv[1:3] == ["admission", verb]:
                lost = True
                return subprocess.CompletedProcess(
                    argv, reply.returncode, b"", reply.stderr
                )
            return reply

        return mock.patch.object(subprocess, "run", side_effect=run)

    def lost_prelaunch(self, verb):
        self.real_clocks()
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        with self.lose_reply(verb):
            observation = self.run_process(capture, plan, argv, logical)
        self.assertIsNone(observation.launch_attempted_at)
        terminal = session.claim_process(plan)
        self.assertEqual(terminal.completion["invocation_state"], "not-invoked")
        snap = self.snapshot()
        own = next(iter(snap["allocations"].values()))
        self.assertEqual(own["terminal"]["result"]["launched"], 0)
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 0)
        before = snap["records"]
        self.enrollment.reconcile_session(session)
        self.assertEqual(self.snapshot()["records"], before)

    def test_lost_reserve_reply_closes_positive_prechild_right(self):
        self.lost_prelaunch("reserve")

    def test_lost_prepare_reply_recovers_committed_permit_without_launch(self):
        self.lost_prelaunch("prepare-launch")

    def lost_postlaunch(self, verb):
        self.real_clocks()
        plan, argv, logical = self.plan(["/bin/sleep", "0.3"], bind_root=True)
        session, capture = self.claim(plan)
        with self.lose_reply(verb):
            observation = self.run_process(capture, plan, argv, logical)
            _terminal_custody_capture(session, plan, capture, self.enrollment)
        self.assertEqual(observation.exit_code, 0)
        self.enrollment.reconcile_session(session)
        snap = self.snapshot()
        self.assertEqual(
            snap["pools"]["fixture-pool"],
            {"slots": 0, "windows": {"fixture-window": {"spent": 1, "outstanding": 0}}},
        )
        before = snap["records"]
        self.enrollment.reconcile_session(session)
        self.assertEqual(self.snapshot()["records"], before)
        self.assertTrue(list(capture.custody_root.glob("shared-control-fault-*.json")))

    def test_lost_created_reply_finishes_native_capture_and_recovers_one_debit(self):
        self.lost_postlaunch("record-launch")

    def test_lost_closed_reply_recovers_without_reopening_native_tree(self):
        self.lost_postlaunch("close-launch")

    def test_lost_settled_reply_recovers_exact_terminal_without_double_release(self):
        self.lost_postlaunch("settle")

    def test_bounded_same_pidfd_wait_retains_late_death_observation(self):
        import threading
        from caplab.revbench.process_tree import ProcessWitness

        self.real_clocks()
        plan, _, _ = self.plan()
        _, capture = self.claim(plan)
        gate = self.enrollment.capture(capture)
        child = subprocess.Popen(["/bin/sleep", "5"])
        self.addCleanup(lambda: child.poll() is None and child.kill())
        gate.namespace_witness = ProcessWitness.open(child.pid)
        gate.observe_liveness()
        timer = threading.Timer(0.01, child.terminate)
        timer.start()
        try:
            gate.close_namespace_observation(deadline=time.monotonic() + 0.05)
            child.wait(timeout=2)
        finally:
            timer.join()
            if gate.namespace_witness is not None:
                gate.namespace_witness.close()
        self.assertTrue(
            (capture.custody_root / "shared-admission-namespace-closure.json").exists()
        )
        # Component pidfd control; this ordinary child is never submitted as
        # native namespace quiescence or a synthetic settlement receipt.

    def test_containment_argv_change_refuses_before_shared_home_or_spawn(self):
        plan, argv, _ = self.plan()
        _, capture = self.claim(plan)
        with self.assertRaisesRegex(LiveExecutionCustodyError, "containment_mismatch"):
            self.enrollment.capture(capture).prepare(argv + ["changed"])
        self.assertFalse(Path(self.document["home"]).exists())
        self.assertFalse(capture._closed)

    def test_missing_death_on_parent_cannot_settle_a_real_closed_namespace(self):
        self.real_clocks()
        plan, argv, logical = self.plan(["/bin/sleep", "0.3"], bind_root=True)
        argv.remove("--die-with-parent")
        plan["containment_argv_sha256"] = sha256_hex(canonical_json(argv))
        session, capture = self.claim(plan)
        self.assertEqual(self.run_process(capture, plan, argv, logical).exit_code, 0)
        _terminal_custody_capture(session, plan, capture, self.enrollment)
        result = self.enrollment.capture(session.claim_process(plan)).reconcile(
            session.claim_process(plan).completion
        )
        self.assertEqual(result["code"], "tree_containment_unproved")
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 1)

    def test_sidecar_and_foreign_input_conflicts_fail_without_overwrite(self):
        plan, _, _ = self.plan()
        _, capture = self.claim(plan)
        gate = self.enrollment.capture(capture)
        path = capture.custody_root / "component-input.json"
        gate._retain_list(path.name, b"original foreign bytes")
        with self.assertRaisesRegex(LiveExecutionCustodyError, "custody_conflict"):
            gate._retain_list(path.name, b"changed foreign bytes")
        self.assertEqual(path.read_bytes(), b"original foreign bytes")
        shared._retain(capture.custody_root, "component-sidecar.json", {"a": 1})
        with self.assertRaisesRegex(LiveExecutionCustodyError, "custody_conflict"):
            shared._retain(capture.custody_root, "component-sidecar.json", {"a": 2})
        self.assertEqual(
            json.loads((capture.custody_root / "component-sidecar.json").read_bytes()),
            {"a": 1},
        )

    def policy_enrollment(self, policy, *, pinned=True):
        path = self.root / "policy-successor.json"
        path.write_bytes(canonical_json(policy))
        doc = dict(
            self.document,
            policy_path=str(path),
            policy_sha256=sha256_hex(path.read_bytes()),
        )
        if pinned:
            cap = json.loads(
                subprocess.check_output([prior.CLI, "admission", "capabilities"])
            )
            doc.update(
                schema_version="caplab-shared-admission-enrollment/2",
                sdk_source_tree_sha256=cap["source_tree_sha256"],
            )
        return shared.SharedAdmissionEnrollment(doc)

    def test_pinned_sdk2_rolling_policy_binds_profile_and_ages_from_latest_birth(self):
        self.real_clocks()
        policy = json.loads(Path(self.document["policy_path"]).read_bytes())
        policy["schema"] = "quartermaster-shared-admission-policy/2"
        policy["charge_reader"]["kind"] = "request-max-slots"
        original = policy["launch_budgets"][0]["windows"][0]
        policy["launch_budgets"][0]["windows"] = [
            dict(
                window_id="short",
                kind="rolling",
                duration_seconds=2,
                limit=2,
                reserve=0,
                caller_limits=original["caller_limits"],
            ),
            dict(
                window_id="long",
                kind="rolling",
                duration_seconds=10,
                limit=2,
                reserve=0,
                caller_limits=original["caller_limits"],
            ),
        ]
        self.enrollment = self.policy_enrollment(policy)
        plan, argv, logical = self.plan(["/bin/sleep", "0.3"], bind_root=True)
        session, capture = self.claim(plan)
        self.assertEqual(self.run_process(capture, plan, argv, logical).exit_code, 0)
        _terminal_custody_capture(session, plan, capture, self.enrollment)
        snap = self.snapshot()
        own = next(iter(snap["allocations"].values()))
        self.assertEqual(own["record"]["profile_id"], "caplab-codex-main")
        self.assertEqual(own["record"]["host"], "fixture-host")
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 0)
        attempt = next(iter(own["attempts"].values()))
        at = datetime.datetime.fromisoformat(attempt["evidence"]["created_at"]["upper"])
        aged = (
            (at + datetime.timedelta(seconds=3))
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
        snap = json.loads(
            subprocess.check_output(
                [
                    prior.CLI,
                    "admission",
                    "status",
                    "--home",
                    self.document["home"],
                    "--home-id",
                    "fixture-home",
                    "--now",
                    aged,
                ]
            )
        )
        self.assertEqual(
            snap["pools"]["fixture-pool"]["windows"],
            {
                "short": {"spent": 0, "outstanding": 0},
                "long": {"spent": 1, "outstanding": 0},
            },
        )

    def test_fixed_deadline_incompatible_refuses_without_claim_or_home(self):
        policy = json.loads(Path(self.document["policy_path"]).read_bytes())
        policy["launch_budgets"][0]["windows"][0]["end"] = "2026-12-31T23:59:59Z"
        enrollment = self.policy_enrollment(policy)
        with self.assertRaisesRegex(LiveExecutionCustodyError, "deadline_incompatible"):
            enrollment.validate_deadline("2027-01-01T00:00:00Z")
        enrollment.validate_deadline("2026-12-31T23:59:59Z")  # fixed fit is inclusive
        self.assertFalse(Path(self.document["home"]).exists())
        self.assertEqual(list(self.root.glob("revbench-live-effects/effects/*")), [])

    def test_sdk_source_pin_mismatch_refuses_without_claim_or_home(self):
        doc = dict(
            self.document,
            schema_version="caplab-shared-admission-enrollment/2",
            sdk_source_tree_sha256="sha256:" + "0" * 64,
        )
        with self.assertRaisesRegex(LiveExecutionCustodyError, "sdk_pin_changed"):
            shared.SharedAdmissionEnrollment(doc)
        self.assertFalse(Path(doc["home"]).exists())

    def test_bad_monotonic_birth_bracket_closes_incident_but_keeps_one_timing_debit(
        self,
    ):
        self.real_clocks()
        plan, argv, logical = self.plan(["/bin/sleep", "0.3"], bind_root=True)
        session, capture = self.claim(plan)
        sample = shared._clock_sample
        calls = 0

        def faulty_clock():
            nonlocal calls
            calls += 1
            fact = sample()
            if calls == 2:
                fact["monotonic_ns"] = (
                    0  # clock instrument fault, not a creation oracle
                )
            return fact

        with mock.patch.object(shared, "_clock_sample", side_effect=faulty_clock):
            self.assertEqual(
                self.run_process(capture, plan, argv, logical).exit_code, 0
            )
        _terminal_custody_capture(session, plan, capture, self.enrollment)
        snap = self.snapshot()
        own = next(iter(snap["allocations"].values()))
        self.assertEqual(
            own["counts"],
            {"known_created": 1, "possible_unknown": 0, "creation_time_unknown": 1},
        )
        self.assertEqual(own["terminal"]["kind"], "reconciled")
        self.assertEqual(
            snap["pools"]["fixture-pool"],
            {"slots": 0, "windows": {"fixture-window": {"spent": 0, "outstanding": 1}}},
        )
        before = snap["records"]
        self.enrollment.reconcile_session(session)
        self.assertEqual(self.snapshot()["records"], before)

    def test_expired_observation_bound_never_fabricates_pidfd_death(self):
        from caplab.revbench.process_tree import ProcessWitness

        self.real_clocks()
        plan, _, _ = self.plan()
        _, capture = self.claim(plan)
        gate = self.enrollment.capture(capture)
        child = subprocess.Popen(["/bin/sleep", "5"])
        try:
            gate.namespace_witness = ProcessWitness.open(child.pid)
            gate.observe_liveness()
            gate.close_namespace_observation(deadline=time.monotonic() - 1)
            self.assertIsNone(child.poll())
            self.assertFalse(
                (
                    capture.custody_root / "shared-admission-namespace-closure.json"
                ).exists()
            )
        finally:
            child.terminate()
            child.wait(timeout=2)

    def test_real_sdk_busy_refuses_launch_and_preserves_positive_prechild_completion(
        self,
    ):
        import fcntl
        import threading

        self.real_clocks()
        subprocess.check_call(
            [
                prior.CLI,
                "admission",
                "configure",
                "--home",
                self.document["home"],
                "--home-id",
                "fixture-home",
                "--policy",
                self.document["policy_path"],
            ],
            stdout=subprocess.DEVNULL,
        )
        lock = open(Path(self.document["home"]) / "admissions.lock", "a+")
        fcntl.flock(lock, fcntl.LOCK_EX)
        timer = None
        original = subprocess.run

        def contended(argv, **kwargs):
            nonlocal timer
            if argv[0] == prior.CLI and argv[1:3] == ["admission", "reserve"]:
                timer = threading.Timer(6, lambda: fcntl.flock(lock, fcntl.LOCK_UN))
                timer.start()
            return original(argv, **kwargs)

        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        try:
            with mock.patch.object(subprocess, "run", side_effect=contended):
                observation = self.run_process(capture, plan, argv, logical)
            self.assertIsNone(observation.launch_attempted_at)
            self.assertEqual(
                session.claim_process(plan).completion["invocation_state"],
                "not-invoked",
            )
            faults = [
                json.loads(p.read_bytes())
                for p in capture.custody_root.glob("shared-control-fault-*.json")
            ]
            self.assertIn(
                "shared_admission_admission_busy", {f["code"] for f in faults}
            )
            snap = self.snapshot()
            self.assertEqual(snap["allocations"], {})
            self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 0)
        finally:
            if timer is not None:
                timer.join()
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()

    def test_same_prepared_attempt_replay_is_exit6_information_never_another_right(
        self,
    ):
        self.real_clocks()
        plan, argv, _ = self.plan()
        _, capture = self.claim(plan)
        gate = self.enrollment.capture(capture)
        self.assertTrue(gate.prepare(argv))
        before = self.snapshot()["records"]
        self.assertFalse(self.enrollment.capture(capture).prepare(argv))
        self.assertEqual(self.snapshot()["records"], before)
        transports = [
            json.loads(p.read_bytes())
            for p in capture.custody_root.glob("shared-transport-*.json")
        ]
        replay = [
            p
            for p in transports
            if p["verb"] == "prepare-launch" and p["exit_code"] == 6
        ]
        self.assertEqual(len(replay), 1)
        self.assertEqual(
            json.loads(bytes.fromhex(replay[0]["stdout_hex"]))["result"]["status"],
            "existing",
        )
        capture.shared_admission = gate
        codex._complete_before_launch(capture, "preflight-refused")
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 0)
