import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_publication_witness import assess_instant, assess_rss, assess_timestamp, producer_dates


class PublicationWitnessTest(unittest.TestCase):
    def test_timezone_label_is_checked_as_an_instant_not_a_string(self):
        row = {'published_at': '2026-09-10T07:00:00-07:00', 'line': '[0] title @2026-09-10T07:00Z'}
        self.assertEqual(assess_timestamp(row)['rendered_error_seconds'], -7 * 3600)
        row['line'] = '[0] title @2026-09-10T14:00Z'
        self.assertTrue(assess_timestamp(row)['same_instant'])
        row['line'] = '[0] title @2026-09-10T07:00-07:00'
        self.assertTrue(assess_timestamp(row)['same_instant'])

    def test_publication_field_absence_stays_unknown(self):
        text = ('Unread articles (2):\n\n[1] [new] AI dated\n Blog: x\n URL: http://x/dated\n Published: 2026-09-10\n\n'
                '[2] [new] AI undated\n Blog: x\n URL: http://x/undated\n')
        self.assertEqual(producer_dates(text), {'dated': '2026-09-10', 'undated': None})
        with self.assertRaises(ValueError):
            producer_dates(text + '[3] [new] Duplicate\n URL: http://x/dated\n')

    def test_known_future_instant_is_outside_lookback(self):
        criteria = {'utc_date': '2026-09-10', 'instant_kept': {'future': False}}
        row = {'condition': 'future', 'published_at': '2026-09-17T12:00:00+00:00',
               'before': '2026-09-10T12:00:00+00:00', 'after': '2026-09-10T12:00:01+00:00', 'kept': True, 'dropped': 0}
        self.assertFalse(assess_instant(row, criteria)['matches'])
        row.update(kept=False, dropped=1)
        self.assertTrue(assess_instant(row, criteria)['matches'])

    def test_clock_boundary_ambiguity_cannot_supply_a_correctness_label(self):
        criteria = {'utc_date': '2026-09-10', 'instant_kept': {'inside': True}}
        row = {'condition': 'inside', 'published_at': '2026-09-09T12:00:00.500000+00:00',
               'before': '2026-09-10T12:00:00+00:00', 'after': '2026-09-10T12:00:01+00:00', 'kept': True, 'dropped': 0}
        with self.assertRaises(ValueError):
            assess_instant(row, criteria)

    def test_calendar_date_preservation_cannot_be_proved_by_inventing_midnight(self):
        criteria = {'producer_entries': ['today', 'undated', 'non-ai'], 'known_dates': {'today': '2026-09-10', 'non-ai': '2026-09-10'},
                    'expected_rss_candidates': ['today', 'undated']}
        producer = {'today': '2026-09-10', 'undated': None, 'non-ai': '2026-09-10'}
        rows = [{'url': 'http://127.0.0.1:8765/' + key, 'title': 'AI ' + key, 'published_at': None,
                 'published_date': producer[key]} for key in ('today', 'undated')]
        rss = {'parsed': rows, 'fetched': rows, 'pipeline_kept': rows}
        output = '\n'.join(row['url'] for row in rows)
        prompt = 'AI today @2026-09-10 (time unavailable)\nAI undated'
        self.assertTrue(assess_rss(rss, producer, output, prompt, criteria)['known_dates_preserved_without_invented_instants'])
        rows[0]['published_at'] = '2026-09-10T00:00:00Z'
        self.assertFalse(assess_rss(rss, producer, output, prompt, criteria)['known_dates_preserved_without_invented_instants'])
        rows[0]['published_at'] = None
        wrong_prompt = 'AI today\nDifferent article @2026-09-10 (time unavailable)\nAI undated'
        self.assertFalse(assess_rss(rss, producer, output, wrong_prompt, criteria)['date_only_evidence_visible_to_curator'])


if __name__ == '__main__':
    unittest.main()
