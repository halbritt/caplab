"""A selected child must belong to the selected launch, with its own outcome."""

from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import tempfile
import unittest

from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.exec_provenance import observe_exec_tracer, verify_exec_tracer
from caplab.process_capture import capture_process
from caplab.native_launch_configuration import (NativeLaunchContext, NativeLaunchTraceEvidence,
    NativeChildTraceEvidence, build_native_launch_configuration, inspect_native_child_trace)
from test_exec_trace import string, array

POLICY = Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'


def exec_line(pid, executable, command, environment):
    return (str(pid) + ' execve(' + string(executable) + ', ' + array(command) + ', ' +
            array([k+'='+v for k, v in environment.items()]) + ') = 0\n')


class NativeChildExecutionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name); self.trace = self.root / 'trace'
        self.plan = build_native_capture_invocation(POLICY, 'codex-terra-max',
            context=NativeCaptureContext('/work', '/episode', 'Fixed café diagnostic.\n'.encode(), None))
        self.launch = build_native_launch_configuration(POLICY, self.plan,
            expected_invocation_sha256=self.plan['invocation_sha256'], context=NativeLaunchContext('canonical-native/v1'))
        self.child = NativeChildTraceEvidence(91, '/native', ['/native', 'café'], {'LANG': 'C.UTF-8'})
        self.parent_exec = exec_line(73, '/toolbin/codex', self.launch['command'], self.launch['environment'])
        self.birth = "73 fork() = 3 /* 91 in strace's PID NS */\n"
        self.child_exec = exec_line(91, self.child.expected_executable, self.child.expected_command, self.child.expected_environment)

    def inspect(self, text, *, child=None, evidence_changes=None):
        raw = text.encode('ascii'); self.trace.write_bytes(raw)
        evidence = NativeLaunchTraceEvidence(self.plan['invocation_sha256'], self.launch['launch_configuration_sha256'],
            hashlib.sha256(raw).hexdigest(), 73, len(raw))
        return inspect_native_child_trace(POLICY, self.plan, self.launch, self.trace,
            evidence=replace(evidence, **(evidence_changes or {})), child=self.child if child is None else child)

    def test_child_and_entrypoint_outcomes_are_distinct_in_one_verified_chain(self):
        report = self.inspect(self.parent_exec + self.birth + self.child_exec +
            '91 +++ exited with 0 +++\n73 +++ exited with 7 +++\n')
        self.assertEqual(report['launch']['entrypoint_termination']['termination']['exit_code'], 7)
        self.assertEqual(report['child_execution']['termination']['exit_code'], 0)
        self.assertEqual((report['creation']['parent_pid'], report['creation']['child_pid']), (73, 91))
        self.assertTrue(report['recorded_child_execution_linked'])
        self.assertFalse(report['executable_bytes_verified'])
        self.assertFalse(report['task_success_verified']); self.assertFalse(report['binding_complete'])
        self.assertFalse(report['study_eligible']); self.assertIsNone(report['native_capture_complete'])

    def test_child_created_before_the_selected_entrypoint_exec_cannot_supply_its_execution(self):
        with self.assertRaisesRegex(ValueError, 'child creation precedes selected entrypoint'):
            self.inspect(self.birth + self.parent_exec + self.child_exec +
                '91 +++ exited with 0 +++\n73 +++ exited with 0 +++\n')

    def test_interleaved_vfork_keeps_child_exec_before_creation_completion(self):
        report = self.inspect(self.parent_exec + '73 vfork( <unfinished ...>\n' + self.child_exec +
            "73 <... vfork resumed>) = 3 /* 91 in strace's PID NS */\n" +
            '91 +++ killed by SIGKILL +++\n73 +++ exited with 137 +++\n')
        self.assertEqual(report['creation']['creation'], {'syscall': 'vfork', 'entry_line': 2, 'completion_line': 4})
        self.assertEqual(report['child_execution']['exec_trace']['matching_execve']['entry_line'], 3)
        self.assertEqual(report['child_execution']['termination']['signal'], 'SIGKILL')
        self.assertIsNone(report['child_execution']['termination']['exit_code'])
        self.assertEqual(report['launch']['entrypoint_termination']['termination']['exit_code'], 137)

    def test_wrong_child_identity_and_invocation_cannot_link(self):
        trace = self.parent_exec + self.birth + self.child_exec + '91 +++ exited with 0 +++\n73 +++ exited with 0 +++\n'
        for changes in ({'expected_pid': 73}, {'expected_pid': True}, {'expected_pid': 92},
                        {'expected_executable': '/other'}, {'expected_command': ['/native', 'different']},
                        {'expected_environment': {'LANG': 'C'}}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.inspect(trace, child=replace(self.child, **changes))
        with self.assertRaisesRegex(ValueError, 'invalid native child trace evidence'):
            self.inspect(trace, child={})
        for changes in ({'expected_pid': 74}, {'expected_trace_sha256': '0'*64},
                        {'expected_invocation_sha256': '0'*64}, {'expected_launch_sha256': '0'*64},
                        {'max_trace_bytes': 1}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.inspect(trace, evidence_changes=changes)

    def test_missing_or_ambiguous_creation_and_terminal_records_refuse(self):
        for birth in ('', '73 fork() = 91\n', self.birth*2, self.birth.replace('73 ', '74 '),
                      self.birth.replace('fork()', 'clone(flags=CLONE_THREAD|CLONE_VM)'),
                      self.birth.replace('fork()', 'clone(flags=CLONE_PARENT|SIGCHLD)')):
            with self.subTest(birth=birth), self.assertRaises(ValueError):
                self.inspect(self.parent_exec + birth + self.child_exec +
                    '91 +++ exited with 0 +++\n73 +++ exited with 0 +++\n')
        for terminals in ('', '91 +++ exited with 0 +++\n', '73 +++ exited with 0 +++\n',
                          '91 +++ exited with 0 +++\n'*2 + '73 +++ exited with 0 +++\n'):
            with self.subTest(terminals=terminals), self.assertRaises(ValueError):
                self.inspect(self.parent_exec + self.birth + self.child_exec + terminals)

    @unittest.skipUnless(all(Path(p).is_file() for p in ('/usr/bin/bwrap', '/usr/bin/strace')),
                         'requires Bubblewrap and strace')
    def test_real_authenticated_parent_and_child_keep_independent_outcomes(self):
        handshake = """import os,socket,sys
with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as channel:
 channel.settimeout(5);channel.connect('/control.sock');channel.sendall(b'R')
 if channel.recv(1)!=b'1':sys.exit(99)
"""
        environment = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}
        before = set(os.listdir('/proc/self/fd'))
        for mode in ('zero', 'killed'):
            with self.subTest(mode=mode):
                root = self.root / mode; root.mkdir()
                trace, control, launcher = root/'trace', root/'control.sock', root/'launcher'
                child = ['/usr/bin/python3', '-B', '-c', handshake +
                    ('sys.exit(0)\n' if mode == 'zero' else 'import signal\nos.kill(os.getpid(),signal.SIGKILL)\n')]
                launcher.write_text('#!/usr/bin/python3\n' + handshake + 'import subprocess\n' +
                    'subprocess.run(' + repr(child) + ',env=' + repr(environment) + ')\nsys.exit(7)\n')
                launcher.chmod(0o755)
                bootstrap = 'import json,os,sys\np=json.loads(sys.argv[1]);os.execve("/toolbin/codex",p["command"],p["environment"])'
                command = ['/usr/bin/prlimit', '--fsize=2097152:2097152', '--core=0', '--', '/usr/bin/strace',
                    '-f', '-v', '-xx', '-s', '65536', '--decode-pids=pidns', '-e',
                    'trace=execve,execveat,clone,clone3,fork,vfork', '-o', str(trace), '--',
                    '/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
                    '--cap-drop', 'ALL', '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin',
                    '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
                    '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/work', '--dir', '/toolbin',
                    '--ro-bind', str(launcher), '/toolbin/codex', '--ro-bind', str(control), '/control.sock',
                    '--chdir', '/work', '--remount-ro', '/', '--', '/usr/bin/python3', '-B', '-c',
                    bootstrap, json.dumps(self.plan)]
                peers = []
                with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
                    listener.bind(str(control)); listener.listen(1); listener.settimeout(5)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(capture_process, command, cwd=root, environment=environment,
                            output_dir=root/'capture', max_stream_bytes=10000, timeout_seconds=10)
                        for _ in range(2):
                            channel, _ = listener.accept()
                            with channel:
                                channel.settimeout(5)
                                pid, uid, gid = struct.unpack('3i', channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                                self.assertEqual((uid, gid), (os.getuid(), os.getgid()))
                                self.assertEqual(channel.recv(1), b'R')
                                status = dict(line.split(':', 1) for line in Path('/proc', str(pid), 'status').read_text().splitlines())
                                self.assertEqual(int(status['Tgid']), pid)
                                observation = observe_exec_tracer(pid, trace, expected_tracer_executable=Path('/usr/bin/strace'))
                                peers.append((pid, observation)); channel.sendall(b'1')
                        captured = future.result(timeout=12)
                self.assertEqual(captured['return_code'], 7); self.assertTrue(captured['streams_complete'])
                evidence = NativeLaunchTraceEvidence(self.plan['invocation_sha256'], self.launch['launch_configuration_sha256'],
                    hashlib.sha256(trace.read_bytes()).hexdigest(), peers[0][0], 2*1024*1024)
                result = inspect_native_child_trace(POLICY, self.plan, self.launch, trace, evidence=evidence,
                    child=NativeChildTraceEvidence(peers[1][0], child[0], child, environment))
                self.assertEqual(result['launch']['entrypoint_termination']['termination']['exit_code'], 7)
                terminal = result['child_execution']['termination']
                self.assertEqual((terminal['exit_code'], terminal['signal']), (0, None) if mode == 'zero' else (None, 'SIGKILL'))
                for pid, observation in peers:
                    self.assertTrue(verify_exec_tracer(observation, trace, expected_pid=pid)['recorded_tracer_custody_agrees'])
                    self.assertFalse(Path('/proc', str(pid)).exists())
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)
