"""Governed Study 001 training-candidate manifest derivation."""

from __future__ import annotations

from typing import Any

from caplab.runtime.canonical import canonical_json, sha256_hex


IDENTITY_KINDS = {
    "corpus",
    "experiment",
    "order",
    "preservation-manifest",
    "result-csv",
    "result-record",
    "runtime",
    "subject",
    "task",
    "treatment",
    "verifier",
}


class CandidateManifestMismatch(RuntimeError):
    """Sealed lineage is incomplete, altered, or outside the Study 001 contract."""


def _content_body(document: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in document.items() if key != "manifest_sha256"}


def _validate_manifest_identity(document: dict[str, object], label: str) -> None:
    if document.get("manifest_sha256") != sha256_hex(canonical_json(_content_body(document))):
        raise CandidateManifestMismatch(f"{label} differs from its content identity")


def _validate_typed_identity(
    document: object, kind: str, mirrored_fields: tuple[str, ...]
) -> dict[str, Any]:
    if not isinstance(document, dict) or not isinstance(document.get("body"), dict):
        raise CandidateManifestMismatch(f"{kind} lineage is incomplete")
    body = document["body"]
    if (
        document.get("kind") != kind
        or document.get("identity_sha256") != sha256_hex(canonical_json(body))
    ):
        raise CandidateManifestMismatch(f"{kind} differs from its sealed identity")
    if any(document.get(field) != body.get(field) for field in mirrored_fields):
        raise CandidateManifestMismatch(f"{kind} mirrored lineage differs")
    return document


def _identity_index(registration: dict[str, object]) -> dict[str, dict[str, Any]]:
    records = registration.get("identity_records")
    if not isinstance(records, list):
        raise CandidateManifestMismatch("global identity lineage is absent")
    indexed: dict[str, dict[str, Any]] = {}
    for item in records:
        if not isinstance(item, dict) or not isinstance(item.get("body"), dict):
            raise CandidateManifestMismatch("global identity lineage is invalid")
        kind = item.get("kind")
        body = item["body"]
        if (
            not isinstance(kind, str)
            or kind in indexed
            or item.get("identity_sha256") != sha256_hex(canonical_json(body))
        ):
            raise CandidateManifestMismatch("global identity differs from its sealed body")
        indexed[kind] = item
    if set(indexed) != IDENTITY_KINDS:
        raise CandidateManifestMismatch("global identity kinds are incomplete or unexpected")
    return indexed


def _validate_recomputation(
    recomputation: dict[str, object], registration: dict[str, object]
) -> None:
    _validate_manifest_identity(recomputation, "recomputation")
    output = recomputation.get("output")
    historical = recomputation.get("historical_comparison")
    claims = recomputation.get("broader_claims")
    if (
        recomputation.get("schema_version") != "caplab-study-recomputation/1"
        or recomputation.get("study_id") != "caplab-study-001"
        or recomputation.get("assertion_type") != "observation"
        or recomputation.get("admission_manifest_sha256")
        != registration.get("manifest_sha256")
        or not isinstance(output, dict)
        or not isinstance(historical, dict)
        or not isinstance(claims, dict)
        or set(claims.values()) != {"unavailable"}
    ):
        raise CandidateManifestMismatch("recomputation is not the bound Study 001 observation")
    normalized = output.get("body")
    if not isinstance(normalized, dict):
        raise CandidateManifestMismatch("recomputation output is absent")
    digest = sha256_hex(canonical_json(normalized))
    if (
        output.get("normalized_result_sha256") != digest
        or historical.get("normalized_result_sha256") != digest
        or historical.get("status") != "byte-identical"
    ):
        raise CandidateManifestMismatch("recomputation output is not byte-identical")


