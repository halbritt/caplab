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


def update(bundle: Path, digest: str) -> None:
    digest = digest.removeprefix("sha256:")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ContractError(
            "image digest must be sha256 followed by 64 lowercase hex digits"
        )
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
    spec.pop("bundle_hash", None)
    bundle_hash = _canonical_hash({"input_manifest": manifest, "job_spec": spec})
    rendered, hash_replacements = BUNDLE_RE.subn(
        f'bundle_hash: "{bundle_hash}"', rendered
    )
    if hash_replacements != 1:
        raise ContractError("job.yaml does not contain exactly one bundle hash")
    metadata = json.loads(metadata_path.read_text())
    metadata["image_digest_pinned"] = True
    metadata["image_digest"] = f"sha256:{digest}"
    metadata["bundle_hash"] = bundle_hash
    _atomic_write(job_path, rendered)
    _atomic_write(metadata_path, json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("digest")
    args = parser.parse_args()
    update(args.bundle.resolve(), args.digest)


if __name__ == "__main__":
    main()
