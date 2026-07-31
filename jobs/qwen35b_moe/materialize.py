"""Create a generated bundle with copied, hash-verified SFT inputs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from .contract import ContractError, load_input_manifest, verify_input_tree


JOB_ROOT = Path(__file__).resolve().parent
PROFILES = ("full", "preflight-only")


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
    spec["name"] = "striatum-qwen36-35b-a3b-preflight"
    phases = spec["phases"]
    phases["verify"]["timeout_seconds"] = 60
    phases["preflight"]["timeout_seconds"] = 480
    phases["train"]["enabled"] = False
    phases["evaluate"]["enabled"] = False
    phases["package"]["argv"] = [
        "/opt/striatum-qwen35b/bin/package",
        "--preflight-only",
    ]
    phases["package"]["timeout_seconds"] = 60
    spec["limits"]["max_elapsed_seconds"] = 600
    spec["limits"]["max_cost_usd"] = "2.00"
    spec["artifacts"].pop("incremental_manifest_glob", None)
    spec["artifacts"].pop("incremental_mirror_ack", None)
    return yaml.safe_dump(spec, sort_keys=False)


def materialize(source_repo: Path, destination: Path, profile: str = "full") -> Path:
    if destination.exists() or destination.is_symlink():
        raise ContractError(f"destination already exists: {destination}")
    entries = load_input_manifest(JOB_ROOT / "input-manifest.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    try:
        (staging / "job.yaml").write_text(_render_job(profile))
        shutil.copy2(JOB_ROOT / "input-manifest.json", staging / "input-manifest.json")
        shutil.copytree(JOB_ROOT / "bin", staging / "bin", symlinks=False)
        input_root = staging / "inputs"
        for entry in entries:
            source = source_repo / entry.path
            if not source.is_file() or source.is_symlink():
                raise ContractError(
                    f"source is missing, not regular, or a symlink: {source}"
                )
            target = input_root / entry.path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target, follow_symlinks=False)
        verify_input_tree(input_root, entries)
        (staging / "bundle-metadata.json").write_text(
            json.dumps(
                {
                    "protocol": "striatum-job-materialization/1",
                    "profile": profile,
                    "input_files": len(entries),
                    "input_bytes": sum(entry.size for entry in entries),
                    "image_digest_pinned": False,
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
    args = parser.parse_args()
    print(
        materialize(
            args.source_repo.resolve(), args.destination.resolve(), args.profile
        )
    )


if __name__ == "__main__":
    main()
