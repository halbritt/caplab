"""Known-secret gates protect prospective capture before durable writes."""

import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import caplab.process_capture as capture
from caplab.revbench.codex import ExactSecretStreamQuarantine


class ProcessCaptureQuarantineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / 'capture'

    def launch(self, code, factory, **kwargs):
        return capture.capture_process(
            [sys.executable, '-c', code], cwd=self.root, environment={},
            output_dir=self.output, max_stream_bytes=kwargs.pop('max_stream_bytes', 200000),
            timeout_seconds=kwargs.pop('timeout_seconds', 3),
            quarantine_factory=factory, **kwargs)

    def test_split_secret_never_reaches_durable_capture_and_child_is_reaped(self):
        secret = b'fabricated-secret-' + b'x' * 70000 + b'-end'
        processes = []
        real_popen = subprocess.Popen

        def observe(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            processes.append(process)
            return process

        with tempfile.TemporaryFile() as source:
            source.write(b'public prefix\n' + secret + b'public suffix\n')
            source.seek(0)
            fd = source.fileno()
            code = (f'import os,time\nwhile chunk := os.read({fd},4096):\n'
                    ' os.write(1,chunk)\ntime.sleep(30)\n')
            with patch.object(capture.subprocess, 'Popen', side_effect=observe):
                with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                    self.launch(code, lambda: ExactSecretStreamQuarantine((secret,)), pass_fds=(fd,))
            self.assertEqual(processes[0].poll(), -signal.SIGKILL)
            self.assertTrue(processes[0].stdout.closed)
            self.assertTrue(processes[0].stderr.closed)
            self.assertFalse(os.get_inheritable(fd))
            self.assertEqual(os.pread(fd, 14, 0), b'public prefix\n')
        self.assertFalse((self.output / 'capture.json').exists())
        for path in self.output.iterdir():
            self.assertNotIn(secret, path.read_bytes())

    def test_safe_binary_streams_keep_exact_bytes_at_combined_limit(self):
        stdout = b'\x00\xff\nabc'
        stderr = 'déf'.encode() + b'def'
        receipt = self.launch(
            f'import os; os.write(1,{stdout!r}); os.write(2,{stderr!r}); raise SystemExit(7)',
            lambda: ExactSecretStreamQuarantine((b'abcdef',)),
            max_stream_bytes=len(stdout) + len(stderr))
        self.assertEqual((self.output / 'native.stdout').read_bytes(), stdout)
        self.assertEqual((self.output / 'native.stderr').read_bytes(), stderr)
        self.assertEqual(receipt['return_code'], 7)
        self.assertTrue(receipt['streams_complete'])
        self.assertEqual(receipt['retained_stream_bytes'], len(stdout) + len(stderr))

    def test_transforming_gate_cannot_publish_a_raw_capture(self):
        class TransformingGate(ExactSecretStreamQuarantine):
            def feed(self, payload):
                return super().feed(payload.replace(b'public', b'edited'))

        with self.assertRaisesRegex(RuntimeError, '^quarantine changed raw stream$'):
            self.launch("print('public output')", lambda: TransformingGate((b'secret',)))
        self.assertFalse((self.output / 'capture.json').exists())

    def test_incomplete_guarded_capture_discards_overlap_without_receipt(self):
        for reason, code, options in (
            ('timeout', "import os,time; os.write(1,b'secret-token-'); time.sleep(30)",
             {'timeout_seconds': .2}),
            ('byte-limit', "import os; os.write(1,b'secret')", {'max_stream_bytes': 5}),
        ):
            with self.subTest(reason=reason):
                self.output = self.root / reason
                with self.assertRaisesRegex(RuntimeError, '^guarded capture incomplete: ' + reason + '$'):
                    self.launch(code, lambda: ExactSecretStreamQuarantine((b'secret-token-full',)), **options)
                self.assertFalse((self.output / 'capture.json').exists())
                self.assertEqual((self.output / 'native.stdout').read_bytes(), b'')

    def test_invalid_or_shared_gates_are_rejected_before_custody(self):
        shared = ExactSecretStreamQuarantine((b'secret',))
        for factory in (False, lambda: object(), lambda: shared):
            with self.subTest(factory=factory):
                with patch.object(capture.subprocess, 'Popen') as launch:
                    with self.assertRaises(ValueError):
                        self.launch('pass', factory)
                    launch.assert_not_called()
                self.assertFalse(self.output.exists())

    def test_factory_failure_abandons_already_created_gate(self):
        abandoned = []

        class ObservedGate(ExactSecretStreamQuarantine):
            def abandon(self):
                abandoned.append(True)
                super().abandon()

        gate = ObservedGate((b'secret',))
        with patch.object(capture.subprocess, 'Popen') as launch:
            with self.assertRaisesRegex(OSError, '^factory failure$'):
                self.launch('pass', Mock(side_effect=[gate, OSError('factory failure')]))
            launch.assert_not_called()
        self.assertEqual(abandoned, [True])
        self.assertFalse(self.output.exists())

    def test_rejected_gate_with_cleanup_is_abandoned(self):
        abandoned = []

        class UsedGate(ExactSecretStreamQuarantine):
            def abandon(self):
                abandoned.append(True)
                super().abandon()

        gate = UsedGate((b'secret',))
        gate.feed(b'secret')
        with self.assertRaises(ValueError):
            self.launch('pass', lambda: gate)
        self.assertEqual(abandoned, [True])
        self.assertFalse(self.output.exists())

    def test_gate_cannot_expand_output_beyond_received_allowance(self):
        class ExpandingGate(ExactSecretStreamQuarantine):
            def feed(self, payload):
                return b'x' * 10000

        with self.assertRaisesRegex(RuntimeError, '^quarantine changed raw stream$'):
            self.launch("print('tiny')", lambda: ExpandingGate((b'secret',)), max_stream_bytes=16)
        self.assertEqual((self.output / 'native.stdout').read_bytes(), b'')
        self.assertFalse((self.output / 'capture.json').exists())

    def test_invalid_gate_flag_cannot_pass_bytes_to_disk(self):
        class InvalidFlagGate(ExactSecretStreamQuarantine):
            def feed(self, payload):
                self.quarantined = None
                return payload

        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.launch("print('public')", lambda: InvalidFlagGate((b'secret',)))
        self.assertEqual((self.output / 'native.stdout').read_bytes(), b'')
        self.assertFalse((self.output / 'capture.json').exists())

    def test_stderr_secret_is_quarantined(self):
        secret = b'fabricated-error-secret'
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.launch(f'import os; os.write(2,{secret!r})',
                        lambda: ExactSecretStreamQuarantine((secret,)))
        self.assertFalse((self.output / 'capture.json').exists())
        for path in self.output.iterdir():
            self.assertNotIn(secret, path.read_bytes())

    def test_gate_cleanup_failure_prevents_receipt_publication(self):
        abandoned = []

        class FailingCleanupGate(ExactSecretStreamQuarantine):
            def abandon(self):
                abandoned.append(True)
                super().abandon()
                raise OSError('cleanup failure')

        with self.assertRaisesRegex(OSError, '^cleanup failure$'):
            self.launch("print('public')", lambda: FailingCleanupGate((b'secret',)))
        self.assertEqual(abandoned, [True, True])
        self.assertFalse((self.output / 'capture.json').exists())

    def test_feed_and_storage_errors_reap_child_and_abandon_both_gates(self):
        for failing_feed in (False, True):
            with self.subTest(failing_feed=failing_feed):
                self.output = self.root / str(failing_feed)
                abandoned, processes = [], []
                real_popen = subprocess.Popen

                class ObservedGate(ExactSecretStreamQuarantine):
                    def feed(self, payload):
                        if failing_feed:
                            raise OSError('feed failure')
                        return super().feed(payload)

                    def abandon(self):
                        abandoned.append(True)
                        super().abandon()

                def observe(*args, **kwargs):
                    process = real_popen(*args, **kwargs)
                    processes.append(process)
                    return process

                with patch.object(capture.subprocess, 'Popen', side_effect=observe), patch.object(
                        capture, '_write_all', side_effect=OSError('storage failure')):
                    with self.assertRaisesRegex(OSError, '^(feed|storage) failure$'):
                        self.launch("import os,time; os.write(1,b'public output'); time.sleep(30)",
                                    lambda: ObservedGate((b'secret',)))
                self.assertEqual(processes[0].poll(), -signal.SIGKILL)
                self.assertTrue(processes[0].stdout.closed)
                self.assertTrue(processes[0].stderr.closed)
                self.assertEqual(abandoned, [True, True])
                self.assertFalse((self.output / 'capture.json').exists())
