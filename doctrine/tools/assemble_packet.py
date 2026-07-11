#!/usr/bin/env python3
"""Assemble a deterministic doctrine evidence packet from the routing index.

The assembler implements the routing index ``selection_order`` for a stated
role, task, and decision question:

1. canonical role aliases and task families/variants are resolved;
2. the universal safety kernel and the role/task baseline are nominated;
3. complete question phrases, repository signals, task variants, languages, and
   risk classes nominate additional routes;
4. role, task-family, language, risk, and exclusion gates filter nominations;
5. prerequisite closure is selected under an explicit relative-cost budget;
6. procedures, lenses, prohibitions, evidence classes, authority constraints,
   change types, conflicts, and claim-level provenance are attached.

Every nominated concept dropped by a gate is recorded in the packet's
``excluded_candidates`` with the nomination source and the specific failing
condition, per the retrieval contract in ``doctrine/README.md``.

Signal matching. Free-text ``--signal`` values are matched against activation
and exclusion conditions case-insensitively after whitespace normalization: a
signal matches a condition when it equals the condition or contains the whole
condition as a substring. Keyword overlap short of the whole condition never
matches. Signals nominate or exclude doctrine; they never satisfy evidence.

Prerequisite interpretation. This CLI cannot inspect a target repository, so
it cannot verify evidence-shaped prerequisites. The interpretation used here:

- a route prerequisite that names another concept record is pulled into the
  activated set (transitively), because the operationalization contract says a
  packet contains "the activated concept and its prerequisites"; prerequisite
  pulls bypass role/task gates but still honor language and exclusion gates,
  and an unloadable prerequisite is recorded in ``excluded_candidates`` and as
  an unmet evidence obligation;
- every other prerequisite and each concept ``required_evidence`` item becomes
  a typed obligation. Only a schema-valid ``evidence-record/1`` supplied with
  ``--evidence`` can discharge it; unresolved obligations remain explicit.

Delivery profiles. The default ``compact`` profile emits only canonical packet
records: obligations replace the old flattened missing-evidence list, and
claim-level provenance replaces flattened formulation and locator lists.
``--detail full`` adds those derived lists under ``audit_views`` for audit and
migration consumers. The retrieval budget uses relative routing-cost units for
concept selection only; it is explicitly not a byte, word, or tokenizer token
limit. Compact delivery size is guarded independently by contract tests.

Corpus version. ``corpus_version`` is derived from repository data only:
``corpus-<traceability corpus_snapshot_date>-<digest>`` where the digest is the
first 12 hex characters of sha256 over the newline-joined, sorted
``source_sha256`` values in ``doctrine/sources.yaml``.

Identity and determinism. ``doctrine_version`` hashes all decision-bearing
doctrine inputs, ``retriever_version`` hashes this assembler, and ``packet_id``
is derived from the canonical packet content. The packet contains no generated
timestamp or randomness; identical inputs produce byte-identical output.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "runtime" / "evidence-packet.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "runtime" / "evidence-record.schema.json"
PACKET_SCHEMA_VERSION = "evidence-packet/2"

CORE_PROHIBITIONS = (
    "prohibit-generic-doctrine-over-local-contract",
    "prohibit-authority-inference-from-access",
)

# The libyaml loader parses the large routing and graph artifacts an order of
# magnitude faster; both loaders produce identical plain-Python documents.
SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        document = yaml.load(stream, Loader=SAFE_LOADER)
    if not isinstance(document, dict):
        raise ValueError(f"{path}: expected a mapping at document root")
    return document


def load_json_schema(path: Path) -> dict[str, Any]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(schema, dict):
        raise ValueError(f"{path}: expected a schema object")
    return schema


def packet_schema_validator() -> jsonschema.Draft202012Validator:
    packet_schema = load_json_schema(SCHEMA_PATH)
    evidence_schema = load_json_schema(EVIDENCE_SCHEMA_PATH)
    resolver = jsonschema.RefResolver.from_schema(
        packet_schema,
        store={evidence_schema["$id"]: evidence_schema},
    )
    return jsonschema.Draft202012Validator(packet_schema, resolver=resolver)


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def matching_signal(condition: str, signals: list[str]) -> str | None:
    """Return the first signal that matches an index condition, else None."""
    normalized_condition = normalize(condition)
    for signal in signals:
        normalized_signal = normalize(signal)
        if (
            normalized_condition == normalized_signal
            or normalized_condition in normalized_signal
        ):
            return signal
    return None


def phrase_in_text(phrase: str, text: str) -> bool:
    """Match a complete normalized phrase, never a substring inside a word."""
    normalized_phrase = normalize(phrase)
    normalized_text = normalize(text)
    if not normalized_phrase:
        return False
    pattern = (
        r"(?<!\w)" + re.escape(normalized_phrase).replace(r"\ ", r"\s+") + r"(?!\w)"
    )
    return re.search(pattern, normalized_text) is not None


class Corpus:
    """Read-only view over the doctrine artifacts the assembler consumes."""

    def __init__(self) -> None:
        self.routing = load_yaml(ROOT / "routing-index.yaml")
        self.routes = {
            route["concept_id"]: route for route in self.routing["concept_routes"]
        }
        self.role_bundles = {
            bundle["role"]: bundle for bundle in self.routing["role_bundles"]
        }
        self.task_bundles = {
            bundle["task"]: bundle for bundle in self.routing["task_bundles"]
        }
        self.role_aliases = {
            alias: record["role"]
            for record in self.routing.get("role_registry", [])
            for alias in [record["role"], *record.get("aliases", [])]
        }
        self.task_aliases = {
            alias: record["family"]
            for record in self.routing.get("task_registry", [])
            for alias in [record["family"], *record.get("aliases", [])]
        }
        self.task_variants = {
            record["family"]: set(record.get("variants", []))
            for record in self.routing.get("task_registry", [])
        }
        self.concepts: dict[str, dict[str, Any]] = {}
        for path in sorted((ROOT / "concepts").glob("*.yaml")):
            for concept in load_yaml(path).get("concepts", []):
                self.concepts[concept["id"]] = concept
        self.conflicts = {
            record["conflict_id"]: record
            for record in load_yaml(ROOT / "conflicts.yaml").get("conflicts", [])
        }
        self.nodes = load_yaml(ROOT / "graph" / "nodes.yaml").get("nodes", [])
        self.formulations = load_yaml(ROOT / "graph" / "formulations.yaml").get(
            "formulations", []
        )
        self.edges = load_yaml(ROOT / "graph" / "edges.yaml").get("edges", [])
        self.sources = load_yaml(ROOT / "sources.yaml").get("sources", [])
        self.traceability = load_yaml(ROOT / "traceability.yaml")
        self.procedures = {
            record["id"]: record
            for record in load_yaml(ROOT / "procedures.yaml").get("procedures", [])
        }
        self.lenses = {
            record["id"]: record
            for record in load_yaml(ROOT / "context-lenses.yaml").get("lenses", [])
        }
        self.prohibitions = {
            record["id"]: record
            for record in load_yaml(ROOT / "negative-doctrine.yaml").get(
                "prohibitions", []
            )
        }
        self.evidence_classes = {
            record["id"]: record
            for record in load_yaml(ROOT / "evidence-taxonomy.yaml").get("classes", [])
        }
        self.authority = load_yaml(ROOT / "authority-model.yaml")
        self.change_types = {
            record["id"]: record
            for record in load_yaml(ROOT / "change-types.yaml").get("types", [])
        }

    def corpus_version(self) -> str:
        hashes = sorted(source["source_sha256"] for source in self.sources)
        digest = hashlib.sha256("\n".join(hashes).encode("utf-8")).hexdigest()[:12]
        snapshot_date = str(self.traceability["corpus_snapshot_date"])
        return f"corpus-{snapshot_date}-{digest}"

    def doctrine_version(self) -> str:
        paths = [
            ROOT / "routing-index.yaml",
            ROOT / "procedures.yaml",
            ROOT / "context-lenses.yaml",
            ROOT / "negative-doctrine.yaml",
            ROOT / "conflicts.yaml",
            ROOT / "evidence-taxonomy.yaml",
            ROOT / "authority-model.yaml",
            ROOT / "change-types.yaml",
            ROOT / "runtime" / "evidence-packet.schema.json",
            ROOT / "runtime" / "evidence-record.schema.json",
            ROOT / "graph" / "nodes.yaml",
            ROOT / "graph" / "formulations.yaml",
            ROOT / "graph" / "edges.yaml",
            *sorted((ROOT / "concepts").glob("*.yaml")),
        ]
        digest = hashlib.sha256()
        for path in sorted(paths):
            digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        return "doctrine-" + digest.hexdigest()[:16]


@dataclass(frozen=True)
class RetrievalRequest:
    """Canonical request values used by selection, assembly, and rendering."""

    requested_role: str
    role: str
    requested_task: str
    task_family: str
    task_variants: tuple[str, ...]
    requested_lenses: tuple[str, ...]
    question: str
    signals: tuple[str, ...]
    languages: tuple[str, ...]
    risk: str | None
    retrieval_budget: int
    detail: str


def language_gate_failure(route: dict[str, Any], languages: list[str]) -> str | None:
    route_languages = {
        normalize(route_language)
        for route_language in route.get("activate_for_languages", [])
    }
    if "language-independent" in route_languages:
        return None
    if route_languages & {
        normalize(requested_language) for requested_language in languages
    }:
        return None
    return (
        f"route languages {sorted(route_languages)} include neither "
        f"'language-independent' nor a requested language {sorted(languages)}"
    )


def exclusion_failure(route: dict[str, Any], signals: list[str]) -> str | None:
    for condition in route.get("exclude_when", []):
        if normalize(condition) == "never":
            continue
        signal = matching_signal(condition, signals)
        if signal is not None:
            return f"exclude_when condition '{condition}' matched signal '{signal}'"
    return None


def additional_gate_failures(
    route: dict[str, Any],
    request: RetrievalRequest,
    nomination_reasons: list[str],
) -> list[str]:
    """Gates that apply only to concepts nominated outside the baseline."""
    failures: list[str] = []
    if request.role not in route.get(
        "activate_for_role_families", route.get("activate_for_roles", [])
    ):
        failures.append(f"role '{request.role}' not in activate_for_roles")
    primary_family = request.task_family in route.get("activate_for_task_families", [])
    conditional_family = request.task_family in route.get(
        "conditional_for_task_families", []
    )
    contextual_task_match = request.task_family in route.get(
        "activate_for_tasks", []
    ) or any(
        reason.startswith(("question term", "task variant"))
        for reason in nomination_reasons
    )
    if not primary_family and not (conditional_family and contextual_task_match):
        failures.append(
            f"task '{request.task_family}' not in activate_for_tasks/task_families"
        )
    if request.risk is not None:
        risk_classes = {
            normalize(risk_class)
            for risk_class in route.get("activate_for_risk_classes", [])
        }
        if "all" not in risk_classes and normalize(request.risk) not in risk_classes:
            failures.append(
                f"risk class '{request.risk}' not in activate_for_risk_classes"
            )
    return failures


class Selection:
    def __init__(self) -> None:
        self.activated: dict[str, list[str]] = {}
        self.excluded: dict[str, str] = {}
        self.excluded_prerequisites: set[str] = set()


def select_concepts(corpus: Corpus, request: RetrievalRequest) -> Selection:
    role = request.role
    task_family = request.task_family
    signals = list(request.signals)
    languages = list(request.languages)
    risk = request.risk
    role_bundle = corpus.role_bundles[role]
    task_bundle = corpus.task_bundles[task_family]
    always_load = list(corpus.routing["always_load"]["concepts"])
    baseline = sorted(
        (
            set(role_bundle.get("core_concepts", []))
            | set(role_bundle.get("default_concepts", []))
        )
        & set(task_bundle.get("primary_concepts", []))
    )
    protected = set(always_load) | set(baseline)

    nominations: dict[str, list[str]] = {}

    def nominate(concept_id: str, source: str) -> None:
        if concept_id not in corpus.routes:
            return
        reasons = nominations.setdefault(concept_id, [])
        if source not in reasons:
            reasons.append(source)

    for concept_id in always_load:
        nominate(concept_id, "always-load core concept")
    for concept_id in baseline:
        nominate(concept_id, "role bundle intersected with task bundle")
    for concept_id in sorted(corpus.routes):
        route = corpus.routes[concept_id]
        for term in corpus.concepts[concept_id].get("retrieval_terms", []):
            if phrase_in_text(term, request.question):
                nominate(concept_id, f"question term '{term}'")
                break
        for variant in route.get("activate_for_tasks", []):
            if variant in request.task_variants:
                nominate(concept_id, f"task variant '{variant}'")
                break
        for condition in route.get("activate_for_repository_signals", []):
            signal = matching_signal(condition, signals)
            if signal is not None:
                nominate(
                    concept_id,
                    f"signal '{signal}' matched activation signal '{condition}'",
                )
                break
    for bundle in corpus.routing.get("language_bundles", []):
        if normalize(bundle["language"]) in {
            normalize(requested_language) for requested_language in languages
        }:
            for concept_id in bundle.get("concepts", []):
                nominate(concept_id, f"language bundle '{bundle['language']}'")
    if risk is not None:
        for risk_route in corpus.routing.get("risk_routes", []):
            if normalize(risk_route["risk_class"]) == normalize(risk):
                for concept_id in risk_route.get("concepts", []):
                    nominate(concept_id, f"risk route '{risk_route['risk_class']}'")

    selection = Selection()
    for concept_id in sorted(nominations):
        route = corpus.routes[concept_id]
        failures: list[str] = []
        if concept_id not in protected:
            failures.extend(
                additional_gate_failures(route, request, nominations[concept_id])
            )
        language_failure = language_gate_failure(route, languages)
        if language_failure is not None:
            failures.append(language_failure)
        excluded_by = exclusion_failure(route, signals)
        if excluded_by is not None:
            failures.append(excluded_by)
        if failures:
            nominated = "; ".join(nominations[concept_id])
            selection.excluded[concept_id] = (
                f"nominated by: {nominated}; dropped: " + "; ".join(failures)
            )
        else:
            selection.activated[concept_id] = nominations[concept_id]

    expand_prerequisites(corpus, selection, signals, languages)
    return selection


def expand_prerequisites(
    corpus: Corpus, selection: Selection, signals: list[str], languages: list[str]
) -> None:
    """Pull concept prerequisites in and record any that cannot be loaded."""
    queue = sorted(selection.activated)
    processed: set[str] = set()
    while queue:
        concept_id = queue.pop(0)
        if concept_id in processed:
            continue
        processed.add(concept_id)
        route = corpus.routes[concept_id]
        for prerequisite in route.get("prerequisites", []):
            if prerequisite in corpus.concepts:
                if prerequisite in selection.activated:
                    continue
                prerequisite_route = corpus.routes[prerequisite]
                failures = []
                language_failure = language_gate_failure(prerequisite_route, languages)
                if language_failure is not None:
                    failures.append(language_failure)
                excluded_by = exclusion_failure(prerequisite_route, signals)
                if excluded_by is not None:
                    failures.append(excluded_by)
                if failures:
                    selection.excluded[prerequisite] = (
                        f"nominated by: prerequisite of {concept_id}; dropped: "
                        + "; ".join(failures)
                    )
                    selection.excluded_prerequisites.add(
                        f"{prerequisite} (prerequisite concept excluded) — required by {concept_id}"
                    )
                else:
                    selection.excluded.pop(prerequisite, None)
                    selection.activated[prerequisite] = [
                        f"prerequisite of {concept_id}"
                    ]
                    queue.append(prerequisite)


def ordered_concepts(corpus: Corpus, activated: dict[str, list[str]]) -> list[str]:
    """Core routes first, then ascending retrieval budget hint, then ID."""

    def key(concept_id: str) -> tuple[int, int, str]:
        route = corpus.routes[concept_id]
        core_rank = 0 if route.get("retrieval_priority") == "core" else 1
        return (core_rank, route.get("retrieval_budget_hint", 0), concept_id)

    return sorted(activated, key=key)


def apply_retrieval_budget(
    corpus: Corpus, selection: Selection, requested: int
) -> tuple[list[str], dict[str, Any], list[dict[str, Any]]]:
    """Select a prerequisite-closed concept set within relative routing cost."""
    active = set(selection.activated)

    def concept_prerequisite_closure(concept_id: str) -> set[str]:
        prerequisite_closure: set[str] = set()
        queue = [concept_id]
        while queue:
            current = queue.pop()
            if current in prerequisite_closure or current not in active:
                continue
            prerequisite_closure.add(current)
            for prerequisite in corpus.routes[current].get("prerequisites", []):
                if prerequisite in corpus.concepts:
                    queue.append(prerequisite)
        return prerequisite_closure

    always = set(corpus.routing["always_load"]["concepts"])
    mandatory: set[str] = set()
    for concept_id in always:
        mandatory.update(concept_prerequisite_closure(concept_id))

    def concept_cost(concept_ids: set[str]) -> int:
        return sum(
            int(corpus.routes[concept_id].get("retrieval_budget_hint", 0))
            for concept_id in concept_ids
        )

    minimum = concept_cost(mandatory)
    if requested < minimum:
        raise ValueError(
            f"retrieval budget {requested} is below mandatory core cost {minimum}"
        )

    selected = set(mandatory)
    used = minimum
    priority_rank = {"core": 0, "high": 1, "normal": 2, "specialist": 3}

    def candidate_key(concept_id: str) -> tuple[int, int, int, str]:
        reasons = selection.activated[concept_id]
        contextual = any(
            reason.startswith(
                (
                    "question term",
                    "signal ",
                    "task variant",
                    "language bundle",
                    "risk route",
                )
            )
            for reason in reasons
        )
        baseline = "role bundle intersected with task bundle" in reasons
        nomination_rank = 0 if contextual else 1 if baseline else 2
        route = corpus.routes[concept_id]
        return (
            nomination_rank,
            priority_rank.get(route.get("retrieval_priority", "normal"), 4),
            int(route.get("retrieval_budget_hint", 0)),
            concept_id,
        )

    budget_excluded: list[dict[str, Any]] = []
    for concept_id in sorted(active - mandatory, key=candidate_key):
        required_concepts = concept_prerequisite_closure(concept_id) - selected
        required_cost = concept_cost(required_concepts)
        if used + required_cost <= requested:
            selected.update(required_concepts)
            used += required_cost
        else:
            budget_excluded.append(
                {
                    "id": concept_id,
                    "cost": required_cost,
                    "reason": (
                        f"requires {required_cost} relative routing-cost units with prerequisites; "
                        f"only {requested - used} remain"
                    ),
                }
            )

    for concept_id in active - selected:
        selection.activated.pop(concept_id, None)
    ordered = ordered_concepts(corpus, selection.activated)
    budget = {
        "unit": "relative-routing-cost-unit",
        "scope": "activated-concept-selection-only",
        "meaning": (
            "Relative doctrine-selection cost; not a byte, word, or tokenizer-measured "
            "context limit. Delivery size is governed separately by the selected "
            "detail profile."
        ),
        "requested": requested,
        "minimum_required": minimum,
        "used": used,
        "remaining": requested - used,
    }
    return (
        ordered,
        budget,
        sorted(
            (
                exclusion
                for exclusion in budget_excluded
                if exclusion["id"] not in selected
            ),
            key=lambda exclusion: exclusion["id"],
        ),
    )


def collect_conflicts(corpus: Corpus, activated: set[str]) -> list[str]:
    conflict_ids: set[str] = set()
    for concept_id in activated:
        conflict_ids.update(corpus.concepts[concept_id].get("conflicts", []))
    for edge in corpus.edges:
        if "conflict_ref" not in edge:
            continue
        if edge.get("from") in activated or edge.get("to") in activated:
            conflict_ids.add(edge["conflict_ref"])
    return sorted(conflict_ids)


def collect_formulations(corpus: Corpus, activated: set[str]) -> list[str]:
    node_ids = {
        node["id"]
        for node in corpus.nodes
        if node["id"] in activated or activated & set(node.get("doctrine_refs", []))
    }
    formulation_ids: set[str] = set()
    for node in corpus.nodes:
        if node["id"] in node_ids:
            formulation_ids.update(node.get("formulations", []))
    for formulation in corpus.formulations:
        if any(
            mapping.get("node_id") in node_ids
            for mapping in formulation.get("mappings", [])
        ):
            formulation_ids.add(formulation["id"])
    return sorted(formulation_ids)


def canonical_locator(locator: str) -> str:
    if " :: " in locator:
        return locator
    if "#" in locator:
        path, heading = locator.split("#", 1)
        return f"{path} :: {heading}"
    return locator


def collect_source_locators(
    corpus: Corpus, activated: set[str], formulation_ids: list[str]
) -> list[str]:
    locators: set[str] = set()
    for concept_id in activated:
        for support in corpus.concepts[concept_id].get("source_support", []):
            locators.add(canonical_locator(support["locator"]))
    wanted = set(formulation_ids)
    for formulation in corpus.formulations:
        if formulation["id"] in wanted:
            locators.add(canonical_locator(formulation["locator"]))
    return sorted(locators)


def collect_provenance_links(
    corpus: Corpus, activated_ids: list[str]
) -> list[dict[str, Any]]:
    formulation_ids_by_concept: dict[str, set[str]] = {
        concept_id: set() for concept_id in activated_ids
    }
    for formulation in corpus.formulations:
        for mapping in formulation.get("mappings", []):
            concept_id = mapping.get("node_id")
            if concept_id in formulation_ids_by_concept:
                formulation_ids_by_concept[concept_id].add(formulation["id"])

    links = []
    for concept_id in activated_ids:
        support = []
        for source_support in corpus.concepts[concept_id].get("source_support", []):
            support.append(
                {
                    "source_id": source_support["source_id"],
                    "relationship": source_support["relationship"],
                    "locator": canonical_locator(source_support["locator"]),
                    "contribution": source_support["contribution"],
                }
            )
        links.append(
            {
                "concept_id": concept_id,
                "formulation_ids": sorted(formulation_ids_by_concept[concept_id]),
                "source_support": sorted(
                    support,
                    key=lambda source_support: (
                        source_support["source_id"],
                        source_support["locator"],
                        source_support["relationship"],
                    ),
                ),
            }
        )
    return links


def content_address_packet(packet: dict[str, Any]) -> dict[str, Any]:
    canonical = json.dumps(
        packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        **packet,
        "packet_content_sha256": digest,
        "packet_id": f"pkt-{digest[:16]}",
    }


def activated_lenses(
    corpus: Corpus, request: RetrievalRequest
) -> tuple[list[str], dict[str, list[str]]]:
    allowed = set(corpus.role_bundles[request.role].get("context_lenses", []))
    selected: dict[str, list[str]] = {}
    for lens_id in request.requested_lenses:
        selected[lens_id] = ["explicit lens selection"]
    for language in request.languages:
        lens_id = f"lens-{normalize(language)}"
        if lens_id in allowed and lens_id in corpus.lenses:
            selected.setdefault(lens_id, []).append(f"language '{language}'")
    for lens_id in sorted(allowed):
        lens = corpus.lenses[lens_id]
        for condition in lens.get("activation_evidence", []):
            signal = matching_signal(condition, list(request.signals))
            if signal is not None:
                selected.setdefault(lens_id, []).append(
                    f"signal '{signal}' matched lens evidence '{condition}'"
                )
                break
    return sorted(selected), selected


def activated_prohibitions(corpus: Corpus, task_family: str) -> list[str]:
    selected = {
        prohibition_id
        for prohibition_id in CORE_PROHIBITIONS
        if prohibition_id in corpus.prohibitions
    }
    task_words = set(normalize(task_family).replace("-", " ").split())
    for prohibition_id, record in corpus.prohibitions.items():
        scopes = " ".join(record.get("applies_when", []))
        if task_words & set(normalize(scopes).replace("-", " ").split()):
            selected.add(prohibition_id)
    return sorted(selected)


def obligation_records(
    corpus: Corpus,
    activated_ids: list[str],
    evidence_class_ids: list[str],
    evidence_records: list[dict[str, Any]],
    task_family: str,
) -> list[dict[str, Any]]:
    obligations: set[tuple[str, str]] = set()
    activated = set(activated_ids)
    for concept_id in activated_ids:
        route = corpus.routes[concept_id]
        for prerequisite in route.get("prerequisites", []):
            if prerequisite not in corpus.concepts or prerequisite not in activated:
                obligations.add((concept_id, prerequisite))
        for requirement in corpus.concepts[concept_id].get("required_evidence", []):
            obligations.add((concept_id, requirement))
    for evidence_class in evidence_class_ids:
        obligations.add((f"task:{task_family}", evidence_class))

    obligation_mappings = []
    for required_by, requirement in sorted(obligations):
        matched = []
        if requirement not in corpus.concepts:
            for evidence in evidence_records:
                satisfies = {
                    normalize(claim) for claim in evidence.get("satisfies", [])
                }
                if normalize(requirement) in satisfies or requirement == evidence.get(
                    "evidence_class"
                ):
                    matched.append(evidence["id"])
        digest = hashlib.sha256(
            f"{required_by}\0{requirement}".encode("utf-8")
        ).hexdigest()[:16]
        obligation_mappings.append(
            {
                "obligation_id": f"obl-{digest}",
                "requirement": requirement,
                "required_by": required_by,
                "evidence_ids": sorted(matched),
                "status": "satisfied" if matched else "missing",
            }
        )
    return obligation_mappings


def read_evidence_records(
    paths: list[Path], corpus: Corpus
) -> tuple[list[dict[str, Any]], list[str]]:
    schema = load_json_schema(EVIDENCE_SCHEMA_PATH)
    validator = jsonschema.Draft202012Validator(schema)
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_ids: set[str] = set()
    for path in paths:
        path_errors: list[str] = []
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path}: unable to read evidence record: {error}")
            continue
        for validation_error in sorted(
            validator.iter_errors(record),
            key=lambda schema_error: list(schema_error.path),
        ):
            location = ".".join(str(part) for part in validation_error.path)
            path_errors.append(
                f"{path}{'.' + location if location else ''}: "
                f"{validation_error.message}"
            )
        if (
            isinstance(record, dict)
            and record.get("evidence_class") not in corpus.evidence_classes
        ):
            path_errors.append(
                f"{path}: unknown evidence_class '{record.get('evidence_class')}'"
            )
        if path_errors:
            errors.extend(path_errors)
            continue
        evidence_id = record["id"]
        if evidence_id in seen_ids:
            errors.append(f"{path}: duplicate evidence record ID '{evidence_id}'")
            continue
        seen_ids.add(evidence_id)
        records.append(record)
    return sorted(records, key=lambda evidence_record: evidence_record["id"]), errors


def assemble_packet(
    corpus: Corpus,
    request: RetrievalRequest,
    evidence_records: list[dict[str, Any]],
) -> tuple[dict[str, Any], Selection]:
    selection = select_concepts(corpus, request)
    activated_ids, budget_record, budget_excluded = apply_retrieval_budget(
        corpus, selection, request.retrieval_budget
    )
    activated_set = set(activated_ids)
    corpus_version = corpus.corpus_version()
    doctrine_version = corpus.doctrine_version()
    retriever_version = (
        "retriever-" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
    )
    lens_ids, lens_reasons = activated_lenses(corpus, request)
    procedure_ids = sorted(
        set(corpus.task_bundles[request.task_family].get("procedures", []))
        | (
            {"proc-assess-authority-to-act"}
            if "proc-assess-authority-to-act" in corpus.procedures
            else set()
        )
    )
    evidence_class_ids = sorted(
        evidence_class_id
        for evidence_class_id in corpus.task_bundles[request.task_family].get(
            "evidence", []
        )
        if evidence_class_id in corpus.evidence_classes
    )
    authority_constraints = {
        "artifact": "authority-model.yaml",
        **corpus.authority["role_defaults"][request.role],
    }
    prohibition_ids = activated_prohibitions(corpus, request.task_family)
    change_type_ids = sorted(
        change_type_id
        for change_type_id in corpus.task_bundles[request.task_family].get(
            "change_types", []
        )
        if change_type_id in corpus.change_types
    )
    doctrine_artifacts = sorted(corpus.routing["always_load"]["artifacts"])
    obligations = obligation_records(
        corpus, activated_ids, evidence_class_ids, evidence_records, request.task_family
    )
    packet = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "question": request.question,
        "corpus_version": corpus_version,
        "doctrine_version": doctrine_version,
        "retriever_version": retriever_version,
        "retrieval_context": {
            "requested_role": request.requested_role,
            "canonical_role": request.role,
            "requested_task": request.requested_task,
            "task_family": request.task_family,
            "task_variants": sorted(request.task_variants),
            "requested_lenses": sorted(request.requested_lenses),
            "signals": sorted(request.signals),
            "languages": sorted(request.languages),
            "risk_class": request.risk,
            "detail": request.detail,
            "evidence_ids": [record["id"] for record in evidence_records],
            "retrieval_budget": request.retrieval_budget,
        },
        "retrieval_budget": budget_record,
        "budget_excluded": budget_excluded,
        "activated_concepts": activated_ids,
        "activated_procedures": procedure_ids,
        "activated_lenses": lens_ids,
        "activated_prohibitions": prohibition_ids,
        "required_evidence_classes": evidence_class_ids,
        "authority_constraints": authority_constraints,
        "applicable_change_types": change_type_ids,
        "doctrine_artifacts": doctrine_artifacts,
        "evidence_records": evidence_records,
        "evidence_obligations": obligations,
        "activation_reasons": [
            {"id": concept_id, "reasons": sorted(selection.activated[concept_id])}
            for concept_id in activated_ids
        ]
        + [
            {"id": lens_id, "reasons": sorted(lens_reasons[lens_id])}
            for lens_id in lens_ids
        ]
        + [
            {
                "id": procedure_id,
                "reasons": [f"procedure for task family '{request.task_family}'"],
            }
            for procedure_id in procedure_ids
        ]
        + [
            {
                "id": prohibition_id,
                "reasons": [
                    "core prohibition"
                    if prohibition_id in CORE_PROHIBITIONS
                    else f"applies to task family '{request.task_family}'"
                ],
            }
            for prohibition_id in prohibition_ids
        ]
        + [
            {
                "id": evidence_class,
                "reasons": [f"required by task family '{request.task_family}'"],
            }
            for evidence_class in evidence_class_ids
        ]
        + [
            {
                "id": change_type,
                "reasons": [f"applicable to task family '{request.task_family}'"],
            }
            for change_type in change_type_ids
        ]
        + [
            {"id": artifact, "reasons": ["always-load doctrine artifact"]}
            for artifact in doctrine_artifacts
        ],
        "provenance_links": collect_provenance_links(corpus, activated_ids),
        "conflicts": collect_conflicts(corpus, activated_set),
        "excluded_candidates": [
            {"id": concept_id, "reason": selection.excluded[concept_id]}
            for concept_id in sorted(selection.excluded)
        ],
    }
    if request.detail == "full":
        formulation_ids = collect_formulations(corpus, activated_set)
        missing_evidence = sorted(
            {
                f"{obligation['requirement']} — required by {obligation['required_by']}"
                for obligation in obligations
                if obligation["status"] == "missing"
            }
            | {
                excluded_prerequisite
                for excluded_prerequisite in selection.excluded_prerequisites
                if "(prerequisite concept excluded)" in excluded_prerequisite
            }
        )
        packet["audit_views"] = {
            "formulations": formulation_ids,
            "missing_evidence": missing_evidence,
            "source_locators": collect_source_locators(
                corpus, activated_set, formulation_ids
            ),
        }
    return content_address_packet(packet), selection


PRECEDENCE_PREAMBLE = (
    "Precedence: explicit human authorization and stop conditions, then accepted "
    "repository contracts, tests, decisions, and current runtime facts, precede all "
    "doctrine below. This packet is retrieved guidance: it can justify a question, "
    "investigation, proposal, or bounded action; retrieval never creates authority "
    "to select, execute, verify, or accept a change."
)


def render_markdown(corpus: Corpus, packet: dict[str, Any]) -> str:
    context_record = packet["retrieval_context"]
    provenance_by_concept = {
        record["concept_id"]: record for record in packet["provenance_links"]
    }
    lines: list[str] = []
    lines.append("# Doctrine evidence packet")
    lines.append("")
    lines.append(
        f"- Packet: {packet['packet_id']} · Corpus: {packet['corpus_version']}"
    )
    lines.append(f"- Question: {packet['question']}")
    context = (
        f"- Role: {context_record['canonical_role']} · "
        f"Task: {context_record['task_family']} · "
        f"Languages: {', '.join(context_record['languages'])}"
    )
    if context_record["risk_class"] is not None:
        context += f" · Risk: {context_record['risk_class']}"
    if context_record["signals"]:
        context += f" · Signals: {'; '.join(context_record['signals'])}"
    lines.append(context)
    budget = packet["retrieval_budget"]
    lines.append(
        f"- Detail: {context_record['detail']} · Selection cost: "
        f"{budget['used']}/{budget['requested']} {budget['unit']}"
    )
    lines.append("")
    lines.append(PRECEDENCE_PREAMBLE)
    lines.append("")

    lines.append(f"## Activated concepts ({len(packet['activated_concepts'])})")
    for concept_id in packet["activated_concepts"]:
        concept = corpus.concepts[concept_id]
        route = corpus.routes[concept_id]
        lines.append("")
        lines.append(f"### {concept_id} ({route.get('retrieval_priority', 'normal')})")
        lines.append(f"- Claim: {concept['claim']}")
        lines.append(f"- Decision rule: {concept['decision_rule']}")
        provenance = provenance_by_concept[concept_id]
        source_refs = "; ".join(
            f"{support['source_id']} [{support['relationship']}] {support['locator']}"
            for support in provenance["source_support"]
        )
        lines.append(f"- Source support: {source_refs}")

    lines.append("")
    lines.append("## Operational layers")
    for title, field in (
        ("Procedures", "activated_procedures"),
        ("Lenses", "activated_lenses"),
        ("Prohibitions", "activated_prohibitions"),
        ("Evidence classes", "required_evidence_classes"),
        ("Change types", "applicable_change_types"),
    ):
        values = packet[field]
        lines.append(f"- {title}: {', '.join(values) if values else 'none'}")
    authority = packet["authority_constraints"]
    lines.append(f"- Authority ceiling: {authority['usual_ceiling']}")
    for constraint in authority["constraints"]:
        lines.append(f"  - {constraint}")

    lines.append("")
    lines.append(f"## Activation reasons ({len(packet['activation_reasons'])})")
    for record in packet["activation_reasons"]:
        lines.append(f"- {record['id']}: {'; '.join(record['reasons'])}")

    missing_obligations = [
        record
        for record in packet["evidence_obligations"]
        if record["status"] == "missing"
    ]
    lines.append("")
    lines.append(f"## Unmet evidence obligations ({len(missing_obligations)})")
    for record in missing_obligations:
        lines.append(f"- {record['required_by']}: {record['requirement']}")

    lines.append("")
    lines.append(f"## Conflicts ({len(packet['conflicts'])})")
    for conflict_id in packet["conflicts"]:
        lines.append(f"- {conflict_id}")

    if "audit_views" in packet:
        audit = packet["audit_views"]
        lines.append("")
        lines.append("## Expanded audit views")
        for title, field in (
            ("Formulations", "formulations"),
            ("Missing evidence", "missing_evidence"),
            ("Source locators", "source_locators"),
        ):
            lines.append("")
            lines.append(f"### {title} ({len(audit[field])})")
            for audit_entry in audit[field]:
                lines.append(f"- {audit_entry}")
    lines.append("")
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> list[str]:
    validator = packet_schema_validator()
    errors = []
    for validation_error in sorted(
        validator.iter_errors(packet),
        key=lambda schema_error: list(schema_error.path),
    ):
        location = ".".join(str(part) for part in validation_error.path)
        errors.append(
            f"packet{'.' + location if location else ''}: {validation_error.message}"
        )
    return errors


def serialize_packet(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble a deterministic, schema-conformant doctrine evidence packet."
    )
    parser.add_argument(
        "--role", required=True, help="agent role ID from the routing index"
    )
    parser.add_argument("--task", required=True, help="task ID from the routing index")
    parser.add_argument(
        "--task-variant",
        action="append",
        default=[],
        help="fine-grained task variant from the selected task family (repeatable)",
    )
    parser.add_argument(
        "--lens",
        action="append",
        default=[],
        help="explicit context lens ID (repeatable)",
    )
    parser.add_argument("--question", required=True, help="free-text decision question")
    parser.add_argument(
        "--signal",
        action="append",
        default=[],
        help="repository activation signal (repeatable; never satisfies evidence obligations)",
    )
    parser.add_argument(
        "--evidence",
        action="append",
        type=Path,
        default=[],
        help="typed evidence-record/1 JSON file (repeatable)",
    )
    parser.add_argument(
        "--language",
        action="append",
        default=[],
        help="repository language (repeatable; default language-independent)",
    )
    parser.add_argument("--risk", default=None, help="declared risk class")
    parser.add_argument(
        "--budget",
        type=int,
        default=None,
        help=(
            "maximum activated-concept selection budget in relative routing-cost "
            "units (not bytes, words, or measured tokens)"
        ),
    )
    parser.add_argument(
        "--detail",
        choices=("compact", "full"),
        default="compact",
        help="compact canonical packet or full packet with derived audit views",
    )
    parser.add_argument(
        "--out", type=Path, default=None, help="write the packet JSON here"
    )
    parser.add_argument(
        "--render",
        choices=("markdown", "json", "none"),
        default="markdown",
        help="what to print to stdout (default markdown)",
    )
    args = parser.parse_args()

    corpus = Corpus()
    role = corpus.role_aliases.get(args.role)
    if role is None:
        valid = ", ".join(sorted(corpus.role_bundles))
        print(f"unknown role '{args.role}'. valid roles: {valid}", file=sys.stderr)
        return 1
    task_family = corpus.task_aliases.get(args.task)
    if task_family is None:
        valid = ", ".join(sorted(corpus.task_bundles))
        print(f"unknown task '{args.task}'. valid tasks: {valid}", file=sys.stderr)
        return 1
    unknown_variants = sorted(
        set(args.task_variant) - corpus.task_variants.get(task_family, set())
    )
    if unknown_variants:
        valid = ", ".join(sorted(corpus.task_variants.get(task_family, set())))
        print(
            f"unknown task variant(s) for '{task_family}': {', '.join(unknown_variants)}. "
            f"valid variants: {valid}",
            file=sys.stderr,
        )
        return 1
    unknown_lenses = sorted(set(args.lens) - set(corpus.lenses))
    if unknown_lenses:
        print(f"unknown lens(es): {', '.join(unknown_lenses)}", file=sys.stderr)
        return 1
    disallowed_lenses = sorted(
        set(args.lens) - set(corpus.role_bundles[role].get("context_lenses", []))
    )
    if disallowed_lenses:
        print(
            f"lens(es) not applicable to role '{role}': {', '.join(disallowed_lenses)}",
            file=sys.stderr,
        )
        return 1

    signals = sorted(set(args.signal))
    languages = (
        sorted(set(args.language)) if args.language else ["language-independent"]
    )
    evidence_records, evidence_errors = read_evidence_records(args.evidence, corpus)
    if evidence_errors:
        for error in evidence_errors:
            print(f"invalid evidence: {error}", file=sys.stderr)
        return 1
    retrieval_budget = (
        args.budget
        if args.budget is not None
        else int(corpus.role_bundles[role]["initial_retrieval_budget_hint"])
    )
    if retrieval_budget <= 0:
        print("retrieval budget must be positive", file=sys.stderr)
        return 1
    try:
        request = RetrievalRequest(
            requested_role=args.role,
            role=role,
            requested_task=args.task,
            task_family=task_family,
            task_variants=tuple(sorted(set(args.task_variant))),
            requested_lenses=tuple(sorted(set(args.lens))),
            question=args.question,
            signals=tuple(signals),
            languages=tuple(languages),
            risk=args.risk,
            retrieval_budget=retrieval_budget,
            detail=args.detail,
        )
        packet, _ = assemble_packet(corpus, request, evidence_records)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1

    errors = validate_packet(packet)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("refusing to emit an invalid evidence packet", file=sys.stderr)
        return 1

    if args.out is not None:
        args.out.write_text(serialize_packet(packet), encoding="utf-8")
    if args.render == "json":
        sys.stdout.write(serialize_packet(packet))
    elif args.render == "markdown":
        sys.stdout.write(render_markdown(corpus, packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
