"""Build or publish the controller-matched worker image and print its digest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="registry repository without a tag")
    parser.add_argument("version", help="exact semantic version")
    parser.add_argument(
        "--jobrunner-image",
        required=True,
        help="published runpod-jobrunner image in repository@sha256:digest form",
    )
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.version):
        raise ContractError("version must be an exact semantic version")
    if not re.fullmatch(r"[^@\s]+@sha256:[0-9a-f]{64}", args.jobrunner_image):
        raise ContractError("jobrunner image must use one immutable sha256 digest")
    job_root = Path(__file__).resolve().parent
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
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
