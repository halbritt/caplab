"""Frozen native-harness evaluation for the CAPLAB-16 r2 adapter."""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from collections import Counter
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable

from .instrument import load_qualification_instrument
from .local_training import (
    build_local_review_prompt,
    grade_local_review,
    parse_local_review_output,
)


class TrainingEvaluationError(RuntimeError):
    """The frozen evaluation departed from its adapter, harness, or call contract."""


SUBJECTS = {
    "base": {
        "model": "caplab-qwen3.6-27b-base",
        "tuple_id": "qwen3.6-27b-base-striatum-openai-lane-v1",
    },
    "tuned": {
        "model": "caplab-qwen3.6-27b-tuned",
        "tuple_id": "qwen3.6-27b-tuned-striatum-openai-lane-v1",
    },
}


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _exclusive(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def validate_adapter_seal(training_root: Path) -> str:
    """Require the final adapter to match the immutable training result."""

    result_path = training_root / "result.json"
    adapter_path = training_root / "final-adapter" / "adapter_model.safetensors"
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        expected = result["files"]["final-adapter/adapter_model.safetensors"]
    except (OSError, KeyError, json.JSONDecodeError) as error:
        raise TrainingEvaluationError("training_result_or_adapter_binding_missing") from error
    actual = sha256(adapter_path.read_bytes()).hexdigest()
    sealed = dict(result)
    claimed = sealed.pop("result_sha256", None)
    if claimed != _digest(sealed):
        raise TrainingEvaluationError("training_result_digest_mismatch")
    if result.get("experiment_id") != "caplab-review-dissent-qwen27b-qlora-r2":
        raise TrainingEvaluationError("training_result_experiment_mismatch")
    if result.get("global_steps") != 12 or actual != expected:
        raise TrainingEvaluationError("final_adapter_not_sealed")
    return actual


def heldout_order() -> list[tuple[str, str]]:
    """Return the frozen cell order with independently randomized pair order."""

    rng = random.Random(1729)
    order: list[tuple[str, str]] = []
    for cell_id in ("r09", "r10", "r11", "r12", "r13", "r14", "r15", "r16"):
        pair = ["base", "tuned"]
        rng.shuffle(pair)
        order.extend((cell_id, subject_id) for subject_id in pair)
    return order


def _invoke(
    endpoint: str,
    subject_id: str,
    prompt: bytes,
    *,
    run: Callable[..., subprocess.CompletedProcess[bytes]],
) -> subprocess.CompletedProcess[bytes]:
    subject = SUBJECTS[subject_id]
    command = [
        "striatum-openai-lane",
        "-base-url",
        endpoint,
        "-model",
        subject["model"],
        "-max-tokens",
        "4096",
        "-temperature",
        "0",
        "-timeout",
        "15m",
    ]
    return run(
        command,
        input=prompt,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=900,
    )


def _review_attempt(
    instrument: dict[str, Any],
    *,
    endpoint: str,
    cell_id: str,
    subject_id: str,
    attempt_number: int,
    output: Path,
    run: Callable[..., subprocess.CompletedProcess[bytes]],
    replacement_for: int | None = None,
) -> dict[str, Any]:
    prompt = build_local_review_prompt(instrument, cell_id).encode("utf-8")
    completed = _invoke(endpoint, subject_id, prompt, run=run)
    root = output / "heldout-attempts" / f"a{attempt_number:02d}-{cell_id}-{subject_id}"
    _exclusive(root / "prompt.txt", prompt)
    _exclusive(root / "stdout", completed.stdout)
    _exclusive(root / "stderr", completed.stderr)
    status = "infrastructure" if completed.returncode else "subject-invalid"
    row: dict[str, Any] | None = None
    if completed.returncode == 0:
        try:
            review = parse_local_review_output(completed.stdout)
            row = grade_local_review(
                instrument,
                cell_id=cell_id,
                review=review,
                response_sha256=sha256(completed.stdout).hexdigest(),
                tuple_id=SUBJECTS[subject_id]["tuple_id"],
            )
            status = "completed"
        except ValueError:
            pass
    attempt = {
        "schema": "caplab.training.heldout-attempt/v1",
        "attempt_number": attempt_number,
        "cell_id": cell_id,
        "subject_id": subject_id,
        "tuple_id": SUBJECTS[subject_id]["tuple_id"],
        "native_harness": "striatum-openai-lane",
        "native_harness_version": 1,
        "prompt_sha256": sha256(prompt).hexdigest(),
        "stdout_sha256": sha256(completed.stdout).hexdigest(),
        "stderr_sha256": sha256(completed.stderr).hexdigest(),
        "return_code": completed.returncode,
        "status": status,
        "row": row,
        "replacement_for": replacement_for,
    }
    attempt["attempt_sha256"] = _digest(attempt)
    _exclusive(root / "attempt.json", _canonical(attempt) + b"\n")
    return attempt


def _control_attempt(
    control: dict[str, Any],
    *,
    endpoint: str,
    subject_id: str,
    sequence: int,
    output: Path,
    run: Callable[..., subprocess.CompletedProcess[bytes]],
) -> dict[str, Any]:
    prompt = control["prompt"].encode("utf-8")
    completed = _invoke(endpoint, subject_id, prompt, run=run)
    schema_valid = False
    answer: str | None = None
    if completed.returncode == 0:
        try:
            value = json.loads(completed.stdout)
            schema_valid = (
                isinstance(value, dict)
                and set(value) == {"answer"}
                and isinstance(value["answer"], str)
            )
            answer = value["answer"] if schema_valid else None
        except (UnicodeError, json.JSONDecodeError):
            pass
    attempt = {
        "schema": "caplab.training.general-control-attempt/v1",
        "sequence": sequence,
        "control_id": control["control_id"],
        "subject_id": subject_id,
        "tuple_id": SUBJECTS[subject_id]["tuple_id"],
        "native_harness": "striatum-openai-lane",
        "native_harness_version": 1,
        "prompt_sha256": sha256(prompt).hexdigest(),
        "stdout_sha256": sha256(completed.stdout).hexdigest(),
        "stderr_sha256": sha256(completed.stderr).hexdigest(),
        "return_code": completed.returncode,
        "schema_valid": schema_valid,
        "answer": answer,
        "correct": schema_valid and answer == control["oracle"],
    }
    attempt["attempt_sha256"] = _digest(attempt)
    root = output / "control-attempts" / f"a{sequence:02d}-{control['control_id']}-{subject_id}"
    _exclusive(root / "prompt.txt", prompt)
    _exclusive(root / "stdout", completed.stdout)
    _exclusive(root / "stderr", completed.stderr)
    _exclusive(root / "attempt.json", _canonical(attempt) + b"\n")
    return attempt


def _subject_summary(attempts: list[dict[str, Any]], subject_id: str) -> dict[str, Any]:
    rows = [item["row"] for item in attempts if item["subject_id"] == subject_id]
    eligible = [row for row in rows if isinstance(row, dict)]
    scores = [Decimal(row["score"]) for row in eligible]
    return {
        "slots": sum(item["subject_id"] == subject_id for item in attempts),
        "schema_valid": len(eligible),
        "mean_score": format(sum(scores) / len(scores), ".6f") if scores else None,
        "score_bands": dict(sorted(Counter(row["score"] for row in eligible).items())),
        "clean_false_blockers": sum(
            row["truth"] == "clean" and row["review"]["verdict"] != "clear"
            for row in eligible
        ),
        "defect_false_clears": sum(
            row["truth"] == "defect" and row["review"]["verdict"] == "clear"
            for row in eligible
        ),
    }


def run_evaluation(
    *,
    endpoint: str,
    training_root: Path,
    study_root: Path,
    controls_path: Path,
    output: Path,
    run: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    """Open held-out bytes only after the final adapter is sealed, then run once."""

    if output.exists() or output.is_symlink():
        raise TrainingEvaluationError("evaluation_output_exists")
    adapter_sha256 = validate_adapter_seal(training_root)
    instrument = load_qualification_instrument(study_root)
    if instrument["artifacts"]["heldout"]["sha256"] != "ec7ef0160e878608094f190b7af5bb3c20e4183e7621cdb5d9d1464fb5fe2834":
        raise TrainingEvaluationError("heldout_seal_mismatch")
    controls_bytes = controls_path.read_bytes()
    if sha256(controls_bytes).hexdigest() != "3f228381f6eb6175e8924af00709c3fe01e66bcb7f7c2601585ac09272647108":
        raise TrainingEvaluationError("general_controls_digest_mismatch")
    controls = json.loads(controls_bytes)["controls"]
    output.mkdir(parents=True, mode=0o700)

    attempts: list[dict[str, Any]] = []
    replacements = 0
    attempt_number = 0
    for cell_id, subject_id in heldout_order():
        attempt_number += 1
        attempt = _review_attempt(
            instrument,
            endpoint=endpoint,
            cell_id=cell_id,
            subject_id=subject_id,
            attempt_number=attempt_number,
            output=output,
            run=run,
        )
        attempts.append(attempt)
        if attempt["status"] == "infrastructure":
            if replacements >= 2:
                raise TrainingEvaluationError("infrastructure_replacement_ceiling")
            replacements += 1
            attempt_number += 1
            replacement = _review_attempt(
                instrument,
                endpoint=endpoint,
                cell_id=cell_id,
                subject_id=subject_id,
                attempt_number=attempt_number,
                output=output,
                run=run,
                replacement_for=attempt["attempt_number"],
            )
            attempts.append(replacement)
            if replacement["status"] == "infrastructure":
                raise TrainingEvaluationError("repeated_infrastructure_failure")

    controls_result: list[dict[str, Any]] = []
    sequence = 0
    for control in controls:
        for subject_id in ("base", "tuned"):
            sequence += 1
            controls_result.append(
                _control_attempt(
                    control,
                    endpoint=endpoint,
                    subject_id=subject_id,
                    sequence=sequence,
                    output=output,
                    run=run,
                )
            )

    effective = [
        item
        for item in attempts
        if item["status"] != "infrastructure"
    ]
    base = _subject_summary(effective, "base")
    tuned = _subject_summary(effective, "tuned")
    control_summary = {
        subject_id: {
            "correct": sum(
                item["correct"] for item in controls_result if item["subject_id"] == subject_id
            ),
            "schema_valid": sum(
                item["schema_valid"] for item in controls_result if item["subject_id"] == subject_id
            ),
        }
        for subject_id in ("base", "tuned")
    }
    improvement = (
        Decimal(tuned["mean_score"]) - Decimal(base["mean_score"])
        if tuned["mean_score"] is not None and base["mean_score"] is not None
        else None
    )
    success = (
        len(effective) == 16
        and base["schema_valid"] == 8
        and tuned["schema_valid"] == 8
        and improvement is not None
        and improvement >= Decimal("0.10")
        and tuned["clean_false_blockers"] == 0
        and tuned["clean_false_blockers"] <= base["clean_false_blockers"]
        and tuned["defect_false_clears"] <= base["defect_false_clears"]
        and control_summary["tuned"]["correct"] >= control_summary["base"]["correct"] - 1
        and control_summary["tuned"]["schema_valid"] >= control_summary["base"]["schema_valid"]
    )
    result = {
        "schema": "caplab.training.heldout-evaluation-result/v1",
        "experiment_id": "caplab-review-dissent-qwen27b-qlora-r2",
        "adapter_sha256": adapter_sha256,
        "native_harness": "striatum-openai-lane",
        "native_harness_version": 1,
        "heldout_attempts": attempts,
        "infrastructure_replacements": replacements,
        "subjects": {"base": base, "tuned": tuned},
        "paired_mean_improvement": format(improvement, ".6f") if improvement is not None else None,
        "general_controls": controls_result,
        "general_control_summary": control_summary,
        "success": success,
    }
    result["result_sha256"] = _digest(result)
    _exclusive(output / "result.json", _canonical(result) + b"\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--training-root", required=True, type=Path)
    parser.add_argument("--study-root", required=True, type=Path)
    parser.add_argument("--controls", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = run_evaluation(
            endpoint=args.endpoint,
            training_root=args.training_root,
            study_root=args.study_root,
            controls_path=args.controls,
            output=args.output,
        )
    except Exception as error:
        print(
            f"caplab-training-evaluation: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
