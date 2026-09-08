import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from caplab.code_agreement import build_code_agreement_report


def document(pairs):
    return {
        "schema_version": "caplab-code-agreement-input/1",
        "coder_ids": ["a", "b"], "worlds": {"w": ["C1"]},
        "slots": [{"slot": str(i), "world": "w"} for i in range(len(pairs))],
        "judgments": [
            {"slot": str(i), "coder_id": coder, "code_id": "C1", "value": value}
            for i, pair in enumerate(pairs) for coder, value in zip(("a", "b"), pair)
        ],
    }


class CodeAgreementTest(unittest.TestCase):
    def test_known_joint_table_uses_separate_coder_marginals(self):
        source = document([(False, False)] * 3 + [(False, True)] + [(True, True)] * 2)
        row = build_code_agreement_report(source)["codes"][0]
        self.assertEqual(row["joint_counts"], {"00": 3, "01": 1, "10": 0, "11": 2})
        self.assertAlmostEqual(row["observed_agreement"], 5 / 6)
        self.assertEqual(row["chance_agreement"], 0.5)
        self.assertAlmostEqual(row["kappa"], 2 / 3)
        self.assertEqual(row["complete_pairs"], 6)

    def test_missing_and_explicitly_unavailable_are_distinct(self):
        source = document([(False, False), (True, None), (True, False)])
        source["judgments"] = [r for r in source["judgments"]
                               if not (r["slot"] == "2" and r["coder_id"] == "a")]
        row = build_code_agreement_report(source)["codes"][0]
        self.assertEqual(row["expected_pairs"], 3)
        self.assertEqual(row["complete_pairs"], 1)
        self.assertEqual(row["incomplete_pairs"], 2)
        self.assertEqual(row["missing_judgments"], {"a": 1, "b": 0})
        self.assertEqual(row["unavailable_judgments"], {"a": 0, "b": 1})
        self.assertIsNone(row["kappa"])

    def test_constant_agreement_is_undefined_not_perfect_kappa(self):
        for value in (False, True):
            row = build_code_agreement_report(document([(value, value)] * 4))["codes"][0]
            self.assertEqual(row["observed_agreement"], 1.0)
            self.assertEqual(row["chance_agreement"], 1.0)
            self.assertIsNone(row["kappa"])
            self.assertEqual(row["kappa_unavailable_reason"], "chance-agreement-is-one")

    def test_opposite_labels_can_have_negative_agreement_beyond_chance(self):
        row = build_code_agreement_report(document([(False, True), (True, False)]))["codes"][0]
        self.assertEqual(row["kappa"], -1.0)

    def test_world_code_identity_is_not_pooled(self):
        source = document([(False, False), (True, True)])
        source["worlds"]["different"] = ["C1", "C2"]
        source["slots"].append({"slot": "other", "world": "different"})
        source["judgments"] += [
            {"slot": "other", "coder_id": coder, "code_id": "C1", "value": value}
            for coder, value in (("a", False), ("b", True))]
        rows = {(r["world"], r["code_id"]): r
                for r in build_code_agreement_report(source)["codes"]}
        self.assertEqual(rows[("w", "C1")]["kappa"], 1.0)
        self.assertEqual(rows[("different", "C1")]["kappa"], 0.0)
        self.assertEqual(rows[("different", "C2")]["expected_pairs"], 1)
        self.assertEqual(rows[("different", "C2")]["complete_pairs"], 0)

    def test_no_observed_pairs_keeps_all_expected_codes(self):
        source = document([])
        source["worlds"]["unlaunched"] = ["C1"]
        rows = build_code_agreement_report(source)["codes"]
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row["expected_pairs"], 0)
            self.assertIsNone(row["observed_agreement"])
            self.assertIsNone(row["chance_agreement"])
            self.assertIsNone(row["kappa"])
            self.assertEqual(row["kappa_unavailable_reason"], "no-complete-pairs")

    def test_identical_wrong_coders_do_not_establish_accuracy(self):
        truth = [True, False, True, False]
        wrong = [not x for x in truth]
        report = build_code_agreement_report(document(list(zip(wrong, wrong))))
        self.assertEqual(report["codes"][0]["kappa"], 1.0)
        self.assertNotIn("passed", report)
        self.assertIn("does not establish accuracy", report["interpretation"])

    def test_swapping_coders_and_record_order_preserves_kappa(self):
        source = document([(False, False), (False, True), (True, True)])
        original = copy.deepcopy(source)
        report = build_code_agreement_report(source)
        self.assertEqual(source, original)
        source["judgments"].reverse()
        source["slots"].reverse()
        self.assertEqual(build_code_agreement_report(source), report)
        source["coder_ids"].reverse()
        swapped = build_code_agreement_report(source)["codes"][0]
        self.assertEqual(swapped["kappa"], report["codes"][0]["kappa"])
        self.assertEqual(swapped["joint_counts"]["10"], report["codes"][0]["joint_counts"]["01"])

    def test_duplicate_assignments_or_judgments_fail(self):
        for field in ("slots", "judgments"):
            source = document([(False, True)])
            source[field].append(copy.deepcopy(source[field][0]))
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "duplicate"):
                build_code_agreement_report(source)

    def test_outside_population_and_non_boolean_values_fail(self):
        for field, value in [("coder_id", "third"), ("slot", "extra"),
                             ("code_id", "extra"), ("value", 1),
                             ("value", "false"), ("value", {})]:
            source = document([(False, True)])
            source["judgments"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                build_code_agreement_report(source)

    def test_invalid_contracts_fail(self):
        mutations = [lambda d: d.update(schema_version="unknown"),
                     lambda d: d.update(coder_ids=["a", "a"]),
                     lambda d: d.update(coder_ids=["a", "b", "c"]),
                     lambda d: d.update(worlds={"w": ["C1", "C1"]}),
                     lambda d: d.update(worlds={"w": []}),
                     lambda d: d.update(unexpected=True),
                     lambda d: d["slots"][0].update(world="absent"),
                     lambda d: d["judgments"][0].pop("value")]
        for mutate in mutations:
            source = document([(False, True)])
            mutate(source)
            with self.subTest(source=source), self.assertRaises(ValueError):
                build_code_agreement_report(source)


class AgreementCLITest(unittest.TestCase):
    def invoke(self, path):
        return subprocess.run([sys.executable, "scripts/code_agreement.py", str(path)],
                              env={**os.environ, "PYTHONPATH": "src"},
                              capture_output=True, text=True, check=False)

    def test_cli_reads_without_modifying_input_and_names_original_hash(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "judgments.json"
            data = json.dumps(document([(False, False), (True, True)])).encode()
            path.write_bytes(data)
            result = self.invoke(path)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["input_sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(report["codes"][0]["kappa"], 1.0)
            self.assertEqual(path.read_bytes(), data)

    def test_cli_rejects_ambiguous_json_without_a_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "judgments.json"
            valid = json.dumps(document([(False, True)]))
            for bad in (valid.replace('"value": false', '"value": true, "value": false'),
                        valid.replace('"value": false', '"value": NaN')):
                path.write_text(bad)
                result = self.invoke(path)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertEqual(path.read_text(), bad)


if __name__ == "__main__":
    unittest.main()
