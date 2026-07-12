from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOADER_PATH = ROOT / "doctrine" / "tools" / "build_robustness_suite.py"
RUNNER_PATH = ROOT / "doctrine" / "tools" / "run_robustness_case.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_robustness_suite", LOADER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load robustness contract module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_runner():
    spec = importlib.util.spec_from_file_location("run_robustness_case", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load robustness runner module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RobustnessContractTests(unittest.TestCase):
    def valid_case(self):
        return {
            "schema_version": "doctrine-robustness-case/1",
            "id": "authority-withdrawal-case", "status": "candidate",
            "rationale": "Exercise the existing authority canary contract.",
            "subject_adapter": "scenario-runner/2",
            "clean_seed": {"artifact_kind": "scenario", "locator": "seed.json", "scenario_version": "doctrine-scenario/2", "target_hash": "a" * 64, "container_hash": "b" * 64},
            "operator": {"id": "authority-withdrawal", "version": 1, "parameters": {}, "expected_input_validity": "valid"},
            "evidence": [], "oracles": {"clean": {}, "mutant": {}, "pair": {}},
            "comparison_projection": ["/assertions"], "expected_detection_boundary": "metamorphic",
        }

    def test_valid_operator_loads_through_the_public_contract_loader(self):
        loader = load_module()
        artifact = {
            "schema_version": "doctrine-robustness-operator/1",
            "id": "authority-withdrawal",
            "version": 1,
            "family": "authority",
            "target_artifact_kinds": ["scenario"],
            "implementation_id": "builtin/authority-withdrawal/1",
            "allowed_selectors": ["/authority/authorization_granted"],
            "preconditions": ["clean scenario grants authorization"],
            "postconditions": ["mutant scenario withdraws authorization"],
            "expected_mutant_validity": "valid",
            "detection_boundary": "metamorphic",
            "default_oracle_class": "pair-relation",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "operator.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            self.assertEqual(artifact, loader.load_artifact("operator", path))

    def test_all_laboratory_contracts_are_portable_offline_schemas(self):
        loader = load_module()
        self.assertEqual(
            {"operator", "case", "result", "human-adjudication", "skill-eval-case", "skill-eval-result"},
            set(loader.SCHEMA_PATHS),
        )
        loader.validate_schema_registry()

    def test_case_loader_rejects_malformed_and_unsupported_inputs_stably(self):
        loader = load_module()
        base = {
            "schema_version": "doctrine-robustness-case/1",
            "id": "authority-withdrawal-case",
            "status": "candidate",
            "rationale": "Exercise the existing authority canary contract.",
            "subject_adapter": "scenario-runner/2",
            "clean_seed": {
                "artifact_kind": "scenario",
                "locator": "doctrine/evaluations/fixtures/authority-present/scenario.json",
                "scenario_version": "doctrine-scenario/2",
                "target_hash": "a" * 64,
                "container_hash": "b" * 64,
            },
            "operator": {"id": "authority-withdrawal", "version": 1, "parameters": {}, "expected_input_validity": "valid"},
            "evidence": [],
            "oracles": {"clean": {}, "mutant": {}, "pair": {}},
            "comparison_projection": ["/assertions"],
            "expected_detection_boundary": "metamorphic",
        }
        variants = []
        missing = dict(base)
        missing.pop("id")
        variants.append(missing)
        unexpected = dict(base, surprise=True)
        variants.append(unexpected)
        old_version = dict(base, schema_version="doctrine-robustness-case/2")
        variants.append(old_version)
        unknown_adapter = dict(base, subject_adapter="shell/1")
        variants.append(unknown_adapter)
        old_scenario = dict(base)
        old_scenario["clean_seed"] = dict(base["clean_seed"], scenario_version="doctrine-scenario/1")
        variants.append(old_scenario)
        invalid_evidence = dict(base, evidence=[{"id": "not-a-complete-evidence-record"}])
        variants.append(invalid_evidence)

        with tempfile.TemporaryDirectory() as directory:
            for index, artifact in enumerate(variants):
                with self.subTest(index=index):
                    path = Path(directory) / f"case-{index}.json"
                    path.write_text(json.dumps(artifact), encoding="utf-8")
                    with self.assertRaisesRegex(loader.ContractError, "^schema_validation_error: case:/"):
                        loader.load_artifact("case", path)

    def test_case_resolution_rejects_unknown_operator_and_stale_seed(self):
        loader = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case_path = root / "case.json"
            case_path.write_text(json.dumps(self.valid_case()), encoding="utf-8")
            with self.assertRaisesRegex(loader.ContractError, "^unresolved_operator: authority-withdrawal/1$"):
                loader.load_case(case_path, root=root, operator_paths=[])

            operator = {
                "schema_version": "doctrine-robustness-operator/1", "id": "authority-withdrawal", "version": 1,
                "family": "authority", "target_artifact_kinds": ["scenario"], "implementation_id": "builtin/authority-withdrawal/1",
                "allowed_selectors": ["/authority/authorization_granted"], "preconditions": ["authorization present"],
                "postconditions": ["authorization absent"], "expected_mutant_validity": "valid",
                "detection_boundary": "metamorphic", "default_oracle_class": "pair-relation",
            }
            operator_path = root / "operator.json"
            operator_path.write_text(json.dumps(operator), encoding="utf-8")
            (root / "seed.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(loader.ContractError, "^stale_seed: seed.json$"):
                loader.load_case(case_path, root=root, operator_paths=[operator_path])

    def test_result_references_and_human_ownership_are_closed(self):
        loader = load_module()
        result = {
            "schema_version": "doctrine-robustness-result/1", "case_id": "missing-case", "case_hash": "a" * 64,
            "operator_id": "missing-operator", "operator_version": 1, "runner_version": "runner/1",
            "subject_adapter": "scenario-runner/2", "clean_output_hash": "b" * 64, "mutant_output_hash": "c" * 64,
            "criteria": [], "mechanical_status": "pending", "human_status": "pending",
        }
        machine_adjudication = {
            "schema_version": "doctrine-robustness-human-adjudication/1",
            "adjudications": [{
                "case_id": "case", "run_hash": "a" * 64, "clean_output_hash": "b" * 64, "mutant_output_hash": "c" * 64,
                "adjudicator": {"kind": "machine", "id": "builder"}, "adjudicated_at": "2026-07-11T00:00:00Z",
                "evidence_reviewed": ["run"], "disposition": "indeterminate", "rationale": "Machine attempted write.", "uncertainty": "unknown",
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result_path = root / "result.json"
            result_path.write_text(json.dumps(result), encoding="utf-8")
            with self.assertRaisesRegex(loader.ContractError, "^unresolved_case: missing-case$"):
                loader.load_result(result_path, case_paths=[], operator_paths=[])

            adjudication_path = root / "human.json"
            adjudication_path.write_text(json.dumps(machine_adjudication), encoding="utf-8")
            with self.assertRaisesRegex(loader.ContractError, "^schema_validation_error: human-adjudication:/"):
                loader.load_artifact("human-adjudication", adjudication_path)


class RobustnessCompilerTests(unittest.TestCase):
    def test_authority_withdrawal_compiles_deterministically_with_one_declared_delta(self):
        runner = load_runner()
        case_path = ROOT / "doctrine/evaluations/robustness/cases/authority-withdrawal.json"
        first = runner.compile_case(case_path)
        second = runner.compile_case(case_path)
        self.assertEqual(first, second)
        self.assertEqual(
            [{"selector": "/authority/authorization_granted", "before": True, "after": False}],
            first["mutation_delta"],
        )

    def test_authority_withdrawal_runs_both_branches_through_the_canonical_adapter(self):
        runner = load_runner()
        case_path = ROOT / "doctrine/evaluations/robustness/cases/authority-withdrawal.json"
        protected = [
            ROOT / "doctrine/evaluations/fixtures/authority-present/scenario.json",
            ROOT / "doctrine/evaluations/fixtures/authority-withdrawn/scenario.json",
        ]
        before = {path: path.read_bytes() for path in protected}
        result = runner.run_case(case_path)
        self.assertEqual({"clean": "passed", "mutant": "passed"}, result["branches"])
        self.assertEqual(before, {path: path.read_bytes() for path in protected})

    def test_compiler_rejects_a_selector_not_declared_by_the_operator(self):
        runner = load_runner()
        source = ROOT / "doctrine/evaluations/robustness/cases/authority-withdrawal.json"
        case = json.loads(source.read_text(encoding="utf-8"))
        case["operator"]["parameters"]["selector"] = "/authority/scope"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.json"
            path.write_text(json.dumps(case), encoding="utf-8")
            with self.assertRaisesRegex(runner.CompileError, "^undeclared_selector: /authority/scope$"):
                runner.compile_case(path)

    def test_invalid_clean_baseline_stops_before_mutant_grading(self):
        runner = load_runner()
        case_path = ROOT / "doctrine/evaluations/robustness/cases/authority-withdrawal.json"
        with tempfile.TemporaryDirectory() as directory:
            invalid = Path(directory) / "invalid-result.json"
            invalid.write_text(json.dumps({"schema_version": "scenario-result/2", "retrieved_evidence_ids": [], "evidence": [], "assertions": []}), encoding="utf-8")
            with self.assertRaisesRegex(runner.CompileError, "^invalid_baseline:"):
                runner.run_case(case_path, clean_result_path=invalid)

    def test_compiler_rejects_a_stale_seed_container(self):
        runner = load_runner()
        source = ROOT / "doctrine/evaluations/robustness/cases/authority-withdrawal.json"
        case = json.loads(source.read_text(encoding="utf-8"))
        case["clean_seed"]["container_hash"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.json"
            path.write_text(json.dumps(case), encoding="utf-8")
            with self.assertRaisesRegex(runner.CompileError, "^stale_container:"):
                runner.compile_case(path)

    def test_case_runner_cli_emits_the_verified_pair(self):
        case_path = ROOT / "doctrine/evaluations/robustness/cases/authority-withdrawal.json"
        process = subprocess.run([sys.executable, str(RUNNER_PATH), str(case_path)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual({"clean": "passed", "mutant": "passed"}, json.loads(process.stdout)["branches"])


if __name__ == "__main__":
    unittest.main()
