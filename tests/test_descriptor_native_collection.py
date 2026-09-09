"""New synthetic captures exercise descriptor custody; no native harness runs."""

import hashlib
import array
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import unittest

from caplab.capture_accounting import build_capture_byte_report
from caplab.claude_capture_link import link_claude_root
from caplab.codex_capture_link import link_codex_final_message
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import NativeCollectionError, NativeRuntimeDescriptor, collect_native_outputs
from caplab.native_collection_verify import verify_native_collection
from caplab.native_runtime import prepare_native_runtime
from caplab.task_capture import TaskCaptureError, TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import CaptureVerificationError
from test_claude_capture_link import SESSION, stdout_events, transcript_events
from test_codex_capture_link import NAME, jsonl, rollout


POLICY = Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DescriptorCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def prepare(self, harness='codex'):
        self.task = self.root / 'task'; self.task.mkdir()
        self.prepared = self.root / 'prepared'
        self.plan = build_native_capture_invocation(POLICY,
            'codex-terra-max' if harness == 'codex' else 'claude-fable-5-max',
            context=NativeCaptureContext('/work', '/episode', b'synthetic descriptor fixture',
                                         None if harness == 'codex' else SESSION))
        prep = prepare_native_runtime(POLICY, self.plan, expected_invocation_sha256=self.plan['invocation_sha256'],
                                      task_root=self.task, output_dir=self.prepared)
        self.anchor = digest(self.prepared / 'preparation.json')
        self.paths = {k: Path(v) for k, v in prep['capture_paths'].items()}
        self.fd = os.open(self.prepared / 'runtime', os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.fd)
        info = os.fstat(self.fd)
        self.descriptor = NativeRuntimeDescriptor(self.fd, info.st_dev, info.st_ino)

    def collect(self, name='collection', **changes):
        options = dict(expected_preparation_sha256=self.anchor, output_dir=self.root / name,
                       max_receipt_bytes=100000, max_artifact_bytes=10000, max_entries=100,
                       runtime_descriptor=self.descriptor)
        options.update(changes)
        return collect_native_outputs(POLICY, self.prepared, **options)

    def verify(self, root=None):
        root = self.root / 'collection' if root is None else root
        return verify_native_collection(POLICY, root, expected_collection_sha256=digest(root / 'collection.json'),
                                         max_receipt_bytes=200000)

    def test_moved_runtime_ignores_replacement_host_path_and_preserves_binary_sources(self):
        self.prepare()
        (self.paths['session_search_root'] / 'raw').write_bytes(b'\xff\x00\r\n')
        (self.paths['session_search_root'] / 'link').symlink_to('/not-read')
        (self.prepared / 'runtime').rename(self.root / 'detached')
        (self.prepared / 'runtime').mkdir()
        (self.prepared / 'runtime/final-message.txt').write_bytes(b'decoy')
        before = set(os.listdir('/proc/self/fd'))
        collected = self.collect()
        self.assertEqual(before, set(os.listdir('/proc/self/fd')))
        self.assertEqual(os.fstat(self.fd).st_ino, self.descriptor.inode)
        self.assertEqual(collected['schema'], 'caplab.native-output-collection/v2')
        self.assertEqual(collected['missing_locations'], ['final_message'])
        entry, = [e for e in collected['entries'] if e['kind'] == 'file']
        self.assertEqual((self.root / 'collection/objects' / entry['object']).read_bytes(), b'\xff\x00\r\n')
        self.assertTrue(any(e['kind'] == 'symlink' for e in collected['entries']))
        self.assertTrue(all(i['source'].startswith('/episode/') for i in collected['locations']))
        shutil.rmtree(self.root / 'detached'); shutil.rmtree(self.prepared)
        check = self.verify()
        self.assertEqual(check['runtime_source'], {'kind': 'directory-descriptor', 'namespace_root': '/episode',
                         'device': self.descriptor.device, 'inode': self.descriptor.inode})
        self.assertFalse(check['native_identity_verified'])
        self.assertIsNone(check['native_capture_complete'])

    def test_identity_and_output_overlap_refuse_before_custody_without_closing_borrowed_fd(self):
        self.prepare()
        before = set(os.listdir('/proc/self/fd'))
        for index, source in enumerate((NativeRuntimeDescriptor(self.fd, self.descriptor.device, self.descriptor.inode+1),
                                       NativeRuntimeDescriptor(self.fd, self.descriptor.device+1, self.descriptor.inode),
                                       123)):
            with self.subTest(source=source), self.assertRaises(NativeCollectionError):
                self.collect(str(index), runtime_descriptor=source)
            self.assertFalse((self.root / str(index)).exists())
        detached = self.root / 'detached'; (self.prepared / 'runtime').rename(detached)
        with self.assertRaisesRegex(NativeCollectionError, 'outside-descriptor-runtime'):
            self.collect(output_dir=detached / 'output')
        self.assertFalse((detached / 'output').exists())
        self.assertEqual(before, set(os.listdir('/proc/self/fd')))
        self.assertEqual(os.fstat(self.fd).st_ino, self.descriptor.inode)

    def test_invalid_and_nondirectory_descriptors_refuse(self):
        for fields in ((True, 0, 1), (1, False, 1), (1, 1, 0), (-1, 1, 1), (1, 1, 1.0)):
            with self.subTest(fields=fields), self.assertRaises(NativeCollectionError):
                NativeRuntimeDescriptor(*fields)
        self.prepare()
        path = self.root / 'file'; path.write_bytes(b'not a directory')
        fd = os.open(path, os.O_RDONLY)
        try:
            info = os.fstat(fd)
            source = NativeRuntimeDescriptor(fd, info.st_dev, info.st_ino)
            with self.assertRaisesRegex(NativeCollectionError, 'identity-differs'):
                self.collect(runtime_descriptor=source)
        finally:
            os.close(fd)
        # Opening source receipts may reuse this closed descriptor number.
        with self.assertRaises((OSError, NativeCollectionError)):
            self.collect(runtime_descriptor=source)
        self.assertFalse((self.root / 'collection').exists())

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'Bubblewrap required for detached mount fixture')
    def test_collects_private_tmpfs_after_its_namespace_process_exits(self):
        self.prepare()
        payload = b'synthetic detached diagnostic\x00\xff'
        producer = """import array,os,socket
from pathlib import Path
Path('/episode/codex/sessions').mkdir(parents=True)
Path('/episode/codex/log').mkdir()
Path('/episode/codex/log/raw').write_bytes(b'synthetic detached diagnostic\\x00\\xff')
fd = os.open('/episode', os.O_RDONLY | os.O_DIRECTORY)
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
    channel.connect('/handoff.sock')
    channel.sendmsg([b'R'], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', [fd]))])
os.close(fd)
"""
        handoff = self.root / 'handoff.sock'
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
            listener.bind(str(handoff)); listener.listen(1); listener.settimeout(5)
            command = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
                '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
                '--symlink', 'usr/lib64', '/lib64', '--size', '1048576', '--tmpfs', '/episode',
                '--ro-bind', str(handoff), '/handoff.sock', '--chdir', '/episode', '--remount-ro', '/',
                '--', '/usr/bin/python3', '-B', '-c', producer]
            descriptors = []
            process = subprocess.Popen(command, env={'PATH': '/usr/bin:/bin'}, start_new_session=True,
                                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                channel, _ = listener.accept()
                with channel:
                    channel.settimeout(5)
                    data, ancillary, flags, _ = channel.recvmsg(1, socket.CMSG_SPACE(array.array('i').itemsize),
                                                               socket.MSG_CMSG_CLOEXEC)
                    for level, kind, raw in ancillary:
                        if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                            received = array.array('i'); received.frombytes(raw)
                            descriptors.extend(received)
                    self.assertEqual(data, b'R')
                    self.assertEqual(flags & ~socket.MSG_CMSG_CLOEXEC, 0)
                    self.assertEqual(len(descriptors), 1)
                self.assertEqual(process.wait(timeout=5), 0)
                descriptor, = descriptors
                info = os.fstat(descriptor)
                source = NativeRuntimeDescriptor(descriptor, info.st_dev, info.st_ino)
                self.assertNotEqual(source, self.descriptor)
                self.assertEqual(os.fstatvfs(descriptor).f_blocks * os.fstatvfs(descriptor).f_frsize, 1048576)
                collected = self.collect(runtime_descriptor=source)
                entry, = [e for e in collected['entries'] if e['kind'] == 'file']
                self.assertEqual((self.root/'collection/objects'/entry['object']).read_bytes(), payload)
                self.assertEqual(self.verify()['runtime_source']['inode'], source.inode)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
                for descriptor in descriptors:
                    os.close(descriptor)

    def test_shared_quotas_preserve_partial_output_and_borrowed_descriptor(self):
        self.prepare()
        self.paths['final_message'].write_bytes(b'1234')
        (self.paths['session_search_root'] / 'raw').write_bytes(b'56789')
        before = set(os.listdir('/proc/self/fd'))
        with self.assertRaisesRegex(TaskCaptureError, 'task-byte-limit'):
            self.collect(max_artifact_bytes=7)
        self.assertEqual(sum(p.stat().st_size for p in (self.root/'collection/objects').iterdir()), 7)
        self.assertFalse((self.root / 'collection/collection.json').exists())
        with self.assertRaisesRegex(TaskCaptureError, 'task-entry-limit'):
            self.collect('entries', max_entries=1)
        self.assertFalse((self.root / 'entries/collection.json').exists())
        self.assertEqual(before, set(os.listdir('/proc/self/fd')))
        self.collect('exact', max_artifact_bytes=9, max_entries=4)
        self.assertEqual(self.verify(self.root/'exact')['retained_artifact_bytes'], 9)

    def test_v2_provenance_and_version_tampering_refuse_after_rehash(self):
        self.prepare(); self.collect()
        for index, change in enumerate((
            lambda i: i.pop('runtime_source'),
            lambda i: i['runtime_source'].update(inode=True),
            lambda i: i['runtime_source'].update(inode=0),
            lambda i: i['runtime_source'].update(device=-1),
            lambda i: i['runtime_source'].update(kind='host-path'),
            lambda i: i['runtime_source'].update(namespace_root='/other'),
            lambda i: i['runtime_source'].update(extra='unknown'),
            lambda i: i.update(schema='caplab.native-collection-intent/v1'),
            lambda i: i['capture_paths'].update(final_message=str(self.paths['final_message'])),
        )):
            with self.subTest(index=index):
                target = self.root / ('tampered-' + str(index))
                shutil.copytree(self.root / 'collection', target)
                intent = json.loads((target / 'intent.json').read_bytes()); change(intent)
                (target / 'intent.json').write_text(json.dumps(intent))
                collection = json.loads((target / 'collection.json').read_bytes())
                collection['intent_sha256'] = digest(target / 'intent.json')
                (target / 'collection.json').write_text(json.dumps(collection))
                with self.assertRaises(CaptureVerificationError):
                    self.verify(target)

    def test_payload_corruption_is_not_hidden_by_descriptor_provenance(self):
        self.prepare(); self.paths['final_message'].write_bytes(b'original')
        self.collect()
        payload, = (self.root/'collection/objects').iterdir()
        payload.write_bytes(b'changed!')
        with self.assertRaisesRegex(CaptureVerificationError, 'payload size or hash mismatch'):
            self.verify()

    def test_both_harness_links_and_accounting_survive_source_removal(self):
        for harness in ('codex', 'claude'):
            with self.subTest(harness=harness):
                original = self.root
                self.root = original / harness; self.root.mkdir()
                self.prepare(harness)
                if harness == 'codex':
                    message = 'synthetic résumé\u2028only'
                    stdout = jsonl([{'type': 'thread.started', 'thread_id': 'root-A'}, {'type': 'turn.started'},
                        {'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'final', 'text': message}},
                        {'type': 'turn.completed'}])
                    (self.paths['session_search_root'] / NAME).write_bytes(rollout())
                    self.paths['final_message'].write_bytes(message.encode())
                    linker = link_codex_final_message
                else:
                    stdout = jsonl(stdout_events())
                    project = self.paths['session_search_root'] / '-work'; project.mkdir()
                    (project / (SESSION + '.jsonl')).write_bytes(jsonl(transcript_events()))
                    linker = link_claude_root
                for name, path in self.paths.items():
                    if name.startswith('diagnostic'):
                        (path / 'log' if name.endswith('_root') else path).write_bytes(b'\x00\xffdiagnostic')
                capture_task_attempt([sys.executable, '-B', '-c',
                    'import sys;sys.stdout.buffer.write(bytes.fromhex(sys.argv[1]));raise SystemExit(7)', stdout.hex()],
                    task_root=self.task, environment={'PATH': '/usr/bin:/bin'}, output_dir=self.root/'attempt',
                    limits=TaskCaptureLimits(10000, 10000, 100, 5))
                (self.prepared/'runtime').rename(self.root/'detached')
                self.collect()
                options = dict(task_custody=self.root/'attempt', collection_custody=self.root/'collection',
                    expected_attempt_sha256=digest(self.root/'attempt/attempt.json'),
                    expected_collection_sha256=digest(self.root/'collection/collection.json'), max_receipt_bytes=200000)
                shutil.rmtree(self.root/'detached'); shutil.rmtree(self.prepared); shutil.rmtree(self.task)
                linked = linker(POLICY, **options, max_identity_bytes=10000)
                fields = linked.get('root_link', linked)
                counted = build_capture_byte_report(POLICY, **options)
                self.assertEqual(fields['runtime_source'], counted['runtime_source'])
                self.assertEqual(fields['runtime_source']['inode'], self.descriptor.inode)
                self.assertEqual(fields['process_return_code'], 7)
                self.assertFalse(fields['executed_invocation_bound'])
                self.assertIsNone(fields['native_capture_complete'])
                self.assertEqual(counted['return_code'], 7)
                self.assertGreater(counted['retained_logical_payload_bytes'], len(stdout))
                self.root = original
