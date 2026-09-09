"""Opt-in procfs supports a real nested sandbox before guarded task completion."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest

from caplab.process_capture import capture_process
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureError, TaskCaptureLimits
from test_mount_capture_quarantine import probe

PRODUCER = r'''import array,json,os,socket,subprocess,sys
from pathlib import Path
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
 channel.connect('/control.sock')
 fds=[os.open(p,os.O_RDONLY|os.O_DIRECTORY) for p in ('/scratch','/tmp','/dev/shm','/work','/episode')]
 channel.sendmsg([b'R'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',fds))])
 for fd in fds:os.close(fd)
 if channel.recv(1)!=b'1':sys.exit(7)
cmd=['/usr/bin/bwrap','--unshare-user','--unshare-pid','--unshare-net','--die-with-parent','--new-session','--clearenv','--cap-drop','ALL','--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--proc','/proc','--dir','/dev','--dev-bind','/dev/null','/dev/null','--bind','/work','/work','--size','67108864','--tmpfs','/tmp','--chdir','/work','--remount-ro','/','--','/usr/bin/python3','-B','-c',"from pathlib import Path; Path('witness.txt').write_text('CAPLAB café nested witness'+chr(10),encoding='utf-8')"]
r=subprocess.run(cmd,capture_output=True,timeout=5)
assert r.returncode==0,r.stderr
print(Path('/work/witness.txt').read_text(),end='')
'''

@unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'Bubblewrap required')
class NestedProcfsTests(unittest.TestCase):
    def exercise(self, *, retain_capability=False):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);task=root/'task';task.mkdir();sock=root/'control.sock'
            member=Path('/proc/self/cgroup').read_text().strip()
            group=Path('/sys/fs/cgroup')/member[3:].lstrip('/')
            cmd=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv','--cap-drop','ALL',
                 '--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib',
                 '--symlink','usr/lib64','/lib64','--proc','/proc','--dir','/dev',
                 '--dev-bind','/dev/null','/dev/null','--dev-bind','/dev/urandom','/dev/urandom']
            if retain_capability:cmd+=['--cap-add','CAP_NET_ADMIN']
            for path in probe.MOUNTS:cmd+=['--size',str(64*probe.MIB),'--tmpfs',path]
            cmd+=['--ro-bind',str(sock),'/control.sock','--chdir','/work','--remount-ro','/',
                  '--','/usr/bin/python3','-B','-c',PRODUCER]
            with SupervisedTaskCapture(cmd,task_root=task,namespace_root='/work',environment={},
                    output_dir=root/'attempt',limits=TaskCaptureLimits(10000,1000,20,10),max_process_receipt_bytes=10000) as recorder:
                with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as listener:
                    listener.bind(str(sock));listener.listen(1);listener.settimeout(5)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future=pool.submit(capture_process,cmd,cwd=task,environment={},
                            output_dir=root/'attempt/process',max_stream_bytes=10000,timeout_seconds=10)
                        if retain_capability:
                            with self.assertRaisesRegex(RuntimeError, 'retains privileges'):
                                probe.receive_mount(listener,group,recorder,usable_devices=True,nested_userns=True)
                            process=future.result(timeout=12)
                            self.assertEqual(process['return_code'],7)
                            self.assertEqual((root/'attempt/process/native.stdout').read_bytes(),b'')
                            self.assertFalse((root/'attempt/attempt.json').exists())
                            receipt=group.name.removeprefix('fixture-')+'-handoff.json'
                            self.assertFalse((root/receipt).exists())
                            return
                        fds,handoff=probe.receive_mount(listener,group,recorder,usable_devices=True,nested_userns=True)
                        try:
                            self.assertEqual(handoff['mount_coverage']['writable_procfs'],['/proc'])
                            probe.verify_nested_procfs(handoff['nested_procfs'])
                            self.assertNotEqual(handoff['nested_procfs']['namespaces']['pid']['peer'],
                                                handoff['nested_procfs']['namespaces']['pid']['supervisor'])
                        finally:
                            for fd in fds:os.close(fd)
                        process=future.result(timeout=12)
                recorder.finish(expected_process_sha256=probe.digest(root/'attempt/process/capture.json'))
            self.assertEqual(process['return_code'],0,(root/'attempt/process/native.stderr').read_text())
            self.assertEqual((root/'attempt/process/native.stdout').read_bytes(),'CAPLAB café nested witness\n'.encode())
            after=json.loads((root/'attempt/after/inventory.json').read_bytes())
            witness,=[e for e in after['entries'] if e['path']=='witness.txt']
            self.assertEqual((root/'attempt/after'/witness['object']).read_bytes(),'CAPLAB café nested witness\n'.encode())
            # The default must continue to reject this writable-procfs topology.
            with self.assertRaisesRegex(RuntimeError,'unexpected writable'):
                probe.mount_coverage(handoff['mount_coverage']['raw'],usable_devices=True)

            return handoff

    def test_handoff_permits_nested_sandbox_with_isolated_procfs(self):
        self.exercise()

    def test_host_procfs_is_refused(self):
        with self.assertRaisesRegex(RuntimeError, 'shares supervisor namespace'):
            probe.inspect_nested_procfs(os.getpid())

    def test_recorded_namespace_and_privilege_claims_must_remain_consistent(self):
        observed = self.exercise()['nested_procfs']
        for name in ('pid', 'mnt', 'net', 'user'):
            bad = deepcopy(observed)
            bad['namespaces'][name]['peer'] = bad['namespaces'][name]['supervisor']
            with self.subTest(namespace=name), self.assertRaisesRegex(RuntimeError, 'shares supervisor'):
                probe.verify_nested_procfs(bad)
        for name in ('CapEff', 'CapPrm', 'CapInh', 'CapAmb', 'NoNewPrivs'):
            bad = deepcopy(observed)
            bad['status'][name] = '0' if name == 'NoNewPrivs' else '0000000000000001'
            with self.subTest(privilege=name), self.assertRaisesRegex(RuntimeError, 'retains privileges'):
                probe.verify_nested_procfs(bad)
        bad = deepcopy(observed)
        bad['proc_pid1_namespace'] = bad['namespaces']['pid']['supervisor']
        with self.assertRaisesRegex(RuntimeError, 'does not show the peer PID namespace'):
            probe.verify_nested_procfs(bad)
        for bad in (None, {}, {'schema': 'caplab.nested-procfs/v1'}, observed | {'status': None}):
            with self.subTest(observation=bad), self.assertRaises(RuntimeError):
                probe.verify_nested_procfs(bad)

    def test_opt_in_does_not_admit_other_writable_or_covered_mounts(self):
        raw = self.exercise()['mount_coverage']['raw']
        rows = raw.splitlines()
        proc = next(line for line in rows if line.split()[4] == '/proc')
        cases = [raw + '9999 9998 0:9 / /escape rw - tmpfs tmpfs rw\n',
                 raw + '9999 9998 0:9 / /proc/sys ro - proc proc rw\n',
                 raw.replace(proc, proc.replace(' - proc ', ' - tmpfs ')),
                 raw.replace(proc, proc.replace('noexec,', '').replace(',noexec', '')),
                 raw.replace(proc, proc.replace(' rw,', ' ro,', 1))]
        for bad in cases:
            with self.subTest(mountinfo=bad), self.assertRaises(RuntimeError):
                probe.mount_coverage(bad, usable_devices=True, nested_userns=True)
        for flag in ('true', 1, None):
            with self.subTest(flag=flag), self.assertRaisesRegex(RuntimeError, 'must be a boolean'):
                probe.mount_coverage(raw, usable_devices=True, nested_userns=flag)

    def test_capable_peer_is_not_released(self):
        before=set(os.listdir('/proc/self/fd'))
        with self.assertRaisesRegex(TaskCaptureError, 'supervised-capture-exited-without-finish'):
            self.exercise(retain_capability=True)
        self.assertEqual(before,set(os.listdir('/proc/self/fd')))
