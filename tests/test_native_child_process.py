"""Real frozen cgroups establish child identity without consuming trace text."""

from contextlib import contextmanager
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

from caplab.native_child_process import FrozenNativeChildEvidence, observe_frozen_native_child
from caplab.exec_provenance import observe_exec_tracer
from caplab.exec_trace import inspect_exec_termination
from caplab.process_trace import ProcessCreationEvidence, inspect_process_creation

REPO = Path(__file__).resolve().parents[1]
CGROUP = Path('/sys/fs/cgroup')
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}
JOIN = "import os,sys;from pathlib import Path;Path(sys.argv[1],'cgroup.procs').write_text(str(os.getpid()));os.execv(sys.argv[2],sys.argv[2:])"
LAUNCHER = '''import os,socket,subprocess,sys
with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as channel:
 channel.settimeout(10);channel.connect('/control.sock');channel.sendall(b'P')
 mode=channel.recv(1)
 if mode==b'G':
  readfd,writefd=os.pipe()
  code="import os,signal,subprocess,sys;p=subprocess.Popen(['/usr/bin/sleep','20']);signal.signal(signal.SIGTERM,lambda *_:p.terminate());os.write(int(sys.argv[1]),b'R');os.close(int(sys.argv[1]));p.wait()"
  children=[subprocess.Popen(['/usr/bin/python3','-B','-c',code,str(writefd)],pass_fds=(writefd,))]
  os.close(writefd);assert os.read(readfd,1)==b'R';os.close(readfd)
 else:children=[subprocess.Popen(['/usr/bin/sleep','20'],env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'}) for _ in range(int(mode))]
 channel.sendall(b'R');channel.recv(1)
 for child in children:child.terminate()
 for child in children:child.wait(timeout=2)
 channel.sendall(b'D');channel.recv(1)
'''


def await_field(path, key, expected):
    deadline = time.monotonic() + 2
    while dict(line.split() for line in path.read_text().splitlines()).get(key) != expected:
        if time.monotonic() >= deadline:
            raise RuntimeError('owned cgroup did not reach ' + key + '=' + expected)
        time.sleep(.01)


@contextmanager
def frozen(group):
    (group/'cgroup.freeze').write_text('1')
    try:
        await_field(group/'cgroup.events', 'frozen', '1')
        yield
    finally:
        (group/'cgroup.freeze').write_text('0')
        await_field(group/'cgroup.events', 'frozen', '0')


