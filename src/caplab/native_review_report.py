"""Inspect reviewer-authored units without deciding whether findings are true."""

import hashlib
import json
from pathlib import Path


SCHEMA = "caplab.native-code-review-report/v1"
TEXT_FIELDS = frozenset({"title", "claim", "trigger", "expected_behavior",
                         "observed_or_predicted_behavior", "change_attribution", "evidence"})
FINDING_FIELDS = TEXT_FIELDS | {"claim_status", "acceptance_effect", "locations"}


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _unique_fields(pairs):
    value = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate review field")
        value[key] = child
    return value


def _invalid_constant(value):
    raise ValueError("non-JSON numeric constant")


def _validate(document):
    if not isinstance(document, dict) or set(document) != {"schema", "findings", "limitations"} or document["schema"] != SCHEMA:
        raise ValueError("unexpected review report schema")
    if not isinstance(document["limitations"], list) or not all(isinstance(v, str) for v in document["limitations"]):
        raise ValueError("review limitations must be strings")
    if not isinstance(document["findings"], list):
        raise ValueError("review findings must be an array")
    for finding in document["findings"]:
        if not isinstance(finding, dict) or set(finding) != FINDING_FIELDS:
            raise ValueError("unexpected finding fields")
        if not all(isinstance(finding[key], str) for key in TEXT_FIELDS):
            raise ValueError("finding explanations must be strings")
        if finding["claim_status"] not in ("asserted", "uncertain", "withdrawn") or finding["acceptance_effect"] not in ("block", "advise", "undetermined"):
            raise ValueError("explicit reported stance and acceptance effect required")
        if not isinstance(finding["locations"], list):
            raise ValueError("finding locations must be an array")
        for location in finding["locations"]:
            if not isinstance(location, dict) or set(location) != {"path", "start_line", "end_line"}:
                raise ValueError("unexpected location fields")
            if not isinstance(location["path"], str) or type(location["start_line"]) is not int or type(location["end_line"]) is not int:
                raise ValueError("location path and line types are invalid")


def _location(location, source_root):
    relative = Path(location["path"])
    if relative.is_absolute() or ".." in relative.parts or "\x00" in location["path"]:
        return {"status": "unsafe-path"}
    try:
        path = (source_root / relative).resolve()
        if not path.is_relative_to(source_root):
            return {"status": "outside-source-root"}
        if not path.exists():
            return {"status": "missing"}
        if not path.is_file():
            return {"status": "not-a-file"}
        payload = path.read_bytes()
    except (OSError, RuntimeError) as exc:
        return {"status": "unavailable", "error_type": type(exc).__name__}
    lines = len(payload.splitlines())
    first, last = location["start_line"], location["end_line"]
    return {"status": "resolved" if 1 <= first <= last <= lines else "invalid-line-range",
            "file_sha256": _digest(payload), "file_lines": lines}


def inspect_report(raw: bytes, source_root: Path) -> dict:
    """Bind each complete finding to its report and inspect its own locations.

    The caller supplies an immutable, authorized source tree. A resolved line
    range establishes a locator, not semantic support or change attribution.
    """
    if not isinstance(raw, bytes) or len(raw) > 1024 * 1024:
        raise ValueError("review report must be at most one MiB of bytes")
    document = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_fields, parse_constant=_invalid_constant)
    _validate(document)
    root = Path(source_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("source root must be a directory")
    report_hash = _digest(raw)
    units = []
    for index, finding in enumerate(document["findings"]):
        canonical = json.dumps(finding, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        content_hash = _digest(canonical)
        units.append({"finding_index": index, "finding_sha256": content_hash,
            "finding_id": _digest(f"{report_hash}:{index}:{content_hash}".encode()),
            "reported": finding, "location_checks": [_location(value, root) for value in finding["locations"]]})
    return {"schema": "caplab.native-review-inspection/v1", "source_schema": SCHEMA,
            "raw_report_sha256": report_hash, "findings": units,
            "limitations": document["limitations"], "truth_assessed": False}
