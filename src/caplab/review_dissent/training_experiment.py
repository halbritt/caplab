"""Fail-closed loader for the preregistered local-Qwen training experiment."""

from __future__ import annotations

import hashlib
import json
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
