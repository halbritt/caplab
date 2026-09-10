import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_pool_transport_witness import assess


class PoolTransportWitnessTest(unittest.TestCase):
    def setUp(self):
        self.config = {'expected_bodies': {'control': 'a' * 64, 'mutant': 'b' * 64}}
        self.events = [{'arm': arm, 'body_sha256': digest, 'delivery': 'arg',
                        'response': '{"verdict":"accept","findings":[]}'}
                       for arm, digest in self.config['expected_bodies'].items()]
        self.observation = {'condition': 'pair-inline', 'kind': 'pool', 'row': {'usable': True},
                            'summary': {'pairs_usable': 1, 'pairs_discarded': 0, 'catch_rate': 0.0, 'false_alarm_rate': 0.0}}

    def test_parseable_json_without_verdict_is_not_a_valid_response(self):
        self.assertFalse(assess(self.observation, self.config, self.events)['invalid_response_enters_denominator'])
        for response in ('{"status":"done"}', '{"verdict":"invented","findings":[]}', '', None):
            self.events[1]['response'] = response
            with self.subTest(response=response):
                self.assertTrue(assess(self.observation, self.config, self.events)['invalid_response_enters_denominator'])

    def test_discarded_timeout_is_missingness_not_a_scored_clearance(self):
        self.events[1]['response'] = None
        self.observation['row']['usable'] = False
        self.observation['summary'].update(pairs_usable=0, pairs_discarded=1, catch_rate=None, false_alarm_rate=None)
        result = assess(self.observation, self.config, self.events)
        self.assertFalse(result['invalid_response_enters_denominator'])
        self.assertFalse(result['independently_valid_response_pair'])

    def test_original_denominator_must_match_persisted_row(self):
        self.observation['summary']['pairs_usable'] = 0
        with self.assertRaises(ValueError):
            assess(self.observation, self.config, self.events)

    def test_duplicate_or_corrupted_body_receipts_cannot_supply_transport_evidence(self):
        events = copy.deepcopy(self.events)
        events[1]['body_sha256'] = 'c' * 64
        with self.assertRaises(ValueError):
            assess(self.observation, self.config, events)
        with self.assertRaises(ValueError):
            assess(self.observation, self.config, self.events + [self.events[0]])

    def test_explicit_refusal_and_silent_nondelivery_are_distinct(self):
        config = {'expected_bodies': {'direct': 'a' * 64}}
        observation = {'condition': 'direct-arg-over', 'kind': 'invoke',
                       'result': {'error': 'prompt exceeds transport capacity', 'exit_code': None, 'transport': 'none'}}
        result = assess(observation, config, [])
        self.assertTrue(result['explicit_prelaunch_refusal'])
        self.assertTrue(result['delivery_or_refusal'])
        observation['result'].update(error=None, exit_code=0, transport='stdin-oversize-fallback')
        events = [{'arm': None, 'body_sha256': 'unused', 'delivery': 'absent', 'response': ''}]
        result = assess(observation, config, events)
        self.assertTrue(result['silently_undelivered'])
        self.assertFalse(result['delivery_or_refusal'])


if __name__ == '__main__':
    unittest.main()
