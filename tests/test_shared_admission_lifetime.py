"""Readiness controls using real bwrap, native custody and the installed SDK."""

import datetime
import contextlib
import json
import os
import time
import unittest
from unittest import mock

from caplab.revbench import shared_admission as shared
from caplab.revbench.codex import _run_owned_process
from caplab.revbench.process_tree import SandboxReadiness, ProcessProofUnavailable
from caplab.revbench.execution import _terminal_custody_capture
import tests.test_shared_admission as prior
import tests.test_shared_admission_review as review


@unittest.skipUnless(prior.CLI, "set CAPLAB_TEST_SHARED_QM to the installed SDK")
class ReadinessAdmissionTests(unittest.TestCase):
    setUp = prior.SharedAdmissionTests.setUp
    plan = prior.SharedAdmissionTests.plan
    claim = prior.SharedAdmissionTests.claim
    snapshot = review.ReviewRegressionTests.snapshot

    @contextlib.contextmanager
    def readiness(self, *, unobserved_init=False):
        readiness = SandboxReadiness()
        try:
            yield readiness
        finally:
            try:
                readiness.close()
            except ProcessProofUnavailable as error:
                if not unobserved_init:
                    raise
                # ADR0068: a missing descriptor is not successful abort cleanup.
                # The block writer must remain open, never EOF-release the app.
                self.assertEqual(str(error), 'sandbox_abort_init_unproved')
                self.assertFalse(readiness.released)
                self.assertGreaterEqual(readiness.block_writer, 0)
                os.fstat(readiness.block_writer)
                # Fixture-only disposal after the actual local monitor's forced
                # group kill. This grants no Q fact or shared terminal effect.
                for name in ('block_reader', 'block_writer', 'info_reader', 'info_writer'):
                    descriptor = getattr(readiness, name)
                    if descriptor >= 0:
                        os.close(descriptor)
                        setattr(readiness, name, -1)

    def run_readiness(self, command, *, corrupt_info=False, pidfd_unavailable=False,
                      expire_barrier=False, deadline=float("inf"), writable_marker_root=None):
        self.clocks.close()
        with self.readiness(unobserved_init=corrupt_info or pidfd_unavailable) as readiness:
            original, _, logical = self.plan(command, bind_root=True)
            normalized = ["/usr/bin/bwrap", "--unshare-all", "--die-with-parent",
                          "--new-session", "--block-fd", "{sandbox_block_fd}",
                          "--info-fd", "{sandbox_info_fd}",
                          "--ro-bind", "/", "/",
                          *(["--bind", str(writable_marker_root), str(writable_marker_root)] if writable_marker_root is not None else []),
                          "--", *logical]
            plan = {**original, "containment_argv_sha256":
                    shared.sha256_hex(shared.canonical_json(normalized))}
            session, capture = self.claim(plan)
            capture.shared_admission = self.enrollment.capture(capture)
            fds = dict(zip(("{sandbox_block_fd}", "{sandbox_info_fd}"), readiness.pass_fds))
            actual = [str(fds[t]) if t in fds else t for t in normalized]
            if corrupt_info:
                # Real bytes on the owned pipe, not a fabricated positive pidfd.
                os.write(readiness.info_writer, b"invalid-prefix")
            # These are OS/clock boundaries. No positive kernel observation is
            # mocked, and native capture/home transactions remain real.
            import contextlib
            with contextlib.ExitStack() as faults:
                if pidfd_unavailable:
                    faults.enter_context(mock.patch("os.pidfd_open", side_effect=OSError("unsupported")))
                if expire_barrier:
                    # Advance the supervisor's UTC source only after the actual
                    # kernel pidfd acquisition. No internal budget helper is mocked.
                    from caplab.revbench import codex
                    real_open = os.pidfd_open
                    acquired = False
                    def open_pidfd(*args):
                        nonlocal acquired
                        descriptor = real_open(*args)
                        acquired = True
                        return descriptor
                    class Clock(datetime.datetime):
                        @classmethod
                        def now(cls, tz=None):
                            if acquired:
                                return datetime.datetime.fromisoformat(
                                    plan["execution_deadline_at"].replace("Z", "+00:00"))
                            return datetime.datetime.now(tz)
                    faults.enter_context(mock.patch("os.pidfd_open", side_effect=open_pidfd))
                    faults.enter_context(mock.patch.object(codex, "datetime", Clock))
                try:
                    observation = _run_owned_process(
                    actual, normalized, logical, b"", contained_environment={},
                    runtime_ref_sha256="d" * 64, apparatus_sha256="4" * 64,
                    command_ref_sha256="e" * 64, credential_profile_id="caplab-openai-revbench",
                    credential_profile_sha256="f" * 64, pass_fds=readiness.pass_fds,
                    capture=capture, credential=None, monotonic_deadline=deadline,
                    sandbox_readiness=readiness)
                except (ProcessProofUnavailable, prior.codex.CodexAdapterError):
                    if not (corrupt_info or pidfd_unavailable or expire_barrier):
                        raise
                    self.assertFalse(readiness.released)
                    observation = None
            _terminal_custody_capture(session, plan, capture, self.enrollment)
            snap = self.snapshot()
            self.enrollment.reconcile_session(session)
            self.assertEqual(self.snapshot()["records"], snap["records"])
            root = capture.custody_root
            born = json.loads((root / "shared-admission-creation.json").read_bytes())
            closure = root / "shared-admission-namespace-closure.json"
            return observation, snap, born, (json.loads(closure.read_bytes())
                                           if closure.exists() else None)

    def test_instant_child_acquires_pidfd_before_release_and_settles(self):
        observation, snap, born, closed = self.run_readiness(["/bin/true"])
        self.assertEqual(observation.exit_code, 0)
        self.assertEqual(closed["basis"], "owned-namespace-init-pidfd-death")
        self.assertEqual(closed["namespace_init"]["parent_pid"], born["pid"])
        self.assertEqual(closed["namespace_init"]["namespace_pids"][-1], 1)
        self.assertIsNotNone(closed["ended_at"])
        self.assertEqual(snap["pools"]["fixture-pool"], {
            "slots": 0, "windows": {"fixture-window": {"spent": 1, "outstanding": 0}}})

    def test_expired_barrier_in_full_supervisor_does_not_run_application(self):
        marker = self.root / 'application-marker'
        observation, snap, born, closed = self.run_readiness(
            ['/bin/sh', '-c', 'touch ' + str(marker)], expire_barrier=True,
            writable_marker_root=self.root)
        self.assertIsNone(observation)
        # The regression is an EOF-triggered child after the supervisor returns;
        # observe that asynchronous cut point before disposing the fixture.
        time.sleep(0.05)
        self.assertFalse(marker.exists())
        self.assertEqual(born['outcome'], 'created')
        self.assertEqual(snap['pools']['fixture-pool']['slots'], 1)
        self.assertEqual(snap['pools']['fixture-pool']['windows']['fixture-window']['spent'], 1)

    def test_real_child_exec_failure_counts_one_and_closes_namespace(self):
        observation, snap, _, closed = self.run_readiness(["/no-such-contained-executable"])
        self.assertNotEqual(observation.exit_code, 0)
        self.assertEqual(observation.invocation_state, "invoked")
        self.assertIn(b"execvp", observation.stderr)
        self.assertIsNotNone(closed)
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 0)
        self.assertEqual(snap["pools"]["fixture-pool"]["windows"]["fixture-window"]["spent"], 1)

    def test_invalid_info_never_releases_application_or_closes_on_monitor_exit(self):
        observation, snap, born, closed = self.run_readiness(["/bin/true"], corrupt_info=True)
        self.assertIsNone(observation)
        self.assertEqual(born["outcome"], "created")
        self.assertIsNone(closed)
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 1)
        self.assertEqual(snap["pools"]["fixture-pool"]["windows"]["fixture-window"]["spent"], 1)

    def test_unavailable_pidfd_after_real_creation_keeps_uncertainty(self):
        observation, snap, born, closed = self.run_readiness(["/bin/true"], pidfd_unavailable=True)
        self.assertIsNone(observation)
        self.assertEqual(born["outcome"], "created")
        self.assertIsNone(closed)
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 1)
        self.assertEqual(snap["pools"]["fixture-pool"]["windows"]["fixture-window"]["spent"], 1)

    def test_expired_post_observation_authority_does_not_release_application(self):
        observation, snap, born, _ = self.run_readiness(["/bin/true"], expire_barrier=True)
        self.assertIsNone(observation)
        self.assertEqual(born["outcome"], "created")
        # No terminal native completion is fabricated after startup interruption.
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 1)

    def test_timeout_observes_pidfd_death_without_renewing_execution_deadline(self):
        start = time.monotonic()
        observation, snap, _, closed = self.run_readiness(
            ["/bin/sleep", "30"], deadline=start + 3)
        self.assertEqual(observation.termination, "timeout")
        self.assertLess(time.monotonic() - start, 12)
        self.assertIsNotNone(closed)
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 0)

    def test_background_descendant_requires_namespace_death_after_monitor_completion(self):
        observation, snap, _, closed = self.run_readiness(
            ["/bin/sh", "-c", "sleep 30 >/dev/null 2>&1 & exit 0"])
        self.assertEqual(observation.exit_code, 0)
        self.assertEqual(closed["basis"], "owned-namespace-init-pidfd-death")
        self.assertEqual(snap["pools"]["fixture-pool"]["slots"], 0)


