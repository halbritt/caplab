import json
import os
import sys
import unittest
from unittest import mock

from caplab.advisory.adjudication import Adjudications

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import review_gate


def attempt(verdict="accept", **changes):
    return {"doc": {"verdict": verdict, "findings": []}, "exit_code": 0,
            "timed_out": False, "error": None, "sandbox": "bwrap",
            "manifest_verified": True, **changes}


class GateAccountingTest(unittest.TestCase):
    def setUp(self):
        self.gate = {"cells": [{"substrate_id": "qs-a", "operator": "contradicted_clause"}],
                     "replication": {"control": 3, "mutant": 1}}
        self.row = {"substrate_id": "qs-a", "defect_class": "contradicted_clause",
                    "dispatch_id": "qs-a:contradicted_clause:1", "usable": True,
                    "environment": "tree-v1", "false_alarm": False, "caught": True,
                    "control_attempts": [attempt("reject"), attempt(), attempt()],
                    "mutant_attempts": [attempt("reject")]}
        self.adj = Adjudications([{"dispatch_id": "qs-a", "disposition": "sound"}])

    def summarize(self, rows):
        return review_gate.summarize_cells(self.gate, rows, self.adj, {})

    def test_counts_individual_controls_not_majority(self):
        result = self.summarize([self.row])
        self.assertEqual(result["controls_by_disposition"]["sound"],
                         {"expected": 3, "observed": 3, "refused": 1, "unavailable": 0})
        self.assertEqual(result["cells_scorable"], 1)
        self.assertEqual(result["missed"], 0)

    def test_failed_mutant_keeps_control_observations_and_is_not_inapplicable(self):
        self.row.update(usable=False, error="no parseable review on mutant arm",
                        mutant_attempts=[attempt(doc=None, timed_out=True, exit_code=None)])
        result = self.summarize([self.row])
        self.assertEqual(result["cells_incomplete"], 1)
        self.assertEqual(result["cells_not_applicable"], 0)
        self.assertEqual(result["cells_scorable"], 0)
        self.assertEqual(result["controls_by_disposition"]["sound"]["refused"], 1)

    def test_missing_rows_and_operator_inapplicability_are_distinct(self):
        self.assertEqual(self.summarize([])["cells_missing"], 1)
        self.assertEqual(self.summarize([])["controls_by_disposition"]["sound"],
                         {"expected": 3, "observed": 0, "refused": 0, "unavailable": 3})
        row = {**self.row, "usable": False, "error": "not applicable: no clause"}
        row.pop("control_attempts")
        row.pop("mutant_attempts")
        result = self.summarize([row])
        self.assertEqual(result["cells_not_applicable"], 1)
        self.assertEqual(result["cells_incomplete"], 0)
        row["error"] = "materialization failed: missing object"
        self.assertEqual(self.summarize([row])["cells_incomplete"], 1)

    def test_unknown_control_is_not_called_sound(self):
        self.adj = Adjudications()
        result = self.summarize([self.row])
        self.assertEqual(result["controls_by_disposition"]["sound"]["observed"], 0)
        self.assertEqual(result["controls_by_disposition"]["unadjudicated"]["refused"], 1)

    def test_failed_invalid_or_uncontained_replicate_is_unavailable(self):
        for changes in ({"exit_code": 1}, {"timed_out": True}, {"error": "transport"},
                        {"manifest_verified": False}, {"sandbox": "none"},
                        {"doc": {"verdict": "maybe"}}, {"doc": {"verdict": []}}):
            with self.subTest(changes=changes):
                self.row["control_attempts"] = [attempt(**changes), attempt(), attempt()]
                result = self.summarize([self.row])
                self.assertEqual(result["cells_incomplete"], 1)
                self.assertEqual(result["controls_by_disposition"]["sound"]["unavailable"], 1)

    def test_old_rows_cannot_supply_unrecorded_execution_evidence(self):
        self.row.pop("control_attempts")
        result = self.summarize([self.row])
        self.assertEqual(result["cells_incomplete"], 1)
        self.assertEqual(result["controls_by_disposition"]["sound"]["unavailable"], 3)

    def test_duplicate_unexpected_and_wrong_environment_rows_are_rejected(self):
        for rows in ([self.row, self.row], [{**self.row, "substrate_id": "other"}],
                     [{**self.row, "environment": "iso-v1"}],
                     [{**self.row, "control_attempts": [attempt()] * 4}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.summarize(rows)

    def test_cli_reports_aborted_pool_without_running_natural_cases(self):
        import tempfile
        gate = review_gate.load_gate()
        gate["cells"] = self.gate["cells"]

        def aborted_pool(**kwargs):
            with open(os.path.join(kwargs["out_dir"], "results.jsonl"), "w") as f:
                f.write("")
            return {"aborted": "empty lanes", "environment": "tree-v1"}

        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "gate")
            with mock.patch.object(sys, "argv", ["review_gate", "--run", "fixture", "--out", out]), \
                    mock.patch.object(review_gate, "load_gate", return_value=gate), \
                    mock.patch.object(review_gate.pool_runner, "sandbox_available", return_value=True), \
                    mock.patch.object(review_gate.pool_runner, "tree_mode", return_value=True), \
                    mock.patch.object(review_gate.pool_runner, "run_pool", side_effect=aborted_pool), \
                    mock.patch.object(review_gate.pool_runner, "load_declaration", return_value={"adapter": {}}), \
                    mock.patch.object(review_gate, "run_natural_case") as natural, \
                    mock.patch("builtins.print"):
                self.assertEqual(review_gate.main(), 0)
                natural.assert_not_called()
                with open(os.path.join(out, "gate-result.json")) as f:
                    report = json.load(f)
                self.assertEqual(report["record"], "caplab-review-admission-gate-result/3")
                self.assertEqual(report["conformance_validation"], "review-gate-conformance/2")
                self.assertEqual(report["cells_missing"], 1)
                self.assertEqual(report["natural_cases"][0]["unavailable"], 3)
                self.assertEqual(report["natural_cases"][0]["expected_replicates"], 3)
                self.assertEqual(report["natural_cases"][0]["unattempted_replicates"], 3)
                self.assertIsNone(report["natural_cases"][0]["conforming"])
                self.assertEqual(report["natural_cases"][0]["mechanical_checks_passed"], 0)
                self.assertEqual(report["natural_cases"][0]["conformance_unverified"], 0)
                self.assertEqual(report["pool_aborted"], "empty lanes")
                with self.assertRaises(FileExistsError):
                    review_gate.main()


class NaturalEvidenceTest(unittest.TestCase):
    def test_rationale_words_cannot_establish_verdict_discipline(self):
        for rationale in ("No harm exists. The result is correct.",
                          "D0003 is not violated.",
                          "This deletes the customer's only persisted copy."):
            with self.subTest(rationale=rationale):
                check = review_gate.conformance({"verdict": "reject", "findings": [
                    {"element_anchor": "result_tree_hash", "rationale": rationale}]})
                self.assertIsNone(check["ok"])
                self.assertTrue(check["mechanical_checks_passed"])
                self.assertEqual(check["status"], "unverified")
                self.assertEqual(check["rationale_cues_present"], "harm" in rationale or "D0003" in rationale)

    def test_missing_rationale_fails_mechanical_checks(self):
        for finding in ({"element_anchor": "result_tree_hash"},
                        {"element_anchor": "result_tree_hash", "rationale": "   "},
                        {"element_anchor": "result_tree_hash", "text": "harm"}):
            with self.subTest(finding=finding):
                check = review_gate.conformance({"verdict": "reject", "findings": [finding]})
                self.assertFalse(check["mechanical_checks_passed"])
                self.assertIs(check["ok"], False)

    def test_natural_case_reports_mentions_without_semantic_conformance(self):
        import tempfile
        nc = review_gate.load_gate()["natural_cases"][0]
        anchors = ["result_tree_hash_backup", "unrelated_result_tree_hash", "`result_tree_hash`"]
        responses = [
            {"verdict": "reject", "findings": [{"element_anchor": anchor,
                "rationale": "No harm exists. The result is correct."}]} for anchor in anchors]
        runs = [{**attempt(doc=doc), "seconds": 1} for doc in responses]
        with tempfile.TemporaryDirectory() as out, \
                mock.patch.object(review_gate.M, "materialize_case", return_value={"digest": "d"}), \
                mock.patch.object(review_gate.M, "store_object", return_value=b"{}"), \
                mock.patch.object(review_gate, "render_preamble_v3", return_value=""), \
                mock.patch.object(review_gate.M, "verify_manifest", return_value=True), \
                mock.patch.object(review_gate.pool_runner, "invoke", side_effect=runs):
            result = review_gate.run_natural_case(nc, {}, out, 10, 3)
        self.assertEqual(result["anchor_matching"], "normalized-anchor-exact/1")
        self.assertEqual(result["refused_with_exact_anchor_mention"], 1)
        self.assertIsNone(result["conforming"])
        self.assertEqual(result["mechanical_checks_passed"], 3)
        self.assertEqual(result["conformance_unverified"], 3)
        self.assertEqual([r["doc"] for r in result["replicates"]], responses)
        self.assertEqual([r["exact_anchor_mention"] for r in result["replicates"]], [False, False, True])

    def test_malformed_findings_do_not_conform_or_crash(self):
        for doc in ([], "accept", {"verdict": []},
                    {"verdict": "accept", "findings": ["harm"]},
                    {"verdict": "accept", "findings": {}},
                    {"verdict": "reject", "findings": [{"element_anchor": 1, "rationale": "harm"}]},
                    {"verdict": "reject", "findings": [{"element_anchor": " ", "rationale": "harm"}]},
                    {"verdict": "reject", "findings": [{"element_anchor": "x", "rationale": 2}]}):
            with self.subTest(doc=doc):
                self.assertFalse(review_gate.conformance(doc)["ok"])

    def test_failed_execution_cannot_supply_a_natural_case_hit(self):
        import tempfile
        nc = review_gate.load_gate()["natural_cases"][0]
        doc = {"verdict": "reject", "findings": [
            {"element_anchor": "result_tree_hash", "rationale": "violates clause"}]}
        runs = [{**attempt(doc=doc, exit_code=1), "seconds": 1},
                {**attempt(doc=doc), "seconds": 1},
                {**attempt(doc=doc), "seconds": 1}]
        with tempfile.TemporaryDirectory() as out, \
                mock.patch.object(review_gate.M, "materialize_case", return_value={"digest": "d"}), \
                mock.patch.object(review_gate.M, "store_object", return_value=b"{}"), \
                mock.patch.object(review_gate, "render_preamble_v3", return_value=""), \
                mock.patch.object(review_gate.M, "verify_manifest", return_value=True), \
                mock.patch.object(review_gate.pool_runner, "invoke", side_effect=runs):
            result = review_gate.run_natural_case(nc, {}, out, 10, 3)
        self.assertEqual(result["refused_with_exact_anchor_mention"], 2)
        self.assertIsNone(result["conforming"])
        self.assertEqual(result["mechanical_checks_passed"], 2)
        self.assertEqual(result["conformance_unverified"], 2)
        self.assertEqual(result["conformance_failed_mechanical"], 0)
        self.assertEqual(result["unavailable"], 1)
        self.assertEqual(len(result["replicates"]), 3)
        self.assertEqual(result["replicates"][0]["doc"], doc)


class GateSpecTest(unittest.TestCase):
    def test_gate_spec_is_the_five_analog_operators_plus_one_natural_case(self):
        from caplab.advisory.operators import QUALIFICATION_OPERATORS
        with open(os.path.join(ROOT, "advisory", "gate", "review-gate-20260819.json")) as f:
            gate = json.load(f)
        self.assertEqual(gate["selection"], "admission-gate")
        self.assertTrue({c["operator"] for c in gate["cells"]} <= set(QUALIFICATION_OPERATORS))
        self.assertEqual(len(gate["cells"]), 16)
        self.assertEqual([n["id"] for n in gate["natural_cases"]], ["cancellation-320479-empty-patch"])
        self.assertEqual(gate["natural_cases"][0]["perturbation"], "none; verbatim")
        rep = gate["replication"]
        self.assertEqual(16 * (rep["control"] + rep["mutant"]) + rep["natural_case"], 67)

    def test_admission_gate_runs_are_never_claims(self):
        import tempfile
        from caplab.advisory import scoring
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "summary.json"), "w") as f:
                json.dump({"case_selection": "admission-gate"}, f)
            self.assertTrue(scoring.outcome_selected(d))

    def test_conformance_check(self):
        import sys
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import review_gate
        ok = review_gate.conformance({"verdict": "needs_revision", "findings": [
            {"element_anchor": "result_tree_hash", "rationale": "Falsification of clause delivery-is-current-product and D0003.C6"}]})
        self.assertTrue(ok["mechanical_checks_passed"])
        self.assertIsNone(ok["ok"])
        bad = review_gate.conformance({"verdict": "reject", "findings": [{"rationale": "looks wrong"}]})
        self.assertFalse(bad["ok"])
        self.assertFalse(review_gate.conformance(None)["ok"])
        accepting = review_gate.conformance({"verdict": "accept", "findings": []})
        self.assertTrue(accepting["mechanical_checks_passed"])
        self.assertIsNone(accepting["ok"])


if __name__ == "__main__":
    unittest.main()
