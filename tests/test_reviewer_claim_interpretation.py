import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_claim_interpretation import compare, unique_object


class ClaimInterpretationTest(unittest.TestCase):
    def setUp(self):
        self.inputs = {'hypotheses': [{'hypothesis_id': 'h'}], 'documents': [
            {'document_id': 'd', 'text': 'At src/config.ts:7 the timeout may end early; not verified.'},
            {'document_id': 'u', 'text': 'The logger loses request identities.'}]}
        self.expected = {'entries': [
            {'document_id': 'd', 'assertions': {'h': 'uncertain'}, 'unmapped_required': False,
             'locations': ['src/config.ts:7']},
            {'document_id': 'u', 'assertions': {}, 'unmapped_required': True, 'locations': []}],
            'cases': {'d': 'uncertainty', 'u': 'unknown'}}
        self.output = {'entries': [
            {'document_id': 'd', 'assertions': [{'hypothesis_id': 'h', 'stance': 'uncertain',
             'quote': 'the timeout may end early; not verified.'}], 'unmapped_claims': [], 'locations': ['src/config.ts:7']},
            {'document_id': 'u', 'assertions': [], 'unmapped_claims': ['The logger loses request identities.'], 'locations': []}]}

    def test_strengthening_uncertainty_and_losing_unknown_findings_fail(self):
        self.assertTrue(compare(self.inputs, self.expected, self.output)['all_match'])
        self.output['entries'][0]['assertions'][0]['stance'] = 'asserted'
        self.output['entries'][1]['unmapped_claims'] = []
        result = compare(self.inputs, self.expected, self.output)
        self.assertEqual(result['matching_documents'], 0)
        self.assertFalse(result['observations'][0]['checks']['assertion_mapping_matches'])
        self.assertFalse(result['observations'][1]['checks']['unmapped_presence_matches'])

    def test_duplicate_or_missing_documents_cannot_improve_the_denominator(self):
        for entries in (self.output['entries'][:1], self.output['entries'] * 2):
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                compare(self.inputs, self.expected, {'entries': entries})

    def test_unknown_hypotheses_and_repeated_claim_rows_are_invalid(self):
        for variant in ('unknown', 'duplicate'):
            output = copy.deepcopy(self.output)
            if variant == 'unknown':
                output['entries'][0]['assertions'][0]['hypothesis_id'] = 'not-listed'
            else:
                output['entries'][0]['assertions'] *= 2
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                compare(self.inputs, self.expected, output)

    def test_fabricated_quote_and_corrected_location_are_not_attribution(self):
        for field, value in (('quote', 'the timeout definitely ends early'), ('location', 'src/runtime.ts:9')):
            output = copy.deepcopy(self.output)
            if field == 'quote':
                output['entries'][0]['assertions'][0]['quote'] = value
            else:
                output['entries'][0]['locations'] = [value]
            with self.subTest(field=field), self.assertRaises(ValueError):
                compare(self.inputs, self.expected, output)

    def test_duplicate_json_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"entries": [], "entries": [1]}', object_pairs_hook=unique_object)

    def test_literal_quote_is_not_proof_that_it_supports_the_hypothesis(self):
        # This limit is deliberate and must remain visible in study reports.
        self.output['entries'][0]['assertions'][0]['quote'] = 'At'
        self.assertTrue(compare(self.inputs, self.expected, self.output)['all_match'])


if __name__ == '__main__':
    unittest.main()
