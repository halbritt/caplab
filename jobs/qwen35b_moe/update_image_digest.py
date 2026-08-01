"""Pin the generated bundle to one immutable worker image digest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from .contract import ContractError


IMAGE_RE = re.compile(
    r"^(image:\s+ghcr\.io/halbritt/striatum-tuner-qwen35b-moe@sha256:)"
    r"(?:REPLACE_WITH_IMAGE_DIGEST|[0-9a-f]{64})$",
    re.MULTILINE,
)
BUNDLE_RE = re.compile(r"^bundle_hash:\s+['\"]?[0-9a-f]{64}['\"]?$", re.MULTILINE)
EXPECTED_IMAGE_REPOSITORY = "ghcr.io/halbritt/striatum-tuner-qwen35b-moe"


def _canonical_hash(value: object) -> str:
    # The v1 job contains only JSON-native YAML values. For those values this
    # matches runpod-jobrunner's canonical encoder byte-for-byte; its `check`
    # command remains the final authority.
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _atomic_write(path: Path, text: str) -> None:
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def _load_build_receipt(path: Path) -> tuple[dict[str, object], str]:
    if path.is_symlink() or not path.is_file():
        raise ContractError("image build receipt is missing, linked, or not a file")
    raw = path.read_bytes()
    try:
        receipt = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ContractError("image build receipt is not valid JSON") from error
    if not isinstance(receipt, dict):
        raise ContractError("image build receipt must be an object")
    if receipt.get("protocol") != "striatum-worker-image-build/2":
        raise ContractError("image build receipt protocol is unsupported")
    if receipt.get("pushed") is not True:
        raise ContractError("image build receipt must prove a pushed image")
    digest_value = receipt.get("digest")
    if not isinstance(digest_value, str) or not re.fullmatch(
        r"sha256:[0-9a-f]{64}", digest_value
    ):
        raise ContractError("image build receipt has an invalid digest")
    immutable_image = receipt.get("immutable_image")
    if immutable_image != f"{EXPECTED_IMAGE_REPOSITORY}@{digest_value}":
        raise ContractError("image build receipt names the wrong immutable image")
    source_commit = receipt.get("source_commit")
    if not isinstance(source_commit, str) or not re.fullmatch(
        r"[0-9a-f]{40}", source_commit
    ):
        raise ContractError("image build receipt has an invalid source commit")
    return receipt, hashlib.sha256(raw).hexdigest()


def update(bundle: Path, receipt_path: Path) -> None:
    receipt, receipt_sha256 = _load_build_receipt(receipt_path)
    digest = str(receipt["digest"]).removeprefix("sha256:")
    job_path = bundle / "job.yaml"
    metadata_path = bundle / "bundle-metadata.json"
    if not job_path.is_file() or not metadata_path.is_file():
        raise ContractError("not a materialized Qwen job bundle")
    rendered, replacements = IMAGE_RE.subn(rf"\g<1>{digest}", job_path.read_text())
    if replacements != 1:
        raise ContractError(
            "job.yaml does not contain exactly one expected image reference"
        )
    try:
        import yaml
    except ImportError as error:
        raise ContractError("PyYAML is required to stamp a generated bundle") from error
    spec = yaml.safe_load(rendered)
    manifest = json.loads((bundle / "input-manifest.json").read_text())
    if not isinstance(spec, dict) or not isinstance(manifest, dict):
        raise ContractError("generated job or manifest is not an object")
    runner = spec.get("runner")
    release = receipt.get("jobrunner_release")
    if not isinstance(runner, dict) or not isinstance(release, dict):
        raise ContractError("job or build receipt runner contract is missing")
    supported_protocols = release.get("supported_protocol_majors")
    if (
        release.get("protocol") != "runner-release/1"
        or release.get("runner_version") != runner.get("version")
        or release.get("runner_git_commit") != runner.get("git_commit")
        or not isinstance(supported_protocols, dict)
        or supported_protocols.get("run-request") != [1]
    ):
        raise ContractError("image build receipt runner does not match job.yaml")
    spec.pop("bundle_hash", None)
    bundle_hash = _canonical_hash({"input_manifest": manifest, "job_spec": spec})
    rendered, hash_replacements = BUNDLE_RE.subn(
        f'bundle_hash: "{bundle_hash}"', rendered
    )
    if hash_replacements != 1:
        raise ContractError("job.yaml does not contain exactly one bundle hash")
    metadata = json.loads(metadata_path.read_text())
    gate3_image = metadata.get("gate3_image_digest")
    if gate3_image is not None and gate3_image != receipt["immutable_image"]:
        raise ContractError(
            "full bundle image does not match the image accepted by Gate 3"
        )
    metadata["image_digest_pinned"] = True
    metadata["image_digest"] = f"sha256:{digest}"
    metadata["image_build_receipt_sha256"] = receipt_sha256
    metadata["image_source_commit"] = receipt["source_commit"]
    metadata["jobrunner_release"] = release
    metadata["bundle_hash"] = bundle_hash
    receipt_target = bundle / "image-build-receipt.json"
    _atomic_write(job_path, rendered)
    _atomic_write(metadata_path, json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    _atomic_write(
        receipt_target, json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("build_receipt", type=Path)
    args = parser.parse_args()
    update(args.bundle.resolve(), args.build_receipt.resolve())


if __name__ == "__main__":
    main()
