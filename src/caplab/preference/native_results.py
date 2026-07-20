"""Normalization, blind disposition, and reveal for native preference runs."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

from .native import (
    NativePreferenceContractError,
    build_native_blinded_packet,
    build_native_capture,
    load_native_instrument,
)
from .native_live import (
    _native_result,
    assess_native_attempts,
    load_native_custody_attempts,
    load_native_live_manifest,
)
from .instrument import PreferenceContractError


class NativePreferenceResultContractError(ValueError):
    """Native campaign results failed normalization or reveal checks."""


_REASONS = {
    "more complete requested effect",
    "better mandatory-constraint coverage",
    "safer authority and preservation behavior",
    "better evidence and failure handling",
    "clearer, more accurate handoff",
    "presentation preference only",
}
_SELECTIONS = {"A", "B", "tie", "unjudgeable"}
_IDENTITY_MARKERS = (
    "anthropic",
    "claude",
    "fable",
    "openai",
    "gpt",
    "gpt-5.6",
    "codex",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise NativePreferenceResultContractError(f"result_json_symlink:{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NativePreferenceResultContractError(
            f"result_json_unreadable:{path}:{error}"
        ) from error
    if not isinstance(value, dict):
        raise NativePreferenceResultContractError(f"result_json_not_object:{path}")
    return value


def _validate_digest(document: dict[str, Any], field: str, error: str) -> str:
    sealed = dict(document)
    claimed = sealed.pop(field, None)
    if not isinstance(claimed, str) or claimed != _digest(sealed):
        raise NativePreferenceResultContractError(error)
    return claimed


def _write_exact(path: Path, value: object) -> None:
    content = _canonical(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
        )
    except FileExistsError:
        if path.is_symlink() or path.read_bytes() != content:
            raise NativePreferenceResultContractError(f"result_write_conflict:{path}")
        return
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def _assert_blind(value: object) -> None:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).casefold()
    for marker in _IDENTITY_MARKERS:
        if marker in encoded:
            raise NativePreferenceResultContractError(
                f"native_blind_identity_leak:{marker}"
            )


def prepare_native_normalization(
    manifest: dict[str, Any], *, output_root: str | os.PathLike[str]
) -> dict[str, Any]:
    """Normalize complete custody and emit six identity-free packets."""

    attempts = load_native_custody_attempts(manifest)
    state = assess_native_attempts(manifest, attempts)
    if not state["complete"] or state["stop_reason"] is not None:
        raise NativePreferenceResultContractError("native_campaign_not_complete")
    instrument = manifest.get("_instrument")
    if not isinstance(instrument, dict):
        raise NativePreferenceResultContractError("native_instrument_not_loaded")
    custody_root = Path(manifest["storage"]["raw_custody_root"])
    attempt_roots = sorted((custody_root / "attempts").iterdir())
    captures: dict[str, dict[str, dict[str, Any]]] = {}
    for attempt_root in attempt_roots:
        launch = _read_json(attempt_root / "launch.json")
        observation = _read_json(attempt_root / "observation.json")
        if observation.get("status") != "completed":
            raise NativePreferenceResultContractError("native_subject_outcome_unavailable")
        try:
            handoff, _ = _native_result(
                launch["subject_id"], (attempt_root / "native.stdout").read_bytes()
            )
            capture = build_native_capture(
                instrument,
                task_id=launch["task_id"],
                subject_id=launch["subject_id"],
                task_root=attempt_root / "input" / launch["task_id"],
                handoff=handoff,
                observation_sha256=observation["observation_sha256"],
                campaign_manifest_sha256=manifest["manifest_sha256"],
            )
        except (OSError, KeyError, NativePreferenceContractError) as error:
            raise NativePreferenceResultContractError(
                f"native_capture_normalization_failed:{attempt_root.name}:{error}"
            ) from error
        pair = captures.setdefault(launch["task_id"], {})
        if launch["subject_id"] in pair:
            raise NativePreferenceResultContractError("duplicate_native_capture")
        pair[launch["subject_id"]] = capture
    expected_tasks = set(instrument["reveal_map"])
    if set(captures) != expected_tasks:
        raise NativePreferenceResultContractError("incomplete_native_capture_set")
    packets: dict[str, dict[str, Any]] = {}
    for task_id in sorted(expected_tasks):
        try:
            packet = build_native_blinded_packet(instrument, task_id, captures[task_id])
        except (KeyError, NativePreferenceContractError, PreferenceContractError) as error:
            raise NativePreferenceResultContractError(
                f"native_packet_build_failed:{task_id}:{error}"
            ) from error
        _assert_blind(packet)
        packets[task_id] = packet

    raw_normalization = custody_root / "normalization"
    packet_root = Path(output_root)
    capture_hashes: dict[str, str] = {}
    for task_id in sorted(captures):
        for subject_id in sorted(captures[task_id]):
            relative = f"captures/{task_id}/{subject_id}.json"
            capture = captures[task_id][subject_id]
            _write_exact(raw_normalization / relative, capture)
            capture_hashes[relative] = _digest(capture)
    packet_hashes: dict[str, str] = {}
    for task_id, packet in packets.items():
        relative = f"packets/{task_id}.json"
        _write_exact(packet_root / relative, packet)
        packet_hashes[task_id] = _digest(packet)
    source_sha256 = sha256(Path(__file__).read_bytes()).hexdigest()
    capture_manifest = {
        "schema": "caplab.preference.native-capture-manifest/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "normalization_source_sha256": source_sha256,
        "captures": capture_hashes,
    }
    capture_manifest["capture_manifest_sha256"] = _digest(capture_manifest)
    _write_exact(raw_normalization / "capture-manifest.json", capture_manifest)
    packet_manifest = {
        "schema": "caplab.preference.native-packet-manifest/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "authority": "adr-0043",
        "normalization_source_sha256": source_sha256,
        "capture_manifest_sha256": capture_manifest["capture_manifest_sha256"],
        "packets": packet_hashes,
        "status": "prepared-blind",
        "prepared_at": datetime.now(UTC).isoformat(),
    }
    packet_manifest["packet_manifest_sha256"] = _digest(packet_manifest)
    _write_exact(packet_root / "packet-manifest.json", packet_manifest)
    return packet_manifest


def freeze_native_dispositions(
    packet_root: str | os.PathLike[str], decisions_path: str | os.PathLike[str]
) -> dict[str, Any]:
    """Freeze all six delegated blind judgments before reveal."""

    root = Path(packet_root)
    manifest = _read_json(root / "packet-manifest.json")
    _validate_digest(
        manifest, "packet_manifest_sha256", "native_packet_manifest_digest_mismatch"
    )
    decisions = _read_json(Path(decisions_path))
    packet_hashes = manifest.get("packets")
    if not isinstance(packet_hashes, dict) or set(packet_hashes) != set(decisions):
        raise NativePreferenceResultContractError("incomplete_native_dispositions")
    frozen: dict[str, Any] = {}
    for task_id in sorted(packet_hashes):
        packet = _read_json(root / "packets" / f"{task_id}.json")
        _assert_blind(packet)
        if _digest(packet) != packet_hashes[task_id]:
            raise NativePreferenceResultContractError("native_packet_digest_mismatch")
        decision = decisions[task_id]
        if not isinstance(decision, dict):
            raise NativePreferenceResultContractError("invalid_native_disposition")
        if decision.get("preferred_alias") not in _SELECTIONS:
            raise NativePreferenceResultContractError("invalid_native_preferred_alias")
        reasons = decision.get("reasons")
        if (
            not isinstance(reasons, list)
            or not reasons
            or not set(reasons).issubset(_REASONS)
        ):
            raise NativePreferenceResultContractError("invalid_native_disposition_reasons")
        if not isinstance(decision.get("rationale"), str) or not decision["rationale"].strip():
            raise NativePreferenceResultContractError("missing_native_disposition_rationale")
        if decision.get("uncertainty") not in {"low", "medium", "high"}:
            raise NativePreferenceResultContractError("invalid_native_disposition_uncertainty")
        _assert_blind(decision)
        frozen[task_id] = decision
    result = {
        "schema": "caplab.preference.native-blind-dispositions/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "authority": "repository-owner blanket delegation through adr-0026 exercised by primary-agent",
        "packet_manifest_sha256": manifest["packet_manifest_sha256"],
        "packet_sha256": packet_hashes,
        "dispositions": frozen,
        "status": "frozen-before-reveal",
        "frozen_at": datetime.now(UTC).isoformat(),
    }
    _assert_blind(result)
    result["freeze_sha256"] = _digest(result)
    _write_exact(root / "frozen-dispositions.json", result)
    return result


def reveal_native_dispositions(
    instrument: dict[str, Any], *, packet_root: str | os.PathLike[str],
    raw_normalization_root: str | os.PathLike[str],
) -> dict[str, Any]:
    """Reveal frozen aliases and recompute preregistered thresholds."""

    root = Path(packet_root)
    packet_manifest = _read_json(root / "packet-manifest.json")
    packet_manifest_sha256 = _validate_digest(
        packet_manifest,
        "packet_manifest_sha256",
        "native_packet_manifest_digest_mismatch",
    )
    frozen = _read_json(root / "frozen-dispositions.json")
    sealed = dict(frozen)
    claimed = sealed.pop("freeze_sha256", None)
    if claimed != _digest(sealed) or frozen.get("status") != "frozen-before-reveal":
        raise NativePreferenceResultContractError("native_disposition_freeze_invalid")
    if frozen.get("packet_manifest_sha256") != packet_manifest_sha256:
        raise NativePreferenceResultContractError("native_frozen_packet_manifest_mismatch")
    raw_root = Path(raw_normalization_root)
    capture_manifest = _read_json(raw_root / "capture-manifest.json")
    capture_manifest_sha256 = _validate_digest(
        capture_manifest,
        "capture_manifest_sha256",
        "native_capture_manifest_digest_mismatch",
    )
    if capture_manifest_sha256 != packet_manifest.get("capture_manifest_sha256"):
        raise NativePreferenceResultContractError("native_capture_packet_lineage_mismatch")
    pairs: dict[str, Any] = {}
    valid_pairs = 0
    fable_constraint_advantage = 0
    fable_preference = 0
    for task_id in sorted(instrument["reveal_map"]):
        decision = frozen["dispositions"][task_id]
        preferred_alias = decision["preferred_alias"]
        preferred_subject = (
            instrument["reveal_map"][task_id][preferred_alias]
            if preferred_alias in {"A", "B"}
            else preferred_alias
        )
        subject_scores: dict[str, int] = {}
        outcomes: dict[str, str] = {}
        for subject_id in ("fable", "gpt"):
            capture = _read_json(
                raw_root / "captures" / task_id / f"{subject_id}.json"
            )
            relative_capture = f"captures/{task_id}/{subject_id}.json"
            if _digest(capture) != capture_manifest.get("captures", {}).get(
                relative_capture
            ):
                raise NativePreferenceResultContractError(
                    "native_capture_digest_mismatch"
                )
            subject_scores[subject_id] = len(capture["mechanical"]["satisfied"])
            outcomes[subject_id] = capture["outcome"]
        valid = all(outcome != "invalid" for outcome in outcomes.values())
        if valid:
            valid_pairs += 1
            if subject_scores["fable"] > subject_scores["gpt"]:
                fable_constraint_advantage += 1
            if preferred_subject == "fable":
                fable_preference += 1
        pairs[task_id] = {
            "valid": valid,
            "outcomes": outcomes,
            "constraints_satisfied": subject_scores,
            "preferred_alias": preferred_alias,
            "preferred_subject": preferred_subject,
            "reasons": decision["reasons"],
            "rationale": decision["rationale"],
            "uncertainty": decision["uncertainty"],
        }
    thresholds = instrument["analysis_thresholds"]
    if valid_pairs < thresholds["minimum_valid_pairs"]:
        conclusion = "inconclusive"
    elif (
        fable_constraint_advantage >= thresholds["constraint_advantage_pairs"]
        and fable_preference >= thresholds["blinded_preference_pairs"]
    ):
        conclusion = "descriptive-thresholds-met"
    else:
        conclusion = "hypothesis-disconfirmed"
    result = {
        "schema": "caplab.preference.native-revealed-result/v1",
        "study_id": instrument["study_id"],
        "instrument_design_sha256": instrument["design_sha256"],
        "freeze_sha256": claimed,
        "pairs": pairs,
        "thresholds": thresholds,
        "counts": {
            "valid_pairs": valid_pairs,
            "fable_constraint_advantage_pairs": fable_constraint_advantage,
            "fable_blinded_preference_pairs": fable_preference,
        },
        "conclusion": conclusion,
        "claim_ceiling": "task-conditioned descriptive association on this synthetic population only",
        "revealed_at": datetime.now(UTC).isoformat(),
    }
    result["result_sha256"] = _digest(result)
    _write_exact(root / "revealed-result.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m caplab.preference.native_results")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--instrument", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare")
    freeze = commands.add_parser("freeze")
    freeze.add_argument("--decisions", required=True, type=Path)
    commands.add_parser("reveal")
    args = parser.parse_args(argv)
    manifest = load_native_live_manifest(args.manifest, args.instrument)
    if args.command == "prepare":
        value = prepare_native_normalization(manifest, output_root=args.output_root)
    elif args.command == "freeze":
        value = freeze_native_dispositions(args.output_root, args.decisions)
    else:
        instrument = load_native_instrument(args.instrument)
        value = reveal_native_dispositions(
            instrument,
            packet_root=args.output_root,
            raw_normalization_root=Path(manifest["storage"]["raw_custody_root"])
            / "normalization",
        )
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
