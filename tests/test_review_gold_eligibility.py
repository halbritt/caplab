"""Downstream artifact gates are observations, not adjudications of reviews."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import review_criterion_ledger_pass as criterion
from test_review_gate_attribution import gate_for_review


class ReviewGoldEligibilityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.events = []
        self.event('graph_genesis', {})

    def event(self, kind, payload, at=None):
        seq = len(self.events)
        self.events.append({'seq': seq, 'type': kind,
                            'written_at': at or f'2026-09-09T00:00:{seq:02d}Z', 'payload': payload})
        return seq

    def review(self, verdict='pass', close=True, **pin):
        subject = {'identity': 'work/a/change-set', 'version_seq': 0, 'content_hash': 'same-bytes'} | pin
        run = self.event('pass_run_opened', {'pass_id': 'review', 'manifest': {
            'subject_pin': subject, 'input_pins': [{'role': 'materialized_base', 'content_hash': 'base'}]}})
        if verdict:
            gate_for_review(self.event, self.events, run, verdict)
        if close:
            self.event('pass_run_closed', {'run_ref': run, 'outcome': 'submitted'})
        return run

    def acceptance(self, outcome='fail', at=None, **pin):
        subject = {'identity': 'work/a/change-set', 'version_seq': 0, 'content_hash': 'same-bytes'} | pin
        return self.event('gate_result', {'gate_class': 'acceptance', 'authority': {'kind': 'principal'},
            'outcome': outcome, 'subject': subject, 'applicability': {'materialization': {
                'kind': 'artifact-body', 'identity': subject['identity'], 'content_hash': subject['content_hash']}},
            'detail': 'Artifact acceptance only'}, at)

    def read(self):
        ledger = self.root / 'ledger.jsonl'
        ledger.write_text(''.join(json.dumps(e) + '\n' for e in self.events))
        return criterion.read_reviews(str(ledger))

    def test_artifact_acceptance_cannot_supply_gold_in_either_review_direction(self):
        clear = self.review()
        refuse = self.review(verdict='fail', version_seq=1, content_hash='refused-bytes')
        self.acceptance('fail')
        self.acceptance('pass', version_seq=1, content_hash='refused-bytes')
        _, report, runs, strata = self.read()
        self.assertFalse(strata.get('gold-defect'))
        self.assertFalse(strata.get('gold-clear'))
        self.assertTrue(report['gold_outcomes'].startswith('unavailable:'))
        self.assertTrue(runs[clear]['cleared'])
        self.assertFalse(runs[refuse]['cleared'])
        self.assertEqual(len(runs[clear]['later']['acceptance_fail']), 1)
        self.assertEqual(len(runs[refuse]['later']['acceptance_pass']), 1)

    def test_shared_bytes_do_not_join_acceptance_across_artifact_identities_or_versions(self):
        exact = self.review()
        other_identity = self.review(identity='work/b/change-set')
        other_version = self.review(version_seq=1)
        gate = self.acceptance()
        _, report, runs, _ = self.read()
        self.assertEqual([e['seq'] for e in runs[exact]['later']['acceptance_fail']], [gate])
        self.assertEqual(runs[other_identity]['later']['acceptance_fail'], [])
        self.assertEqual(runs[other_version]['later']['acceptance_fail'], [])
        self.assertEqual(report['principal_acceptance_rulings']['total'], 1)

    def test_acceptance_uses_ledger_closure_order_and_preserves_unknown_verdict_observations(self):
        closed = self.review(close=False)
        self.acceptance(at='2099-01-01T00:00:00Z')
        self.event('pass_run_closed', {'run_ref': closed, 'outcome': 'submitted'})
        after = self.acceptance(at='2000-01-01T00:00:00Z')
        opened = self.review(close=False)
        unknown = self.review(verdict=None)
        latest = self.acceptance('pending')
        _, _, runs, _ = self.read()
        self.assertEqual([e['seq'] for e in runs[closed]['later']['acceptance_fail']], [after])
        self.assertEqual(runs[opened]['post_close_acceptance_observations'], [])
        self.assertEqual([e['seq'] for e in runs[unknown]['post_close_acceptance_observations']], [latest])
        self.assertIsNone(runs[unknown]['cleared'])

    def test_cli_retains_acceptance_observations_without_gold_cases(self):
        run = self.review()
        gate = self.acceptance()
        self.read()
        out = self.root / 'output'
        completed = subprocess.run([sys.executable, str(SCRIPTS / 'review_criterion_ledger_pass.py'),
            '--ledger', str(self.root / 'ledger.jsonl'), '--out', str(out)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        observations = [json.loads(line) for line in (out / 'review-acceptance-observations.jsonl').read_text().splitlines()]
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]['review_run'], run)
        self.assertEqual(observations[0]['acceptance']['seq'], gate)
        self.assertEqual(observations[0]['subject'], {'identity': 'work/a/change-set', 'version_seq': 0,
                                                     'content_hash': 'same-bytes'})
        report = json.loads((out / 'review-criterion-summary.json').read_text())
        self.assertEqual(observations[0]['ledger_sha256'], report['snapshot']['sha256'])
        self.assertTrue(report['gold_outcomes'].startswith('unavailable:'))
        self.assertEqual((out / 'review-criterion-cases.jsonl').read_bytes(), b'')

    def test_existing_export_is_not_overwritten_by_the_repaired_method(self):
        self.review()
        self.read()
        out = self.root / 'existing'; out.mkdir()
        original = out / 'review-criterion-summary.json'
        original.write_bytes(b'preserved earlier method output\n')
        completed = subprocess.run([sys.executable, str(SCRIPTS / 'review_criterion_ledger_pass.py'),
            '--ledger', str(self.root / 'ledger.jsonl'), '--out', str(out)], capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(original.read_bytes(), b'preserved earlier method output\n')
        self.assertEqual(list(out.iterdir()), [original])

    def test_incomplete_pins_do_not_match_even_when_both_records_omit_the_same_field(self):
        for field in ('identity', 'version_seq', 'content_hash'):
            with self.subTest(field=field):
                self.events[:] = self.events[:1]
                run = self.review(**{field: None})
                self.acceptance(**{field: None})
                _, report, runs, _ = self.read()
                self.assertEqual(runs[run]['post_close_acceptance_observations'], [])
                self.assertEqual(report['principal_acceptance_rulings']['total'], 1)

    def test_acceptance_version_reference_is_not_coerced_from_boolean_or_text(self):
        self.review()
        for value in (True, False, '0', -1):
            with self.subTest(value=value):
                self.acceptance(version_seq=value)
                with self.assertRaisesRegex(ValueError, 'subject.version_seq'):
                    self.read()
                self.events.pop()

    def test_product_tree_gate_links_subject_bytes_instead_of_materialized_tree(self):
        subject = {'identity': 'work/a/product', 'version_seq': 1, 'content_hash': 'a' * 64}
        run = self.review(**subject)
        tree_bytes = self.review(**(subject | {'content_hash': 'b' * 64}))
        producer = {'run_ref': 1, 'run_manifest_hash': 'c' * 64}
        gate = self.event('gate_result', {
            'operation_key': 'd' * 64, 'subject': subject, 'request_ref': 1,
            'target_semantic_hash': 'e' * 64, 'producing_run': producer,
            'gate_id': 'principal-acceptance', 'gate_class': 'acceptance',
            'gate_contract_hash': 'f' * 64, 'gate_predicate_version': 1,
            'outcome': 'fail', 'verdict': 'reject', 'inputs_fresh': True, 'evidence': [],
            'semantic_environment': {'digest': '1' * 64, 'pins': [
                {'kind': 'gate-contract', 'id': 'principal-acceptance', 'hash': 'f' * 64}]},
            'applicability': {
                'product': subject | {'linked_tree_hash': '2' * 64, 'materialized_tree_hash': 'b' * 64},
                'materialization': {'kind': 'product-tree', 'identity': subject['identity'], 'content_hash': 'b' * 64}},
            'independence': {'predicate': 'not-required@1', 'result': 'not_required',
                'producer': producer | {'lane_id': 'synthetic', 'backend_id': 'synthetic',
                    'aliasing_class': 'synthetic', 'session_nonce': 'synthetic'}, 'evidence': []},
            'authority': {'kind': 'principal', 'identity': 'synthetic-principal',
                          'authority_proof': {'synthetic': True}},
        })
        self.events[gate]['schema_version'] = 2
        _, report, runs, strata = self.read()
        observation, = runs[run]['post_close_acceptance_observations']
        self.assertEqual(observation['seq'], gate)
        self.assertEqual({key: observation[key] for key in subject}, subject)
        self.assertEqual(runs[tree_bytes]['post_close_acceptance_observations'], [])
        self.assertEqual(report['acceptance_observation_linkage'], 'gate-subject-pin-after-review-closure/2')
        self.assertEqual(report['principal_acceptance_rulings']['by_class'], {'product': 1})
        self.assertFalse(strata.get('gold-defect'))

    def test_missing_subject_does_not_fall_back_to_a_materialization_pin(self):
        run = self.review()
        gate = self.acceptance()
        payload = self.events[gate]['payload']
        payload['applicability']['materialization'] = payload.pop('subject')
        _, report, runs, _ = self.read()
        self.assertEqual(runs[run]['post_close_acceptance_observations'], [])
        self.assertEqual(report['principal_acceptance_rulings']['total'], 1)
        self.assertEqual(report['principal_acceptance_rulings']['by_class'], {'(unknown)': 1})
