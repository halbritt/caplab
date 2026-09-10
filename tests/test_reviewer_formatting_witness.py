from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_formatting_witness import assess_format, passed_tests


class FormattingWitnessTests(unittest.TestCase):
    def test_formatted_program_change_is_not_semantic_preservation(self):
        old = b'package p\nvar X = 1\n'
        new = b'package p\nvar X = 2\n'
        result = assess_format(old, new, old, new)
        self.assertFalse(result['canonical_outputs_equal'])
        self.assertTrue(result['change_is_formatted'])

    def test_equal_canonical_output_does_not_mean_changed_input_is_formatted(self):
        canonical = b'package p\nvar X = 1\n'
        result = assess_format(b'package p;var X=1', b'package p;var X = 1', canonical, canonical)
        self.assertTrue(result['canonical_outputs_equal'])
        self.assertFalse(result['change_is_formatted'])

    def test_pass_banner_without_exact_original_tests_is_insufficient(self):
        for output in ('PASS\n', '--- PASS: Other (0.00s)\nPASS\n',
                       '--- SKIP: Wanted (0.00s)\nPASS\n',
                       '--- PASS: Wanted (0.00s)\n--- PASS: Wanted (0.00s)\nPASS\n'):
            with self.subTest(output=output), self.assertRaises(ValueError):
                passed_tests(output, ['Wanted'])
        self.assertEqual(passed_tests('=== RUN   Wanted\n--- PASS: Wanted (0.00s)\nPASS\n', ['Wanted']), ['Wanted'])


if __name__ == '__main__':
    unittest.main()
