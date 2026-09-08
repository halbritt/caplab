"""Minimum covers, declared population failures and a read-only CLI boundary."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from caplab.coverage_plan import plan_shakedown_coverage


ROOT = Path(__file__).resolve().parents[1]


def document(requirements, candidates):
    return {"schema_version": "caplab-shakedown-coverage-input/1",
            "requirements": requirements, "candidates": candidates}


class CoveragePlanTests(unittest.TestCase):
    def test_greedy_largest_first_would_consume_an_extra_world(self):
        source = document(list("123456"), {
            "a": list("1234"), "b": list("125"), "c": list("346")})
        result = plan_shakedown_coverage(source)
        self.assertEqual(result["selected"], ["b", "c"])
        self.assertEqual(result["minimum_cardinality"], 2)
        self.assertEqual(result["candidate_remainder"], ["a"])
        self.assertEqual(set(result["coverage_witnesses"]), set("123456"))
        for token, names in result["coverage_witnesses"].items():
            self.assertTrue(names)
            self.assertTrue(all(token in source["candidates"][name] for name in names))

    def test_search_breaks_equal_minimum_ties_by_exact_ids(self):
        # No single candidate covers all four requirements; a+d and b+c do.
        source = document(list("1234"), {
            "d": list("34"), "c": list("24"), "b": list("13"), "a": list("12")})
        before = copy.deepcopy(source)
        result = plan_shakedown_coverage(source)
        self.assertEqual(result["selected"], ["a", "d"])
        self.assertEqual(source, before)
        reordered = document(list("4321"), {
            name: list(reversed(tokens)) for name, tokens in reversed(list(source["candidates"].items()))})
        self.assertEqual(plan_shakedown_coverage(reordered), result)

    def test_forced_candidate_preserves_tie_break_for_remaining_choice(self):
        result = plan_shakedown_coverage(document(["x", "y"], {
            "b": ["x"], "middle": ["y"], "a": ["x"]}))
        self.assertEqual(result["selected"], ["a", "middle"])

    def test_single_complete_candidate_and_twenty_four_forced_candidates(self):
        result = plan_shakedown_coverage(document(["x", "y"], {
            "partial": ["x"], "complete": ["x", "y"]}))
        self.assertEqual(result["selected"], ["complete"])
        ids = [f"id-{i:02d}" for i in range(24)]
        result = plan_shakedown_coverage(document(ids, {name: [name] for name in ids}))
        self.assertEqual(result["selected"], ids)
        self.assertEqual(result["minimum_cardinality"], 24)
        self.assertEqual(result["candidate_remainder"], [])

    def test_missing_requirement_is_not_dropped_or_called_a_seal(self):
        result = plan_shakedown_coverage(document(["x", "y"], {"only": ["x"]}))
        self.assertEqual(result["status"], "uncovered-requirements")
        self.assertEqual(result["requirements_without_candidate"], ["y"])
        self.assertIsNone(result["selected"])
        self.assertIsNone(result["candidate_remainder"])
        self.assertIsNone(result["minimum_cardinality"])
        self.assertEqual(result["coverage_witnesses"], {})
        self.assertEqual(result["basis"], "declared-metadata-only")

    def test_invalid_metadata_is_rejected_before_selection(self):
        valid = document(["x"], {"a": ["x"]})
        invalid = [None, {**valid, "unknown": True}, {**valid, "schema_version": "other"},
                   document([], {"a": ["x"]}), document(["x", "x"], {"a": ["x"]}),
                   document([True], {"a": ["x"]}), document([" "], {"a": ["x"]}),
                   document(["x"], {}), document(["x"], {str(i): ["x"] for i in range(25)}),
                   document(["x"], {" ": ["x"]}), document(["x"], {1: ["x"]}),
                   document(["x"], {"a": []}), document(["x"], {"a": ["x", "x"]}),
                   document(["x"], {"a": [1]}), document(["x"], {"a": ["other"]})]
        for source in invalid:
            with self.subTest(source=source), self.assertRaises(ValueError):
                plan_shakedown_coverage(source)

    def test_cli_reads_exact_input_and_reports_its_hash(self):
        raw = json.dumps(document(["é"], {"世界": ["é"]}), ensure_ascii=False).encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "input.json")
            path.write_bytes(raw)
            result = self.run_cli(path, directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["selected"], ["世界"])
            self.assertEqual(report["input_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_cli_rejects_ambiguous_json_and_invalid_utf8_without_output(self):
        duplicate = (b'{"schema_version":"caplab-shakedown-coverage-input/1",'
                     b'"requirements":["x"],"candidates":{"a":["x"],"a":["x"]}}')
        for raw in (duplicate, b'{"x":NaN}', b'\xff'):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as directory:
                path = Path(directory, "input.json")
                path.write_bytes(raw)
                result = self.run_cli(path, directory)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertEqual(path.read_bytes(), raw)
                self.assertEqual(list(Path(directory).iterdir()), [path])

    @staticmethod
    def run_cli(path, directory):
        return subprocess.run([sys.executable, str(ROOT / "scripts/shakedown_coverage.py"), str(path)],
                              cwd=directory, capture_output=True, text=True, check=False,
                              env={**os.environ, "PYTHONPATH": str(ROOT / "src"),
                                   "PYTHONDONTWRITEBYTECODE": "1"})


if __name__ == "__main__":
    unittest.main()
