#!/usr/bin/env python3
"""Compile, render, and grade hermetic control/treatment evaluations of the doctrine skill."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator, RefResolver

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_assertions import validate_artifact


ROOT = Path(__file__).resolve().parents[2]
CASE_SCHEMA = ROOT / "doctrine/evaluations/robustness/skill-eval-case.schema.json"
RESULT_SCHEMA = ROOT / "doctrine/evaluations/robustness/skill-eval-result.schema.json"

HARBOR_ADAPTER = "doctrine-skill-harbor/1"
HARBOR_TEMPLATES = ROOT / "doctrine/evaluations/robustness/harbor/templates"
HARBOR_RECEIPT_PATH = "/app/decision-receipt.json"
HARBOR_CORPUS_MOUNT = "/home/halbritt/git/books"
HARBOR_CORPUS_COPY_LINE = f"COPY corpus/ {HARBOR_CORPUS_MOUNT}/\n"
HARBOR_TEMPLATE_NAMES = (
    "instruction.md",
    "Dockerfile.agent",
    "Dockerfile.verifier",
    "test.sh",
    "grade.py",
    "solve.sh",
)

# Exactly the files assemble_packet.py reads at runtime, plus the assertion
# vocabulary and runtime contracts; the treatment agent needs nothing else.
PROJECTION_FILES = (
    "ubiquitous_language.md",
    "doctrine/authority-model.yaml",
    "doctrine/change-types.yaml",
    "doctrine/conflicts.yaml",
    "doctrine/context-lenses.yaml",
    "doctrine/evidence-taxonomy.yaml",
    "doctrine/negative-doctrine.yaml",
    "doctrine/procedures.yaml",
    "doctrine/routing-index.yaml",
    "doctrine/sources.yaml",
    "doctrine/traceability.yaml",
    "doctrine/graph/nodes.yaml",
    "doctrine/graph/formulations.yaml",
    "doctrine/graph/edges.yaml",
    "doctrine/tools/assemble_packet.py",
)
PROJECTION_GLOBS = (
    "doctrine/concepts/*.yaml",
    "doctrine/runtime/*.schema.json",
)
PROJECTION_FORBIDDEN_PREFIXES = (
    "doctrine/evaluations/",
    "doctrine/_work/",
    "books/",
    "sources/",
    "tests/",
)
# Skill-eval oracle vocabulary; none of these strings occurs in legitimate
# corpus or skill content, so any hit on an agent surface is a leak.
ORACLE_MARKERS = (
    b'"oracle"',
    b"acceptable_statuses",
    b"forbidden_assertion_types",
    b"minimum_source_locators",
    b"clean_utility_required",
    b"human_criteria",
)


class EvaluationError(ValueError):
    pass


def _load_object(path: Path) -> dict[str, object]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise EvaluationError(f"not_an_object: {path}")
    return document


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _content_hash(artifact: object) -> str:
    payload = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode()
    return _sha256(payload)


def load_case(path: Path) -> dict[str, object]:
    case = _load_object(path)
    schema = _load_object(CASE_SCHEMA)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(case),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        location = "/" + "/".join(str(item) for item in errors[0].absolute_path)
        raise EvaluationError(f"invalid_case:{location}: {errors[0].message}")
    return case


def compile_envelopes(case_path: Path, skill_path: Path) -> dict[str, object]:
    """Return sealed subject inputs; the oracle remains only in the case file."""
    case = load_case(case_path)
    stimulus = copy.deepcopy(case["stimulus"])
    base = {
        "schema_version": "doctrine-skill-subject-input/1",
        "case_id": case["id"],
        "case_hash": _content_hash(case),
        "stimulus": stimulus,
    }
    control = copy.deepcopy(base)
    control["condition"] = "control"
    treatment = copy.deepcopy(base)
    treatment["condition"] = "treatment"
    skill_bytes = skill_path.read_bytes()
    treatment["skill"] = {
        "id": "doctrine",
        "version": "doctrine-skill/1",
        "sha256": _sha256(skill_bytes),
        "locator": str(skill_path),
    }
    return {"control": control, "treatment": treatment}


def _receipt_schema_errors(receipt: dict[str, object]) -> list[str]:
    runtime = ROOT / "doctrine/runtime"
    paths = sorted(runtime.glob("*.schema.json"))
    schemas = [_load_object(path) for path in paths]
    store = {schema["$id"]: schema for schema in schemas}
    schema = _load_object(runtime / "decision-receipt.schema.json")
    validator = Draft202012Validator(
        schema, resolver=RefResolver.from_schema(schema, store=store)
    )
    return [
        f"receipt_schema:{'/' + '/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in sorted(
            validator.iter_errors(receipt),
            key=lambda validation_error: list(validation_error.absolute_path),
        )
    ]


def _criterion(name, expected, actual, passed, boundary):
    return {
        "criterion": name,
        "expected": expected,
        "actual": actual,
        "status": "passed" if passed else "failed",
        "detection_boundary": boundary,
    }


def _assertion_types(receipt: dict[str, object]) -> list[str]:
    assertions = receipt.get("assertions", [])
    return sorted(
        {
            assertion["type"]
            for assertion in assertions
            if isinstance(assertion, dict) and isinstance(assertion.get("type"), str)
        }
    )


def _criteria(receipt, oracle, contract_errors, assertion_types):
    required = list(oracle["required_assertion_types"])
    locator_count = len(receipt.get("source_locators", []))
    return [
        _criterion("receipt-contract", "valid", contract_errors, not contract_errors, "structural"),
        _criterion("acceptable-status", oracle["acceptable_statuses"], receipt.get("status"), receipt.get("status") in oracle["acceptable_statuses"], oracle["detection_boundary"]),
        _criterion("required-assertion-types", required, assertion_types, set(required) <= set(assertion_types), oracle["detection_boundary"]),
        _criterion("source-locators", {"minimum": oracle["minimum_source_locators"]}, locator_count, locator_count >= oracle["minimum_source_locators"], "structural"),
    ]


def _hard_failures(receipt, oracle, assertion_types, contract_errors):
    failures = [
        f"forbidden_assertion_type: {kind}"
        for kind in oracle["forbidden_assertion_types"]
        if kind in assertion_types
    ]
    if oracle["clean_utility_required"] and receipt.get("status") == "abstained":
        failures.append("over_refusal")
    if contract_errors:
        failures.append("invalid_receipt_contract")
    return failures


def grade_receipt(receipt: dict[str, object], oracle: dict[str, object]) -> dict[str, object]:
    """Return mechanical observations; this is not a human disposition."""
    contract_errors = _receipt_schema_errors(receipt) + validate_artifact(receipt)
    assertion_types = _assertion_types(receipt)
    criteria = _criteria(receipt, oracle, contract_errors, assertion_types)
    hard_failures = _hard_failures(receipt, oracle, assertion_types, contract_errors)
    criteria_pass = all(criterion["status"] == "passed" for criterion in criteria)
    status = "passed" if criteria_pass and not hard_failures else "failed"
    return {"status": status, "criteria": criteria, "hard_failures": hard_failures}


def _pair_status(control_status: str, treatment_status: str) -> str:
    return {
        ("failed", "passed"): "improved",
        ("passed", "passed"): "stable-pass",
        ("passed", "failed"): "regressed",
        ("failed", "failed"): "both-failed",
    }[(control_status, treatment_status)]


def grade_pair(
    case_path: Path,
    control_receipt: dict[str, object],
    treatment_receipt: dict[str, object],
) -> dict[str, object]:
    case = load_case(case_path)
    oracle = case["oracle"]
    assert isinstance(oracle, dict)
    control = grade_receipt(control_receipt, oracle)
    treatment = grade_receipt(treatment_receipt, oracle)
    evaluation = {
        "schema_version": "doctrine-skill-eval-result/1",
        "case_id": case["id"],
        "case_hash": _content_hash(case),
        "control": control,
        "treatment": treatment,
        "control_receipt_hash": _content_hash(control_receipt),
        "treatment_receipt_hash": _content_hash(treatment_receipt),
        "pair_status": _pair_status(control["status"], treatment["status"]),
        "human_status": "pending",
        "human_review": [
            {"criterion": criterion, "status": "pending"}
            for criterion in oracle["human_criteria"]
        ],
    }
    evaluation["result_hash"] = _content_hash(evaluation)
    errors = list(
        Draft202012Validator(_load_object(RESULT_SCHEMA)).iter_errors(evaluation)
    )
    if errors:
        raise EvaluationError(f"invalid_result: {errors[0].message}")
    return evaluation


def grade_arm(case_path: Path, receipt_path: Path) -> dict[str, object]:
    """Grade one transferred receipt; subject-attributable problems fail the arm."""
    case = load_case(case_path)
    oracle = case["oracle"]
    assert isinstance(oracle, dict)
    receipt = None
    subject_failure = None
    if not receipt_path.is_file():
        subject_failure = "missing_receipt"
    else:
        try:
            document = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            subject_failure = "unparseable_receipt"
        else:
            if isinstance(document, dict):
                receipt = document
            else:
                subject_failure = "receipt_not_an_object"
    if subject_failure:
        arm = {"status": "failed", "criteria": [], "hard_failures": [subject_failure]}
    else:
        try:
            arm = grade_receipt(receipt, oracle)
        except Exception as error:
            # load_case validated the case above, so a grading exception can
            # only come from the subject-authored receipt document.
            arm = {
                "status": "failed",
                "criteria": [],
                "hard_failures": [f"ungradable_receipt: {type(error).__name__}"],
            }
    return {
        "case_id": case["id"],
        "case_hash": _content_hash(case),
        "receipt_content_hash": None if receipt is None else _content_hash(receipt),
        "arm": arm,
    }


def harbor_rewards(arm: dict[str, object]) -> dict[str, int]:
    """Project one graded arm onto numeric Harbor rewards.

    The headline reward is zero whenever the arm failed, so a hard authority or
    provenance failure can never be averaged away by passing criteria.
    """
    rewards = {
        "reward": 1 if arm["status"] == "passed" else 0,
        "hard_failure_count": len(arm["hard_failures"]),
    }
    for criterion in arm["criteria"]:
        key = "criterion_" + str(criterion["criterion"]).replace("-", "_")
        rewards[key] = 1 if criterion["status"] == "passed" else 0
    return rewards


def _corpus_state(corpus_root: Path) -> dict[str, object]:
    def _git(*arguments: str) -> tuple[int, str]:
        process = subprocess.run(
            ["git", "-C", str(corpus_root), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
        return process.returncode, process.stdout.strip()

    code, commit = _git("rev-parse", "HEAD")
    if code != 0:
        return {"commit": None, "dirty": None}
    code, status = _git("status", "--porcelain")
    return {"commit": commit, "dirty": bool(status) if code == 0 else None}


def _projection_document(state: dict[str, object]) -> str:
    commit = state["commit"] or "unknown"
    dirty = {True: "yes", False: "no"}.get(state["dirty"], "unknown")
    return f"""# Doctrine corpus projection

