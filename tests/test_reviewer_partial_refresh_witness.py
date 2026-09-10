import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_partial_refresh_witness import assess


class PartialRefreshWitnessTests(unittest.TestCase):
    def setUp(self):
        self.expected = [{'host': 'old.reddit.com', 'path': '/healthy', 'status': 200, 'body_sha256': 'html', 'body_bytes': 8},
                         {'host': 'www.reddit.com', 'path': '/fallback', 'status': 403, 'body_sha256': 'failure', 'body_bytes': 7}]
        self.row = {'condition': 'mixed-rss-failure', 'returncode': 0,
                    'database': {'state': {'last_status': 'unavailable', 'last_error': 'HTTP 403', 'last_harvest_at': '123'},
                                 'candidates': [{'url': 'https://healthy'}], 'feeds': []}}
        self.criteria = {'controls': {}}

    def test_success_status_is_observed_and_a_correct_failure_is_also_representable(self):
        result = assess(self.row, self.expected, self.expected, self.criteria)
        self.assertTrue(result['failed_refresh_reported_success'])
        self.row['returncode'] = 1
        result = assess(self.row, self.expected, self.expected, self.criteria)
        self.assertFalse(result['failed_refresh_reported_success'])

    def test_missing_or_wrong_endpoint_evidence_cannot_validate_the_trigger(self):
        for changes in ({'status': 404}, {'body_sha256': 'other'}, {'host': 'unrelated'}):
            requests = copy.deepcopy(self.expected)
            requests[-1].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                assess(self.row, requests, self.expected, self.criteria)
        with self.assertRaises(ValueError):
            assess(self.row, self.expected[:-1], self.expected, self.criteria)

    def test_failed_control_cannot_be_treated_as_successful_witness(self):
        self.criteria['controls']['mixed-rss-failure'] = {'exit': 1, 'urls': ['https://healthy']}
        with self.assertRaises(ValueError):
            assess(self.row, self.expected, self.expected, self.criteria)

    def test_cached_feed_cannot_stand_in_for_the_no_cache_failure(self):
        self.row['database']['feeds'] = [{'url': 'https://cached'}]
        with self.assertRaises(ValueError):
            assess(self.row, self.expected, self.expected, self.criteria)


if __name__ == '__main__':
    unittest.main()
