"""Fail-closed paid training orchestration for the Qwen MoE job.

The model worker remains :mod:`jobs.qwen35b_moe.train`.  This module owns
only the paid-run policy around it: measure five optimizer steps, project the
whole run against the controller-declared limits, advance to checkpoint 25,
screen that checkpoint in a separate model process, advance to the exact first-
epoch checkpoint at step 159, screen all 98 held-out examples in another model
process, and only then resume the intended 318-step run.

The arithmetic and receipt validators deliberately import no GPU libraries so
their decisions can be exercised in ordinary unit tests.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import time
from typing import Mapping, Sequence

from .contract import (
    STRATEGIES,
    ContractError,
    expected_adapter_measurement,
    sha256_file,
)
from .peft_config import validate_base_preparation_receipt
from .runtime import input_dir_from_env, model_dir_from_env, output_dir_from_env
from .train import (
    validate_liger_fused_loss_proof,
    validate_sft_tokenization_census,
)


TIMING_STEPS = 5
SCREENING_CHECKPOINT_STEP = 25
EPOCH_ONE_CHECKPOINT_STEP = 159
TOTAL_STEPS = 318
CHECKPOINT_INTERVAL = 25
MINI_EVAL_EXAMPLES = 16
EPOCH_ONE_EVAL_EXAMPLES = 98
IN_TRAIN_EVALUATION_RESERVE_SECONDS = 1_800.0
POST_TRAIN_EVALUATION_EXPORT_RESERVE_SECONDS = 3_600.0
AVAILABLE_QUALITY_METRICS = ("json_valid", "verdict_legal", "side_match")


@dataclass(frozen=True)
class PaidLimits:
    """Controller-normalized limits copied from one ``run-request/1``."""

    max_elapsed_seconds: float
    max_cost_usd: Decimal
    usd_per_hour: Decimal

    @property
    def cost_cap_elapsed_seconds(self) -> Decimal:
        return self.max_cost_usd * Decimal(3_600) / self.usd_per_hour

    def to_dict(self) -> dict[str, object]:
        return {
            "max_elapsed_seconds": self.max_elapsed_seconds,
            "max_cost_usd": format(self.max_cost_usd, "f"),
            "usd_per_hour": format(self.usd_per_hour, "f"),
            "cost_cap_elapsed_seconds": format(self.cost_cap_elapsed_seconds, "f"),
        }


@dataclass(frozen=True)
class TimingProjection:
    """A transparent projection from measured optimizer work to run close."""

    measured_steps: int
    completed_steps: int
    target_steps: int
    measured_train_runtime_seconds: float
    measured_worker_wall_seconds: float
    elapsed_per_step_seconds: float
    observed_worker_startup_seconds: float
    runner_elapsed_at_gate_seconds: float
    remaining_steps: int
    future_training_worker_starts: int
    evaluation_export_reserve_seconds: float
    projected_total_elapsed_seconds: float
    projected_cost_usd: Decimal
    elapsed_cap_passed: bool
    cost_cap_passed: bool

    @property
    def passed(self) -> bool:
        return self.elapsed_cap_passed and self.cost_cap_passed

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["projected_cost_usd"] = format(self.projected_cost_usd, "f")
        result["passed"] = self.passed
        result["method"] = (
            "runner elapsed at gate + remaining steps at measured Transformers "
            "train_runtime/step + observed startup for each future training "
            "worker + fixed mini/full-eval-and-export reserve"
        )
        return result


@dataclass(frozen=True)
class TrainPhaseProjection:
    """Projected training-worker wall time against the runner phase timeout."""

    phase_elapsed_at_gate_seconds: float
    remaining_steps: int
    elapsed_per_step_seconds: float
    future_training_worker_starts: int
    observed_worker_startup_seconds: float
    in_phase_evaluation_reserve_seconds: float
    projected_remaining_train_wall_seconds: float
    projected_train_phase_elapsed_seconds: float
    train_phase_timeout_seconds: float
    remaining_train_phase_budget_seconds: float
    passed: bool

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["method"] = (
            "train-phase elapsed at gate + remaining optimizer steps + observed "
            "startup for each future training worker + evaluation gates inside "
            "train; later evaluate/package phase reserve is excluded"
        )
        return result


@dataclass(frozen=True)
class CheckpointEvidence:
    step: int
    checkpoint: str
    manifest_sha256: str
    files: int
    bytes: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _positive_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{label} must be a positive number")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ContractError(f"{label} must be a positive finite number")
    return number


def _nonnegative_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{label} must be a nonnegative number")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ContractError(f"{label} must be a nonnegative finite number")
    return number


def _positive_decimal(value: object, label: str) -> Decimal:
    if not isinstance(value, str):
        raise ContractError(f"{label} must be an exact decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ContractError(f"{label} is not a decimal amount") from error
    if not result.is_finite() or result <= 0:
        raise ContractError(f"{label} must be positive and finite")
    return result


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{label} must be an object")
    return value


def limits_from_run_request(request: Mapping[str, object]) -> PaidLimits:
    """Extract paid limits without accepting a second source of authority."""

    if request.get("protocol") != "run-request/1":
        raise ContractError("paid training requires a run-request/1")
    limits = _mapping(request.get("limits"), "run request limits")
    return PaidLimits(
        max_elapsed_seconds=_positive_number(
            limits.get("max_elapsed_seconds"), "limits.max_elapsed_seconds"
        ),
        max_cost_usd=_positive_decimal(
            limits.get("max_cost_usd"), "limits.max_cost_usd"
        ),
        usd_per_hour=_positive_decimal(
            limits.get("usd_per_hour"), "limits.usd_per_hour"
        ),
    )


def optimizer_steps_per_epoch(
    examples: object,
    per_device_batch_size: object,
    gradient_accumulation_steps: object,
) -> int:
    """Derive single-GPU optimizer steps using the Trainer rounding contract."""

    values = {
        "examples": examples,
        "per_device_batch_size": per_device_batch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
    }
    for label, value in values.items():
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ContractError(f"{label} must be a positive integer")
    assert isinstance(examples, int)
    assert isinstance(per_device_batch_size, int)
    assert isinstance(gradient_accumulation_steps, int)
    examples_per_step = per_device_batch_size * gradient_accumulation_steps
    return (examples + examples_per_step - 1) // examples_per_step


def train_timeout_from_run_request(request: Mapping[str, object]) -> float:
    """Read the independently enforced train-phase timeout from the request."""

    if request.get("protocol") != "run-request/1":
        raise ContractError("paid training requires a run-request/1")
    phases = _mapping(request.get("phases"), "run request phases")
    train = _mapping(phases.get("train"), "run request train phase")
    if train.get("enabled") is not True:
        raise ContractError("paid training requires the train phase to be enabled")
    return _positive_number(
        train.get("timeout_seconds"), "phases.train.timeout_seconds"
    )


def project_paid_run(
    limits: PaidLimits,
    *,
    measured_steps: int,
    completed_steps: int,
    target_steps: int,
    measured_train_runtime_seconds: float,
    measured_worker_wall_seconds: float,
    runner_elapsed_at_gate_seconds: float,
    future_training_worker_starts: int,
    evaluation_export_reserve_seconds: float,
    elapsed_per_step_floor_seconds: float = 0.0,
    worker_startup_floor_seconds: float = 0.0,
) -> TimingProjection:
    """Project the run from observed work, retaining conservative overhead.

    ``train_runtime`` is the worker's Transformers metric and is therefore the
    optimizer-step timing source.  Wall time minus that metric is retained as
    observed model/dataset startup overhead for each future training worker.
    The optional floor prevents a later sample from revising an earlier,
    slower observation downward before the expensive final continuation.
    """

    if isinstance(measured_steps, bool) or measured_steps < TIMING_STEPS:
        raise ContractError(
            f"timing projection requires at least {TIMING_STEPS} optimizer steps"
        )
    if (
        isinstance(completed_steps, bool)
        or isinstance(target_steps, bool)
        or completed_steps < measured_steps
        or target_steps <= completed_steps
    ):
        raise ContractError("projection step bounds are inconsistent")
    if (
        isinstance(future_training_worker_starts, bool)
        or future_training_worker_starts < 0
    ):
        raise ContractError("future worker start count must be nonnegative")
    train_runtime = _positive_number(
        measured_train_runtime_seconds, "measured train runtime"
    )
    worker_wall = _positive_number(
        measured_worker_wall_seconds, "measured worker wall time"
    )
    runner_elapsed = _positive_number(
        runner_elapsed_at_gate_seconds, "runner elapsed at gate"
    )
    reserve = _nonnegative_number(
        evaluation_export_reserve_seconds, "evaluation/export reserve"
    )
    floor = _nonnegative_number(
        elapsed_per_step_floor_seconds, "elapsed-per-step floor"
    )
    startup_floor = _nonnegative_number(
        worker_startup_floor_seconds, "worker-startup floor"
    )
    observed_per_step = train_runtime / measured_steps
    elapsed_per_step = max(observed_per_step, floor)
    startup = max(0.0, worker_wall - train_runtime, startup_floor)
    remaining_steps = target_steps - completed_steps
    projected_elapsed = (
        runner_elapsed
        + remaining_steps * elapsed_per_step
        + future_training_worker_starts * startup
        + reserve
    )
    projected_cost = (
        Decimal(str(projected_elapsed)) * limits.usd_per_hour / Decimal(3_600)
    )
    return TimingProjection(
        measured_steps=measured_steps,
        completed_steps=completed_steps,
        target_steps=target_steps,
        measured_train_runtime_seconds=train_runtime,
        measured_worker_wall_seconds=worker_wall,
        elapsed_per_step_seconds=elapsed_per_step,
        observed_worker_startup_seconds=startup,
        runner_elapsed_at_gate_seconds=runner_elapsed,
        remaining_steps=remaining_steps,
        future_training_worker_starts=future_training_worker_starts,
        evaluation_export_reserve_seconds=reserve,
        projected_total_elapsed_seconds=projected_elapsed,
        projected_cost_usd=projected_cost,
        # The runner stops at equality, so a projection must retain positive
        # headroom rather than merely avoid being greater than the caps.
        elapsed_cap_passed=projected_elapsed < limits.max_elapsed_seconds,
        cost_cap_passed=projected_cost < limits.max_cost_usd,
    )


def project_train_phase(
    *,
    phase_elapsed_at_gate_seconds: float,
    completed_steps: int,
    target_steps: int,
    elapsed_per_step_seconds: float,
    future_training_worker_starts: int,
    observed_worker_startup_seconds: float,
    train_phase_timeout_seconds: float,
    in_phase_evaluation_reserve_seconds: float = 0.0,
) -> TrainPhaseProjection:
    """Project only work that executes inside the runner's train phase."""

    phase_elapsed = _positive_number(
        phase_elapsed_at_gate_seconds, "train phase elapsed at gate"
    )
    elapsed_per_step = _positive_number(
        elapsed_per_step_seconds, "elapsed per optimizer step"
    )
    startup = _nonnegative_number(
        observed_worker_startup_seconds, "observed worker startup"
    )
    timeout = _positive_number(train_phase_timeout_seconds, "train phase timeout")
    evaluation_reserve = _nonnegative_number(
        in_phase_evaluation_reserve_seconds, "in-phase evaluation reserve"
    )
    if (
        isinstance(completed_steps, bool)
        or isinstance(target_steps, bool)
        or completed_steps < TIMING_STEPS
        or target_steps <= completed_steps
    ):
        raise ContractError("train phase projection step bounds are inconsistent")
    if (
        isinstance(future_training_worker_starts, bool)
        or future_training_worker_starts < 0
    ):
        raise ContractError("future worker start count must be nonnegative")
    remaining_steps = target_steps - completed_steps
    remaining_wall = (
        remaining_steps * elapsed_per_step
        + future_training_worker_starts * startup
        + evaluation_reserve
    )
    projected_phase_elapsed = phase_elapsed + remaining_wall
    return TrainPhaseProjection(
        phase_elapsed_at_gate_seconds=phase_elapsed,
        remaining_steps=remaining_steps,
        elapsed_per_step_seconds=elapsed_per_step,
        future_training_worker_starts=future_training_worker_starts,
        observed_worker_startup_seconds=startup,
        in_phase_evaluation_reserve_seconds=evaluation_reserve,
        projected_remaining_train_wall_seconds=remaining_wall,
        projected_train_phase_elapsed_seconds=projected_phase_elapsed,
        train_phase_timeout_seconds=timeout,
        remaining_train_phase_budget_seconds=max(0.0, timeout - phase_elapsed),
        passed=projected_phase_elapsed < timeout,
    )


