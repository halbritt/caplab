"""Structural and execution validity for advisory review observations."""
from __future__ import annotations

from ._tuner_vendored import VERDICTS

VALIDATION_VERSION = "review-response/1"


def response_error(doc: object) -> str | None:
    """Validate the response envelope, without judging finding correctness."""
    if not isinstance(doc, dict):
        return "invalid-json-object"
    verdict = doc.get("verdict")
    if not isinstance(verdict, str) or verdict not in VERDICTS:
        return "invalid-verdict"
    findings = doc.get("findings")
    if not isinstance(findings, list) or not all(isinstance(f, dict) for f in findings):
        return "invalid-findings"
    for finding in findings:
        for field in ("element_anchor", "text", "rationale"):
            if field in finding and not isinstance(finding[field], str):
                return f"invalid-finding-{field}"
    return None


def attempt_error(attempt: dict, *, require_manifest: bool = False) -> str | None:
    """A parsed answer from a failed process is not a completed observation."""
    if attempt.get("error"):
        return "transport-error"
    if attempt.get("timed_out") is not False:
        return "timeout-or-missing-status"
    if type(attempt.get("exit_code")) is not int or attempt["exit_code"] != 0:
        return "unsuccessful-exit"
    if require_manifest and attempt.get("manifest_verified") is not True:
        return "manifest-not-verified"
    return response_error(attempt.get("doc"))
