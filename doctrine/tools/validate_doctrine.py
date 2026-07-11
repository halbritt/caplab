#!/usr/bin/env python3
"""Validate doctrine schemas, graph provenance, and cross-file references."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a mapping at document root")
    return value


def duplicate_values(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def plain_heading(markup: str) -> str:
    value = markup.strip().rstrip("#").strip()
    # Conversion preserves printed section numbers as bold superscripts. They are
    # layout metadata rather than part of the chapter heading used by doctrine
    # locators (for example, ``**<sup>8</sup>** Orthogonality``).
    value = re.sub(r"^(?:\*\*|__)?<sup>\d+</sup>(?:\*\*|__)?\s*", "", value)
    value = re.sub(r"^(?:\*\*|__)\d+(?:\*\*|__)\s*", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = value.replace("\\_", "_")
    while len(value) >= 2:
        changed = re.sub(r"^(?:\*\*|__|\*|_)(.*?)(?:\*\*|__|\*|_)$", r"\1", value)
        if changed == value:
            break
        value = changed
    # OCR/conversion can interleave emphasis markers inside small-cap words
    # (``B***OUNDED* **C***ONTEXTS``). They are formatting, not provenance text.
    return value.replace("*", "").strip()


def heading_exists(path: Path, expected: str) -> bool:
    normalized_expected = plain_heading(expected)
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match and plain_heading(match.group(1)) == normalized_expected:
            return True
    return False


def source_registry() -> dict[str, dict[str, Any]]:
    sources = load_yaml(ROOT / "sources.yaml").get("sources", [])
    return {item["id"]: item for item in sources}


def validate_source_support(
    result: "Validation",
    label: str,
    support: dict[str, Any],
    source_by_id: dict[str, dict[str, Any]],
) -> tuple[str, str] | None:
    source_id = support.get("source_id")
    result.require(source_id in source_by_id, f"{label}: unknown source {source_id}")
    locator = support.get("locator", "")
    if " :: " not in locator:
        result.errors.append(f"{label}: malformed source locator {locator}")
        return None
    relative_path, expected_heading = locator.split(" :: ", 1)
    path = REPOSITORY / relative_path
    result.require(path.is_file(), f"{label}: locator file missing {relative_path}")
    if source_id in source_by_id:
        expected_prefix = source_by_id[source_id]["corpus_path"] + "/chapters/"
        result.require(
            relative_path.startswith(expected_prefix),
            f"{label}: locator {relative_path} is outside source {source_id}",
        )
    if path.is_file():
        result.require(
            heading_exists(path, expected_heading),
            f"{label}: heading not found exactly: {relative_path} :: {expected_heading}",
        )
    return relative_path, expected_heading


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.notes: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def schema(self, instance: Any, schema: dict[str, Any], label: str) -> None:
        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path)
            self.errors.append(f"{label}{'.' + location if location else ''}: {error.message}")


def ref_schema(root_schema: dict[str, Any], definition: str) -> dict[str, Any]:
    return {
        "$schema": root_schema["$schema"],
        "$ref": f"#/$defs/{definition}",
        "$defs": root_schema["$defs"],
    }


def validate_graph(result: Validation) -> tuple[set[str], set[str], set[str]]:
    graph_dir = ROOT / "graph"
    nodes_doc = load_yaml(graph_dir / "nodes.yaml")
    formulations_doc = load_yaml(graph_dir / "formulations.yaml")
    edges_doc = load_yaml(graph_dir / "edges.yaml")
    index = load_yaml(graph_dir / "index.yaml")
    views_doc = load_yaml(graph_dir / "views.yaml")
    sources_doc = load_yaml(ROOT / "sources.yaml")
    schema = json.loads((ROOT / "schemas" / "graph.schema.json").read_text(encoding="utf-8"))

    nodes = nodes_doc.get("nodes", [])
    formulations = formulations_doc.get("formulations", [])
    edges = edges_doc.get("edges", [])
    views = views_doc.get("views", [])
    sources = sources_doc.get("sources", [])

    for node in nodes:
        result.schema(node, ref_schema(schema, "node"), f"graph node {node.get('id', '<missing>')}")
    for formulation in formulations:
        result.schema(
            formulation,
            ref_schema(schema, "formulation"),
            f"graph formulation {formulation.get('id', '<missing>')}",
        )
    for edge in edges:
        result.schema(edge, ref_schema(schema, "edge"), f"graph edge {edge.get('id', '<missing>')}")

    node_ids = [item.get("id") for item in nodes if isinstance(item, dict)]
    formulation_ids = [item.get("id") for item in formulations if isinstance(item, dict)]
    edge_ids = [item.get("id") for item in edges if isinstance(item, dict)]
    source_ids = [item.get("id") for item in sources if isinstance(item, dict)]
    result.require(not duplicate_values(node_ids), f"duplicate graph node IDs: {duplicate_values(node_ids)}")
    result.require(
        not duplicate_values(formulation_ids),
        f"duplicate graph formulation IDs: {duplicate_values(formulation_ids)}",
    )
    result.require(not duplicate_values(edge_ids), f"duplicate graph edge IDs: {duplicate_values(edge_ids)}")
    result.require(not duplicate_values(source_ids), f"duplicate source IDs: {duplicate_values(source_ids)}")

    node_by_id = {item["id"]: item for item in nodes if isinstance(item, dict) and "id" in item}
    formulation_by_id = {
        item["id"]: item for item in formulations if isinstance(item, dict) and "id" in item
    }
    source_by_id = {item["id"]: item for item in sources if isinstance(item, dict) and "id" in item}

    for source in sources:
        corpus_path = REPOSITORY / source["corpus_path"]
        result.require(corpus_path.is_dir(), f"source {source['id']} corpus path missing: {corpus_path}")
        chapter_count = len(list((corpus_path / "chapters").glob("*.md")))
        result.require(
            chapter_count == source["chapter_count"],
            f"source {source['id']} chapter count {chapter_count} != registry {source['chapter_count']}",
        )

    for formulation in formulations:
        formulation_id = formulation.get("id", "<missing>")
        source_id = formulation.get("source_id")
        result.require(source_id in source_by_id, f"{formulation_id}: unknown source {source_id}")
        locator = formulation.get("locator", "")
        if "#" not in locator:
            result.errors.append(f"{formulation_id}: locator lacks chapter heading: {locator}")
            continue
        relative_path, expected_heading = locator.split("#", 1)
        path = REPOSITORY / relative_path
        result.require(path.is_file(), f"{formulation_id}: locator file missing: {relative_path}")
        if source_id in source_by_id:
            expected_prefix = source_by_id[source_id]["corpus_path"] + "/chapters/"
            result.require(
                relative_path.startswith(expected_prefix),
                f"{formulation_id}: locator {relative_path} is outside source {source_id}",
            )
        if path.is_file():
            result.require(
                heading_exists(path, expected_heading),
                f"{formulation_id}: heading not found exactly: {relative_path} :: {expected_heading}",
            )
        mapped_nodes = [mapping.get("node_id") for mapping in formulation.get("mappings", [])]
        result.require(
            not duplicate_values(mapped_nodes),
            f"{formulation_id}: duplicate node mappings {duplicate_values(mapped_nodes)}",
        )
        for node_id in mapped_nodes:
            result.require(node_id in node_by_id, f"{formulation_id}: unknown mapped node {node_id}")

    for node in nodes:
        node_id = node.get("id", "<missing>")
        for formulation_id in node.get("formulations", []):
            result.require(
                formulation_id in formulation_by_id,
                f"{node_id}: unknown formulation {formulation_id}",
            )
            if formulation_id in formulation_by_id:
                mapped_nodes = {
                    mapping.get("node_id")
                    for mapping in formulation_by_id[formulation_id].get("mappings", [])
                }
                result.require(
                    node_id in mapped_nodes,
                    f"{node_id}: formulation {formulation_id} lacks an explicit mapping back to node",
                )

    allowed_relations = set(index["edge_relations"]["directional"]) | set(
        index["edge_relations"]["symmetric"]
    )
    conflict_relations = {"contradicts", "in-tension-with"}
    for edge in edges:
        edge_id = edge.get("id", "<missing>")
        result.require(edge.get("from") in node_by_id, f"{edge_id}: unknown from node {edge.get('from')}")
        result.require(edge.get("to") in node_by_id, f"{edge_id}: unknown to node {edge.get('to')}")
        result.require(
            edge.get("relation") in allowed_relations,
            f"{edge_id}: undeclared relation {edge.get('relation')}",
        )
        if edge.get("relation") in conflict_relations:
            result.require("conflict_ref" in edge, f"{edge_id}: conflict edge lacks conflict_ref")
        for formulation_id in edge.get("provenance", []):
            result.require(
                formulation_id in formulation_by_id,
                f"{edge_id}: unknown provenance formulation {formulation_id}",
            )

    view_ids: list[str] = []
    for view in views:
        view_id = view.get("id", "<missing>")
        view_ids.append(view_id)
        for node_id in view.get("entry_nodes", []):
            result.require(node_id in node_by_id, f"{view_id}: unknown entry node {node_id}")
        for relation in view.get("include_relations", []):
            result.require(relation in allowed_relations, f"{view_id}: undeclared relation {relation}")
    result.require(not duplicate_values(view_ids), f"duplicate graph view IDs: {duplicate_values(view_ids)}")

    result.notes.append(
        f"graph: {len(node_by_id)} nodes, {len(formulation_by_id)} formulations, "
        f"{len(edges)} edges, {len(views)} views"
    )
    return set(node_by_id), set(formulation_by_id), set(source_by_id)


def validate_concepts(
    result: Validation,
    graph_nodes: set[str],
    source_ids: set[str],
    conflict_ids: set[str],
) -> set[str]:
    concept_dir = ROOT / "concepts"
    paths = sorted(concept_dir.glob("*.yaml")) if concept_dir.exists() else []
    if not paths:
        result.errors.append("no concept ontology files found under doctrine/concepts")
        return set()
    schema = json.loads((ROOT / "schemas" / "concepts.schema.json").read_text(encoding="utf-8"))
    source_by_id = source_registry()
    graph_formulations = load_yaml(ROOT / "graph" / "formulations.yaml").get("formulations", [])
    concept_ids: list[str] = []
    concepts: list[dict[str, Any]] = []
    for path in paths:
        document = load_yaml(path)
        result.schema(document, schema, str(path.relative_to(REPOSITORY)))
        for concept in document.get("concepts", []):
            concept_ids.append(concept.get("id"))
            concepts.append(concept)
    result.require(
        not duplicate_values(concept_ids),
        f"duplicate concept IDs: {duplicate_values(concept_ids)}",
    )
    known = set(concept_ids)
    for concept in concepts:
        concept_id = concept["id"]
        result.require(
            concept_id in graph_nodes,
            f"concept {concept_id}: missing canonical graph node",
        )
        for support in concept.get("source_support", []):
            result.require(
                support.get("source_id") in source_ids,
                f"concept {concept_id}: unknown source {support.get('source_id')}",
            )
            parsed = validate_source_support(result, f"concept {concept_id}", support, source_by_id)
            if parsed:
                relative_path, expected_heading = parsed
                graph_locator = f"{relative_path}#{expected_heading}"
                projected = any(
                    formulation.get("source_id") == support.get("source_id")
                    and formulation.get("locator") == graph_locator
                    and any(
                        mapping.get("node_id") == concept_id
                        and mapping.get("relationship_to_canonical") == support.get("relationship")
                        for mapping in formulation.get("mappings", [])
                    )
                    for formulation in graph_formulations
                )
                result.require(
                    projected,
                    f"concept {concept_id}: source support is not projected into graph with relationship {support.get('relationship')}: {graph_locator}",
                )
        for related in concept.get("routing", {}).get("related_concepts", []):
            result.require(related in known, f"concept {concept_id}: unknown related concept {related}")
        for conflict_id in concept.get("conflicts", []):
            result.require(
                conflict_id in conflict_ids,
                f"concept {concept_id}: unknown conflict {conflict_id}",
            )
    result.notes.append(f"concepts: {len(known)} records in {len(paths)} files")
    return known


def validate_conflicts(result: Validation) -> set[str]:
    records = load_yaml(ROOT / "conflicts.yaml").get("conflicts", [])
    source_by_id = source_registry()
    ids = [item.get("conflict_id") for item in records]
    result.require(not duplicate_values(ids), f"duplicate conflict IDs: {duplicate_values(ids)}")
    required = {
        "conflict_id",
        "positions",
        "hidden_assumptions",
        "evidence_favoring_each_position",
        "decision_rule",
        "unresolved_questions",
        "roles_affected",
        "source_support",
    }
    for record in records:
        conflict_id = record.get("conflict_id", "<missing>")
        result.require(required <= set(record), f"{conflict_id}: missing conflict fields {sorted(required - set(record))}")
        result.require(
            isinstance(conflict_id, str) and re.fullmatch(r"conflict-[a-z0-9-]+", conflict_id) is not None,
            f"invalid conflict ID: {conflict_id}",
        )
        positions = record.get("positions", [])
        result.require(len(positions) >= 2, f"{conflict_id}: fewer than two positions")
        position_ids = [item.get("id") for item in positions if isinstance(item, dict)]
        result.require(not duplicate_values(position_ids), f"{conflict_id}: duplicate position IDs")
        evidence_keys = set(record.get("evidence_favoring_each_position", {}))
        result.require(
            evidence_keys == set(position_ids),
            f"{conflict_id}: evidence keys {sorted(evidence_keys)} do not match positions {sorted(position_ids)}",
        )
        for index, support in enumerate(record.get("source_support", []), start=1):
            validate_source_support(result, f"{conflict_id} support {index}", support, source_by_id)
    result.notes.append(f"conflicts: {len(records)} records")
    return set(ids)


def validate_negative_doctrine(result: Validation) -> set[str]:
    records = load_yaml(ROOT / "negative-doctrine.yaml").get("prohibitions", [])
    source_by_id = source_registry()
    ids = [item.get("id") for item in records]
    result.require(not duplicate_values(ids), f"duplicate prohibition IDs: {duplicate_values(ids)}")
    required = {
        "id",
        "prohibition",
        "applies_when",
        "evidence_threshold",
        "exceptions",
        "source_support",
    }
    for record in records:
        prohibition_id = record.get("id", "<missing>")
        result.require(required <= set(record), f"{prohibition_id}: missing prohibition fields {sorted(required - set(record))}")
        result.require(
            isinstance(prohibition_id, str) and re.fullmatch(r"prohibit-[a-z0-9-]+", prohibition_id) is not None,
            f"invalid prohibition ID: {prohibition_id}",
        )
        result.require(bool(record.get("applies_when")), f"{prohibition_id}: empty applicability")
        result.require(bool(record.get("source_support")), f"{prohibition_id}: lacks source support")
        for index, support in enumerate(record.get("source_support", []), start=1):
            validate_source_support(result, f"{prohibition_id} support {index}", support, source_by_id)
    result.notes.append(f"negative doctrine: {len(records)} prohibitions")
    return set(ids)


def validate_corpus_map(result: Validation) -> None:
    document = load_yaml(ROOT / "corpus-map.yaml")
    records = document.get("sources", [])
    registry = source_registry()
    mapped_ids = [item.get("source_id") for item in records]
    result.require(not duplicate_values(mapped_ids), f"duplicate corpus-map sources: {duplicate_values(mapped_ids)}")
    result.require(set(mapped_ids) == set(registry), "corpus map does not cover the exact source registry")
    required = {
        "source_id",
        "primary_domain",
        "strongest_contributions",
        "contextual_assumptions",
        "limitations",
        "known_tensions",
        "likely_agent_roles",
        "concepts_worth_mining",
        "coverage_ledger",
    }
    for record in records:
        source_id = record.get("source_id", "<missing>")
        result.require(required <= set(record), f"corpus map {source_id}: missing fields {sorted(required - set(record))}")
        ledger = record.get("coverage_ledger", "").split("#", 1)[0]
        result.require((REPOSITORY / ledger).is_file(), f"corpus map {source_id}: missing coverage ledger {ledger}")
    summary = document.get("coverage_summary", {})
    result.require(summary.get("chapter_files") == 331, "corpus map chapter-file total is not 331")
    result.require(summary.get("covered_chapters") == 331, "corpus map covered chapter total is not 331")
    counts = summary.get("per_source_counts", {})
    result.require(
        counts == {source_id: item["chapter_count"] for source_id, item in registry.items()},
        "corpus map source counts differ from source registry",
    )
    result.notes.append("corpus map: 11 sources, 331/331 chapter files")


def validate_traceability(result: Validation) -> None:
    document = load_yaml(ROOT / "traceability.yaml")
    coverage = document.get("coverage_definition", {})
    result.require(coverage.get("expected_units") == 331, "traceability expected coverage is not 331")
    result.require(coverage.get("covered_units") == 331, "traceability covered units is not 331")
    seen_sources: set[str] = set()
    for ledger in document.get("chapter_coverage_ledgers", []):
        relative = ledger.get("ledger", "")
        path = REPOSITORY / relative
        result.require(path.is_file(), f"traceability ledger missing: {relative}")
        if path.is_file():
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            result.require(actual == ledger.get("sha256"), f"traceability checksum drift: {relative}")
        for source in ledger.get("sources", []):
            source_id = source.get("source_id")
            seen_sources.add(source_id)
            result.require(source.get("expected") == source.get("covered"), f"traceability incomplete: {source_id}")
    result.require(seen_sources == set(source_registry()), "traceability ledgers do not cover the exact source registry")
    result.notes.append("traceability: extraction checksums and 331/331 coverage current")


def validate_cross_references(
    result: Validation,
    concept_ids: set[str],
    conflict_ids: set[str],
) -> None:
    procedures = load_yaml(ROOT / "procedures.yaml").get("procedures", [])
    procedure_ids = {item.get("id") for item in procedures}
    for procedure in procedures:
        for concept_id in procedure.get("related_concepts", []):
            result.require(concept_id in concept_ids, f"{procedure.get('id')}: unknown concept {concept_id}")

    lenses = load_yaml(ROOT / "context-lenses.yaml").get("lenses", [])
    lens_ids = {item.get("id") for item in lenses}
    for lens in lenses:
        for concept_id in lens.get("emphasize_concepts", []):
            result.require(concept_id in concept_ids, f"{lens.get('id')}: unknown concept {concept_id}")

    edges = load_yaml(ROOT / "graph" / "edges.yaml").get("edges", [])
    for edge in edges:
        if "conflict_ref" in edge:
            result.require(edge["conflict_ref"] in conflict_ids, f"{edge.get('id')}: unknown conflict {edge['conflict_ref']}")

    routing = load_yaml(ROOT / "routing-index.yaml")
    for artifact in routing.get("always_load", {}).get("artifacts", []):
        result.require((ROOT / artifact).is_file(), f"routing always-load artifact missing: {artifact}")
    for concept_id in routing.get("always_load", {}).get("concepts", []):
        result.require(concept_id in concept_ids, f"routing always-load concept unknown: {concept_id}")
    routes = routing.get("concept_routes", [])
    route_ids = [item.get("concept_id") for item in routes]
    result.require(not duplicate_values(route_ids), f"duplicate concept routes: {duplicate_values(route_ids)}")
    result.require(set(route_ids) == concept_ids, "routing index does not contain exactly one route per concept")
    evidence_ids = {item.get("id") for item in load_yaml(ROOT / "evidence-taxonomy.yaml").get("classes", [])}
    for bundle in routing.get("role_bundles", []):
        for concept_id in bundle.get("core_concepts", []) + bundle.get("default_concepts", []) + bundle.get("conditional_concepts", []):
            result.require(concept_id in concept_ids, f"role {bundle.get('role')}: unknown concept {concept_id}")
        for procedure_id in bundle.get("procedures", []):
            result.require(procedure_id in procedure_ids, f"role {bundle.get('role')}: unknown procedure {procedure_id}")
        for lens_id in bundle.get("context_lenses", []):
            result.require(lens_id in lens_ids, f"role {bundle.get('role')}: unknown lens {lens_id}")
        for conflict_id in bundle.get("conflicts", []):
            result.require(conflict_id in conflict_ids, f"role {bundle.get('role')}: unknown conflict {conflict_id}")
    for bundle in routing.get("task_bundles", []):
        for concept_id in bundle.get("primary_concepts", []) + bundle.get("conditional_concepts", []):
            result.require(concept_id in concept_ids, f"task {bundle.get('task')}: unknown concept {concept_id}")
        for procedure_id in bundle.get("procedures", []):
            result.require(procedure_id in procedure_ids, f"task {bundle.get('task')}: unknown procedure {procedure_id}")
        for evidence_id in bundle.get("evidence", []):
            result.require(evidence_id in evidence_ids, f"task {bundle.get('task')}: unknown evidence class {evidence_id}")
    for bundle in routing.get("language_bundles", []):
        for concept_id in bundle.get("concepts", []):
            result.require(concept_id in concept_ids, f"language {bundle.get('language')}: unknown concept {concept_id}")
        for lens_id in bundle.get("context_lenses", []):
            result.require(lens_id in lens_ids, f"language {bundle.get('language')}: unknown lens {lens_id}")
    result.notes.append(
        f"routing: {len(routes)} concept routes, {len(routing.get('role_bundles', []))} role bundles, "
        f"{len(routing.get('task_bundles', []))} task bundles"
    )


def validate_techniques(result: Validation, concept_ids: set[str]) -> None:
    schema = json.loads((ROOT / "schemas" / "techniques.schema.json").read_text(encoding="utf-8"))
    source_by_id = source_registry()
    records: list[dict[str, Any]] = []
    for relative in ("techniques/architecture.yaml", "techniques/domain.yaml"):
        path = ROOT / relative
        result.require(path.is_file(), f"required artifact missing: doctrine/{relative}")
        if not path.is_file():
            continue
        document = load_yaml(path)
        result.schema(document, schema, f"doctrine/{relative}")
        records.extend(document.get("techniques", []))
    ids = [item.get("id") for item in records]
    result.require(not duplicate_values(ids), f"duplicate technique IDs: {duplicate_values(ids)}")
    candidate_ids = [item.get("candidate_id") for item in records]
    result.require(
        not duplicate_values(candidate_ids),
        f"duplicate technique candidate IDs: {duplicate_values(candidate_ids)}",
    )
    expected_candidates = {f"TECH-ARC-{index:03d}" for index in range(1, 21)} | {
        f"TECH-DOM-{index:03d}" for index in range(1, 19)
    }
    result.require(set(candidate_ids) == expected_candidates, "technique candidate sequence is incomplete")
    for record in records:
        technique_id = record.get("id", "<missing>")
        for concept_id in record.get("related_concepts", []):
            result.require(concept_id in concept_ids, f"{technique_id}: unknown related concept {concept_id}")
        for index, support in enumerate(record.get("source_support", []), start=1):
            validate_source_support(result, f"{technique_id} support {index}", support, source_by_id)
    result.require(len(records) == 38, f"technique catalog has {len(records)} records, expected 38")
    result.notes.append(f"techniques: {len(records)} contextual records")


def validate_required_artifacts(result: Validation) -> None:
    required = [
        "corpus-map.yaml",
        "universal-doctrine.md",
        "role-doctrine.md",
        "procedures.yaml",
        "negative-doctrine.yaml",
        "conflicts.yaml",
        "change-types.yaml",
        "evidence-taxonomy.yaml",
        "authority-model.yaml",
        "routing-index.yaml",
        "context-lenses.yaml",
        "rubrics.md",
        "checklists.md",
        "traceability.yaml",
    ]
    for relative in required:
        result.require((ROOT / relative).is_file(), f"required artifact missing: doctrine/{relative}")
    procedures = load_yaml(ROOT / "procedures.yaml").get("procedures", [])
    procedure_ids = {item.get("id") for item in procedures}
    expected = {
        "proc-plan-implementation",
        "proc-place-new-behavior",
        "proc-determine-abstraction-earned",
        "proc-review-api",
        "proc-assess-architectural-pressure",
        "proc-select-architectural-boundary",
        "proc-determine-refactoring-earned",
        "proc-select-first-refactoring-campaign",
        "proc-work-poorly-characterized-code",
        "proc-distinguish-repair-structural",
        "proc-evaluate-duplication",
        "proc-evaluate-module-depth",
        "proc-identify-domain-boundaries",
        "proc-decide-performance-justified",
        "proc-rank-engineering-risks",
        "proc-establish-preservation-boundaries",
        "proc-determine-tests-characterization",
        "proc-decide-leave-code-alone",
        "proc-stop-and-escalate",
        "proc-assess-authority-to-act",
    }
    result.require(expected <= procedure_ids, f"missing required procedures: {sorted(expected - procedure_ids)}")
    result.require(
        not duplicate_values([item.get("id") for item in procedures]),
        "duplicate procedure IDs",
    )
    result.notes.append(f"procedures: {len(procedures)} records")


def validate_machine_files_parse(result: Validation) -> None:
    yaml_paths = sorted(ROOT.rglob("*.yaml"))
    json_paths = sorted(ROOT.rglob("*.json"))
    for path in yaml_paths:
        load_yaml(path)
    for path in json_paths:
        with path.open(encoding="utf-8") as stream:
            json.load(stream)
    result.notes.append(f"machine files: {len(yaml_paths)} YAML and {len(json_paths)} JSON parse")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--graph-only",
        action="store_true",
        help="validate graph provenance without requiring the unfinished doctrinal library",
    )
    args = parser.parse_args()
    result = Validation()
    try:
        validate_machine_files_parse(result)
        graph_nodes, _, source_ids = validate_graph(result)
        if not args.graph_only:
            validate_required_artifacts(result)
            conflict_ids = validate_conflicts(result)
            validate_negative_doctrine(result)
            validate_corpus_map(result)
            validate_traceability(result)
            concept_ids = validate_concepts(result, graph_nodes, source_ids, conflict_ids)
            validate_cross_references(result, concept_ids, conflict_ids)
            validate_techniques(result, concept_ids)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, json.JSONDecodeError) as error:
        result.errors.append(f"validator aborted: {type(error).__name__}: {error}")

    for note in result.notes:
        print(f"OK: {note}")
    if result.errors:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(result.errors)} error(s)", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
