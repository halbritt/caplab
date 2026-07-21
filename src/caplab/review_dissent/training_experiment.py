"""Fail-closed loader for the preregistered local-Qwen training experiment."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class TrainingExperimentContractError(ValueError):
    """The frozen training experiment is incomplete or has drifted."""


_EXPERIMENT_AUTHORITIES = {
    "caplab-review-dissent-qwen27b-qlora-r1": "adr-0049",
    "caplab-review-dissent-qwen27b-qlora-r2": "adr-0053",
}


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
    experiment_id = manifest.get("experiment_id")
    if manifest.get("authority") != _EXPERIMENT_AUTHORITIES.get(experiment_id):
        raise TrainingExperimentContractError("preregistration_authority_mismatch")

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

    if experiment_id == "caplab-review-dissent-qwen27b-qlora-r2":
        qualification = manifest.get("host_qualification", {})
        if qualification != {
            "no_update_seconds": 60,
            "distinct_fleet_heartbeats_min": 4,
            "remote_pulse_interval_seconds": 5,
            "remote_pulse_ttl_seconds": 45,
            "process_containment": "windows-job-object-kill-on-close",
            "host_boot_identity_must_remain_constant": True,
            "training_starts_only_after_qualification": True,
        }:
            raise TrainingExperimentContractError("host_qualification_mismatch")

    return manifest


def load_training_execution(
    authorization_path: Path,
    repository_root: Path,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate the exact execution authority without performing an effect."""
    authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
    schema = authorization.get("schema")
    if schema not in {
        "caplab.training.execution-authorization/v1",
        "caplab.training.execution-authorization/v2",
        "caplab.training.execution-authorization/v3",
    }:
        raise TrainingExperimentContractError("execution_schema_mismatch")
    expected_authority = {
        "caplab.training.execution-authorization/v1": "adr-0050",
        "caplab.training.execution-authorization/v2": "adr-0054",
        "caplab.training.execution-authorization/v3": "adr-0055",
    }[schema]
    if (
        authorization.get("status") != "active"
        or authorization.get("authority") != expected_authority
    ):
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
    if host.get("name") != "peecee" or host.get("gpu_fleet_model") != "marker" or host.get("gpu_fleet_slot") != 1:
        raise TrainingExperimentContractError("execution_host_binding_mismatch")
    effects = authorization.get("permitted_effects", {})
    if schema == "caplab.training.execution-authorization/v1":
        if (
            effects.get("training_attempts") != 1
            or effects.get("heldout_primary_calls") != 16
            or effects.get("general_control_calls") != 8
            or effects.get("paid_usd") != "0"
            or effects.get("stop_ollama_service") is not False
            or effects.get("striatum_mutation") is not False
        ):
            raise TrainingExperimentContractError("execution_effect_boundary_mismatch")
    else:
        if authorization.get("experiment_id") != "caplab-review-dissent-qwen27b-qlora-r2":
            raise TrainingExperimentContractError("retry_experiment_mismatch")
        expected_containment = {
            "windows_process_tree": "job-object-kill-on-close",
            "remote_pulse_schema": "caplab.training.remote-pulse/v1",
            "remote_pulse_interval_seconds": 5,
            "remote_pulse_ttl_seconds": 45,
            "fleet_observation_interval_seconds": 5,
            "distinct_fleet_heartbeats_min": 4,
            "host_boot_identity_must_remain_constant": True,
            "training_requires_qualification_acceptance": True,
        }
        if authorization.get("containment") != expected_containment:
            raise TrainingExperimentContractError("retry_containment_mismatch")
        if schema == "caplab.training.execution-authorization/v3":
            predecessor = authorization.get("predecessor", {})
            if predecessor != {
                "path": "docs/product/training/caplab-review-dissent-local-qwen-r2/training-execution.json",
                "file_sha256": "0c095d5c58732678c151ad31b6874736a5f559d79d70d30894175b77d4f31d3c",
                "outcome": "qualification-launch-refused-before-model-load",
            }:
                raise TrainingExperimentContractError("retry_predecessor_mismatch")
            predecessor_path = repository_root / predecessor["path"]
            if _sha256(predecessor_path) != predecessor["file_sha256"]:
                raise TrainingExperimentContractError("retry_predecessor_sha256_mismatch")
            if authorization.get("launch_correction") != {
                "powershell_execution_policy": "Bypass",
                "scope": "child-process-only",
                "host_policy_mutation": False,
            }:
                raise TrainingExperimentContractError("retry_launch_correction_mismatch")
            if authorization.get("remote_paths", {}).get("root") != (
                "C:/Users/halbr/caplab/experiments/"
                "caplab-review-dissent-qwen27b-qlora-r2-q2"
            ):
                raise TrainingExperimentContractError("retry_remote_root_mismatch")
        expected_effects = {
            "gpu_fleet_leases": 2,
            "temporary_ollama_model_unload": "qwen3.6:27b",
            "stop_ollama_service": False,
            "reuse_existing_environment": True,
            "install_packages": False,
            "reuse_checkpoint_cache": True,
            "download_checkpoint": False,
            "host_qualification_runs": 1,
            "training_attempts": 1,
            "heldout_reads_after_adapter_seal": 1,
            "heldout_primary_calls": 16,
            "general_control_calls": 8,
            "infrastructure_replacements_max": 2,
            "transient_eval_servers": 1,
            "eval_server_port": 18081,
            "paid_usd": "0",
            "external_telemetry": False,
            "checkpoint_deployment": False,
            "striatum_mutation": False,
            "scheduler_policy_mutation": False,
        }
        if effects != expected_effects:
            raise TrainingExperimentContractError("execution_effect_boundary_mismatch")
    result = dict(authorization)
    result["_experiment"] = experiment
    return result