def require_train_phase_within_timeout(projection: TrainPhaseProjection) -> None:
    if not projection.passed:
        raise ContractError(
            "projected training workers exceed the declared train-phase timeout: "
            f"{projection.projected_train_phase_elapsed_seconds:.3f}s >= "
            f"{projection.train_phase_timeout_seconds:.3f}s"
        )


def require_projection_within_caps(projection: TimingProjection) -> None:
    if not projection.passed:
        failed = []
        if not projection.elapsed_cap_passed:
            failed.append("elapsed")
        if not projection.cost_cap_passed:
            failed.append("cost")
        raise ContractError(
            "projected paid run exceeds declared "
            f"{' and '.join(failed)} cap: "
            f"{projection.projected_total_elapsed_seconds:.3f}s, "
            f"${projection.projected_cost_usd}"
        )


def runner_elapsed_from_status(
    status: Mapping[str, object], *, now_unix: float, expected_run_id: str
) -> float:
    """Conservatively age a runner heartbeat to the current wall-clock time."""

    if status.get("protocol") != "run-status/1":
        raise ContractError("runner status protocol must be run-status/1")
    if status.get("run_id") != expected_run_id:
        raise ContractError("runner status run_id does not match the paid request")
    heartbeat_elapsed = _nonnegative_number(
        status.get("heartbeat_monotonic_seconds"),
        "status.heartbeat_monotonic_seconds",
    )
    heartbeat_at = _positive_number(
        status.get("heartbeat_at_unix"), "status.heartbeat_at_unix"
    )
    current_unix = _positive_number(now_unix, "current unix time")
    heartbeat_age = max(0.0, current_unix - heartbeat_at)
    return heartbeat_elapsed + heartbeat_age