def _is_failure(row: dict[str, Any]) -> str | None:
    attempt = row.get("attempt")
    if row.get("status") != "valid" or not (
        (isinstance(attempt, int) and not isinstance(attempt, bool) and attempt == 1)
        or attempt == "1"
    ):
        return "invalid-or-replaced-attempt"
    capture_exit = row.get("capture_exit")
    if not (
        (isinstance(capture_exit, int) and not isinstance(capture_exit, bool) and capture_exit == 0)
        or capture_exit == "0"
    ):
        return "provider-or-capture-failure"
    timed_out = row.get("timed_out")
    if not (timed_out is False or timed_out == "false"):
        return "provider-or-infrastructure-timeout"
    verifier_error = row.get("verifier_error")
    if not (verifier_error is False or verifier_error == "false"):
        return "verifier-failure"
    if row.get("observer_error") not in {None, ""}:
        return "observer-failure"
    return None


def _row_integer(value: object, label: str) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.isascii() and value.isdigit():
        return int(value)
    raise CandidateManifestMismatch(f"result row {label} is not an integer")


def _row_boolean(value: object, label: str) -> bool:
    if isinstance(value, bool):
        return value
    if value == "true":
        return True
    if value == "false":
        return False
    raise CandidateManifestMismatch(f"result row {label} is not a boolean")


def _candidate(
    assignment: dict[str, Any],
    attempt: dict[str, Any],
    outcome: dict[str, Any],
    evidence_identities: dict[str, str],
) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    body = outcome["body"]
    row = body.get("historical_result_row")
    observation = body.get("historical_observation")
    if (
        not isinstance(row, dict)
        or not isinstance(observation, dict)
        or body.get("human_disposition") != "not-recorded"
    ):
        return None, {
            "outcome_sha256": outcome["identity_sha256"],
            "reason": "incomplete-or-ambiguous-human-lineage",
        }
    if (
        _row_integer(row.get("sequence"), "sequence") != assignment["sequence"]
        or row.get("block") != assignment["block"]
        or row.get("task") != assignment["task"]
        or row.get("arm") != assignment["condition"]
    ):
        raise CandidateManifestMismatch("result row differs from its trial assignment")
    harmful = _row_boolean(row.get("harmful_shipment"), "harmful shipment")
    clean_guard = _row_boolean(row.get("clean_guard_passed"), "clean guard")
    if (
        observation.get("sequence") != assignment["sequence"]
        or observation.get("block") != assignment["block"]
        or observation.get("task") != assignment["task"]
        or observation.get("arm") != assignment["condition"]
        or observation.get("harmful_shipment") is not harmful
        or observation.get("clean_guard_passed") is not clean_guard
    ):
        raise CandidateManifestMismatch("result row differs from its sealed observation")
    failure = _is_failure(row)
    if failure is not None:
        return None, {
            "outcome_sha256": outcome["identity_sha256"],
            "reason": failure,
        }
    candidate_body: dict[str, object] = {
        "study_id": "caplab-study-001",
        "task_family": "checkout-retries",
        "split_group": "checkout-retries-study-001",
        "sequence": assignment["sequence"],
        "block": assignment["block"],
        "task": assignment["task"],
        "condition": assignment["condition"],
        "candidate_status": "derived-not-eligible",
        "lineage": {
            "assignment_sha256": assignment["identity_sha256"],
            "attempt_sha256": attempt["identity_sha256"],
            "outcome_sha256": outcome["identity_sha256"],
            "outcome_record_sha256": body.get("outcome_record_sha256"),
            "evidence_identity_sha256": evidence_identities,
        },
        "mechanical_label": {
            "harmful_shipment": harmful,
            "clean_guard_passed": clean_guard,
            "reward": row.get("reward", "not-present-in-result-row"),
        },
        "human_disposition": {
            "recorded_value": "not-recorded",
            "eligibility_effect": "unavailable",
        },
        "leakage_review": "unavailable-pending-human-eligibility",
    }
    candidate = dict(candidate_body)
    candidate["candidate_id"] = sha256_hex(canonical_json(candidate_body))
    return candidate, None


