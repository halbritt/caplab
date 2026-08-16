import json
import os
import tempfile
import unittest

from caplab.advisory.compare import _binom_two_sided, paired_comparison


def write_run(root, name, rows, aborted=None):
    run_dir = os.path.join(root, name)
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "results.jsonl"), "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    with open(os.path.join(run_dir, "summary.json"), "w") as f:
        json.dump({"instrument": "matched-pair defect injection",
                   "aborted": aborted}, f)
    return run_dir


def row(dispatch, caught, alarm=False, cls="dropped_section"):
    return {"dispatch_id": dispatch, "usable": True, "caught": caught,
            "false_alarm": alarm, "defect_class": cls,
            "control_json_valid": True, "mutant_json_valid": True}


class CompareTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_pairs_on_shared_cases_only(self):
        a = write_run(self.root, "a", [row("1" * 64, True), row("2" * 64, True),
                                       row("3" * 64, True)])
        b = write_run(self.root, "b", [row("2" * 64, False), row("3" * 64, True),
                                       row("4" * 64, True)])
        result = paired_comparison(a, b)
        self.assertEqual(result["shared_cases"], 2)
        self.assertEqual(result["a_only_caught"], 1)
        self.assertEqual(result["b_only_caught"], 0)
        self.assertEqual(result["both_caught"], 1)

    def test_concordant_pairs_are_uninformative(self):
        rows_a = [row(str(i) * 64, True) for i in range(1, 6)]
        rows_b = [row(str(i) * 64, True) for i in range(1, 6)]
        result = paired_comparison(write_run(self.root, "a", rows_a),
                                   write_run(self.root, "b", rows_b))
        self.assertEqual(result["discordant_pairs"], 0)
        self.assertEqual(result["uninformative_pairs"], 5)
        self.assertEqual(result["sign_test_p"], 1.0)
        self.assertFalse(result["significant_at_05"])

    def test_small_discordance_is_not_significant(self):
        # 3 vs 0 discordant: p = 0.25, honestly not enough.
        rows_a = [row(str(i) * 64, True) for i in range(1, 4)]
        rows_b = [row(str(i) * 64, False) for i in range(1, 4)]
        result = paired_comparison(write_run(self.root, "a", rows_a),
                                   write_run(self.root, "b", rows_b))
        self.assertEqual(result["discordant_pairs"], 3)
        self.assertAlmostEqual(result["sign_test_p"], 0.25, places=6)
        self.assertFalse(result["significant_at_05"])
        self.assertIn("does not establish", result["reading"])

    def test_large_discordance_is_significant(self):
        rows_a = [row(str(i).zfill(64), True) for i in range(1, 9)]
        rows_b = [row(str(i).zfill(64), False) for i in range(1, 9)]
        result = paired_comparison(write_run(self.root, "a", rows_a),
                                   write_run(self.root, "b", rows_b))
        self.assertAlmostEqual(result["sign_test_p"], 2 * 0.5 ** 8, places=6)
        self.assertTrue(result["significant_at_05"])

    def test_aborted_run_refuses_comparison(self):
        a = write_run(self.root, "a", [row("1" * 64, True)])
        b = write_run(self.root, "b", [row("1" * 64, True)], aborted="limit")
        with self.assertRaises(ValueError):
            paired_comparison(a, b)

    def test_binom_symmetry(self):
        self.assertEqual(_binom_two_sided(0, 0), 1.0)
        self.assertAlmostEqual(_binom_two_sided(0, 5), 2 * 0.5 ** 5, places=9)


if __name__ == "__main__":
    unittest.main()
