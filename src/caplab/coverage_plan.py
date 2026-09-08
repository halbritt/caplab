"""Exact structural coverage over declared candidate metadata, without custody effects."""

from __future__ import annotations

from itertools import combinations


def _identifiers(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label}: expected a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{label}: identifiers must be non-empty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{label}: duplicate identifier")
    return value


def plan_shakedown_coverage(document: object) -> dict:
    """Find minimum cardinality and an exact-ID tie break, not study readiness."""
    if not isinstance(document, dict) or set(document) != {
        "schema_version", "requirements", "candidates"
    }:
        raise ValueError("expected schema_version, requirements and candidates")
    if document["schema_version"] != "caplab-shakedown-coverage-input/1":
        raise ValueError("unsupported shakedown coverage schema")
    requirements = sorted(_identifiers(document["requirements"], "requirements"))
    source = document["candidates"]
    if not isinstance(source, dict) or not 1 <= len(source) <= 24:
        raise ValueError("candidates: expected 1 to 24 entries")
    if any(not isinstance(key, str) or not key.strip() for key in source):
        raise ValueError("candidate identifiers must be non-empty strings")
    candidates = {}
    required = set(requirements)
    for name in sorted(source):
        tokens = set(_identifiers(source[name], f"candidate {name}"))
        if tokens - required:
            raise ValueError(f"candidate {name}: unknown requirements {sorted(tokens - required)}")
        candidates[name] = tokens
    witnesses = {token: [name for name, tokens in candidates.items() if token in tokens]
                 for token in requirements}
    missing = [token for token in requirements if not witnesses[token]]
    report = {
        "schema_version": "caplab-shakedown-coverage-report/1",
        "basis": "declared-metadata-only",
        "status": "uncovered-requirements" if missing else "covered",
        "requirements_without_candidate": missing,
        "selected": None,
        "candidate_remainder": None,
        "minimum_cardinality": None,
        "coverage_witnesses": {},
    }
    if missing:
        return report
    forced = {names[0] for names in witnesses.values() if len(names) == 1}
    covered = set().union(*(candidates[name] for name in forced))
    remaining = [name for name in candidates if name not in forced]
    bits = {token: 1 << index for index, token in enumerate(requirements)}
    masks = {name: sum(bits[token] for token in tokens) for name, tokens in candidates.items()}
    forced_mask = sum(bits[token] for token in covered)
    target = (1 << len(requirements)) - 1
    for size in range(len(remaining) + 1):
        for extra in combinations(remaining, size):
            mask = forced_mask
            for name in extra:
                mask |= masks[name]
            if mask == target:
                selected = sorted(forced.union(extra))
                report.update({
                    "selected": selected,
                    "candidate_remainder": [name for name in candidates if name not in selected],
                    "minimum_cardinality": len(selected),
                    "coverage_witnesses": {
                        token: [name for name in selected if token in candidates[name]]
                        for token in requirements
                    },
                })
                return report
    raise AssertionError("complete candidate union must have a cover")
