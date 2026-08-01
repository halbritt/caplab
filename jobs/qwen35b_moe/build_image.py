"""Build or publish the controller-matched worker image and print its digest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Mapping

import yaml

from .contract import ContractError
from .volume_assets import (
    ASSET_BYTES,
    ASSET_FILES,
    ASSET_MANIFEST_SHA256,
    _manifest_entries,
)


def _run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, text=True, **kwargs)
    except subprocess.CalledProcessError as error:
        raise ContractError(
            f"image command failed with exit {error.returncode}: {command!r}"
        ) from error


def _write_receipt(path: Path, receipt: Mapping[str, object]) -> None:
    """Durably publish one build receipt without exposing a partial JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(receipt, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def _asset_manifest_receipt(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ContractError("network-volume asset manifest is missing or linked")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != ASSET_MANIFEST_SHA256:
        raise ContractError("network-volume asset manifest hash mismatch")
    if len(_manifest_entries(path)) != ASSET_FILES:
        raise ContractError("network-volume asset manifest file count mismatch")
    return {
        "manifest_sha256": digest,
        "files": ASSET_FILES,
        "bytes": ASSET_BYTES,
    }


def _validate_jobrunner_release(
    release: Mapping[str, object], job_spec: Mapping[str, object]
) -> Mapping[str, object]:
    if release.get("protocol") != "runner-release/1":
        raise ContractError("jobrunner image has an unsupported release receipt")
    runner = job_spec.get("runner")
    if not isinstance(runner, Mapping):
        raise ContractError("job spec runner contract is missing")
    if release.get("runner_version") != runner.get("version"):
        raise ContractError(
            "jobrunner image runner version does not match the job spec"
        )
    if release.get("runner_git_commit") != runner.get("git_commit"):
        raise ContractError(
            "jobrunner image runner git commit does not match the job spec"
        )
    protocols = release.get("supported_protocol_majors")
    if not isinstance(protocols, Mapping) or protocols.get("run-request") != [1]:
        raise ContractError("jobrunner image does not support run-request/1")
    return release


def _inspect_jobrunner_release(
    image: str, job_spec: Mapping[str, object]
) -> Mapping[str, object]:
    raw = _run(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "/bin/cat",
            image,
            "/opt/runpod-jobrunner/release.json",
        ],
        capture_output=True,
    ).stdout
    try:
        release = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ContractError("jobrunner image release receipt is not JSON") from error
    if not isinstance(release, Mapping):
        raise ContractError("jobrunner image release receipt must be an object")
    return _validate_jobrunner_release(release, job_spec)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="registry repository without a tag")
    parser.add_argument("version", help="exact semantic version")
    parser.add_argument(
        "--jobrunner-image",
        required=True,
        help="published runpod-jobrunner image in repository@sha256:digest form",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        required=True,
        help="path for the atomic machine-readable build admission receipt",
    )
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.version):
        raise ContractError("version must be an exact semantic version")
    if not re.fullmatch(r"[^@\s]+@sha256:[0-9a-f]{64}", args.jobrunner_image):
        raise ContractError("jobrunner image must use one immutable sha256 digest")
    job_root = Path(__file__).resolve().parent
    job_spec = yaml.safe_load((job_root / "job.yaml").read_text())
    if not isinstance(job_spec, Mapping):
        raise ContractError("job spec must be an object")
    jobrunner_release = _inspect_jobrunner_release(args.jobrunner_image, job_spec)
    asset_manifest = _asset_manifest_receipt(
        job_root / "network-volume-assets.sha256"
    )
    repository = job_root.parents[1]
    job_pathspec = job_root.relative_to(repository).as_posix()
    if _run(
        ["git", "-C", str(repository), "status", "--porcelain", "--", job_pathspec],
        capture_output=True,
    ).stdout.strip():
        raise ContractError("Qwen job source must be committed before image build")
    source_commit = _run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"], capture_output=True
    ).stdout.strip()
    tag = f"{args.image}:{args.version}"
    command = [
        "docker",
        "buildx",
        "build",
        "--platform",
        "linux/amd64",
        "--file",
        str(job_root / "Dockerfile"),
        "--build-arg",
        f"RUNPOD_JOBRUNNER_IMAGE={args.jobrunner_image}",
        "--label",
        f"org.opencontainers.image.revision={source_commit}",
        "--label",
        f"org.opencontainers.image.base.name={args.jobrunner_image}",
        "--tag",
        tag,
    ]
    if args.push:
        command.extend(["--push", "--provenance=mode=max", "--sbom=true"])
    else:
        command.append("--load")
    command.append(str(job_root))
    _run(command)
    receipt = {
        "protocol": "striatum-worker-image-build/2",
        "image": tag,
        "source_commit": source_commit,
        "jobrunner_image": args.jobrunner_image,
        "jobrunner_release": jobrunner_release,
        "network_volume_assets": asset_manifest,
        "pushed": args.push,
    }
    if args.push:
        raw = _run(
            [
                "docker",
                "buildx",
                "imagetools",
                "inspect",
                tag,
                "--format",
                "{{json .Manifest}}",
            ],
            capture_output=True,
        ).stdout
        manifest = json.loads(raw)
        receipt["digest"] = manifest["digest"]
        receipt["immutable_image"] = f"{args.image}@{manifest['digest']}"
    _write_receipt(args.receipt.resolve(), receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
