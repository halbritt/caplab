#!/usr/bin/env python3
"""Project concept records into the repository-native doctrine graph.

The graph keeps hand-curated nodes, formulations, and edges. This command only
adds or refreshes the projection owned by Concept Record source support and
routing metadata; it never deletes curated graph material.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "graph"


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
    if any(word in concept_id for word in ("evidence", "baseline", "validity", "preservation")):
        return "proof-obligation"
    if any(word in concept_id for word in ("seam", "context", "boundary", "cache", "repository", "factory")):
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


def concept_documents() -> list[dict[str, Any]]:
    concepts: list[dict[str, Any]] = []
    for path in sorted((ROOT / "concepts").glob("*.yaml")):
        concepts.extend(load(path).get("concepts", []))
    return concepts


def formulation_id(concept_id: str, support: dict[str, str]) -> str:
    source = support["source_id"].removeprefix("SRC-")
    return f"F-CONCEPT-{source}-{digest(concept_id, support['locator'], support['contribution'])}"


def project() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, int]]:
    nodes_doc = load(GRAPH / "nodes.yaml")
    formulations_doc = load(GRAPH / "formulations.yaml")
    edges_doc = load(GRAPH / "edges.yaml")
    concepts = concept_documents()

    nodes = nodes_doc["nodes"]
    formulations = formulations_doc["formulations"]
    edges = edges_doc["edges"]
    node_by_id = {item["id"]: item for item in nodes}
    formulation_by_id = {item["id"]: item for item in formulations}
    edge_by_id = {item["id"]: item for item in edges}
    concept_by_id = {item["id"]: item for item in concepts}
    additions = {"nodes": 0, "formulations": 0, "edges": 0, "mappings": 0}

    concept_formulations: dict[str, list[str]] = {}
    for concept in sorted(concepts, key=lambda item: item["id"]):
        concept_id = concept["id"]
        support_ids: list[str] = []
        for support in concept["source_support"]:
            fid = formulation_id(concept_id, support)
            support_ids.append(fid)
            mapping = {
                "node_id": concept_id,
                "relationship_to_canonical": support["relationship"],
            }
            if fid not in formulation_by_id:
                formulation = {
                    "id": fid,
                    "source_id": support["source_id"],
                    "locator": locator_for_graph(support["locator"]),
                    "mappings": [mapping],
                    "paraphrase": support["contribution"],
                    "conditions": "; ".join(concept["applicable_when"]),
                    "caveats": (
                        "This formulation is bounded by the concept's required evidence, "
                        "preservation rules, repository contracts, and stated applicability."
                    ),
                }
                formulations.append(formulation)
                formulation_by_id[fid] = formulation
                additions["formulations"] += 1
            else:
                mappings = formulation_by_id[fid]["mappings"]
                if mapping not in mappings:
                    mappings.append(mapping)
                    additions["mappings"] += 1

        concept_formulations[concept_id] = support_ids
        if concept_id not in node_by_id:
            node = {
                "id": concept_id,
                "kind": kind_for(concept),
                "label": concept["title"],
                "definition": concept["claim"],
                "operational_significance": concept["why_it_matters"],
                "status": status_for(concept["confidence"]),
                "confidence": concept["confidence"],
                "doctrine_refs": [concept_id],
                "formulations": support_ids,
                "tags": tags_for(concept),
            }
            nodes.append(node)
            node_by_id[concept_id] = node
            additions["nodes"] += 1
        else:
            node = node_by_id[concept_id]
            if concept_id not in node["doctrine_refs"]:
                node["doctrine_refs"].append(concept_id)
            for fid in support_ids:
                if fid not in node["formulations"]:
                    node["formulations"].append(fid)

    # Routing relations are deliberately projected as synthesized composition
    # edges. Stronger hand-curated relations coexist with these audit links.
    for concept in sorted(concepts, key=lambda item: item["id"]):
        source = concept["id"]
        for target in sorted(concept["routing"]["related_concepts"]):
            if target not in concept_by_id or target == source:
                continue
            left, right = sorted((source, target))
            edge_id = f"E-ROUTE-{digest(left, right)}"
            if edge_id in edge_by_id:
                continue
            provenance = concept_formulations[source][:2]
            if not provenance:
                continue
            edge = {
                "id": edge_id,
                "from": left,
                "relation": "composes-with",
                "to": right,
                "claim": (
                    f"{concept_by_id[left]['title']} and {concept_by_id[right]['title']} "
                    "must be considered together for at least one declared retrieval route."
                ),
                "conditions": [
                    "the activating role, task, repository signal, language, and risk filters match",
                    "a stronger curated relation does not change the traversal decision",
                ],
                "derivation": "synthesized",
                "confidence": "contextual",
                "provenance": provenance,
            }
            edges.append(edge)
            edge_by_id[edge_id] = edge
            additions["edges"] += 1

    return nodes_doc, formulations_doc, edges_doc, additions


def dump(value: dict[str, Any]) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=1000)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="add/update concept projections")
    mode.add_argument("--check", action="store_true", help="fail if the projection is stale")
    args = parser.parse_args()

    nodes, formulations, edges, additions = project()
    changed = any(additions.values())
    if args.check:
        if changed:
            print(f"STALE: {additions}", file=sys.stderr)
            return 1
        print("OK: concept-to-graph projection is current")
        return 0

    (GRAPH / "nodes.yaml").write_text(dump(nodes), encoding="utf-8")
    (GRAPH / "formulations.yaml").write_text(dump(formulations), encoding="utf-8")
    (GRAPH / "edges.yaml").write_text(dump(edges), encoding="utf-8")
    print(f"UPDATED: {additions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
