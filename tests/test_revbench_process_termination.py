"""Process-group termination and failure cleanup of the live process runner, with no real signal.

``_terminate_process_group`` is the only place the live runner signals a process group.  Two
properties are pinned here, with every signalling and launch primitive intercepted:

* an identity that is not a plain integer greater than one - a mock's coerced value, a boolean,
  zero, a negative number - is refused *before* any signal or wait, because ``killpg(1, ...)``,
  ``killpg(0, ...)`` and ``killpg(-1, ...)`` name host-wide targets rather than an owned child;
* when the runner fails after a launch, the cleanup closes every owned resource even if signalling
  or closing itself fails, and the primary exception stays in the raised exception's chain.

Nothing here starts a process or signals one: ``subprocess.Popen`` is replaced by a fake that hands
back a scripted process, and ``os.killpg``/``os.kill`` record their arguments and never signal.
"""

from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from caplab.revbench.codex import CodexAdapterError, _terminate_process_group
from caplab.revbench.custody import FilesystemLiveExecutionRuntime, LiveExecutionCustodyError
from tests.test_revbench_external_token import process_claim, run_claimed

CHILD_PID = 424242
IDENTITY_CODE = "live_process_group_identity_invalid"


def chain(error: BaseException | None):
    """The exception and everything it was raised from or while handling."""

    seen = []
    while error is not None and all(error is not other for other in seen):
        seen.append(error)
        error = error.__cause__ or error.__context__
    return seen


class SignalGuardCase(unittest.TestCase):
    """Base case: every way of signalling a process is replaced for the duration of each test."""

    def setUp(self):
        self.signals: list[tuple[int, int]] = []
        self.killpg_script: list[BaseException | None] = []

        def killpg(pgid, signal_number):
            self.signals.append((pgid, signal_number))
            if self.killpg_script:
                action = self.killpg_script.pop(0)
                if action is not None:
                    raise action

        def forbidden(*args, **kwargs):
            raise AssertionError(f"unintercepted signal primitive called: {args!r}")

        for target, replacement in (
            ("os.killpg", killpg),
            ("os.kill", forbidden),
            ("signal.pthread_kill", forbidden),
            ("signal.raise_signal", forbidden),
        ):
            patcher = mock.patch(target, side_effect=replacement)
            patcher.start()
            self.addCleanup(patcher.stop)


class Pipe:
    """A real pipe end whose ``close`` releases the descriptor and then may raise."""

    def __init__(self, read_side: bool, error: BaseException | None):
        reader, writer = os.pipe()
        os.close(writer if read_side else reader)  # the child is simulated: nothing else holds the pipe
        self._file = os.fdopen(reader if read_side else writer, "rb" if read_side else "wb", buffering=0)
        self._error = error
        self.close_attempts = 0

    def fileno(self):
        return self._file.fileno()

    @property
    def closed(self):
        return self._file.closed

    def close(self):
        self.close_attempts += 1
        self._file.close()
        if self._error is not None:
            raise self._error


class FakeProcess:
    """A scripted child: a pid, a script of ``wait`` results, and pipes that can fail to close."""

    def __init__(self, pid, *, waits=(), close_errors=None):
        self.pid = pid
        self.waits: list[float | None] = []
        self._script = list(waits)
        close_errors = close_errors or {}
        self.stdin = Pipe(False, close_errors.get("stdin"))
        self.stdout = Pipe(True, close_errors.get("stdout"))
        self.stderr = Pipe(True, close_errors.get("stderr"))

    def release(self):
        for pipe in (self.stdin, self.stdout, self.stderr):
            if not pipe.closed:
                pipe._file.close()

    def wait(self, timeout=None):
        self.waits.append(timeout)
        action = self._script.pop(0) if self._script else 0
        if isinstance(action, BaseException):
            raise action
        return action


