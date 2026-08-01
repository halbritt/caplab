"""Issue and validate the Gate 3 receipt that admits a full paid run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from .contract import ContractError, atomic_json, sha256_file
from .package_smoke import build_smoke_manifest
from .update_image_digest import EXPECTED_IMAGE_REPOSITORY, _load_build_receipt


MODEL_ID = "Qwen/Qwen3.6-35B-A3B"
MODEL_REVISION = "995ad96eacd98c81ed38be0c5b274b04031597b0"
MODEL_TYPE = "qwen3_5_moe"
REQUIRED_EVIDENCE = {
    "artifacts/preflight/preflight.json",
    "artifacts/preflight/flash-qla-smoke.json",
    "artifacts/preflight/inference.json",
    "artifacts/preflight/training/training-result.json",
    "artifacts/preflight/training/checkpoint-2/checkpoint-complete.json",
    "artifacts/preflight/training/checkpoint-4/checkpoint-complete.json",
}


def _normalized_image(value: str) -> str:
    if re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        return f"{EXPECTED_IMAGE_REPOSITORY}@{value}"
    return value


def validate_gate3_acceptance(
    path: Path, *, expected_image_digest: str | None = None
) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ContractError("Gate 3 acceptance receipt is missing, linked, or not a file")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError("Gate 3 acceptance receipt is invalid JSON") from error
    if not isinstance(value, dict):
        raise ContractError("Gate 3 acceptance receipt must be an object")
    model = value.get("model")
    image = value.get("image_digest")
    if (
        value.get("protocol") != "striatum-gate-acceptance/1"
        or value.get("gate") != 3
        or value.get("accepted") is not True
        or not isinstance(value.get("run_id"), str)
        or re.fullmatch(r"run-[A-Za-z0-9._-]+", str(value.get("run_id"))) is None
        or not isinstance(image, str)
        or re.fullmatch(
            re.escape(EXPECTED_IMAGE_REPOSITORY) + r"@sha256:[0-9a-f]{64}", image
        )
        is None
        or not isinstance(value.get("image_source_commit"), str)
        or re.fullmatch(r"[0-9a-f]{40}", str(value.get("image_source_commit")))
        is None
        or model
        != {"id": MODEL_ID, "revision": MODEL_REVISION, "model_type": MODEL_TYPE}
        or not isinstance(value.get("artifact_manifest_sha256"), str)
        or re.fullmatch(
            r"[0-9a-f]{64}", str(value.get("artifact_manifest_sha256"))
        )
        is None
    ):
        raise ContractError("Gate 3 acceptance receipt contract is invalid")
    if expected_image_digest is not None and image != _normalized_image(
        expected_image_digest
    ):
        raise ContractError("Gate 3 acceptance image digest does not match this run")
    return value


def issue_gate3_acceptance(
    run_root: Path,
    build_receipt_path: Path,
    run_id: str,
    output: Path,
) -> dict[str, object]:
    run_root = run_root.resolve()
    build_receipt, _ = _load_build_receipt(build_receipt_path.resolve())
    artifact_path = run_root / "artifact-manifest.json"
    if artifact_path.is_symlink() or not artifact_path.is_file():
        raise ContractError("recovered Gate 3 artifact manifest is missing")
    try:
        recovered = json.loads(artifact_path.read_text())
    except json.JSONDecodeError as error:
        raise ContractError("recovered Gate 3 artifact manifest is invalid") from error
    expected = build_smoke_manifest(
        run_root, Path(__file__).with_name("smoke") / "moe-training-config.json"
    )
    if recovered != expected:
        raise ContractError("recovered Gate 3 artifacts do not match terminal evidence")
    paths = {
        str(item.get("path"))
        for item in recovered.get("files", [])
        if isinstance(item, dict)
    }
    if not REQUIRED_EVIDENCE.issubset(paths):
        raise ContractError("recovered Gate 3 evidence set is incomplete")
    receipt = {
        "protocol": "striatum-gate-acceptance/1",
        "gate": 3,
        "accepted": True,
        "run_id": run_id,
        "image_digest": build_receipt["immutable_image"],
        "image_source_commit": build_receipt["source_commit"],
        "model": {
            "id": MODEL_ID,
            "revision": MODEL_REVISION,
            "model_type": MODEL_TYPE,
        },
        "artifact_manifest_sha256": sha256_file(artifact_path),
    }
    atomic_json(output.resolve(), receipt)
    return validate_gate3_acceptance(
        output.resolve(), expected_image_digest=str(build_receipt["digest"])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--build-receipt", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = issue_gate3_acceptance(
        args.run_root, args.build_receipt, args.run_id, args.output
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
