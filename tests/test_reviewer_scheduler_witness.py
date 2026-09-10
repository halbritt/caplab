import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_scheduler_witness import assess


class SchedulerWitnessTest(unittest.TestCase):
    def setUp(self):
        self.criteria = {'expected_selected': {'ordinary-local': ['local']}}
        self.row = {'condition': 'ordinary-local', 'evaluation_error': '', 'stamp': 2, 'evaluation_version': 2,
                    'input': {'as_of': '2026-08-21T12:00:00Z'}, 'payload': {'input_preimage': {}},
                    'selected': ['local'], 'refusals': [], 'deferrals': [],
                    'stamped_record': {'encode_error': '', 'decode_error': ''},
                    'without_observations': {'selected': ['local'], 'error': ''}}

    def test_matching_versions_do_not_hide_record_encoder_or_decoder_failure(self):
        self.assertTrue(assess(self.row, self.criteria)['stamped_record_accepted'])
        for key in ('encode_error', 'decode_error'):
            row = copy.deepcopy(self.row)
            row['stamped_record'][key] = 'independent record boundary rejected payload'
            result = assess(row, self.criteria)
            self.assertTrue(result['version_agreement'])
            self.assertFalse(result['stamped_record_accepted'])

    def test_lost_causal_input_requires_observation_effect_and_durable_record(self):
        self.row['input']['capacity_observations'] = [{
            'RecordRef': 50, 'RecordHash': 'a' * 64, 'BackendID': 'remote', 'PassID': 'build',
            'SourceRunRef': 10, 'DispatchID': 'd10', 'SignatureID': 'limit',
            'Classifier': {'PolicyID': 'limits', 'PolicyVersion': 1, 'ContentHash': 'b' * 64},
            'ObservedAt': '2026-08-21T11:00:00Z', 'ExpiresAt': '2026-08-21T13:00:00Z', 'TTLSeconds': 7200}]
        self.row['without_observations']['selected'] = ['remote']
        result = assess(self.row, self.criteria)
        self.assertTrue(result['accepted_record_omits_selection_input'])
        self.row['stamp'] = 5
        self.assertFalse(assess(self.row, self.criteria)['accepted_record_omits_selection_input'])
        self.row['stamp'] = 2
        self.row['without_observations']['selected'] = ['local']
        self.assertFalse(assess(self.row, self.criteria)['accepted_record_omits_selection_input'])

    def test_expired_observation_is_not_a_missing_active_input(self):
        self.row['input']['capacity_observations'] = [{'ObservedAt': '2026-08-21T09:00:00Z',
                                                       'ExpiresAt': '2026-08-21T11:00:00Z'}]
        self.assertTrue(assess(self.row, self.criteria)['active_observations_retained'])

    def test_invalid_input_rejection_is_separate_from_valid_scenario_failure(self):
        self.row['evaluation_error'] = 'invalid TTL'
        self.assertEqual(assess(self.row, self.criteria)['disposition'], 'evaluation-failed')
        self.row['condition'] = 'malformed-observation'
        self.assertEqual(assess(self.row, self.criteria)['disposition'], 'malformed-input-rejected')
        self.row['evaluation_error'] = ''
        self.assertEqual(assess(self.row, self.criteria)['disposition'], 'malformed-input-accepted')


if __name__ == '__main__':
    unittest.main()
