#!/usr/bin/env python3
"""Tailnet-local web bench for human adjudication of doctrine evaluations.

Serves a single-page UI over two work surfaces: the gold calibration queue
(``doctrine/evaluations/gold``) and the claim-to-source entailment screening
flags (``doctrine/evaluations/entailment``).

Epistemic framing (see ubiquitous_language.md): every model verdict shown or
joined here is a screening observation. The dispositions and flag audits this
server records are the human judgment surface; the server persists exactly
what the human dictated and never fabricates rationale, uncertainty, or
evidence.

Access is restricted to loopback and the Tailscale CGNAT range, judged by the
socket peer address only. Forwarded headers are never consulted.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime
import fcntl
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import threading
from typing import Any, Iterator
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker
import yaml

_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import entailment_eval  # noqa: E402

DEFAULT_PORT = 8788
DEFAULT_BIND = "0.0.0.0"
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
UI_FILENAME = "adjudication_ui.html"
GOLD_RELATIVE = Path("doctrine/evaluations/gold")
ENTAILMENT_RELATIVE = Path("doctrine/evaluations/entailment")
AUDIT_FILENAME = "human-audit.jsonl"
FRONTIER_REVIEW_FILENAME = "frontier-review.jsonl"
AUDIT_SCHEMA_VERSION = "entailment-human-audit/1"
FINDINGS = ("citation-holds", "citation-defective", "needs-deeper-review")
FLAG_VERDICTS = (
    "contradicted",
    "not_supported",
    "partially_supported",
    "insufficient_context",
    "unparseable",
    "quote_not_found",
)
BUILDER_TAIL_CHARS = 2000
BUILDER_TIMEOUT_SECONDS = 300
MAX_BODY_BYTES = 1 << 20

ALLOWED_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("100.64.0.0/10"),
)

# role-doctrine.md sections are shared by role family; authority-model.yaml
# role IDs map onto those headings explicitly so drift shows up as an
# unresolved reference rather than a silent mismatch.
ROLE_DOCTRINE_HEADINGS = {
    "coding-agent": "Coding and implementation agents",
    "implementation-agent": "Coding and implementation agents",
    "architecture-agent": "Architectural agents",
    "refactoring-agent": "Refactoring agents",
    "legacy-code-agent": "Legacy-code agents",
    "performance-agent": "Performance agents",
    "review-agent": "Review agents",
    "debugging-and-repair-agent": "Debugging and repair agents",
    "repository-assessment-agent": "Repository-assessment agents",
}

# Outcomes have no standalone record in a doctrine file; they are the required
# non-action outcomes defined by the gold queue builder. Each resolution below
# carries that provenance instead of pretending a doctrine file defines it.
OUTCOME_DEFINITIONS = {
    "abstention": (
        "Required non-action outcome: unresolved evidence or authority gaps "
        "require abstaining from selection or execution while preserving "
        "established observations."
    ),
    "insufficient-evidence": (
        "Required non-action outcome: supplied evidence fails the applicable "
        "proof obligation, so the correct output is an explicit "
        "insufficient-evidence disposition rather than a recommendation."
    ),
    "no-change": (
        "Required non-action outcome: evidence favors leaving the target "
        "unchanged, with a bounded rationale and a concrete revisit trigger."
    ),
}
OUTCOME_PROVENANCE = "doctrine/tools/build_gold_queue.py (required non-action outcomes)"


def client_allowed(address: str) -> bool:
    """Pure access guard over the socket peer address.

    Allows loopback (127.0.0.0/8, ::1) and the Tailscale CGNAT range
    (100.64.0.0/10). IPv4-mapped IPv6 peers are judged by their IPv4 form.
    Never consults forwarded headers.
    """
    candidate = address.split("%", 1)[0]
    try:
        ip: ipaddress.IPv4Address | ipaddress.IPv6Address = ipaddress.ip_address(
            candidate
        )
    except ValueError:
        return False
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        ip = mapped
    return any(
        ip.version == network.version and ip in network
        for network in ALLOWED_NETWORKS
    )


def utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def load_json_mapping(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def atomic_write(path: Path, data: bytes) -> None:
    """Write via temp file + rename in the destination directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.tmp-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with open(descriptor, "wb", closefd=True) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o644)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


