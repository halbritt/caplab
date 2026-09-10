import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reviewer_outcome_assessment import assess_lifetime, compare_reported, verify_capture
from codex_rollout_projection import project_rollout


class OutcomeAssessmentTest(unittest.TestCase):
    def setUp(self):
        self.fact = {'delayed_body_property_satisfied': False, 'lineage': 'introduced-module',
                     'source_file': 'src/runtime.ts', 'causal_region': [10, 20]}
        self.report = {'document_id': 'd', 'assertions': [{'hypothesis_id': 'h', 'stance': 'asserted'}],
                       'unmapped_claims': [], 'locations': ['src/runtime.ts:15']}

    def test_same_claim_has_different_meaning_on_introduction_inheritance_and_repair(self):
        introduced = assess_lifetime(self.report, self.fact, 'h')
        self.assertEqual(introduced['disposition'], 'confirmed-introduced-defect')
        inherited = self.fact | {'lineage': 'unchanged-module-and-only-codex-adapter-change'}
        self.assertEqual(assess_lifetime(self.report, inherited, 'h')['disposition'], 'inherited-behavior')
        repaired = self.fact | {'delayed_body_property_satisfied': True, 'lineage': 'changed-module'}
        outcome = assess_lifetime(self.report, repaired, 'h')
        self.assertEqual(outcome['disposition'], 'refuted-scenario')
        self.assertFalse(outcome['introduced_defect_credit'])

    def test_wrong_location_is_unresolved_not_automatically_false(self):
        self.report['locations'] = ['src/config.ts:15']
        result = assess_lifetime(self.report, self.fact, 'h')
        self.assertEqual(result['disposition'], 'causal-attribution-unresolved')
        self.assertFalse(result['introduced_defect_credit'])

    def test_one_finding_cannot_borrow_another_findings_aggregate_location(self):
        # The timeout report cites config.ts; another claim cites runtime.ts.
        # This old representation has already discarded that association.
        self.report['assertions'].append({'hypothesis_id': 'other', 'stance': 'asserted'})
        self.report['locations'] = ['src/config.ts:7', 'src/runtime.ts:15']
        result = assess_lifetime(self.report, self.fact, 'h')
        self.assertEqual(result['disposition'], 'causal-attribution-unresolved')
        self.assertFalse(result['introduced_defect_credit'])

    def test_uncertainty_retraction_and_omission_do_not_become_catches_or_clearance(self):
        for stance in ('uncertain', 'rejected'):
            self.report['assertions'][0]['stance'] = stance
            result = assess_lifetime(self.report, self.fact, 'h')
            self.assertFalse(result['introduced_defect_credit'])
            self.assertEqual(result['disposition'], 'uncertain-report' if stance == 'uncertain' else 'retracted-or-rejected-report')
        self.report['assertions'] = []
        self.assertEqual(assess_lifetime(self.report, self.fact, 'h')['disposition'], 'known-defect-not-reported')

    def test_unknown_and_other_claims_remain_available_for_investigation(self):
        self.report['assertions'].append({'hypothesis_id': 'other', 'stance': 'asserted'})
        self.report['unmapped_claims'] = ['A different finding remains unverified.']
        result = assess_lifetime(self.report, self.fact, 'h')
        self.assertEqual(result['unresolved_assertions'], [{'hypothesis_id': 'other', 'stance': 'asserted'}])
        self.assertEqual(result['unmapped_claims'], self.report['unmapped_claims'])

    def test_full_context_is_retained_and_extra_inferred_stance_fails_calibration(self):
        text = 'The timer ends at headers. This is the reported finding.'
        inputs = {'documents': [{'document_id': 'd', 'text': text}],
                  'hypotheses': [{'hypothesis_id': 'h'}, {'hypothesis_id': 'opposite'}]}
        expected = {'entries': [{'document_id': 'd', 'assertions': {'h': 'asserted'},
                                'unmapped_required': False, 'locations': []}], 'cases': {'d': 'case'}}
        self.report['locations'] = []
        result = compare_reported(inputs, expected, {'entries': [self.report]})
        self.assertTrue(result['all_match'])
        self.assertEqual(result['observations'][0]['full_source_text'], text)
        self.report['assertions'].append({'hypothesis_id': 'opposite', 'stance': 'rejected'})
        self.assertFalse(compare_reported(inputs, expected, {'entries': [self.report]})['all_match'])

    def test_duplicate_document_or_assertion_is_not_additional_credit(self):
        inputs = {'documents': [{'document_id': 'd', 'text': 'src/runtime.ts:15'}],
                  'hypotheses': [{'hypothesis_id': 'h'}]}
        expected = {'entries': [{'document_id': 'd', 'assertions': {'h': 'asserted'},
                                'unmapped_required': False, 'locations': ['src/runtime.ts:15']}], 'cases': {'d': 'case'}}
        for duplicate in ('document', 'assertion'):
            report = copy.deepcopy(self.report)
            entries = [report, report] if duplicate == 'document' else [report]
            if duplicate == 'assertion':
                report['assertions'] *= 2
            with self.subTest(duplicate=duplicate), self.assertRaises(ValueError):
                compare_reported(inputs, expected, {'entries': entries})

    def test_capture_requires_complete_files_and_explicit_projection_custody(self):
        digest = lambda data: hashlib.sha256(data).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relative = 'codex/sessions/2026/09/10/rollout-example.jsonl'
            raw = b'{"type":"response_item","payload":{"type":"reasoning","encrypted_content":"opaque"}}\n'
            projected, receipt = project_rollout(raw)
            implementation = b'fixture implementation'
            plan = {'readable_capture_projection': {'schema': receipt['schema'],
                    'implementation_sha256': digest(implementation)}}
            (root / 'plan.json').write_text(json.dumps(plan))
            (root / 'projection.py').write_bytes(implementation)
            entries = []
            for name, payload in [('stdout', b'output'), ('stderr', b''), ('final-message.txt', b'{}'), (relative, projected)]:
                path = root / 'capture' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                entries.append({'path': name, 'sha256': digest(payload), 'disposition': 'retained'})
            receipt.update(source_path=relative, plan_sha256=digest((root / 'plan.json').read_bytes()),
                           implementation_sha256=digest(implementation))
            receipt_relative = str(Path('projection-receipts') / Path(relative).with_suffix('.receipt.json'))
            receipt_path = root / receipt_relative
            receipt_path.parent.mkdir(parents=True)
            receipt_path.write_text(json.dumps(receipt))
            entries[-1].update(disposition='projected-retained', projection_receipt=receipt_relative,
                               projection_receipt_sha256=digest(receipt_path.read_bytes()))
            verify_capture(root, plan, {'entries': entries})
            for changed in (entries[:-1], entries + [entries[0]], entries[1:],
                            entries[:-1] + [entries[-1] | {'disposition': 'quarantined-prefix-retained'}]):
                with self.assertRaises(ValueError):
                    verify_capture(root, plan, {'entries': changed})
            with self.assertRaises(ValueError):
                verify_capture(root, {}, {'entries': entries})
            receipt_path.write_text('{}')
            with self.assertRaises(ValueError):
                verify_capture(root, plan, {'entries': entries})


if __name__ == '__main__':
    unittest.main()
