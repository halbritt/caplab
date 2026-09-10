import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_newsroom_findings_witness import assess


class NaturalFindingWitnessTests(unittest.TestCase):
    def setUp(self):
        self.criteria = {'names': ['A', 'B', 'C'], 'request_interval_seconds': 65,
                         'expected_urls': ['https://fixture/A', 'https://fixture/B', 'https://fixture/C']}
        self.requests = [{'path': f'/r/{name}/hot/?limit=25', 'monotonic': index / 10,
                          'headers': {'Host': 'old.reddit.com'}} for index, name in enumerate(self.criteria['names'])]
        self.articles = [{'url': url} for url in self.criteria['expected_urls']]
        self.row = {'condition': 'base-listing', 'results': {'listing': {'error': None, 'articles': self.articles}}}

    def test_requests_without_accepted_posts_do_not_establish_listing_control(self):
        self.row['results']['listing']['articles'] = []
        with self.assertRaises(ValueError):
            assess(self.row, self.requests, self.criteria)

    def test_overlapping_run_must_actually_refuse_before_network(self):
        row = {'condition': 'change-cli-lock', 'results': {
            'lock_remains_held': True, 'run': {'returncode': 2, 'requests_before': 3, 'requests_after': 4}}}
        with self.assertRaises(ValueError):
            assess(row, self.requests, self.criteria)
        row['results']['lock_remains_held'] = False
        row['results']['run']['requests_after'] = 3
        with self.assertRaises(ValueError):
            assess(row, self.requests, self.criteria)

    def test_disabled_rss_outcome_is_observed_instead_of_assumed_defective(self):
        successful = {'error': None, 'articles': self.articles, 'requests_before': 3, 'requests_after': 3}
        row = {'condition': 'change-pool', 'results': {
            name: copy.deepcopy(successful) for name in ('harvest', 'pool', 'disabled-harvest', 'disabled-pool')}}
        row['results']['database'] = {'candidates': self.articles, 'feeds': [], 'state': {'last_status': 'live'}}
        observed = assess(row, self.requests, self.criteria)
        self.assertIsNone(observed['disabled-harvest']['error'])
        self.assertEqual(observed['disabled-pool']['article_count'], 3)
        row['results']['disabled-pool'].update(error={'type': 'SourceUnavailable', 'message': 'state missing'}, articles=[])
        changed = assess(row, self.requests, self.criteria)
        self.assertEqual(changed['disabled-pool']['error']['type'], 'SourceUnavailable')
        self.assertEqual(changed['disabled-pool']['article_count'], 0)


if __name__ == '__main__':
    unittest.main()