def _safe_manifest_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ContractError("checkpoint manifest path is invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ContractError(f"unsafe checkpoint manifest path: {value!r}")
    if path.as_posix() != value:
        raise ContractError(f"checkpoint manifest path is not normalized: {value!r}")
    return value


def verify_checkpoint(checkpoint: Path, expected_step: int) -> CheckpointEvidence:
    """Verify one closed checkpoint against every hash in its completion record."""

    if isinstance(expected_step, bool) or expected_step <= 0:
        raise ContractError("expected checkpoint step must be positive")
    expected_name = f"checkpoint-{expected_step}"
    if checkpoint.name != expected_name:
        raise ContractError(
            f"checkpoint name is {checkpoint.name!r}, expected {expected_name!r}"
        )
    if checkpoint.is_symlink() or not checkpoint.is_dir():
        raise ContractError(f"checkpoint is not a regular directory: {checkpoint}")
    manifest_path = checkpoint / "checkpoint-complete.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ContractError(f"checkpoint completion manifest is absent: {checkpoint}")
    try:
        raw: object = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(
            f"checkpoint completion manifest is invalid: {checkpoint}"
        ) from error
    manifest = _mapping(raw, "checkpoint completion manifest")
    if manifest.get("protocol") != "striatum-checkpoint-completion/1":
        raise ContractError("checkpoint completion protocol is invalid")
    if manifest.get("checkpoint") != expected_name:
        raise ContractError("checkpoint completion record names another checkpoint")
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise ContractError("checkpoint completion record has no files")

    declared_paths: list[str] = []
    declared_bytes = 0
    for index, raw_entry in enumerate(entries):
        entry = _mapping(raw_entry, f"checkpoint file {index}")
        if set(entry) != {"path", "size", "sha256"}:
            raise ContractError(
                "checkpoint file records require path, size, and sha256"
            )
        relative = _safe_manifest_path(entry.get("path"))
        if relative == "checkpoint-complete.json":
            raise ContractError("checkpoint manifest cannot hash itself")
        if relative in declared_paths:
            raise ContractError(f"duplicate checkpoint file record: {relative}")
        size = entry.get("size")
        digest = entry.get("sha256")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ContractError(f"invalid checkpoint size for {relative}")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise ContractError(f"invalid checkpoint sha256 for {relative}")
        path = checkpoint / relative
        if path.is_symlink() or not path.is_file():
            raise ContractError(f"checkpoint file is absent or a symlink: {relative}")
        if path.stat().st_size != size:
            raise ContractError(f"checkpoint size mismatch: {relative}")
        if sha256_file(path) != digest:
            raise ContractError(f"checkpoint sha256 mismatch: {relative}")
        declared_paths.append(relative)
        declared_bytes += size

    actual_paths = []
    for path in sorted(checkpoint.rglob("*")):
        if path.is_symlink():
            raise ContractError(f"checkpoint symlink is forbidden: {path}")
        if path.is_file() and path != manifest_path:
            actual_paths.append(path.relative_to(checkpoint).as_posix())
    if declared_paths != actual_paths:
        raise ContractError("checkpoint completion inventory is not exact and sorted")

    trainer_state_path = checkpoint / "trainer_state.json"
    try:
        trainer_state: object = json.loads(
            trainer_state_path.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(
            f"checkpoint trainer state is invalid: {checkpoint}"
        ) from error
    trainer_state_mapping = _mapping(trainer_state, "checkpoint trainer state")
    global_step = trainer_state_mapping.get("global_step")
    if (
        isinstance(global_step, bool)
        or not isinstance(global_step, int)
        or global_step != expected_step
    ):
        raise ContractError(
            f"checkpoint global_step is {global_step!r}, expected {expected_step}"
        )
    return CheckpointEvidence(
        step=expected_step,
        checkpoint=str(checkpoint.resolve()),
        manifest_sha256=sha256_file(manifest_path),
        files=len(declared_paths),
        bytes=declared_bytes,
    )


def assess_available_gates(
    summary: Mapping[str, object],
    baseline: Mapping[str, object],
    *,
    expected_examples: int,
    expected_selection: Mapping[str, object] | None = None,
) -> dict[str, dict[str, object]]:
    """Recompute the three remotely available evaluation quality gates."""

    if summary.get("protocol") != "striatum-evaluation-result/1":
        raise ContractError("evaluation summary protocol is invalid")
    observed_n = summary.get("n")
    if (
        isinstance(observed_n, bool)
        or not isinstance(observed_n, int)
        or observed_n != expected_examples
    ):
        raise ContractError(
            f"evaluation scored {observed_n!r} examples, expected {expected_examples}"
        )
    if expected_selection is not None:
        observed_selection = _mapping(
            summary.get("selection"), "evaluation selection evidence"
        )
        mismatched = [
            key
            for key, value in expected_selection.items()
            if observed_selection.get(key) != value
        ]
        if mismatched:
            raise ContractError(
                "evaluation selection evidence does not match declared policy: "
                + ", ".join(sorted(mismatched))
            )
    assessment: dict[str, dict[str, object]] = {}
    for metric in AVAILABLE_QUALITY_METRICS:
        actual = _nonnegative_number(summary.get(metric), f"summary.{metric}")
        threshold = _nonnegative_number(baseline.get(metric), f"baseline.{metric}")
        if actual > 1 or threshold > 1:
            raise ContractError(f"quality metric is outside [0, 1]: {metric}")
        assessment[metric] = {
            "actual": actual,
            "must_strictly_beat": threshold,
            "passed": actual > threshold,
        }
    reported = summary.get("available_gates")
    expected_reported = {
        metric: bool(assessment[metric]["passed"])
        for metric in AVAILABLE_QUALITY_METRICS
    }
    if reported != expected_reported:
        raise ContractError(
            "evaluation reported gates disagree with recomputed thresholds"
        )
    return assessment


def require_available_gate_improvement(
    assessment: Mapping[str, Mapping[str, object]],
    *,
    gate_label: str = "checkpoint-25 mini-evaluation",
) -> None:
    failed = [
        metric
        for metric in AVAILABLE_QUALITY_METRICS
        if assessment.get(metric, {}).get("passed") is not True
    ]
    if failed:
        raise ContractError(
            f"{gate_label} did not strictly improve available 35B gates: "
            + ", ".join(failed)
        )


def _read_json_object(path: Path, label: str) -> Mapping[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"{label} is absent or a symlink: {path}")
    try:
        value: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"{label} is invalid JSON: {path}") from error
    return _mapping(value, label)


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _training_result(
    path: Path,
    *,
    expected_step: int,
    expected_strategy: str,
    expected_resumed_from: Path | None,
) -> Mapping[str, object]:
    result = _read_json_object(path, "training result")
    if result.get("protocol") != "striatum-training-result/2":
        raise ContractError("training result protocol is invalid")
    if result.get("strategy") != expected_strategy:
        raise ContractError("training result strategy is invalid")
    step = result.get("global_step")
    if isinstance(step, bool) or not isinstance(step, int) or step != expected_step:
        raise ContractError(
            f"training result global_step is {step!r}, expected {expected_step}"
        )
    expected_resume = (
        str(expected_resumed_from.resolve())
        if expected_resumed_from is not None
        else None
    )
    if result.get("resumed_from") != expected_resume:
        raise ContractError(
            "training result does not prove the requested resume boundary: "
            f"{result.get('resumed_from')!r} != {expected_resume!r}"
        )
    _mapping(result.get("metrics"), "training result metrics")
    preparation = _mapping(
        result.get("base_preparation"), "training result base preparation"
    )
    validate_base_preparation_receipt(preparation)
    if result.get("measurement") != expected_adapter_measurement(
        expected_strategy
    ).to_dict():
        raise ContractError("training result adapter measurement is invalid")
    selection = _mapping(
        result.get("example_selection"), "training result example selection"
    )
    if (
        selection.get("mode") != "all-authorized"
        or selection.get("candidates") != 1_268
    ):
        raise ContractError("training result did not use all authorized examples")
    validate_sft_tokenization_census(selection.get("tokenization"))
    validate_liger_fused_loss_proof(result.get("liger_fused_loss"))
    return result


def _train_runtime(result: Mapping[str, object]) -> float:
    metrics = _mapping(result.get("metrics"), "training result metrics")
    return _positive_number(metrics.get("train_runtime"), "metrics.train_runtime")


def _run_child(command: Sequence[str], label: str) -> float:
    started = time.monotonic()
    try:
        subprocess.run(list(command), check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        if isinstance(error, subprocess.CalledProcessError):
            detail = f"exit {error.returncode}"
        else:
            detail = str(error)
        raise ContractError(
            f"{label} child failed ({detail}): {list(command)!r}"
        ) from error
    return time.monotonic() - started


def _request_path(argument: Path | None) -> Path:
    if argument is not None:
        return argument.resolve()
    environment_value = os.environ.get("RUNPOD_JOBRUNNER_REQUEST_PATH")
    if not environment_value:
        raise ContractError(
            "paid training requires --request or RUNPOD_JOBRUNNER_REQUEST_PATH"
        )
    return Path(environment_value).resolve()


def _runner_elapsed(
    *,
    request: Mapping[str, object],
    phase_started_monotonic: float,
    phase_started_elapsed: float | None,
) -> tuple[float, str]:
    status_dir_value = os.environ.get("RUNPOD_JOBRUNNER_STATUS_DIR")
    local_elapsed = time.monotonic() - phase_started_monotonic
    if phase_started_elapsed is not None:
        local_elapsed += phase_started_elapsed
    if not status_dir_value:
        return max(local_elapsed, sys.float_info.min), "local-train-phase-monotonic"
    status_path = Path(status_dir_value) / "status.json"
    status = _read_json_object(status_path, "runner status")
    run_id = request.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ContractError("paid run request has no run_id")
    heartbeat_elapsed = runner_elapsed_from_status(
        status,
        now_unix=time.time(),
        expected_run_id=run_id,
    )
    return (
        max(heartbeat_elapsed, local_elapsed, sys.float_info.min),
        "runner-status-heartbeat-plus-age",
    )


def _base_train_command(args: argparse.Namespace, checkpoints: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "jobs.qwen35b_moe.train",
        "--strategy",
        args.strategy,
        "--model-dir",
        str(args.model_dir.resolve()),
        "--input-dir",
        str(args.input_dir.resolve()),
        "--output",
        str(checkpoints.resolve()),
        "--seed",
        str(args.seed),
    ]


def _checkpoint_steps(checkpoints: Path) -> list[int]:
    steps = []
    if not checkpoints.is_dir():
        return steps
    for path in checkpoints.iterdir():
        if not path.name.startswith("checkpoint-"):
            continue
        suffix = path.name.removeprefix("checkpoint-")
        if not suffix.isdigit() or int(suffix) <= 0:
            raise ContractError(f"invalid checkpoint directory name: {path.name}")
        steps.append(int(suffix))
    return sorted(steps)


def _verified_checkpoints(
    checkpoints: Path, required: set[int]
) -> list[dict[str, object]]:
    found = _checkpoint_steps(checkpoints)
    missing = sorted(required - set(found))
    if missing:
        raise ContractError(f"required completed checkpoints are missing: {missing}")
    return [
        verify_checkpoint(checkpoints / f"checkpoint-{step}", step).to_dict()
        for step in found
    ]


def _write_receipt(path: Path, receipt: dict[str, object]) -> None:
    receipt["updated_at_unix"] = time.time()
    _atomic_json(path, receipt)


def run(args: argparse.Namespace) -> dict[str, object]:
    request_path = _request_path(args.request)
    request = _read_json_object(request_path, "paid run request")
    limits = limits_from_run_request(request)
    train_phase_timeout = train_timeout_from_run_request(request)
    config = _read_json_object(
        Path(__file__).with_name("training-config.json"), "training configuration"
    )
    train_config = _mapping(config.get("train"), "training configuration train")
    derived_epoch_steps = optimizer_steps_per_epoch(
        train_config.get("expected_examples"),
        train_config.get("per_device_batch_size"),
        train_config.get("gradient_accumulation_steps"),
    )
    if (
        derived_epoch_steps != EPOCH_ONE_CHECKPOINT_STEP
        or train_config.get("expected_steps_per_epoch")
        != EPOCH_ONE_CHECKPOINT_STEP
    ):
        raise ContractError(
            "training configuration must derive and declare epoch one at "
            f"step {EPOCH_ONE_CHECKPOINT_STEP}"
        )
    epochs = train_config.get("epochs")
    if (
        isinstance(epochs, bool)
        or not isinstance(epochs, int)
        or epochs != 2
        or train_config.get("expected_steps") != derived_epoch_steps * epochs
        or train_config.get("expected_steps") != TOTAL_STEPS
    ):
        raise ContractError(
            f"training configuration must declare two epochs and {TOTAL_STEPS} steps"
        )
    quality = _mapping(config.get("quality_gate"), "quality gate")
    baseline = _mapping(quality.get("strictly_beat"), "35B quality baseline")
    mini_policy = _mapping(
        quality.get("checkpoint_25_mini"), "checkpoint-25 mini policy"
    )
    if mini_policy.get("examples") != MINI_EVAL_EXAMPLES:
        raise ContractError(
            f"checkpoint-25 policy must declare {MINI_EVAL_EXAMPLES} examples"
        )
    epoch_one_policy = _mapping(
        quality.get("epoch_one_full"), "epoch-one full evaluation policy"
    )
    if (
        train_config.get("expected_eval_examples") != EPOCH_ONE_EVAL_EXAMPLES
        or epoch_one_policy.get("examples") != EPOCH_ONE_EVAL_EXAMPLES
    ):
        raise ContractError(
            "training and epoch-one policies must both declare "
            f"{EPOCH_ONE_EVAL_EXAMPLES} evaluation examples"
        )

    output_root = args.output.resolve()
    checkpoints = output_root / "checkpoints"
    mini_eval = output_root / "eval/checkpoint-25-mini"
    epoch_one_eval = output_root / "eval/epoch-one-full"
    receipt_path = (
        args.receipt.resolve()
        if args.receipt is not None
        else output_root / "artifacts/train-phase/train-phase.json"
    )
    receipt: dict[str, object] = {
        "protocol": "striatum-paid-training-phase/2",
        "outcome": "running",
        "strategy": args.strategy,
        "request": {
            "path": str(request_path),
            "run_id": request.get("run_id"),
            "bundle_hash": request.get("bundle_hash"),
        },
        "limits": limits.to_dict(),
        "train_phase_timeout_seconds": train_phase_timeout,
        "policy": {
            "timing_steps": TIMING_STEPS,
            "screening_checkpoint_step": SCREENING_CHECKPOINT_STEP,
            "epoch_one_checkpoint_step": EPOCH_ONE_CHECKPOINT_STEP,
            "total_steps": TOTAL_STEPS,
            "checkpoint_interval": CHECKPOINT_INTERVAL,
            "mini_eval_examples": MINI_EVAL_EXAMPLES,
            "epoch_one_eval_examples": EPOCH_ONE_EVAL_EXAMPLES,
            "in_train_evaluation_reserve_seconds": (
                IN_TRAIN_EVALUATION_RESERVE_SECONDS
            ),
            "post_train_evaluation_export_reserve_seconds": (
                POST_TRAIN_EVALUATION_EXPORT_RESERVE_SECONDS
            ),
            "available_quality_metrics": list(AVAILABLE_QUALITY_METRICS),
        },
        "stages": [],
    }
    _write_receipt(receipt_path, receipt)
    phase_started_monotonic = time.monotonic()
    phase_started_elapsed: float | None = None
    try:
        elapsed, elapsed_source = _runner_elapsed(
            request=request,
            phase_started_monotonic=phase_started_monotonic,
            phase_started_elapsed=None,
        )
        phase_started_elapsed = elapsed

        base_train = _base_train_command(args, checkpoints)
        timing_command = [
            *base_train,
            "--max-steps",
            str(TIMING_STEPS),
            "--save-steps",
            str(TIMING_STEPS),
        ]
        timing_wall = _run_child(timing_command, "five-step timing")
        timing_result = _training_result(
            checkpoints / "training-result.json",
            expected_step=TIMING_STEPS,
            expected_strategy=args.strategy,
            expected_resumed_from=None,
        )
        checkpoint_5 = verify_checkpoint(
            checkpoints / f"checkpoint-{TIMING_STEPS}", TIMING_STEPS
        )
        elapsed_at_timing_gate, elapsed_source = _runner_elapsed(
            request=request,
            phase_started_monotonic=phase_started_monotonic,
            phase_started_elapsed=phase_started_elapsed,
        )
        first_projection = project_paid_run(
            limits,
            measured_steps=TIMING_STEPS,
            completed_steps=TIMING_STEPS,
            target_steps=TOTAL_STEPS,
            measured_train_runtime_seconds=_train_runtime(timing_result),
            measured_worker_wall_seconds=timing_wall,
            runner_elapsed_at_gate_seconds=elapsed_at_timing_gate,
            future_training_worker_starts=3,
            evaluation_export_reserve_seconds=(
                IN_TRAIN_EVALUATION_RESERVE_SECONDS
                + POST_TRAIN_EVALUATION_EXPORT_RESERVE_SECONDS
            ),
        )
        first_phase_projection = project_train_phase(
            phase_elapsed_at_gate_seconds=(time.monotonic() - phase_started_monotonic),
            completed_steps=TIMING_STEPS,
            target_steps=TOTAL_STEPS,
            elapsed_per_step_seconds=first_projection.elapsed_per_step_seconds,
            future_training_worker_starts=3,
            observed_worker_startup_seconds=(
                first_projection.observed_worker_startup_seconds
            ),
            train_phase_timeout_seconds=train_phase_timeout,
            in_phase_evaluation_reserve_seconds=(
                IN_TRAIN_EVALUATION_RESERVE_SECONDS
            ),
        )
        receipt["runner_elapsed_source"] = elapsed_source
        receipt["timing_projection"] = first_projection.to_dict()
        receipt["timing_train_phase_projection"] = first_phase_projection.to_dict()
        stages = receipt["stages"]
        assert isinstance(stages, list)
        stages.append(
            {
                "stage": "timing-5",
                "child_wall_seconds": timing_wall,
                "checkpoint": checkpoint_5.to_dict(),
                "global_step": TIMING_STEPS,
                "base_preparation": timing_result["base_preparation"],
                "adapter_measurement": timing_result["measurement"],
            }
        )
        _write_receipt(receipt_path, receipt)
        require_projection_within_caps(first_projection)
        require_train_phase_within_timeout(first_phase_projection)

        checkpoint_5_manifest_digest = checkpoint_5.manifest_sha256
        checkpoint_5_path = checkpoints / f"checkpoint-{TIMING_STEPS}"
        screening_command = [
            *base_train,
            "--max-steps",
            str(SCREENING_CHECKPOINT_STEP),
            "--save-steps",
            str(SCREENING_CHECKPOINT_STEP),
            "--resume-from-checkpoint",
            str(checkpoint_5_path.resolve()),
        ]
        screening_wall = _run_child(screening_command, "checkpoint-25 training")
        screening_result = _training_result(
            checkpoints / "training-result.json",
            expected_step=SCREENING_CHECKPOINT_STEP,
            expected_strategy=args.strategy,
            expected_resumed_from=checkpoint_5_path,
        )
        preserved_checkpoint_5 = verify_checkpoint(checkpoint_5_path, TIMING_STEPS)
        if preserved_checkpoint_5.manifest_sha256 != checkpoint_5_manifest_digest:
            raise ContractError(
                "checkpoint-5 completion manifest changed during resume"
            )
        checkpoint_25_path = checkpoints / f"checkpoint-{SCREENING_CHECKPOINT_STEP}"
        checkpoint_25 = verify_checkpoint(checkpoint_25_path, SCREENING_CHECKPOINT_STEP)
        stages.append(
            {
                "stage": "screening-checkpoint-25",
                "child_wall_seconds": screening_wall,
                "resumed_from": checkpoint_5.to_dict(),
                "checkpoint": checkpoint_25.to_dict(),
                "global_step": SCREENING_CHECKPOINT_STEP,
                "base_preparation": screening_result["base_preparation"],
                "adapter_measurement": screening_result["measurement"],
            }
        )
        _write_receipt(receipt_path, receipt)

        mini_eval_command = [
            sys.executable,
            "-m",
            "jobs.qwen35b_moe.evaluate",
            "--model-dir",
            str(args.model_dir.resolve()),
            "--input-dir",
            str(args.input_dir.resolve()),
            "--adapter",
            str(checkpoint_25_path.resolve()),
            "--output",
            str(mini_eval.resolve()),
            "--limit",
            str(MINI_EVAL_EXAMPLES),
            "--selection",
            "checkpoint-25-mini",
            "--seed",
            str(args.seed),
        ]
        mini_eval_wall = _run_child(mini_eval_command, "checkpoint-25 mini-evaluation")
        mini_summary = _read_json_object(
            mini_eval / "summary.json", "checkpoint-25 mini-evaluation summary"
        )
        assessment = assess_available_gates(
            mini_summary,
            baseline,
            expected_examples=MINI_EVAL_EXAMPLES,
            expected_selection=mini_policy,
        )
        stages.append(
            {
                "stage": "checkpoint-25-mini-evaluation",
                "child_wall_seconds": mini_eval_wall,
                "process_isolation": "distinct-child-after-training-worker-exit",
                "examples": MINI_EVAL_EXAMPLES,
                "available_gates": assessment,
                "summary": str((mini_eval / "summary.json").resolve()),
            }
        )
        receipt["checkpoint_25_gate"] = assessment
        _write_receipt(receipt_path, receipt)
        require_available_gate_improvement(assessment)

        elapsed_before_epoch_one, elapsed_source = _runner_elapsed(
            request=request,
            phase_started_monotonic=phase_started_monotonic,
            phase_started_elapsed=phase_started_elapsed,
        )
        pre_epoch_projection = project_paid_run(
            limits,
            measured_steps=SCREENING_CHECKPOINT_STEP - TIMING_STEPS,
            completed_steps=SCREENING_CHECKPOINT_STEP,
            target_steps=TOTAL_STEPS,
            measured_train_runtime_seconds=_train_runtime(screening_result),
            measured_worker_wall_seconds=screening_wall,
            runner_elapsed_at_gate_seconds=elapsed_before_epoch_one,
            future_training_worker_starts=2,
            evaluation_export_reserve_seconds=(
                IN_TRAIN_EVALUATION_RESERVE_SECONDS
                + POST_TRAIN_EVALUATION_EXPORT_RESERVE_SECONDS
            ),
            elapsed_per_step_floor_seconds=first_projection.elapsed_per_step_seconds,
            worker_startup_floor_seconds=(
                first_projection.observed_worker_startup_seconds
            ),
        )
        pre_epoch_phase_projection = project_train_phase(
            phase_elapsed_at_gate_seconds=(time.monotonic() - phase_started_monotonic),
            completed_steps=SCREENING_CHECKPOINT_STEP,
            target_steps=TOTAL_STEPS,
            elapsed_per_step_seconds=pre_epoch_projection.elapsed_per_step_seconds,
            future_training_worker_starts=2,
            observed_worker_startup_seconds=(
                pre_epoch_projection.observed_worker_startup_seconds
            ),
            train_phase_timeout_seconds=train_phase_timeout,
            in_phase_evaluation_reserve_seconds=(
                IN_TRAIN_EVALUATION_RESERVE_SECONDS
            ),
        )
        receipt["runner_elapsed_source"] = elapsed_source
        receipt["pre_epoch_one_projection"] = pre_epoch_projection.to_dict()
        receipt["pre_epoch_one_train_phase_projection"] = (
            pre_epoch_phase_projection.to_dict()
        )
        _write_receipt(receipt_path, receipt)
        require_projection_within_caps(pre_epoch_projection)
        require_train_phase_within_timeout(pre_epoch_phase_projection)

        checkpoint_25_manifest_digest = checkpoint_25.manifest_sha256
        epoch_one_command = [
            *base_train,
            "--max-steps",
            str(EPOCH_ONE_CHECKPOINT_STEP),
            "--save-steps",
            str(CHECKPOINT_INTERVAL),
            "--save-final-checkpoint",
            "--resume-from-checkpoint",
            str(checkpoint_25_path.resolve()),
        ]
        epoch_one_wall = _run_child(
            epoch_one_command, "epoch-one checkpoint-159 training"
        )
        epoch_one_result = _training_result(
            checkpoints / "training-result.json",
            expected_step=EPOCH_ONE_CHECKPOINT_STEP,
            expected_strategy=args.strategy,
            expected_resumed_from=checkpoint_25_path,
        )
        preserved_checkpoint_25 = verify_checkpoint(
            checkpoint_25_path, SCREENING_CHECKPOINT_STEP
        )
        if preserved_checkpoint_25.manifest_sha256 != checkpoint_25_manifest_digest:
            raise ContractError(
                "checkpoint-25 completion manifest changed during resume"
            )
        checkpoint_159_path = checkpoints / f"checkpoint-{EPOCH_ONE_CHECKPOINT_STEP}"
        checkpoint_159 = verify_checkpoint(
            checkpoint_159_path, EPOCH_ONE_CHECKPOINT_STEP
        )
        stages.append(
            {
                "stage": "epoch-one-checkpoint-159",
                "child_wall_seconds": epoch_one_wall,
                "resumed_from": checkpoint_25.to_dict(),
                "checkpoint": checkpoint_159.to_dict(),
                "global_step": EPOCH_ONE_CHECKPOINT_STEP,
                "base_preparation": epoch_one_result["base_preparation"],
                "adapter_measurement": epoch_one_result["measurement"],
            }
        )
        _write_receipt(receipt_path, receipt)

        epoch_one_eval_command = [
            sys.executable,
            "-m",
            "jobs.qwen35b_moe.evaluate",
            "--model-dir",
            str(args.model_dir.resolve()),
            "--input-dir",
            str(args.input_dir.resolve()),
            "--adapter",
            str(checkpoint_159_path.resolve()),
            "--output",
            str(epoch_one_eval.resolve()),
            "--selection",
            "prefix",
            "--seed",
            str(args.seed),
        ]
        epoch_one_eval_wall = _run_child(
            epoch_one_eval_command, "epoch-one full evaluation"
        )
        epoch_one_summary = _read_json_object(
            epoch_one_eval / "summary.json", "epoch-one full evaluation summary"
        )
        epoch_one_assessment = assess_available_gates(
            epoch_one_summary,
            baseline,
            expected_examples=EPOCH_ONE_EVAL_EXAMPLES,
            expected_selection=epoch_one_policy,
        )
        stages.append(
            {
                "stage": "epoch-one-full-evaluation",
                "child_wall_seconds": epoch_one_eval_wall,
                "process_isolation": "distinct-child-after-training-worker-exit",
                "examples": EPOCH_ONE_EVAL_EXAMPLES,
                "available_gates": epoch_one_assessment,
                "summary": str((epoch_one_eval / "summary.json").resolve()),
            }
        )
        receipt["epoch_one_gate"] = epoch_one_assessment
        _write_receipt(receipt_path, receipt)
        require_available_gate_improvement(
            epoch_one_assessment, gate_label="epoch-one full evaluation"
        )

        elapsed_before_second_epoch, elapsed_source = _runner_elapsed(
            request=request,
            phase_started_monotonic=phase_started_monotonic,
            phase_started_elapsed=phase_started_elapsed,
        )
        pre_second_epoch_projection = project_paid_run(
            limits,
            measured_steps=EPOCH_ONE_CHECKPOINT_STEP - SCREENING_CHECKPOINT_STEP,
            completed_steps=EPOCH_ONE_CHECKPOINT_STEP,
            target_steps=TOTAL_STEPS,
            measured_train_runtime_seconds=_train_runtime(epoch_one_result),
            measured_worker_wall_seconds=epoch_one_wall,
            runner_elapsed_at_gate_seconds=elapsed_before_second_epoch,
            future_training_worker_starts=1,
            evaluation_export_reserve_seconds=(
                POST_TRAIN_EVALUATION_EXPORT_RESERVE_SECONDS
            ),
            elapsed_per_step_floor_seconds=(
                pre_epoch_projection.elapsed_per_step_seconds
            ),
            worker_startup_floor_seconds=(
                pre_epoch_projection.observed_worker_startup_seconds
            ),
        )
        pre_second_epoch_phase_projection = project_train_phase(
            phase_elapsed_at_gate_seconds=(time.monotonic() - phase_started_monotonic),
            completed_steps=EPOCH_ONE_CHECKPOINT_STEP,
            target_steps=TOTAL_STEPS,
            elapsed_per_step_seconds=(
                pre_second_epoch_projection.elapsed_per_step_seconds
            ),
            future_training_worker_starts=1,
            observed_worker_startup_seconds=(
                pre_second_epoch_projection.observed_worker_startup_seconds
            ),
            train_phase_timeout_seconds=train_phase_timeout,
        )
        receipt["runner_elapsed_source"] = elapsed_source
        receipt["pre_second_epoch_projection"] = (
            pre_second_epoch_projection.to_dict()
        )
        receipt["pre_second_epoch_train_phase_projection"] = (
            pre_second_epoch_phase_projection.to_dict()
        )
        _write_receipt(receipt_path, receipt)
        require_projection_within_caps(pre_second_epoch_projection)
        require_train_phase_within_timeout(pre_second_epoch_phase_projection)

        checkpoint_159_manifest_digest = checkpoint_159.manifest_sha256
        full_command = [
            *base_train,
            "--max-steps",
            str(TOTAL_STEPS),
            "--save-steps",
            str(CHECKPOINT_INTERVAL),
            "--save-final-checkpoint",
            "--resume-from-checkpoint",
            str(checkpoint_159_path.resolve()),
        ]
        full_wall = _run_child(full_command, "second-epoch training continuation")
        final_result = _training_result(
            checkpoints / "training-result.json",
            expected_step=TOTAL_STEPS,
            expected_strategy=args.strategy,
            expected_resumed_from=checkpoint_159_path,
        )
        preserved_checkpoint_159 = verify_checkpoint(
            checkpoint_159_path, EPOCH_ONE_CHECKPOINT_STEP
        )
        if preserved_checkpoint_159.manifest_sha256 != checkpoint_159_manifest_digest:
            raise ContractError(
                "checkpoint-159 completion manifest changed during resume"
            )
        final_adapter = checkpoints / "final-adapter"
        for name in ("adapter_config.json", "adapter_model.safetensors"):
            path = final_adapter / name
            if path.is_symlink() or not path.is_file():
                raise ContractError(
                    f"final adapter file is absent or a symlink: {path}"
                )
        required_steps = {
            TIMING_STEPS,
            SCREENING_CHECKPOINT_STEP,
            EPOCH_ONE_CHECKPOINT_STEP,
            TOTAL_STEPS,
        }
        required_steps.update(range(50, TOTAL_STEPS + 1, CHECKPOINT_INTERVAL))
        checkpoint_evidence = _verified_checkpoints(checkpoints, required_steps)
        stages.append(
            {
                "stage": "second-epoch-318",
                "child_wall_seconds": full_wall,
                "resumed_from": checkpoint_159.to_dict(),
                "global_step": final_result["global_step"],
                "base_preparation": final_result["base_preparation"],
                "adapter_measurement": final_result["measurement"],
                "final_adapter": str(final_adapter.resolve()),
            }
        )
        receipt["checkpoints"] = checkpoint_evidence
        receipt["outcome"] = "training-completed-full-evaluation-pending"
        receipt["full_evaluation"] = "separate-evaluate-job-phase"
        _write_receipt(receipt_path, receipt)
        return receipt
    except Exception as error:
        receipt["outcome"] = "blocked"
        receipt["blocked_reason"] = f"{type(error).__name__}: {error}"
        _write_receipt(receipt_path, receipt)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=STRATEGIES, default="linear-only")
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--input-dir", type=Path, default=input_dir_from_env())
    parser.add_argument("--output", type=Path, default=output_dir_from_env())
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    print(json.dumps(run(parse_args()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
