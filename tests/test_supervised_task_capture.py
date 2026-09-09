"""Fixed local task/native-format fixtures; no native model execution."""

import array
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import unittest

from caplab.capture_accounting import build_capture_byte_report
from caplab.claude_capture_link import link_claude_root
from caplab.codex_capture_link import link_codex_final_message
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import NativeRuntimeDescriptor, collect_native_outputs
from caplab.native_runtime import prepare_native_runtime
from caplab.native_tool_pairs import inspect_captured_tool_pairs
from caplab.process_capture import capture_process
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureError, TaskCaptureLimits
from caplab.task_capture_verify import CaptureVerificationError, verify_task_capture
from test_claude_capture_link import SESSION, stdout_events, transcript_events
from test_codex_capture_link import NAME, jsonl, rollout


POLICY = Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'
PRODUCER = """import array,json,os,socket,sys
from pathlib import Path
data = json.loads(Path('/fixture/payload.json').read_bytes())
Path('/work/item').write_bytes(b'old')
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
    channel.settimeout(3)
    channel.connect('/handoff.sock')
    descriptors = [os.open(p, os.O_RDONLY | os.O_DIRECTORY) for p in data['mounts']]
    channel.sendmsg([b'R'], [(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',descriptors))])
    for descriptor in descriptors: os.close(descriptor)
    if channel.recv(1) != b'1': raise RuntimeError('before capture not acknowledged')
Path('/work/item').write_bytes(b'changed')
for path, raw in data['markers'].items():
    Path(path, 'marker.bin').write_bytes(bytes.fromhex(raw))
for name, raw in data['files'].items():
    target = Path('/episode') / name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(bytes.fromhex(raw))
for name, raw in data['extra_files'].items():
    target = Path(name)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(bytes.fromhex(raw))
sys.stdout.buffer.write(bytes.fromhex(data['stdout']) + bytes.fromhex(data['stdout_suffix']))
raise SystemExit(data['return_code'])
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retained_fixture(root, harness, return_code, *, quarantine_factory=None, mount_retainer=None,
                     extra_files=None, stdout_suffix=b''):
    root.mkdir(mode=0o700)
    task = root/'task'; task.mkdir()
    fixture = root/'fixture'; fixture.mkdir()
    plan = build_native_capture_invocation(POLICY,
        'codex-terra-max' if harness == 'codex' else 'claude-fable-5-max',
        context=NativeCaptureContext('/work','/episode',b'synthetic supervised task',None if harness=='codex' else SESSION))
    prepared = root/'prepared'
    prep = prepare_native_runtime(POLICY,plan,expected_invocation_sha256=plan['invocation_sha256'],
                                  task_root=task,output_dir=prepared)
    preparation_hash = digest(prepared/'preparation.json')
    paths = {name: str(Path(path).relative_to(prepared/'runtime')) for name,path in prep['capture_paths'].items()}
    if harness == 'codex':
        message = 'synthetic résumé\u2028only'
        stdout = jsonl([{'type':'thread.started','thread_id':'root-A'},{'type':'turn.started'},
            {'type':'item.completed','item':{'id':'final','type':'agent_message','text':message}},
            {'type':'turn.completed'}])
        files = {paths['session_search_root']+'/'+NAME:rollout(),paths['final_message']:message.encode(),
                 paths['diagnostic_search_root']+'/raw':b'\x00\xffdiagnostic'}
    else:
        stdout = jsonl(stdout_events())
        files = {paths['session_search_root']+'/-work/'+SESSION+'.jsonl':jsonl(transcript_events()),
                 paths['diagnostic_file']:b'\x00\xffdiagnostic'}
    mounts = ('/scratch', '/tmp', '/dev/shm', '/work', '/episode') if mount_retainer else ('/work', '/episode')
    extra_files = {} if extra_files is None else dict(extra_files)
    assert all(any(Path(path).is_relative_to(mount) and path != mount for mount in mounts)
               and '..' not in Path(path).parts and isinstance(raw, bytes) for path, raw in extra_files.items())
    assert isinstance(stdout_suffix, bytes)
    markers = {path: (b'retained marker\x00\xff\n' + path.encode()).hex() for path in mounts} if mount_retainer else {}
    (fixture/'payload.json').write_text(json.dumps({'files':{k:v.hex() for k,v in files.items()},
        'stdout':stdout.hex(),'return_code':return_code,'mounts':mounts,'markers':markers,
        'extra_files':{path:raw.hex() for path,raw in extra_files.items()},'stdout_suffix':stdout_suffix.hex()}))
    (fixture/'producer.py').write_text(PRODUCER)
    socket_path = root/'handoff.sock'
    command = ['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv',
        '--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib',
        '--symlink','usr/lib64','/lib64']
    for mount in mounts:
        command += ['--size','1048576','--tmpfs',mount]
    command += ['--ro-bind',str(fixture),'/fixture',
        '--ro-bind',str(socket_path),'/handoff.sock','--chdir','/work','--remount-ro','/',
        '--','/usr/bin/python3','-B','/fixture/producer.py']
    environment = {'PATH':'/usr/bin:/bin'}
    attempt = root/'attempt'; collection = root/'collection'
    descriptors = []
    full_retention = None
    try:
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as listener:
            listener.bind(str(socket_path)); listener.listen(1); listener.settimeout(5)
            with SupervisedTaskCapture(command,task_root=task,namespace_root='/work',environment=environment,
                    output_dir=attempt,limits=TaskCaptureLimits(100000,10000,100,5),
                    max_process_receipt_bytes=10000,quarantine_factory=quarantine_factory) as recorder:
                assert (attempt/'intent.json').is_file()
                with ThreadPoolExecutor(max_workers=1) as pool:
                    pending = pool.submit(capture_process,command,cwd=task,environment=environment,
                        output_dir=attempt/'process',max_stream_bytes=100000,timeout_seconds=5,
                        quarantine_factory=quarantine_factory)
                    channel,_ = listener.accept()
                    with channel:
                        channel.settimeout(5)
                        data,ancillary,flags,_ = channel.recvmsg(1,socket.CMSG_SPACE(len(mounts)*array.array('i').itemsize),
                                                                 socket.MSG_CMSG_CLOEXEC)
                        for level,kind,raw in ancillary:
                            if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
                                received=array.array('i'); received.frombytes(raw); descriptors.extend(received)
                        assert data==b'R' and flags & ~socket.MSG_CMSG_CLOEXEC==0 and len(descriptors)==len(mounts)
                        task_descriptor=descriptors[mounts.index('/work')]
                        info=os.fstat(task_descriptor)
                        before_hash=recorder.capture_before(task_descriptor,expected_device=info.st_dev,expected_inode=info.st_ino)
                        assert before_hash==digest(attempt/'before/inventory.json')
                        channel.sendall(b'1')
                    process=pending.result(timeout=7)
                receipt=recorder.finish(expected_process_sha256=digest(attempt/'process/capture.json'))
                assert process['return_code']==return_code and receipt['process']==process
                native_descriptor=descriptors[mounts.index('/episode')]
                info=os.fstat(native_descriptor)
                collect_native_outputs(POLICY,prepared,expected_preparation_sha256=preparation_hash,
                    output_dir=collection,max_receipt_bytes=100000,max_artifact_bytes=10000,max_entries=100,
                    runtime_descriptor=NativeRuntimeDescriptor(native_descriptor,info.st_dev,info.st_ino),
                    quarantine_factory=quarantine_factory)
            if mount_retainer is not None:
                retained = root/'fixture-retained'; retained.mkdir(mode=0o700)
                identities, inventories = [], []
                bytes_left, entries_left = 40*1024*1024, 100
                for index, (mount, descriptor) in enumerate(zip(mounts, descriptors, strict=True)):
                    info = os.fstat(descriptor)
                    identity = {'source_root':mount,'source_dev':info.st_dev,'source_ino':info.st_ino}
                    sha, bytes_left, entries_left = mount_retainer(descriptor,retained/str(index),identity,
                        bytes_left,entries_left,quarantine_factory=quarantine_factory)
                    identities.append(identity)
                    inventories.append({'source_root':mount,'inventory_sha256':sha})
                full_retention = {'mode':'fixture','inventories':inventories,'mount_descriptor':{'mounts':identities},
                    'retained_bytes':40*1024*1024-bytes_left,'retained_entries':100-entries_left}
    finally:
        for descriptor in descriptors: os.close(descriptor)
        socket_path.unlink(missing_ok=True)
    options=dict(task_custody=attempt,collection_custody=collection,
        expected_attempt_sha256=digest(attempt/'attempt.json'),expected_collection_sha256=digest(collection/'collection.json'),
        max_receipt_bytes=200000)
    for source in (task,prepared,fixture): shutil.rmtree(source)
    for phase, expected in (('before',b'old'),('after',b'changed')):
        inventory=json.loads((attempt/phase/'inventory.json').read_bytes())
        item,=[e for e in inventory['entries'] if e['path']=='item']
        assert (attempt/phase/item['object']).read_bytes()==expected
    linker=link_codex_final_message if harness=='codex' else link_claude_root
    linked=linker(POLICY,**options,max_identity_bytes=10000)
    counted=build_capture_byte_report(POLICY,**options)
    pairs=inspect_captured_tool_pairs(attempt,expected_attempt_sha256=options['expected_attempt_sha256'],
        format='codex-exec-jsonl' if harness=='codex' else 'claude-stream-jsonl',
        expected_root_id='root-A' if harness=='codex' else SESSION,max_receipt_bytes=200000,max_event_bytes=10000)
    return {'harness_layout':harness,'configured_process_return_code':return_code,'anchors':options,
            'link':linked,'accounting':counted,'pairs':pairs,'native_execution':False,
            **({'full_retention':full_retention} if full_retention is not None else {})}


class SupervisedTaskCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.task=self.root/'task'; self.task.mkdir(); (self.task/'item').write_bytes(b'old')
        self.fd=os.open(self.task,os.O_RDONLY|os.O_DIRECTORY); self.addCleanup(os.close,self.fd)
        self.info=os.fstat(self.fd)
        self.command=[sys.executable,'-B','-c',"from pathlib import Path;Path('item').write_bytes(b'changed');raise SystemExit(7)"]

    def recorder(self,name='attempt',**changes):
        options=dict(task_root=self.task,namespace_root='/work',environment={'PATH':'/usr/bin:/bin'},
            output_dir=self.root/name,limits=TaskCaptureLimits(100000,10000,100,5),max_process_receipt_bytes=10000)
        options.update(changes)
        return SupervisedTaskCapture(self.command,**options)

    def before(self,recorder,**changes):
        options=dict(expected_device=self.info.st_dev,expected_inode=self.info.st_ino); options.update(changes)
        return recorder.capture_before(self.fd,**options)

    def process(self,recorder):
        capture_process(self.command,cwd=self.task,environment={'PATH':'/usr/bin:/bin'},
            output_dir=recorder.output_dir/'process',max_stream_bytes=100000,timeout_seconds=5)
        return digest(recorder.output_dir/'process/capture.json')

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(),'Bubblewrap required for supervised fixtures')
    def test_both_namespace_layouts_survive_success_and_failed_work_with_all_consumers(self):
        for harness in ('codex','claude'):
            for return_code in (0,7):
                with self.subTest(harness=harness,return_code=return_code):
                    report=retained_fixture(self.root/(harness+str(return_code)),harness,return_code)
                    fields=report['link'].get('root_link',report['link'])
                    self.assertEqual(fields['task_source']['namespace_root'],'/work')
                    self.assertEqual(fields['task_source'],report['accounting']['task_source'])
                    self.assertEqual(fields['process_return_code'],return_code)
                    self.assertFalse(fields['executed_invocation_bound'])
                    self.assertIsNone(fields['native_capture_complete'])
                    self.assertTrue(report['pairs']['tool_pairs_available'])
                    capture=report['pairs']['task_capture']
                    self.assertEqual(capture['retained_task_bytes'],10)
                    self.assertEqual(capture['retained_task_entries'],4)
                    self.assertEqual(capture['changes'],[{'path':'item','change':'modified','fields':['bytes','sha256']}])

    def test_unfinished_and_out_of_order_lifecycles_never_publish(self):
        for mode in ('no-before','no-finish','finish-first','before-twice'):
            with self.subTest(mode=mode),self.assertRaises(TaskCaptureError):
                with self.recorder(mode) as recorder:
                    if mode=='finish-first': recorder.finish(expected_process_sha256='0'*64)
                    if mode in ('no-finish','before-twice'): self.before(recorder)
                    if mode=='before-twice': self.before(recorder)
            self.assertFalse((self.root/mode/'attempt.json').exists())
        self.assertEqual(os.fstat(self.fd).st_ino,self.info.st_ino)

    def test_identity_and_quota_failures_keep_partial_custody_and_close_duplicates(self):
        before=set(os.listdir('/proc/self/fd'))
        for mode in ('identity','before-bytes','after-bytes','after-entries'):
            options={}
            if mode=='before-bytes': options['limits']=TaskCaptureLimits(100000,2,100,5)
            if mode=='after-bytes': options['limits']=TaskCaptureLimits(100000,5,100,5)
            if mode=='after-entries': options['limits']=TaskCaptureLimits(100000,10000,3,5)
            with self.subTest(mode=mode),self.assertRaises(TaskCaptureError):
                with self.recorder(mode,**options) as recorder:
                    self.before(recorder,**({'expected_inode':self.info.st_ino+1} if mode=='identity' else {}))
                    recorder.finish(expected_process_sha256=self.process(recorder))
            self.assertFalse((self.root/mode/'attempt.json').exists())
            (self.task/'item').write_bytes(b'old')
        self.assertEqual(before,set(os.listdir('/proc/self/fd')))

    def test_wrong_process_anchor_and_receipt_bound_refuse_before_after_inventory(self):
        for mode in ('anchor','receipt-limit'):
            with self.subTest(mode=mode),self.assertRaises(CaptureVerificationError):
                with self.recorder(mode,**({'max_process_receipt_bytes':1} if mode=='receipt-limit' else {})) as recorder:
                    self.before(recorder); anchor=self.process(recorder)
                    recorder.finish(expected_process_sha256='0'*64 if mode=='anchor' else anchor)
            self.assertFalse((self.root/mode/'after').exists())
            self.assertFalse((self.root/mode/'attempt.json').exists())

    def test_rehashed_inventory_identity_and_version_changes_refuse(self):
        with self.recorder() as recorder:
            self.before(recorder); recorder.finish(expected_process_sha256=self.process(recorder))
        for index,change in enumerate((lambda i:i['descriptor_identity'].update(inode=123),
            lambda i:i['entries'][0]['source_stat'].update(ino=True),
            lambda i:i.update(schema='caplab.task-inventory/v1'),lambda i:i.update(source_root='/other'))):
            target=self.root/('corrupt'+str(index)); shutil.copytree(self.root/'attempt',target)
            data=json.loads((target/'after/inventory.json').read_bytes()); change(data)
            (target/'after/inventory.json').write_text(json.dumps(data))
            attempt=json.loads((target/'attempt.json').read_bytes()); attempt['after_inventory_sha256']=digest(target/'after/inventory.json')
            (target/'attempt.json').write_text(json.dumps(attempt))
            with self.subTest(index=index),self.assertRaises(CaptureVerificationError):
                verify_task_capture(target,expected_attempt_sha256=digest(target/'attempt.json'),max_receipt_bytes=200000)

    def test_caught_order_violation_cannot_resume_the_same_recorder(self):
        with self.assertRaisesRegex(TaskCaptureError,'without-finish'):
            with self.recorder() as recorder:
                with self.assertRaisesRegex(TaskCaptureError,'finish-out-of-order'):
                    recorder.finish(expected_process_sha256='0'*64)
                with self.assertRaisesRegex(TaskCaptureError,'before-out-of-order'):
                    self.before(recorder)
        self.assertFalse((self.root/'attempt/before').exists())
        self.assertFalse((self.root/'attempt/attempt.json').exists())

    def test_boolean_after_inode_cannot_equal_integer_one_in_before_identity(self):
        with self.recorder() as recorder:
            self.before(recorder); recorder.finish(expected_process_sha256=self.process(recorder))
        root=self.root/'attempt'
        attempt=json.loads((root/'attempt.json').read_bytes())
        for phase in ('before','after'):
            path=root/phase/'inventory.json'
            inventory=json.loads(path.read_bytes())
            inventory['descriptor_identity']['inode']=1 if phase=='before' else True
            inventory['entries'][0]['source_stat']['ino']=1
            path.write_text(json.dumps(inventory))
            attempt[phase+'_inventory_sha256']=digest(path)
        (root/'attempt.json').write_text(json.dumps(attempt))
        with self.assertRaisesRegex(CaptureVerificationError,'after descriptor inode'):
            verify_task_capture(root,expected_attempt_sha256=digest(root/'attempt.json'),max_receipt_bytes=200000)