def build_candidate_manifest(
    recomputation: dict[str, object], registration: dict[str, object]
) -> dict[str, object]:
    """Derive auditable candidates without deciding eligibility, export, or use."""

    _validate_manifest_identity(registration, "admission manifest")
    if (
        registration.get("schema_version") != "caplab-study-admission/1"
        or registration.get("study_id") != "caplab-study-001"
        or registration.get("disposition") != "restricted-admission"
    ):
        raise CandidateManifestMismatch("admission manifest is not Study 001")
    _validate_recomputation(recomputation, registration)
    identities = _identity_index(registration)
    evidence_identities = {
        kind: str(record["identity_sha256"])
        for kind, record in sorted(identities.items())
    }
    assignments = registration.get("assignments")
    attempts = registration.get("attempts")
    outcomes = registration.get("outcomes")
    if not all(isinstance(items, list) and len(items) == 20 for items in (assignments, attempts, outcomes)):
        raise CandidateManifestMismatch("Study 001 trial lineage cardinality differs")
    typed_assignments = [
        _validate_typed_identity(item, "trial-assignment", ("sequence", "block", "task", "condition"))
        for item in assignments
    ]
    typed_attempts = [
        _validate_typed_identity(item, "attempt", ("assignment_sha256", "attempt_number"))
        for item in attempts
    ]
    typed_outcomes = [
        _validate_typed_identity(item, "mechanical-outcome", ("attempt_sha256",))
        for item in outcomes
    ]
    verifier_body = identities["verifier"]["body"]
    registered_outcomes = verifier_body.get("outcome_record_sha256")
    linked_outcomes = [
        item["body"].get("outcome_record_sha256") for item in typed_outcomes
    ]
    if (
        not isinstance(registered_outcomes, list)
        or not all(isinstance(item, str) for item in registered_outcomes)
        or not all(isinstance(item, str) for item in linked_outcomes)
        or sorted(registered_outcomes) != sorted(linked_outcomes)
    ):
        raise CandidateManifestMismatch("verifier lineage omits or substitutes an outcome")
    assignments_by_sha = {item["identity_sha256"]: item for item in typed_assignments}
    attempts_by_sha = {item["identity_sha256"]: item for item in typed_attempts}
    candidates: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for outcome in typed_outcomes:
        attempt = attempts_by_sha.get(outcome["attempt_sha256"])
        if attempt is None:
            raise CandidateManifestMismatch("outcome does not link to one sealed attempt")
        assignment = assignments_by_sha.get(attempt["assignment_sha256"])
        if assignment is None:
            raise CandidateManifestMismatch("attempt does not link to one sealed assignment")
        candidate, exclusion = _candidate(assignment, attempt, outcome, evidence_identities)
        if candidate is not None:
            candidates.append(candidate)
        if exclusion is not None:
            exclusions.append(exclusion)
    candidates.sort(key=lambda item: int(item["sequence"]))
    exclusions.sort(key=lambda item: str(item["outcome_sha256"]))
    body: dict[str, object] = {
        "schema_version": "caplab-training-candidate-manifest/1",
        "study_id": "caplab-study-001",
        "assertion_type": "candidate-manifest",
        "status": "eligibility-unavailable",
        "inputs": {
            "admission_manifest_sha256": registration["manifest_sha256"],
            "recomputation_manifest_sha256": recomputation["manifest_sha256"],
        },
        "split_policy": {
            "unit": "task-family-and-scenario-template",
            "group": "checkout-retries-study-001",
            "cross_split_reuse": "prohibited",
        },
        "exclusion_policy": {
            "provider_or_infrastructure_failure": "exclude",
            "compromised_instrument": "exclude",
            "ambiguous_human_judgment": "exclude",
            "incomplete_provenance": "exclude",
            "known_leakage": "exclude",
        },
        "candidates": candidates,
        "exclusions": exclusions,
        "human_gate": {
            "owner": "repository-owner",
            "eligibility": "pending",
            "export_authorization": "pending",
        },
        "prohibited_effects": {
            "eligibility": "unavailable",
            "export": "unavailable",
            "model_call": "unavailable",
            "training": "unavailable",
        },
    }
    result = dict(body)
    result["manifest_sha256"] = sha256_hex(canonical_json(body))
    return result
