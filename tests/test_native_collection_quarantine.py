from __future__ import annotations

import hashlib
import base64
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import NativeRuntimeDescriptor, collect_native_outputs
from caplab.native_collection_verify import verify_native_collection
from caplab.native_runtime import prepare_native_runtime
from caplab.revbench.codex import ExactSecretStreamQuarantine
from caplab.task_capture import TaskCaptureError


POLICY = Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'
SECRET = b'fabricated-collection-secret-only'


class RecordingGate(ExactSecretStreamQuarantine):
    def __init__(self):
        super().__init__((SECRET,))
        self.abandoned = False

    def abandon(self):
        super().abandon()
        self.abandoned = True


class NativeCollectionQuarantineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.task = self.root / 'task'
        self.task.mkdir()
        self.gates = []

    def factory(self):
        gate = RecordingGate()
        self.gates.append(gate)
        return gate

    def prepare(self, harness='codex', prompt=b'synthetic collection fixture'):
        self.prepared = self.root / harness
        plan = build_native_capture_invocation(POLICY,
            'codex-terra-max' if harness == 'codex' else 'claude-fable-5-max',
            context=NativeCaptureContext('/work', '/episode', prompt,
                None if harness == 'codex' else '11111111-2222-4333-8444-555555555555'))
        receipt = prepare_native_runtime(POLICY, plan, expected_invocation_sha256=plan['invocation_sha256'],
                                         task_root=self.task, output_dir=self.prepared)
        self.anchor = hashlib.sha256((self.prepared / 'preparation.json').read_bytes()).hexdigest()
        self.paths = {key: Path(value) for key, value in receipt['capture_paths'].items()}

    def collect(self, name='collected', **kwargs):
        options = dict(expected_preparation_sha256=self.anchor, output_dir=self.root / name,
                       max_receipt_bytes=100000, max_artifact_bytes=200000, max_entries=100,
                       quarantine_factory=self.factory)
        options.update(kwargs)
        return collect_native_outputs(POLICY, self.prepared, **options)

    def test_split_secret_is_never_copied_and_collection_is_not_published(self):
        self.prepare()
        source = self.paths['session_search_root'] / 'session.jsonl'
        payload = b'a' * 65530 + SECRET + b'after'
        source.write_bytes(payload)
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.collect()
        self.assertFalse((self.root / 'collected/collection.json').exists())
        for path in (self.root / 'collected').rglob('*'):
            if path.is_file():
                self.assertNotIn(SECRET, path.read_bytes())
        self.assertEqual(source.read_bytes(), payload)
        self.assertTrue(self.gates)
        self.assertTrue(all(gate.abandoned for gate in self.gates))
        self.assertTrue(all(gate.finish() == b'' for gate in self.gates))

    def test_filename_secret_is_rejected_before_receipt_retention(self):
        self.prepare()
        (self.paths['session_search_root'] / SECRET.decode()).write_bytes(b'safe')
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.collect()
        self.assertFalse((self.root / 'collected/collection.json').exists())

    def test_symlink_target_is_checked_before_base64_encoding(self):
        self.prepare()
        (self.paths['session_search_root'] / 'linked').symlink_to(SECRET.decode())
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.collect()
        self.assertFalse((self.root / 'collected/collection.json').exists())

    def test_escaped_prompt_secret_is_rejected_before_any_custody(self):
        secret = 'fabricated-\u00e9-\n-"-secret'.encode()
        self.prepare(prompt=b'fixture: ' + secret)
        self.assertNotIn(secret, (self.prepared / 'invocation.json').read_bytes())
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.collect(quarantine_factory=lambda: ExactSecretStreamQuarantine((secret,)))
        self.assertFalse((self.root / 'collected').exists())

    def test_safe_binary_collection_verifies_for_both_harnesses_and_source_modes(self):
        for harness in ('codex', 'claude'):
            self.prepare(harness)
            raw = b'\x00\xff\r\n' * 17000 + '\u00e9\u2028'.encode() + SECRET[:-1]
            (self.paths['session_search_root'] / 'child-\u00e9.jsonl').write_bytes(raw)
            target = b'../not-read-\xff'
            os.symlink(target, self.paths['session_search_root'] / 'linked')
            expected = {'session_search_root/child-\u00e9.jsonl': raw}
            for key, path in self.paths.items():
                if key != 'session_search_root':
                    (path / 'log' if path.is_dir() else path).write_bytes(b'raw log')
                    expected[key + ('/log' if path.is_dir() else '')] = b'raw log'
            total = sum(map(len, expected.values())) + len(target)
            descriptor = os.open(self.prepared / 'runtime', os.O_RDONLY | os.O_DIRECTORY)
            try:
                info = os.fstat(descriptor)
                for version in (1, 2):
                    with self.subTest(harness=harness, version=version):
                        source = None
                        if version == 2:
                            (self.prepared / 'runtime').rename(self.root / (harness + '-detached'))
                            source = NativeRuntimeDescriptor(descriptor, info.st_dev, info.st_ino)
                        name = f'{harness}-v{version}'
                        result = self.collect(name, runtime_descriptor=source, max_artifact_bytes=total)
                        output = self.root / name
                        self.assertEqual(result['schema'], f'caplab.native-output-collection/v{version}')
                        self.assertEqual(result['retained_artifact_bytes'], total)
                        self.assertEqual(result['missing_locations'], [])
                        self.assertEqual({entry['path']: (output / 'objects' / entry['object']).read_bytes()
                                          for entry in result['entries'] if entry['kind'] == 'file'}, expected)
                        link, = [entry for entry in result['entries'] if entry['kind'] == 'symlink']
                        self.assertEqual(base64.b64decode(link['target_base64']), target)
                        for filename in ('preparation.json', 'invocation.json'):
                            self.assertEqual((output / filename).read_bytes(),
                                             (self.prepared / filename).read_bytes())
                        verified = verify_native_collection(POLICY, output,
                            expected_collection_sha256=hashlib.sha256((output / 'collection.json').read_bytes()).hexdigest(),
                            max_receipt_bytes=200000)
                        self.assertFalse(verified['native_identity_verified'])
                        self.assertIsNone(verified['native_capture_complete'])
                        self.assertEqual(os.fstat(descriptor).st_ino, info.st_ino)
                        for path in output.rglob('*'):
                            self.assertEqual(path.stat().st_mode & 0o777, 0o700 if path.is_dir() else 0o600)
            finally:
                os.close(descriptor)
        self.assertTrue(all(gate.abandoned for gate in self.gates))

    def test_quota_counts_received_bytes_and_abandons_incomplete_overlap(self):
        self.prepare()
        self.paths['final_message'].write_bytes(b'first')
        (self.paths['session_search_root'] / 'raw').write_bytes(b'123456789')
        with self.assertRaisesRegex(TaskCaptureError, 'task-byte-limit'):
            self.collect(max_artifact_bytes=12)
        self.assertFalse((self.root / 'collected/collection.json').exists())
        payloads = [path.read_bytes() for path in (self.root / 'collected/objects').iterdir()]
        self.assertEqual(sorted(payloads), [b'', b'first'])
        self.assertTrue(all(gate.abandoned for gate in self.gates))
        self.assertTrue(all(gate.finish() == b'' for gate in self.gates))

    def test_invalid_factory_and_rejected_gate_fail_before_custody(self):
        self.prepare()
        invalid = RecordingGate()
        invalid.quarantined = True
        for index, factory in enumerate((42, lambda: object(), lambda: invalid)):
            with self.subTest(index=index), self.assertRaises(ValueError):
                self.collect(str(index), quarantine_factory=factory)
            self.assertFalse((self.root / str(index)).exists())
        self.assertTrue(invalid.abandoned)

    def test_invalid_file_gate_results_and_cleanup_cannot_publish(self):
        self.prepare()
        payload = b'file-fixture:' + b'a' * 80
        (self.paths['session_search_root'] / 'raw').write_bytes(payload)
        for mode in ('transform', 'drop', 'expand', 'nonbytes', 'flag', 'finish', 'cleanup', 'feed'):
            created = []

            class Gate(RecordingGate):
                artifact = False

                def feed(self, raw):
                    if raw.startswith(b'file-fixture:'):
                        self.artifact = True
                        if mode == 'transform':
                            return b'X' + raw[1:]
                        if mode == 'drop':
                            return b''
                        if mode == 'expand':
                            return raw + b'X'
                        if mode == 'nonbytes':
                            return None
                        if mode == 'flag':
                            self.quarantined = None
                            return raw
                        if mode == 'feed':
                            raise KeyboardInterrupt('synthetic cancellation')
                    return super().feed(raw)

                def finish(self):
                    if self.artifact and mode == 'finish':
                        self.quarantined = True
                    return super().finish()

                def abandon(self):
                    super().abandon()
                    if self.artifact and mode == 'cleanup':
                        raise RuntimeError('synthetic cleanup failure')

            def factory():
                gate = Gate()
                created.append(gate)
                return gate

            before = set(os.listdir('/proc/self/fd'))
            with self.subTest(mode=mode), self.assertRaises(KeyboardInterrupt if mode == 'feed' else RuntimeError):
                self.collect(mode, quarantine_factory=factory)
            self.assertEqual(before, set(os.listdir('/proc/self/fd')))
            self.assertFalse((self.root / mode / 'collection.json').exists())
            self.assertTrue(any(gate.artifact for gate in created))
            self.assertTrue(all(gate.abandoned for gate in created))
            self.assertLessEqual(sum(p.stat().st_size for p in (self.root / mode / 'objects').iterdir()), len(payload))

    def test_source_and_storage_failures_abandon_gates_and_close_descriptors(self):
        self.prepare()
        source = self.paths['session_search_root'] / 'raw'
        source.write_bytes(b'synthetic original')
        read = os.read
        changed = False

        def changing_read(fd, size):
            nonlocal changed
            raw = read(fd, size)
            if raw == b'synthetic original':
                changed = True
                source.write_bytes(b'synthetic modified')
            return raw

        before = set(os.listdir('/proc/self/fd'))
        with patch('caplab.task_capture.os.read', side_effect=changing_read):
            with self.assertRaisesRegex(TaskCaptureError, 'source-changed'):
                self.collect('changed')
        self.assertTrue(changed)
        self.assertFalse((self.root / 'changed/collection.json').exists())
        self.assertTrue(all(gate.abandoned for gate in self.gates))

        original_open = Path.open

        def failed_open(path, *args, **kwargs):
            if path.parent.name == 'objects':
                raise OSError('synthetic storage failure')
            return original_open(path, *args, **kwargs)

        with patch.object(Path, 'open', failed_open):
            with self.assertRaisesRegex(OSError, 'synthetic storage failure'):
                self.collect('storage')
        self.assertFalse((self.root / 'storage/collection.json').exists())
        self.assertTrue(all(gate.abandoned for gate in self.gates))
        self.assertEqual(before, set(os.listdir('/proc/self/fd')))

    def test_generated_custody_names_are_checked_before_creation(self):
        self.prepare()
        (self.paths['session_search_root'] / 'raw').write_bytes(b'safe file')
        for index, secret in enumerate((b'object-', b'.intent.pending', b'collection.json')):
            name = f'generated-{index}'
            with self.subTest(secret=secret), self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                self.collect(name, quarantine_factory=lambda: ExactSecretStreamQuarantine((secret,)))
            output = self.root / name
            self.assertFalse((output / 'collection.json').exists())
            for path in output.rglob('*'):
                self.assertNotIn(secret, os.fsencode(path))

    def test_receipt_keys_raw_serialization_and_final_metadata_are_checked(self):
        self.prepare()
        path = self.prepared / 'preparation.json'
        original = path.read_bytes()
        secret = 'fabricated-\u00e9-key'.encode()
        document = json.loads(original)
        document[secret.decode()] = 'synthetic extra field'
        path.write_text(json.dumps(document))
        self.anchor = hashlib.sha256(path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.collect('key', quarantine_factory=lambda: ExactSecretStreamQuarantine((secret,)))
        self.assertFalse((self.root / 'key').exists())
        path.write_bytes(original)
        self.anchor = hashlib.sha256(original).hexdigest()
        for name, value in (('raw', b'"schema": "caplab.native-runtime-preparation/v1"'),
                            ('final', b'raw planned-path custody only')):
            with self.subTest(name=name), self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                self.collect(name, quarantine_factory=lambda: ExactSecretStreamQuarantine((value,)))
            self.assertFalse((self.root / name / 'collection.json').exists())
            for retained in (self.root / name).rglob('*'):
                if retained.is_file():
                    self.assertNotIn(value, retained.read_bytes())

    def test_guard_is_opt_in_and_raw_source_paths_are_checked(self):
        self.prepare()
        raw_name = b'fabricated-name-\xff'
        source = self.paths['session_search_root'] / os.fsdecode(raw_name)
        source.write_bytes(SECRET)
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.collect('bad-name', quarantine_factory=lambda: ExactSecretStreamQuarantine((raw_name,)))
        self.assertFalse((self.root / 'bad-name/collection.json').exists())
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.collect(SECRET.decode())
        self.assertFalse((self.root / SECRET.decode()).exists())
        result = self.collect('unguarded', quarantine_factory=None)
        entry, = [entry for entry in result['entries'] if entry['kind'] == 'file']
        self.assertEqual((self.root / 'unguarded/objects' / entry['object']).read_bytes(), SECRET)


if __name__ == '__main__':
    unittest.main()
