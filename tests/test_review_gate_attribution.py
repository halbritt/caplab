"""A gate fallback must identify one admitted review of this subject."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import review_criterion_ledger_pass as criterion
import review_canary


def gate_for_review(event, events, run, outcome):
    subject = events[run]['payload']['manifest']['subject_pin']
    verdict = {'pass': 'accept', 'fail': 'reject'}.get(outcome, 'unknown')
    identity, content_hash = f'reviews/{run}', f'review-hash-{run}'
    admission = event('artifact_admitted', {'kind': 'review-ledger', 'produced_by_run': run,
        'identity': identity, 'content_hash': content_hash,
        'edges': {'evidences': [{'subject': subject, 'claim': f'verdict:{verdict}'}]}})
    return event('gate_result', {'gate_class': 'review', 'outcome': outcome, 'verdict': verdict,
        'subject': subject, 'evidence': [{'pin': {'identity': identity, 'version_seq': admission,
            'content_hash': content_hash}, 'producing_run': {'run_ref': run}}]})


class ReviewGateAttributionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.events = []
        self.event('graph_genesis', {})

    def event(self, kind, payload):
        seq = len(self.events)
        self.events.append({'seq': seq, 'type': kind, 'written_at': '2026-09-09T00:00:00Z', 'payload': payload})
        return seq

    def review(self):
        run = self.event('pass_run_opened', {'pass_id': 'review', 'manifest': {
            'subject_pin': {'identity': 'work/change-set', 'version_seq': 1, 'content_hash': 'subject'},
            'input_pins': [{'role': 'materialized_base', 'content_hash': 'base'}]}})
        gate = gate_for_review(self.event, self.events, run, 'pass')
        self.event('pass_run_closed', {'run_ref': run, 'outcome': 'submitted'})
        return run, gate

    def read(self):
        ledger = self.root / 'ledger.jsonl'
        ledger.write_text(''.join(json.dumps(e) + '\n' for e in self.events))
        snapshot, report, runs, strata = criterion.read_reviews(str(ledger))
        return report, runs, review_canary.summarize(snapshot, runs, 0)

    def test_gate_subject_mismatch_cannot_assign_a_review_verdict(self):
        run, gate = self.review()
        self.events[gate]['payload']['subject'] = {'identity': 'another/change-set', 'version_seq': 1, 'content_hash': 'subject'}
        _, runs, report = self.read()
        self.assertIsNone(runs[run]['cleared'])
        observation, = runs[run]['review_gate_observations']
        self.assertEqual(observation['attribution'], 'subject-mismatch-or-incomplete')
        self.assertEqual(observation['outcome'], 'pass')
        self.assertEqual(report['reviews'][0]['decision'], 'unknown')

    def test_gate_requires_exact_preceding_admission_and_its_recorded_verdict(self):
        run, gate = self.review()
        baseline = copy.deepcopy(self.events)
        changes = {
            'missing-evidence-pin': lambda p, a: p['evidence'][0].pop('pin'),
            'wrong-evidence-hash': lambda p, a: p['evidence'][0]['pin'].update(content_hash='other'),
            'wrong-evidence-identity': lambda p, a: p['evidence'][0]['pin'].update(identity='other'),
            'wrong-evidence-version': lambda p, a: p['evidence'][0]['pin'].update(version_seq=run),
            'wrong-producer': lambda p, a: a.update(produced_by_run=0),
            'wrong-kind': lambda p, a: a.update(kind='verification-report'),
            'wrong-admitted-subject': lambda p, a: a['edges']['evidences'][0].update(subject={}),
            'wrong-admitted-verdict': lambda p, a: a['edges']['evidences'][0].update(claim='verdict:reject'),
            'missing-admitted-claim': lambda p, a: a.pop('edges'),
            'contradictory-gate-verdict': lambda p, a: p.update(verdict='reject'),
            'multiple-evidence': lambda p, a: p['evidence'].append({'producing_run': {'run_ref': 0}}),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                self.events = copy.deepcopy(baseline)
                change(self.events[gate]['payload'], self.events[gate - 1]['payload'])
                _, runs, _ = self.read()
                self.assertIsNone(runs[run]['cleared'])
                self.assertNotEqual(runs[run]['review_gate_observations'][0]['attribution'], 'linked')

    def test_exact_gate_fallback_is_retained_once_and_unverified_latest_cannot_inherit_it(self):
        run, gate = self.review()
        payload = self.events[gate]['payload']
        payload['evidence'] *= 2
        _, runs, report = self.read()
        self.assertTrue(runs[run]['cleared'])
        self.assertEqual(len(runs[run]['review_gate_observations']), 1)
        self.assertEqual(report['reviews'][0]['verdict_source'], 'gate-only')
        latest = copy.deepcopy(payload)
        latest.pop('subject')
        self.event('gate_result', latest)
        _, runs, report = self.read()
        self.assertIsNone(runs[run]['cleared'])
        self.assertEqual(report['reviews'][0]['unverified_gate_observations'], 1)
        self.assertIn('subject-mismatch-or-incomplete', review_canary.render(report))

    def test_disagreement_requires_the_same_admitted_body_as_the_gate_evidence(self):
        run, gate = self.review()
        admission = self.events[gate - 1]['payload']
        admission['body'] = {'content_hash': 'a' * 64}
        admission['content_hash'] = 'a' * 64
        self.events[gate]['payload']['evidence'][0]['pin']['content_hash'] = 'a' * 64
        with patch.object(criterion.M, 'store_object', return_value=b'{"verdict":"reject"}'):
            _, _, report = self.read()
        self.assertTrue(report['reviews'][0]['body_gate_disagreement'])
        self.event('artifact_admitted', copy.deepcopy(admission))
        with patch.object(criterion.M, 'store_object', return_value=b'{"verdict":"reject"}'):
            _, _, report = self.read()
        self.assertFalse(report['reviews'][0]['body_gate_disagreement'])
        self.assertFalse(report['reviews'][0]['body_gate_comparable'])
        self.assertEqual(report['reviews'][0]['decision'], 'refused')

    def test_future_admission_cannot_retroactively_support_a_gate(self):
        run, gate = self.review()
        future = self.event('artifact_admitted', copy.deepcopy(self.events[gate - 1]['payload']))
        self.events[gate]['payload']['evidence'][0]['pin']['version_seq'] = future
        _, runs, _ = self.read()
        self.assertIsNone(runs[run]['cleared'])
        self.assertEqual(runs[run]['review_gate_observations'][0]['attribution'],
                         'evidence-admission-missing-or-out-of-order')

    def test_evidence_sequence_references_are_validated_before_body_reads(self):
        run, gate = self.review()
        for value in (True, False, 2.0, '2', -1, [], {}):
            with self.subTest(value=value):
                self.events[gate]['payload']['evidence'][0]['pin']['version_seq'] = value
                with patch.object(criterion.M, 'store_object') as store:
                    with self.assertRaisesRegex(ValueError, 'pin.version_seq'):
                        self.read()
                store.assert_not_called()
