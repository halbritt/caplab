"""Exact loopback runner for the authorized local-Qwen training-source study."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import urllib.request
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

from .instrument import load_calibration_instrument
from .local_training import (
    build_local_review_prompt,
    grade_local_review,
    parse_local_review_output,
)


class LocalTrainingLiveError(ValueError):
    """The authorized manifest, runtime, or custody contract failed."""


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _exclusive(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def load_local_training_manifest(path: Path, project_root: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "caplab.review-dissent.local-training-instrument/v1":
        raise LocalTrainingLiveError("invalid_local_training_manifest")
    sealed = dict(manifest)
    claimed = sealed.pop("design_sha256", None)
    if claimed != _digest(sealed):
        raise LocalTrainingLiveError("local_training_manifest_digest_mismatch")
    if manifest.get("status") != "active" or manifest.get("authority") != "adr-0047":
        raise LocalTrainingLiveError("local_training_not_authorized")
    expiry = datetime.fromisoformat(manifest["expires_at"].replace("Z", "+00:00"))
    if datetime.now(UTC) > expiry:
        raise LocalTrainingLiveError("local_training_authorization_expired")
    for field, relative in (
        ("runtime_source_sha256", "src/caplab/review_dissent/local_training.py"),
        ("runner_source_sha256", "src/caplab/review_dissent/local_training_live.py"),
    ):
        if sha256((project_root / relative).read_bytes()).hexdigest() != manifest.get(field):
            raise LocalTrainingLiveError(f"{field}_mismatch")
    binding = manifest["base_instrument"]
    instrument_path = project_root / binding["path"]
    if sha256(instrument_path.read_bytes()).hexdigest() != binding["file_sha256"]:
        raise LocalTrainingLiveError("local_training_base_instrument_mismatch")
    instrument = load_calibration_instrument(instrument_path.parent)
    if instrument["design_sha256"] != binding["design_sha256"]:
        raise LocalTrainingLiveError("local_training_base_design_mismatch")
    result = dict(manifest)
    result["_instrument"] = instrument
    return result


def _server_idle() -> bool:
    with urllib.request.urlopen("http://127.0.0.1:8081/metrics", timeout=2) as response:
        metrics = response.read().decode("utf-8")
    values: dict[str, float] = {}
    for line in metrics.splitlines():
        if line.startswith("llamacpp:requests_processing ") or line.startswith("llamacpp:requests_deferred "):
            key, value = line.split()
            values[key] = float(value)
    return values == {
        "llamacpp:requests_processing": 0.0,
        "llamacpp:requests_deferred": 0.0,
    }


def run_local_training_campaign(manifest: dict[str, Any]) -> dict[str, Any]:
    root = Path(manifest["storage"]["raw_custody_root"])
    if not root.is_absolute() or root.exists() or root.is_symlink():
        raise LocalTrainingLiveError("unsafe_local_training_custody_root")
    if not _server_idle():
        raise LocalTrainingLiveError("local_qwen_server_busy")
    root.mkdir(parents=True, mode=0o700)
    instrument = manifest["_instrument"]
    manifest_public = {key: value for key, value in manifest.items() if not key.startswith("_")}
    manifest_file_sha = sha256(_canonical(manifest_public)).hexdigest()
    _exclusive(root / "manifest.json", _canonical(manifest_public) + b"\n")
    attempts: list[dict[str, Any]] = []
    for sequence, cell_id in enumerate(manifest["execution_order"], 1):
        if not _server_idle():
            raise LocalTrainingLiveError("local_qwen_server_busy")
        prompt = build_local_review_prompt(instrument, cell_id).encode("utf-8")
        attempt_root = root / "attempts" / f"a{sequence:02d}-{cell_id}"
        _exclusive(attempt_root / "prompt.txt", prompt)
        started = time.monotonic()
        completed = subprocess.run(
            manifest["subject"]["command"], input=prompt, capture_output=True,
            timeout=manifest["limits"]["trial_wall_clock_minutes"] * 60, check=False,
        )
        duration = time.monotonic() - started
        _exclusive(attempt_root / "stdout", completed.stdout)
        _exclusive(attempt_root / "stderr", completed.stderr)
        status = "harness-failure" if completed.returncode else "subject-invalid"
        row: dict[str, Any] | None = None
        if completed.returncode == 0:
            try:
                review = parse_local_review_output(completed.stdout)
                row = grade_local_review(
                    instrument, cell_id=cell_id, review=review,
                    response_sha256=sha256(completed.stdout).hexdigest(),
                    tuple_id=manifest["subject"]["tuple_id"],
                )
                status = "completed"
            except ValueError:
                status = "subject-invalid"
        attempt = {
            "schema": "caplab.review-dissent.local-training-attempt/v1",
            "sequence": sequence,
            "cell_id": cell_id,
            "manifest_file_sha256": manifest_file_sha,
            "tuple_id": manifest["subject"]["tuple_id"],
            "command": manifest["subject"]["command"],
            "prompt_sha256": sha256(prompt).hexdigest(),
            "stdout_sha256": sha256(completed.stdout).hexdigest(),
            "stderr_sha256": sha256(completed.stderr).hexdigest(),
            "return_code": completed.returncode,
            "duration_seconds": f"{duration:.6f}",
            "status": status,
            "row": row,
        }
        attempt["attempt_sha256"] = _digest(attempt)
        _exclusive(attempt_root / "attempt.json", _canonical(attempt) + b"\n")
        attempts.append(attempt)
    result = {
        "schema": "caplab.review-dissent.local-training-result/v1",
        "campaign_id": manifest["study_id"],
        "manifest_file_sha256": manifest_file_sha,
        "tuple_id": manifest["subject"]["tuple_id"],
        "attempts": attempts,
        "counts": {
            "attempts": len(attempts),
            "completed": sum(item["status"] == "completed" for item in attempts),
            "subject_invalid": sum(item["status"] == "subject-invalid" for item in attempts),
            "harness_failure": sum(item["status"] == "harness-failure" for item in attempts),
        },
        "heldout_status": "sealed-unopened",
    }
    result["result_sha256"] = _digest(result)
    _exclusive(root / "result.json", _canonical(result) + b"\n")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args(argv)
    project_root = Path(__file__).resolve().parents[3]
    manifest = load_local_training_manifest(args.manifest, project_root)
    print(json.dumps(run_local_training_campaign(manifest), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