class MutationLock:
    """One lock file guards every mutation this server performs.

    Combines an in-process threading lock (the HTTP server is threaded) with
    an ``fcntl`` flock so concurrent processes are also excluded.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self._thread_lock = threading.Lock()

    @contextmanager
    def acquire(self) -> Iterator[None]:
        with self._thread_lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a+", encoding="utf-8") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


# --- reference resolution -------------------------------------------------

_CONTEXT_CACHE_LOCK = threading.Lock()
_CONTEXT_CACHE: dict[Path, tuple[tuple, dict[str, Any]]] = {}


def _context_fingerprint(root: Path) -> tuple:
    paths = [
        root / "doctrine/sources.yaml",
        root / "doctrine/graph/nodes.yaml",
        root / "doctrine/graph/edges.yaml",
        root / "doctrine/graph/formulations.yaml",
        root / "doctrine/authority-model.yaml",
        root / "doctrine/context-lenses.yaml",
        root / "doctrine/routing-index.yaml",
        root / "doctrine/role-doctrine.md",
    ]
    paths.extend(sorted((root / "doctrine/concepts").glob("*.yaml")))
    key = []
    for path in paths:
        try:
            stat = path.stat()
            key.append((str(path), stat.st_mtime_ns, stat.st_size))
        except OSError:
            key.append((str(path), None, None))
    return tuple(key)


def _load_optional_mapping(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        return {}
    try:
        return load_yaml_mapping(path)
    except (OSError, ValueError, yaml.YAMLError):
        return {}


def build_context(root: Path) -> dict[str, Any]:
    """Indexes over every doctrine file candidate references resolve against."""
    fingerprint = _context_fingerprint(root)
    with _CONTEXT_CACHE_LOCK:
        cached = _CONTEXT_CACHE.get(root)
        if cached and cached[0] == fingerprint:
            return cached[1]

    sources = _load_optional_mapping(root, "doctrine/sources.yaml").get("sources", [])
    nodes = _load_optional_mapping(root, "doctrine/graph/nodes.yaml").get("nodes", [])
    edges = _load_optional_mapping(root, "doctrine/graph/edges.yaml").get("edges", [])
    formulations = _load_optional_mapping(root, "doctrine/graph/formulations.yaml").get(
        "formulations", []
    )
    authority = _load_optional_mapping(root, "doctrine/authority-model.yaml")
    lenses = _load_optional_mapping(root, "doctrine/context-lenses.yaml").get(
        "lenses", []
    )
    routing = _load_optional_mapping(root, "doctrine/routing-index.yaml")

    concepts: dict[str, dict[str, Any]] = {}
    concepts_dir = root / "doctrine/concepts"
    if concepts_dir.is_dir():
        for path in sorted(concepts_dir.glob("*.yaml")):
            try:
                document = load_yaml_mapping(path)
            except (OSError, ValueError, yaml.YAMLError):
                continue
            for concept in document.get("concepts", []):
                identifier = str(concept.get("id", ""))
                if identifier:
                    record = dict(concept)
                    record["_file"] = path.relative_to(root).as_posix()
                    concepts[identifier] = record

    role_doctrine_path = root / "doctrine/role-doctrine.md"
    role_doctrine_text = (
        role_doctrine_path.read_text(encoding="utf-8")
        if role_doctrine_path.is_file()
        else ""
    )

    context = {
        "sources": {str(item.get("id")): item for item in sources},
        "nodes": {str(item.get("id")): item for item in nodes},
        "edges": {str(item.get("id")): item for item in edges},
        "formulations": {str(item.get("id")): item for item in formulations},
        "role_defaults": authority.get("role_defaults", {}) or {},
        "levels": {
            str(level.get("id")): level for level in authority.get("levels", []) or []
        },
        "transitions": {
            f"{item.get('from')}->{item.get('to')}": item
            for item in authority.get("transitions", []) or []
        },
        "lenses": {str(item.get("id")): item for item in lenses},
        "lens_list": lenses,
        "risk_routes": routing.get("risk_routes", []) or [],
        "concepts": concepts,
        "role_doctrine_text": role_doctrine_text,
    }
    with _CONTEXT_CACHE_LOCK:
        _CONTEXT_CACHE[root] = (fingerprint, context)
    return context


def graph_locator_to_concept(locator: str) -> str:
    """Formulation locators use ``path#Heading``; sections resolve via ``::``."""
    if "#" in locator:
        path, heading = locator.split("#", 1)
        return f"{path} :: {heading}"
    return locator


