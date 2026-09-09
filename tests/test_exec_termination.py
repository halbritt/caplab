"""Selected-PID termination must not inherit a wrapper's outcome."""

import hashlib
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import socket
import struct
import tempfile
import unittest

from caplab.exec_trace import inspect_exec_termination
from caplab.exec_provenance import observe_exec_tracer, verify_exec_tracer
from caplab.process_capture import capture_process
from caplab.task_capture_verify import CaptureVerificationError


def quoted(value):
    return '"' + ''.join('\\x%02x' % byte for byte in value.encode()) + '"'


class ExecTerminationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.trace = Path(self.temp.name) / 'trace'
        self.command = ['/native', 'café']
        self.call = 'execve(' + quoted('/native') + ', [' + ', '.join(map(quoted, self.command)) + '], []) = 0'

    def inspect(self, text, **changes):
        raw = text.encode('ascii')
        self.trace.write_bytes(raw)
        options = {'expected_trace_sha256': hashlib.sha256(raw).hexdigest(), 'expected_pid': 73,
                   'expected_executable': '/native', 'expected_command': self.command,
                   'expected_environment': {}, 'max_trace_bytes': len(raw)}
        return inspect_exec_termination(self.trace, **(options | changes))

    def test_exact_exec_links_native_zero_exit_despite_wrapper_failure(self):
        report = self.inspect('73 ' + self.call + '\n73 +++ exited with 0 +++\n72 +++ exited with 1 +++\n')
        self.assertEqual(report['termination'], {'kind': 'exited', 'exit_code': 0,
                         'signal': None, 'core_dump_reported': False, 'line': 2})
        self.assertTrue(report['exec_trace']['successful_execve_agrees'])
        self.assertFalse(report['task_success_verified'])
        self.assertFalse(report['trace_provenance_verified'])
        self.assertFalse(report['binding_complete'])
        self.assertIsNone(report['native_capture_complete'])
        self.assertFalse(report['study_eligible'])

    def test_exit_codes_and_signal_termination_remain_distinct(self):
        for code in (1, 7, 137, 255):
            with self.subTest(code=code):
                result = self.inspect('73 ' + self.call + '\n73 +++ exited with ' + str(code) + ' +++\n')
                self.assertEqual(result['termination']['exit_code'], code)
                self.assertEqual(result['termination']['kind'], 'exited')
                self.assertIsNone(result['termination']['signal'])
        for signal, marker in (('SIGKILL', ''), ('SIGTERM', ''), ('SIGSEGV', ' (core dumped)')):
            with self.subTest(signal=signal):
                result = self.inspect('73 ' + self.call + '\n73 +++ killed by ' + signal + marker + ' +++\n')
                self.assertEqual(result['termination'], {'kind': 'signaled', 'exit_code': None,
                                 'signal': signal, 'core_dump_reported': bool(marker), 'line': 2})

    def test_missing_malformed_and_other_pid_termination_cannot_supply_outcome(self):
        bodies = ('', '74 +++ exited with 0 +++\n', '73 --- SIGTERM {si_signo=SIGTERM} ---\n',
                  '73 +++ exited with -9 +++\n', '73 +++ exited with 256 +++\n',
                  '73 +++ exited with 00 +++\n', '73 +++ exited with 0 (core dumped) +++\n',
                  '73 +++ killed by 9 +++\n', '73 +++ killed by SIGUNKNOWN +++\n',
                  '73 +++ killed by SIGRT_2 +++\n', '73 +++ killed by SIGTERM (core) +++\n',
                  '73 +++ exited with 0 +++ trailing\n', '73 +++ detached +++\n')
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(CaptureVerificationError):
                self.inspect('73 ' + self.call + '\n' + body)

    def test_lifetime_contradictions_do_not_link_a_reused_pid(self):
        execution = '73 ' + self.call + '\n'
        terminal = '73 +++ exited with 0 +++\n'
        for text in (terminal + execution, execution + terminal * 2,
                     execution + terminal + '73 --- SIGCHLD {} ---\n',
                     execution + terminal + '73 fork() = -1 EAGAIN (Try again)\n',
                     execution + terminal + '73 +++ killed by SIGKILL +++\n'):
            with self.subTest(text=text), self.assertRaises(CaptureVerificationError):
                self.inspect(text)

    def test_resumed_exec_and_later_exec_chain_keep_the_selected_pid(self):
        text = ('73 ' + self.call[:-5] + ' <unfinished ...>\n74 +++ exited with 9 +++\n'
                '73 <... execve resumed>) = 0\n73 +++ exited with 7 +++\n')
        report = self.inspect(text)
        self.assertEqual(report['exec_trace']['matching_execve']['completion_line'], 3)
        self.assertEqual(report['termination']['line'], 4)
        other = self.call.replace(quoted('/native'), quoted('/other'))
        report = self.inspect('73 ' + self.call + '\n73 ' + other + '\n73 +++ exited with 0 +++\n')
        self.assertEqual(report['exec_trace']['observed_pid_execve_calls'], 2)
        self.assertFalse(report['task_success_verified'])

    def test_exec_identity_and_file_custody_checks_are_not_bypassed(self):
        text = '73 ' + self.call + '\n73 +++ exited with 0 +++\n'
        before = set(os.listdir('/proc/self/fd'))
        for changes in ({'expected_pid': True}, {'expected_pid': 74}, {'expected_command': ['/wrong']},
                        {'expected_environment': {'INJECTED': 'yes'}}, {'expected_executable': '/other'},
                        {'expected_trace_sha256': '0' * 64}, {'max_trace_bytes': 1}):
            with self.subTest(changes=changes), self.assertRaises(CaptureVerificationError):
                self.inspect(text, **changes)
        for bad in (text.rstrip('\n'), text.replace('= 0\n', '= -1 ENOENT (No such file)\n'),
                    text.replace(quoted('café'), '"truncated"...'),
                    '73 ' + self.call[:-5] + ' <unfinished ...>\n73 +++ killed by SIGKILL +++\n'):
            with self.subTest(text=bad), self.assertRaises(CaptureVerificationError):
                self.inspect(bad)
        self.inspect(text)
        link = self.trace.with_name('link'); link.symlink_to(self.trace)
        with self.assertRaises(OSError):
            inspect_exec_termination(link, expected_trace_sha256=hashlib.sha256(self.trace.read_bytes()).hexdigest(),
                expected_pid=73, expected_executable='/native', expected_command=self.command,
                expected_environment={}, max_trace_bytes=10000)
        self.trace.write_bytes(text.encode() + b'74 \xff\n')
        with self.assertRaises(ValueError):
            inspect_exec_termination(self.trace, expected_trace_sha256=hashlib.sha256(self.trace.read_bytes()).hexdigest(),
                expected_pid=73, expected_executable='/native', expected_command=self.command,
                expected_environment={}, max_trace_bytes=10000)
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)

    @unittest.skipUnless(all(Path(p).is_file() for p in ('/usr/bin/bwrap', '/usr/bin/strace')),
                         'Bubblewrap and strace required')
    def test_real_authenticated_children_keep_exit_and_signal_outcomes_apart_from_wrapper(self):
        environment = {'LANG': 'C.UTF-8', 'PATH': '/usr/bin:/bin'}
        program = """import os,signal,socket,sys
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
 channel.settimeout(5);channel.connect('/control.sock');channel.sendall(b'R')
 if channel.recv(1)!=b'1':sys.exit(99)
if sys.argv[1]=='kill':os.kill(os.getpid(),signal.SIGKILL)
sys.exit(int(sys.argv[1]))
"""
        wrapper = """import json,subprocess,sys
result=subprocess.run(json.loads(sys.argv[1]),env=json.loads(sys.argv[2]))
print(result.returncode)
sys.exit(1)
"""
        before = set(os.listdir('/proc/self/fd'))
        for mode, outcome in (('0', 0), ('7', 7), ('137', 137), ('kill', -9)):
            with self.subTest(mode=mode):
                root = Path(self.temp.name) / mode; root.mkdir()
                trace = root / 'trace'; sock = root / 'control.sock'
                child = ['/usr/bin/python3', '-B', '-c', program, mode]
                command = ['/usr/bin/prlimit', '--fsize=1048576:1048576', '--core=0', '--',
                    '/usr/bin/strace', '-f', '-v', '-xx', '-s', '65536', '-e', 'trace=execve,execveat',
                    '-o', str(trace), '--', '/usr/bin/bwrap', '--unshare-all', '--die-with-parent',
                    '--new-session', '--clearenv', '--cap-drop', 'ALL', '--ro-bind', '/usr', '/usr',
                    '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
                    '--symlink', 'usr/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev',
                    '--tmpfs', '/work', '--ro-bind', str(sock), '/control.sock', '--chdir', '/work',
                    '--remount-ro', '/', '--', '/usr/bin/python3', '-B', '-c', wrapper,
                    json.dumps(child), json.dumps(environment)]
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
                    listener.bind(str(sock)); listener.listen(1); listener.settimeout(5)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(capture_process, command, cwd=root, environment=environment,
                            output_dir=root / 'capture', max_stream_bytes=10000, timeout_seconds=10)
                        channel, _ = listener.accept()
                        with channel:
                            channel.settimeout(5)
                            pid, uid, gid = struct.unpack('3i', channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                            self.assertEqual((uid, gid), (os.getuid(), os.getgid()))
                            self.assertEqual(channel.recv(1), b'R')
                            observation = observe_exec_tracer(pid, trace, expected_tracer_executable=Path('/usr/bin/strace'))
                            channel.sendall(b'1')
                        captured = future.result(timeout=12)
                self.assertEqual(captured['return_code'], 1)
                self.assertTrue(captured['streams_complete'])
                self.assertEqual((root / 'capture/native.stdout').read_text(), str(outcome) + '\n')
                result = inspect_exec_termination(trace, expected_trace_sha256=hashlib.sha256(trace.read_bytes()).hexdigest(),
                    expected_pid=pid, expected_executable=child[0], expected_command=child,
                    expected_environment=environment, max_trace_bytes=1048576)
                self.assertTrue(verify_exec_tracer(observation, trace, expected_pid=pid)['recorded_tracer_custody_agrees'])
                self.assertEqual(result['termination']['kind'], 'signaled' if mode == 'kill' else 'exited')
                self.assertEqual(result['termination']['signal'], 'SIGKILL' if mode == 'kill' else None)
                self.assertEqual(result['termination']['exit_code'], None if mode == 'kill' else outcome)
                self.assertFalse(Path('/proc', str(pid)).exists())
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)
