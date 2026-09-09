"""Explicit descriptor delivery and caller ownership across capture outcomes."""

import errno
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import caplab.process_capture as capture


class ProcessCaptureDescriptorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / 'capture'
        self.input = tempfile.TemporaryFile()
        self.addCleanup(self.input.close)
        self.payload = b'synthetic-input-only\x00\xff-not-for-argv'
        self.input.write(self.payload)
        self.input.flush()
        self.input.seek(0)
        self.fd = self.input.fileno()

    def launch(self, code, **kwargs):
        return capture.capture_process(
            [sys.executable, '-c', code], cwd=self.root, environment={},
            output_dir=self.output, max_stream_bytes=4096,
            timeout_seconds=kwargs.pop('timeout_seconds', 3), **kwargs)

    def test_allowed_input_reaches_child_without_payload_in_capture(self):
        code = (f'import hashlib,os; payload=os.read({self.fd},4096); '
                'print(hashlib.sha256(payload).hexdigest())')
        receipt = self.launch(code, pass_fds=(self.fd,))
        self.assertEqual(receipt['return_code'], 0)
        self.assertTrue(receipt['streams_complete'])
        self.assertEqual((self.output/'native.stdout').read_text().strip(),
                         hashlib.sha256(self.payload).hexdigest())
        self.assertEqual(os.lseek(self.fd, 0, os.SEEK_CUR), len(self.payload))
        self.assertFalse(os.get_inheritable(self.fd))
        self.assertEqual(os.pread(self.fd, 4096, 0), self.payload)
        for path in self.output.iterdir():
            self.assertNotIn(self.payload, path.read_bytes())
        self.assertNotIn(self.payload, code.encode())

    def test_unlisted_inheritable_descriptor_is_excluded_with_and_without_allowlist(self):
        with tempfile.TemporaryFile() as unrelated:
            other = unrelated.fileno()
            os.set_inheritable(other, True)
            code = (f'import errno,os\ntry: os.fstat({other})\n'
                    'except OSError as error: assert error.errno==errno.EBADF\n'
                    "else: raise AssertionError('unlisted descriptor inherited')\n")
            for allow in ((), (self.fd,)):
                with self.subTest(allow=allow):
                    self.output = self.root / str(len(allow))
                    receipt = self.launch(code, **({'pass_fds':allow} if allow else {}))
                    self.assertEqual(receipt['return_code'], 0)
                    self.assertTrue(receipt['streams_complete'])
                    self.assertTrue(os.get_inheritable(other))

    def test_allowlist_snapshot_precedes_capture_setup(self):
        allowed = [self.fd]
        real_open = os.open
        def mutate(path, *args, **kwargs):
            if path == self.output / 'native.stdout':
                allowed.clear()
            return real_open(path, *args, **kwargs)
        with patch.object(capture.os, 'open', side_effect=mutate):
            receipt = self.launch(f'import os; os.fstat({self.fd})', pass_fds=allowed)
        self.assertEqual(allowed, [])
        self.assertEqual(receipt['return_code'], 0)
        self.assertTrue(receipt['streams_complete'])

    def test_invalid_allowlists_fail_before_custody_or_launch(self):
        cases = (None, 3, '3', b'3', {self.fd}, {self.fd: True},
                 [True], [False], [-1], [0], [1], [2], [3.0], ['3'],
                 [self.fd, self.fd])
        for allowed in cases:
            with self.subTest(allowed=allowed), patch.object(capture.subprocess, 'Popen') as launch:
                with self.assertRaises(ValueError):
                    self.launch('pass', pass_fds=allowed)
                launch.assert_not_called()
                self.assertFalse(self.output.exists())
                self.assertEqual(os.pread(self.fd, 4096, 0), self.payload)

    def test_closed_descriptor_cannot_be_reused_by_capture_setup(self):
        closed = os.dup(self.fd)
        os.close(closed)
        with patch.object(capture.subprocess, 'Popen') as launch:
            with self.assertRaises(OSError) as raised:
                self.launch('pass', pass_fds=(closed,))
            self.assertEqual(raised.exception.errno, errno.EBADF)
            launch.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_timeout_preserves_borrowed_handle_and_reaps_child(self):
        receipt = self.launch(
            f'import os,time; os.read({self.fd},1); os.write(1,b"ready"); time.sleep(30)',
            pass_fds=(self.fd,), timeout_seconds=.3)
        self.assertEqual(receipt['termination'], 'timeout')
        self.assertEqual(receipt['return_code'], -signal.SIGKILL)
        self.assertFalse(receipt['streams_complete'])
        self.assertEqual((self.output/'native.stdout').read_bytes(), b'ready')
        self.assertFalse(os.get_inheritable(self.fd))
        self.assertEqual(os.pread(self.fd, 4096, 0), self.payload)

    def test_launch_and_capture_exceptions_preserve_caller_ownership(self):
        with self.assertRaises(FileNotFoundError):
            capture.capture_process([str(self.root/'missing')], cwd=self.root,
                environment={}, output_dir=self.output, max_stream_bytes=4096,
                timeout_seconds=3, pass_fds=(self.fd,))
        self.assertFalse((self.output/'capture.json').exists())
        self.assertEqual(os.pread(self.fd, 4096, 0), self.payload)
        for index, failure in enumerate((OSError('capture storage failure'), KeyboardInterrupt())):
            self.output = self.root / str(index)
            processes = []
            real_popen = subprocess.Popen
            def retain(*args, **kwargs):
                process = real_popen(*args, **kwargs)
                processes.append(process)
                return process
            with patch.object(capture.subprocess,'Popen',side_effect=retain), patch.object(
                    capture,'_write_all',side_effect=failure):
                with self.assertRaises(type(failure)):
                    self.launch(f'import os,time; os.read({self.fd},1); '
                                'os.write(1,b"ready"); time.sleep(30)', pass_fds=(self.fd,))
            self.assertEqual(processes[0].poll(), -signal.SIGKILL)
            self.assertFalse((self.output/'capture.json').exists())
            self.assertFalse(os.get_inheritable(self.fd))
            self.assertEqual(os.pread(self.fd, 4096, 0), self.payload)
            self.assertTrue(processes[0].stdout.closed)
            self.assertTrue(processes[0].stderr.closed)
