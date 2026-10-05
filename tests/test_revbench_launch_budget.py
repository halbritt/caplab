"""The launch boundary re-reads its budgets after the host-closure check, and never renews them.

The pre-launch host-closure check reads files, parses ELF and cache data and writes a durable
record, so it takes time.  Retained authority (a UTC deadline) and the absolute monotonic total
deadline both keep running meanwhile.  These controls drive ``_run_owned_process`` with controlled
UTC and monotonic clocks and a verifier that advances them, and pin:

* both budgets are read again after the check and its record; if either ran out the check stays,
  the slot is consumed as ``not-invoked`` / ``authorization-expired`` and nothing is launched;
* when time was consumed but not all of it, the process runs and its stop bound is still the
  absolute total deadline (or the UTC authority translated once), not a fresh interval measured
  from the launch.

Nothing here starts or signals a process: ``Popen`` is replaced, ``os.killpg`` records only.
"""

from __future__ import annotations

import os
import signal
import tempfile
import unittest
from datetime import UTC, datetime as RealDatetime, timedelta
from pathlib import Path
from unittest import mock

from caplab.revbench import codex, host_closure
from caplab.revbench.custody import FilesystemLiveExecutionRuntime, RecoveredProcessCapture
from tests.support_host_closure import SyntheticHost
from tests.test_revbench_external_token import process_claim, run_claimed
from tests.test_revbench_process_termination import SignalGuardCase

ARGV = ["/synthetic-never-launched"]
CHILD_PID = 424242
START_UTC = RealDatetime(2098, 12, 31, 23, 59, 50, tzinfo=UTC)  # the plan's deadline is 2099-01-01T00:00:00Z
START_MONOTONIC = 100.0


class LongRunningChild:
    """A child that never exits by itself: open pipes, a scripted ``wait``, ``poll`` once terminated."""

    def __init__(self):
        self.pid = CHILD_PID
        self.terminated = False
        self._held = []  # write ends of the child's output pipes stay open: no EOF
        self.stdin, self.stdout, self.stderr = None, None, None

    def attach(self):
        reader_in, writer_in = os.pipe()
        os.close(reader_in)
        self.stdin = os.fdopen(writer_in, "wb", buffering=0)
        for name in ("stdout", "stderr"):
            reader, writer = os.pipe()
            self._held.append(writer)
            setattr(self, name, os.fdopen(reader, "rb", buffering=0))

    def poll(self):
        return 0 if self.terminated else None

    def wait(self, timeout=None):
        return 0

    def release(self):
        for stream in (self.stdin, self.stdout, self.stderr):
            if stream is not None and not stream.closed:
                stream.close()
        while self._held:
            os.close(self._held.pop())


