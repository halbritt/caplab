"""Actual Bubblewrap refusal-path regression: EOF must not release an aborted app."""
import os
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from caplab.revbench.process_tree import SandboxReadiness, ProcessProofUnavailable

class ReadinessAbortTests(unittest.TestCase):
    def trial(self, *, release=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readiness = SandboxReadiness()
            process = subprocess.Popen(['/usr/bin/bwrap', '--unshare-all', '--die-with-parent',
                '--new-session', '--ro-bind', '/', '/', '--bind', directory, directory,
                '--proc', '/proc', '--dev', '/dev', '--block-fd', str(readiness.block_reader),
                '--info-fd', str(readiness.info_writer), '--', '/bin/sh', '-c',
                f'touch {directory}/application-marker'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                pass_fds=readiness.pass_fds)
            try:
                readiness.child_started()
                witness = readiness.observe(process.pid, deadline=time.monotonic() + 3)
                # A separate held descriptor is exclusively fixture cleanup, not
                # an alternate production proof or numeric-PID death inference.
                backup = os.pidfd_open(witness.fact['pid'])
                try:
                    if release:
                        readiness.release()
                    else:
                        process.terminate()
                    process.wait(timeout=3)
                    readiness.close()
                    time.sleep(0.05)
                    self.assertEqual((root / 'application-marker').exists(), release)
                finally:
                    try:
                        signal.pidfd_send_signal(backup, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    os.close(backup)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=3)
                readiness.close()
                process.stderr.close()

    def test_reaped_sigterm_monitor_cannot_release_unapproved_application(self):
        self.trial()

    def test_explicit_release_runs_application(self):
        self.trial(release=True)
