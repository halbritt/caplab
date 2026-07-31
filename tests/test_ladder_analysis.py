"""Tests for deterministic ladder result recomputation."""

import unittest

from caplab.ladder_analysis import empirical_contrast, realized_arm


class LadderAnalysisTests(unittest.TestCase):
    def test_identical_first_two_stop_at_two(self) -> None:
        value = (True, False, False, True)
        realized = realized_arm(
            [
                (1, 0, value, "t1"),
                (2, 0, value, "t2"),
                (3, 0, (False, False, False, True), "t3"),
            ]
        )
        self.assertEqual(realized["k"], 2)
        self.assertEqual(realized["mean"], 1 / 3)
        self.assertEqual(realized["slots"], ["t1", "t2"])

    def test_disagreement_requires_five_and_excludes_infrastructure(self) -> None:
        zero = (False, False, False, True)
        one = (True, False, False, True)
        realized = realized_arm(
            [
                (1, 0, None, "failed-t1"),
                (1, 1, zero, "replacement-t1"),
                (2, 0, one, "t2"),
                (3, 0, zero, "t3"),
                (4, 0, one, "t4"),
                (5, 0, zero, "t5"),
            ]
        )
        self.assertEqual(realized["k"], 5)
        self.assertEqual(len(realized["slots"]), 5)
        self.assertNotIn("failed-t1", realized["slots"])

    def test_empirical_contrast_reports_delta_standard_error_and_mde(self) -> None:
        zero = realized_arm(
            [
                (1, 0, (False, False, False, True), "n1"),
                (2, 0, (False, False, False, True), "n2"),
            ]
        )
        one = realized_arm(
            [
                (1, 0, (True, False, False, True), "i1"),
                (2, 0, (True, False, False, True), "i2"),
            ]
        )
        result = empirical_contrast([zero], [one], threshold=0.35)
        self.assertAlmostEqual(result["delta"], 1 / 3)
        self.assertEqual(result["empirical_standard_error"], 0.0)
        self.assertEqual(result["empirical_mde"], 0.0)
        self.assertFalse(result["measurable"])


if __name__ == "__main__":
    unittest.main()