class LaunchBudgetTests(SignalGuardCase):
    def setUp(self):
        super().setUp()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        ledger = root / "ledger"
        ledger.mkdir(mode=0o700)
        self.runtime = FilesystemLiveExecutionRuntime(ledger)
        host_root = root / "host"
        host_root.mkdir()
        self.host = SyntheticHost(host_root)
        self.closure = host_closure.capture_host_closure(SyntheticHost.EXECUTABLE, root=self.host.root)
        self.clock = {"utc": START_UTC, "mono": START_MONOTONIC, "tick": 0.0}
        self.launches = 0
        self.stops: list[tuple[int, int, float]] = []  # (group, signal, monotonic reading at the signal)
        self.child = LongRunningChild()
        self.addCleanup(self.child.release)

    # --- controlled time -----------------------------------------------------------------

    def patches(self, *, consumes_utc: float, consumes_mono: float, popen):
        clock = self.clock

        class Clock(RealDatetime):
            @classmethod
            def now(cls, tz=None):
                return clock["utc"]

        def monotonic():
            clock["mono"] += clock["tick"]
            return clock["mono"]

        def slow_verify(pinned):
            facts = host_closure.verify_host_closure(pinned, root=self.host.root, trusted_uid=os.getuid())
            clock["utc"] += timedelta(seconds=consumes_utc)
            clock["mono"] += consumes_mono
            return facts

        def killpg(group, signal_number):
            self.stops.append((group, signal_number, clock["mono"]))
            self.child.terminated = True

        def launch(argv, **kwargs):
            self.launches += 1
            clock["tick"] = 0.5  # time passes only once a process exists
            return popen(argv, **kwargs)

        return (
            mock.patch.object(codex, "datetime", Clock),
            mock.patch.object(codex.time, "monotonic", side_effect=monotonic),
            mock.patch.object(codex, "verify_host_closure", side_effect=slow_verify),
            mock.patch.object(codex.subprocess, "Popen", side_effect=launch),
            mock.patch("os.killpg", side_effect=killpg),
        )

    def run_boundary(self, *, consumes_utc, consumes_mono, popen, monotonic_deadline=110.0, closure=True):
        plan, intent = process_claim(self.runtime, ARGV)
        with self.runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            with capture:
                patches = self.patches(consumes_utc=consumes_utc, consumes_mono=consumes_mono, popen=popen)
                for patch in patches:
                    patch.start()
                try:
                    observation = run_claimed(
                        capture, ARGV, monotonic_deadline=monotonic_deadline,
                        host_closure=self.closure if closure else None)
                finally:
                    for patch in reversed(patches):
                        patch.stop()
            recovered = execution.claim_process(plan)
        return observation, recovered

    @staticmethod
    def never_launches(argv, **kwargs):
        raise AssertionError("a process launch was attempted")

    @staticmethod
    def spawn_fails(argv, **kwargs):
        raise OSError("synthetic: no process is started")

    # --- the recheck -----------------------------------------------------------------------

    def test_positive_headroom_after_the_check_still_launches_exactly_once(self):
        for closure in (True, False):
            with self.subTest(closure=closure):
                self.setUp()
                observation, recovered = self.run_boundary(
                    consumes_utc=1, consumes_mono=1, popen=self.spawn_fails, closure=closure)
                self.assertEqual(self.launches, 1)
                self.assertEqual((observation.termination, observation.invocation_state), ("spawn-failure", "not-invoked"))
                self.assertEqual(recovered.host_closure_check is not None, closure)

    def test_a_check_that_outlasts_the_utc_authority_consumes_the_slot_without_a_launch(self):
        observation, recovered = self.run_boundary(consumes_utc=11, consumes_mono=1, popen=self.never_launches)
        self.assertEqual(self.launches, 0)
        self.assertEqual((observation.termination, observation.invocation_state), ("authorization-expired", "not-invoked"))
        self.assertIsInstance(recovered, RecoveredProcessCapture)
        self.assertEqual(recovered.host_closure_check["result"], "verified")  # the check that ran is retained
        self.assertEqual(recovered.completion["launch_attempted_at"], None)

    def test_a_check_that_outlasts_the_monotonic_total_budget_consumes_the_slot_without_a_launch(self):
        observation, recovered = self.run_boundary(consumes_utc=1, consumes_mono=11, popen=self.never_launches)
        self.assertEqual(self.launches, 0)
        self.assertEqual(observation.termination, "authorization-expired")
        self.assertEqual(recovered.host_closure_check["result"], "verified")

    def test_a_check_that_outlasts_both_budgets_and_one_that_lands_exactly_on_them_launch_nothing(self):
        for utc, mono in ((11, 11), (10, 1), (1, 10)):
            with self.subTest(utc=utc, mono=mono):
                self.setUp()
                observation, recovered = self.run_boundary(consumes_utc=utc, consumes_mono=mono, popen=self.never_launches)
                self.assertEqual((self.launches, observation.termination), (0, "authorization-expired"))
                self.assertEqual(recovered.host_closure_check["result"], "verified")

    def test_an_expiry_found_before_the_check_runs_it_not_at_all(self):
        self.clock["mono"] = 111.0  # already past the absolute total deadline
        verified = []
        plan, intent = process_claim(self.runtime, ARGV)
        with self.runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            with capture:
                patches = self.patches(consumes_utc=0, consumes_mono=0, popen=self.never_launches)
                for patch in patches:
                    patch.start()
                try:
                    with mock.patch.object(codex, "verify_host_closure", side_effect=lambda *_: verified.append(1)):
                        observation = run_claimed(capture, ARGV, monotonic_deadline=110.0, host_closure=self.closure)
                finally:
                    for patch in reversed(patches):
                        patch.stop()
            recovered = execution.claim_process(plan)
        self.assertEqual((observation.termination, verified, self.launches), ("authorization-expired", [], 0))
        self.assertIsNone(recovered.host_closure_check)  # nothing was checked, so nothing is claimed

    # --- the stop bound ---------------------------------------------------------------------

    def run_long_child(self, *, consumes, monotonic_deadline):
        self.child.attach()

        def popen(argv, **kwargs):
            return self.child

        return self.run_boundary(
            consumes_utc=consumes, consumes_mono=consumes, popen=popen, monotonic_deadline=monotonic_deadline)

    def first_term(self):
        terms = [stop for stop in self.stops if stop[1] == signal.SIGTERM]
        self.assertTrue(terms, "the child was never stopped")
        return terms[0][2]

    def test_partial_consumption_by_the_check_does_not_renew_the_absolute_total_deadline(self):
        # 10 s of total budget; the check takes 6; the 5 s per-process timeout would run to 111 if it
        # restarted after the check, but the total deadline is 110.  The UTC authority is far away, so
        # only the absolute total deadline can be what stops the child.
        self.clock["utc"] = START_UTC - timedelta(days=3650)
        observation, recovered = self.run_long_child(consumes=6, monotonic_deadline=110.0)
        self.assertEqual((self.launches, observation.termination), (1, "timeout"))
        # Exactly the absolute deadline.  A timeout restarted after the launch would stop at 110.5
        # (the half second the launch itself takes), and one measured from before the check at 111.5.
        self.assertEqual(self.first_term(), 110.0)
        self.assertEqual(recovered.host_closure_check["result"], "verified")

    def test_partial_consumption_does_not_renew_the_utc_authority_either(self):
        # No monotonic total budget to speak of, 10 s of UTC authority, 6 consumed: the authority ends at
        # 110 on the monotonic clock, not at launch + the 5 s per-process timeout (111).
        observation, _recovered = self.run_long_child(consumes=6, monotonic_deadline=1e9)
        self.assertEqual((self.launches, observation.termination), (1, "timeout"))
        self.assertEqual(self.first_term(), 110.0)  # not 110.5 (restarted at launch) or 111.5

    def test_the_per_process_timeout_still_counts_from_the_launch_when_the_budgets_are_larger(self):
        # Plenty of authority and total budget: the 5 s per-process timeout from the launch (106) rules.
        self.clock["utc"] = START_UTC - timedelta(days=3650)  # authority far away
        observation, _recovered = self.run_long_child(consumes=6, monotonic_deadline=1e9)
        self.assertEqual((self.launches, observation.termination), (1, "timeout"))
        self.assertEqual(self.first_term(), 111.5)  # launch at 106.5 plus the 5 s timeout

    def test_without_a_closure_the_same_absolute_bounds_apply_and_nothing_is_checked(self):
        self.child.attach()
        observation, recovered = self.run_boundary(
            consumes_utc=0, consumes_mono=0, popen=lambda argv, **kwargs: self.child,
            monotonic_deadline=103.0, closure=False)
        self.assertEqual((self.launches, observation.termination), (1, "timeout"))
        self.assertEqual(self.first_term(), 103.0)  # the total deadline, tighter than the 5 s timeout
        self.assertIsNone(recovered.host_closure_check)


if __name__ == "__main__":
    unittest.main()