def resolve_section(root: Path, locator: str) -> dict[str, Any]:
    resolution = entailment_eval.resolve_locator(root, locator)
    return {
        "locator": locator,
        "relative_path": resolution.relative_path,
        "heading": resolution.heading,
        "text": resolution.section_text,
        "error": resolution.error,
    }


def unresolved(reference: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "kind": reference.get("kind"),
        "id": reference.get("id"),
        "resolved": False,
        "unresolved_reason": reason,
        "raw": reference,
        "record": None,
        "evidence_paths": [],
    }


def resolve_reference(
    root: Path, context: dict[str, Any], reference: dict[str, Any]
) -> dict[str, Any]:
    """Best-effort resolution; unresolvable references stay visible."""
    kind = str(reference.get("kind", ""))
    identifier = str(reference.get("id", ""))
    resolved: dict[str, Any] = {
        "kind": kind,
        "id": identifier,
        "resolved": True,
        "record": None,
        "evidence_paths": [],
    }
    if kind == "source":
        record = context["sources"].get(identifier)
        if record is None:
            return unresolved(reference, "source id not present in sources.yaml")
        resolved["record"] = record
        resolved["evidence_paths"] = [f"doctrine/sources.yaml#{identifier}"]
        return resolved
    if kind == "formulation":
        record = context["formulations"].get(identifier)
        if record is None:
            return unresolved(
                reference, "formulation id not present in graph/formulations.yaml"
            )
        resolved["record"] = record
        resolved["evidence_paths"] = [f"doctrine/graph/formulations.yaml#{identifier}"]
        locator = str(record.get("locator", ""))
        if locator:
            section = resolve_section(root, graph_locator_to_concept(locator))
            resolved["section"] = section
            if section.get("error") is None:
                resolved["evidence_paths"].append(section["locator"])
        return resolved
    if kind == "node":
        record = context["nodes"].get(identifier)
        if record is None:
            return unresolved(reference, "node id not present in graph/nodes.yaml")
        resolved["record"] = record
        resolved["evidence_paths"] = [f"doctrine/graph/nodes.yaml#{identifier}"]
        concept = context["concepts"].get(identifier)
        if concept is not None:
            resolved["concept"] = concept
            resolved["evidence_paths"].append(f"{concept['_file']}#{identifier}")
        return resolved
    if kind == "edge":
        record = context["edges"].get(identifier)
        if record is None:
            return unresolved(reference, "edge id not present in graph/edges.yaml")
        resolved["record"] = record
        resolved["evidence_paths"] = [f"doctrine/graph/edges.yaml#{identifier}"]
        endpoints = {}
        for end in ("from", "to"):
            node = context["nodes"].get(str(record.get(end, "")))
            endpoints[end] = {
                "id": record.get(end),
                "label": node.get("label") if node else None,
                "definition": node.get("definition") if node else None,
            }
        resolved["endpoints"] = endpoints
        return resolved
    if kind == "lens":
        record = context["lenses"].get(identifier)
        if record is None:
            return unresolved(reference, "lens id not present in context-lenses.yaml")
        resolved["record"] = record
        resolved["evidence_paths"] = [f"doctrine/context-lenses.yaml#{identifier}"]
        return resolved
    if kind == "role":
        default = context["role_defaults"].get(identifier)
        if default is None:
            return unresolved(
                reference, "role id not present in authority-model.yaml role_defaults"
            )
        resolved["record"] = {"role_default": default}
        resolved["evidence_paths"] = [
            f"doctrine/authority-model.yaml#role_defaults.{identifier}"
        ]
        heading = ROLE_DOCTRINE_HEADINGS.get(identifier)
        section_text = None
        if heading and context["role_doctrine_text"]:
            section_text = entailment_eval.extract_section(
                context["role_doctrine_text"], heading
            )
        if heading and section_text is not None:
            resolved["doctrine_section"] = {"heading": heading, "text": section_text}
            resolved["evidence_paths"].append(f"doctrine/role-doctrine.md :: {heading}")
        else:
            resolved["doctrine_section"] = {
                "heading": heading,
                "text": None,
                "error": "no role-doctrine.md section mapped for this role",
            }
        return resolved
    if kind == "risk-class":
        lenses = [
            lens
            for lens in context["lens_list"]
            if identifier in (lens.get("routing", {}) or {}).get("risk_classes", [])
        ]
        routes = [
            route
            for route in context["risk_routes"]
            if str(route.get("risk_class", "")).casefold() == identifier.casefold()
        ]
        if not lenses and not routes:
            return unresolved(
                reference,
                "risk class not routed by any context lens or routing-index entry",
            )
        resolved["record"] = {
            "risk_class": identifier,
            "routed_by_lenses": [
                {
                    "id": lens.get("id"),
                    "title": lens.get("title"),
                    "risk_classes": (lens.get("routing", {}) or {}).get(
                        "risk_classes", []
                    ),
                }
                for lens in lenses
            ],
            "risk_routes": routes,
        }
        resolved["evidence_paths"] = [
            f"doctrine/context-lenses.yaml#{lens.get('id')}" for lens in lenses
        ]
        if routes:
            resolved["evidence_paths"].append(
                f"doctrine/routing-index.yaml#risk_routes.{identifier}"
            )
        return resolved
    if kind == "authority-transition":
        record = context["transitions"].get(identifier)
        if record is None:
            return unresolved(
                reference, "transition not present in authority-model.yaml transitions"
            )
        resolved["record"] = record
        resolved["evidence_paths"] = [
            f"doctrine/authority-model.yaml#transitions.{identifier}"
        ]
        resolved["levels"] = {
            "from": context["levels"].get(str(record.get("from", ""))),
            "to": context["levels"].get(str(record.get("to", ""))),
        }
        return resolved
    if kind == "outcome":
        definition = OUTCOME_DEFINITIONS.get(identifier)
        if definition is None:
            return unresolved(reference, "outcome has no registered definition")
        resolved["record"] = {
            "outcome": identifier,
            "definition": definition,
            "defined_by": OUTCOME_PROVENANCE,
        }
        resolved["evidence_paths"] = [
            f"doctrine/evaluations/gold/queue.json#outcome={identifier}"
        ]
        return resolved
    return unresolved(reference, f"unknown reference kind {kind!r}")


