"""Fail-closed loader for the preregistered local-Qwen training experiment."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class TrainingExperimentContractError(ValueError):
    """The frozen training experiment is incomplete or has drifted."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_training_experiment(manifest_path: Path, repository_root: Path) -> dict[str, Any]:
    """Validate executable preregistration inputs without opening held-out bytes."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "caplab.training.experiment-preregistration/v1":
        raise TrainingExperimentContractError("experiment_schema_mismatch")
    if manifest.get("status") != "preregistered-zero-execution-authority":
        raise TrainingExperimentContractError("experiment_status_mismatch")

    authorization = manifest.get("authorization")
    expected_authorization = {
        "downloads": 0,
        "installations": 0,
        "training_attempts": 0,
        "evaluation_calls": 0,
        "heldout_reads": 0,
        "server_mutation": False,
        "deployment": False,
        "policy_change": False,
    }
    if authorization != expected_authorization:
        raise TrainingExperimentContractError("execution_authority_not_zero")

    for section, path_key, hash_key in (
        ("training_data", "path", "file_sha256"),
        ("evaluation", "general_controls_path", "general_controls_sha256"),
    ):
        binding = manifest.get(section)
        if not isinstance(binding, dict):
            raise TrainingExperimentContractError(f"{section}_missing")
        relative = binding.get(path_key)
        expected = binding.get(hash_key)
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise TrainingExperimentContractError(f"{section}_binding_invalid")
        candidate = (repository_root / relative).resolve()
        try:
            candidate.relative_to(repository_root.resolve())
        except ValueError as error:
            raise TrainingExperimentContractError(f"{section}_path_escape") from error
        if _sha256(candidate) != expected:
            raise TrainingExperimentContractError(f"{section}_sha256_mismatch")

    if manifest["training_data"].get("family") != "RD-D01":
        raise TrainingExperimentContractError("training_family_mismatch")
    if manifest["evaluation"].get("heldout_families") != ["RD-H01", "RD-H02"]:
        raise TrainingExperimentContractError("heldout_family_mismatch")
    if manifest["evaluation"].get("native_harness") != "striatum-openai-lane":
        raise TrainingExperimentContractError("native_harness_mismatch")

    return manifest


def load_training_execution(
    authorization_path: Path,
    repository_root: Path,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate the exact execution authority without performing an effect."""
    authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
    if authorization.get("schema") != "caplab.training.execution-authorization/v1":
        raise TrainingExperimentContractError("execution_schema_mismatch")
    if authorization.get("status") != "active" or authorization.get("authority") != "adr-0050":
        raise TrainingExperimentContractError("execution_not_authorized")
    expiry = datetime.fromisoformat(authorization["expires_at"].replace("Z", "+00:00"))
    if (now or datetime.now(UTC)) > expiry:
        raise TrainingExperimentContractError("execution_authorization_expired")

    bindings = [authorization["preregistration"], *authorization["sources"].values()]
    for binding in bindings:
        relative = binding.get("path")
        expected = binding.get("file_sha256", binding.get("sha256"))
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise TrainingExperimentContractError("execution_source_binding_invalid")
        candidate = (repository_root / relative).resolve()
        try:
            candidate.relative_to(repository_root.resolve())
        except ValueError as error:
            raise TrainingExperimentContractError("execution_source_path_escape") from error
        if _sha256(candidate) != expected:
            raise TrainingExperimentContractError(f"execution_source_sha256_mismatch:{relative}")

    preregistration_path = repository_root / authorization["preregistration"]["path"]
    experiment = load_training_experiment(preregistration_path, repository_root)
    host = authorization.get("host", {})
    if (
        host.get("name") != "peecee"
        or host.get("gpu_fleet_model") != "marker"
        or host.get("gpu_fleet_slot") != 1
    ):
        raise TrainingExperimentContractError("execution_host_binding_mismatch")
    effects = authorization.get("permitted_effects", {})
    if (
        effects.get("training_attempts") != 1
        or effects.get("heldout_primary_calls") != 16
        or effects.get("general_control_calls") != 8
        or effects.get("paid_usd") != "0"
        or effects.get("stop_ollama_service") is not False
        or effects.get("striatum_mutation") is not False
    ):
        raise TrainingExperimentContractError("execution_effect_boundary_mismatch")
    result = dict(authorization)
    result["_experiment"] = experiment
    return result
