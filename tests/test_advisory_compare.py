import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from caplab.advisory.compare import _binom_two_sided, paired_comparison
from caplab.advisory import pool_runner, run_spec


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
        self.assertEqual(result["comparison_basis"]["status"], "unverified-historical")
        self.assertIn("historical conditions unverified", result["reading"])

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
             "defect_class": "hash_mismatch", "calibration_profile": None,
             "caught_by": "a"}])

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


class AnnotationTest(unittest.TestCase):
    """The contrast document carries what the promotion gate and a reader need."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def _stamp(self, run_dir, **fields):
        path = os.path.join(run_dir, "summary.json")
        with open(path) as f:
            summary = json.load(f)
        summary.update(fields)
        with open(path, "w") as f:
            json.dump(summary, f)

    def test_shared_seed_is_annotated(self):
        from caplab.advisory.compare import annotate_from_summaries
        a = write_run(self.root, "a", [row("1" * 64, True)])
        b = write_run(self.root, "b", [row("1" * 64, False)])
        self._stamp(a, sweep_seed=20260820)
        self._stamp(b, sweep_seed=20260820)
        doc = annotate_from_summaries(paired_comparison(a, b), a, b)
        self.assertEqual(doc["sweep_seed"], 20260820)

    def test_mismatched_seeds_warn(self):
        from caplab.advisory.compare import annotate_from_summaries
        a = write_run(self.root, "a", [row("1" * 64, True)])
        b = write_run(self.root, "b", [row("1" * 64, False)])
        self._stamp(a, sweep_seed=20260817)
        self._stamp(b, sweep_seed=20260820)
        doc = annotate_from_summaries(paired_comparison(a, b), a, b)
        self.assertIsNone(doc["sweep_seed"])
        self.assertIn("different sweep seeds", doc["reading"])

    def test_targeted_runs_mark_the_contrast_as_outcome_selected(self):
        # The sign test is a discovery statistic; on cases chosen because
        # they separated before, the honest number is the reproduction rate.
        from caplab.advisory.compare import annotate_from_summaries
        a = write_run(self.root, "a", [row("1" * 64, True)])
        b = write_run(self.root, "b", [row("1" * 64, False)])
        for run in (a, b):
            self._stamp(run, sweep_seed=20260820,
                        case_selection="targeted-reproduction")
        doc = annotate_from_summaries(paired_comparison(a, b), a, b)
        self.assertEqual(doc["case_selection"], "targeted-reproduction")
        self.assertIn("selected on prior outcome", doc["reading"])


class ProfileAnnotationTest(unittest.TestCase):
    """Discordant cases carry their prompt profile, so the promotion gate
    can quarantine cells measured under a contaminated contract."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_discordant_case_records_the_profile(self):
        ra = row("1" * 64, True)
        ra["calibration_profile"] = "v1-changeset"
        rb = row("1" * 64, False)
        rb["calibration_profile"] = "v1-changeset"
        result = paired_comparison(write_run(self.root, "a", [ra]),
                                   write_run(self.root, "b", [rb]))
        self.assertEqual(result["discordant_cases"][0]["calibration_profile"],
                         "v1-changeset")


class FrozenComparisonTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_fixture(self, name, verdict="accept", *, selection="seeded-draw", plan_transform=None, **changes):
        out = str(Path(self.tmp.name, name))
        adapter = {"command": ["python3", "-c", "import json; print(json.dumps("
                               + repr({"verdict": verdict, "findings": []}) + "))"],
                   "prompt_mode": "stdin"}
        plan = [{"substrate_id": f"fixture-{i}", "operator": "refuted_conclusion",
                 "seed": i, "sha256": "d" * 64, "source": {"kind": "repo-doc"}}
                for i in range(3)]
        if plan_transform:
            plan = plan_transform(plan)
        options = dict(backend=name, backends_root="unused", registry_path="unused",
                       out_dir=out, sweep_seed=1, per_operator=3, timeout=20)
        with mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "iso-v1"), \
                mock.patch.object(pool_runner, "load_declaration", return_value={"adapter": adapter}), \
                mock.patch.object(pool_runner.SubstrateRegistry, "read", return_value=[]), \
                mock.patch.object(pool_runner, "select_cases", return_value=(plan, selection)), \
                mock.patch("caplab.advisory.calibrate.load_substrate_body", return_value=
                           "## Results {#el:results}\n\nEvery probe finished within budget.\n"):
            pool_runner.run_pool(**(options | changes))
        return out

    def change_rows(self, run, transform):
        path = Path(run, "results.jsonl")
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        path.write_text("".join(json.dumps(row) + "\n" for row in transform(rows)))

    def test_same_experiment_allows_distinct_subject_declarations(self):
        a, b = self.run_fixture("a"), self.run_fixture("b", "reject")
        doc = paired_comparison(a, b)
        self.assertEqual(doc["shared_cases"], 3)
        self.assertEqual(doc["a_discrimination"], 0)
        self.assertEqual(doc["b_discrimination"], 0)
        basis = doc["comparison_basis"]
        self.assertEqual(basis["record"], "caplab-paired-conditions/1")
        self.assertEqual(basis["planned_cases"], 3)
        self.assertNotEqual(basis["subjects"][0]["declaration_sha256"],
                            basis["subjects"][1]["declaration_sha256"])

    def test_changed_common_parameters_refuse_even_with_identical_case_ids(self):
        a = self.run_fixture("a")
        for i, changes in enumerate(({"timeout": 21}, {"replicates": 2},
                                      {"sweep_seed": 2}, {"workers": 2})):
            with self.subTest(changes=changes):
                b = self.run_fixture(f"b-{i}", **changes)
                with self.assertRaisesRegex(ValueError, "comparison conditions"):
                    paired_comparison(a, b)

    def test_changed_instrument_sources_refuse(self):
        a = self.run_fixture("a")
        with mock.patch.object(run_spec, "instrument_sources", return_value={"changed.py": "d" * 64}):
            b = self.run_fixture("b")
        with self.assertRaisesRegex(ValueError, "comparison conditions"):
            paired_comparison(a, b)

    def test_new_and_historical_runs_cannot_be_mixed(self):
        a = self.run_fixture("a")
        b = write_run(self.tmp.name, "legacy", [row("fixture-0:refuted_conclusion:0", False)])
        with self.assertRaisesRegex(ValueError, "frozen.*historical"):
            paired_comparison(a, b)

    def test_missing_duplicate_and_relabelled_rows_refuse(self):
        a = self.run_fixture("a")
        changes = [lambda rows: rows[:-1], lambda rows: rows + [rows[0]],
                   lambda rows: [{**rows[0], "backend_measured": "wrong"}] + rows[1:],
                   lambda rows: [{**rows[0], "run_spec_sha256": "d" * 64}] + rows[1:],
                   lambda rows: [{**rows[0], "anchor": True}] + rows[1:],
                   lambda rows: [{**rows[0], "defect_anchor": "another"}] + rows[1:]]
        for i, change in enumerate(changes):
            with self.subTest(change=i):
                b = self.run_fixture(f"b-{i}")
                self.change_rows(b, change)
                with self.assertRaises(ValueError):
                    paired_comparison(a, b)

    def test_incomplete_row_cannot_hide_behind_a_complete_summary(self):
        a, b = self.run_fixture("a"), self.run_fixture("b")
        self.change_rows(b, lambda rows: [{**rows[0], "usable": False,
                                          "error": "preparation failed"}] + rows[1:])
        with self.assertRaisesRegex(ValueError, "incomplete"):
            paired_comparison(a, b)

    def test_symmetric_inapplicability_is_reported_without_a_silent_drop(self):
        def one_inapplicable(plan):
            return [{**plan[0], "operator": "hash_mismatch"}] + plan[1:]
        a = self.run_fixture("a", plan_transform=one_inapplicable)
        b = self.run_fixture("b", plan_transform=one_inapplicable)
        doc = paired_comparison(a, b)
        self.assertEqual(doc["shared_cases"], 2)
        self.assertEqual(doc["comparison_basis"]["planned_cases"], 3)
        self.assertEqual(doc["comparison_basis"]["not_applicable_cases"], 1)

    def test_outcome_selected_runs_carry_no_discovery_statistics(self):
        for selection in ("targeted-reproduction", "admission-gate"):
            with self.subTest(selection=selection):
                a = self.run_fixture(selection + "-a", selection=selection)
                b = self.run_fixture(selection + "-b", "reject", selection=selection)
                doc = paired_comparison(a, b)
                self.assertEqual(doc["shared_cases"], 3)
                self.assertEqual(doc["case_selection"], selection)
                self.assertIsNone(doc["sign_test_p"])
                self.assertIsNone(doc["significant_at_05"])
                self.assertIsNone(doc["false_alarm_sign_test_p"])
                self.assertIsNone(doc["false_alarm_significant_at_05"])
                self.assertIn("descriptive", doc["reading"])

    def test_unknown_selection_cannot_gain_discovery_statistics(self):
        a = self.run_fixture("a", selection="future-selection")
        b = self.run_fixture("b", selection="future-selection")
        with self.assertRaisesRegex(ValueError, "unknown case selection"):
            paired_comparison(a, b)

    def test_profile_remeasurement_retains_its_exogenous_selection_label(self):
        a = self.run_fixture("a", selection="profile-remeasurement")
        b = self.run_fixture("b", selection="profile-remeasurement")
        doc = paired_comparison(a, b)
        self.assertEqual(doc["case_selection"], "profile-remeasurement")
        self.assertEqual(doc["sign_test_p"], 1)