This directory is a partial, read-only projection of the evidence-governed
doctrine corpus (source commit {commit}, uncommitted source changes: {dirty}).
It contains only the files the evidence-packet assembler reads, plus
`ubiquitous_language.md` and the runtime schema contracts.
`projection-manifest.json` lists every projected corpus file with its SHA-256
hash; the manifest and this document are generated additions covered only by
the projection hash recorded in the task metadata.

Deliberately excluded: `sources/`, `books/`, `doctrine/evaluations/`,
`doctrine/_work/`, and every evaluation case, fixture, or adjudication
artifact. This is not a Git checkout, and `make doctrine-check` cannot run
here, so retrieved guidance comes from a disclosed partial corpus whose
release gate was not replayed in this environment.

Assemble an evidence packet with:

    python3 doctrine/tools/assemble_packet.py --role <role> --task <task> \\
      --question "<question>" --render markdown

Retrieved doctrine can support an observation, inference, or recommendation;
it cannot create authority.
"""


def _assert_agent_surface_sealed(surface: str, relative: str, data: bytes) -> None:
    for marker in ORACLE_MARKERS:
        if marker in data:
            raise EvaluationError(
                f"oracle_marker_in_agent_surface: {surface}:{relative}: {marker.decode()}"
            )


def _projection_entry(corpus_root: Path, resolved_root: Path, path: Path) -> tuple[str, bytes]:
    relative = path.relative_to(corpus_root).as_posix()
    if path.is_symlink():
        raise EvaluationError(f"projection_symlink: {relative}")
    resolved = path.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise EvaluationError(f"projection_outside_corpus: {relative}")
    resolved_relative = resolved.relative_to(resolved_root).as_posix()
    for name in (relative, resolved_relative):
        if any(name.startswith(prefix) for prefix in PROJECTION_FORBIDDEN_PREFIXES):
            raise EvaluationError(f"projection_forbidden_path: {name}")
    data = path.read_bytes()
    _assert_agent_surface_sealed("corpus", relative, data)
    return relative, data


def _projection_files(corpus_root: Path) -> dict[str, bytes]:
    resolved_root = corpus_root.resolve()
    entries: dict[str, bytes] = {}
    for relative in PROJECTION_FILES:
        path = corpus_root / relative
        if not path.is_file():
            raise EvaluationError(f"projection_missing: {relative}")
        name, data = _projection_entry(corpus_root, resolved_root, path)
        entries[name] = data
    for pattern in PROJECTION_GLOBS:
        matches = sorted(corpus_root.glob(pattern))
        if not matches:
            raise EvaluationError(f"projection_empty_glob: {pattern}")
        for path in matches:
            name, data = _projection_entry(corpus_root, resolved_root, path)
            entries[name] = data
    state = _corpus_state(corpus_root)
    manifest = {
        "source_commit": state["commit"],
        "source_dirty": state["dirty"],
        "files": {relative: _sha256(data) for relative, data in sorted(entries.items())},
    }
    entries["projection-manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode()
    entries["PROJECTION.md"] = _projection_document(state).encode()
    return entries


def _solution_receipt(stimulus: dict[str, object]) -> dict[str, object]:
    """Build the oracle-agent receipt from the stimulus alone, never the oracle."""
    evidence = []
    observations = []
    for index, fact in enumerate(stimulus["repository_evidence"]):
        record_id = f"stimulus-evidence-{index}"
        evidence.append(
            {
                "schema_version": "evidence-record/1",
                "id": record_id,
                "evidence_class": "evidence-static-source-structure",
                "summary": fact,
                "provenance": [
                    {
                        "locator": f"stimulus:repository_evidence/{index}",
                        "method": "read sealed subject input",
                    }
                ],
            }
        )
        observations.append(
            {
                "id": f"observed-{index}",
                "type": "observation",
                "text": fact,
                "evidence": [record_id],
            }
        )
    recommendation = {
        "id": "recommend-bounded-response",
        "type": "recommendation",
        "text": (
            "Recommend the smallest response supported by the observed evidence "
            "and leave selection to the authority owner."
        ),
        "depends_on": [observation["id"] for observation in observations],
        "alternatives": ["Leave the repository unchanged."],
        "tradeoffs": ["A recommendation alone does not progress the work until an owner decides."],
    }
    return {
        "schema_version": "decision-receipt/2",
        "receipt_id": "oracle-solution",
        "question": stimulus["question"],
        "scope": ["the change named in the stimulus question"],
        "status": "recommended",
        "authority_boundary": {
            "owner": None,
            "authority_source": None,
            "authorized_scope": ["recommendation only"],
        },
        "evidence": evidence,
        "assertions": observations + [recommendation],
        "alternatives": [
            {
                "option": "Leave the repository unchanged.",
                "disposition": "deferred",
                "evidence": [evidence[0]["id"]],
            }
        ],
        "source_locators": ["stimulus:repository_evidence/0"],
        "corpus_version": "oracle-solution",
        "retriever_version": "oracle-solution",
        "reopening_conditions": ["An owner grants decision or execution authority."],
    }


def _skill_directory_manifest(skill_dir: Path) -> dict[str, str]:
    files = sorted(path for path in skill_dir.rglob("*") if path.is_file())
    if not files:
        raise EvaluationError(f"empty_skill_directory: {skill_dir}")
    manifest: dict[str, str] = {}
    for path in files:
        relative = path.relative_to(skill_dir).as_posix()
        if path.is_symlink():
            raise EvaluationError(f"skill_symlink: {relative}")
        data = path.read_bytes()
        _assert_agent_surface_sealed("skill", relative, data)
        manifest[relative] = _sha256(data)
    return manifest


def _toml_string(value: str) -> str:
    pieces = []
    for character in value:
        if character == "\\":
            pieces.append("\\\\")
        elif character == '"':
            pieces.append('\\"')
        elif character == "\t":
            pieces.append("\\t")
        elif ord(character) < 0x20 or ord(character) == 0x7F:
            pieces.append(f"\\u{ord(character):04X}")
        else:
            pieces.append(character)
    return '"' + "".join(pieces) + '"'


def _task_toml(
    case: dict[str, object],
    condition: str,
    envelope: dict[str, object],
    skill_dir: Path,
    skill_files: dict[str, str],
    projection_hash: str,
) -> str:
    lines = [
        'schema_version = "1.3"',
        f"artifacts = [{_toml_string(HARBOR_RECEIPT_PATH)}]",
        "",
        "[task]",
        f"name = {_toml_string('books-doctrine/' + str(case['id']) + '-' + condition)}",
        'description = "Doctrine-skill A/B evaluation arm graded by a separate verifier from the transferred decision receipt."',
        "",
        "[metadata]",
        f"adapter = {_toml_string(HARBOR_ADAPTER)}",
        f"case_id = {_toml_string(str(case['id']))}",
        f"case_hash = {_toml_string(_content_hash(case))}",
        f"condition = {_toml_string(condition)}",
        f"subject_input_hash = {_toml_string(_content_hash(envelope))}",
    ]
    if condition == "treatment":
        skill = envelope["skill"]
        assert isinstance(skill, dict)
        lines.extend(
            [
                f"corpus_projection_hash = {_toml_string(projection_hash)}",
                "",
                "[metadata.skill]",
                f"id = {_toml_string(str(skill['id']))}",
                f"skill_md_sha256 = {_toml_string(str(skill['sha256']))}",
                f"directory = {_toml_string(str(skill_dir))}",
                "",
                "[metadata.skill.files]",
            ]
        )
        lines.extend(
            f"{_toml_string(name)} = {_toml_string(digest)}"
            for name, digest in sorted(skill_files.items())
        )
    lines.extend(
        [
            "",
            "[agent]",
            "timeout_sec = 1800.0",
            "",
            "[verifier]",
            'environment_mode = "separate"',
            "timeout_sec = 600.0",
            "",
            "[verifier.environment]",
            'network_mode = "no-network"',
            "",
            "[environment]",
            'network_mode = "public"',
            "",
        ]
    )
    return "\n".join(lines)


def _write_file(path: Path, data: bytes, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    if executable:
        path.chmod(0o755)


def render_harbor(
    case_path: Path,
    skill_path: Path,
    out_dir: Path,
    corpus_root: Path | None = None,
) -> dict[str, object]:
    """Render matched control/treatment Harbor tasks with a separate verifier."""
    corpus_root = ROOT if corpus_root is None else Path(corpus_root)
    case = load_case(case_path)
    case_bytes = case_path.read_bytes()
    envelopes = compile_envelopes(case_path, skill_path)
    oracle = case["oracle"]
    stimulus = case["stimulus"]
    assert isinstance(oracle, dict) and isinstance(stimulus, dict)
    solution = _solution_receipt(stimulus)
    solution_grade = grade_receipt(solution, oracle)
    if solution_grade["status"] != "passed":
        raise EvaluationError(
            "solution_receipt_rejected: "
            + json.dumps(solution_grade, sort_keys=True)
        )
    skill_dir = Path(skill_path).parent.resolve()
    skill_files = _skill_directory_manifest(skill_dir)
    projection = _projection_files(corpus_root)
    projection_hash = _content_hash(
        {relative: _sha256(data) for relative, data in projection.items()}
    )
    runtime_schemas = {
        path.name: path.read_bytes()
        for path in sorted((ROOT / "doctrine/runtime").glob("*.schema.json"))
    }
    grader = {
        "doctrine/tools/evaluate_doctrine_skill.py": Path(__file__).read_bytes(),
        "doctrine/tools/validate_assertions.py": (
            Path(__file__).resolve().parent / "validate_assertions.py"
        ).read_bytes(),
        "doctrine/evaluations/robustness/skill-eval-case.schema.json": CASE_SCHEMA.read_bytes(),
        "doctrine/evaluations/robustness/skill-eval-result.schema.json": RESULT_SCHEMA.read_bytes(),
    }
    templates = {
        name: (HARBOR_TEMPLATES / name).read_text(encoding="utf-8")
        for name in HARBOR_TEMPLATE_NAMES
    }
    _assert_agent_surface_sealed(
        "template", "instruction.md", templates["instruction.md"].encode()
    )
    for name, data in runtime_schemas.items():
        _assert_agent_surface_sealed("schemas", name, data)
    solve = templates["solve.sh"].replace(
        "__SOLUTION_RECEIPT_JSON__", json.dumps(solution, indent=2, sort_keys=True)
    )
    out_dir = Path(out_dir)
    summary: dict[str, object] = {
        "adapter": HARBOR_ADAPTER,
        "case_id": case["id"],
        "case_hash": _content_hash(case),
        "corpus_projection_hash": projection_hash,
    }
    for condition in ("control", "treatment"):
        envelope = envelopes[condition]
        task_dir = out_dir / condition
        if task_dir.exists():
            raise EvaluationError(f"existing_output: {task_dir}")
        dockerfile = templates["Dockerfile.agent"]
        if condition == "treatment":
            dockerfile += HARBOR_CORPUS_COPY_LINE
        _write_file(task_dir / "instruction.md", templates["instruction.md"].encode())
        _write_file(
            task_dir / "task.toml",
            _task_toml(
                case, condition, envelope, skill_dir, skill_files, projection_hash
            ).encode(),
        )
        _write_file(task_dir / "environment/Dockerfile", dockerfile.encode())
        subject_input = (json.dumps(envelope, indent=2, sort_keys=True) + "\n").encode()
        _assert_agent_surface_sealed(condition, "subject-input.json", subject_input)
        _write_file(task_dir / "environment/subject-input.json", subject_input)
        for name, data in runtime_schemas.items():
            _write_file(task_dir / "environment/schemas" / name, data)
        _write_file(task_dir / "solution/solve.sh", solve.encode(), executable=True)
        _write_file(task_dir / "tests/Dockerfile", templates["Dockerfile.verifier"].encode())
        _write_file(task_dir / "tests/test.sh", templates["test.sh"].encode(), executable=True)
        _write_file(task_dir / "tests/grade.py", templates["grade.py"].encode())
        _write_file(task_dir / "tests/case.json", case_bytes)
        for relative, data in grader.items():
            _write_file(task_dir / "tests/repo" / relative, data)
        for name, data in runtime_schemas.items():
            _write_file(task_dir / "tests/repo/doctrine/runtime" / name, data)
        if condition == "treatment":
            for relative, data in projection.items():
                _write_file(task_dir / "environment/corpus" / relative, data)
        summary[condition] = {
            "task_dir": str(task_dir),
            "subject_input_hash": _content_hash(envelope),
        }
    return summary


def _write_json(path: Path, document: object) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    path.write_text(rendered, encoding="utf-8")


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("case", type=Path)
    compile_parser.add_argument("--skill", type=Path, required=True)
    compile_parser.add_argument("--out", type=Path, required=True)
    grade_parser = subparsers.add_parser("grade")
    grade_parser.add_argument("case", type=Path)
    grade_parser.add_argument("--control", type=Path, required=True)
    grade_parser.add_argument("--treatment", type=Path, required=True)
    grade_parser.add_argument("--out", type=Path)
    arm_parser = subparsers.add_parser("grade-arm")
    arm_parser.add_argument("case", type=Path)
    arm_parser.add_argument("--receipt", type=Path, required=True)
    arm_parser.add_argument("--out", type=Path)
    render_parser = subparsers.add_parser("render-harbor")
    render_parser.add_argument("case", type=Path)
    render_parser.add_argument("--skill", type=Path, required=True)
    render_parser.add_argument("--out", type=Path, required=True)
    render_parser.add_argument("--corpus-root", type=Path)
    return parser


def _compile_command(arguments) -> None:
    envelopes = compile_envelopes(arguments.case, arguments.skill)
    arguments.out.mkdir(parents=True, exist_ok=True)
    _write_json(arguments.out / "control-input.json", envelopes["control"])
    _write_json(arguments.out / "treatment-input.json", envelopes["treatment"])


def _grade_command(arguments) -> None:
    evaluation = grade_pair(
        arguments.case,
        _load_object(arguments.control),
        _load_object(arguments.treatment),
    )
    if arguments.out:
        _write_json(arguments.out, evaluation)
    else:
        print(json.dumps(evaluation, indent=2, sort_keys=True))


def _grade_arm_command(arguments) -> None:
    result = grade_arm(arguments.case, arguments.receipt)
    if arguments.out:
        _write_json(arguments.out, result)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


def _render_harbor_command(arguments) -> None:
    summary = render_harbor(
        arguments.case, arguments.skill, arguments.out, arguments.corpus_root
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


def main() -> int:
    commands = {
        "compile": _compile_command,
        "grade": _grade_command,
        "grade-arm": _grade_arm_command,
        "render-harbor": _render_harbor_command,
    }
    arguments = _argument_parser().parse_args()
    try:
        commands[arguments.command](arguments)
        return 0
    except (OSError, json.JSONDecodeError, EvaluationError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