class TerminateProcessGroupTests(SignalGuardCase):
    def test_an_identity_that_is_not_a_plain_integer_above_one_is_refused_before_any_signal_or_wait(self):
        hostile = {
            "mock": mock.MagicMock(),
            "mock int": mock.MagicMock(**{"__int__.return_value": 4242}),
            "one": 1,
            "zero": 0,
            "negative": -1,
            "very negative": -4242,
            "true": True,
            "false": False,
            "float": 4242.0,
            "string": "4242",
            "bytes": b"4242",
            "none": None,
            "int subclass": type("Pid", (int,), {})(4242),
        }
        for name, pid in hostile.items():
            for force in (False, True):
                with self.subTest(name, force=force):
                    process = FakeProcess(pid)
                    self.addCleanup(process.release)
                    with self.assertRaisesRegex(CodexAdapterError, f"^{IDENTITY_CODE}$"):
                        _terminate_process_group(process, force=force)
                    self.assertEqual(self.signals, [])
                    self.assertEqual(process.waits, [])

    def test_a_valid_group_gets_term_then_waits_and_kills_only_after_a_timeout(self):
        graceful = FakeProcess(CHILD_PID)
        self.addCleanup(graceful.release)
        _terminate_process_group(graceful)
        self.assertEqual((self.signals, graceful.waits), ([(CHILD_PID, signal.SIGTERM)], [1]))
        self.signals.clear()
        stubborn = FakeProcess(CHILD_PID, waits=[subprocess.TimeoutExpired("child", 1)])
        self.addCleanup(stubborn.release)
        _terminate_process_group(stubborn)
        self.assertEqual(self.signals, [(CHILD_PID, signal.SIGTERM), (CHILD_PID, signal.SIGKILL)])
        self.assertEqual(stubborn.waits, [1])

    def test_a_forced_termination_kills_once_without_waiting(self):
        process = FakeProcess(CHILD_PID)
        self.addCleanup(process.release)
        _terminate_process_group(process, force=True)
        self.assertEqual((self.signals, process.waits), ([(CHILD_PID, signal.SIGKILL)], []))

    def test_a_group_that_is_already_gone_is_not_an_error_and_is_not_waited_for(self):
        for force in (False, True):
            with self.subTest(force=force):
                self.signals.clear()
                self.killpg_script[:] = [ProcessLookupError()]
                process = FakeProcess(CHILD_PID)
                self.addCleanup(process.release)
                _terminate_process_group(process, force=force)
                self.assertEqual(self.signals, [(CHILD_PID, signal.SIGKILL if force else signal.SIGTERM)])
                self.assertEqual(process.waits, [])
        # A group that disappears between TERM and the kill that follows a timeout is also fine.
        self.signals.clear()
        self.killpg_script[:] = [None, ProcessLookupError()]
        process = FakeProcess(CHILD_PID, waits=[subprocess.TimeoutExpired("child", 1)])
        self.addCleanup(process.release)
        _terminate_process_group(process)
        self.assertEqual(len(self.signals), 2)

    def test_any_other_signalling_failure_is_not_swallowed(self):
        self.killpg_script[:] = [PermissionError("not ours")]
        process = FakeProcess(CHILD_PID)
        self.addCleanup(process.release)
        with self.assertRaises(PermissionError):
            _terminate_process_group(process)


