#!/usr/bin/env python3
"""Compile and run one isolated Doctrine Robustness Laboratory pair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_robustness_suite import validate_artifact
from evaluation_outcomes import classify_scenario_exit


ROOT = Path(__file__).resolve().parents[2]
ROBUSTNESS = ROOT / "doctrine" / "evaluations" / "robustness"


class CompileError(ValueError):
    pass


class InfrastructureError(RuntimeError):
    pass


class ModelFailure(CompileError):
    pass


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CompileError(f"not_an_object: {path}")
    return value


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _container_hash(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(directory.iterdir()):
        if path.is_file():
            digest.update(path.name.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def _operator(operator_id: str, version: int) -> dict[str, object]:
    registry = yaml.safe_load((ROBUSTNESS / "operators.yaml").read_text(encoding="utf-8"))
    matches = [item for item in registry["operators"] if item["id"] == operator_id and item["version"] == version]
    if len(matches) != 1:
        raise CompileError(f"unresolved_operator: {operator_id}/{version}")
    validate_artifact("operator", matches[0])
    return matches[0]


def compile_case(case_path: Path) -> dict[str, object]:
    """Purely compile clean and mutant stimuli; canonical inputs remain read-only."""
    case = _load_json(case_path)
    validate_artifact("case", case)
    seed = case["clean_seed"]
    reference = case["operator"]
    assert isinstance(seed, dict) and isinstance(reference, dict)
    seed_path = ROOT / str(seed["locator"])
    raw = seed_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != seed["target_hash"]:
        raise CompileError(f"stale_seed: {seed['locator']}")
    if _container_hash(seed_path.parent) != seed["container_hash"]:
        raise CompileError(f"stale_container: {seed_path.parent.relative_to(ROOT)}")
    clean = json.loads(raw)
    clean.pop("expected", None)
    mutant = copy.deepcopy(clean)
    operator = _operator(str(reference["id"]), int(reference["version"]))
    parameters = reference["parameters"]
    assert isinstance(parameters, dict)
    selector = str(parameters["selector"])
    if selector not in operator["allowed_selectors"]:
        raise CompileError(f"undeclared_selector: {selector}")
    if selector != "/authority/authorization_granted":
        raise CompileError(f"unsupported_selector: {selector}")
    before = mutant["authority"]["authorization_granted"]
    after = parameters["value"]
    mutant["authority"]["authorization_granted"] = after
    delta = [{"selector": selector, "before": before, "after": after}]
    return {
        "schema_version": "doctrine-robustness-compiled-pair/1",
        "case_id": case["id"],
        "case_hash": _canonical_hash(case),
        "operator_id": operator["id"],
        "operator_version": operator["version"],
        "clean_input": clean,
        "clean_input_hash": _canonical_hash(clean),
        "mutant_input": mutant,
        "mutant_input_hash": _canonical_hash(mutant),
        "mutation_delta": delta,
        "mutation_delta_hash": _canonical_hash(delta),
    }


def run_case(
    case_path: Path, *, clean_result_path: Path | None = None
) -> dict[str, object]:
    """Run the clean baseline first, then the mutant, via the canonical runner."""
    case = _load_json(case_path)
    compiled = compile_case(case_path)
    seed = case["clean_seed"]
    oracles = case["oracles"]
    assert isinstance(seed, dict) and isinstance(oracles, dict)
    clean_source = _load_json(ROOT / str(seed["locator"]))
    runner = ROOT / "doctrine" / "tools" / "run_scenario.py"
    branches: dict[str, str] = {}
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        for branch in ("clean", "mutant"):
            oracle = oracles[branch]
            assert isinstance(oracle, dict)
            oracle_result_path = ROOT / str(oracle["result_locator"])
            result_path = (
                clean_result_path
                if branch == "clean" and clean_result_path is not None
                else oracle_result_path
            )
            expected_source = _load_json(oracle_result_path.with_name("scenario.json"))
            scenario = copy.deepcopy(compiled[f"{branch}_input"])
            scenario["expected"] = expected_source["expected"]
            scenario_path = workspace / f"{branch}-scenario.json"
            scenario_path.write_text(
                json.dumps(scenario, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            process = subprocess.run(
                [sys.executable, str(runner), str(scenario_path), str(result_path)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            outcome_class = classify_scenario_exit(process.returncode)
            if outcome_class == "infrastructure-failure":
                raise InfrastructureError(
                    f"scenario_runner_infrastructure_failure:{branch}: "
                    f"{process.stderr.strip()}"
                )
            if outcome_class == "model-failure":
                label = "invalid_baseline" if branch == "clean" else "mutant_failed"
                raise ModelFailure(f"{label}: {process.stderr.strip()}")
            branches[branch] = "passed"
    return {"compiled": compiled, "branches": branches}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    args = parser.parse_args()
    try:
        result = run_case(args.case)
    except ModelFailure as error:
        print(f"model-failure: {error}", file=sys.stderr)
        return 1
    except InfrastructureError as error:
        print(f"infrastructure-failure: {error}", file=sys.stderr)
        return 2
    except (CompileError, OSError, json.JSONDecodeError) as error:
        print(f"infrastructure-failure: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
