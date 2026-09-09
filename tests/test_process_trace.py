"""Process creation evidence is distinct from execution or native identity."""

import hashlib
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import tempfile
import unittest

from caplab.exec_provenance import observe_exec_tracer, verify_exec_tracer
from caplab.exec_trace import inspect_exec_trace
from caplab.process_capture import capture_process
from caplab.process_trace import ProcessCreationEvidence, inspect_process_creation
from caplab.task_capture_verify import CaptureVerificationError


class ProcessTraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'trace'

    def inspect(self, text, **changes):
        raw = text.encode('ascii'); self.path.write_bytes(raw)
        options = dict(expected_trace_sha256=hashlib.sha256(raw).hexdigest(), parent_pid=73,
                       child_pid=91, max_trace_bytes=len(raw))
        return inspect_process_creation(self.path, evidence=ProcessCreationEvidence(**(options | changes)))

    def test_namespaced_vfork_links_host_pids_despite_interleaved_child_exec(self):
        report = self.inspect("73 vfork( <unfinished ...>\n"
            '91 execve("\\x2f\\x78", ["\\x78"], []) = 0\n'
            "73 <... vfork resumed>) = 3 /* 91 in strace's PID NS */\n"
            "91 +++ exited with 0 +++\n73 +++ exited with 0 +++\n")
        self.assertEqual((report['parent_pid'], report['child_pid'], report['namespace_child_pid']), (73, 91, 3))
        self.assertEqual(report['creation'], {'syscall': 'vfork', 'entry_line': 1, 'completion_line': 3})
        self.assertTrue(report['recorded_parentage_agrees'])
        self.assertFalse(report['trace_provenance_verified'])
        self.assertFalse(report['binding_complete'])

    def test_clone_parent_thread_unknown_and_abbreviated_flags_cannot_claim_parentage(self):
        for flags in ('CLONE_PARENT|SIGCHLD', 'CLONE_THREAD|CLONE_VM', '0x100|SIGCHLD',
                      'CLONE_UNKNOWN|SIGCHLD', 'CLONE_VM|...'):
            with self.subTest(flags=flags), self.assertRaises(CaptureVerificationError):
                self.inspect('73 clone(child_stack=NULL, flags=' + flags +
                             ") = 3 /* 91 in strace's PID NS */\n")
        for call in ('fork(123)', 'vfork(unexpected)', 'clone(child_stack=NULL)',
                     'clone3({flags=CLONE_PARENT|CLONE_VM, exit_signal=SIGCHLD}, 88)'):
            with self.subTest(call=call), self.assertRaises(CaptureVerificationError):
                self.inspect('73 ' + call + " = 3 /* 91 in strace's PID NS */\n")

    def test_pid_lifetime_contradictions_cannot_link_an_earlier_or_reused_process(self):
        birth = "73 vfork() = 3 /* 91 in strace's PID NS */\n"
        for text in ('91 +++ exited with 0 +++\n' + birth,
                     '73 +++ exited with 0 +++\n' + birth,
                     birth + '91 +++ exited with 0 +++\n91 --- SIGTERM {} ---\n',
                     birth + "74 fork() = 3 /* 91 in strace's PID NS */\n"):
            with self.subTest(text=text), self.assertRaises(CaptureVerificationError): self.inspect(text)

    def test_legacy_detached_flag_preserves_process_and_thread_distinction(self):
        for flag in ('0x400000', '0x00400000', 'CLONE_DETACHED', '0x400000 /* CLONE_??? */'):
            birth = '73 clone(child_stack=NULL, flags=' + flag + "|SIGCHLD) = 3 /* 91 in strace's PID NS */\n"
            thread = ('91 clone(child_stack=0x753f789ff3e8, flags=CLONE_VM|CLONE_FS|CLONE_FILES|'
                'CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS|CLONE_PARENT_SETTID|'
                'CLONE_CHILD_CLEARTID|' + flag + ", parent_tid=[4 /* 92 in strace's PID NS */], "
                "tls=0x753f789ffb38, child_tidptr=0x753f789ffe10) = 4 /* 92 in strace's PID NS */\n")
            with self.subTest(flag=flag):
                self.assertTrue(self.inspect(birth + thread)['recorded_parentage_agrees'])
                with self.assertRaisesRegex(CaptureVerificationError, 'parentage flags'):
                    self.inspect(birth + thread, parent_pid=91, child_pid=92)
                with self.assertRaises(CaptureVerificationError):
                    self.inspect(birth.replace('|SIGCHLD', '|CLONE_PARENT|SIGCHLD'))

    def test_clone_and_clone3_preserve_exact_flags_without_confusing_parent_settid(self):
        for call in ('clone(child_stack=NULL, flags=CLONE_PARENT_SETTID|SIGCHLD)',
                     'clone3({flags=CLONE_VM|CLONE_VFORK, exit_signal=SIGCHLD}, 88)', 'fork()'):
            with self.subTest(call=call):
                report = self.inspect('73 ' + call + " = 3 /* 91 in strace's PID NS */\n")
                self.assertTrue(report['recorded_parentage_agrees'])

    def test_detached_invalid_syscall_combinations_only_allow_failed_observations(self):
        birth = "73 fork() = 3 /* 91 in strace's PID NS */\n"
        for flag in ('0x400000', 'CLONE_DETACHED'):
            for call in ('clone(child_stack=NULL, flags=CLONE_PIDFD|' + flag + '|SIGCHLD)',
                         'clone3({flags=' + flag + ', exit_signal=SIGCHLD}, 88)'):
                with self.subTest(call=call):
                    self.assertTrue(self.inspect('73 ' + call + ' = -1 EINVAL (Invalid argument)\n' + birth)[
                        'recorded_parentage_agrees'])
                    with self.assertRaisesRegex(CaptureVerificationError, 'invalid successful detached clone'):
                        self.inspect('73 ' + call + " = 3 /* 91 in strace's PID NS */\n")

    def test_missing_wrong_ambiguous_and_incomplete_creation_evidence_refuses(self):
        for text in ('73 vfork() = 91\n', "74 vfork() = 3 /* 91 in strace's PID NS */\n",
                     '73 vfork() = -1 EAGAIN (Resource temporarily unavailable)\n',
                     '73 vfork() = 0\n', '73 vfork( <unfinished ...>\n',
                     '73 <... vfork resumed>) = 91\n',
                     '73 vfork( <unfinished ...>\n73 <... clone resumed>) = 91\n',
                     '73 vfork( <unfinished ...>\n73 fork() = 91\n',
                     '73 vfork( <unfinished ...>\n73 execve("\\x78", [], []) = 0\n',
                     "73 fork() = 3 /* 91 in strace's PID NS */\n" * 2,
                     'invalid prefix\n', "73 fork() = 3 /* 91 in strace's PID NS */"):
            with self.subTest(text=text), self.assertRaises(CaptureVerificationError): self.inspect(text)

    def test_restarted_clone_only_links_the_later_successful_creation(self):
        interrupted = ('73 clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|SIGCHLD <unfinished ...>\n'
            '74 --- SIGCHLD {} ---\n'
            '73 <... clone resumed>, child_tidptr=0x1000) = ? ERESTARTNOINTR (To be restarted)\n'
            '73 --- SIGCHLD {} ---\n')
        completed = ('73 clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|SIGCHLD <unfinished ...>\n'
            '91 execve("\\x2f\\x78", ["\\x78"], []) = 0\n'
            "73 <... clone resumed>, child_tidptr=0x1000) = 3 /* 91 in strace's PID NS */\n")
        report = self.inspect(interrupted + completed)
        self.assertEqual(report['creation'], {'syscall': 'clone', 'entry_line': 5, 'completion_line': 7})
        with self.assertRaisesRegex(CaptureVerificationError, 'exactly one child creation'):
            self.inspect(interrupted)
        with self.assertRaises(CaptureVerificationError):
            self.inspect(interrupted + completed.replace('CLONE_CHILD_CLEARTID', 'CLONE_PARENT'))
        with self.assertRaises(CaptureVerificationError):
            self.inspect(interrupted + completed + "73 fork() = 3 /* 91 in strace's PID NS */\n")

    def test_restart_results_never_supply_a_child_or_accept_unknown_result_shapes(self):
        birth = "73 fork() = 3 /* 91 in strace's PID NS */\n"
        for call in ('fork()', 'vfork()', 'clone(child_stack=NULL, flags=SIGCHLD)',
                     'clone3({flags=0, exit_signal=SIGCHLD}, 88)'):
            restart = '74 ' + call + ' = ? ERESTARTNOINTR (To be restarted)\n'
            with self.subTest(call=call):
                self.assertTrue(self.inspect(restart + birth)['recorded_parentage_agrees'])
                with self.assertRaisesRegex(CaptureVerificationError, 'exactly one child creation'):
                    self.inspect(restart)
        for result in ('?', '? ERESTARTSYS (To be restarted)', '? ERESTARTNOINTR (unknown)',
                       '? ERESTARTNOINTR (To be restarted) trailing',
                       "? ERESTARTNOINTR (To be restarted) /* 91 in strace's PID NS */"):
            with self.subTest(result=result), self.assertRaises(CaptureVerificationError):
                self.inspect('74 fork() = ' + result + '\n' + birth)
        for call in ('clone(flags=0x100)', 'clone(flags=CLONE_VM|...)', 'fork(unexpected)'):
            with self.subTest(call=call), self.assertRaises(CaptureVerificationError):
                self.inspect('74 ' + call + ' = ? ERESTARTNOINTR (To be restarted)\n' + birth)

    def test_hash_bounds_identities_and_symlinks_fail_without_leaking_descriptors(self):
        text = "73 fork() = 3 /* 91 in strace's PID NS */\n"
        before = set(os.listdir('/proc/self/fd'))
        for changes in ({'parent_pid': True}, {'child_pid': 73}, {'child_pid': 0},
                        {'expected_trace_sha256': '0'*64}, {'max_trace_bytes': 1}, {'max_trace_bytes': True}):
            with self.subTest(changes=changes), self.assertRaises(CaptureVerificationError): self.inspect(text, **changes)
        self.inspect(text)
        link = self.path.with_name('link'); link.symlink_to(self.path)
        with self.assertRaises(OSError):
            inspect_process_creation(link, evidence=ProcessCreationEvidence(
                hashlib.sha256(self.path.read_bytes()).hexdigest(), 73, 91, 1000))
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)

    @unittest.skipUnless(shutil.which('bwrap') and shutil.which('strace'), 'requires Bubblewrap and strace')
    def test_real_namespaced_child_matches_authenticated_parent_and_exact_exec(self):
        root = self.path.parent; control = root/'control.sock'; trace = root/'kernel.trace'
        environment = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}
        handshake = """import json,os,socket
with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as channel:
 channel.settimeout(5);channel.connect('/control.sock')
 channel.sendall(json.dumps([os.getpid(),os.getppid()]).encode())
 if channel.recv(1)!=b'1':raise RuntimeError('release refused')
"""
        child = ['/usr/bin/python3', '-B', '-c', handshake + "print('CAPLAB café child')\n"]
        parent = handshake + 'import subprocess\nsubprocess.run(' + repr(child) + ',env=' + repr(environment) + ',check=True)\n'
        command = ['/usr/bin/prlimit', '--fsize=2097152', '--core=0', '--', '/usr/bin/strace',
            '-f', '-v', '-xx', '-s', '65536', '--decode-pids=pidns', '-e',
            'trace=execve,execveat,clone,clone3,fork,vfork', '-o', str(trace), '--',
            '/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
            '--ro-bind', '/usr', '/usr', '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
            '--proc', '/proc', '--dev', '/dev', '--size', '1048576', '--tmpfs', '/tmp',
            '--ro-bind', str(control), '/control.sock', '--remount-ro', '/', '--',
            '/usr/bin/python3', '-B', '-c', parent]
        before = set(os.listdir('/proc/self/fd')); peers = []
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
            listener.bind(str(control)); listener.listen(1); listener.settimeout(5)
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(capture_process, command, cwd=root, environment=environment,
                    output_dir=root/'capture', max_stream_bytes=10000, timeout_seconds=10)
                for _ in range(2):
                    channel, _ = listener.accept()
                    with channel:
                        channel.settimeout(5)
                        pid, uid, gid = struct.unpack('3i', channel.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                        self.assertEqual((uid,gid), (os.getuid(),os.getgid()))
                        local = json.loads(channel.recv(100))
                        observation = observe_exec_tracer(pid, trace, expected_tracer_executable=Path('/usr/bin/strace'))
                        peers.append((pid,local,observation)); channel.sendall(b'1')
                process = future.result(timeout=12)
        self.assertEqual(process['return_code'], 0)
        self.assertEqual((root/'capture/native.stdout').read_bytes(), 'CAPLAB café child\n'.encode())
        self.assertEqual(peers[1][1][1], peers[0][1][0])
        anchor = hashlib.sha256(trace.read_bytes()).hexdigest()
        report = inspect_process_creation(trace, evidence=ProcessCreationEvidence(anchor,peers[0][0],peers[1][0],2*1024*1024))
        self.assertEqual(report['namespace_child_pid'], peers[1][1][0])
        for pid, _, observation in peers:
            self.assertTrue(verify_exec_tracer(observation,trace,expected_pid=pid)['recorded_tracer_custody_agrees'])
        self.assertTrue(inspect_exec_trace(trace, expected_trace_sha256=anchor, expected_pid=peers[1][0],
            expected_executable=child[0], expected_command=child, expected_environment=environment,
            max_trace_bytes=2*1024*1024)['successful_execve_agrees'])
        self.assertEqual(set(os.listdir('/proc/self/fd')), before)


if __name__ == '__main__': unittest.main()
