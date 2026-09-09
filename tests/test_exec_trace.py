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

    def test_process_creation_records_do_not_obscure_exact_exec_evidence(self):
        report = self.inspect('73 ' + self.call + '\n73 vfork( <unfinished ...>\n'
            '91 ' + self.call + "\n73 <... vfork resumed>) = 3 /* 91 in strace's PID NS */\n")
        self.assertEqual(report['observed_pid_execve_calls'], 1)
        self.assertEqual(report['matching_execve'], {'entry_line': 1, 'completion_line': 1})
        for tail in ('73 vfork( <unfinished ...>\n', '73 <... vfork resumed>) = 3\n',
                     '73 clone(unknown) = abbreviated\n', '73 fork(unexpected) = 3\n',
                     '73 clone(unknown) = 3\n'):
            with self.subTest(tail=tail), self.assertRaises(CaptureVerificationError):
                self.inspect('73 ' + self.call + '\n' + tail)

    def test_aligned_resumed_exec_result_keeps_exact_payload_comparison(self):
        text = '73 ' + self.call[:-5] + ' <unfinished ...>\n73 <... execve resumed>)           = 0\n'
        self.assertEqual(self.inspect(text)['matching_execve'], {'entry_line': 1, 'completion_line': 2})
        with self.assertRaises(CaptureVerificationError): self.inspect(text, expected_command=['wrong'])

    def test_known_detached_thread_records_preserve_exact_exec_checks(self):
        thread = ('73 clone(child_stack=0x1000, flags=CLONE_VM|CLONE_SIGHAND|CLONE_THREAD|'
                  "0x400000) = 3 /* 91 in strace's PID NS */\n")
        text = '73 ' + self.call + '\n' + thread
        self.assertTrue(self.inspect(text)['successful_execve_agrees'])
        with self.assertRaises(CaptureVerificationError): self.inspect(text, expected_command=['wrong'])
        for flag in ('0x400100', '0x800000', '0x400000x', '4194304', 'CLONE_UNKNOWN', '0x400000|...',
                     '0x400100 /* CLONE_??? */', '0x400000 /* CLONE_PARENT */', '0x400000||SIGCHLD'):
            with self.subTest(flag=flag), self.assertRaises(CaptureVerificationError):
                self.inspect(text.replace('0x400000', flag))
        with self.assertRaises(CaptureVerificationError):
            self.inspect(text.replace('CLONE_THREAD', 'CLONE_PIDFD'))

    def test_restarted_creation_does_not_obscure_or_replace_exact_exec(self):
        restart = ('73 clone(child_stack=NULL, flags=SIGCHLD <unfinished ...>\n'
                   '73 <... clone resumed>) = ? ERESTARTNOINTR (To be restarted)\n')
        text = restart + '73 ' + self.call + '\n'
        self.assertEqual(self.inspect(text)['matching_execve'], {'entry_line': 3, 'completion_line': 3})
        with self.assertRaises(CaptureVerificationError): self.inspect(text, expected_command=['wrong'])
        for bad in (restart, text.replace('ERESTARTNOINTR', 'ERESTARTSYS'),
                    '73 ' + self.call[:-5] + ' <unfinished ...>\n' + restart,
                    '73 <... clone resumed>) = ? ERESTARTNOINTR (To be restarted)\n73 ' + self.call + '\n'):
            with self.subTest(text=bad), self.assertRaises(CaptureVerificationError): self.inspect(bad)
