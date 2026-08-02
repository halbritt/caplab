"""Create a generated bundle with copied, hash-verified SFT inputs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from .contract import (
    ContractError,
    load_input_manifest,
    sha256_file,
    verify_input_tree,
)
from .gate_acceptance import validate_gate3_acceptance


JOB_ROOT = Path(__file__).resolve().parent
PROFILES = (
    "full",
    "preflight-only",
    "hopper-dense-smoke",
    "hopper-moe-smoke",
)
PREFLIGHT_MAX_ELAPSED_SECONDS = 2_700


def _render_job(profile: str) -> str:
    if profile not in PROFILES:
        raise ContractError(f"unknown materialization profile: {profile}")
    template = (JOB_ROOT / "job.yaml").read_text()
    if profile == "full":
        return template
    try:
        import yaml
    except ImportError as error:
        raise ContractError(
            "PyYAML is required for preflight materialization"
        ) from error
    spec = yaml.safe_load(template)
    if not isinstance(spec, dict):
        raise ContractError("job template is not an object")
    if profile == "preflight-only":
        spec["name"] = "striatum-qwen36-35b-a3b-preflight"
        spec["phases"]["verify"]["argv"] = [
            "/opt/striatum-qwen35b/bin/verify"
        ]
    else:
        dense = profile == "hopper-dense-smoke"
        spec["name"] = (
            "striatum-qwen35-08b-hopper-smoke"
            if dense
            else "striatum-qwen36-35b-a3b-moe-smoke"
        )
        config_name = "training-config.json" if dense else "moe-training-config.json"
        model_dir = (
            "/workspace/models/Qwen3.5-0.8B-2fc06364"
            if dense
            else "/workspace/models/Qwen3.6-35B-A3B-995ad96e"
        )
        spec["phases"]["verify"]["enabled"] = False
        spec["phases"]["preflight"]["enabled"] = True
        spec["phases"]["preflight"]["argv"] = [
            "/opt/striatum-qwen35b/bin/preflight",
            "--config",
            f"/opt/striatum-qwen35b/jobs/qwen35b_moe/smoke/{config_name}",
            "--model-dir",
            model_dir,
            "--strategy",
            "linear-only",
            "--check-hopper-kernels",
            "--run-smoke",
        ]
        spec["phases"]["preflight"]["timeout_seconds"] = 2_400
        spec["phases"]["train"]["enabled"] = False
        spec["phases"]["evaluate"]["enabled"] = False
        spec["phases"]["package"]["argv"] = [
            "/opt/striatum-qwen35b/bin/package-smoke",
            "--config",
            f"/opt/striatum-qwen35b/jobs/qwen35b_moe/smoke/{config_name}",
        ]
        spec["phases"]["package"]["timeout_seconds"] = 60
        spec["artifacts"]["incremental_manifest_glob"] = (
            "artifacts/preflight/training/checkpoint-*/checkpoint-complete.json"
        )
        spec["artifacts"]["incremental_mirror_ack"]["timeout_seconds"] = 120
        spec["limits"]["max_elapsed_seconds"] = 3_600
        spec["limits"]["max_cost_usd"] = "3.50" if dense else "5.00"
        return yaml.safe_dump(spec, sort_keys=False)
    phases = spec["phases"]
    phases["preflight"]["enabled"] = True
    phases["preflight"]["timeout_seconds"] = 900
    phases["train"]["enabled"] = False
    phases["evaluate"]["enabled"] = False
    phases["package"]["argv"] = [
        "/opt/striatum-qwen35b/bin/package",
        "--preflight-only",
    ]
    phases["package"]["timeout_seconds"] = 45
    spec["limits"]["max_elapsed_seconds"] = PREFLIGHT_MAX_ELAPSED_SECONDS
    spec["limits"]["max_cost_usd"] = "3.50"
    artifacts = spec["artifacts"]
    artifacts["incremental_manifest_glob"] = (
        "artifacts/preflight/one-step/checkpoint-*/checkpoint-complete.json"
    )
    artifacts["incremental_mirror_ack"]["timeout_seconds"] = 120
    return yaml.safe_dump(spec, sort_keys=False)


def materialize(
    source_repo: Path,
    destination: Path,
    profile: str = "full",
    gate3_acceptance: Path | None = None,
) -> Path:
    if destination.exists() or destination.is_symlink():
        raise ContractError(f"destination already exists: {destination}")
    smoke_profile = profile in {"hopper-dense-smoke", "hopper-moe-smoke"}
    manifest_path = (
        JOB_ROOT / "smoke/input-manifest.json"
        if smoke_profile
        else JOB_ROOT / "input-manifest.json"
    )
    entries = load_input_manifest(
        manifest_path, strict_production=not smoke_profile
    )
    acceptance = None
    if profile == "full":
        if gate3_acceptance is None:
            raise ContractError("full materialization requires a Gate 3 acceptance receipt")
        acceptance = validate_gate3_acceptance(gate3_acceptance.resolve())
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    try:
        (staging / "job.yaml").write_text(_render_job(profile))
        shutil.copytree(JOB_ROOT / "bin", staging / "bin", symlinks=False)
        input_root = staging / "inputs"
        for entry in entries:
            source = (
                JOB_ROOT / "smoke/inputs" / entry.path
                if smoke_profile
                else source_repo / entry.path
            )
            if not source.is_file() or source.is_symlink():
                raise ContractError(
                    f"source is missing, not regular, or a symlink: {source}"
                )
            target = input_root / entry.path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target, follow_symlinks=False)
        rendered_manifest = json.loads(manifest_path.read_text())
        if acceptance is not None:
            assert gate3_acceptance is not None
            acceptance_target = input_root / "control/gate3-acceptance.json"
            acceptance_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(
                gate3_acceptance.resolve(), acceptance_target, follow_symlinks=False
            )
            rendered_manifest["files"].append(
                {
                    "path": "control/gate3-acceptance.json",
                    "size": acceptance_target.stat().st_size,
                    "sha256": sha256_file(acceptance_target),
                }
            )
        (staging / "input-manifest.json").write_text(
            json.dumps(rendered_manifest, indent=2, sort_keys=True) + "\n"
        )
        rendered_entries = load_input_manifest(
            staging / "input-manifest.json", strict_production=False
        )
        verify_input_tree(input_root, rendered_entries)
        (staging / "bundle-metadata.json").write_text(
            json.dumps(
                {
                    "protocol": "striatum-job-materialization/1",
                    "profile": profile,
                    "input_files": len(entries),
                    "input_bytes": sum(entry.size for entry in entries),
                    "image_digest_pinned": False,
                    **(
                        {
                            "gate3_acceptance_sha256": sha256_file(
                                input_root / "control/gate3-acceptance.json"
                            ),
                            "gate3_image_digest": acceptance["image_digest"],
                        }
                        if acceptance is not None
                        else {}
                    ),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        os.replace(staging, destination)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--profile", choices=PROFILES, default="full")
    parser.add_argument("--gate3-acceptance", type=Path)
    args = parser.parse_args()
    print(
        materialize(
            args.source_repo.resolve(),
            args.destination.resolve(),
            args.profile,
            args.gate3_acceptance,
        )
    )


if __name__ == "__main__":
    main()
