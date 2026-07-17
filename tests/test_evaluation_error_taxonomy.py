from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "doctrine" / "tools"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvaluationErrorTaxonomyTest(unittest.TestCase):
    def test_registry_is_portable_and_classes_are_closed(self) -> None:
        schema = json.loads(
            (ROOT / "doctrine/evaluations/error-taxonomy.schema.json").read_text()
        )
        registry = json.loads(
            (ROOT / "doctrine/evaluations/error-taxonomy.json").read_text()
        )

        jsonschema.Draft202012Validator(schema).validate(registry)
        self.assertEqual(
            {
                "infrastructure-failure",
                "model-failure",
                "model-outcome",
                "not-evaluated",
            },
            set(registry["outcome_classes"]),
        )
        self.assertEqual(
            {"score_eligible": False, "may_supply_model_evidence": False},
            registry["outcome_classes"]["infrastructure-failure"],
        )

        remapped = json.loads(json.dumps(registry))
        remapped["scenario_exit_codes"]["2"] = "model-outcome"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(remapped)

    def test_entailment_verdicts_have_unambiguous_classes(self) -> None:
        outcomes = load_module("evaluation_outcomes", TOOLS / "evaluation_outcomes.py")

        self.assertEqual("model-outcome", outcomes.classify_entailment("supported"))
        self.assertEqual("model-failure", outcomes.classify_entailment("unparseable"))
        self.assertEqual(
            "infrastructure-failure",
            outcomes.classify_entailment("transport_error"),
        )
        self.assertEqual(
            "not-evaluated",
            outcomes.classify_entailment("insufficient_context"),
        )
        self.assertEqual(
            "infrastructure-failure",
            outcomes.classify_entailment("unknown-future-verdict"),
        )

    def test_summary_derives_class_from_verdict_not_stored_claim(self) -> None:
        evaluator = load_module(
            "entailment_eval_taxonomy",
            TOOLS / "entailment_eval.py",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            results = root / "results.jsonl"
            summary = root / "summary.md"
            results.write_text(
                json.dumps(
                    {
                        "key": "inconsistent",
                        "concept_id": "concept",
                        "source_id": "source",
                        "locator": "book/chapter.md#Heading",
                        "verdict": "transport_error",
                        "outcome_class": "model-outcome",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            self.assertEqual(0, evaluator.summarize(results, summary))
            rendered = summary.read_text(encoding="utf-8")

        self.assertIn("| infrastructure-failure | 1 |", rendered)
        self.assertIn("`transport_error`", rendered)

    def test_scenario_cli_distinguishes_fixture_and_result_failures(self) -> None:
        runner = TOOLS / "run_scenario.py"
        valid_scenario = ROOT / (
            "doctrine/evaluations/fixtures/authority-present/scenario.json"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            malformed_scenario = root / "scenario.json"
            malformed_scenario.write_text("not json\n", encoding="utf-8")
            malformed_result = root / "result.json"
            malformed_result.write_text("not json\n", encoding="utf-8")

            fixture_failure = subprocess.run(
                [sys.executable, str(runner), str(malformed_scenario), str(malformed_result)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            model_failure = subprocess.run(
                [sys.executable, str(runner), str(valid_scenario), str(malformed_result)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(2, fixture_failure.returncode)
        self.assertIn("infrastructure-failure", fixture_failure.stderr)
        self.assertEqual(1, model_failure.returncode)
        self.assertIn("model-failure", model_failure.stderr)

    def test_infrastructure_failure_is_not_in_model_score_denominator(self) -> None:
        gate = load_module(
            "evaluation_regression_gate_taxonomy",
            TOOLS / "evaluation_regression_gate.py",
        )

        infrastructure = gate._suite(
            ["one"],
            Counter({"canary": 1}),
            [],
            ["one: fixture unreadable"],
        )
        model_failure = gate._suite(
            ["one"],
            Counter({"canary": 1}),
            ["one: output invalid"],
            [],
        )

        self.assertEqual(
            {"count": 0, "value": 0.0},
            infrastructure["scores"]["contract_pass_rate"],
        )
        self.assertEqual(1, infrastructure["outcome_counts"]["infrastructure_failure"])
        self.assertEqual(
            {"count": 1, "value": 0.0},
            model_failure["scores"]["contract_pass_rate"],
        )
        self.assertEqual(1, model_failure["outcome_counts"]["model_failure"])

    def test_robustness_replay_preserves_child_infrastructure_failure(self) -> None:
        runner = load_module(
            "run_robustness_case_taxonomy",
            TOOLS / "run_robustness_case.py",
        )
        case_path = ROOT / (
            "doctrine/evaluations/robustness/cases/authority-withdrawal.json"
        )
        child = subprocess.CompletedProcess(
            args=["run_scenario.py"],
            returncode=2,
            stdout="",
            stderr="infrastructure-failure: fixture unreadable",
        )

        with patch.object(runner.subprocess, "run", return_value=child):
            with self.assertRaisesRegex(
                runner.InfrastructureError,
                "scenario_runner_infrastructure_failure:clean",
            ):
                runner.run_case(case_path)


if __name__ == "__main__":
    unittest.main()
