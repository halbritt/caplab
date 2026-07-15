"""Non-executing custody plans for state outside the active delete authority."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .canonical import canonical_json, sha256_hex
from .models import RegistrationReceipt


def _field(record: RegistrationReceipt | Mapping[str, Any], name: str) -> Any:
    if isinstance(record, RegistrationReceipt):
        return getattr(record, name)
    return record[name]


def build_cleanup_plan(
    record: RegistrationReceipt | Mapping[str, Any],
    *,
    registration_status: str = "complete",
) -> dict[str, Any]:
    if registration_status not in {"complete", "incomplete"}:
        raise ValueError("registration status must be complete or incomplete")
    object_key = _field(record, "object_key")
    body: dict[str, Any] = {
        "schema_version": "caplab-cleanup-plan/1",
        "campaign_id": _field(record, "campaign_id"),
        "operation_id": _field(record, "operation_id"),
        "registration_status": registration_status,
        "status": "quarantine-required",
        "deletions_authorized": False,
        "retained": {
            "content_sha256": _field(record, "content_sha256"),
            "object_key": object_key,
            "local_copy_key": (
                object_key
                if isinstance(record, RegistrationReceipt)
                else _field(record, "local_copy_key")
            ),
            "manifest_sha256": _field(record, "manifest_sha256"),
        },
        "permitted_completion_actions": [
            "revoke-campaign-keys",
            "remove-credential-files",
            "disable-postgres-login-roles",
            "lock-os-accounts",
        ],
        "requires_separate_authority": [
            "object-deletion",
            "local-copy-deletion",
            "application-row-deletion",
            "p5-fault-or-recovery-work",
        ],
    }
    return {**body, "plan_sha256": sha256_hex(canonical_json(body))}
