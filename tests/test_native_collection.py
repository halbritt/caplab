from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import NativeCollectionError, collect_native_outputs
from caplab.native_runtime import prepare_native_runtime
from caplab.task_capture import TaskCaptureError, TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import CaptureVerificationError, verify_task_capture


POLICY = Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'


class NativeCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = self.root / 'task'
        self.task.mkdir()

    def prepare(self, harness='codex'):
        self.prepared = self.root / harness
        plan = build_native_capture_invocation(POLICY,
            'codex-terra-max' if harness == 'codex' else 'claude-fable-5-max',
            context=NativeCaptureContext('/work', '/episode', 'synthetic\u2028prompt\n'.encode(),
                None if harness == 'codex' else '11111111-2222-4333-8444-555555555555'))
        receipt = prepare_native_runtime(POLICY, plan, expected_invocation_sha256=plan['invocation_sha256'],
                                         task_root=self.task, output_dir=self.prepared)
        self.anchor = hashlib.sha256((self.prepared / 'preparation.json').read_bytes()).hexdigest()
        self.paths = {key: Path(value) for key, value in receipt['capture_paths'].items()}
        return receipt

    def collect(self, name='collected', **kwargs):
        options = dict(expected_preparation_sha256=self.anchor, output_dir=self.root / name,
                       max_receipt_bytes=100000, max_artifact_bytes=10000, max_entries=100)
        options.update(kwargs)
        return collect_native_outputs(POLICY, self.prepared, **options)

    def payloads(self, receipt, name='collected'):
        values = {}
        for entry in receipt['entries']:
            if entry['kind'] == 'file':
                path = self.root / name / 'objects' / entry['object']
                raw = path.read_bytes()
                self.assertEqual(entry['sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(entry['bytes'], len(raw))
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                values[entry['path']] = raw
        return values

    def test_both_harnesses_retain_nested_raw_files_and_exclude_home(self):
        for harness in ('codex', 'claude'):
            with self.subTest(harness=harness):
                self.prepare(harness)
                sessions = self.paths['session_search_root']
                child = sessions / 'project' / 'children'
                child.mkdir(parents=True)
                root_raw = b'not valid JSON\r\n\xff\x00'
                (sessions / 'root.jsonl').write_bytes(root_raw)
                (child / 'child-\u00e9.jsonl').write_bytes('child\u2028data\n'.encode())
                expected = {'session_search_root/root.jsonl': root_raw,
                            'session_search_root/project/children/child-\u00e9.jsonl': 'child\u2028data\n'.encode()}
                for key, path in self.paths.items():
                    if key == 'session_search_root':
                        continue
                    target = path / 'trace.log' if key.endswith('_search_root') else path
                    target.write_bytes(b'raw diagnostic\n')
                    expected[key + ('/trace.log' if key.endswith('_search_root') else '')] = b'raw diagnostic\n'
                (self.prepared / 'runtime/home/secret').write_bytes(b'synthetic excluded home')
                (self.prepared / 'runtime/unselected').write_bytes(b'synthetic excluded file')
                receipt = self.collect(harness + '-collected')
                self.assertEqual(self.payloads(receipt, harness + '-collected'), expected)
                self.assertEqual(receipt['missing_locations'], [])
                self.assertIsNone(receipt['native_capture_complete'])
                self.assertIs(receipt['native_identity_verified'], False)
                self.assertEqual(receipt['retained_artifact_bytes'], sum(map(len, expected.values())))
                for filename in ('preparation.json', 'invocation.json'):
                    copy = self.root / (harness + '-collected') / filename
                    self.assertEqual(copy.read_bytes(), (self.prepared / filename).read_bytes())
                    self.assertEqual(copy.stat().st_mode & 0o777, 0o600)

    def test_missing_locations_are_explicit_and_empty_tree_is_not_native_completeness(self):
        self.prepare()
        receipt = self.collect()
        self.assertEqual(receipt['missing_locations'], ['final_message'])
        self.assertEqual(receipt['retained_entries'], 2)
        self.assertEqual(receipt['retained_artifact_bytes'], 0)
        self.assertIsNone(receipt['native_capture_complete'])
        self.paths['session_search_root'].rmdir()
        receipt = self.collect('second')
        self.assertEqual(receipt['missing_locations'], ['final_message', 'session_search_root'])

    def test_shared_byte_limit_retains_only_allowed_prefix_and_no_final_receipt(self):
        self.prepare()
        self.paths['final_message'].write_bytes(b'1234')
        (self.paths['session_search_root'] / 'root.jsonl').write_bytes(b'56789')
        with self.assertRaisesRegex(TaskCaptureError, 'task-byte-limit'):
            self.collect(max_artifact_bytes=7)
        self.assertFalse((self.root / 'collected/collection.json').exists())
        self.assertEqual(sum(p.stat().st_size for p in (self.root / 'collected/objects').iterdir()), 7)
        with self.assertRaises(FileExistsError):
            self.collect()

    def test_exact_combined_receipt_and_artifact_limits(self):
        self.prepare()
        self.paths['final_message'].write_bytes(b'1234')
        (self.paths['session_search_root'] / 'root.jsonl').write_bytes(b'56789')
        total = sum((self.prepared / name).stat().st_size for name in ('preparation.json', 'invocation.json'))
        receipt = self.collect(max_receipt_bytes=total, max_artifact_bytes=9, max_entries=4)
        self.assertEqual(receipt['retained_artifact_bytes'], 9)
        self.assertEqual(receipt['retained_entries'], 4)
        with self.assertRaises(CaptureVerificationError):
            self.collect('too-small', max_receipt_bytes=total - 1)
        self.assertFalse((self.root / 'too-small').exists())

    def test_shared_entry_limit_applies_across_selected_roots(self):
        self.prepare()
        with self.assertRaisesRegex(TaskCaptureError, 'task-entry-limit'):
            self.collect(max_entries=1)
        self.assertFalse((self.root / 'collected/collection.json').exists())

    def test_nested_symlink_is_literal_but_selected_symlink_and_parent_are_rejected(self):
        self.prepare()
        outside = self.root / 'outside'
        outside.write_bytes(b'synthetic must not read')
        (self.paths['session_search_root'] / 'linked').symlink_to(outside)
        receipt = self.collect()
        link = next(e for e in receipt['entries'] if e['kind'] == 'symlink')
        self.assertIn('target_base64', link)
        self.assertEqual(self.payloads(receipt), {})
        self.paths['final_message'].symlink_to(outside)
        with self.assertRaisesRegex(NativeCollectionError, 'unexpected-selected-object'):
            self.collect('linked-leaf')
        self.paths['final_message'].unlink()
        codex = self.prepared / 'runtime/codex'
        codex.rename(self.prepared / 'saved-codex')
        codex.symlink_to(self.prepared / 'saved-codex', target_is_directory=True)
        with self.assertRaises(OSError):
            self.collect('linked-parent')
        self.assertFalse((self.root / 'linked-parent/collection.json').exists())

    def test_fifo_is_rejected_without_opening_it(self):
        self.prepare()
        os.mkfifo(self.paths['session_search_root'] / 'fifo')
        with self.assertRaisesRegex(TaskCaptureError, 'unsupported-task-object'):
            self.collect()
        self.assertFalse((self.root / 'collected/collection.json').exists())

    def test_changed_file_is_not_published(self):
        self.prepare()
        source = self.paths['session_search_root'] / 'root.jsonl'
        source.write_bytes(b'original')
        real_read = os.read
        changed = False
        def read(fd, count):
            nonlocal changed
            raw = real_read(fd, count)
            if raw == b'original' and not changed:
                changed = True
                source.write_bytes(b'modified')
            return raw
        with patch('caplab.task_capture.os.read', side_effect=read):
            with self.assertRaisesRegex(TaskCaptureError, 'source-changed'):
                self.collect()
        self.assertTrue(changed)
        self.assertFalse((self.root / 'collected/collection.json').exists())

    def test_validation_precedes_output_creation(self):
        self.prepare()
        for index, options in enumerate(({'expected_preparation_sha256': '0' * 64},
                {'max_receipt_bytes': 1}, {'max_artifact_bytes': True}, {'max_entries': 0})):
            with self.subTest(options=options):
                name = 'invalid-' + str(index)
                with self.assertRaises((NativeCollectionError, CaptureVerificationError)):
                    self.collect(name, **options)
                self.assertFalse((self.root / name).exists())
        for destination in (self.prepared / 'output', self.task / 'output'):
            with self.assertRaises(NativeCollectionError):
                self.collect(output_dir=destination)
            self.assertFalse(destination.exists())
        p = self.prepared / 'preparation.json'
        data = json.loads(p.read_bytes())
        data['capture_paths']['session_search_root'] = str(self.root)
        p.write_text(json.dumps(data))
        self.anchor = hashlib.sha256(p.read_bytes()).hexdigest()
        with self.assertRaisesRegex(NativeCollectionError, 'layout-differs'):
            self.collect()
        self.assertFalse((self.root / 'collected').exists())

    def test_publication_error_keeps_payload_without_final_receipt(self):
        self.prepare()
        self.paths['final_message'].write_bytes(b'retained')
        from caplab.native_collection import seal_capture_json
        def publish(directory, name, receipt):
            if name == 'collection.json':
                raise OSError('synthetic publication failure')
            return seal_capture_json(directory, name, receipt)
        with patch('caplab.native_collection.seal_capture_json', side_effect=publish):
            with self.assertRaisesRegex(OSError, 'synthetic publication'):
                self.collect()
        self.assertFalse((self.root / 'collected/collection.json').exists())
        self.assertIn(b'retained', [p.read_bytes() for p in (self.root / 'collected/objects').iterdir()])

    def test_real_producer_task_capture_then_collection_survives_source_deletion(self):
        self.prepare()
        code = ('from pathlib import Path; import sys; r=Path(sys.argv[1]); '
                '(r/"codex/sessions/root.jsonl").write_bytes(b"synthetic mechanics only\\n"); '
                '(r/"codex/log/diagnostic").write_bytes(b"log\\n"); '
                '(r/"final-message.txt").write_bytes(b"done\\n"); '
                'Path("result").write_bytes(b"task result\\n")')
        capture = self.root / 'attempt'
        result = capture_task_attempt([sys.executable, '-c', code, str(self.prepared / 'runtime')],
            task_root=self.task, environment={'PATH': '/usr/bin:/bin'}, output_dir=capture,
            limits=TaskCaptureLimits(1000, 1000, 100, 5))
        self.assertEqual(result['process']['return_code'], 0)
        anchor = hashlib.sha256((capture / 'attempt.json').read_bytes()).hexdigest()
        self.assertTrue(verify_task_capture(capture, expected_attempt_sha256=anchor,
                                           max_receipt_bytes=100000)['integrity_verified'])
        receipt = self.collect()
        original = self.payloads(receipt)
        (self.paths['session_search_root'] / 'root.jsonl').unlink()
        self.paths['final_message'].write_bytes(b'changed after collection')
        self.assertEqual(self.payloads(receipt), original)
        self.assertEqual(original['session_search_root/root.jsonl'], b'synthetic mechanics only\n')


if __name__ == '__main__':
    unittest.main()
