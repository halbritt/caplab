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


def parse_heading_selector(expected: str) -> tuple[str, dict[str, str]]:
    """Split ``Heading @@ key=value;...`` into heading text and selectors."""
    if " @@ " not in expected:
        return expected, {}
    heading, raw_selectors = expected.rsplit(" @@ ", 1)
    selectors: dict[str, str] = {}
    for item in raw_selectors.split(";"):
        if "=" not in item:
            return heading, {"invalid": raw_selectors}
        key, value = item.split("=", 1)
        selectors[key.strip()] = value.strip()
    return heading, selectors


def heading_sections(path: Path, expected: str) -> list[dict[str, object]]:
    """Return every matching heading and a stable hash of its bounded section."""
    heading, selectors = parse_heading_selector(expected)
    if "invalid" in selectors or set(selectors) - {"level", "occurrence", "sha256"}:
        return []
    normalized_expected = plain_heading(heading)
    lines = path.read_text(encoding="utf-8").splitlines()
    matches: list[dict[str, object]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match or plain_heading(match.group(2)) != normalized_expected:
            continue
        level = len(match.group(1))
        end = len(lines)
        for candidate_index in range(index + 1, len(lines)):
            candidate = re.match(r"^(#{1,6})\s+(.+?)\s*$", lines[candidate_index])
            if candidate and len(candidate.group(1)) <= level:
                end = candidate_index
                break
        section = "\n".join(lines[index:end]).rstrip() + "\n"
        matches.append(
            {
                "line": index + 1,
                "level": level,
                "sha256": hashlib.sha256(section.encode("utf-8")).hexdigest(),
            }
        )
    if "level" in selectors:
        try:
            level = int(selectors["level"])
        except ValueError:
            return []
        matches = [match for match in matches if match["level"] == level]
    if "sha256" in selectors:
        matches = [match for match in matches if match["sha256"] == selectors["sha256"]]
    if "occurrence" in selectors:
        try:
            occurrence = int(selectors["occurrence"])
        except ValueError:
            return []
        if occurrence < 1 or occurrence > len(matches):
            return []
        matches = [matches[occurrence - 1]]
    return matches


def heading_exists(path: Path, expected: str) -> bool:
    """A canonical heading locator must resolve to exactly one section."""
    return len(heading_sections(path, expected)) == 1


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


def validate_concept_confidence(result: "Validation", concept: dict[str, Any]) -> None:
    """Keep the highest portability claim tied to independent source support."""
    if concept.get("confidence") != "universal":
        return
    source_ids = {
        support.get("source_id")
        for support in concept.get("source_support", [])
        if isinstance(support, dict) and support.get("source_id")
    }
    result.require(
        len(source_ids) >= 2,
        f"concept {concept.get('id', '<missing>')}: universal confidence requires "
        "support from at least two independent sources",
    )


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.notes: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def schema(self, instance: Any, schema: dict[str, Any], label: str) -> None:
        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(
            validator.iter_errors(instance), key=lambda item: list(item.path)
        ):
            location = ".".join(str(part) for part in error.path)
            self.errors.append(
                f"{label}{'.' + location if location else ''}: {error.message}"
            )


def ref_schema(root_schema: dict[str, Any], definition: str) -> dict[str, Any]:
    return {
        "$schema": root_schema["$schema"],
        "$ref": f"#/$defs/{definition}",
        "$defs": root_schema["$defs"],
    }


def validate_source_identity(
    result: Validation, source: dict[str, Any], repository: Path
) -> None:
    """Verify one source registry record through the original and generated record."""
    source_id = source.get("id", "<missing>")
    relative_input = source.get("source_input_path")
    if not isinstance(relative_input, str) or not relative_input:
        result.errors.append(f"source {source_id}: missing source_input_path")
        return
    relative_path = Path(relative_input)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        result.errors.append(
            f"source {source_id}: unsafe source_input_path {relative_input}"
        )
        return
    source_path = repository / relative_path
    result.require(
        source_path.is_file(), f"source {source_id}: binary missing: {relative_input}"
    )
    result.require(
        not source_path.is_symlink(),
        f"source {source_id}: binary must not be a symlink: {relative_input}",
    )
    if not source_path.is_file():
        return
    expected_format = source.get("source_format")
    actual_format = source_path.suffix.lower().lstrip(".")
    result.require(
        actual_format == expected_format,
        f"source {source_id}: binary format {actual_format} != registry {expected_format}",
    )
    actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    result.require(
        actual_hash == source.get("source_sha256"),
        f"source {source_id}: binary sha256 {actual_hash} != registry {source.get('source_sha256')}",
    )

    source_json_path = repository / source.get("corpus_path", "") / "source.json"
    result.require(
        source_json_path.is_file(),
        f"source {source_id}: generated source.json missing: {source_json_path}",
    )
    if not source_json_path.is_file():
        return
    try:
        generated = json.loads(source_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        result.errors.append(f"source {source_id}: invalid source.json: {error}")
        return
    result.require(
        generated.get("source_path") == relative_input,
        f"source {source_id}: source.json path {generated.get('source_path')} != registry {relative_input}",
    )
    result.require(
        generated.get("source_sha256") == source.get("source_sha256"),
        f"source {source_id}: source.json sha256 {generated.get('source_sha256')} != registry {source.get('source_sha256')}",
    )
    result.require(
        generated.get("source_format") == expected_format,
        f"source {source_id}: source.json format {generated.get('source_format')} != registry {expected_format}",
    )
    result.require(
        generated.get("source_size_bytes") == source_path.stat().st_size,
        f"source {source_id}: source.json size {generated.get('source_size_bytes')} != binary {source_path.stat().st_size}",
    )


def validate_graph(result: Validation) -> tuple[set[str], set[str], set[str]]:
    graph_dir = ROOT / "graph"
    nodes_doc = load_yaml(graph_dir / "nodes.yaml")
    formulations_doc = load_yaml(graph_dir / "formulations.yaml")
    edges_doc = load_yaml(graph_dir / "edges.yaml")
    routing_doc = load_yaml(ROOT / "routing-graph" / "links.yaml")
    index = load_yaml(graph_dir / "index.yaml")
    views_doc = load_yaml(graph_dir / "views.yaml")
    sources_doc = load_yaml(ROOT / "sources.yaml")
    schema = json.loads(
        (ROOT / "schemas" / "graph.schema.json").read_text(encoding="utf-8")
    )
    sources_schema = json.loads(
        (ROOT / "schemas" / "sources.schema.json").read_text(encoding="utf-8")
    )

    nodes = nodes_doc.get("nodes", [])
    formulations = formulations_doc.get("formulations", [])
    edges = edges_doc.get("edges", [])
    routing_links = routing_doc.get("links", [])
    views = views_doc.get("views", [])
    sources = sources_doc.get("sources", [])

    result.schema(sources_doc, sources_schema, "doctrine/sources.yaml")

    for node in nodes:
        result.schema(
            node,
            ref_schema(schema, "node"),
            f"graph node {node.get('id', '<missing>')}",
        )
    for formulation in formulations:
        result.schema(
            formulation,
            ref_schema(schema, "formulation"),
            f"graph formulation {formulation.get('id', '<missing>')}",
        )
    for edge in edges:
        result.schema(
            edge,
            ref_schema(schema, "edge"),
            f"graph edge {edge.get('id', '<missing>')}",
        )

    node_ids = [item.get("id") for item in nodes if isinstance(item, dict)]
    formulation_ids = [
        item.get("id") for item in formulations if isinstance(item, dict)
    ]
    edge_ids = [item.get("id") for item in edges if isinstance(item, dict)]
    source_ids = [item.get("id") for item in sources if isinstance(item, dict)]
    result.require(
        not duplicate_values(node_ids),
        f"duplicate graph node IDs: {duplicate_values(node_ids)}",
    )
    result.require(
        not duplicate_values(formulation_ids),
        f"duplicate graph formulation IDs: {duplicate_values(formulation_ids)}",
    )
    result.require(
        not duplicate_values(edge_ids),
        f"duplicate graph edge IDs: {duplicate_values(edge_ids)}",
    )
    result.require(
        not duplicate_values(source_ids),
        f"duplicate source IDs: {duplicate_values(source_ids)}",
    )

    node_by_id = {
        item["id"]: item for item in nodes if isinstance(item, dict) and "id" in item
    }
    formulation_by_id = {
        item["id"]: item
        for item in formulations
        if isinstance(item, dict) and "id" in item
    }
    source_by_id = {
        item["id"]: item for item in sources if isinstance(item, dict) and "id" in item
    }

    for source in sources:
        validate_source_identity(result, source, REPOSITORY)
        corpus_path = REPOSITORY / source["corpus_path"]
        result.require(
            corpus_path.is_dir(),
            f"source {source['id']} corpus path missing: {corpus_path}",
        )
        chapter_count = len(list((corpus_path / "chapters").glob("*.md")))
        result.require(
            chapter_count == source["chapter_count"],
            f"source {source['id']} chapter count {chapter_count} != registry {source['chapter_count']}",
        )

    for formulation in formulations:
        formulation_id = formulation.get("id", "<missing>")
        source_id = formulation.get("source_id")
        result.require(
            source_id in source_by_id, f"{formulation_id}: unknown source {source_id}"
        )
        locator = formulation.get("locator", "")
        if "#" not in locator:
            result.errors.append(
                f"{formulation_id}: locator lacks chapter heading: {locator}"
            )
            continue
        relative_path, expected_heading = locator.split("#", 1)
        path = REPOSITORY / relative_path
        result.require(
            path.is_file(), f"{formulation_id}: locator file missing: {relative_path}"
        )
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
        mapped_nodes = [
            mapping.get("node_id") for mapping in formulation.get("mappings", [])
        ]
        result.require(
            not duplicate_values(mapped_nodes),
            f"{formulation_id}: duplicate node mappings {duplicate_values(mapped_nodes)}",
        )
        for node_id in mapped_nodes:
            result.require(
                node_id in node_by_id,
                f"{formulation_id}: unknown mapped node {node_id}",
            )

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
        result.require(
            edge.get("from") in node_by_id,
            f"{edge_id}: unknown from node {edge.get('from')}",
        )
        result.require(
            edge.get("to") in node_by_id, f"{edge_id}: unknown to node {edge.get('to')}"
        )
        result.require(
            edge.get("relation") in allowed_relations,
            f"{edge_id}: undeclared relation {edge.get('relation')}",
        )
        if edge.get("relation") in conflict_relations:
            result.require(
                "conflict_ref" in edge, f"{edge_id}: conflict edge lacks conflict_ref"
            )
        for formulation_id in edge.get("provenance", []):
            result.require(
                formulation_id in formulation_by_id,
                f"{edge_id}: unknown provenance formulation {formulation_id}",
            )
        mapped_endpoints = {
            mapping.get("node_id")
            for formulation_id in edge.get("provenance", [])
            if formulation_id in formulation_by_id
            for mapping in formulation_by_id[formulation_id].get("mappings", [])
        }
        required_endpoints = {edge.get("from"), edge.get("to")}
        result.require(
            required_endpoints <= mapped_endpoints,
            f"{edge_id}: provenance does not cover both endpoints",
        )

    result.require(
        routing_doc.get("schema_version") == "agent-doctrine-routing-graph/1",
        "routing graph: unsupported schema version",
    )
    routing_ids = [link.get("id") for link in routing_links]
    result.require(
        not duplicate_values(routing_ids),
        f"duplicate routing link IDs: {duplicate_values(routing_ids)}",
    )
    for link in routing_links:
        link_id = link.get("id", "<missing>")
        result.require(link.get("from") in node_by_id, f"{link_id}: unknown from node")
        result.require(link.get("to") in node_by_id, f"{link_id}: unknown to node")
        result.require(
            link.get("relation") == "co-retrieved-with",
            f"{link_id}: routing relation must be co-retrieved-with",
        )
        result.require(
            link.get("semantic") is False,
            f"{link_id}: routing link must declare semantic false",
        )
        result.require(
            "provenance" not in link,
            f"{link_id}: routing link must not claim source provenance",
        )
        result.require(
            set(link.get("declared_by", [])) <= {link.get("from"), link.get("to")},
            f"{link_id}: declared_by must name an endpoint",
        )

    view_ids: list[str] = []
    for view in views:
        view_id = view.get("id", "<missing>")
        view_ids.append(view_id)
        for node_id in view.get("entry_nodes", []):
            result.require(
                node_id in node_by_id, f"{view_id}: unknown entry node {node_id}"
            )
        for relation in view.get("include_relations", []):
            result.require(
                relation in allowed_relations,
                f"{view_id}: undeclared relation {relation}",
            )
    result.require(
        not duplicate_values(view_ids),
        f"duplicate graph view IDs: {duplicate_values(view_ids)}",
    )

    result.notes.append(
        f"graph: {len(node_by_id)} nodes, {len(formulation_by_id)} formulations, "
        f"{len(edges)} semantic edges, {len(routing_links)} routing links, {len(views)} views"
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
    schema = json.loads(
        (ROOT / "schemas" / "concepts.schema.json").read_text(encoding="utf-8")
    )
    source_by_id = source_registry()
    graph_formulations = load_yaml(ROOT / "graph" / "formulations.yaml").get(
        "formulations", []
    )
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
        validate_concept_confidence(result, concept)
        result.require(
            concept_id in graph_nodes,
            f"concept {concept_id}: missing canonical graph node",
        )
        for support in concept.get("source_support", []):
            result.require(
                support.get("source_id") in source_ids,
                f"concept {concept_id}: unknown source {support.get('source_id')}",
            )
            parsed = validate_source_support(
                result, f"concept {concept_id}", support, source_by_id
            )
            if parsed:
                relative_path, expected_heading = parsed
                graph_locator = f"{relative_path}#{expected_heading}"
                projected = any(
                    formulation.get("source_id") == support.get("source_id")
                    and formulation.get("locator") == graph_locator
                    and any(
                        mapping.get("node_id") == concept_id
                        and mapping.get("relationship_to_canonical")
                        == support.get("relationship")
                        for mapping in formulation.get("mappings", [])
                    )
                    for formulation in graph_formulations
                )
                result.require(
                    projected,
                    f"concept {concept_id}: source support is not projected into graph with relationship {support.get('relationship')}: {graph_locator}",
                )
        for related in concept.get("routing", {}).get("related_concepts", []):
            result.require(
                related in known,
                f"concept {concept_id}: unknown related concept {related}",
            )
        for conflict_id in concept.get("conflicts", []):
            result.require(
                conflict_id in conflict_ids,
                f"concept {concept_id}: unknown conflict {conflict_id}",
            )
    result.notes.append(f"concepts: {len(known)} records in {len(paths)} files")
    return known


def validate_conflicts(result: Validation) -> set[str]:
    document = load_yaml(ROOT / "conflicts.yaml")
    graph_schema = json.loads(
        (ROOT / "schemas" / "graph.schema.json").read_text(encoding="utf-8")
    )
    result.schema(
        document,
        ref_schema(graph_schema, "conflictDocument"),
        "doctrine/conflicts.yaml",
    )
    records = document.get("conflicts", [])
    source_by_id = source_registry()
    ids = [item.get("conflict_id") for item in records]
    result.require(
        not duplicate_values(ids), f"duplicate conflict IDs: {duplicate_values(ids)}"
    )
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
        result.require(
            required <= set(record),
            f"{conflict_id}: missing conflict fields {sorted(required - set(record))}",
        )
        result.require(
            isinstance(conflict_id, str)
            and re.fullmatch(r"conflict-[a-z0-9-]+", conflict_id) is not None,
            f"invalid conflict ID: {conflict_id}",
        )
        positions = record.get("positions", [])
        result.require(len(positions) >= 2, f"{conflict_id}: fewer than two positions")
        position_ids = [item.get("id") for item in positions if isinstance(item, dict)]
        result.require(
            not duplicate_values(position_ids), f"{conflict_id}: duplicate position IDs"
        )
        evidence_keys = set(record.get("evidence_favoring_each_position", {}))
        result.require(
            evidence_keys == set(position_ids),
            f"{conflict_id}: evidence keys {sorted(evidence_keys)} do not match positions {sorted(position_ids)}",
        )
        aggregate_support = {
            (support.get("source_id"), support.get("locator"))
            for support in record.get("source_support", [])
            if isinstance(support, dict)
        }
        attributed_support: set[tuple[Any, Any]] = set()
        for position in positions:
            if not isinstance(position, dict):
                continue
            position_id = position.get("id", "<missing>")
            evidence = record.get("evidence_favoring_each_position", {}).get(
                position_id, []
            )
            result.require(
                bool(evidence),
                f"{conflict_id}/{position_id}: no evidence-selection conditions",
            )
            supports = position.get("source_support", [])
            basis_kind = position.get("basis", {}).get("kind")
            result.require(
                basis_kind != "source-supported" or bool(supports),
                f"{conflict_id}/{position_id}: source-supported basis lacks source support",
            )
            result.require(
                bool(supports) or basis_kind in {"derived-inference", "local-policy"},
                f"{conflict_id}/{position_id}: unsupported position must be derived-inference or local-policy",
            )
            for support_index, support in enumerate(supports, start=1):
                validate_source_support(
                    result,
                    f"{conflict_id}/{position_id} support {support_index}",
                    support,
                    source_by_id,
                )
                attributed_support.add(
                    (support.get("source_id"), support.get("locator"))
                )
        result.require(
            aggregate_support == attributed_support,
            f"{conflict_id}: aggregate source support does not match position-attributed support",
        )
        for index, support in enumerate(record.get("source_support", []), start=1):
            validate_source_support(
                result, f"{conflict_id} support {index}", support, source_by_id
            )
    result.notes.append(f"conflicts: {len(records)} records")
    return set(ids)


def validate_negative_doctrine(result: Validation) -> set[str]:
    records = load_yaml(ROOT / "negative-doctrine.yaml").get("prohibitions", [])
    source_by_id = source_registry()
    ids = [item.get("id") for item in records]
    result.require(
        not duplicate_values(ids), f"duplicate prohibition IDs: {duplicate_values(ids)}"
    )
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
        result.require(
            required <= set(record),
            f"{prohibition_id}: missing prohibition fields {sorted(required - set(record))}",
        )
        result.require(
            isinstance(prohibition_id, str)
            and re.fullmatch(r"prohibit-[a-z0-9-]+", prohibition_id) is not None,
            f"invalid prohibition ID: {prohibition_id}",
        )
        result.require(
            bool(record.get("applies_when")), f"{prohibition_id}: empty applicability"
        )
        result.require(
            bool(record.get("source_support")),
            f"{prohibition_id}: lacks source support",
        )
        for index, support in enumerate(record.get("source_support", []), start=1):
            validate_source_support(
                result, f"{prohibition_id} support {index}", support, source_by_id
            )
    result.notes.append(f"negative doctrine: {len(records)} prohibitions")
    return set(ids)


def validate_corpus_map(result: Validation) -> None:
    document = load_yaml(ROOT / "corpus-map.yaml")
    records = document.get("sources", [])
    registry = source_registry()
    mapped_ids = [item.get("source_id") for item in records]
    result.require(
        not duplicate_values(mapped_ids),
        f"duplicate corpus-map sources: {duplicate_values(mapped_ids)}",
    )
    result.require(
        set(mapped_ids) == set(registry),
        "corpus map does not cover the exact source registry",
    )
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
        result.require(
            required <= set(record),
            f"corpus map {source_id}: missing fields {sorted(required - set(record))}",
        )
        ledger = record.get("coverage_ledger", "").split("#", 1)[0]
        result.require(
            (REPOSITORY / ledger).is_file(),
            f"corpus map {source_id}: missing coverage ledger {ledger}",
        )
    summary = document.get("coverage_summary", {})
    expected_total = sum(item["chapter_count"] for item in registry.values())
    result.require(
        summary.get("chapter_files") == expected_total,
        f"corpus map chapter-file total is not {expected_total}",
    )
    result.require(
        summary.get("covered_chapters") == expected_total,
        f"corpus map covered chapter total is not {expected_total}",
    )
    counts = summary.get("per_source_counts", {})
    result.require(
        counts
        == {source_id: item["chapter_count"] for source_id, item in registry.items()},
        "corpus map source counts differ from source registry",
    )
    result.notes.append(
        f"corpus map: {len(registry)} sources, {expected_total}/{expected_total} chapter files"
    )


def validate_bibliography(result: Validation) -> None:
    path = ROOT / "bibliography.json"
    if not path.is_file():
        result.errors.append("canonical bibliography missing")
        return
    document = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(
        (ROOT / "schemas" / "bibliography.schema.json").read_text(encoding="utf-8")
    )
    result.schema(document, schema, "doctrine/bibliography.json")
    registry = source_registry()
    records = document.get("books", [])
    record_ids = [record.get("source_id") for record in records]
    result.require(
        not duplicate_values(record_ids),
        f"duplicate bibliography source IDs: {duplicate_values(record_ids)}",
    )
    result.require(
        set(registry) <= set(record_ids),
        "bibliography does not cover the doctrine source registry",
    )
    for record in records:
        source_id = record.get("source_id", "<missing>")
        source = registry.get(source_id)
        slug = record.get("slug")
        corpus_path = f"books/{slug}" if isinstance(slug, str) else ""
        corpus_prefix = f"{corpus_path}/"
        if source is not None:
            result.require(
                record.get("source_path") == source.get("source_input_path"),
                f"bibliography {source_id}: source path differs from source registry",
            )
            result.require(
                record.get("slug") == Path(source["corpus_path"]).name,
                f"bibliography {source_id}: slug differs from corpus path",
            )
        else:
            source_json_path = REPOSITORY / corpus_path / "source.json"
            result.require(
                source_json_path.is_file(),
                f"bibliography {source_id}: generated source.json missing",
            )
            if source_json_path.is_file():
                try:
                    generated = json.loads(
                        source_json_path.read_text(encoding="utf-8")
                    )
                except (OSError, json.JSONDecodeError) as error:
                    result.errors.append(
                        f"bibliography {source_id}: invalid source.json: {error}"
                    )
                else:
                    validate_source_identity(
                        result,
                        {
                            "id": source_id,
                            "source_input_path": record.get("source_path"),
                            "source_sha256": generated.get("source_sha256"),
                            "source_format": generated.get("source_format"),
                            "corpus_path": corpus_path,
                        },
                        REPOSITORY,
                    )
        canonical_authors = {
            creator.get("name")
            for creator in record.get("creators", [])
            if creator.get("role") == "author"
        }
        result.require(
            bool(canonical_authors), f"bibliography {source_id}: no canonical author"
        )
        if source is not None:
            result.require(
                canonical_authors <= set(source.get("authors", [])),
                f"bibliography {source_id}: canonical authors are absent from source registry",
            )
        evidence_paths = list(record.get("title_evidence", []))
        evidence_paths.extend(record.get("edition", {}).get("evidence", []))
        evidence_paths.extend(
            evidence
            for creator in record.get("creators", [])
            for evidence in creator.get("evidence", [])
        )
        for evidence in evidence_paths:
            result.require(
                evidence == record.get("source_path")
                or evidence.startswith(corpus_prefix),
                f"bibliography {source_id}: field evidence belongs to another source: {evidence}",
            )
            result.require(
                (REPOSITORY / evidence).is_file(),
                f"bibliography {source_id}: field evidence missing: {evidence}",
            )
    result.notes.append(f"bibliography: {len(records)} canonical source records")


def validate_traceability(result: Validation) -> None:
    document = load_yaml(ROOT / "traceability.yaml")
    registry = source_registry()
    expected_total = sum(item["chapter_count"] for item in registry.values())
    coverage = document.get("coverage_definition", {})
    result.require(
        coverage.get("expected_units") == expected_total,
        f"traceability expected coverage is not {expected_total}",
    )
    result.require(
        coverage.get("covered_units") == expected_total,
        f"traceability covered units is not {expected_total}",
    )
    seen_sources: set[str] = set()
    for ledger in document.get("chapter_coverage_ledgers", []):
        relative = ledger.get("ledger", "")
        path = REPOSITORY / relative
        result.require(path.is_file(), f"traceability ledger missing: {relative}")
        if path.is_file():
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            result.require(
                actual == ledger.get("sha256"),
                f"traceability checksum drift: {relative}",
            )
        for source in ledger.get("sources", []):
            source_id = source.get("source_id")
            seen_sources.add(source_id)
            registered_count = registry.get(source_id, {}).get("chapter_count")
            result.require(
                source.get("expected") == registered_count,
                f"traceability expected count differs from registry: {source_id}",
            )
            result.require(
                source.get("covered") == registered_count,
                f"traceability incomplete: {source_id}",
            )
    result.require(
        seen_sources == set(registry),
        "traceability ledgers do not cover the exact source registry",
    )
    result.notes.append(
        f"traceability: extraction checksums and {expected_total}/{expected_total} coverage current"
    )


def validate_chapter_coverage_records(
    result: Validation,
    document: dict[str, Any],
    sources: dict[str, dict[str, Any]],
    repository: Path,
) -> None:
    records = document.get("chapters", [])
    result.require(
        document.get("schema_version") == "chapter-coverage/1",
        "chapter coverage: unsupported schema version",
    )
    paths = [
        record.get("chapter_path") for record in records if isinstance(record, dict)
    ]
    result.require(
        not duplicate_values(paths),
        f"chapter coverage duplicate paths: {duplicate_values(paths)}",
    )
    expected_paths = {
        path.relative_to(repository).as_posix()
        for source in sources.values()
        for path in sorted(
            (repository / source["corpus_path"] / "chapters").glob("*.md")
        )
    }
    covered_paths = set(paths)
    missing = sorted(expected_paths - covered_paths)
    extra = sorted(covered_paths - expected_paths)
    if missing:
        result.errors.append(
            "chapter coverage missing filesystem chapters: " + ", ".join(missing)
        )
    if extra:
        result.errors.append(
            "chapter coverage has unregistered chapters: " + ", ".join(extra)
        )
    for record in records:
        if not isinstance(record, dict):
            result.errors.append("chapter coverage record must be an object")
            continue
        chapter_path = record.get("chapter_path", "")
        source_id = record.get("source_id")
        if source_id not in sources:
            result.errors.append(
                f"chapter coverage {chapter_path}: unknown source {source_id}"
            )
            continue
        prefix = sources[source_id]["corpus_path"] + "/chapters/"
        result.require(
            chapter_path.startswith(prefix),
            f"chapter coverage {chapter_path}: outside source {source_id}",
        )
        path = repository / chapter_path
        if path.is_file():
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            result.require(
                record.get("sha256") == actual_hash,
                f"chapter coverage {chapter_path}: sha256 drift",
            )
        result.require(
            bool(record.get("title")),
            f"chapter coverage {chapter_path}: missing title",
        )
        result.require(
            bool(record.get("disposition")),
            f"chapter coverage {chapter_path}: missing disposition",
        )


def validate_chapter_coverage(result: Validation) -> None:
    path = ROOT / "chapter-coverage.yaml"
    result.require(path.is_file(), "chapter coverage manifest missing")
    if not path.is_file():
        return
    document = load_yaml(path)
    registry = source_registry()
    validate_chapter_coverage_records(result, document, registry, REPOSITORY)
    for generated in document.get("generated_from", []):
        ledger_path = REPOSITORY / generated.get("ledger", "")
        result.require(
            ledger_path.is_file(),
            f"chapter coverage source ledger missing: {generated.get('ledger')}",
        )
        if ledger_path.is_file():
            result.require(
                hashlib.sha256(ledger_path.read_bytes()).hexdigest()
                == generated.get("sha256"),
                f"chapter coverage source ledger drift: {generated.get('ledger')}",
            )
    result.notes.append(
        f"chapter coverage: {len(document.get('chapters', []))} exact hashed records"
    )


def validate_cross_references(
    result: Validation,
    concept_ids: set[str],
    conflict_ids: set[str],
) -> None:
    procedures = load_yaml(ROOT / "procedures.yaml").get("procedures", [])
    procedure_ids = {item.get("id") for item in procedures}
    for procedure in procedures:
        related = procedure.get("related_concepts", [])
        result.require(
            not duplicate_values(related),
            f"{procedure.get('id')}: duplicate related concepts {duplicate_values(related)}",
        )
        for concept_id in related:
            result.require(
                concept_id in concept_ids,
                f"{procedure.get('id')}: unknown concept {concept_id}",
            )

    lenses = load_yaml(ROOT / "context-lenses.yaml").get("lenses", [])
    lens_ids = {item.get("id") for item in lenses}
    for lens in lenses:
        emphasized = lens.get("emphasize_concepts", [])
        result.require(
            not duplicate_values(emphasized),
            f"{lens.get('id')}: duplicate emphasized concepts {duplicate_values(emphasized)}",
        )
        for concept_id in emphasized:
            result.require(
                concept_id in concept_ids,
                f"{lens.get('id')}: unknown concept {concept_id}",
            )

    conflicts = load_yaml(ROOT / "conflicts.yaml").get("conflicts", [])
    graph_nodes = load_yaml(ROOT / "graph" / "nodes.yaml").get("nodes", [])
    graph_formulations = load_yaml(ROOT / "graph" / "formulations.yaml").get(
        "formulations", []
    )
    edges = load_yaml(ROOT / "graph" / "edges.yaml").get("edges", [])
    conflict_node_ids = {
        node.get("id") for node in graph_nodes if node.get("kind") == "conflict"
    }
    for conflict in conflicts:
        conflict_id = conflict["conflict_id"]
        result.require(
            conflict_id in conflict_node_ids,
            f"{conflict_id}: missing canonical graph conflict node",
        )
        related_concepts = set(conflict.get("related_concepts", []))
        for concept_id in related_concepts:
            result.require(
                concept_id in concept_ids,
                f"{conflict_id}: unknown related concept {concept_id}",
            )
        participants = {
            edge.get("from")
            for edge in edges
            if edge.get("relation") == "participates-in"
            and edge.get("to") == conflict_id
            and edge.get("conflict_ref") == conflict_id
        }
        result.require(
            participants == related_concepts,
            f"{conflict_id}: graph participants {sorted(participants)} do not match related concepts {sorted(related_concepts)}",
        )
        for position in conflict.get("positions", []):
            for support in position.get("source_support", []):
                relative_path, heading = support["locator"].split(" :: ", 1)
                graph_locator = f"{relative_path}#{heading}"
                projected = any(
                    formulation.get("conflict_ref") == conflict_id
                    and formulation.get("position_ref") == position.get("id")
                    and formulation.get("source_id") == support.get("source_id")
                    and formulation.get("locator") == graph_locator
                    and any(
                        mapping.get("node_id") == conflict_id
                        and mapping.get("relationship_to_canonical")
                        == support.get("relationship")
                        for mapping in formulation.get("mappings", [])
                    )
                    for formulation in graph_formulations
                )
                result.require(
                    projected,
                    f"{conflict_id}/{position.get('id')}: source support is not projected with relationship {support.get('relationship')}: {graph_locator}",
                )
    for edge in edges:
        if "conflict_ref" in edge:
            result.require(
                edge["conflict_ref"] in conflict_ids,
                f"{edge.get('id')}: unknown conflict {edge['conflict_ref']}",
            )

    routing = load_yaml(ROOT / "routing-index.yaml")
    for artifact in routing.get("always_load", {}).get("artifacts", []):
        result.require(
            (ROOT / artifact).is_file(),
            f"routing always-load artifact missing: {artifact}",
        )
    for concept_id in routing.get("always_load", {}).get("concepts", []):
        result.require(
            concept_id in concept_ids,
            f"routing always-load concept unknown: {concept_id}",
        )
    routes = routing.get("concept_routes", [])
    route_ids = [item.get("concept_id") for item in routes]
    result.require(
        not duplicate_values(route_ids),
        f"duplicate concept routes: {duplicate_values(route_ids)}",
    )
    result.require(
        set(route_ids) == concept_ids,
        "routing index does not contain exactly one route per concept",
    )
    evidence_ids = {
        item.get("id")
        for item in load_yaml(ROOT / "evidence-taxonomy.yaml").get("classes", [])
    }
    for bundle in routing.get("role_bundles", []):
        for concept_id in (
            bundle.get("core_concepts", [])
            + bundle.get("default_concepts", [])
            + bundle.get("conditional_concepts", [])
        ):
            result.require(
                concept_id in concept_ids,
                f"role {bundle.get('role')}: unknown concept {concept_id}",
            )
        for procedure_id in bundle.get("procedures", []):
            result.require(
                procedure_id in procedure_ids,
                f"role {bundle.get('role')}: unknown procedure {procedure_id}",
            )
        for lens_id in bundle.get("context_lenses", []):
            result.require(
                lens_id in lens_ids,
                f"role {bundle.get('role')}: unknown lens {lens_id}",
            )
        for conflict_id in bundle.get("conflicts", []):
            result.require(
                conflict_id in conflict_ids,
                f"role {bundle.get('role')}: unknown conflict {conflict_id}",
            )
    for bundle in routing.get("task_bundles", []):
        for concept_id in bundle.get("primary_concepts", []) + bundle.get(
            "conditional_concepts", []
        ):
            result.require(
                concept_id in concept_ids,
                f"task {bundle.get('task')}: unknown concept {concept_id}",
            )
        for procedure_id in bundle.get("procedures", []):
            result.require(
                procedure_id in procedure_ids,
                f"task {bundle.get('task')}: unknown procedure {procedure_id}",
            )
        for evidence_id in bundle.get("evidence", []):
            result.require(
                evidence_id in evidence_ids,
                f"task {bundle.get('task')}: unknown evidence class {evidence_id}",
            )
    for bundle in routing.get("language_bundles", []):
        for concept_id in bundle.get("concepts", []):
            result.require(
                concept_id in concept_ids,
                f"language {bundle.get('language')}: unknown concept {concept_id}",
            )
        for lens_id in bundle.get("context_lenses", []):
            result.require(
                lens_id in lens_ids,
                f"language {bundle.get('language')}: unknown lens {lens_id}",
            )
    result.notes.append(
        f"routing: {len(routes)} concept routes, {len(routing.get('role_bundles', []))} role bundles, "
        f"{len(routing.get('task_bundles', []))} task bundles"
    )


def validate_techniques(result: Validation, concept_ids: set[str]) -> None:
    schema = json.loads(
        (ROOT / "schemas" / "techniques.schema.json").read_text(encoding="utf-8")
    )
    source_by_id = source_registry()
    records: list[dict[str, Any]] = []
    for relative in ("techniques/architecture.yaml", "techniques/domain.yaml"):
        path = ROOT / relative
        result.require(
            path.is_file(), f"required artifact missing: doctrine/{relative}"
        )
        if not path.is_file():
            continue
        document = load_yaml(path)
        result.schema(document, schema, f"doctrine/{relative}")
        records.extend(document.get("techniques", []))
    ids = [item.get("id") for item in records]
    result.require(
        not duplicate_values(ids), f"duplicate technique IDs: {duplicate_values(ids)}"
    )
    candidate_ids = [item.get("candidate_id") for item in records]
    result.require(
        not duplicate_values(candidate_ids),
        f"duplicate technique candidate IDs: {duplicate_values(candidate_ids)}",
    )
    expected_candidates = {f"TECH-ARC-{index:03d}" for index in range(1, 21)} | {
        f"TECH-DOM-{index:03d}" for index in range(1, 19)
    }
    result.require(
        set(candidate_ids) == expected_candidates,
        "technique candidate sequence is incomplete",
    )
    for record in records:
        technique_id = record.get("id", "<missing>")
        for concept_id in record.get("related_concepts", []):
            result.require(
                concept_id in concept_ids,
                f"{technique_id}: unknown related concept {concept_id}",
            )
        for index, support in enumerate(record.get("source_support", []), start=1):
            validate_source_support(
                result, f"{technique_id} support {index}", support, source_by_id
            )
    result.require(
        len(records) == 38, f"technique catalog has {len(records)} records, expected 38"
    )
    result.notes.append(f"techniques: {len(records)} contextual records")


def validate_required_artifacts(result: Validation) -> None:
    required = [
        "bibliography.json",
        "chapter-coverage.yaml",
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
        result.require(
            (ROOT / relative).is_file(),
            f"required artifact missing: doctrine/{relative}",
        )
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
    result.require(
        expected <= procedure_ids,
        f"missing required procedures: {sorted(expected - procedure_ids)}",
    )
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
    result.notes.append(
        f"machine files: {len(yaml_paths)} YAML and {len(json_paths)} JSON parse"
    )


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
            validate_bibliography(result)
            validate_corpus_map(result)
            validate_traceability(result)
            validate_chapter_coverage(result)
            concept_ids = validate_concepts(
                result, graph_nodes, source_ids, conflict_ids
            )
            validate_cross_references(result, concept_ids, conflict_ids)
            validate_techniques(result, concept_ids)
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        yaml.YAMLError,
        json.JSONDecodeError,
    ) as error:
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
