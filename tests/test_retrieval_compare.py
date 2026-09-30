"""Paired comparison of verified retrieval runs: alignment, exact deltas and fail-closed pins."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from caplab.retrieval import artifacts, compare
from caplab.retrieval.artifacts import ArtifactError, ArtifactIntegrityError
from caplab.retrieval.compare import compare_runs
from caplab.retrieval.report import render_markdown

from retrieval_evidence_support import CORPUS, make_spec, write_run


class CompareFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def run_dir(self, name="run", **kwargs):
        kwargs.setdefault("raw", False)
        return write_run(self.root, name, **kwargs)[0].output


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


class ArmComparisonTests(CompareFixture):
    def test_known_good_against_bad_has_exact_case_level_deltas(self):
        run = self.run_dir()
        result = compare_runs(run, run, left_arm="good", right_arm="bad")
        self.assertEqual(result["schema_version"], "caplab-retrieval-comparison/1")
        (pair,) = result["comparisons"]
        self.assertEqual(pair["arms"], {"left": "good", "right": "bad"})
        self.assertEqual(pair["pairing"]["counts"], {"planned_pairs": 6, "both_scorable": 6, "left_only_scorable": 0,
                                                     "right_only_scorable": 0, "neither_scorable": 0, "not_both_scorable": 0})
        one = pair["cutoffs"]["1"]["answerable"]["metrics"]
        self.assertEqual(one["recall"]["cases"], 2)  # cases are queries, not (query, seed) rows
        self.assertEqual(fraction(one["recall"]["left_mean"]), Fraction(3, 4))
        self.assertEqual(fraction(one["recall"]["right_mean"]), 0)
        self.assertEqual(fraction(one["recall"]["delta"]), Fraction(-3, 4))
        self.assertEqual(fraction(one["precision"]["delta"]), -1)
        self.assertEqual(fraction(one["success"]["delta"]), -1)
        self.assertEqual((one["recall"]["right_wins"], one["recall"]["left_wins"], one["recall"]["ties"]), (0, 2, 0))
        self.assertAlmostEqual(one["recall"]["sign_test_p"], 0.5)
        self.assertIsNone(one["recall"]["interval"])
        self.assertAlmostEqual(one["ndcg"]["delta"]["value"], -1.0)
        three = pair["cutoffs"]["3"]["answerable"]["metrics"]
        self.assertEqual(fraction(three["recall"]["delta"]), -1)
        self.assertEqual(fraction(three["precision"]["left_mean"]), Fraction(1, 2))
        self.assertEqual(fraction(three["precision"]["delta"]), Fraction(-1, 2))

    def test_orientation_is_right_minus_left(self):
        run = self.run_dir()
        flipped = compare_runs(run, run, left_arm="bad", right_arm="good")["comparisons"][0]
        metrics = flipped["cutoffs"]["1"]["answerable"]["metrics"]
        self.assertEqual(fraction(metrics["recall"]["delta"]), Fraction(3, 4))
        self.assertEqual((metrics["recall"]["right_wins"], metrics["recall"]["left_wins"]), (2, 0))

    def test_discordant_hits_and_control_flags_are_listed_not_just_counted(self):
        run = self.run_dir()
        pair = compare_runs(run, run, left_arm="good", right_arm="bad")["comparisons"][0]
        hits = pair["cutoffs"]["1"]["answerable"]["discordant_hits"]
        self.assertEqual((hits["left_hit_right_miss"]["count"], hits["right_hit_left_miss"]["count"],
                          hits["both_hit"], hits["both_miss"]), (4, 0, 0, 0))
        self.assertEqual(sorted((a["query_id"], a["seed"]) for a in hits["left_hit_right_miss"]["assignments"]),
                         [("q1", 0), ("q1", 1), ("q2", 0), ("q2", 1)])
        controls = pair["cutoffs"]["1"]["controls"]
        self.assertEqual(controls["false_positive"], {"both_clean": 0, "left_fp_only": 0, "right_fp_only": 2,
                                                      "both_fp": 0, "assignments": 2})
        self.assertEqual(controls["forbidden_hit"]["right_hit_only"], 2)  # the bad arm returns the forbidden note

    def test_seeds_are_averaged_inside_a_case_before_aggregating(self):
        overrides = {("mid", "q1", 1): {"ranked": ["n1"]}}  # hit on seed 1 only
        run = self.run_dir(spec=make_spec(arms=("good", "mid")), overrides=overrides)
        pair = compare_runs(run, run, left_arm="good", right_arm="mid")["comparisons"][0]
        success = pair["cutoffs"]["1"]["answerable"]["metrics"]["success"]
        self.assertEqual(success["cases"], 2)
        self.assertEqual(fraction(success["delta"]), Fraction(-1, 4))  # q1: 1/2 - 1, q2: 0
        self.assertEqual((success["right_wins"], success["left_wins"], success["ties"]), (0, 1, 1))
        hits = pair["cutoffs"]["1"]["answerable"]["discordant_hits"]
        self.assertEqual((hits["left_hit_right_miss"]["count"], hits["both_hit"]), (1, 3))

    def test_partial_failures_stay_visible_as_unpaired_and_shrink_only_the_paired_set(self):
        overrides = {("bad", "q1", 0): {"status": "timeout"}}
        run = self.run_dir(overrides=overrides)
        pair = compare_runs(run, run, left_arm="good", right_arm="bad")["comparisons"][0]
        counts = pair["pairing"]["counts"]
        self.assertEqual((counts["both_scorable"], counts["left_only_scorable"], counts["not_both_scorable"]), (5, 1, 1))
        self.assertEqual(pair["pairing"]["unpaired"], [{"query_id": "q1", "seed": 0, "left": "ok", "right": "timeout"}])
        self.assertEqual(pair["cutoffs"]["1"]["answerable"]["metrics"]["recall"]["cases"], 2)
        hits = pair["cutoffs"]["1"]["answerable"]["discordant_hits"]
        self.assertEqual(hits["left_hit_right_miss"]["count"], 3)  # the timed-out pair is not a miss
        text = render_markdown(compare_runs(run, run, left_arm="good", right_arm="bad"))
        self.assertIn("Unpaired (kept visible, never dropped)", text)

    def test_a_failing_arm_cannot_look_good_and_its_sensitivity_is_bounded_not_imputed_away(self):
        run = self.run_dir(spec=make_spec(arms=("good", "failing")))
        result = compare_runs(run, run, left_arm="good", right_arm="failing")
        pair = result["comparisons"][0]
        self.assertEqual(pair["pairing"]["counts"]["both_scorable"], 0)
        self.assertEqual(pair["pairing"]["counts"]["left_only_scorable"], 6)
        metrics = pair["cutoffs"]["3"]["answerable"]["metrics"]
        self.assertEqual(metrics["recall"]["cases"], 0)
        self.assertIsNone(metrics["recall"]["delta"]["value"])
        sensitivity = pair["cutoffs"]["3"]["answerable"]["all_roster_sensitivity"]
        self.assertEqual((sensitivity["planned_assignments"], sensitivity["unscorable"]), (4, {"left": 0, "right": 4}))
        self.assertEqual([fraction(sensitivity["right"][end]) for end in ("lower", "upper")], [0, 1])
        self.assertEqual([fraction(sensitivity["delta_bounds"][end]) for end in ("lower", "upper")], [-1, 0])
        self.assertIn("not a bound", render_markdown(result))

    def test_missingness_that_differs_across_arms_does_not_turn_the_zero_imputed_delta_into_a_bound(self):
        # Left arm "bad" has one answerable assignment unscorable; right arm "good" is complete.
        run = self.run_dir(spec=make_spec(arms=("bad", "good")), overrides={("bad", "q1", 0): {"status": "timeout"}})
        pair = compare_runs(run, run, left_arm="bad", right_arm="good")["comparisons"][0]
        sensitivity = pair["cutoffs"]["3"]["answerable"]["all_roster_sensitivity"]
        self.assertEqual(sensitivity["unscorable"], {"left": 1, "right": 0})
        self.assertEqual([fraction(sensitivity["left"][end]) for end in ("lower", "upper")], [0, Fraction(1, 4)])
        lower, upper = (fraction(sensitivity["delta_bounds"][end]) for end in ("lower", "upper"))
        scenario = fraction(sensitivity["zero_imputed_scenario_delta"])
        self.assertEqual((lower, upper, scenario), (Fraction(3, 4), Fraction(1), Fraction(1)))
        self.assertLess(lower, scenario)  # the zero-imputed delta overstates the smallest possible delta
        # The same question with the missing outcome on the right-hand arm.
        pair = compare_runs(run, run, left_arm="good", right_arm="bad")["comparisons"][0]
        sensitivity = pair["cutoffs"]["3"]["answerable"]["all_roster_sensitivity"]
        self.assertEqual([fraction(sensitivity["delta_bounds"][end]) for end in ("lower", "upper")],
                         [Fraction(-1), Fraction(-3, 4)])
        # Complete-pair conditional estimates are reported separately and do not use imputation.
        conditional = pair["cutoffs"]["3"]["answerable"]["metrics"]["recall"]
        self.assertEqual(fraction(conditional["delta"]), -1)
        self.assertEqual(pair["pairing"]["counts"]["both_scorable"], 5)

    def test_a_five_arm_run_separates_good_mid_bad_empty_and_failing_retrievers(self):
        run = self.run_dir(spec=make_spec(arms=("good", "mid", "bad", "empty", "failing")))
        deltas = {}
        for arm in ("mid", "bad", "empty", "failing"):
            pair = compare_runs(run, run, left_arm="good", right_arm=arm)["comparisons"][0]
            block = pair["cutoffs"]["3"]
            deltas[arm] = (fraction(block["answerable"]["metrics"]["recall"]["delta"]) if block["answerable"]["metrics"]["recall"]["cases"] else None,
                           block["controls"]["false_positive"], block["controls"]["forbidden_hit"])
        self.assertEqual(deltas["mid"][0], Fraction(-1, 4))          # mid finds q1 but only one of q2's two notes
        self.assertEqual(deltas["bad"][0], -1)
        self.assertEqual(deltas["empty"][0], -1)
        self.assertIsNone(deltas["failing"][0])                      # nothing scorable to compare
        self.assertEqual(deltas["mid"][1]["right_fp_only"], 2)       # mid returns an unrelated note for the control
        self.assertEqual(deltas["mid"][2]["both_clean"], 2)          # but never the forbidden note for the control
        self.assertEqual(deltas["empty"][1]["both_clean"], 2)        # an empty retriever is clean on controls, not good
        self.assertEqual(deltas["failing"][1]["assignments"], 0)     # a failing arm never counts as a clean abstention

    def test_selection_errors_are_explicit(self):
        run = self.run_dir()
        cases = [
            (dict(), "AMBIGUOUS_ARM"),                                        # same run, no selectors
            (dict(left_arm="good"), "AMBIGUOUS_ARM"),                         # one selector only
            (dict(left_arm="good", right_arm="nope"), "UNKNOWN_ARM"),
            (dict(left_arm="good", right_arm="good"), "SAME_ARM"),
        ]
        for kwargs, code in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ArtifactError) as caught:
                compare_runs(run, run, **kwargs)
            self.assertEqual(caught.exception.code, code)


class RunComparisonTests(CompareFixture):
    def test_two_single_arm_runs_compare_without_selectors(self):
        left = self.run_dir("left", spec=make_spec(experiment_id="baseline", arms=("good",)))
        right = self.run_dir("right", spec=make_spec(experiment_id="candidate", arms=("bad",)))
        result = compare_runs(left, right)
        self.assertEqual(result["compatibility"]["arm_selection"]["mode"], "single_arm_inputs")
        self.assertEqual(result["comparisons"][0]["arms"], {"left": "good", "right": "bad"})
        self.assertFalse(result["compatibility"]["pins"]["experiment_id"]["equal"])
        self.assertTrue(all(pin["equal"] for pin in result["compatibility"]["pins"].values() if pin["required"]))
        self.assertEqual([row["side"] for row in result["runs"]], ["left", "right"])
        self.assertNotEqual(result["runs"][0]["manifest_sha256"], result["runs"][1]["manifest_sha256"])

    def test_multi_arm_runs_with_identical_arm_ids_give_a_matching_arm_report(self):
        left = self.run_dir("left", spec=make_spec(experiment_id="before", arms=("good", "bad")))
        right = self.run_dir("right", spec=make_spec(experiment_id="after", arms=("good", "bad")),
                             overrides={("bad", "q1", 0): {"ranked": ["n1"]}, ("bad", "q1", 1): {"ranked": ["n1"]}})
        result = compare_runs(left, right)
        self.assertEqual(result["compatibility"]["arm_selection"], {"mode": "matching_arms", "arms": ["bad", "good"]})
        self.assertEqual([c["arms"] for c in result["comparisons"]],
                         [{"left": "bad", "right": "bad"}, {"left": "good", "right": "good"}])
        bad, good = (c["cutoffs"]["1"]["answerable"]["metrics"]["recall"] for c in result["comparisons"])
        self.assertEqual(fraction(bad["delta"]), Fraction(1, 2))   # q1 recall 0 -> 1, q2 unchanged
        self.assertEqual(fraction(good["delta"]), 0)

    def test_multi_arm_runs_with_different_arm_ids_are_ambiguous(self):
        left = self.run_dir("left", spec=make_spec(arms=("good", "bad")))
        right = self.run_dir("right", spec=make_spec(arms=("good", "mid")))
        with self.assertRaises(ArtifactError) as caught:
            compare_runs(left, right)
        self.assertEqual(caught.exception.code, "AMBIGUOUS_ARM")
        result = compare_runs(left, right, left_arm="good", right_arm="mid")
        self.assertEqual(result["comparisons"][0]["arms"], {"left": "good", "right": "mid"})

    def test_incompatible_pins_fail_closed_instead_of_dropping_pairs(self):
        base = dict(arms=("good",))
        left = self.run_dir("left", spec=make_spec(**base))
        bad_corpus = [dict(note, body=note["body"] + " edited") if note["id"] == "n4" else note for note in CORPUS]
        relabelled = make_spec(**base)
        relabelled["queries"][0]["relevant_ids"] = ["n2"]
        renamed = make_spec(**base)
        renamed["queries"][0]["text"] = "a different question"
        fewer = make_spec(arms=("good",))
        fewer["queries"].pop()
        cases = {
            "corpus": (make_spec(corpus=bad_corpus, **base), {"corpus_sha256"}),
            "labels": (relabelled, {"cases_sha256"}),
            "query text": (renamed, {"cases_sha256"}),
            "fewer queries": (fewer, {"cases_sha256"}),
            "seeds": (make_spec(seeds=(0,), **base), {"seeds"}),
            "cutoffs": (make_spec(cutoffs=(1, 2), **base), {"cutoffs"}),
            "timeout": (make_spec(timeout=9, **base), {"timeout_seconds"}),
        }
        for name, (spec, expected) in cases.items():
            with self.subTest(name):
                right = self.run_dir(f"right-{name.replace(' ', '-')}", spec=spec)
                with self.assertRaises(ArtifactError) as caught:
                    compare_runs(left, right)
                self.assertEqual(caught.exception.code, "INCOMPATIBLE_RUNS")
                self.assertTrue(expected <= set(caught.exception.detail["mismatches"]), caught.exception.detail)

    def test_unverifiable_or_unfinished_runs_are_never_compared(self):
        left = self.run_dir("left", spec=make_spec(arms=("good",)))
        right = self.run_dir("right", spec=make_spec(arms=("bad",)))
        unfinished, _ = write_run(self.root, "unfinished", spec=make_spec(arms=("bad",)), finish=False, raw=False)
        with self.assertRaises(ArtifactIntegrityError) as caught:
            compare_runs(left, unfinished.output)
        self.assertEqual(caught.exception.code, "RUN_NOT_FINISHED")
        tampered = self.root / "tampered"
        shutil.copytree(right, tampered)
        attempts = tampered / "attempts.jsonl"
        attempts.chmod(0o600)
        attempts.write_bytes(attempts.read_bytes().replace(b'"ranked_ids":["n4","n5"]', b'"ranked_ids":["n1","n5"]', 1))
        with self.assertRaises(ArtifactIntegrityError) as caught:
            compare_runs(left, tampered)
        self.assertEqual(caught.exception.code, "ATTEMPT_WITHOUT_EVIDENCE")

    def test_comparison_output_renders_with_reviewer_context_first(self):
        run = self.run_dir()
        text = render_markdown(compare_runs(run, run, left_arm="good", right_arm="bad"))
        self.assertLess(text.index("## What was compared"), text.index("## Compatibility checks"))
        self.assertLess(text.index("## Compatibility checks"), text.index("### Pairing and denominators"))
        self.assertLess(text.index("### Pairing and denominators"), text.index("### Cutoff k=1"))
        self.assertIn("right minus left", text)
        self.assertIn("No pass threshold", text)
        json.dumps(compare_runs(run, run, left_arm="good", right_arm="bad"))  # the result is plain JSON


class StatisticsTests(unittest.TestCase):
    def test_exact_sign_test(self):
        self.assertIsNone(compare._sign_test_p(0, 0))
        self.assertAlmostEqual(compare._sign_test_p(5, 0), 0.0625)
        self.assertAlmostEqual(compare._sign_test_p(3, 1), 0.625)
        self.assertAlmostEqual(compare._sign_test_p(2, 2), 1.0)
        self.assertAlmostEqual(compare._sign_test_p(0, 5), compare._sign_test_p(5, 0))

    def test_interval_needs_three_cases_and_uses_the_t_quantile(self):
        self.assertIsNone(compare._interval([1.0, 2.0])[0])
        low, high = compare._interval([1.0, 2.0, 3.0])[0]
        self.assertAlmostEqual(low, 2 - 4.303 / 3 ** 0.5, places=6)
        self.assertAlmostEqual(high, 2 + 4.303 / 3 ** 0.5, places=6)
        self.assertEqual(compare._interval([0.5, 0.5, 0.5])[0], [0.5, 0.5])

    def test_interval_never_claims_more_precision_than_a_t_quantile_allows(self):
        for cases, critical in ((3, 4.303), (31, 2.042), (32, 2.042), (41, 2.021), (200, 1.980)):
            deltas = [0.0, 1.0] * (cases // 2) + [0.0] * (cases % 2)
            low, high = compare._interval(deltas)[0]
            mean = sum(deltas) / cases
            sd = (sum((d - mean) ** 2 for d in deltas) / (cases - 1)) ** 0.5
            self.assertAlmostEqual(high - mean, critical * sd / cases ** 0.5, places=9, msg=cases)
            self.assertGreater(critical, 1.96)

    def test_float_metrics_treat_rounding_noise_as_a_tie_but_rational_metrics_do_not(self):
        noisy = compare._case_stats([("q1", 0.6309297535714574, 0.6309297535714574 + 1e-15)], exact=False)
        self.assertEqual((noisy["right_wins"], noisy["left_wins"], noisy["ties"]), (0, 0, 1))
        real = compare._case_stats([("q1", Fraction(1, 3), Fraction(1, 3) + Fraction(1, 10**15))], exact=True)
        self.assertEqual((real["right_wins"], real["ties"]), (1, 0))

    def test_means_keep_exact_numerators_and_denominators(self):
        mean = compare._mean([Fraction(1, 3), Fraction(2, 3)])
        self.assertEqual((mean["numerator"], mean["denominator"], mean["count"]), (1, 2, 2))
        empty = compare._mean([])
        self.assertEqual((empty["value"], empty["count"]), (None, 0))


if __name__ == "__main__":
    unittest.main()
