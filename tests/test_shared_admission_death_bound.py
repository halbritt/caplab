"""Real namespace death with no post-birth positive liveness sample."""

import json
import datetime
import unittest
from unittest import mock

from caplab.revbench import shared_admission as shared
from caplab.revbench.execution import _terminal_custody_capture
import tests.test_shared_admission as prior
import tests.test_shared_admission_review as review


@unittest.skipUnless(prior.CLI, "set CAPLAB_TEST_SHARED_QM to the installed SDK")
class DeathBoundTests(unittest.TestCase):
    setUp = prior.SharedAdmissionTests.setUp
    plan = prior.SharedAdmissionTests.plan
    claim = prior.SharedAdmissionTests.claim
    run_process = prior.SharedAdmissionTests.run_process
    snapshot = review.ReviewRegressionTests.snapshot

    def test_held_init_death_uses_real_precreation_bound_without_liveness_sample(self):
        self.clocks.close()
        plan, argv, logical = self.plan(["/bin/sleep", "0.3"], bind_root=True)
        session, capture = self.claim(plan)
        with mock.patch.object(shared.ProcessAdmission, "observe_liveness"):
            observation = self.run_process(capture, plan, argv, logical)
        self.assertEqual(observation.exit_code, 0)
        born = json.loads((capture.custody_root / "shared-admission-creation.json").read_bytes())
        ended = json.loads((capture.custody_root / "shared-admission-namespace-closure.json").read_bytes())
        self.assertIsNone(ended["last_alive_at"])
        self.assertIsNotNone(ended["ended_at"])
        self.assertEqual(ended["ended_at"]["lower"], born["before"]["utc"])
        self.assertEqual(ended["namespace_init"]["parent_pid"], born["pid"])
        _terminal_custody_capture(session, plan, capture, self.enrollment)
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"], {
            "slots": 0, "windows": {"fixture-window": {"spent": 1, "outstanding": 0}}})
        records = self.snapshot()["records"]
        self.enrollment.reconcile_session(session)
        self.assertEqual(self.snapshot()["records"], records)

    def test_unobserved_init_still_holds_with_positive_native_completion(self):
        self.clocks.close()
        plan, argv, logical = self.plan(["/bin/true"], bind_root=True)
        session, capture = self.claim(plan)
        with mock.patch.object(shared, "namespace_init", return_value=None):
            self.assertEqual(self.run_process(capture, plan, argv, logical).exit_code, 0)
        _terminal_custody_capture(session, plan, capture, self.enrollment)
        terminal = session.claim_process(plan)
        result = self.enrollment.capture(terminal).reconcile(terminal.completion)
        self.assertEqual(result["code"], "namespace_quiescence_unproved")
        self.assertFalse((capture.custody_root / "shared-admission-namespace-closure.json").exists())
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 1)

    def invalid_birth_clock(self, change):
        self.clocks.close()
        plan, argv, logical = self.plan(["/bin/sleep", "0.3"], bind_root=True)
        session, capture = self.claim(plan)
        clock = shared._clock_sample
        first = True

        def disturbed_clock():
            nonlocal first
            sample = clock()
            if first:
                first = False
                change(sample)
            return sample

        with mock.patch.object(shared, "_clock_sample", disturbed_clock), \
                mock.patch.object(shared.ProcessAdmission, "observe_liveness"):
            self.assertEqual(self.run_process(capture, plan, argv, logical).exit_code, 0)
        closure = json.loads((capture.custody_root / "shared-admission-namespace-closure.json").read_bytes())
        self.assertIsNone(closure["ended_at"])
        _terminal_custody_capture(session, plan, capture, self.enrollment)
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 1)

    def test_changed_boot_does_not_make_a_death_time_from_birth(self):
        self.invalid_birth_clock(lambda sample: sample.update(boot_id="another-boot"))

    def test_reversed_utc_does_not_make_a_death_time_from_birth(self):
        def forward(sample):
            sample["utc"] = (datetime.datetime.fromisoformat(sample["utc"])
                             + datetime.timedelta(days=1)).isoformat().replace("+00:00", "Z")
        self.invalid_birth_clock(forward)
