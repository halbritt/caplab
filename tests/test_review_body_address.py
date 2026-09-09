"""Read source-shaped body references through a real private SOB1 object store."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import review_criterion_ledger_pass as criterion
import review_canary


class ReviewBodyAddressTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.store = self.root / 'store'
        self.raw = json.dumps({'verdict': 'reject', 'summary': 'Café review', 'findings': []},
                              ensure_ascii=False).encode('utf-8')
        self.hash = hashlib.sha256(self.raw).hexdigest()
        self.object = self.store / 'objects' / 'sha256' / self.hash[:2] / self.hash[2:4] / (self.hash + '.zst')
        self.object.parent.mkdir(parents=True)
        compressed = subprocess.run(['zstd', '-q', '-c'], input=self.raw, capture_output=True, check=True).stdout
        self.object.write_bytes(b'SOB1zstd' + struct.pack('>Q', len(self.raw)) + compressed)
        self.body = {'store': 'object', 'address': 'sha256/' + self.hash,
                     'compression': 'zstd', 'size': len(self.raw)}
        subject = {'identity': 'work/change-set', 'version_seq': 0, 'content_hash': 'subject'}
        self.events = [
            {'type': 'graph_genesis', 'payload': {}},
            {'type': 'pass_run_opened', 'payload': {'pass_id': 'review', 'manifest': {
                'subject_pin': subject, 'input_pins': [{'role': 'materialized_base', 'content_hash': 'base'}]}}},
            {'type': 'artifact_admitted', 'schema_version': 1, 'payload': {'identity': 'work/review',
                'kind': 'review-ledger', 'content_hash': self.hash, 'produced_by_run': 1, 'body': self.body}},
            {'type': 'pass_run_closed', 'payload': {'run_ref': 1, 'outcome': 'submitted'}},
        ]
        for seq, event in enumerate(self.events):
            event.update(seq=seq, written_at='2026-09-09T00:00:00Z')

    def ledger(self):
        path = self.root / 'ledger.jsonl'
        path.write_text(''.join(json.dumps(e) + '\n' for e in self.events))
        return path

    def read(self):
        snapshot, _, runs, _ = criterion.read_reviews(str(self.ledger()), object_store=str(self.store))
        return runs[1], review_canary.summarize(snapshot, runs, 0)

    def test_address_only_admission_reads_the_verified_stored_body(self):
        before = self.object.read_bytes()
        row, report = self.read()
        self.assertIs(row['cleared'], False)
        self.assertEqual(row['summary'], 'Café review')
        self.assertEqual(row['review_body_hash'], self.hash)
        self.assertEqual(report['reviews'][0]['verdict_source'], 'body')
        self.assertEqual(self.object.read_bytes(), before)

    def test_invalid_or_conflicting_references_do_not_read_any_object(self):
        malformed = [
            self.body | {'address': address}
            for address in ('../../outside', 'sha256/../outside', 'sha256/' + 'A' * 64,
                            'sha256/' + 'a' * 63, 'sha256/' + self.hash + '/tail', '', None, [])
        ]
        malformed += [self.body | {'content_hash': value} for value in ('f' * 64, 'short', None, [], True)]
        malformed += [self.body | {'store': 'file'}, self.body | {'compression': 'gzip'}]
        malformed += [self.body | {'size': value} for value in (True, -1, 1.0, '1', None)]
        for body in malformed:
            with self.subTest(body=body):
                self.events[2]['payload']['body'] = body
                with patch.object(criterion.M, 'store_object') as reader:
                    row, _ = self.read()
                reader.assert_not_called()
                self.assertIsNone(row['cleared'])
                self.assertIn(row['review_body_observations'][0]['status'], ('invalid-reference', 'conflicting-reference'))

    def test_missing_corrupt_and_size_mismatched_objects_do_not_supply_verdicts(self):
        original = self.object.read_bytes()
        self.events[2]['payload']['body'] = self.body | {'size': len(self.raw) + 1}
        row, _ = self.read()
        self.assertIsNone(row['cleared'])
        self.assertEqual(row['review_body_observations'][0]['status'], 'body-size-mismatch')
        self.events[2]['payload']['body'] = self.body
        wrong = subprocess.run(['zstd', '-q', '-c'], input=b'{"verdict":"accept"}', capture_output=True, check=True).stdout
        for contents in (b'corrupt', original[:16] + wrong):
            self.object.write_bytes(contents)
            row, _ = self.read()
            self.assertIsNone(row['cleared'])
            self.assertEqual(row['review_body_observations'][0]['status'], 'unavailable-or-unverified')
        self.object.unlink()
        row, _ = self.read()
        self.assertIsNone(row['cleared'])
        self.assertEqual(row['review_body_observations'][0]['status'], 'unavailable-or-unverified')

    def test_both_clis_read_the_selected_store_and_preserve_existing_reports(self):
        source = self.ledger()
        original_ledger = source.read_bytes()
        original_object = self.object.read_bytes()
        for script, filename in (('review_canary.py', 'report.json'),
                                 ('review_criterion_ledger_pass.py', 'review-criterion-summary.json')):
            with self.subTest(script=script):
                out = self.root / script
                command = [sys.executable, str(Path(criterion.ROOT) / 'scripts' / script),
                    '--ledger', str(source), '--object-store', str(self.store), '--out', str(out)]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads((out / filename).read_text())
                self.assertEqual(report['snapshot']['object_store'], str(self.store))
                self.assertEqual(report['body_reference_resolution'], 'sha256-address-or-hash-agreement/1')
                if script == 'review_canary.py':
                    self.assertEqual(report['reviews'][0]['decision'], 'refused')
                    self.assertEqual(report['reviews'][0]['review_body_observations'][0]['body_reference'], self.body)
                else:
                    self.assertEqual(report['verdict_sources']['review_ledger_body'], 1)
                files = {p.name: p.read_bytes() for p in out.iterdir()}
                repeated = subprocess.run(command, capture_output=True, text=True)
                self.assertNotEqual(repeated.returncode, 0)
                self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()}, files)
        self.assertEqual(source.read_bytes(), original_ledger)
        self.assertEqual(self.object.read_bytes(), original_object)

    def test_hash_only_and_matching_dual_locators_read_the_same_verified_bytes(self):
        for body in ({'content_hash': self.hash}, self.body | {'content_hash': self.hash}):
            with self.subTest(body=body):
                self.events[2]['payload']['body'] = body
                row, _ = self.read()
                self.assertIs(row['cleared'], False)
                self.assertEqual(row['summary'], 'Café review')
                self.assertEqual(row['review_body_observations'][0]['body_reference'], body)
        empty = self.root / 'empty-store'
        snapshot, _, runs, _ = criterion.read_reviews(str(self.ledger()), object_store=str(empty))
        self.assertIsNone(runs[1]['cleared'])
        self.assertEqual(snapshot['object_store'], str(empty))
        self.assertFalse(empty.exists())
