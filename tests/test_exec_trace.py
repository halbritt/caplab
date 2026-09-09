"""Synthetic syscall text tests parsing/refusal only; real traces live in diagnostic custody."""

import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from caplab.exec_trace import inspect_exec_trace
from caplab.task_capture_verify import CaptureVerificationError


def string(value):
    return '"' + ''.join('\\x%02x' % byte for byte in value.encode()) + '"'


def array(values):
    return '[' + ', '.join(string(value) for value in values) + ']'


class ExecTraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'trace'
        self.command = ['native', '--', 'résumé\n"quoted" \\ literal']
        self.environment = {'PATH': '/toolbin:/usr/bin', 'EMPTY': '', 'VALUE': 'a=b'}
        self.call = 'execve(' + string('/toolbin/native') + ', ' + array(self.command) + ', ' + array(
            [key + '=' + value for key, value in reversed(list(self.environment.items()))]) + ') = 0'

    def inspect(self, text=None, **changes):
        raw = (text if text is not None else '73 ' + self.call + '\n73 +++ exited with 1 +++\n').encode()
        self.path.write_bytes(raw)
        return inspect_exec_trace(self.path, **({'expected_trace_sha256': hashlib.sha256(raw).hexdigest(),
            'expected_pid': 73, 'expected_executable': '/toolbin/native', 'expected_command': self.command,
            'expected_environment': self.environment, 'max_trace_bytes': len(raw)} | changes))

    def test_exact_unicode_argv_and_unordered_environment_allow_failed_program_exit(self):
        result = self.inspect()
        self.assertTrue(result['successful_execve_agrees'])
        self.assertEqual(result['matching_execve'], {'entry_line': 1, 'completion_line': 1})
        self.assertFalse(result['trace_provenance_verified'])
        self.assertIsNone(result['native_capture_complete'])

    def test_interleaved_resumption_links_only_the_expected_pid(self):
        result = self.inspect('73 ' + self.call[:-5] + ' <unfinished ...>\n74 ' + self.call +
            '\n73 <... execve resumed>) = 0\n')
        self.assertEqual(result['matching_execve'], {'entry_line': 1, 'completion_line': 3})

    def test_wrong_pid_command_environment_executable_or_duplicate_success_refuses(self):
        for changes in ({'expected_pid': 74}, {'expected_pid': True}, {'expected_command': ['native']},
                        {'expected_environment': {'PATH': '/other'}}, {'expected_executable': '/different'}):
            with self.subTest(changes=changes), self.assertRaises(CaptureVerificationError): self.inspect(**changes)
        with self.assertRaises(CaptureVerificationError): self.inspect(('73 ' + self.call + '\n') * 2)

    def test_failed_execution_and_payload_decoys_do_not_count_as_success(self):
        for text in ('73 ' + self.call[:-1] + '-1 ENOENT (No such file or directory)\n',
                     '74 ' + self.call + '\n', '73 --- SIGTERM {si_signo=SIGTERM} ---\n'):
            with self.subTest(text=text), self.assertRaises(CaptureVerificationError): self.inspect(text)

    def test_abbreviation_malformed_arrays_duplicates_and_unfinished_records_refuse(self):
        duplicate = self.call.replace(array(['VALUE=a=b','EMPTY=','PATH=/toolbin:/usr/bin']), array(['PATH=/toolbin:/usr/bin'] * 2))
        for body in (self.call.replace(string(self.command[2]), '"truncated"...'), duplicate,
                     self.call.replace('execve(', 'execveat('), self.call.replace('], [', '], 0x123 /* env */ ['),
                     self.call[:-5] + ' <unfinished ...>', '<... execve resumed>) = 0'):
            with self.subTest(body=body), self.assertRaises(CaptureVerificationError): self.inspect('73 ' + body + '\n')
        with self.assertRaises(CaptureVerificationError): self.inspect('73 ' + self.call)

    def test_independent_hash_byte_limit_and_symlink_refusal_preserve_descriptors(self):
        before = set(os.listdir('/proc/self/fd'))
        for options in ({'expected_trace_sha256': '0'*64}, {'max_trace_bytes': 1}, {'max_trace_bytes': True}):
            with self.subTest(options=options), self.assertRaises(CaptureVerificationError): self.inspect(**options)
        self.inspect(); target = self.path.with_name('link'); target.symlink_to(self.path)
        with self.assertRaises(OSError):
            inspect_exec_trace(target, expected_trace_sha256=hashlib.sha256(self.path.read_bytes()).hexdigest(),
                expected_pid=73, expected_executable='/toolbin/native', expected_command=self.command,
                expected_environment=self.environment, max_trace_bytes=100000)
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)
