import copy
from decimal import Decimal, localcontext
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from caplab.code_agreement import build_code_agreement_report
from caplab.code_agreement_bounds import build_iid_agreement_bounds
import test_code_agreement as fixtures


class AgreementBoundsTests(unittest.TestCase):
    def test_balanced_perfect_sample_has_nonzero_uncertainty(self):
        source = fixtures.document([(False, False), (True, True)] * 5000)
        before = copy.deepcopy(source)
        report = build_iid_agreement_bounds(source, confidence=0.95)
        self.assertEqual(source, before)
        self.assertEqual(report['agreement'], build_code_agreement_report(source))
        row, = report['bounds']
        with localcontext() as context:
            context.prec = 60
            epsilon = (Decimal(120).ln() / 20000).sqrt()
            expected_low = 1 - epsilon / (Decimal('0.5') - 2 * epsilon**2)
        self.assertAlmostEqual(row['kappa'][0], float(expected_low), places=13)
        self.assertLess(row['kappa'][0], 1)
        self.assertEqual(row['kappa'][1], 1)
        self.assertFalse(row['undefined_population_kappa_not_excluded'])
        self.assertNotIn('passed', report)

    def test_small_perfect_sample_does_not_give_point_interval(self):
        row = build_iid_agreement_bounds(fixtures.document([(False, False), (True, True)]),
                                         confidence=0.95)['bounds'][0]
        self.assertEqual(row['kappa'], [-1, 1])
        self.assertTrue(row['undefined_population_kappa_not_excluded'])

    def test_constant_labels_keep_undefined_point_and_population_warning(self):
        for value in (False, True):
            report = build_iid_agreement_bounds(fixtures.document([(value, value)] * 100), confidence=0.95)
            self.assertIsNone(report['agreement']['codes'][0]['kappa'])
            self.assertEqual(report['bounds'][0]['kappa'], [-1, 1])
            self.assertTrue(report['bounds'][0]['undefined_population_kappa_not_excluded'])

    def test_declared_empty_rows_count_toward_family_and_remain_unavailable(self):
        source = fixtures.document([(False, False), (True, True)] * 500)
        single = build_iid_agreement_bounds(source, confidence=0.95)
        source['worlds']['unobserved'] = ['C1', 'C2']
        report = build_iid_agreement_bounds(source, confidence=0.95)
        self.assertEqual(report['family_size'], 3)
        rows = {(r['world'], r['code_id']): r for r in report['bounds']}
        self.assertLess(rows['w', 'C1']['kappa'][0], single['bounds'][0]['kappa'][0])
        self.assertEqual(rows['unobserved', 'C1']['bounds_unavailable_reason'], 'no-complete-pairs')
        self.assertIsNone(rows['unobserved', 'C1']['kappa'])
        self.assertIsNone(rows['unobserved', 'C2']['epsilon'])

    def test_missing_and_unavailable_pairs_do_not_inflate_sample_size(self):
        pairs = [(False, False), (True, True)] * 50
        source = fixtures.document(pairs)
        complete = build_iid_agreement_bounds(source, confidence=0.95)
        source['slots'] += [{'slot': 'missing', 'world': 'w'}, {'slot': 'unavailable', 'world': 'w'}]
        source['judgments'] += [{'slot': 'unavailable', 'coder_id': c, 'code_id': 'C1', 'value': None}
                                for c in ('a', 'b')]
        report = build_iid_agreement_bounds(source, confidence=0.95)
        self.assertEqual(report['bounds'], complete['bounds'])
        row = report['agreement']['codes'][0]
        self.assertEqual((row['expected_pairs'], row['complete_pairs'], row['incomplete_pairs']), (102, 100, 2))
        self.assertEqual(row['missing_judgments'], {'a': 1, 'b': 1})
        self.assertEqual(row['unavailable_judgments'], {'a': 1, 'b': 1})

    def test_more_confidence_widens_and_more_pairs_narrows(self):
        source = fixtures.document([(False, False), (True, True)] * 500)
        lower = lambda d, c: build_iid_agreement_bounds(d, confidence=c)['bounds'][0]['kappa'][0]
        self.assertLess(lower(source, 0.99), lower(source, 0.9))
        self.assertGreater(lower(source, 0.95), lower(fixtures.document([(False, False), (True, True)] * 50), 0.95))

    def test_asymmetric_labels_preserve_swap_and_order_symmetry(self):
        source = fixtures.document([(False, False)] * 60 + [(False, True)] * 10 + [(True, True)] * 30)
        first = build_iid_agreement_bounds(source, confidence=0.8)
        source['judgments'].reverse(); source['slots'].reverse()
        self.assertEqual(build_iid_agreement_bounds(source, confidence=0.8), first)
        source['coder_ids'].reverse()
        swapped = build_iid_agreement_bounds(source, confidence=0.8)
        self.assertEqual(swapped['bounds'][0]['kappa'], first['bounds'][0]['kappa'])
        self.assertEqual(swapped['bounds'][0]['coder_positive_rates'], first['bounds'][0]['coder_positive_rates'][::-1])

    def test_invalid_confidence_and_invalid_judgments_fail(self):
        source = fixtures.document([(False, True)])
        for confidence in (None, True, False, 0, 1, -0.1, 1.1, float('nan'), float('inf'), '0.95'):
            with self.subTest(confidence=confidence), self.assertRaises(ValueError):
                build_iid_agreement_bounds(source, confidence=confidence)
        source['judgments'][0]['value'] = 0
        with self.assertRaises(ValueError):
            build_iid_agreement_bounds(source, confidence=0.95)


class AgreementBoundsCLITests(unittest.TestCase):
    def test_opt_in_output_and_invalid_combinations(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'judgments.json'
            raw = json.dumps(fixtures.document([(False, False), (True, True)]), ensure_ascii=False).encode()
            source.write_bytes(raw)
            command = [sys.executable, 'scripts/code_agreement.py', str(source)]
            environment = {**os.environ, 'PYTHONPATH': 'src'}
            run = subprocess.run([*command, '--iid-confidence', '0.95'], env=environment,
                                 capture_output=True, text=True, check=True)
            report = json.loads(run.stdout)
            self.assertEqual(report['schema_version'], 'caplab-code-agreement-bounds-report/1')
            self.assertEqual(report['input_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(source.read_bytes(), raw)
            for args in (['--iid-confidence', 'nan'], ['--iid-confidence', '1'],
                         ['--iid-confidence', '0.95', '--reference', str(source)]):
                bad = subprocess.run([*command, *args], env=environment, capture_output=True, text=True)
                self.assertEqual(bad.returncode, 2, bad.stderr)
                self.assertEqual(bad.stdout, '')


if __name__ == '__main__':
    unittest.main()
