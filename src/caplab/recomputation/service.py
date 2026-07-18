"""Read-only reconstruction of the frozen CAPLAB Study 001 result."""

from __future__ import annotations

import csv
import io
import json
import re
from typing import Protocol

from caplab.runtime.canonical import canonical_json, sha256_hex

from .analysis import analyze_mutant_blocks


COMMIT = re.compile(r"\A[0-9a-f]{40}\Z")
MUTANT_BLOCKS = tuple(f"m{index}" for index in range(1, 9))
CLEAN_BLOCKS = ("c1", "c2")


class RecomputationMismatch(RuntimeError):
    """Registered metadata, immutable bytes, or normalized results disagree."""


class MetadataStore(Protocol):
    def get(self, manifest_sha256: str) -> dict[str, object] | None: ...
    def locator(self, content_sha256: str) -> dict[str, object] | None: ...


class ByteStore(Protocol):
    def read(self, key: str) -> bytes | None: ...


def _bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise RecomputationMismatch(f"{label} must be a boolean")
    return value


def _csv_bool(value: str | None, label: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise RecomputationMismatch(f"{label} must be true or false")


def _validate_content_identity(document: dict[str, object]) -> None:
    retained = document.get("manifest_sha256")
    body = {key: value for key, value in document.items() if key != "manifest_sha256"}
    if not isinstance(retained, str) or sha256_hex(canonical_json(body)) != retained:
        raise RecomputationMismatch("registration differs from its content identity")


def _validate_relational_identity(
    document: dict[str, object],
    *,
    kind: str,
    mirrored_fields: tuple[str, ...],
) -> None:
    body = document.get("body")
    identity = document.get("identity_sha256")
    if (
        document.get("kind") != kind
        or not isinstance(body, dict)
        or not isinstance(identity, str)
        or sha256_hex(canonical_json(body)) != identity
    ):
        raise RecomputationMismatch(f"{kind} identity differs from its frozen body")
    for field in mirrored_fields:
        if document.get(field) != body.get(field):
            raise RecomputationMismatch(f"{kind} field {field} differs from its frozen body")


def _normalized_result(rows: list[dict[str, object]]) -> dict[str, object]:
    if len(rows) != 20:
        raise RecomputationMismatch("Study 001 must contain exactly twenty outcomes")
    by_block_condition: dict[tuple[str, str], dict[str, object]] = {}
    for expected_sequence, row in enumerate(rows, start=1):
        if row.get("sequence") != expected_sequence:
            raise RecomputationMismatch("Study 001 outcome sequence is not complete")
        block = row.get("block")
        condition = row.get("condition")
        if not isinstance(block, str) or condition not in {"B", "V"}:
            raise RecomputationMismatch("outcome block or condition is invalid")
        key = (block, condition)
        if key in by_block_condition:
            raise RecomputationMismatch("outcome block and condition are duplicated")
        by_block_condition[key] = row
    expected_keys = {
        (block, condition)
        for block in MUTANT_BLOCKS + CLEAN_BLOCKS
        for condition in ("B", "V")
    }
    if set(by_block_condition) != expected_keys:
        raise RecomputationMismatch("Study 001 block pairs differ from the frozen design")
    for block in MUTANT_BLOCKS:
        for condition in ("B", "V"):
            if by_block_condition[(block, condition)]["task"] != "checkout-retries-m1":
                raise RecomputationMismatch("mutant block task differs from the frozen design")
    for block in CLEAN_BLOCKS:
        for condition in ("B", "V"):
            if by_block_condition[(block, condition)]["task"] != "checkout-retries-v2":
                raise RecomputationMismatch("clean block task differs from the frozen design")
    mutant_outcomes = tuple(
        (
            by_block_condition[(block, "B")]["harmful_shipment"],
            by_block_condition[(block, "V")]["harmful_shipment"],
        )
        for block in MUTANT_BLOCKS
    )
    clean_rows = [
        by_block_condition[(block, condition)]
        for block in CLEAN_BLOCKS
        for condition in ("B", "V")
    ]
    failure_fields = (
        "capture_failed",
        "timed_out",
        "verifier_failed",
        "observer_failed",
    )
    return {
        "schema_version": "caplab-study-001-normalized-result/1",
        "study_id": "caplab-study-001",
        "primary": analyze_mutant_blocks(mutant_outcomes),
        "clean_guard": {
            "b_pass_count": sum(
                row["clean_guard_passed"]
                for row in clean_rows
                if row["condition"] == "B"
            ),
            "v_pass_count": sum(
                row["clean_guard_passed"]
                for row in clean_rows
                if row["condition"] == "V"
            ),
            "arm_denominator": 2,
            "v_guard_passed": all(
                row["clean_guard_passed"]
                for row in clean_rows
                if row["condition"] == "V"
            ),
        },
        "failure_classifications": {
            field: sum(row[field] for row in rows) for field in failure_fields
        },
    }


class RecomputationService:
    def __init__(
        self,
        metadata: MetadataStore,
        objects: ByteStore,
        copies: ByteStore,
    ) -> None:
        self.metadata = metadata
        self.objects = objects
        self.copies = copies

    def _verified_bytes(
        self, record: dict[str, object], records_by_digest: dict[str, dict[str, object]]
    ) -> bytes:
        digest = record.get("content_sha256")
        representative = records_by_digest.get(digest)
        if not isinstance(digest, str) or representative is None:
            raise RecomputationMismatch("registered evidence record identity is invalid")
        for field in ("object_key", "local_copy_key", "byte_count"):
            if representative.get(field) != record.get(field):
                raise RecomputationMismatch(
                    "one content identity has conflicting registered locators"
                )
        locator = self.metadata.locator(digest)
        expected_locator = {
            "object_key": record.get("object_key"),
            "local_copy_key": record.get("local_copy_key"),
            "byte_count": record.get("byte_count"),
        }
        if locator != expected_locator:
            raise RecomputationMismatch("registered byte locator differs from the manifest")
        object_key = record.get("object_key")
        copy_key = record.get("local_copy_key")
        if not isinstance(object_key, str) or not isinstance(copy_key, str):
            raise RecomputationMismatch("registered byte locator is invalid")
        object_bytes = self.objects.read(object_key)
        copy_bytes = self.copies.read(copy_key)
        if object_bytes is None or sha256_hex(object_bytes) != digest:
            raise RecomputationMismatch("registered object bytes are missing or altered")
        if copy_bytes is None or sha256_hex(copy_bytes) != digest:
            raise RecomputationMismatch("independent copy bytes are missing or altered")
        if object_bytes != copy_bytes or len(object_bytes) != record.get("byte_count"):
            raise RecomputationMismatch("registered immutable byte copies disagree")
        return object_bytes

    def _observation_rows(
        self,
        manifest: dict[str, object],
        records_by_digest: dict[str, dict[str, object]],
    ) -> tuple[list[dict[str, object]], list[str]]:
        assignments = manifest.get("assignments")
        attempts = manifest.get("attempts")
        outcomes = manifest.get("outcomes")
        if not all(isinstance(value, list) for value in (assignments, attempts, outcomes)):
            raise RecomputationMismatch("registration has no complete relational links")
        assert isinstance(assignments, list)
        assert isinstance(attempts, list)
        assert isinstance(outcomes, list)
        if (len(assignments), len(attempts), len(outcomes)) != (20, 20, 20):
            raise RecomputationMismatch("registration relational cardinality differs")
        for assignment in assignments:
            if not isinstance(assignment, dict):
                raise RecomputationMismatch("registered assignment is invalid")
            _validate_relational_identity(
                assignment,
                kind="trial-assignment",
                mirrored_fields=("sequence", "block", "task", "condition"),
            )
        for attempt in attempts:
            if not isinstance(attempt, dict):
                raise RecomputationMismatch("registered attempt is invalid")
            _validate_relational_identity(
                attempt,
                kind="attempt",
                mirrored_fields=("assignment_sha256", "attempt_number"),
            )
        for outcome in outcomes:
            if not isinstance(outcome, dict):
                raise RecomputationMismatch("registered outcome is invalid")
            _validate_relational_identity(
                outcome,
                kind="mechanical-outcome",
                mirrored_fields=("attempt_sha256",),
            )
        assignments_by_sha = {
            assignment.get("identity_sha256"): assignment
            for assignment in assignments
            if isinstance(assignment, dict)
        }
        attempts_by_sha = {
            attempt.get("identity_sha256"): attempt
            for attempt in attempts
            if isinstance(attempt, dict)
        }
        if len(assignments_by_sha) != 20 or len(attempts_by_sha) != 20:
            raise RecomputationMismatch("registration relational identities are invalid")
        rows: list[dict[str, object]] = []
        outcome_digests: list[str] = []
        for outcome in outcomes:
            if not isinstance(outcome, dict) or not isinstance(outcome.get("body"), dict):
                raise RecomputationMismatch("registered outcome is invalid")
            outcome_body = outcome["body"]
            assert isinstance(outcome_body, dict)
            attempt = attempts_by_sha.get(outcome.get("attempt_sha256"))
            if not isinstance(attempt, dict):
                raise RecomputationMismatch("outcome does not link to one frozen attempt")
            assignment = assignments_by_sha.get(attempt.get("assignment_sha256"))
            if not isinstance(assignment, dict):
                raise RecomputationMismatch("attempt does not link to one frozen assignment")
            digest = outcome_body.get("outcome_record_sha256")
            record = records_by_digest.get(digest)
            if not isinstance(digest, str) or record is None:
                raise RecomputationMismatch("outcome byte record is not registered")
            payload = self._verified_bytes(record, records_by_digest)
            try:
                observed = json.loads(payload)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise RecomputationMismatch("outcome record is not valid UTF-8 JSON") from error
            if not isinstance(observed, dict) or canonical_json(observed) != canonical_json(
                outcome_body.get("historical_observation")
            ):
                raise RecomputationMismatch("outcome metadata differs from immutable bytes")
            sequence = assignment.get("sequence")
            block = assignment.get("block")
            task = assignment.get("task")
            condition = assignment.get("condition")
            if (
                observed.get("sequence") != sequence
                or observed.get("block") != block
                or observed.get("task") != task
                or observed.get("arm") != condition
            ):
                raise RecomputationMismatch("outcome differs from its frozen assignment")
            errors = observed.get("errors")
            if not isinstance(errors, dict):
                raise RecomputationMismatch("outcome has no frozen failure classification")
            capture_exit = errors.get("capture_exit")
            if not isinstance(capture_exit, int) or isinstance(capture_exit, bool):
                raise RecomputationMismatch("capture exit must be an integer")
            rows.append(
                {
                    "sequence": sequence,
                    "block": block,
                    "task": task,
                    "condition": condition,
                    "harmful_shipment": _bool(
                        observed.get("harmful_shipment"), "harmful shipment"
                    ),
                    "clean_guard_passed": _bool(
                        observed.get("clean_guard_passed"), "clean guard"
                    ),
                    "capture_failed": capture_exit != 0,
                    "timed_out": _bool(errors.get("timed_out"), "timed out"),
                    "verifier_failed": _bool(
                        errors.get("verifier_error"), "verifier error"
                    ),
                    "observer_failed": errors.get("observer_error") is not None,
                }
            )
            outcome_digests.append(digest)
        rows.sort(key=lambda row: int(row["sequence"]))
        return rows, outcome_digests

    def _historical_rows(
        self,
        record: dict[str, object],
        records_by_digest: dict[str, dict[str, object]],
    ) -> list[dict[str, object]]:
        payload = self._verified_bytes(record, records_by_digest)
        try:
            source_rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8"))))
        except UnicodeDecodeError as error:
            raise RecomputationMismatch("registered result CSV is not UTF-8") from error
        rows: list[dict[str, object]] = []
        for expected_sequence, source in enumerate(source_rows, start=1):
            try:
                sequence = int(source.get("sequence", ""))
                capture_exit = int(source.get("capture_exit", ""))
            except ValueError as error:
                raise RecomputationMismatch("result CSV integer field is invalid") from error
            if sequence != expected_sequence or source.get("status") != "valid":
                raise RecomputationMismatch("result CSV sequence or status differs")
            if source.get("attempt") != "1":
                raise RecomputationMismatch("result CSV is not the frozen first attempt")
            rows.append(
                {
                    "sequence": sequence,
                    "block": source.get("block"),
                    "task": source.get("task"),
                    "condition": source.get("arm"),
                    "harmful_shipment": _csv_bool(
                        source.get("harmful_shipment"), "CSV harmful shipment"
                    ),
                    "clean_guard_passed": _csv_bool(
                        source.get("clean_guard_passed"), "CSV clean guard"
                    ),
                    "capture_failed": capture_exit != 0,
                    "timed_out": _csv_bool(source.get("timed_out"), "CSV timed out"),
                    "verifier_failed": _csv_bool(
                        source.get("verifier_error"), "CSV verifier error"
                    ),
                    "observer_failed": bool(source.get("observer_error")),
                }
            )
        return rows

    def recompute(
        self, manifest_sha256: str, *, implementation_commit: str
    ) -> dict[str, object]:
        if not COMMIT.fullmatch(implementation_commit):
            raise ValueError("implementation commit must be forty lowercase hexadecimal characters")
        manifest = self.metadata.get(manifest_sha256)
        if manifest is None:
            raise RecomputationMismatch("Study 001 admission manifest is not registered")
        _validate_content_identity(manifest)
        if manifest.get("study_id") != "caplab-study-001":
            raise RecomputationMismatch("registered study identity differs")
        records = manifest.get("records")
        if not isinstance(records, list):
            raise RecomputationMismatch("registration has no evidence records")
        typed_records = [record for record in records if isinstance(record, dict)]
        if len(typed_records) != len(records):
            raise RecomputationMismatch("registration contains an invalid evidence record")
        if any(record.get("disposition") != "restricted-admission" for record in typed_records):
            raise RecomputationMismatch("registration contains a non-restricted disposition")
        records_by_digest: dict[str, dict[str, object]] = {}
        for record in typed_records:
            digest = record.get("content_sha256")
            if not isinstance(digest, str):
                raise RecomputationMismatch("registration has an invalid content identity")
            retained = records_by_digest.setdefault(digest, record)
            for field in ("object_key", "local_copy_key", "byte_count"):
                if retained.get(field) != record.get(field):
                    raise RecomputationMismatch(
                        "one content identity has conflicting registered locators"
                    )
        result_csv = next(
            (record for record in typed_records if record.get("record_id") == "result-csv"),
            None,
        )
        if result_csv is None:
            raise RecomputationMismatch("registered historical result CSV is absent")
        observation_rows, outcome_digests = self._observation_rows(
            manifest, records_by_digest
        )
        recomputed = _normalized_result(observation_rows)
        historical = _normalized_result(
            self._historical_rows(result_csv, records_by_digest)
        )
        recomputed_bytes = canonical_json(recomputed)
        historical_bytes = canonical_json(historical)
        if recomputed_bytes != historical_bytes:
            raise RecomputationMismatch(
                "recomputed result differs from the registered historical result"
            )
        result_sha256 = sha256_hex(recomputed_bytes)
        body: dict[str, object] = {
            "schema_version": "caplab-study-recomputation/1",
            "study_id": "caplab-study-001",
            "assertion_type": "observation",
            "admission_manifest_sha256": manifest_sha256,
            "inputs": {
                "result_csv_sha256": result_csv["content_sha256"],
                "outcome_record_sha256": sorted(outcome_digests),
            },
            "code": {
                "repository": "halbritt/caplab",
                "commit": implementation_commit,
            },
            "output": {
                "normalized_result_sha256": result_sha256,
                "body": recomputed,
            },
            "historical_comparison": {
                "normalized_result_sha256": sha256_hex(historical_bytes),
                "status": "byte-identical",
            },
            "failure_policy": {
                "missing_mutant_outcome": "analysis-undefined",
                "registered_byte_mismatch": "quarantine",
                "historical_result_mismatch": "quarantine",
            },
            "broader_claims": {
                "capability_inference": "unavailable",
                "cross_task_capability": "unavailable",
                "universal_ranking": "unavailable",
                "preference": "unavailable",
                "striatum_placement": "unavailable",
                "training_eligibility": "unavailable",
            },
        }
        result = dict(body)
        result["manifest_sha256"] = sha256_hex(canonical_json(body))
        return result