class OwnedProcessFailureCleanupTests(SignalGuardCase):
    """``_run_owned_process`` after a launch whose handling then fails (the credential check raises)."""

    class Primary(Exception):
        pass

    def fresh_runtime(self):
        """A new custody root, so each scenario claims its own never-launched process slot."""

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        ledger = Path(temporary.name) / "ledger"
        ledger.mkdir(mode=0o700)
        return FilesystemLiveExecutionRuntime(ledger)

    def credential_that_fails(self, primary):
        class Credential:
            descriptor = -1

            def stream_quarantine(self_inner):
                raise primary  # raised after launch, while the child's output pipes are open

            def assert_streams_safe(self_inner, stdout, stderr):
                raise AssertionError("the run must not reach its stream check")

        return Credential()

    def run_failing(self, process, *, primary=None, popen_error=None):
        """Run the owned-process path with a scripted child and return (error, capture)."""

        primary = primary or self.Primary("primary failure")
        runtime = self.fresh_runtime()
        plan, intent = process_claim(runtime, ["/usr/bin/true"])
        with runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            self.addCleanup(process.release)
            with mock.patch("caplab.revbench.codex.subprocess.Popen", return_value=process) as popen:
                with self.assertRaises(BaseException) as caught:
                    run_claimed(capture, ["/usr/bin/true"], credential=self.credential_that_fails(primary))
            self.assertEqual(popen.call_count, 1)
            with self.assertRaisesRegex(LiveExecutionCustodyError, "^process_capture_closed$"):
                capture.write_stdout(b"x")  # the capture was closed by the cleanup
            for name in ("stdin", "stdout", "stderr"):
                self.assertTrue(getattr(process, name).closed, f"the {name} pipe was left open")
            return caught.exception, primary

    def test_cleanup_after_a_failure_terminates_the_group_closes_everything_and_reraises_the_primary(self):
        process = FakeProcess(CHILD_PID)
        error, primary = self.run_failing(process)
        self.assertIs(error, primary)
        self.assertEqual((self.signals, process.waits), ([(CHILD_PID, signal.SIGTERM)], [1, 1]))

    def test_a_child_that_ignores_term_is_killed_and_reaped_after_the_failure(self):
        # TERM's own wait times out (it escalates inside the helper); the cleanup's wait then times out
        # too, so the cleanup forces a kill and waits without a deadline.
        process = FakeProcess(
            CHILD_PID, waits=[subprocess.TimeoutExpired("c", 1), subprocess.TimeoutExpired("c", 1), 0])
        error, primary = self.run_failing(process)
        self.assertIs(error, primary)
        self.assertEqual(
            self.signals,
            [(CHILD_PID, signal.SIGTERM), (CHILD_PID, signal.SIGKILL), (CHILD_PID, signal.SIGKILL)],
        )
        self.assertEqual(process.waits, [1, 1, None])  # reaped without a deadline after the forced kill

    def test_a_missing_group_is_tolerated_during_cleanup(self):
        self.killpg_script[:] = [ProcessLookupError()]
        process = FakeProcess(CHILD_PID)
        error, primary = self.run_failing(process)
        self.assertIs(error, primary)
        self.assertEqual(self.signals, [(CHILD_PID, signal.SIGTERM)])
        self.assertEqual(process.waits, [1])

    def test_failures_while_signalling_or_closing_still_close_every_resource_and_keep_the_primary(self):
        cases = {
            "signal fails": dict(signal_error=PermissionError("denied")),
            "output pipe close fails": dict(close_errors={"stdout": OSError("stdout close")}),
            "error pipe close fails": dict(close_errors={"stderr": OSError("stderr close")}),
            "both pipes fail to close": dict(
                close_errors={"stdout": OSError("stdout close"), "stderr": OSError("stderr close")}),
            "signal and close fail": dict(
                signal_error=PermissionError("denied"), close_errors={"stdout": OSError("stdout close")}),
        }
        for name, options in cases.items():
            with self.subTest(name):
                self.signals.clear()
                self.killpg_script[:] = [options["signal_error"]] if "signal_error" in options else []
                process = FakeProcess(CHILD_PID, close_errors=options.get("close_errors"))
                error, primary = self.run_failing(process)
                self.assertIn(primary, chain(error), "the primary failure must stay reachable")
                for name, failure in options.get("close_errors", {}).items():
                    self.assertEqual(getattr(process, name).close_attempts, 1, name)

    def test_an_invalid_child_identity_signals_nothing_and_still_closes_everything(self):
        for name, pid in {"mock": mock.MagicMock(), "init": 1, "group zero": 0, "negative": -1}.items():
            with self.subTest(name):
                self.signals.clear()
                process = FakeProcess(pid)
                error, primary = self.run_failing(process)
                self.assertEqual(self.signals, [])
                self.assertEqual(process.waits, [])  # neither a signal nor any wait on an unowned identity
                self.assertIn(primary, chain(error))
                self.assertEqual(str(error), IDENTITY_CODE)

    def test_bypassing_the_pre_launch_check_fails_at_the_launch_primitive_without_any_signal(self):
        """A mutant that skips the closure check reaches ``Popen``; here that is an immediate failure."""

        runtime = self.fresh_runtime()
        plan, intent = process_claim(runtime, ["/usr/bin/true"])
        with runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            with mock.patch(
                "caplab.revbench.codex.subprocess.Popen", side_effect=AssertionError("unexpected process launch")
            ) as popen:
                with mock.patch(
                    "caplab.revbench.codex._host_closure_verified", return_value=True
                ):  # the preflight is bypassed on purpose
                    with self.assertRaisesRegex(AssertionError, "unexpected process launch"):
                        run_claimed(capture, ["/usr/bin/true"], host_closure={"pins": "unused"})
            popen.assert_called_once()
            self.assertEqual(self.signals, [])
            capture.close()


if __name__ == "__main__":
    unittest.main()
