"""Task-input identity and failure ownership, including a blocked repair namespace."""

import array
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import tempfile
import unittest
from unittest.mock import patch

from caplab.process_capture import capture_process, seal_capture_json
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureError, TaskCaptureLimits
from caplab.task_capture_verify import CaptureVerificationError, verify_task_capture
from caplab.task_input import prepare_task_input, materialize_task_input, verify_task_input


WORLD = Path(__file__).parents[1] / 'docs/product/studies/advisory-selection-001/development-worlds/atomic-transfer-v1'
PRODUCER = """import array,os,shutil,socket
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
    channel.settimeout(3);channel.connect('/handoff.sock')
    fd=os.open('/work',os.O_RDONLY|os.O_DIRECTORY)
    try:channel.sendmsg([b'R'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd]))])
    finally:os.close(fd)
    if channel.recv(1)!=b'1':raise RuntimeError('input not accepted')
shutil.copyfile('/repair.py','/work/transfer.py')
print('authored repair applied')
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def namespace_fixture(root):
    root.mkdir(mode=0o700)
    source=root/'source';source.mkdir()
    shutil.copyfile(WORLD/'TASK.md',source/'TASK.md')
    shutil.copyfile(WORLD/'parent/transfer.py',source/'transfer.py')
    (source/'!first').write_bytes(b'\x00\xff task identity sentinel')
    bundle=root/'input'
    input_sha=prepare_task_input(source,output_dir=bundle,max_task_bytes=100000,max_task_entries=100)
    expected={p.name:p.read_bytes() for p in source.iterdir()}
    shutil.rmtree(source)
    launch=root/'launch';launch.mkdir()
    socket_path=root/'handoff.sock';attempt=root/'attempt'
    command=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv',
        '--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib',
        '--symlink','usr/lib64','/lib64','--size','1048576','--tmpfs','/work',
        '--ro-bind',str(WORLD/'repairs/transaction.py'),'/repair.py','--ro-bind',str(socket_path),'/handoff.sock',
        '--chdir','/work','--remount-ro','/','--','/usr/bin/python3','-B','-c',PRODUCER]
    fds=[]
    try:
        with SupervisedTaskCapture(command,task_root=launch,namespace_root='/work',environment={'PATH':'/usr/bin:/bin'},
                output_dir=attempt,limits=TaskCaptureLimits(100000,200000,200,5),max_process_receipt_bytes=10000) as recorder:
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as listener:
                listener.bind(str(socket_path));listener.listen(1);listener.settimeout(5)
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future=pool.submit(capture_process,command,cwd=launch,environment={'PATH':'/usr/bin:/bin'},
                        output_dir=attempt/'process',max_stream_bytes=100000,timeout_seconds=5)
                    channel,_=listener.accept()
                    with channel:
                        data,ancillary,flags,_=channel.recvmsg(1,socket.CMSG_SPACE(array.array('i').itemsize),socket.MSG_CMSG_CLOEXEC)
                        for level,kind,raw in ancillary:
                            if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
                                received=array.array('i');received.frombytes(raw);fds.extend(received)
                        assert data==b'R' and flags & ~socket.MSG_CMSG_CLOEXEC==0 and len(fds)==1
                        info=os.fstat(fds[0])
                        materialized=materialize_task_input(bundle,fds[0],expected_input_sha256=input_sha,
                            expected_device=info.st_dev,expected_inode=info.st_ino,max_receipt_bytes=100000)
                        materialization_sha=seal_capture_json(root,'materialization.json',materialized)
                        before_sha=recorder.capture_before(fds[0],expected_device=info.st_dev,expected_inode=info.st_ino)
                        seal_capture_json(root,'before-release.json',{'input_sha256':input_sha,
                            'materialization_sha256':materialization_sha,'before_inventory_sha256':before_sha})
                        channel.sendall(b'1')
                    process=future.result(timeout=7)
            assert process['return_code']==0
            recorder.finish(expected_process_sha256=digest(attempt/'process/capture.json'))
    finally:
        for fd in fds:os.close(fd)
        socket_path.unlink(missing_ok=True)
    for phase in ('before','after'):
        inventory=json.loads((attempt/phase/'inventory.json').read_bytes())
        for entry in inventory['entries']:
            if entry['kind']=='file':
                raw=(attempt/phase/entry['object']).read_bytes()
                wanted=(WORLD/'repairs/transaction.py').read_bytes() if phase=='after' and entry['path']=='transfer.py' else expected[entry['path']]
                assert raw==wanted
    inspected=verify_task_capture(attempt,expected_attempt_sha256=digest(attempt/'attempt.json'),max_receipt_bytes=100000)
    return {'input_sha256':input_sha,'materialization':materialized,'task_capture':inspected,
            'source_removed':not source.exists(),'native_execution':False}


class TaskInputTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=self.root/'source';self.source.mkdir()
        (self.source/'!first').write_bytes(b'\x00\xffpayload')
        (self.source/'empty').mkdir(mode=0o750)
        (self.source/'run').write_bytes(b'#!/bin/sh\nexit 0\n');(self.source/'run').chmod(0o751)
        (self.source/os.fsdecode(b'raw-\xfe')).write_bytes(b'\xfe')
        os.symlink(b'../\xff-unavailable',os.fsencode(self.source/'link'))
        self.bundle=self.root/'input'
        self.sha=prepare_task_input(self.source,output_dir=self.bundle,max_task_bytes=1000,max_task_entries=20)
        self.target=self.root/'target';self.target.mkdir()
        self.fd=os.open(self.target,os.O_RDONLY|os.O_DIRECTORY);self.addCleanup(os.close,self.fd)
        info=os.fstat(self.fd)
        self.options=dict(expected_input_sha256=self.sha,expected_device=info.st_dev,expected_inode=info.st_ino,max_receipt_bytes=100000)

    def materialize(self,**changes):
        return materialize_task_input(self.bundle,self.fd,**(self.options|changes))

    def test_bytes_links_modes_and_empty_directories_survive_source_removal(self):
        inspected=verify_task_input(self.bundle,expected_input_sha256=self.sha,max_receipt_bytes=100000)
        shutil.rmtree(self.source)
        report=self.materialize()
        self.assertEqual(report['task_content_sha256'],inspected['task_content_sha256'])
        self.assertEqual((self.target/'!first').read_bytes(),b'\x00\xffpayload')
        self.assertEqual((self.target/os.fsdecode(b'raw-\xfe')).read_bytes(),b'\xfe')
        self.assertEqual(os.fsencode(os.readlink(self.target/'link')),b'../\xff-unavailable')
        self.assertEqual(stat.S_IMODE((self.target/'run').stat().st_mode),0o751)
        self.assertEqual(stat.S_IMODE((self.target/'empty').stat().st_mode),0o750)
        self.assertEqual(list((self.target/'empty').iterdir()),[])
        self.assertFalse(report['study_eligible'])

    def test_wrong_anchor_payload_and_receipt_allowance_refuse_before_destination_writes(self):
        before=set(os.listdir('/proc/self/fd'))
        with self.assertRaises(CaptureVerificationError):self.materialize(expected_input_sha256='0'*64)
        count=sum((self.bundle/p).stat().st_size for p in ('input.json','inventory/inventory.json'))
        self.assertEqual(verify_task_input(self.bundle,expected_input_sha256=self.sha,max_receipt_bytes=count)['verified_receipt_bytes'],count)
        with self.assertRaises(CaptureVerificationError):self.materialize(max_receipt_bytes=count-1)
        inv=json.loads((self.bundle/'inventory/inventory.json').read_bytes())
        file=next(e for e in inv['entries'] if e['kind']=='file')
        (self.bundle/'inventory'/file['object']).write_bytes(b'corrupt')
        with self.assertRaises(CaptureVerificationError):self.materialize()
        self.assertEqual(list(self.target.iterdir()),[])
        self.assertEqual(set(os.listdir('/proc/self/fd')),before)

    def test_rehashed_unsupported_permissions_are_rejected_before_creation(self):
        original=(self.bundle/'inventory/inventory.json').read_bytes()
        receipt=json.loads((self.bundle/'input.json').read_bytes())
        for kind,mode in (('file',0o4755),('file',0o000),('directory',0o400),('symlink',0o700)):
            with self.subTest(kind=kind,mode=mode):
                inv=json.loads(original);entry=next(e for e in inv['entries'] if e['kind']==kind);entry['mode']=mode
                raw=json.dumps(inv).encode();(self.bundle/'inventory/inventory.json').write_bytes(raw)
                receipt['inventory_sha256']=hashlib.sha256(raw).hexdigest()
                raw=json.dumps(receipt).encode();(self.bundle/'input.json').write_bytes(raw)
                with self.assertRaisesRegex(CaptureVerificationError,'task input .*'):
                    self.materialize(expected_input_sha256=hashlib.sha256(raw).hexdigest())
                self.assertEqual(list(self.target.iterdir()),[])

    def test_nonempty_identity_and_overlapping_destinations_preserve_existing_state(self):
        before=set(os.listdir('/proc/self/fd'))
        for changes in ({'expected_inode':self.options['expected_inode']+1},{'expected_device':True}):
            with self.assertRaises(CaptureVerificationError):self.materialize(**changes)
        (self.target/'keep').write_bytes(b'keep')
        with self.assertRaises((CaptureVerificationError,TaskCaptureError)):self.materialize()
        self.assertEqual((self.target/'keep').read_bytes(),b'keep')
        nested=self.bundle/'nested';nested.mkdir()
        for path in (self.bundle,nested,self.root):
            fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
            try:
                info=os.fstat(fd)
                with self.assertRaisesRegex(CaptureVerificationError,'overlaps'):
                    materialize_task_input(self.bundle,fd,**(self.options|{'expected_device':info.st_dev,'expected_inode':info.st_ino}))
            finally:os.close(fd)
        self.assertEqual(set(os.listdir('/proc/self/fd')),before)

    def test_input_quota_failure_and_output_sync_failure_preserve_partial_custody(self):
        for name,limits in (('bytes',{'max_task_bytes':1,'max_task_entries':20}),('entries',{'max_task_bytes':1000,'max_task_entries':1})):
            with self.assertRaises(TaskCaptureError):prepare_task_input(self.source,output_dir=self.root/name,**limits)
            self.assertFalse((self.root/name/'input.json').exists())
        before=set(os.listdir('/proc/self/fd'))
        # The filesystem durability boundary fails after creation; no internal component is mocked.
        with patch('caplab.task_input.os.fsync',side_effect=OSError('synthetic sync failure')):
            with self.assertRaisesRegex(OSError,'synthetic sync failure'):self.materialize()
        self.assertTrue((self.target/'!first').exists())
        self.assertEqual(set(os.listdir('/proc/self/fd')),before)
        with self.assertRaises((CaptureVerificationError,TaskCaptureError)):self.materialize()

    def test_final_tree_check_refuses_changed_payload_and_unexpected_entries(self):
        real_sync=os.fsync
        for kind in ('payload','extra'):
            with self.subTest(kind=kind):
                target=self.root/('changed-'+kind);target.mkdir()
                fd=os.open(target,os.O_RDONLY|os.O_DIRECTORY);info=os.fstat(fd)
                changed=False
                def sync_then_change(handle):
                    nonlocal changed
                    real_sync(handle)
                    if not changed and stat.S_ISREG(os.fstat(handle).st_mode):
                        changed=True
                        (target/('!first' if kind=='payload' else 'unexpected')).write_bytes(b'altered')
                try:
                    # Corruption at the filesystem boundary must be caught by the final readback.
                    with patch('caplab.task_input.os.fsync',side_effect=sync_then_change):
                        with self.assertRaises((CaptureVerificationError,TaskCaptureError)):
                            materialize_task_input(self.bundle,fd,**(self.options|{
                                'expected_device':info.st_dev,'expected_inode':info.st_ino}))
                    self.assertTrue(changed)
                    self.assertEqual(os.fstat(fd).st_ino,info.st_ino)
                finally:os.close(fd)

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(),'Bubblewrap required for namespace integration')
    def test_frozen_input_is_materialized_before_blocked_repair_and_capture_handles_punctuation(self):
        result=namespace_fixture(self.root/'namespace')
        self.assertTrue(result['source_removed'])
        self.assertTrue(result['task_capture']['capture_complete'])
        self.assertEqual([c['path'] for c in result['task_capture']['changes']],['transfer.py'])
