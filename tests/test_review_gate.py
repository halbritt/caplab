import json
import os
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")


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
        self.assertTrue(ok["ok"])
        bad = review_gate.conformance({"verdict": "reject", "findings": [{"rationale": "looks wrong"}]})
        self.assertFalse(bad["ok"])
        self.assertFalse(review_gate.conformance(None)["ok"])
        self.assertTrue(review_gate.conformance({"verdict": "accept", "findings": []})["ok"])


if __name__ == "__main__":
    unittest.main()
