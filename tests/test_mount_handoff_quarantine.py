"""Real borrowed descriptors exercise refusal before releasing a synthetic child."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest

from caplab.process_capture import capture_process
from caplab.revbench.codex import ExactSecretStreamQuarantine
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureLimits
from test_mount_capture_quarantine import probe


PRODUCER = """import array,os,socket,sys
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
    channel.settimeout(3)
    channel.connect('/control.sock')
    descriptors=[os.open(path,os.O_RDONLY|os.O_DIRECTORY) for path in ('/scratch','/tmp','/dev/shm','/work','/episode')]
    channel.sendmsg([b'R'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',descriptors))])
    for fd in descriptors:os.close(fd)
    if channel.recv(1)!=b'1':sys.exit(7)
print('released')
"""
SECRET = b'fabricated-mount-handoff-only'


@unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'Bubblewrap required for isolated descriptor fixture')
class MountHandoffQuarantineTests(unittest.TestCase):
    def exercise(self, mode):
        before = set(os.listdir('/proc/self/fd'))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            task = root / 'task'; task.mkdir()
            socket_path = root / 'control.sock'
            member = Path('/proc/self/cgroup').read_text().strip()
            self.assertTrue(member.startswith('0::/'))
            child = Path('/sys/fs/cgroup') / member[3:].lstrip('/')
            receipt_name = child.name.removeprefix('fixture-') + '-handoff.json'
            secret = receipt_name.encode() if mode == 'name' else SECRET
            factory = lambda: ExactSecretStreamQuarantine((secret,))
            command = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
                '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
                '--symlink', 'usr/lib64', '/lib64', '--proc', '/proc', '--dir', '/dev',
                '--dev-bind', '/dev/null', '/dev/null', '--dev-bind', '/dev/urandom', '/dev/urandom']
            for mount in probe.MOUNTS:
                command += ['--size', str(64 * probe.MIB), '--tmpfs', mount]
            command += ['--ro-bind', str(socket_path), '/control.sock', '--chdir', '/work',
                '--remount-ro', '/proc', '--remount-ro', '/', '--', '/usr/bin/python3', '-B', '-c', PRODUCER]
            peer = {'diagnostic': SECRET.decode() if mode == 'metadata' else 'safe café'}
            expected = nullcontext() if mode == 'safe' else self.assertRaisesRegex(RuntimeError, '^capture output quarantined$')
            with expected:
                with SupervisedTaskCapture(command, task_root=task, namespace_root='/work', environment={},
                        output_dir=root / 'attempt', limits=TaskCaptureLimits(10000, 1000, 20, 5),
                        max_process_receipt_bytes=10000, quarantine_factory=factory) as recorder:
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
                        listener.bind(str(socket_path)); listener.listen(1); listener.settimeout(5)
                        with ThreadPoolExecutor(max_workers=1) as pool:
                            future = pool.submit(capture_process, command, cwd=task, environment={},
                                output_dir=root / 'attempt/process', max_stream_bytes=10000,
                                timeout_seconds=5, quarantine_factory=factory)
                            descriptors, handoff = probe.receive_mount(listener, child, recorder,
                                inspect_peer=lambda pid: peer, usable_devices=True, quarantine_factory=factory)
                            try:
                                self.assertEqual(handoff['peer_checks'], peer)
                                self.assertEqual(json.loads((root / receipt_name).read_bytes()), handoff)
                                for descriptor, identity in zip(descriptors, handoff['mounts'], strict=True):
                                    self.assertEqual(os.fstat(descriptor).st_ino, identity['source_ino'])
                            finally:
                                for descriptor in descriptors: os.close(descriptor)
                            future.result(timeout=7)
                    recorder.finish(expected_process_sha256=probe.digest(root / 'attempt/process/capture.json'))
            process = future.result(timeout=7)
            self.assertEqual(process['return_code'], 0 if mode == 'safe' else 7)
            self.assertEqual((root / 'attempt/process/native.stdout').read_bytes(), b'released\n' if mode == 'safe' else b'')
            if mode != 'safe':
                self.assertFalse((root / receipt_name).exists())
                self.assertFalse((root / ('.' + receipt_name.removesuffix('.json') + '.pending')).exists())
                self.assertFalse((root / 'attempt/attempt.json').exists())
            for path in root.rglob('*'):
                if path.is_file():
                    self.assertNotIn(secret, path.read_bytes())
        self.assertEqual(before, set(os.listdir('/proc/self/fd')))

    def test_safe_peer_metadata_preserves_bytes_and_releases_child(self):
        self.exercise('safe')

    def test_secret_peer_metadata_refuses_before_receipt_and_release(self):
        self.exercise('metadata')

    def test_secret_receipt_name_refuses_before_receipt_and_release(self):
        self.exercise('name')
