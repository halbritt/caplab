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

from .base_gguf import BaseGgufArtifacts, validate_base_gguf_artifacts
from .census import census_snapshot
from .contract import ContractError


MODEL_DIRECTORY_NAME = "Qwen3.6-35B-A3B-995ad96e"
MODEL_LICENSE_SHA256 = (
    "50cbab8a892c5f2993b8c7351a99182507472def3b1374558308605d99b86b32"
)
MODEL_CARD_SHA256 = (
    "c4ddaa065649ff6352648f64747a16eda31726f3e34add94ce04abb461c77b75"
)
MODEL_METADATA = (
    "LICENSE",
    "README.md",
    "config.json",
    "configuration.json",
    "generation_config.json",
    "preprocessor_config.json",
    "video_preprocessor_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
    "chat_template.jinja",
    "model.safetensors.index.json",
    "snapshot-revision.txt",
    "base-bf16.receipt.json",
    "base-bf16.split-receipt.json",
)


def _run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, text=True, **kwargs)
    except subprocess.CalledProcessError as error:
        raise ContractError(
            f"image command failed with exit {error.returncode}: {command!r}"
        ) from error


def _render_dockerfile(job_root: Path, artifacts: BaseGgufArtifacts) -> str:
    template = (job_root / "Dockerfile").read_text()
    marker = "# __BASE_GGUF_SHARD_COPIES__"
    if template.count(marker) != 1:
        raise ContractError("Dockerfile must contain exactly one GGUF shard marker")
    destination = f"/opt/models/{MODEL_DIRECTORY_NAME}/"
    copies = "\n".join(
        f"COPY --from=model-snapshot /{shard.name} {destination}"
        for shard in artifacts.shards
    )
    return template.replace(marker, copies)


def _stage_model_context(
    source: Path,
    destination: Path,
    artifacts: BaseGgufArtifacts,
    *,
    expected_license_sha256: str = MODEL_LICENSE_SHA256,
    expected_model_card_sha256: str = MODEL_CARD_SHA256,
) -> None:
    destination.mkdir()
    selected = [source / name for name in MODEL_METADATA]
    selected.extend(sorted(source.glob("model-*-of-*.safetensors")))
    selected.extend(artifacts.shards)
    if len(selected) != len(MODEL_METADATA) + 26 + len(artifacts.shards):
        raise ContractError("model image context has an unexpected weight shard count")
    for path in selected:
        if path.is_symlink() or not path.is_file():
            raise ContractError(f"model image input is not a regular file: {path}")
        target = destination / path.name
        if target.exists():
            raise ContractError(f"duplicate model image input: {path.name}")
        os.link(path, target)
    if (
        hashlib.sha256((destination / "LICENSE").read_bytes()).hexdigest()
        != expected_license_sha256
    ):
        raise ContractError("model license does not match the pinned snapshot")
    if (
        hashlib.sha256((destination / "README.md").read_bytes()).hexdigest()
        != expected_model_card_sha256
    ):
        raise ContractError("model card does not match the pinned snapshot")


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
        "--model-snapshot",
        type=Path,
        required=True,
        help="exact Qwen snapshot directory used as a named BuildKit context",
    )
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.version):
        raise ContractError("version must be an exact semantic version")
    if not re.fullmatch(r"[^@\s]+@sha256:[0-9a-f]{64}", args.jobrunner_image):
        raise ContractError("jobrunner image must use one immutable sha256 digest")
    model_snapshot = args.model_snapshot.resolve()
    if model_snapshot.name != MODEL_DIRECTORY_NAME:
        raise ContractError("model snapshot directory has an unexpected name")
    if any(
        part in {"sft", "corpus"}
        for path in model_snapshot.rglob("*")
        for part in path.parts
    ):
        raise ContractError(
            "model snapshot context contains forbidden SFT or corpus paths"
        )
    census = census_snapshot(model_snapshot)
    base_gguf = validate_base_gguf_artifacts(model_snapshot)

    job_root = Path(__file__).resolve().parent
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
    with tempfile.TemporaryDirectory(
        prefix=".striatum-image-context-", dir=model_snapshot.parent
    ) as temporary:
        temporary_root = Path(temporary)
        staged_model = temporary_root / "model-snapshot"
        _stage_model_context(model_snapshot, staged_model, base_gguf)
        rendered_dockerfile = temporary_root / "Dockerfile"
        rendered_dockerfile.write_text(_render_dockerfile(job_root, base_gguf))
        command = [
            "docker",
            "buildx",
            "build",
            "--platform",
            "linux/amd64",
            "--file",
            str(rendered_dockerfile),
            "--build-arg",
            f"RUNPOD_JOBRUNNER_IMAGE={args.jobrunner_image}",
            "--build-arg",
            f"BASE_GGUF_FIRST_SHARD={base_gguf.first_shard.name}",
            "--build-context",
            f"model-snapshot={staged_model}",
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
        "protocol": "striatum-worker-image-build/1",
        "image": tag,
        "source_commit": source_commit,
        "jobrunner_image": args.jobrunner_image,
        "model_snapshot": {
            "revision": census["model"]["revision"],
            "shards": census["snapshot"]["shards"],
            "tensor_bytes": census["snapshot"]["tensor_bytes"],
            "license": "Apache-2.0",
            "license_sha256": MODEL_LICENSE_SHA256,
            "model_card_sha256": MODEL_CARD_SHA256,
        },
        "base_gguf": {
            "source_size": base_gguf.source_receipt["size"],
            "source_sha256": base_gguf.source_receipt["sha256"],
            "first_shard": base_gguf.first_shard.name,
            "shards": len(base_gguf.shards),
            "split_receipt": base_gguf.split_receipt,
        },
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