class ReadinessPolicyTests(unittest.TestCase):
    def test_new_policy_requires_exact_registered_bytes_and_preserves_predecessors(self):
        import copy
        from caplab.revbench import codex, _core
        policy = codex.codex_native_shared_bundle_policy()
        self.assertEqual(_core.selected_bundle_policy(policy), policy)
        altered = copy.deepcopy(policy)
        altered["readiness_observation"]["post_monitor_timeout_ms"] = 999
        self.assertIsNone(_core.selected_bundle_policy(altered))
        external = codex.codex_native_external_bundle_policy()
        original = codex.codex_native_bundle_policy()
        self.assertEqual(_core.selected_bundle_policy(external), external)
        self.assertEqual(_core.selected_bundle_policy(original), original)
        for field in ["version_containment_argv_template", "review_containment_argv_template"]:
            argv = policy[field]
            index = argv.index("{sandbox_block_fd}")
            self.assertEqual(argv[index - 1], "--block-fd")
            self.assertEqual(argv[index + 1:index + 3], ["--info-fd", "{sandbox_info_fd}"])
            self.assertLess(index + 2, argv.index("--"))
            without = argv[:index - 1] + argv[index + 3:]
            self.assertEqual(without, external[field])

    def test_unobserved_pipe_cannot_release_application(self):
        with SandboxReadiness() as readiness:
            with self.assertRaisesRegex(ProcessProofUnavailable, "not_observed"):
                readiness.release()
            self.assertFalse(readiness.released)

    def test_context_closes_all_descriptors_when_setup_fails(self):
        with self.assertRaisesRegex(RuntimeError, "setup"):
            with SandboxReadiness() as readiness:
                fds = [readiness.block_reader, readiness.block_writer,
                       readiness.info_reader, readiness.info_writer]
                raise RuntimeError("setup")
        for descriptor in fds:
            with self.assertRaises(OSError):
                os.fstat(descriptor)


class ReadinessFactoryTests(unittest.TestCase):
    from tests import test_revbench_external_token as external
    setUp = external.DirectLaunchWiringTests.setUp
    bundle_for = external.DirectLaunchWiringTests.bundle_for
    launched_argv = external.DirectLaunchWiringTests.launched_argv

    def test_public_native_factory_passes_owned_fds_and_closes_descriptors(self):
        from caplab.revbench import codex
        _, launched, events, observation = self.launched_argv(
            codex.codex_native_shared_bundle_policy(), "codex_native_shared_bundle_policy")
        (argv, kwargs), = launched
        for option in ("--block-fd", "--info-fd"):
            fd = int(argv[argv.index(option) + 1])
            self.assertIn(fd, kwargs["pass_fds"])
            with self.assertRaises(OSError):
                os.fstat(fd)
        self.assertEqual(events, ["verify", "popen"])
        self.assertEqual(observation.termination, "spawn-failure")
