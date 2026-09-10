import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_reddit_recovery_witness import assess


class RedditRecoveryWitnessTest(unittest.TestCase):
    def setUp(self):
        self.criteria = {'drip_seconds': 190, 'socket_timeout_seconds': 30, 'recovery_seconds': 180,
                         'timing_tolerance_seconds': 2, 'expected_urls': ['https://fixture/fresh']}
        self.row = {'condition': 'drip', 'elapsed_seconds': 190.2, 'error': None,
                    'articles': [{'url': 'https://fixture/fresh'}], 'reopened_articles': [{'url': 'https://fixture/fresh'}],
                    'reopen_error': None, 'requests_before_reopen': 1, 'requests_after_reopen': 1,
                    'state': {'last_status': 'live'}}
        self.events = [{'event': 'request', 'monotonic': 0.0, 'headers': {}, 'path': '/r/MachineLearning/hot/.rss?limit=25'},
                       {'event': 'headers', 'monotonic': 0.01}]
        self.events += [{'event': 'byte', 'monotonic': 0.02 + i, 'index': i} for i in range(190)]
        self.events.append({'event': 'body-complete', 'monotonic': 190.02})

    def test_successful_persistence_does_not_establish_a_bounded_request(self):
        result = assess(self.row, self.events, {'complete': True}, self.criteria)
        self.assertTrue(result['harvest_succeeded'])
        self.assertTrue(result['pool_reopens'])
        self.assertTrue(result['successful_harvest_exceeds_recovery_budget'])

    def test_inactivity_gap_cannot_be_used_as_active_stream_evidence(self):
        events = copy.deepcopy(self.events)
        for event in events[100:]:
            event['monotonic'] += 31
        with self.assertRaises(ValueError):
            assess(self.row, events, {'complete': True}, self.criteria)

    def test_missing_endpoint_request_is_fixture_failure(self):
        with self.assertRaises(ValueError):
            assess(self.row, self.events[1:], {'complete': True}, self.criteria)

    def test_ordinary_completion_and_timely_rejection_are_separate_outcomes(self):
        row = copy.deepcopy(self.row)
        row.update(condition='ordinary', elapsed_seconds=0.1)
        events = self.events[:2] + [{'event': 'body-complete', 'monotonic': 0.1}]
        self.assertTrue(assess(row, events, {'complete': True}, self.criteria)['budget_respected_with_tolerance'])
        row = copy.deepcopy(self.row)
        row.update(elapsed_seconds=180.1, error={'type': 'SourceUnavailable'}, articles=[], reopened_articles=[])
        active_until_rejection = [e for e in self.events if e['monotonic'] < 180.1]
        result = assess(row, active_until_rejection, {'complete': False}, self.criteria)
        self.assertTrue(result['budget_respected_with_tolerance'])
        self.assertFalse(result['harvest_succeeded'])
        self.assertFalse(result['successful_harvest_exceeds_recovery_budget'])


if __name__ == '__main__':
    unittest.main()
