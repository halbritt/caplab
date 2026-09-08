from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from caplab.native_capture_invocation import NativeCaptureContext, _digest, build_native_capture_invocation
from caplab.native_collection import collect_native_outputs
from caplab.native_collection_verify import verify_native_collection
from caplab.native_runtime import prepare_native_runtime
from caplab.task_capture_verify import CaptureVerificationError

REPO = Path(__file__).resolve().parents[1]
POLICY = REPO / 'docs/product/contracts/native-agent-systems.json'


class NativeCollectionVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def build(self, harness='codex', *, empty=False, payload=b'\xff\x00raw\r\n', suffix=''):
        task = self.root / ('task' + suffix); task.mkdir()
        prepared = self.root / ('prepared' + suffix)
        plan = build_native_capture_invocation(POLICY,
            'codex-terra-max' if harness == 'codex' else 'claude-fable-5-max',
            context=NativeCaptureContext('/work', '/episode', 'private synthetic prompt\u2028'.encode(),
                None if harness == 'codex' else '11111111-2222-4333-8444-555555555555'))
        prep = prepare_native_runtime(POLICY, plan, expected_invocation_sha256=plan['invocation_sha256'],
                                      task_root=task, output_dir=prepared)
        paths = {k: Path(v) for k, v in prep['capture_paths'].items()}
        if empty:
            for path in paths.values():
                if path.is_dir():
                    path.rmdir()
        else:
            nested = paths['session_search_root'] / 'children'; nested.mkdir()
            (nested / 'child-\u00e9.jsonl').write_bytes(payload)
            (nested / 'link').symlink_to('/nonexistent-synthetic-link')
            for name, path in paths.items():
                if name != 'session_search_root':
                    target = path / 'log' if name.endswith('_search_root') else path
                    target.write_bytes(b'diagnostic\n')
        self.custody = self.root / ('custody' + suffix)
        self.receipt = collect_native_outputs(POLICY, prepared,
            expected_preparation_sha256=self.hash_file(prepared / 'preparation.json'),
            output_dir=self.custody, max_receipt_bytes=100000, max_artifact_bytes=1000000, max_entries=100)
        self.anchor = self.hash_file(self.custody / 'collection.json')
        self.originals = {name: (self.custody / name).read_bytes()
                          for name in ('collection.json', 'intent.json', 'preparation.json', 'invocation.json')}
        return prepared, task

    @staticmethod
    def hash_file(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def verify(self, **kwargs):
        options = dict(expected_collection_sha256=self.anchor, max_receipt_bytes=100000)
        options.update(kwargs)
        return verify_native_collection(POLICY, self.custody, **options)

    def restore(self):
        for name, raw in self.originals.items():
            (self.custody / name).write_bytes(raw)
        self.anchor = self.hash_file(self.custody / 'collection.json')

    def rewrite(self, name, mutate):
        docs = {n: json.loads((self.custody / n).read_bytes()) for n in self.originals}
        mutate(docs[name])
        def write(n):
            (self.custody / n).write_text(json.dumps(docs[n], sort_keys=True) + '\n')
            return self.hash_file(self.custody / n)
        docs['preparation.json']['invocation_file_sha256'] = write('invocation.json')
        docs['intent.json']['invocation_file_sha256'] = docs['preparation.json']['invocation_file_sha256']
        docs['intent.json']['preparation_sha256'] = write('preparation.json')
        docs['collection.json']['intent_sha256'] = write('intent.json')
        self.anchor = write('collection.json')

    def test_both_layouts_verify_after_sources_removed_and_custody_moved(self):
        for harness in ('codex', 'claude'):
            with self.subTest(harness=harness):
                prepared, task = self.build(harness, suffix=harness)
                shutil.rmtree(prepared); shutil.rmtree(task)
                moved = self.root / ('moved-' + harness)
                self.custody.rename(moved); self.custody = moved
                before = {str(p.relative_to(moved)): p.read_bytes() for p in moved.rglob('*') if p.is_file()}
                report = self.verify()
                self.assertTrue(report['integrity_verified'])
                self.assertIs(report['native_identity_verified'], False)
                self.assertIsNone(report['native_capture_complete'])
                self.assertEqual(report['retained_entries'], self.receipt['retained_entries'])
                self.assertEqual(report['retained_artifact_bytes'], self.receipt['retained_artifact_bytes'])
                self.assertEqual(report['missing_locations'], [])
                self.assertNotIn('private synthetic prompt', json.dumps(report))
                self.assertEqual(before, {str(p.relative_to(moved)): p.read_bytes() for p in moved.rglob('*') if p.is_file()})

    def test_all_missing_collection_is_integral_without_native_completeness(self):
        self.build(empty=True)
        report = self.verify()
        self.assertEqual(report['retained_entries'], 0)
        self.assertEqual(report['retained_artifact_bytes'], 0)
        self.assertEqual(report['missing_locations'], ['diagnostic_search_root', 'final_message', 'session_search_root'])
        self.assertIsNone(report['native_capture_complete'])

    def test_every_receipt_link_and_independent_anchor_are_checked(self):
        self.build()
        for name in self.originals:
            with self.subTest(name=name):
                (self.custody / name).write_bytes(self.originals[name] + b' ')
                with self.assertRaisesRegex(CaptureVerificationError, 'hash mismatch'):
                    self.verify()
                self.restore()
        with self.assertRaises(CaptureVerificationError):
            self.verify(expected_collection_sha256='0' * 64)

    def test_resealed_collection_contradictions_are_rejected(self):
        self.build()
        def file_entry(doc):
            return next(e for e in doc['entries'] if e['kind'] == 'file')
        def link_entry(doc):
            return next(e for e in doc['entries'] if e['kind'] == 'symlink')
        changes = {
            'count': lambda d: d.update(retained_entries=True),
            'bytes': lambda d: d.update(retained_artifact_bytes=d['retained_artifact_bytes'] + 1),
            'missing': lambda d: d.update(missing_locations=['session_search_root']),
            'identity': lambda d: d.update(native_identity_verified=True),
            'complete': lambda d: d.update(native_capture_complete=True),
            'omitted_complete': lambda d: d.pop('native_capture_complete'),
            'duplicate_location': lambda d: d['locations'].__setitem__(1, copy.deepcopy(d['locations'][0])),
            'status': lambda d: d['locations'][0].update(status='unknown'),
            'source': lambda d: d['locations'][0].update(source='/other'),
            'traversal': lambda d: file_entry(d).update(path='session_search_root/../escape'),
            'locator': lambda d: file_entry(d).update(object='../invocation.json'),
            'duplicate_entry': lambda d: d['entries'].append(copy.deepcopy(d['entries'][-1])),
            'unselected': lambda d: file_entry(d).update(path='home/secret'),
            'wrong_root': lambda d: next(e for e in d['entries'] if e['path']=='session_search_root').update(kind='symlink'),
            'bad_link': lambda d: link_entry(d).update(target_base64='!!!'),
            'bad_mode': lambda d: file_entry(d).update(mode=0o10000),
        }
        for label, change in changes.items():
            with self.subTest(label=label):
                self.rewrite('collection.json', change)
                with self.assertRaises(CaptureVerificationError):
                    self.verify()
                self.restore()

    def test_resealed_intent_limits_and_selection_are_checked(self):
        self.build()
        changes = (
            lambda d: d.update(max_entries=1), lambda d: d.update(max_artifact_bytes=1),
            lambda d: d.update(max_artifact_bytes=True), lambda d: d.update(max_receipt_bytes=1),
            lambda d: d['capture_paths'].update(session_search_root='/other'),
            lambda d: d.update(invocation_sha256='0' * 64),
            lambda d: d.update(source_root='/a/../b'),
        )
        for change in changes:
            self.rewrite('intent.json', change)
            with self.assertRaises(CaptureVerificationError):
                self.verify()
            self.restore()

    def test_unsupported_rehashed_invocation_does_not_become_canonical(self):
        self.build()
        def change(doc):
            doc['command'].insert(-2, '--unsupported-override')
            doc['invocation_sha256'] = _digest({k:v for k,v in doc.items() if k!='invocation_sha256'})
        self.rewrite('invocation.json', change)
        digest = json.loads((self.custody/'invocation.json').read_bytes())['invocation_sha256']
        self.rewrite('preparation.json', lambda d: d.update(invocation_sha256=digest))
        self.rewrite('intent.json', lambda d: d.update(invocation_sha256=digest))
        with self.assertRaisesRegex(CaptureVerificationError, 'invalid collection invocation'):
            self.verify()

    def test_payload_tampering_links_and_fifo_are_rejected(self):
        self.build()
        entry = next(e for e in self.receipt['entries'] if e['kind']=='file')
        path = self.custody/'objects'/entry['object']; original = path.read_bytes()
        for raw in (b'', b'x' * len(original), original + b'x'):
            path.write_bytes(raw)
            with self.assertRaises(CaptureVerificationError):
                self.verify()
        path.unlink(); path.symlink_to(self.custody/'invocation.json')
        with self.assertRaises(OSError):
            self.verify()
        path.unlink(); os.mkfifo(path)
        with self.assertRaises(CaptureVerificationError):
            self.verify()

    def test_changed_payload_fails_stable_read_and_closes_descriptors(self):
        self.build(payload=b'unique-changing-payload')
        entry = next(e for e in self.receipt['entries'] if e['path'].endswith('.jsonl'))
        path = self.custody/'objects'/entry['object']
        real_read = os.read
        touched = []
        def read(fd, count):
            raw = real_read(fd, count)
            if raw == b'unique-changing-payload':
                touched.append(fd); path.write_bytes(b'replacement-changed')
            return raw
        with patch('caplab.task_capture_verify.os.read', side_effect=read):
            with self.assertRaisesRegex(CaptureVerificationError, 'changed during read'):
                self.verify()
        self.assertEqual(len(touched), 1)
        with self.assertRaises(OSError):
            os.fstat(touched[0])

    def test_receipt_budget_and_chunk_boundaries(self):
        self.build(payload=b'x' * 70000)
        total = sum(len(raw) for raw in self.originals.values())
        sizes=[]; real_read=os.read
        def read(fd, count):
            sizes.append(count); return real_read(fd,count)
        with patch('caplab.task_capture_verify.os.read', side_effect=read):
            report=self.verify(max_receipt_bytes=total)
        self.assertEqual(report['verified_receipt_bytes'], total)
        self.assertLessEqual(max(sizes),65536)
        with self.assertRaises(CaptureVerificationError):
            self.verify(max_receipt_bytes=total-1)
        for invalid in (True,0,-1):
            with self.assertRaises(CaptureVerificationError):
                self.verify(max_receipt_bytes=invalid)

    def test_malformed_receipt_json_and_linked_custody_are_rejected(self):
        self.build()
        for raw in (b'{"schema":1,"schema":2}', b'{"schema":NaN}', b'\xff', b'[]'):
            (self.custody/'collection.json').write_bytes(raw)
            self.anchor=self.hash_file(self.custody/'collection.json')
            with self.assertRaises(CaptureVerificationError):
                self.verify()
        self.restore()
        original=self.custody; linked=self.root/'linked'; linked.symlink_to(original,target_is_directory=True)
        self.custody=linked
        with self.assertRaises(OSError):
            self.verify()

    def test_cli_reports_missingness_and_rejects_bad_anchor_without_stdout(self):
        self.build(empty=True)
        os.mkfifo(self.custody/'unreferenced')
        command=[sys.executable,str(REPO/'scripts/verify_native_collection.py'),str(self.custody),
                 '--policy',str(POLICY),'--expected-collection-sha256',self.anchor,'--max-receipt-bytes','100000']
        env=os.environ|{'PYTHONPATH':str(REPO/'src')}
        good=subprocess.run(command,env=env,capture_output=True,timeout=5)
        self.assertEqual(good.returncode,0,good.stderr)
        self.assertTrue(json.loads(good.stdout)['integrity_verified'])
        command[command.index(self.anchor)]='0'*64
        bad=subprocess.run(command,env=env,capture_output=True,timeout=5)
        self.assertEqual(bad.returncode,2)
        self.assertEqual(bad.stdout,b'')
        self.assertIn(b'hash mismatch',bad.stderr)


if __name__ == '__main__':
    unittest.main()
