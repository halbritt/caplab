"""Issue and validate the Gate 3 receipt that admits a full paid run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from pathlib import PurePosixPath
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


def _json_object(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"{label} is missing, linked, or not a file")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"{label} is invalid JSON") from error
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def _resolve_controller_recovery(
    run_root: Path,
    run_id: str,
    expected_image: str,
) -> tuple[Path, Path, Path]:
    """Resolve a verified jobrunner recovery into the worker's artifact layout."""

    if re.fullmatch(r"run-[A-Za-z0-9._-]+", run_id) is None:
        raise ContractError("Gate 3 run ID is invalid")
    if run_root.is_symlink() or not run_root.is_dir():
        raise ContractError("Gate 3 controller run root is missing, linked, or not a directory")
    root = run_root.resolve()
    request = _json_object(root / "request.json", "Gate 3 controller request")
    state = _json_object(root / "state.json", "Gate 3 controller state")
    controller = request.get("controller")
    provider = request.get("provider")
    remote = request.get("remote")
    closeout = state.get("closeout")
    artifact_disposition = (
        closeout.get("artifact_disposition") if isinstance(closeout, dict) else None
    )
    deletion_closed = isinstance(closeout, dict) and (
        closeout.get("delete_acknowledged") is True
        or closeout.get("delete_already_absent") is True
    )
    if (
        request.get("protocol") != "controller-request/1"
        or state.get("protocol") != "run-status/1"
        or state.get("run_id") != run_id
        or state.get("lifecycle") != "closed"
        or state.get("workload_result") != "succeeded"
        or not isinstance(artifact_disposition, dict)
        or artifact_disposition.get("status") != "verified"
        or not isinstance(closeout, dict)
        or str(closeout.get("current_spend_usd_per_hour")) not in {"0", "0.0", "0.00"}
        or not deletion_closed
    ):
        raise ContractError(
            "Gate 3 controller run is not closed, successful, verified, and spend-free"
        )
    if not isinstance(controller, dict):
        raise ContractError("Gate 3 controller request has no controller binding")
    remote_root_value = controller.get("remote_run_root")
    if not isinstance(remote_root_value, str):
        raise ContractError("Gate 3 controller request has no remote run root")
    remote_root = PurePosixPath(remote_root_value)
    if (
        not remote_root.is_absolute()
        or ".." in remote_root.parts
        or remote_root.name != run_id
    ):
        raise ContractError("Gate 3 remote run root does not match the run ID")
    if (
        not isinstance(provider, dict)
        or not isinstance(remote, dict)
        or provider.get("image") != expected_image
        or remote.get("image_digest") != expected_image
    ):
        raise ContractError("Gate 3 controller image digest does not match the build receipt")

    artifact_root = root / "receipts/artifacts"
    manifest = root / "receipts/manifest/artifact-manifest.json"
    if artifact_root.is_symlink() or not artifact_root.is_dir():
        raise ContractError("recovered Gate 3 artifact tree is missing or linked")
    if manifest.is_symlink() or not manifest.is_file():
        raise ContractError("recovered Gate 3 artifact manifest is missing or linked")
    expected_resume = Path(
        str(remote_root / "artifacts/preflight/training/checkpoint-2")
    )
    return artifact_root.resolve(), manifest.resolve(), expected_resume


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
    build_receipt, _ = _load_build_receipt(build_receipt_path.resolve())
    artifact_root, artifact_path, expected_resume = _resolve_controller_recovery(
        run_root,
        run_id,
        str(build_receipt["immutable_image"]),
    )
    recovered = _json_object(artifact_path, "recovered Gate 3 artifact manifest")
    expected = build_smoke_manifest(
        artifact_root,
        Path(__file__).with_name("smoke") / "moe-training-config.json",
        expected_resume=expected_resume,
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
