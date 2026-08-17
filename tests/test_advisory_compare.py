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
        self.assertIn("not established", result["reading"])

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

    def test_false_alarm_pairing_is_tested_separately(self):
        # A subject may catch no better yet refuse sound controls far more.
        # Catch-rate pairing cannot see that; discrimination must.
        rows_a = [row(str(i) * 64, True, alarm=False) for i in range(1, 7)]
        rows_b = [row(str(i) * 64, True, alarm=True) for i in range(1, 7)]
        result = paired_comparison(write_run(self.root, "a", rows_a),
                                   write_run(self.root, "b", rows_b))
        self.assertEqual(result["discordant_pairs"], 0)
        self.assertEqual(result["sign_test_p"], 1.0)
        self.assertEqual(result["false_alarm_discordant_pairs"], 6)
        self.assertTrue(result["false_alarm_significant_at_05"])
        self.assertEqual(result["a_discrimination"], 1.0)
        self.assertEqual(result["b_discrimination"], 0.0)

    def test_dead_arm_and_anchor_rows_do_not_pair(self):
        # A pair with an unmeasured arm is not a measurement, and anchor
        # rows measure the instrument, not the corpus.
        rows_a = [row("1" * 64, True),
                  {**row("2" * 64, True), "mutant_json_valid": False},
                  {**row("3" * 64, True), "anchor": True}]
        rows_b = [row("1" * 64, False), row("2" * 64, False),
                  {**row("3" * 64, False), "anchor": True}]
        result = paired_comparison(write_run(self.root, "a", rows_a),
                                   write_run(self.root, "b", rows_b))
        self.assertEqual(result["shared_cases"], 1)
        self.assertEqual(result["a_only_caught"], 1)

    def test_discordant_cases_are_itemized(self):
        # Promotion into a discrimination corpus needs to know WHICH cases
        # separated the pair, not only how many.
        rows_a = [row("1" * 64, True, cls="hash_mismatch"),
                  row("2" * 64, True)]
        rows_b = [row("1" * 64, False, cls="hash_mismatch"),
                  row("2" * 64, True)]
        result = paired_comparison(write_run(self.root, "a", rows_a),
                                   write_run(self.root, "b", rows_b))
        self.assertEqual(result["discordant_cases"], [
            {"dispatch_id": "1" * 64, "substrate_id": None,
             "defect_class": "hash_mismatch", "caught_by": "a"}])

    def test_binom_symmetry(self):
        self.assertEqual(_binom_two_sided(0, 0), 1.0)
        self.assertAlmostEqual(_binom_two_sided(0, 5), 2 * 0.5 ** 5, places=9)


if __name__ == "__main__":
    unittest.main()


class ComparisonAdjudicationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_defective_control_pairs_leave_the_false_alarm_test(self):
        from caplab.advisory.adjudication import (Adjudications,
                                                  build_adjudication)
        rows_a = [row("1" * 64, True, alarm=False), row("2" * 64, True, alarm=False)]
        rows_b = [row("1" * 64, True, alarm=True), row("2" * 64, True, alarm=True)]
        a = write_run(self.root, "a", rows_a)
        b = write_run(self.root, "b", rows_b)

        plain = paired_comparison(a, b)
        self.assertEqual(plain["false_alarm_discordant_pairs"], 2)
        self.assertEqual(plain["false_alarm_unaudited_pairs"], 2)
        self.assertEqual(plain["false_alarm_audit_status"],
                         "contains-unaudited-refusals")

        adj = Adjudications([build_adjudication(
            dispatch_id="1" * 64, disposition="defective",
            basis="audited", adjudicated_by="principal:test",
            as_of="2026-08-16T00:00:00+00:00")])
        judged = paired_comparison(a, b, adjudications=adj)
        self.assertEqual(judged["false_alarm_defective_controls_excluded"], 1)
        self.assertEqual(judged["false_alarm_discordant_pairs"], 1)
        self.assertEqual(judged["b_false_alarms"], 1)

    def test_pool_rows_reach_adjudications_through_substrate_source(self):
        # Pool-run rows key by substrate; adjudications key by the striatum
        # dispatch the control came from.
        from caplab.advisory.adjudication import (Adjudications,
                                                  build_adjudication)
        dispatch = "e" * 64
        rows_a = [{**row("qs-x:op:1", True, alarm=False),
                   "substrate_id": "qs-x"}]
        rows_b = [{**row("qs-x:op:1", True, alarm=True),
                   "substrate_id": "qs-x"}]
        adj = Adjudications([build_adjudication(
            dispatch_id=dispatch, disposition="defective", basis="audited",
            adjudicated_by="principal:test",
            as_of="2026-08-17T00:00:00+00:00")])
        judged = paired_comparison(
            write_run(self.root, "a", rows_a),
            write_run(self.root, "b", rows_b),
            adjudications=adj, substrate_sources={"qs-x": dispatch})
        self.assertEqual(judged["false_alarm_defective_controls_excluded"], 1)
        self.assertEqual(judged["b_false_alarms"], 0)
