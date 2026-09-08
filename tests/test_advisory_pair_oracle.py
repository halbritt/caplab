"""Counterexamples to treating marker checks as proof of a defective pair."""
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from caplab.advisory import calibrate, operators, pool_runner
from caplab.advisory.instrument_defects import Injection


TEST_BODY = """from support import check

def verify(records):
    for record in records:
        check(record)
    assert len(records) > 0
"""
SUPPORT = """import json
from pathlib import Path
from jsonschema import validate

def check(record):
    validate(record, json.loads(Path('record.schema.json').read_text()))
"""
SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema",
          "type": "object", "properties": {"id": {"type": "integer"}},
          "required": ["id"], "additionalProperties": False}
FILES = {"README.md": "# Record checks\n", "test_records.py": TEST_BODY,
         "support.py": SUPPORT, "record.schema.json": json.dumps(SCHEMA)}
BODY = json.dumps({"files": FILES})
RESPONSE = {"doc": {"verdict": "accept", "findings": []}, "exit_code": 0,
            "timed_out": False, "raw_head": "", "seconds": 0,
            "transport": "stdin", "prompt_bytes": 10}
CASE = {"substrate_id": "constructed-delegated-validation", "seed": 0,
        "operator": "unearned_verification_claim", "source": {"kind": "repo-doc"}}


class PairOracleTest(unittest.TestCase):
    def test_gate_requires_explicit_opposing_results_and_checkability(self):
        injection = Injection("fixture", "major", "test", "fixture", "mutant", checkable=True)
        for mutant, control, valid in ((True, False, True), (None, False, False),
                                       (True, None, False), (False, False, False),
                                       (True, True, False), (1, 0, False)):
            with self.subTest(mutant=mutant, control=control), \
                    mock.patch.object(operators, "check_present", side_effect=[mutant, control]):
                self.assertEqual(operators.pair_gate_error(injection, "control") is None, valid)
        injection.checkable = False
        with mock.patch.object(operators, "check_present") as checker:
            self.assertIn("oracle unverified", operators.pair_gate_error(injection, "control"))
        checker.assert_not_called()

    def test_delegated_validation_is_real_despite_absent_words_in_test(self):
        # The independent execution checks the fixture's behavior, not the
        # injection's assertion about it. These are authored local files.
        with tempfile.TemporaryDirectory() as root:
            for name, body in FILES.items():
                Path(root, name).write_text(body)
            for record, valid in (({"id": 1}, True), ({"id": "invalid"}, False)):
                result = subprocess.run(
                    [sys.executable, "-c", f"from test_records import verify; verify([{record!r}])"],
                    cwd=root, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode == 0, valid, result.stderr)
                if not valid:
                    self.assertIn("ValidationError", result.stderr)
        self.assertIsNone(operators._SCHEMA_EVIDENCE.search(TEST_BODY))
        injection = operators.BY_NAME[CASE["operator"]](BODY, random.Random(0))
        # Characterize the preserved historical heuristic: it calls this
        # true even though the added documentation describes actual behavior.
        self.assertTrue(operators.check_present(injection, injection.body))
        self.assertFalse(operators.check_present(injection, BODY))

    def test_pool_does_not_send_an_unproved_defect_to_a_reviewer(self):
        with mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "iso-v1"), \
                mock.patch.object(pool_runner, "invoke", side_effect=lambda *a, **k: dict(RESPONSE)) as invoke:
            row = pool_runner.measure_case(CASE, BODY, {}, timeout=20)
        invoke.assert_not_called()
        self.assertFalse(row["usable"])
        self.assertIn("oracle unverified", row["error"])
        self.assertNotIn("caught", row)

    def test_calibration_cannot_blame_a_reference_for_the_unproved_defect(self):
        reviewer = mock.Mock()
        row = calibrate.calibrate_case(CASE, BODY, reviewer=reviewer)
        reviewer.assert_not_called()
        self.assertEqual(row["status"], "injection-failed-gate")
        self.assertNotIn("difficulty_flag", row)

    def test_unknown_presence_checker_prevents_both_execution_paths(self):
        injection = Injection("unknown-fixture", "major", "test", "fixture",
                              "mutant", checkable=True)
        case = {**CASE, "operator": "unknown-fixture"}
        with mock.patch.dict(operators.BY_NAME, {"unknown-fixture": lambda *a: injection}), \
                mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "iso-v1"), \
                mock.patch.object(pool_runner, "invoke", side_effect=lambda *a, **k: dict(RESPONSE)) as invoke:
            row = pool_runner.measure_case(case, "control", {}, timeout=20)
            materialized = calibrate.materialize_case(case, "control")
        invoke.assert_not_called()
        self.assertFalse(row["usable"])
        self.assertIn("oracle unverified", row["error"])
        self.assertIsNone(materialized)

    def test_unverified_cells_stay_in_planned_population(self):
        with tempfile.TemporaryDirectory() as root, \
                mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "iso-v1"), \
                mock.patch.object(pool_runner, "load_declaration", return_value={"adapter": {}}), \
                mock.patch.object(pool_runner.SubstrateRegistry, "read", return_value=[]), \
                mock.patch.object(pool_runner, "select_cases", return_value=([CASE], "breadth")), \
                mock.patch.object(calibrate, "load_substrate_body", return_value=BODY), \
                mock.patch.object(pool_runner, "invoke", side_effect=lambda *a, **k: dict(RESPONSE)) as invoke:
            summary = pool_runner.run_pool(backend="constructed", backends_root="unused",
                registry_path="unused", out_dir=root, sweep_seed=0, per_operator=1, timeout=20)
            rows = [json.loads(line) for line in Path(root, "results.jsonl").read_text().splitlines()]
        invoke.assert_not_called()
        self.assertEqual(len(rows), 1)
        self.assertEqual(summary["pairs_planned"], 1)
        self.assertEqual(summary["pairs_incomplete"], 1)
        self.assertEqual(summary["pairs_not_applicable"], 0)
        self.assertEqual(summary["pairs_usable"], 0)
