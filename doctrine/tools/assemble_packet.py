#!/usr/bin/env python3
"""Assemble a deterministic doctrine evidence packet from the routing index.

The assembler implements the routing index ``selection_order`` for a stated
role, task, and decision question:

1. always-load core concepts are nominated unconditionally;
2. the role bundle (core plus default concepts) is intersected with the task
   bundle's primary concepts to form the role/task baseline;
3. repository signals, requested languages, and a declared risk class nominate
   additional concept routes through their ``activate_for_*`` fields;
4. every nomination is gated: additional (non-baseline) nominations must match
   the route's ``activate_for_roles``, ``activate_for_tasks``, and — when a
   risk class is declared — ``activate_for_risk_classes``; every nomination
   must match ``activate_for_languages`` and must not trip ``exclude_when``;
5. related conflicts are loaded before any contested position is rendered.

Every nominated concept dropped by a gate is recorded in the packet's
``excluded_candidates`` with the nomination source and the specific failing
condition, per the retrieval contract in ``doctrine/README.md``.

Signal matching. Free-text ``--signal`` values are matched against index
conditions (activation signals, ``exclude_when`` conditions, prerequisites,
and required evidence) case-insensitively after whitespace normalization: a
signal matches a condition when it equals the condition or contains the whole
condition as a substring. Keyword overlap short of the whole condition never
matches, per the routing guard against keyword-based loading.

Prerequisite interpretation. This CLI cannot inspect a target repository, so
it cannot verify evidence-shaped prerequisites. The interpretation used here:

- a route prerequisite that names another concept record is pulled into the
  activated set (transitively), because the operationalization contract says a
  packet contains "the activated concept and its prerequisites"; prerequisite
  pulls bypass role/task gates but still honor language and exclusion gates,
  and an unloadable prerequisite is recorded in both ``excluded_candidates``
  and ``missing_evidence``;
- every other prerequisite (procedure IDs and free-text evidence conditions)
  and every concept ``required_evidence`` item is treated as satisfied only
  when a provided ``--signal`` matches it; otherwise it is recorded in
  ``missing_evidence`` as ``<evidence item> — required by <concept-id>``.
  Always-load and baseline concepts are never dropped for missing evidence.

Corpus version. ``corpus_version`` is derived from repository data only:
``corpus-<traceability generated_at_utc>-<digest>`` where the digest is the
first 12 hex characters of sha256 over the newline-joined, sorted
``source_sha256`` values in ``doctrine/sources.yaml``.

Determinism. The packet contains no timestamps and no randomness. Identical
invocations produce byte-identical output: ``packet_id`` is ``pkt-`` plus a
truncated sha256 over the canonical JSON serialization of the resolved inputs
(role, task, question, sorted signals, sorted normalized languages, risk) and
the corpus version, and every list in the packet has a deterministic order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "runtime" / "evidence-packet.schema.json"
PACKET_SCHEMA_VERSION = "evidence-packet/1"

# The libyaml loader parses the large routing and graph artifacts an order of
# magnitude faster; both loaders produce identical plain-Python documents.
SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.load(stream, Loader=SAFE_LOADER)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a mapping at document root")
    return value


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def matching_signal(condition: str, signals: list[str]) -> str | None:
    """Return the first signal that matches an index condition, else None."""
    normalized_condition = normalize(condition)
    for signal in signals:
        normalized_signal = normalize(signal)
        if normalized_condition == normalized_signal or normalized_condition in normalized_signal:
            return signal
    return None


class Corpus:
    """Read-only view over the doctrine artifacts the assembler consumes."""

    def __init__(self) -> None:
        self.routing = load_yaml(ROOT / "routing-index.yaml")
        self.routes = {route["concept_id"]: route for route in self.routing["concept_routes"]}
        self.role_bundles = {bundle["role"]: bundle for bundle in self.routing["role_bundles"]}
        self.task_bundles = {bundle["task"]: bundle for bundle in self.routing["task_bundles"]}
        self.concepts: dict[str, dict[str, Any]] = {}
        for path in sorted((ROOT / "concepts").glob("*.yaml")):
            for concept in load_yaml(path).get("concepts", []):
                self.concepts[concept["id"]] = concept
        self.conflicts = {
            record["conflict_id"]: record
            for record in load_yaml(ROOT / "conflicts.yaml").get("conflicts", [])
        }
        self.nodes = load_yaml(ROOT / "graph" / "nodes.yaml").get("nodes", [])
        self.formulations = load_yaml(ROOT / "graph" / "formulations.yaml").get("formulations", [])
        self.edges = load_yaml(ROOT / "graph" / "edges.yaml").get("edges", [])
        self.sources = load_yaml(ROOT / "sources.yaml").get("sources", [])
        self.traceability = load_yaml(ROOT / "traceability.yaml")

    def corpus_version(self) -> str:
        hashes = sorted(source["source_sha256"] for source in self.sources)
        digest = hashlib.sha256("\n".join(hashes).encode("utf-8")).hexdigest()[:12]
        generated = str(self.traceability["generated_at_utc"])
        return f"corpus-{generated}-{digest}"


def language_gate_failure(route: dict[str, Any], languages: list[str]) -> str | None:
    route_languages = {normalize(value) for value in route.get("activate_for_languages", [])}
    if "language-independent" in route_languages:
        return None
    if route_languages & {normalize(value) for value in languages}:
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
    route: dict[str, Any], role: str, task: str, risk: str | None
) -> list[str]:
    """Gates that apply only to concepts nominated outside the baseline."""
    failures: list[str] = []
    if role not in route.get("activate_for_roles", []):
        failures.append(f"role '{role}' not in activate_for_roles")
    if task not in route.get("activate_for_tasks", []):
        failures.append(f"task '{task}' not in activate_for_tasks")
    if risk is not None:
        risk_classes = {normalize(value) for value in route.get("activate_for_risk_classes", [])}
        if "all" not in risk_classes and normalize(risk) not in risk_classes:
            failures.append(f"risk class '{risk}' not in activate_for_risk_classes")
    return failures


class Selection:
    def __init__(self) -> None:
        self.activated: dict[str, list[str]] = {}
        self.excluded: dict[str, str] = {}
        self.missing_evidence: set[str] = set()


def select_concepts(
    corpus: Corpus,
    role: str,
    task: str,
    signals: list[str],
    languages: list[str],
    risk: str | None,
) -> Selection:
    role_bundle = corpus.role_bundles[role]
    task_bundle = corpus.task_bundles[task]
    always_load = list(corpus.routing["always_load"]["concepts"])
    baseline = sorted(
        (set(role_bundle.get("core_concepts", [])) | set(role_bundle.get("default_concepts", [])))
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
        for condition in route.get("activate_for_repository_signals", []):
            signal = matching_signal(condition, signals)
            if signal is not None:
                nominate(concept_id, f"signal '{signal}' matched activation signal '{condition}'")
                break
    for bundle in corpus.routing.get("language_bundles", []):
        if normalize(bundle["language"]) in {normalize(value) for value in languages}:
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
            failures.extend(additional_gate_failures(route, role, task, risk))
        language_failure = language_gate_failure(route, languages)
        if language_failure is not None:
            failures.append(language_failure)
        excluded_by = exclusion_failure(route, signals)
        if excluded_by is not None:
            failures.append(excluded_by)
        if failures:
            nominated = "; ".join(nominations[concept_id])
            selection.excluded[concept_id] = f"nominated by: {nominated}; dropped: " + "; ".join(
                failures
            )
        else:
            selection.activated[concept_id] = nominations[concept_id]

    expand_prerequisites(corpus, selection, signals, languages)
    return selection


def expand_prerequisites(
    corpus: Corpus, selection: Selection, signals: list[str], languages: list[str]
) -> None:
    """Pull concept-record prerequisites in; route the rest to missing evidence."""
    queue = sorted(selection.activated)
    processed: set[str] = set()
    while queue:
        concept_id = queue.pop(0)
        if concept_id in processed:
            continue
        processed.add(concept_id)
        route = corpus.routes[concept_id]
        concept = corpus.concepts[concept_id]
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
                    selection.missing_evidence.add(
                        f"{prerequisite} (prerequisite concept excluded) — required by {concept_id}"
                    )
                else:
                    selection.excluded.pop(prerequisite, None)
                    selection.activated[prerequisite] = [f"prerequisite of {concept_id}"]
                    queue.append(prerequisite)
            elif matching_signal(prerequisite, signals) is None:
                selection.missing_evidence.add(f"{prerequisite} — required by {concept_id}")
        for item in concept.get("required_evidence", []):
            if matching_signal(item, signals) is None:
                selection.missing_evidence.add(f"{item} — required by {concept_id}")


def ordered_concepts(corpus: Corpus, activated: dict[str, list[str]]) -> list[str]:
    """Core routes first, then ascending retrieval budget hint, then ID."""

    def key(concept_id: str) -> tuple[int, int, str]:
        route = corpus.routes[concept_id]
        core_rank = 0 if route.get("retrieval_priority") == "core" else 1
        return (core_rank, route.get("retrieval_budget_hint", 0), concept_id)

    return sorted(activated, key=key)


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
        if any(mapping.get("node_id") in node_ids for mapping in formulation.get("mappings", [])):
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


def packet_identifier(resolved_inputs: dict[str, Any]) -> str:
    canonical = json.dumps(resolved_inputs, sort_keys=True, separators=(",", ":"))
    return "pkt-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def assemble_packet(
    corpus: Corpus,
    role: str,
    task: str,
    question: str,
    signals: list[str],
    languages: list[str],
    risk: str | None,
) -> tuple[dict[str, Any], Selection]:
    selection = select_concepts(corpus, role, task, signals, languages, risk)
    activated_ids = ordered_concepts(corpus, selection.activated)
    activated_set = set(activated_ids)
    formulation_ids = collect_formulations(corpus, activated_set)
    corpus_version = corpus.corpus_version()
    resolved_inputs = {
        "corpus_version": corpus_version,
        "languages": sorted(normalize(value) for value in languages),
        "question": question,
        "risk": normalize(risk) if risk is not None else "",
        "role": role,
        "signals": sorted(signals),
        "task": task,
    }
    packet = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "packet_id": packet_identifier(resolved_inputs),
        "question": question,
        "corpus_version": corpus_version,
        "activated_concepts": activated_ids,
        "formulations": formulation_ids,
        "conflicts": collect_conflicts(corpus, activated_set),
        "excluded_candidates": [
            {"id": concept_id, "reason": selection.excluded[concept_id]}
            for concept_id in sorted(selection.excluded)
        ],
        "missing_evidence": sorted(selection.missing_evidence),
        "source_locators": collect_source_locators(corpus, activated_set, formulation_ids),
    }
    return packet, selection


PRECEDENCE_PREAMBLE = (
    "Precedence: explicit human authorization and stop conditions, then accepted "
    "repository contracts, tests, decisions, and current runtime facts, precede all "
    "doctrine below. This packet is retrieved guidance: it can justify a question, "
    "investigation, proposal, or bounded action; retrieval never creates authority "
    "to select, execute, verify, or accept a change."
)


def render_markdown(
    corpus: Corpus,
    packet: dict[str, Any],
    role: str,
    task: str,
    signals: list[str],
    languages: list[str],
    risk: str | None,
) -> str:
    lines: list[str] = []
    lines.append("# Doctrine evidence packet")
    lines.append("")
    lines.append(f"- Packet: {packet['packet_id']} · Corpus: {packet['corpus_version']}")
    lines.append(f"- Question: {packet['question']}")
    context = f"- Role: {role} · Task: {task} · Languages: {', '.join(sorted(languages))}"
    if risk is not None:
        context += f" · Risk: {risk}"
    if signals:
        context += f" · Signals: {'; '.join(sorted(signals))}"
    lines.append(context)
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
        lines.append(f"- Applicable when: {'; '.join(concept.get('applicable_when', []))}")
        if concept.get("not_applicable_when"):
            lines.append(f"- Not applicable when: {'; '.join(concept['not_applicable_when'])}")
        lines.append(f"- Required evidence: {'; '.join(concept.get('required_evidence', []))}")
        lines.append(
            f"- Preservation boundaries: {'; '.join(concept.get('preservation_boundaries', []))}"
        )
        lines.append(f"- Safe actions: {'; '.join(concept.get('safe_actions', []))}")
        lines.append(f"- Unsafe actions: {'; '.join(concept.get('unsafe_actions', []))}")

    lines.append("")
    lines.append(f"## Conflicts ({len(packet['conflicts'])})")
    for conflict_id in packet["conflicts"]:
        record = corpus.conflicts.get(conflict_id)
        lines.append("")
        lines.append(f"### {conflict_id}")
        if record is None:
            lines.append("- Record not found in conflicts.yaml")
            continue
        positions = "; ".join(
            f"{position['id']}: {position['claim']}" for position in record.get("positions", [])
        )
        lines.append(f"- Positions: {positions}")
        lines.append(f"- Selection rule: {record['decision_rule']}")

    lines.append("")
    lines.append(f"## Missing evidence ({len(packet['missing_evidence'])})")
    for item in packet["missing_evidence"]:
        lines.append(f"- {item}")

    lines.append("")
    lines.append(f"## Source locators ({len(packet['source_locators'])})")
    for locator in packet["source_locators"]:
        lines.append(f"- {locator}")
    lines.append("")
    return "\n".join(lines)


def validate_packet(packet: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(packet), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path)
        errors.append(f"packet{'.' + location if location else ''}: {error.message}")
    return errors


def serialize_packet(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble a deterministic, schema-conformant doctrine evidence packet."
    )
    parser.add_argument("--role", required=True, help="agent role ID from the routing index")
    parser.add_argument("--task", required=True, help="task ID from the routing index")
    parser.add_argument("--question", required=True, help="free-text decision question")
    parser.add_argument(
        "--signal",
        action="append",
        default=[],
        help="repository signal (repeatable); also serves as evidence for prerequisites",
    )
    parser.add_argument(
        "--language",
        action="append",
        default=[],
        help="repository language (repeatable; default language-independent)",
    )
    parser.add_argument("--risk", default=None, help="declared risk class")
    parser.add_argument("--out", type=Path, default=None, help="write the packet JSON here")
    parser.add_argument(
        "--render",
        choices=("markdown", "json", "none"),
        default="markdown",
        help="what to print to stdout (default markdown)",
    )
    args = parser.parse_args()

    corpus = Corpus()
    if args.role not in corpus.role_bundles:
        valid = ", ".join(sorted(corpus.role_bundles))
        print(f"unknown role '{args.role}'. valid roles: {valid}", file=sys.stderr)
        return 1
    if args.task not in corpus.task_bundles:
        valid = ", ".join(sorted(corpus.task_bundles))
        print(f"unknown task '{args.task}'. valid tasks: {valid}", file=sys.stderr)
        return 1

    signals = sorted(set(args.signal))
    languages = sorted(set(args.language)) if args.language else ["language-independent"]
    packet, _ = assemble_packet(
        corpus, args.role, args.task, args.question, signals, languages, args.risk
    )

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
        sys.stdout.write(
            render_markdown(corpus, packet, args.role, args.task, signals, languages, args.risk)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
