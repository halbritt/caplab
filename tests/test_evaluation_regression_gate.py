from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "doctrine" / "tools" / "evaluation_regression_gate.py"


def load_gate_module():
    spec = importlib.util.spec_from_file_location("evaluation_regression_gate", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {TOOL}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvaluationRegressionGateTest(unittest.TestCase):
    def test_equal_totals_do_not_hide_removed_case_identity(self) -> None:
        gate = load_gate_module()
        baseline = {
            "schema_version": "books-evaluation-snapshot/1",
            "corpus_identity": "corpus-a",
            "suites": {
                "canary": {
                    "case_ids": ["authority-present", "authority-withdrawn"],
                    "kind_counts": {"authority": 2},
                    "scores": {"contract_pass_rate": {"count": 2, "value": 1.0}},
                    "errors": [],
                }
            },
        }
        candidate = copy.deepcopy(baseline)
        candidate["suites"]["canary"]["case_ids"] = [
            "authority-present",
            "replacement-case",
        ]

        violations = gate.compare_snapshots(
            candidate,
            baseline,
            {
                "schema_version": "books-evaluation-gate-config/1",
                "score_rules": {
                    "contract_pass_rate": {
                        "absolute_floor": 1.0,
                        "baseline_tolerance": 0.0,
                    }
                },
            },
        )

        self.assertIn("canary: removed case IDs: authority-withdrawn", violations)

    def test_run_errors_and_score_regressions_fail_closed(self) -> None:
        gate = load_gate_module()
        baseline = {
            "schema_version": "books-evaluation-snapshot/1",
            "corpus_identity": "corpus-a",
            "suites": {
                "canary": {
                    "case_ids": ["one", "two"],
                    "kind_counts": {"authority": 2},
                    "scores": {"contract_pass_rate": {"count": 2, "value": 1.0}},
                    "errors": [],
                }
            },
        }
        candidate = copy.deepcopy(baseline)
        candidate["suites"]["canary"]["errors"] = ["fixture missing"]
        candidate["suites"]["canary"]["scores"]["contract_pass_rate"] = {
            "count": 2,
            "value": 0.5,
        }
        config = {
            "schema_version": "books-evaluation-gate-config/1",
            "score_rules": {
                "contract_pass_rate": {
                    "absolute_floor": 0.75,
                    "baseline_tolerance": 0.25,
                }
            },
        }

        violations = gate.compare_snapshots(candidate, baseline, config)

        self.assertTrue(any("run error: fixture missing" in item for item in violations))
        self.assertTrue(any("below floor" in item for item in violations))
        self.assertTrue(any("beyond tolerance" in item for item in violations))

    def test_suite_kind_and_corpus_composition_cannot_shrink(self) -> None:
        gate = load_gate_module()
        baseline = {
            "schema_version": "books-evaluation-snapshot/1",
            "corpus_identity": "corpus-a",
            "suites": {
                "canary": {
                    "case_ids": ["one", "two"],
                    "kind_counts": {"authority": 2},
                    "scores": {},
                    "errors": [],
                },
                "hard-cases": {
                    "case_ids": ["hard-one"],
                    "kind_counts": {"injection": 1},
                    "scores": {},
                    "errors": [],
                },
            },
        }
        candidate = copy.deepcopy(baseline)
        candidate["corpus_identity"] = "corpus-b"
        candidate["suites"].pop("hard-cases")
        candidate["suites"]["canary"]["kind_counts"]["authority"] = 1

        violations = gate.compare_snapshots(
            candidate,
            baseline,
            {
                "schema_version": "books-evaluation-gate-config/1",
                "score_rules": {},
            },
        )

        self.assertIn("corpus identity differs from baseline", violations)
        self.assertIn("missing suite: hard-cases", violations)
        self.assertIn("canary: authority coverage shrank from 2 to 1", violations)

    def test_single_case_quantization_at_tolerance_boundary_is_allowed(self) -> None:
        gate = load_gate_module()
        baseline = {
            "schema_version": "books-evaluation-snapshot/1",
            "corpus_identity": "corpus-a",
            "suites": {
                "queue": {
                    "case_ids": ["one", "two", "three", "four"],
                    "kind_counts": {"coverage": 4},
                    "scores": {"queue_coverage": {"count": 4, "value": 1.0}},
                    "errors": [],
                }
            },
        }
        candidate = copy.deepcopy(baseline)
        candidate["suites"]["queue"]["scores"]["queue_coverage"] = {
            "count": 4,
            "value": 0.75,
        }

        violations = gate.compare_snapshots(
            candidate,
            baseline,
            {
                "schema_version": "books-evaluation-gate-config/1",
                "score_rules": {
                    "queue_coverage": {
                        "absolute_floor": 0.75,
                        "baseline_tolerance": 0.25,
                    }
                },
            },
        )

        self.assertEqual([], violations)

    def test_repository_snapshot_covers_each_owned_evaluation_family(self) -> None:
        gate = load_gate_module()

        snapshot = gate.build_snapshot(ROOT)

        self.assertEqual(
            ["canaries", "entailment-queue", "robustness", "skill-a-b"],
            sorted(snapshot["suites"]),
        )
        for suite in snapshot["suites"].values():
            self.assertTrue(suite["case_ids"])
            self.assertEqual([], suite["errors"])

    def test_cli_has_no_automatic_baseline_update_command(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("snapshot", completed.stdout)
        self.assertNotIn("update-baseline", completed.stdout)

    def test_committed_baseline_matches_repository_and_passes_cli(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "check", "--root", str(ROOT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("evaluation regression gate passed", completed.stdout)

    def test_committed_snapshot_and_config_satisfy_portable_schemas(self) -> None:
        snapshot_schema = json.loads(
            (ROOT / "doctrine/evaluations/snapshot.schema.json").read_text()
        )
        config_schema = json.loads(
            (ROOT / "doctrine/evaluations/regression-gate.schema.json").read_text()
        )

        jsonschema.Draft202012Validator(snapshot_schema).validate(
            json.loads(
                (ROOT / "doctrine/evaluations/baselines/repository.json").read_text()
            )
        )
        jsonschema.Draft202012Validator(config_schema).validate(
            json.loads((ROOT / "doctrine/evaluations/regression-gate.json").read_text())
        )


if __name__ == "__main__":
    unittest.main()
