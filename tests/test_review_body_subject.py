"""Verified bytes still need a matching admitted review subject."""
import copy
import hashlib
import json
import struct
import subprocess
import unittest

import test_review_body_address as stored_body


class ReviewBodySubjectTests(unittest.TestCase):
    def setUp(self):
        self.fixture = stored_body.ReviewBodyAddressTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.subject = copy.deepcopy(self.fixture.events[1]['payload']['manifest']['subject_pin'])
        self.fixture.events[2]['payload']['edges'] = {
            'evidences': [{'subject': copy.deepcopy(self.subject), 'claim': 'verdict:reject'}]}

    def test_body_cannot_supply_a_verdict_for_another_admitted_subject(self):
        for key, value in (('identity', 'other/change-set'), ('version_seq', 1), ('content_hash', 'other-bytes')):
            with self.subTest(key=key):
                self.fixture.events[2]['payload']['edges']['evidences'][0]['subject'] = self.subject | {key: value}
                row, report = self.fixture.read()
                self.assertIsNone(row['cleared'])
                observation, = row['review_body_observations']
                self.assertEqual(observation['verdict'], 'reject')
                self.assertEqual(observation['attribution'], 'admitted-subject-mismatch-or-incomplete')
                self.assertEqual(report['reviews'][0]['decision'], 'unknown')

    def write_body(self, doc):
        raw = json.dumps(doc, ensure_ascii=False).encode()
        digest = hashlib.sha256(raw).hexdigest()
        path = self.fixture.store / 'objects' / 'sha256' / digest[:2] / digest[2:4] / (digest + '.zst')
        path.parent.mkdir(parents=True, exist_ok=True)
        compressed = subprocess.run(['zstd', '-q', '-c'], input=raw, capture_output=True, check=True).stdout
        path.write_bytes(b'SOB1zstd' + struct.pack('>Q', len(raw)) + compressed)
        self.fixture.events[2]['payload'].update(content_hash=digest,
            body={'store': 'object', 'address': 'sha256/' + digest, 'size': len(raw), 'compression': 'zstd'})
        return path

    def test_supplied_body_subject_pins_must_be_exactly_one_matching_pin(self):
        values = [None, {}, [], [self.subject, self.subject], [None],
                  [self.subject | {'identity': 'other'}], [self.subject | {'content_hash': 'other'}]]
        values += [[self.subject | {'version_seq': v}] for v in (True, False, 0.0, '0', -1, 1)]
        for pins in values:
            with self.subTest(pins=pins):
                self.write_body(json.loads(self.fixture.raw) | {'subject_pins': pins})
                row, _ = self.fixture.read()
                self.assertIsNone(row['cleared'])
                self.assertEqual(row['review_body_observations'][0]['attribution'], 'body-subject-mismatch-or-incomplete')

    def test_admitted_identity_and_hash_must_identify_the_verified_body(self):
        payload = self.fixture.events[2]['payload']
        original = copy.deepcopy(payload)
        for changes in ({'content_hash': None}, {'content_hash': 'f' * 64}, {'identity': None}, {'identity': ''}):
            with self.subTest(changes=changes):
                self.fixture.events[2]['payload'] = original | changes
                row, _ = self.fixture.read()
                self.assertIsNone(row['cleared'])
                self.assertEqual(row['review_body_observations'][0]['attribution'], 'admission-body-mismatch-or-incomplete')

    def test_an_admission_cannot_precede_its_claimed_producing_run(self):
        events = self.fixture.events
        events[1], events[2] = events[2], events[1]
        events[1]['seq'], events[2]['seq'] = 1, 2
        events[1]['payload']['produced_by_run'] = 2
        events[3]['payload']['run_ref'] = 2
        _, _, runs, _ = stored_body.criterion.read_reviews(str(self.fixture.ledger()), object_store=str(self.fixture.store))
        self.assertIsNone(runs[2]['cleared'])
        self.assertEqual(runs[2]['review_body_observations'][0]['attribution'], 'admission-before-producing-run')

    def test_exact_legacy_and_explicit_subjects_link_but_latest_unlinked_body_does_not_inherit(self):
        row, _ = self.fixture.read()
        self.assertIs(row['cleared'], False)
        self.assertEqual(row['review_body_observations'][0]['attribution'], 'linked')
        self.write_body(json.loads(self.fixture.raw) | {'subject_pins': [self.subject]})
        row, _ = self.fixture.read()
        self.assertIs(row['cleared'], False)
        latest = copy.deepcopy(self.fixture.events[2])
        latest['seq'] = len(self.fixture.events)
        latest['payload']['edges'] = {}
        self.fixture.events.append(latest)
        row, report = self.fixture.read()
        self.assertIsNone(row['cleared'])
        self.assertIsNone(row.get('verdict'))
        self.assertEqual([b['verdict'] for b in row['review_body_observations']], ['reject', 'reject'])
        self.assertEqual(report['reviews'][0]['unverified_body_observations'], 1)
        self.assertIn('admitted-subject-mismatch-or-incomplete', stored_body.review_canary.render(report))

    def test_gate_fallback_cannot_bypass_its_parsed_bodys_subject_conflict(self):
        path = self.write_body(json.loads(self.fixture.raw) | {'subject_pins': [self.subject | {'identity': 'other'}]})
        admission = self.fixture.events[2]['payload']
        self.fixture.events.append({'seq': 4, 'written_at': '2026-09-09T00:00:00Z', 'type': 'gate_result',
            'payload': {'gate_class': 'review', 'outcome': 'fail', 'verdict': 'reject', 'subject': self.subject,
                'evidence': [{'producing_run': {'run_ref': 1}, 'pin': {'identity': admission['identity'],
                    'version_seq': 2, 'content_hash': admission['content_hash']}}]}})
        row, _ = self.fixture.read()
        self.assertIsNone(row['cleared'])
        self.assertEqual(row['review_gate_observations'][0]['attribution'], 'evidence-body-attribution-conflict')
        path.unlink()
        row, report = self.fixture.read()
        self.assertIs(row['cleared'], False)
        self.assertEqual(report['reviews'][0]['verdict_source'], 'gate-only')
