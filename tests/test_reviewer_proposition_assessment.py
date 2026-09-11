import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reviewer_proposition_assessment import inspect_assessment, assessment_schema
from jsonschema import Draft202012Validator


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


class PropositionAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'version.c').write_text('v244 allows on-failure\n')
        self.inventory = [{'path': 'version.c', 'sha256': digest((self.root / 'version.c').read_bytes())}]
        self.reported = dict(title='Compatibility concern', claim='Versions before v250 reject on-failure.',
            trigger='The deployment version is unknown.', expected_behavior='The supported host should load the unit.',
            observed_or_predicted_behavior='The rejection is predicted.', change_attribution='The unit is new.',
            evidence='Inspect upstream validation.', locations=[], claim_status='uncertain', acceptance_effect='advise')
        self.inputs = {'documents': [{'document_id': 'd', 'findings': [{'finding_id': 'f', 'reported': self.reported}],
                                      'limitations': ['No target host was observed.']}]}
        citation = dict(path='version.c', start_line=1, end_line=1, relation='contradicts',
                        kind='source', explanation='A pre-v250 counterexample.')
        self.entry = dict(document_id='d', finding_id='f', reported_claim_status='uncertain',
            acceptance_effect='advise', duplicate_of=None, no_defect_claim=False, no_defect_reason='',
            propositions=[dict(proposition_id='version', role='behavior', statement=self.reported['claim'],
                source_spans=[dict(field='claim', quote=self.reported['claim'])], scenario='The upstream v244 predicate.',
                status='contradicted', reason='v244 is a counterexample.', missing_evidence='', resolution='', evidence=[citation]),
                dict(proposition_id='host', role='applicability', statement='The actual host is affected.',
                source_spans=[dict(field='trigger', quote=self.reported['trigger'])], scenario='Actual deployment host.',
                status='unresolved', reason='No target version is supplied.', missing_evidence='Target host version.',
                resolution='Inspect the target host version under separate authorization.', evidence=[])])
        for role, field in [('requirement', 'expected_behavior'), ('change_attribution', 'change_attribution')]:
            self.entry['propositions'].append(dict(proposition_id=role, role=role, statement=self.reported[field],
                source_spans=[dict(field=field, quote=self.reported[field])], scenario='The new service unit.',
                status='unresolved', reason='This small test packet has no unit or support policy.',
                missing_evidence='Original unit and support policy.', resolution='Inspect the original artifacts.', evidence=[]))

    def inspect(self, entries=None):
        output = {'schema': 'caplab.review-proposition-assessment/v2', 'entries': entries if entries is not None else [self.entry]}
        return inspect_assessment(self.inputs, json.dumps(output).encode(), self.root, self.inventory)

    def test_false_premise_does_not_erase_unknown_applicability_or_advisory_stance(self):
        observed = self.inspect()
        row = observed['entries'][0]
        self.assertEqual(row['reported'], self.reported)
        self.assertEqual(observed['documents'][0]['limitations'], self.inputs['documents'][0]['limitations'])
        self.assertEqual([p['status'] for p in row['propositions'][:2]], ['contradicted', 'unresolved'])
        self.assertTrue(observed['representation_checks_pass'])
        self.assertFalse(observed['semantic_support_verified'])
        self.assertFalse(observed['ranking_eligible'])
        self.assertNotIn('defect_assessment', row)
        self.assertNotIn('score', observed)
        self.entry['acceptance_effect'] = 'block'
        self.assertFalse(self.inspect()['representation_checks_pass'])

    def test_equivalent_patch_and_source_locators_preserve_evidence_identity(self):
        (self.root / 'change.diff').write_text('+v244 allows on-failure\n')
        self.inventory.append({'path': 'change.diff', 'sha256': digest((self.root / 'change.diff').read_bytes())})
        for path in ['version.c', 'change.diff']:
            self.entry['propositions'][0]['evidence'][0]['path'] = path
            observed = self.inspect()
            self.assertTrue(observed['representation_checks_pass'])
            bound = observed['entries'][0]['propositions'][0]['evidence'][0]
            self.assertEqual(bound['location']['file_sha256'], digest((self.root / path).read_bytes()))
            self.assertFalse(observed['semantic_support_verified'])
        (self.root / 'change.diff').write_text('changed after inventory freeze\n')
        self.assertFalse(self.inspect()['representation_checks_pass'])
        self.entry['propositions'][0]['evidence'][0]['path'] = '../outside'
        self.assertFalse(self.inspect()['representation_checks_pass'])

    def test_missing_components_or_invented_quotes_cannot_look_complete(self):
        original = copy.deepcopy(self.entry)
        mutations = [lambda e: e['propositions'].pop(1),
            lambda e: e['propositions'][1].update(missing_evidence=''),
            lambda e: e['propositions'][1].update(resolution=''),
            lambda e: e['propositions'][0]['source_spans'][0].update(quote='The host definitely runs v243.'),
            lambda e: e['propositions'][0].update(evidence=[]),
            lambda e: e['propositions'][1].update(proposition_id='version'),
            lambda e: e.update(no_defect_claim=True, no_defect_reason='No claim.')]
        for mutate in mutations:
            self.entry = copy.deepcopy(original)
            mutate(self.entry)
            with self.subTest(entry=self.entry):
                self.assertFalse(self.inspect()['representation_checks_pass'])

    def test_duplicate_occurrences_and_withdrawal_survive_without_missing_rows(self):
        second_report = {**self.reported, 'claim_status': 'withdrawn'}
        self.inputs['documents'][0]['findings'].append({'finding_id': 'f2', 'reported': second_report})
        second = {**copy.deepcopy(self.entry), 'finding_id': 'f2', 'duplicate_of': 'f',
                  'reported_claim_status': 'withdrawn'}
        observed = self.inspect([second, self.entry])
        self.assertTrue(observed['representation_checks_pass'])
        self.assertEqual(observed['entries'][0]['reported']['claim_status'], 'withdrawn')
        self.assertEqual(observed['entries'][0]['duplicate_of'], 'f')
        self.entry['duplicate_of'] = 'f2'
        self.assertFalse(self.inspect([second, self.entry])['representation_checks_pass'])
        for rows in [[], [self.entry], [self.entry, self.entry]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.inspect(rows)

    def test_unrelated_but_authentic_evidence_never_establishes_semantic_support(self):
        Draft202012Validator.check_schema(assessment_schema())
        (self.root / 'irrelevant.txt').write_text('The logo is blue.\n')
        self.inventory.append({'path': 'irrelevant.txt', 'sha256': digest((self.root / 'irrelevant.txt').read_bytes())})
        self.entry['propositions'][0]['evidence'][0]['path'] = 'irrelevant.txt'
        observed = self.inspect()
        self.assertTrue(observed['representation_checks_pass'])
        self.assertFalse(observed['decomposition_complete_verified'])
        self.assertFalse(observed['semantic_support_verified'])
        self.assertFalse(observed['scorer_accepted'])


if __name__ == '__main__':
    unittest.main()
