#!/usr/bin/env python3
"""Project concept records into the repository-native doctrine graph.

The graph keeps hand-curated nodes, formulations, and edges. This command adds
or refreshes projected Concept Records, source support, conflict records,
concept confidence/status, conflict participation, and routing adjacency. It
removes stale projector-owned records but never deletes curated graph material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a mapping")
    return value


def digest(*values: str) -> str:
    joined = "\0".join(values).encode()
    return hashlib.sha256(joined).hexdigest()[:12]


def locator_for_graph(locator: str) -> str:
    if " :: " not in locator:
        raise ValueError(f"malformed concept locator: {locator}")
    path, heading = locator.split(" :: ", 1)
    return f"{path}#{heading}"


def status_for(confidence: str) -> str:
    if confidence == "contested":
        return "contested"
    if confidence in {"contextual", "weak"}:
        return "contextual"
    return "canonical"


def kind_for(concept: dict[str, Any]) -> str:
    concept_id = concept["id"]
    if any(
        word in concept_id
        for word in ("evidence", "baseline", "validity", "preservation")
    ):
        return "proof-obligation"
    if any(
        word in concept_id
        for word in ("seam", "context", "boundary", "cache", "repository", "factory")
    ):
        return "pattern"
    if any(word in concept_id for word in ("procedure", "loop", "campaign")):
        return "procedure"
    if concept["confidence"] in {"contextual", "weak"}:
        return "heuristic"
    return "principle"


def tags_for(concept: dict[str, Any]) -> list[str]:
    tags = [concept["category"]]
    for value in concept.get("retrieval_terms", []):
        tag = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        if tag and tag not in tags:
            tags.append(tag)
        if len(tags) == 5:
            break
    return tags


def concept_documents(root: Path) -> list[dict[str, Any]]:
    concepts: list[dict[str, Any]] = []
    for path in sorted((root / "concepts").glob("*.yaml")):
        concepts.extend(load(path).get("concepts", []))
    return concepts


def conflict_records(root: Path) -> list[dict[str, Any]]:
    path = root / "conflicts.yaml"
    if not path.is_file():
        return []
    document = load(path)
    local_schema = root / "schemas" / "graph.schema.json"
    schema_path = (
        local_schema
        if local_schema.is_file()
        else ROOT / "schemas" / "graph.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    document_schema = {
        "$schema": schema["$schema"],
        "$ref": "#/$defs/conflictDocument",
        "$defs": schema["$defs"],
    }
    errors = sorted(
        jsonschema.Draft202012Validator(document_schema).iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise ValueError(
            f"invalid conflict registry {path} at {location}: {error.message}"
        )
    conflicts = document["conflicts"]
    conflict_ids = [record["conflict_id"] for record in conflicts]
    if len(conflict_ids) != len(set(conflict_ids)):
        raise ValueError(f"invalid conflict registry {path}: duplicate conflict_id")
    for record in conflicts:
        position_ids = [position["id"] for position in record["positions"]]
        if len(position_ids) != len(set(position_ids)):
            raise ValueError(
                f"invalid conflict registry {path}: {record['conflict_id']} "
                "has duplicate position ids"
            )
    return conflicts


def formulation_id(concept_id: str, support: dict[str, str]) -> str:
    source = support["source_id"].removeprefix("SRC-")
    stable_locator = re.sub(r" @@ occurrence=\d+$", "", support["locator"])
    return f"F-CONCEPT-{source}-{digest(concept_id, stable_locator, support['contribution'])}"


def projected_formulation(
    concept: dict[str, Any], support: dict[str, str]
) -> dict[str, Any]:
    concept_id = concept["id"]
    return {
        "id": formulation_id(concept_id, support),
        "source_id": support["source_id"],
        "locator": locator_for_graph(support["locator"]),
        "mappings": [
            {
                "node_id": concept_id,
                "relationship_to_canonical": support["relationship"],
            }
        ],
        "paraphrase": support["contribution"],
        "conditions": (
            "Canonical mapping applicability (not attributed to the source): "
            + "; ".join(concept["applicable_when"])
        ),
        "caveats": (
            "Canonical policy caveat (not attributed to the source): this mapping "
            "is bounded by the concept's required evidence, preservation rules, "
            "repository contracts, and stated applicability."
        ),
        "context_basis": {
            "conditions": "canonical-mapping",
            "caveats": "canonical-policy",
        },
    }


def converged_concept_formulations(
    concepts: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, list[str]], dict[str, str]]:
    """Converge only exactly identical source formulations.

    The source, locator, and source-attributed contribution form the identity.
    Applicability and relationship remain mapping-specific so convergence does
    not erase the concepts to which the formulation was applied.
    """
    groups: dict[
        tuple[str, str, str],
        list[tuple[dict[str, Any], dict[str, str], dict[str, Any]]],
    ] = {}
    for concept in sorted(concepts, key=lambda item: item["id"]):
        for support in concept["source_support"]:
            key = (
                support["source_id"],
                support["locator"],
                support["contribution"],
            )
            groups.setdefault(key, []).append(
                (concept, support, projected_formulation(concept, support))
            )

    formulations: list[dict[str, Any]] = []
    concept_formulations: dict[str, list[str]] = {
        concept["id"]: [] for concept in concepts
    }
    aliases: dict[str, str] = {}
    for entries in groups.values():
        candidate_ids = sorted(entry[2]["id"] for entry in entries)
        survivor_id = candidate_ids[0]
        formulation = dict(entries[0][2])
        formulation["id"] = survivor_id
        mappings = {
            (concept["id"], support["relationship"]): {
                "node_id": concept["id"],
                "relationship_to_canonical": support["relationship"],
            }
            for concept, support, _candidate in entries
        }
        formulation["mappings"] = [mappings[key] for key in sorted(mappings)]
        if len({concept["id"] for concept, _support, _candidate in entries}) > 1:
            applicability = []
            for concept, _support, _candidate in entries:
                clause = f"{concept['id']}: {'; '.join(concept['applicable_when'])}"
                if clause not in applicability:
                    applicability.append(clause)
            formulation["conditions"] = (
                "Canonical mapped applicability (not attributed to the sources): "
                + " | ".join(applicability)
            )
        formulations.append(formulation)
        for concept, _support, candidate in entries:
            aliases[candidate["id"]] = survivor_id
            if survivor_id not in concept_formulations[concept["id"]]:
                concept_formulations[concept["id"]].append(survivor_id)
    return formulations, concept_formulations, aliases


def conflict_formulation_id(
    conflict_id: str, position_id: str, support: dict[str, str]
) -> str:
    source = support["source_id"].removeprefix("SRC-")
    stable_locator = re.sub(r" @@ occurrence=\d+$", "", support["locator"])
    suffix = digest(conflict_id, position_id, stable_locator, support["contribution"])
    return f"F-CONFLICT-{source}-{suffix}"


def projected_conflict_formulation(
    conflict: dict[str, Any], position: dict[str, Any], support: dict[str, str]
) -> dict[str, Any]:
    conflict_id = conflict["conflict_id"]
    position_id = position["id"]
    return {
        "id": conflict_formulation_id(conflict_id, position_id, support),
        "source_id": support["source_id"],
        "locator": locator_for_graph(support["locator"]),
        "mappings": [
            {
                "node_id": conflict_id,
                "relationship_to_canonical": support["relationship"],
            }
        ],
        "paraphrase": support["contribution"],
        "conditions": support.get(
            "conditions",
            f"Applies to position '{position_id}' within {conflict_id} under its "
            "evidence-selection rule.",
        ),
        "caveats": support.get(
            "caveats",
            "This evidence supports one position; it does not decide the conflict. "
            f"Basis: {position['basis']['rationale']}",
        ),
        "context_basis": {
            "conditions": (
                "source-specific" if "conditions" in support else "conflict-position"
            ),
            "caveats": (
                "source-specific" if "caveats" in support else "conflict-position"
            ),
        },
        "conflict_ref": conflict_id,
        "position_ref": position_id,
    }


def projected_conflict_node(
    conflict: dict[str, Any], formulation_ids: list[str]
) -> dict[str, Any]:
    conflict_id = conflict["conflict_id"]
    positions = " | ".join(
        f"{position['id']}: {position['claim']}" for position in conflict["positions"]
    )
    return {
        "id": conflict_id,
        "projection": {"owner": "conflict-registry", "source_id": conflict_id},
        "kind": "conflict",
        "label": conflict_id.removeprefix("conflict-").replace("-", " ").title(),
        "definition": f"Contested positions: {positions}",
        "operational_significance": conflict["decision_rule"],
        "status": "contested",
        "confidence": "contested",
        "doctrine_refs": [conflict_id],
        "formulations": formulation_ids,
        "tags": ["conflict", conflict["disagreement_kind"]],
    }


def projected_conflict_synthesis(
    concept_id: str, conflict: dict[str, Any]
) -> dict[str, Any]:
    conflict_id = conflict["conflict_id"]
    return {
        "origin": "projected",
        "rationale": (
            f"The conflict registry explicitly associates {concept_id} with {conflict_id}; "
            "the participates-in relationship is a doctrine projection, not a claim "
            "attributed directly to either cited source formulation."
        ),
        "rivals": [
            f"{concept_id} may be active without {conflict_id} when repository "
            "evidence already selects or excludes every competing position."
        ],
        "falsifiers": [
            "The accepted doctrine or repository contract removes "
            f"{concept_id} from the decision scope of {conflict_id}."
        ],
    }


def projected_node(
    concept: dict[str, Any], formulation_ids: list[str]
) -> dict[str, Any]:
    concept_id = concept["id"]
    return {
        "id": concept_id,
        "projection": {"owner": "concept-record", "source_id": concept_id},
        "kind": kind_for(concept),
        "label": concept["title"],
        "definition": concept["claim"],
        "operational_significance": concept["why_it_matters"],
        "status": status_for(concept["confidence"]),
        "confidence": concept["confidence"],
        "doctrine_refs": [concept_id],
        "formulations": formulation_ids,
        "tags": tags_for(concept),
    }


def is_projected_node(node: dict[str, Any]) -> bool:
    projection = node.get("projection", {})
    if projection.get("owner") == "concept-record":
        return True
    formulations = node.get("formulations", [])
    return bool(formulations) and all(
        formulation_id.startswith("F-CONCEPT-") for formulation_id in formulations
    )


def replace_owned_formulations(
    existing: list[str], expected_owned: list[str]
) -> list[str]:
    first_owned = next(
        (
            index
            for index, formulation_id in enumerate(existing)
            if formulation_id.startswith("F-CONCEPT-")
        ),
        len(existing),
    )
    before = [
        formulation_id
        for formulation_id in existing[:first_owned]
        if not formulation_id.startswith("F-CONCEPT-")
    ]
    after = [
        formulation_id
        for formulation_id in existing[first_owned:]
        if not formulation_id.startswith("F-CONCEPT-")
    ]
    return before + expected_owned + after


def projected_synthesis(edge: dict[str, Any]) -> dict[str, Any]:
    source = edge["from"]
    target = edge["to"]
    relation = edge["relation"]
    return {
        "origin": "projected",
        "rationale": (
            f"The cited formulations for {source} and {target} are combined to infer "
            f"a '{relation}' relationship under the edge conditions; the complete "
            "relationship is a synthesis and is not attributed directly to either source."
        ),
        "rivals": [
            f"{source} and {target} may apply independently when the edge conditions do not hold."
        ],
        "falsifiers": [
            f"Repository or source evidence shows that the conditions hold while the "
            f"claimed '{relation}' relationship between {source} and {target} is absent."
        ],
    }


def validate_semantic_edge_provenance(
    edges: list[dict[str, Any]], formulations: list[dict[str, Any]]
) -> None:
    formulation_by_id = {item["id"]: item for item in formulations}
    for edge in edges:
        mapped_nodes: set[str] = set()
        for formulation_id in edge["provenance"]:
            formulation = formulation_by_id.get(formulation_id)
            if formulation is None:
                raise ValueError(
                    f"semantic edge {edge['id']} cites unknown formulation {formulation_id}"
                )
            mapped_nodes.update(
                mapping["node_id"] for mapping in formulation.get("mappings", [])
            )
        for endpoint in (edge["from"], edge["to"]):
            if endpoint not in mapped_nodes:
                raise ValueError(
                    f"semantic edge {edge['id']} provenance does not cover endpoint {endpoint}"
                )


def project(
    root: Path = ROOT,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, int],
]:
    graph = root / "graph"
    nodes_doc = load(graph / "nodes.yaml")
    formulations_doc = load(graph / "formulations.yaml")
    edges_doc = load(graph / "edges.yaml")
    concepts = concept_documents(root)
    conflicts = conflict_records(root)

    original_nodes = nodes_doc["nodes"]
    original_formulations = formulations_doc["formulations"]
    original_edges = edges_doc["edges"]
    # Historical E-ROUTE records were generated retrieval adjacency presented
    # as source-supported semantic edges. They are migrated to routing-graph.
    edges: list[dict[str, Any]] = []
    for original_edge in original_edges:
        if original_edge["id"].startswith(("E-ROUTE-", "E-CONFLICT-")):
            continue
        edge = dict(original_edge)
        if (
            edge["derivation"] == "synthesized"
            and edge.get("synthesis", {}).get("origin") != "curated"
        ):
            edge["synthesis"] = projected_synthesis(edge)
        edges.append(edge)
    edges_doc["edges"] = edges
    concept_by_id = {item["id"]: item for item in concepts}
    conflict_by_id = {item["conflict_id"]: item for item in conflicts}
    for conflict in conflicts:
        missing = sorted(set(conflict["related_concepts"]) - set(concept_by_id))
        if missing:
            raise ValueError(
                f"{conflict['conflict_id']} references unknown related concepts: "
                f"{', '.join(missing)}"
            )
    projection_stats = {
        "concept_nodes": len(concepts),
        "semantic_edges_removed": len(original_edges) - len(edges),
    }

    (
        projected_concept_formulations,
        concept_formulations,
        formulation_aliases,
    ) = converged_concept_formulations(concepts)
    for edge in edges:
        edge["provenance"] = list(
            dict.fromkeys(
                formulation_aliases.get(formulation_id, formulation_id)
                for formulation_id in edge["provenance"]
            )
        )

    conflict_formulations: dict[str, list[str]] = {}
    projected_conflict_formulations: list[dict[str, Any]] = []
    for conflict in sorted(conflicts, key=lambda item: item["conflict_id"]):
        conflict_id = conflict["conflict_id"]
        owned: list[dict[str, Any]] = []
        for position in conflict["positions"]:
            owned.extend(
                projected_conflict_formulation(conflict, position, support)
                for support in position["source_support"]
            )
        if not owned:
            raise ValueError(
                f"{conflict_id} cannot be projected: no position has source support"
            )
        projected_conflict_formulations.extend(owned)
        conflict_formulations[conflict_id] = [item["id"] for item in owned]

    curated_formulations: list[dict[str, Any]] = []
    for original in original_formulations:
        if original["id"].startswith(("F-CONCEPT-", "F-CONFLICT-")):
            continue
        formulation = dict(original)
        formulation.setdefault(
            "context_basis",
            {"conditions": "source-specific", "caveats": "source-specific"},
        )
        curated_formulations.append(formulation)
    formulations = (
        curated_formulations
        + projected_concept_formulations
        + projected_conflict_formulations
    )
    formulations_doc["formulations"] = formulations

    nodes: list[dict[str, Any]] = []
    seen_concepts: set[str] = set()
    for original in original_nodes:
        node_id = original["id"]
        if (
            original.get("projection", {}).get("owner") == "conflict-registry"
            or node_id in conflict_by_id
        ):
            continue
        concept = concept_by_id.get(node_id)
        if is_projected_node(original):
            if concept is not None:
                nodes.append(projected_node(concept, concept_formulations[node_id]))
                seen_concepts.add(node_id)
            continue
        node = dict(original)
        if concept is not None:
            seen_concepts.add(node_id)
            doctrine_refs = list(node.get("doctrine_refs", []))
            if node_id not in doctrine_refs:
                doctrine_refs.append(node_id)
            node["doctrine_refs"] = doctrine_refs
            # Curated nodes may preserve a richer graph-native label and
            # definition, but concept confidence remains owned by the concept
            # record and must not drift between the two views.
            node["confidence"] = concept["confidence"]
            node["status"] = status_for(concept["confidence"])
            node["formulations"] = replace_owned_formulations(
                node.get("formulations", []), concept_formulations[node_id]
            )
        nodes.append(node)

    for concept in sorted(concepts, key=lambda item: item["id"]):
        if concept["id"] not in seen_concepts:
            nodes.append(projected_node(concept, concept_formulations[concept["id"]]))

    for conflict in sorted(conflicts, key=lambda item: item["conflict_id"]):
        conflict_id = conflict["conflict_id"]
        nodes.append(
            projected_conflict_node(conflict, conflict_formulations[conflict_id])
        )

    # Formulation mappings and node formulation lists are two views of the same
    # provenance relation. Normalize both directions without changing node order.
    formulation_order = [item["id"] for item in formulations]
    mapped_to_node: dict[str, set[str]] = {}
    for formulation in formulations:
        for mapping in formulation["mappings"]:
            mapped_to_node.setdefault(mapping["node_id"], set()).add(formulation["id"])
    for node in nodes:
        mapped = mapped_to_node.get(node["id"], set())
        retained = [item for item in node.get("formulations", []) if item in mapped]
        node["formulations"] = retained + [
            item
            for item in formulation_order
            if item in mapped and item not in retained
        ]
    nodes_doc["nodes"] = nodes

    for conflict in sorted(conflicts, key=lambda item: item["conflict_id"]):
        conflict_id = conflict["conflict_id"]
        conflict_provenance = conflict_formulations[conflict_id][0]
        for concept_id in sorted(conflict["related_concepts"]):
            concept_provenance = concept_formulations[concept_id]
            if not concept_provenance:
                raise ValueError(
                    f"{conflict_id} cannot be linked to {concept_id}: "
                    "concept has no source formulation"
                )
            edges.append(
                {
                    "id": f"E-CONFLICT-{digest(concept_id, conflict_id)}",
                    "from": concept_id,
                    "relation": "participates-in",
                    "to": conflict_id,
                    "claim": (
                        f"{concept_id} participates in the evidence-governed choice "
                        f"preserved by {conflict_id}."
                    ),
                    "conditions": [
                        f"{conflict_id} is activated and repository evidence has not "
                        "already excluded the competing positions"
                    ],
                    "derivation": "contested",
                    "confidence": "contested",
                    "provenance": [concept_provenance[0], conflict_provenance],
                    "conflict_ref": conflict_id,
                    "synthesis": projected_conflict_synthesis(concept_id, conflict),
                }
            )
    edges_doc["edges"] = edges
    validate_semantic_edge_provenance(edges, formulations)

    declarations: dict[tuple[str, str], set[str]] = {}
    for concept in sorted(concepts, key=lambda item: item["id"]):
        source = concept["id"]
        for target in sorted(concept["routing"]["related_concepts"]):
            if target not in concept_by_id or target == source:
                continue
            left, right = sorted((source, target))
            declarations.setdefault((left, right), set()).add(source)

    routing_links = [
        {
            "id": f"R-ROUTE-{digest(left, right)}",
            "from": left,
            "relation": "co-retrieved-with",
            "to": right,
            "semantic": False,
            "declared_by": sorted(declared_by),
        }
        for (left, right), declared_by in sorted(declarations.items())
    ]
    routing_doc = {
        "schema_version": "agent-doctrine-routing-graph/1",
        "links": routing_links,
    }
    projection_stats["concept_formulations"] = len(projected_concept_formulations)
    projection_stats["conflict_nodes"] = len(conflicts)
    projection_stats["conflict_formulations"] = len(projected_conflict_formulations)
    projection_stats["conflict_edges"] = sum(
        len(conflict["related_concepts"]) for conflict in conflicts
    )
    projection_stats["routing_links"] = len(routing_links)

    return nodes_doc, formulations_doc, edges_doc, routing_doc, projection_stats


def dump(value: dict[str, Any]) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=1000)


def current_projection(root: Path) -> dict[str, dict[str, Any] | None]:
    graph = root / "graph"
    routing_path = root / "routing-graph" / "links.yaml"
    return {
        "nodes": load(graph / "nodes.yaml"),
        "formulations": load(graph / "formulations.yaml"),
        "edges": load(graph / "edges.yaml"),
        "routing_links": load(routing_path) if routing_path.is_file() else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--write", action="store_true", help="add/update concept projections"
    )
    mode.add_argument(
        "--check", action="store_true", help="fail if the projection is stale"
    )
    parser.add_argument(
        "--doctrine-root",
        type=Path,
        default=ROOT,
        help="doctrine directory to project (defaults to this repository)",
    )
    args = parser.parse_args()

    root = args.doctrine_root.resolve()
    graph = root / "graph"
    routing_graph = root / "routing-graph"
    try:
        current = current_projection(root)
        nodes, formulations, edges, routing, projection_stats = project(root)
    except (KeyError, OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    expected = {
        "nodes": nodes,
        "formulations": formulations,
        "edges": edges,
        "routing_links": routing,
    }
    stale = [name for name, value in expected.items() if current[name] != value]
    if args.check:
        if stale:
            print(f"STALE: projection differs in {', '.join(stale)}", file=sys.stderr)
            return 1
        print("OK: concept-to-graph projection is current")
        return 0

    routing_graph.mkdir(parents=True, exist_ok=True)
    (graph / "nodes.yaml").write_text(dump(nodes), encoding="utf-8")
    (graph / "formulations.yaml").write_text(dump(formulations), encoding="utf-8")
    (graph / "edges.yaml").write_text(dump(edges), encoding="utf-8")
    (routing_graph / "links.yaml").write_text(dump(routing), encoding="utf-8")
    print(f"UPDATED: {', '.join(stale) if stale else 'no changes'}; {projection_stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
