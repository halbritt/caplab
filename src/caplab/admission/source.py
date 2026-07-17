"""Read-only verification and deterministic inventory of frozen source bytes."""

from __future__ import annotations

import re
import subprocess
import csv
import io
import json
from pathlib import Path, PurePosixPath
from typing import Protocol

from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.runtime.models import object_key

from .models import SourceSet


MANIFEST_LINE = re.compile(r"\A([0-9a-f]{64})  ([^\n]+)\Z")
CREDENTIAL_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
)


class SourceMismatch(RuntimeError):
    """A selected source byte, identity, or cardinality does not match."""


class GitReader(Protocol):
    def read(self, commit: str, path: str) -> bytes: ...


class SubprocessGitReader:
    """Read exact committed bytes without consulting or changing a worktree."""

    def __init__(self, repository: Path) -> None:
        if not repository.is_absolute() or repository.is_symlink():
            raise ValueError("Git repository must be an absolute non-symlink path")
        self.repository = repository

    def read(self, commit: str, path: str) -> bytes:
        result = subprocess.run(
            ["git", "-C", str(self.repository), "show", f"{commit}:{path}"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise SourceMismatch(f"selected Git object is unavailable: {commit}:{path}")
        return result.stdout


class DirectoryGitReader:
    """Read pre-extracted committed bytes from a restricted immutable stage."""

    def __init__(self, root: Path) -> None:
        if not root.is_absolute() or root.is_symlink() or not root.is_dir():
            raise ValueError("Git stage must be an absolute non-symlink directory")
        self.root = root

    def read(self, commit: str, path: str) -> bytes:
        pure = PurePosixPath(path)
        if (
            not re.fullmatch(r"[0-9a-f]{40}", commit)
            or pure.is_absolute()
            or ".." in pure.parts
        ):
            raise SourceMismatch("Git stage identity is unsafe")
        selected = self.root.joinpath(commit, *pure.parts)
        if selected.is_symlink() or not selected.is_file():
            raise SourceMismatch(f"staged Git object is unavailable: {commit}:{path}")
        return selected.read_bytes()


def _media_type(path: str) -> str:
    suffix = PurePosixPath(path).suffix.lower()
    return {
        ".csv": "text/csv",
        ".json": "application/json",
        ".jsonl": "application/x-ndjson",
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".yaml": "application/yaml",
        ".yml": "application/yaml",
    }.get(suffix, "application/octet-stream")


def _record(
    *,
    record_id: str,
    source_kind: str,
    source_path: str,
    payload: bytes,
    source_commit: str | None = None,
) -> dict[str, object]:
    digest = sha256_hex(payload)
    record: dict[str, object] = {
        "record_id": record_id,
        "source_kind": source_kind,
        "source_path": source_path,
        "content_sha256": digest,
        "byte_count": len(payload),
        "media_type": _media_type(source_path),
        "object_key": object_key(digest),
        "local_copy_key": object_key(digest),
        "disposition": "restricted-admission",
    }
    if source_commit is not None:
        record["source_commit"] = source_commit
    return record


def _credential_check(record_id: str, payload: bytes) -> None:
    if any(pattern.search(payload) for pattern in CREDENTIAL_PATTERNS):
        raise SourceMismatch(
            f"credential-bearing object requires quarantine: {record_id}"
        )


def _identity(kind: str, body: dict[str, object]) -> dict[str, object]:
    return {
        "kind": kind,
        "identity_sha256": sha256_hex(canonical_json(body)),
        "body": body,
    }


def _json(payload: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(payload, parse_float=str)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SourceMismatch(f"{label} is not valid JSON") from error
    if not isinstance(value, dict):
        raise SourceMismatch(f"{label} must contain a JSON object")
    return value


def _typed_links(
    source: SourceSet,
    records: list[dict[str, object]],
    payload_by_record: dict[str, bytes],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    if source.expected_attempts == 0:
        return [], [], [], []
    by_path = {str(record["source_path"]): record for record in records}
    order_path = "frozen-inputs/checkout-retries-luna-bv-confirmation-order.csv"
    order_record = by_path.get(order_path)
    result_record = next(
        (record for record in records if record["record_id"] == "result-csv"), None
    )
    if order_record is None or result_record is None:
        raise SourceMismatch("frozen order or selected result CSV is absent")
    try:
        order_rows = list(
            csv.DictReader(
                io.StringIO(
                    payload_by_record[str(order_record["record_id"])].decode("utf-8")
                )
            )
        )
        result_rows = list(
            csv.DictReader(
                io.StringIO(
                    payload_by_record[str(result_record["record_id"])].decode("utf-8")
                )
            )
        )
    except UnicodeDecodeError as error:
        raise SourceMismatch("order or result CSV is not UTF-8") from error
    if (
        len(order_rows) != source.expected_attempts
        or len(result_rows) != source.expected_attempts
    ):
        raise SourceMismatch(
            "order or result CSV cardinality differs from the decision"
        )
    results = {row.get("sequence"): row for row in result_rows}
    if len(results) != source.expected_attempts or None in results:
        raise SourceMismatch("result CSV repeats or omits a sequence")
    assignments: list[dict[str, object]] = []
    attempts: list[dict[str, object]] = []
    outcomes: list[dict[str, object]] = []
    metadata_documents: list[dict[str, object]] = []
    for expected_sequence, row in enumerate(order_rows, start=1):
        sequence = str(expected_sequence)
        if row.get("sequence") != sequence or set(row) != {
            "sequence",
            "block",
            "task",
            "arm",
        }:
            raise SourceMismatch("order CSV sequence or columns are inconsistent")
        result = results[sequence]
        if any(
            result.get(field) != row[field]
            for field in ("sequence", "block", "task", "arm")
        ):
            raise SourceMismatch(
                f"result row differs from assignment at sequence {sequence}"
            )
        if result.get("status") != "valid" or result.get("attempt") != "1":
            raise SourceMismatch(
                f"result row is not the frozen first valid attempt at sequence {sequence}"
            )
        trial_name = result.get("trial")
        if not isinstance(trial_name, str) or not trial_name:
            raise SourceMismatch(
                f"result row has no trial identity at sequence {sequence}"
            )
        base = f"attempts/{trial_name}"
        paths = {
            "metadata": f"{base}/trial-metadata.json",
            "trial": f"{base}/trial.json",
            "outcome": f"{base}/confirmation-observation.json",
        }
        selected_records: dict[str, dict[str, object]] = {}
        documents: dict[str, dict[str, object]] = {}
        for label, path in paths.items():
            record = by_path.get(path)
            if record is None:
                raise SourceMismatch(f"{label} record is absent for {trial_name}")
            selected_records[label] = record
            documents[label] = _json(
                payload_by_record[str(record["record_id"])], f"{trial_name} {label}"
            )
        metadata = documents["metadata"]
        observation = documents["outcome"]
        if (
            metadata.get("sequence") != expected_sequence
            or metadata.get("block") != row["block"]
            or metadata.get("task") != row["task"]
            or metadata.get("arm") != row["arm"]
            or metadata.get("attempt") != 1
        ):
            raise SourceMismatch(
                f"trial metadata differs from assignment at sequence {sequence}"
            )
        if (
            observation.get("sequence") != expected_sequence
            or observation.get("block") != row["block"]
            or observation.get("task") != row["task"]
            or observation.get("arm") != row["arm"]
        ):
            raise SourceMismatch(
                f"outcome differs from assignment at sequence {sequence}"
            )
        assignment_body: dict[str, object] = {
            "study_id": source.study_id,
            "sequence": expected_sequence,
            "block": row["block"],
            "task": row["task"],
            "condition": row["arm"],
            "attempt_denominator": 1,
            "replacement": "none-recorded",
            "order_record_sha256": order_record["content_sha256"],
        }
        assignment = _identity("trial-assignment", assignment_body)
        assignment["sequence"] = expected_sequence
        assignment["block"] = row["block"]
        assignment["task"] = row["task"]
        assignment["condition"] = row["arm"]
        assignments.append(assignment)
        attempt_body: dict[str, object] = {
            "trial": trial_name,
            "attempt_number": 1,
            "assignment_sha256": assignment["identity_sha256"],
            "sealed_at": metadata.get("sealed_at"),
            "started_at": documents["trial"].get("started"),
            "finished_at": documents["trial"].get("provenance", {}).get("finished")
            if isinstance(documents["trial"].get("provenance"), dict)
            else None,
            "metadata_record_sha256": selected_records["metadata"]["content_sha256"],
            "trial_record_sha256": selected_records["trial"]["content_sha256"],
            "historical_metadata": metadata,
            "historical_trial": documents["trial"],
        }
        attempt = _identity("attempt", attempt_body)
        attempt["assignment_sha256"] = assignment["identity_sha256"]
        attempt["attempt_number"] = 1
        attempts.append(attempt)
        outcome_body: dict[str, object] = {
            "attempt_sha256": attempt["identity_sha256"],
            "outcome_record_sha256": selected_records["outcome"]["content_sha256"],
            "result_csv_sha256": result_record["content_sha256"],
            "historical_observation": observation,
            "historical_result_row": result,
            "human_disposition": "not-recorded",
        }
        outcome = _identity("mechanical-outcome", outcome_body)
        outcome["attempt_sha256"] = attempt["identity_sha256"]
        outcomes.append(outcome)
        metadata_documents.append(metadata)
    kinds: list[tuple[str, dict[str, object]]] = [
        (
            "preservation-manifest",
            {"content_sha256": source.preservation_manifest_sha256},
        ),
        (
            "order",
            {"content_sha256": order_record["content_sha256"]},
        ),
        (
            "result-csv",
            {"content_sha256": result_record["content_sha256"]},
        ),
    ]
    for kind, path in (
        (
            "experiment",
            "frozen-inputs/checkout-retries-luna-bv-confirmation/experiment.json",
        ),
        (
            "treatment",
            "frozen-inputs/checkout-retries-luna-bv-confirmation/treatment-manifest.json",
        ),
    ):
        record = by_path.get(path)
        if record is None:
            raise SourceMismatch(f"required {kind} identity record is absent")
        kinds.append((kind, {"content_sha256": record["content_sha256"]}))
    result_md = next(
        (record for record in records if record["record_id"] == "result-record"), None
    )
    if result_md is None:
        raise SourceMismatch("selected result record is absent")
    kinds.extend(
        [
            ("result-record", {"content_sha256": result_md["content_sha256"]}),
            (
                "subject",
                {
                    "model": metadata_documents[0].get("model"),
                    "backend_id": metadata_documents[0].get("backend_id"),
                    "reasoning_effort": metadata_documents[0].get("reasoning_effort"),
                },
            ),
            (
                "runtime",
                {
                    "runtime_version": metadata_documents[0].get("runtime_version"),
                    "execution_mode": metadata_documents[0].get("execution_mode"),
                    "capture_binary_sha256": metadata_documents[0].get(
                        "capture_binary_sha256"
                    ),
                    "observer_commit": metadata_documents[0].get("observer_commit"),
                },
            ),
            ("corpus", {"surface_hash": metadata_documents[0].get("surface_hash")}),
            (
                "verifier",
                {
                    "outcome_record_sha256": [
                        outcome["body"]["outcome_record_sha256"] for outcome in outcomes
                    ]
                },
            ),
            (
                "task",
                {
                    "task_content_hashes": sorted(
                        {
                            str(item.get("task_content_hash"))
                            for item in metadata_documents
                        }
                    )
                },
            ),
        ]
    )
    return (
        assignments,
        attempts,
        outcomes,
        [_identity(kind, body) for kind, body in kinds],
    )


def _manifest_members(
    source: SourceSet, manifest: bytes
) -> list[tuple[str, str, bytes]]:
    members: list[tuple[str, str, bytes]] = []
    seen: set[str] = set()
    try:
        lines = manifest.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise SourceMismatch("preservation manifest is not UTF-8") from error
    for line in lines:
        match = MANIFEST_LINE.fullmatch(line)
        if match is None:
            raise SourceMismatch("preservation manifest contains an invalid line")
        expected, relative = match.groups()
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or str(path) != relative:
            raise SourceMismatch("preservation manifest contains an unsafe path")
        if relative in seen:
            raise SourceMismatch(f"preservation manifest repeats {relative}")
        seen.add(relative)
        absolute = source.preservation_root.joinpath(*path.parts)
        if absolute.is_symlink() or not absolute.is_file():
            raise SourceMismatch(
                f"preservation member is missing or unsafe: {relative}"
            )
        payload = absolute.read_bytes()
        actual = sha256_hex(payload)
        if actual != expected:
            raise SourceMismatch(f"preservation member hash mismatch: {relative}")
        members.append((relative, expected, payload))
    if len(members) != source.expected_preservation_records:
        raise SourceMismatch(
            "preservation record count differs: "
            f"expected {source.expected_preservation_records}, got {len(members)}"
        )
    return members


def build_manifest(source: SourceSet, *, git_reader: GitReader) -> dict[str, object]:
    manifest_path = source.preservation_root / "manifest.sha256"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise SourceMismatch("preservation manifest is missing or unsafe")
    manifest_bytes = manifest_path.read_bytes()
    if sha256_hex(manifest_bytes) != source.preservation_manifest_sha256:
        raise SourceMismatch("preservation manifest hash differs from the decision")
    members = _manifest_members(source, manifest_bytes)
    records = []
    payload_by_record: dict[str, bytes] = {}
    for index, (relative, _digest, payload) in enumerate(members, start=1):
        record = _record(
            record_id=f"preservation-{index:04d}",
            source_kind="preservation-member",
            source_path=relative,
            payload=payload,
        )
        _credential_check(str(record["record_id"]), payload)
        records.append(record)
        payload_by_record[str(record["record_id"])] = payload
    by_path = {record["source_path"]: record for record in records}
    manifest_record = _record(
        record_id="preservation-manifest",
        source_kind="preservation-manifest",
        source_path="manifest.sha256",
        payload=manifest_bytes,
    )
    _credential_check("preservation-manifest", manifest_bytes)
    records.append(manifest_record)
    payload_by_record["preservation-manifest"] = manifest_bytes
    for selected in source.git_records:
        payload = git_reader.read(selected.commit, selected.path)
        if sha256_hex(payload) != selected.content_sha256:
            raise SourceMismatch(
                f"selected Git byte hash mismatch: {selected.commit}:{selected.path}"
            )
        _credential_check(selected.record_id, payload)
        if selected.already_preserved_path is not None:
            retained = by_path.get(selected.already_preserved_path)
            if (
                retained is None
                or retained["content_sha256"] != selected.content_sha256
            ):
                raise SourceMismatch(
                    f"Git record does not match preserved member: {selected.record_id}"
                )
            retained["git_provenance"] = {
                "record_id": selected.record_id,
                "source_commit": selected.commit,
                "source_path": selected.path,
            }
            continue
        record = _record(
            record_id=selected.record_id,
            source_kind="git-record",
            source_path=selected.path,
            source_commit=selected.commit,
            payload=payload,
        )
        records.append(record)
        payload_by_record[selected.record_id] = payload
    if len(records) != source.expected_total_records:
        raise SourceMismatch(
            f"total record count differs: expected {source.expected_total_records}, got {len(records)}"
        )
    assignments, attempts, outcomes, identity_records = _typed_links(
        source, records, payload_by_record
    )
    body: dict[str, object] = {
        "schema_version": "caplab-study-admission/1",
        "study_id": source.study_id,
        "disposition": "restricted-admission",
        "source": {
            "preservation_manifest_sha256": source.preservation_manifest_sha256,
        },
        "records": records,
        "assignments": assignments,
        "attempts": attempts,
        "outcomes": outcomes,
        "identity_records": identity_records,
        "summary": {
            "record_count": len(records),
            "unique_content_count": len(
                {record["content_sha256"] for record in records}
            ),
            "assignment_count": len(assignments),
            "attempt_count": len(attempts),
            "outcome_count": len(outcomes),
        },
    }
    body["manifest_sha256"] = sha256_hex(canonical_json(body))
    return body


def read_record_bytes(
    source: SourceSet, record: dict[str, object], *, git_reader: GitReader
) -> bytes:
    source_kind = record.get("source_kind")
    path = record.get("source_path")
    if not isinstance(path, str):
        raise SourceMismatch("record source path is absent")
    if source_kind == "git-record":
        commit = record.get("source_commit")
        if not isinstance(commit, str):
            raise SourceMismatch("Git record commit is absent")
        payload = git_reader.read(commit, path)
    elif source_kind == "preservation-manifest":
        payload = (source.preservation_root / "manifest.sha256").read_bytes()
    elif source_kind == "preservation-member":
        pure = PurePosixPath(path)
        absolute = source.preservation_root.joinpath(*pure.parts)
        if absolute.is_symlink() or not absolute.is_file():
            raise SourceMismatch(f"preservation member is missing or unsafe: {path}")
        payload = absolute.read_bytes()
    else:
        raise SourceMismatch(f"unsupported source kind: {source_kind!r}")
    if sha256_hex(payload) != record.get("content_sha256") or len(
        payload
    ) != record.get("byte_count"):
        raise SourceMismatch(
            f"source bytes changed for record {record.get('record_id')}"
        )
    _credential_check(str(record.get("record_id")), payload)
    return payload