@contextmanager
def launcher(group, root, count):
    control = root/'control.sock'
    trace = root / ('trace-' + str(count))
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
        listener.bind(str(control)); listener.listen(1); listener.settimeout(5)
        command = ['/usr/bin/python3', '-B', '-c', JOIN, str(group), '/usr/bin/prlimit',
            '--fsize=65536:65536', '--core=0', '--', '/usr/bin/bwrap', '--unshare-all',
            '--die-with-parent', '--new-session', '--cap-drop', 'ALL', '--clearenv',
            '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
            '--symlink', 'usr/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev',
            '--ro-bind', str(control), '/control.sock', '--remount-ro', '/',
            '--', '/usr/bin/python3', '-B', '-c', LAUNCHER]
        command = ['/usr/bin/prlimit', '--fsize=1048576:1048576', '--core=0', '--',
            '/usr/bin/strace', '-f', '-v', '-xx', '-s', '65536', '--decode-pids=pidns',
            '-e', 'trace=execve,execveat,clone,clone3,fork,vfork', '-o', str(trace), '--', *command]
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(command, env=ENV, stdout=stdout, stderr=stderr)
            try:
                channel, _ = listener.accept()
                with channel:
                    channel.settimeout(5)
                    pid, uid, gid = struct.unpack('3i', channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                    assert (uid, gid) == (os.getuid(), os.getgid())
                    assert channel.recv(1) == b'P'
                    descriptor = os.open(f'/proc/{pid}', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                    try:
                        tracer = observe_exec_tracer(pid, trace, expected_tracer_executable=Path('/usr/bin/strace'))
                        channel.sendall(str(count).encode()); assert channel.recv(1) == b'R'
                        yield pid, descriptor, tracer
                        channel.sendall(b'X'); assert channel.recv(1) == b'D'; channel.sendall(b'X')
                    finally:
                        os.close(descriptor)
                assert process.wait(timeout=5) == 0
                stderr.seek(0); assert stderr.read(65537) == b''
            finally:
                (group/'cgroup.freeze').write_text('0')
                if process.poll() is None:
                    (group/'cgroup.kill').write_text('1')
                    process.wait(timeout=5)
                await_field(group/'cgroup.events', 'populated', '0')
                control.unlink()


def worker(unit, root):
    assert re.fullmatch(r'caplab-child-observer-[0-9a-f]{32}\.service', unit)
    membership = Path('/proc/self/cgroup').read_text().strip()
    assert membership.startswith('0::/') and '\n' not in membership
    supervisor = CGROUP / membership[3:].lstrip('/')
    assert supervisor.name == 'supervisor' and supervisor.parent.name == unit
    owner = supervisor.parent
    (owner/'cgroup.subtree_control').write_text('+memory +pids')
    group = owner/'workload'; group.mkdir()
    (group/'memory.max').write_text(str(256*1024**2))
    (group/'memory.swap.max').write_text('0'); (group/'pids.max').write_text('32')
    before = set(os.listdir('/proc/self/fd'))
    reports, refusals = [], []
    def refuses(name, evidence, pattern):
        before = set(os.listdir('/proc/self/fd'))
        with unittest.TestCase().assertRaisesRegex(ValueError, pattern):
            observe_frozen_native_child(group, evidence=evidence)
        assert set(os.listdir('/proc/self/fd')) == before
        refusals.append(name)
    try:
        with launcher(group, root, 1) as (pid, descriptor, tracer):
            evidence = FrozenNativeChildEvidence(pid, descriptor, Path('/usr/bin/sleep'),
                hashlib.sha256(Path('/usr/bin/sleep').read_bytes()).hexdigest(), 1024**2, 32)
            refuses('unfrozen', evidence, 'not frozen')
            with frozen(group):
                observed = observe_frozen_native_child(group, evidence=evidence)
                assert observed['parent_pid'] == pid and observed['child_pid'] != pid
                assert observed['child_status']['PPid'] == pid
                assert observed['executable']['sha256'] == evidence.expected_executable_sha256
                assert not observed['binding_complete'] and not observed['study_eligible']
                reports.append(observed)
                assert observed['started_monotonic_ns'] <= observed['finished_monotonic_ns']
                assert os.fstat(descriptor).st_ino == observed['parent_proc_identity']['inode']
                refuses('wrong_hash', replace(evidence, expected_executable_sha256='0'*64), 'hash differs')
                refuses('byte_limit', replace(evidence, max_executable_bytes=1), 'byte allowance')
                refuses('process_limit', replace(evidence, max_processes=1), 'population differs')
                other = os.open('/proc/self', os.O_RDONLY | os.O_DIRECTORY)
                try:
                    refuses('wrong_parent_descriptor', replace(evidence, parent_proc_descriptor=other), 'descriptor differs')
                finally:
                    os.close(other)
                copy = root/'same-bytes-other-inode'; shutil.copyfile('/usr/bin/sleep', copy)
                refuses('same_bytes_other_object', replace(evidence, expected_executable=copy), 'exactly one matching')
                copy.unlink()
                nested = group/'unexpected'; nested.mkdir()
                try:
                    refuses('non_leaf', evidence, 'must be a leaf')
                finally:
                    nested.rmdir()
                assert os.fstat(descriptor).st_ino == observed['parent_proc_identity']['inode']
        trace = root/'trace-1'; trace_sha = hashlib.sha256(trace.read_bytes()).hexdigest()
        creation = inspect_process_creation(trace, evidence=ProcessCreationEvidence(
            trace_sha, observed['parent_pid'], observed['child_pid'], 1024**2))
        execution = inspect_exec_termination(trace, expected_trace_sha256=trace_sha,
            expected_pid=observed['child_pid'], expected_executable='/usr/bin/sleep',
            expected_command=['/usr/bin/sleep', '20'], expected_environment=ENV, max_trace_bytes=1024**2)
        assert execution['termination']['signal'] == 'SIGTERM'
        assert creation['child_pid'] == observed['child_pid']
        observed['test_trace_join'] = {'tracer': tracer, 'creation': creation, 'execution': execution,
                                      'trace_sha256': trace_sha}
        for count, name in [(0, 'missing_child'), (2, 'ambiguous_children'), ('G', 'grandchild_not_direct')]:
            with launcher(group, root, count) as (pid, descriptor, tracer):
                evidence = replace(evidence, parent_pid=pid, parent_proc_descriptor=descriptor)
                with frozen(group):
                    if count == 'G':
                        # Establish that a matching image exists, so the refusal tests parentage.
                        candidates = [int(row) for row in (group/'cgroup.procs').read_text().splitlines()]
                        source = Path('/usr/bin/sleep').stat()
                        assert any((actual.st_dev, actual.st_ino) == (source.st_dev, source.st_ino)
                                   for pid in candidates for actual in [Path(f'/proc/{pid}/exe').stat()])
                    refuses(name, evidence, 'exactly one matching')
    finally:
        (group/'cgroup.freeze').write_text('0')
        (group/'cgroup.kill').write_text('1')
        await_field(group/'cgroup.events', 'populated', '0')
        group.rmdir()
    assert set(os.listdir('/proc/self/fd')) == before
    return {'unit': unit, 'cgroup': str(owner), 'reports': reports, 'refusals': refusals,
            'borrowed_descriptors_closed_by_caller': True,
            'workload_removed': not group.exists()}


class FrozenNativeChildTests(unittest.TestCase):
    @unittest.skipUnless(Path(f'/run/user/{os.getuid()}/systemd/private').exists(), 'requires delegated systemd user service')
    def test_kernel_child_executable_is_selected_independently_of_trace(self):
        with tempfile.TemporaryDirectory(prefix='caplab-child-observer-test-') as temporary:
            root = Path(temporary)
            unit = 'caplab-child-observer-' + uuid.uuid4().hex + '.service'
            environment = ENV | {'XDG_RUNTIME_DIR':f'/run/user/{os.getuid()}',
                'DBUS_SESSION_BUS_ADDRESS':f'unix:path=/run/user/{os.getuid()}/bus'}
            command = ['/usr/bin/systemd-run', '--user', '--unit='+unit, '--wait', '--pipe', '--collect',
                '--service-type=exec', '--property=Delegate=memory pids', '--property=DelegateSubgroup=supervisor',
                '--property=MemoryMax=536870912', '--property=MemorySwapMax=0', '--property=TasksMax=64',
                '--property=RuntimeMaxSec=30', '--property=KillMode=control-group', '--property=LimitCORE=0',
                '--', '/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', 'LANG=C.UTF-8', 'PYTHONPATH='+str(REPO/'src'),
                '/usr/bin/python3', '-B', str(Path(__file__).resolve()), '--worker', unit, str(root)]
            try:
                completed = subprocess.run(command, env=environment, capture_output=True, timeout=40)
                self.assertEqual(completed.returncode, 0, completed.stderr.decode())
                observed = json.loads(completed.stdout)
                self.assertTrue(observed['workload_removed'])
                self.assertEqual(len(observed['reports']), 1)
                self.assertEqual(set(observed['refusals']), {'unfrozen', 'wrong_hash', 'byte_limit', 'process_limit',
                    'wrong_parent_descriptor', 'same_bytes_other_object', 'non_leaf', 'missing_child',
                    'ambiguous_children', 'grandchild_not_direct'})
            finally:
                subprocess.run(['/usr/bin/systemctl', '--user', 'stop', unit], env=environment, capture_output=True, timeout=5)
                state = subprocess.run(['/usr/bin/systemctl', '--user', 'show', unit, '--property=LoadState', '--value'],
                    env=environment, capture_output=True, timeout=5)
                self.assertEqual(state.returncode, 0, state.stderr.decode())
                self.assertEqual(state.stdout.strip(), b'not-found')
            self.assertFalse(Path(observed['cgroup']).exists())


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--worker':
        print(json.dumps(worker(sys.argv[2], Path(sys.argv[3]))))
    else:
        unittest.main()