# --- entailment joins -----------------------------------------------------


def concept_formulation_id(record: dict[str, Any]) -> str | None:
    """Recompute the sync tool's F-CONCEPT id from an entailment record."""
    source_id = str(record.get("source_id") or "")
    concept_id = str(record.get("concept_id") or "")
    locator = str(record.get("locator") or "")
    contribution = str(record.get("contribution") or "")
    if not (source_id and concept_id and locator):
        return None
    stable_locator = re.sub(r" @@ occurrence=\d+$", "", locator)
    joined = "\0".join((concept_id, stable_locator, contribution)).encode()
    digest = hashlib.sha256(joined).hexdigest()[:12]
    return f"F-CONCEPT-{source_id.removeprefix('SRC-')}-{digest}"


def screening_for_formulations(
    formulation_ids: list[str],
    context: dict[str, Any],
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Entailment screening records matching the referenced formulations.

    Primary match recomputes the deterministic F-CONCEPT formulation id from
    each entailment record; fallback matches source id + cited locator against
    the formulation record.
    """
    wanted = set(formulation_ids)
    locator_targets: dict[tuple[str, str], str] = {}
    for formulation_id in formulation_ids:
        record = context["formulations"].get(formulation_id)
        if record is None:
            continue
        locator = graph_locator_to_concept(str(record.get("locator", "")))
        locator_targets[(str(record.get("source_id", "")), locator)] = formulation_id
    matches: list[dict[str, Any]] = []
    for result in results:
        basis = None
        computed = concept_formulation_id(result)
        if computed in wanted:
            basis = "formulation-id"
        else:
            key = (str(result.get("source_id", "")), str(result.get("locator", "")))
            if key in locator_targets:
                basis = "locator"
        if basis is None:
            continue
        entry = dict(result)
        entry["match_basis"] = basis
        entry["evidence_path"] = (
            "doctrine/evaluations/entailment/results.jsonl#key=" + str(result.get("key"))
        )
        matches.append(entry)
    return matches


# --- state assembly -------------------------------------------------------


def load_audits(root: Path) -> list[dict[str, Any]]:
    path = root / ENTAILMENT_RELATIVE / AUDIT_FILENAME
    audits: list[dict[str, Any]] = []
    if not path.is_file():
        return audits
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            audits.append(record)
    return audits


def load_frontier_reviews(root: Path) -> dict[str, dict[str, Any]]:
    """Latest frontier-model second opinion per entailment record key.

    These are model observations (reviewer kind ``model``), never human
    audits; they are displayed beside the local screening verdict only.
    """
    path = root / ENTAILMENT_RELATIVE / FRONTIER_REVIEW_FILENAME
    latest: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return latest
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and record.get("key"):
            latest[str(record["key"])] = record
    return latest


def load_gold_frontier_reviews(root: Path) -> dict[str, dict[str, Any]]:
    """Latest frontier-model second opinion per gold-queue candidate id.

    These are model observations (reviewer kind ``model``), never human
    dispositions; they are displayed beside the candidate only and are never
    copied into ``human-dispositions.json`` by the server.
    """
    path = root / GOLD_RELATIVE / FRONTIER_REVIEW_FILENAME
    latest: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return latest
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and record.get("candidate_id"):
            latest[str(record["candidate_id"])] = record
    return latest


def disposition_verdicts(root: Path) -> list[str]:
    schema = load_json_mapping(
        root / GOLD_RELATIVE / "human-dispositions.schema.json"
    )
    return list(
        schema["$defs"]["disposition"]["properties"]["verdict"]["enum"]
    )


def build_state(
    root: Path, *, pincite_root: Path | None = None
) -> dict[str, Any]:
    source_root = pincite_root or root
    context = build_context(source_root)
    queue_document = load_json_mapping(root / GOLD_RELATIVE / "queue.json")
    dispositions_document = load_json_mapping(
        root / GOLD_RELATIVE / "human-dispositions.json"
    )
    dispositions = [
        item
        for item in dispositions_document.get("dispositions", [])
        if isinstance(item, dict)
    ]
    dispositions_by_id = {str(item.get("candidate_id")): item for item in dispositions}
    results, _ = entailment_eval.load_records(root / ENTAILMENT_RELATIVE / "results.jsonl")
    audits = load_audits(root)
    frontier_reviews = load_frontier_reviews(root)
    gold_frontier_reviews = load_gold_frontier_reviews(root)
    latest_audit: dict[str, dict[str, Any]] = {}
    audit_counts: dict[str, int] = {}
    for audit in audits:
        key = str(audit.get("key", ""))
        latest_audit[key] = audit
        audit_counts[key] = audit_counts.get(key, 0) + 1

    queue: list[dict[str, Any]] = []
    for record in queue_document.get("records", []):
        candidate = record.get("candidate", {})
        target = candidate.get("target", {})
        references = [
            resolve_reference(source_root, context, reference)
            for reference in target.get("references", [])
        ]
        formulation_ids = [
            str(reference.get("id"))
            for reference in target.get("references", [])
            if reference.get("kind") == "formulation"
        ]
        screening = (
            screening_for_formulations(formulation_ids, context, results)
            if formulation_ids
            else []
        )
        queue.append(
            {
                "id": record.get("id"),
                "kind": candidate.get("kind"),
                "adjudication_mode": candidate.get("adjudication_mode"),
                "question": candidate.get("question"),
                "target": {"kind": target.get("kind"), "id": target.get("id")},
                "coverage": candidate.get("coverage", {}),
                "queue_machine_screening": record.get("machine_screening"),
                "human_disposition": record.get("human_disposition"),
                "disposition": dispositions_by_id.get(str(record.get("id"))),
                "frontier": gold_frontier_reviews.get(str(record.get("id"))),
                "references": references,
                "screening": screening,
            }
        )

    # Only current-generation flags reach the bench: a record is stale when
    # its judge semantics predate the harness's prompt version or its
    # contribution no longer matches the (possibly remediated) doctrine.
    # Stale flags remain in results.jsonl as history but are not work items.
    current_contributions = {
        (concept_id, str(support.get("locator", ""))): str(
            support.get("contribution", "")
        )
        for concept_id, concept in context["concepts"].items()
        for support in concept.get("source_support", [])
    }

    def record_is_current(record: dict[str, Any]) -> bool:
        if record.get("prompt_version") != entailment_eval.PROMPT_VERSION:
            return False
        expected = current_contributions.get(
            (str(record.get("concept_id")), str(record.get("locator")))
        )
        return expected is not None and expected == record.get("contribution")

    flags: list[dict[str, Any]] = []
    stale_hidden = 0
    for result in results:
        if result.get("verdict") not in FLAG_VERDICTS:
            continue
        if not record_is_current(result):
            stale_hidden += 1
            continue
        flag = dict(result)
        flag["section"] = resolve_section(
            source_root, str(result.get("locator", ""))
        )
        flag["relationship_meaning"] = entailment_eval.RELATIONSHIP_MEANINGS.get(
            str(result.get("relationship", "")),
            "unregistered relationship type",
        )
        key = str(result.get("key", ""))
        flag["audit"] = latest_audit.get(key)
        flag["audit_count"] = audit_counts.get(key, 0)
        flag["frontier"] = frontier_reviews.get(key)
        flag["evidence_path"] = (
            f"doctrine/evaluations/entailment/results.jsonl#key={key}"
        )
        flags.append(flag)

    progress = {
        "queue_total": len(queue),
        "queue_adjudicated": sum(1 for item in queue if item["disposition"]),
        "gold_frontier_reviewed": sum(1 for item in queue if item["frontier"]),
        "flags_total": len(flags),
        "flags_audited": sum(1 for flag in flags if flag["audit"]),
        "flags_stale_hidden": stale_hidden,
    }
    return {
        "generated_at": utc_now_iso(),
        "progress": progress,
        "queue": queue,
        "flags": flags,
        "dispositions": dispositions,
        "flag_audits": audits,
        "verdicts": disposition_verdicts(root),
        "findings": list(FINDINGS),
    }


# --- mutations ------------------------------------------------------------


class RequestError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def require_text(body: dict[str, Any], field: str) -> str:
    value = body.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RequestError(400, f"{field} must be a non-empty string")
    return value


def validated_disposition_body(
    body: dict[str, Any], verdicts: list[str]
) -> dict[str, Any]:
    candidate_id = require_text(body, "candidate_id")
    adjudicator_id = require_text(body, "adjudicator_id")
    verdict = require_text(body, "verdict")
    if verdict not in verdicts:
        raise RequestError(400, f"verdict must be one of: {', '.join(verdicts)}")
    rationale = require_text(body, "rationale")
    uncertainty = require_text(body, "uncertainty")
    evidence = body.get("evidence_reviewed")
    if (
        not isinstance(evidence, list)
        or not evidence
        or not all(isinstance(item, str) and item.strip() for item in evidence)
    ):
        raise RequestError(
            400, "evidence_reviewed must be a non-empty list of non-empty strings"
        )
    if len(set(evidence)) != len(evidence):
        raise RequestError(400, "evidence_reviewed entries must be unique")
    return {
        "candidate_id": candidate_id,
        "adjudicator_id": adjudicator_id,
        "verdict": verdict,
        "rationale": rationale,
        "uncertainty": uncertainty,
        "evidence_reviewed": list(evidence),
    }


def run_builder(builder_cmd: list[str], mode: str, root: Path) -> dict[str, Any]:
    command = [*builder_cmd, mode]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=root,
            timeout=BUILDER_TIMEOUT_SECONDS,
        )
        output = completed.stdout + completed.stderr
        returncode = completed.returncode
    except (OSError, subprocess.SubprocessError) as error:
        output = f"{type(error).__name__}: {error}"
        returncode = -1
    return {
        "command": " ".join(command),
        "returncode": returncode,
        "output_tail": output[-BUILDER_TAIL_CHARS:],
    }


def handle_disposition(
    root: Path,
    builder_cmd: list[str],
    lock: MutationLock,
    body: dict[str, Any],
) -> dict[str, Any]:
    verdicts = disposition_verdicts(root)
    cleaned = validated_disposition_body(body, verdicts)
    candidate_id = cleaned["candidate_id"]
    queue_path = root / GOLD_RELATIVE / "queue.json"
    queue_document = load_json_mapping(queue_path)
    candidates = {
        str(record.get("id")): record for record in queue_document.get("records", [])
    }
    if candidate_id not in candidates:
        raise RequestError(404, f"unknown candidate_id {candidate_id!r}")

    schema = load_json_mapping(root / GOLD_RELATIVE / "human-dispositions.schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    dispositions_path = root / GOLD_RELATIVE / "human-dispositions.json"

    with lock.acquire():
        document = load_json_mapping(dispositions_path)
        existing = {
            str(item.get("candidate_id"))
            for item in document.get("dispositions", [])
            if isinstance(item, dict)
        }
        if candidate_id in existing:
            raise RequestError(
                409, f"candidate {candidate_id!r} already has a human disposition"
            )
        # The disposition below is the human's dictated judgment verbatim;
        # the server adds only identity envelope and timestamp.
        disposition = {
            "candidate_id": candidate_id,
            "adjudicator": {"kind": "human", "id": cleaned["adjudicator_id"]},
            "adjudicated_at": utc_now_iso(),
            "verdict": cleaned["verdict"],
            "rationale": cleaned["rationale"],
            "evidence_reviewed": cleaned["evidence_reviewed"],
            "uncertainty": cleaned["uncertainty"],
        }
        updated = {
            "schema_version": document.get(
                "schema_version", "doctrine-gold-human-dispositions/1"
            ),
            "dispositions": [*document.get("dispositions", []), disposition],
        }
        errors = sorted(validator.iter_errors(updated), key=lambda e: list(e.path))
        if errors:
            location = (
                ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
            )
            raise RequestError(
                500,
                "refusing to write: updated human-dispositions.json would be "
                f"invalid at {location}: {errors[0].message}",
            )
        atomic_write(dispositions_path, json_bytes(updated))
        builder_write = run_builder(builder_cmd, "--write", root)
        builder_check = run_builder(builder_cmd, "--check", root)

    queue_status = None
    try:
        refreshed = load_json_mapping(queue_path)
        for record in refreshed.get("records", []):
            if str(record.get("id")) == candidate_id:
                queue_status = (record.get("human_disposition") or {}).get("status")
                break
    except (OSError, ValueError, json.JSONDecodeError):
        queue_status = None
    return {
        "recorded": True,
        "disposition": disposition,
        "builder_write": builder_write,
        "builder_check": builder_check,
        "queue_status": queue_status,
    }


def handle_flag_audit(
    root: Path, lock: MutationLock, body: dict[str, Any]
) -> dict[str, Any]:
    key = require_text(body, "key")
    finding = require_text(body, "finding")
    if finding not in FINDINGS:
        raise RequestError(400, f"finding must be one of: {', '.join(FINDINGS)}")
    reviewed_by = require_text(body, "reviewed_by")
    note = body.get("note", "")
    if not isinstance(note, str):
        raise RequestError(400, "note must be a string when present")
    results_path = root / ENTAILMENT_RELATIVE / "results.jsonl"
    records, _ = entailment_eval.load_records(results_path)
    by_key = {str(record.get("key")): record for record in records}
    if key not in by_key:
        raise RequestError(404, f"key {key!r} not present in results.jsonl")
    source = by_key[key]
    audit = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "key": key,
        "concept_id": source.get("concept_id"),
        "locator": source.get("locator"),
        "finding": finding,
        "note": note,
        "reviewed_by": reviewed_by,
        "reviewed_at": utc_now_iso(),
    }
    line = json.dumps(audit, ensure_ascii=False) + "\n"
    audit_path = root / ENTAILMENT_RELATIVE / AUDIT_FILENAME
    with lock.acquire():
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_path, "a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
    return {"recorded": True, "audit": audit}


# --- HTTP layer -----------------------------------------------------------


class AdjudicationServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        handler: type[BaseHTTPRequestHandler],
        *,
        repo_root: Path,
        builder_cmd: list[str],
        pincite_root: Path | None = None,
    ) -> None:
        super().__init__(address, handler)
        self.repo_root = repo_root
        self.pincite_root = pincite_root or repo_root
        self.builder_cmd = builder_cmd
        self.mutation_lock = MutationLock(
            repo_root / GOLD_RELATIVE / ".adjudication.lock"
        )


class AdjudicationHandler(BaseHTTPRequestHandler):
    server: AdjudicationServer
    protocol_version = "HTTP/1.1"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _guard(self) -> bool:
        if client_allowed(self.client_address[0]):
            return True
        self._send_json(
            403,
            {"error": "access limited to loopback and the tailnet (socket peer)"},
        )
        return False

    def _serve_ui(self) -> None:
        ui_path = Path(__file__).resolve().parent / UI_FILENAME
        if not ui_path.is_file():
            self._send_json(500, {"error": f"{UI_FILENAME} is missing"})
            return
        data = ui_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 (http.server contract)
        if not self._guard():
            return
        path = urlsplit(self.path).path
        if path in ("/", "/index.html"):
            self._serve_ui()
            return
        if path == "/api/state":
            try:
                self._send_json(
                    200,
                    build_state(
                        self.server.repo_root,
                        pincite_root=self.server.pincite_root,
                    ),
                )
            except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as err:
                self._send_json(500, {"error": f"failed to build state: {err}"})
            return
        self._send_json(404, {"error": f"unknown path {path!r}"})

    def _read_body(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise RequestError(400, "invalid Content-Length") from error
        if length <= 0:
            raise RequestError(400, "request body is required")
        if length > MAX_BODY_BYTES:
            raise RequestError(413, "request body too large")
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RequestError(400, "request body must be JSON") from error
        if not isinstance(body, dict):
            raise RequestError(400, "request body must be a JSON object")
        return body

    def do_POST(self) -> None:  # noqa: N802 (http.server contract)
        if not self._guard():
            return
        path = urlsplit(self.path).path
        try:
            body = self._read_body()
            if path == "/api/disposition":
                payload = handle_disposition(
                    self.server.repo_root,
                    self.server.builder_cmd,
                    self.server.mutation_lock,
                    body,
                )
            elif path == "/api/flag-audit":
                payload = handle_flag_audit(
                    self.server.repo_root, self.server.mutation_lock, body
                )
            else:
                raise RequestError(404, f"unknown path {path!r}")
        except RequestError as error:
            self._send_json(error.status, {"error": error.message})
            return
        except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
            self._send_json(500, {"error": str(error)})
            return
        self._send_json(200, payload)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        sys.stderr.write(
            "%s - - [%s] %s\n"
            % (self.client_address[0], self.log_date_time_string(), format % args)
        )


def default_builder_cmd(root: Path, pincite_root: Path) -> list[str]:
    return [
        "python3",
        str(root / "doctrine/tools/build_gold_queue.py"),
        "--root",
        str(root),
        "--pincite-root",
        str(pincite_root),
    ]


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--bind", default=DEFAULT_BIND)
    parser.add_argument(
        "--repo-root", type=Path, default=DEFAULT_ROOT, help="repository root"
    )
    parser.add_argument(
        "--pincite-root",
        type=Path,
        default=None,
        help="Pincite root containing doctrine and corpus evidence",
    )
    parser.add_argument(
        "--builder-cmd",
        default=None,
        help="gold queue builder command (server appends --write / --check)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_arguments(argv if argv is not None else sys.argv[1:])
    repo_root = arguments.repo_root.resolve()
    pincite_root = (arguments.pincite_root or repo_root).resolve()
    builder_cmd = (
        shlex.split(arguments.builder_cmd)
        if arguments.builder_cmd
        else default_builder_cmd(repo_root, pincite_root)
    )
    server = AdjudicationServer(
        (arguments.bind, arguments.port),
        AdjudicationHandler,
        repo_root=repo_root,
        builder_cmd=builder_cmd,
        pincite_root=pincite_root,
    )
    host, port = server.server_address[:2]
    print(
        f"doctrine adjudication bench on http://{host}:{port}/ "
        f"(repo {repo_root}); loopback + tailnet peers only",
        file=sys.stderr,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
