#!/usr/bin/env python3
"""Calculate deterministic rebuild and reverification impact."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


REVERIFICATION_RELATIONS = {"evaluates", "verifies"}


def manifest_node_ids(manifest: dict[str, object]) -> set[str]:
    return {
        node.get("id")
        for node in manifest.get("nodes", [])
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }


def validate_changed_nodes(node_ids: set[str], changed: set[str]) -> None:
    unknown = changed - node_ids
    if unknown:
        raise ValueError(f"unknown_changed_nodes: {', '.join(sorted(unknown))}")


def consumer_index(
    manifest: dict[str, object], node_ids: set[str]
) -> dict[str, list[tuple[str, str]]]:
    consumers: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for edge in manifest.get("edges", []):
        if not isinstance(edge, dict):
            continue
        provider = edge.get("provider")
        consumer = edge.get("consumer")
        relation = edge.get("relation")
        if provider in node_ids and consumer in node_ids and isinstance(relation, str):
            consumers[provider].append((consumer, relation))
    return consumers


def downstream_state(provider_state: str, relation: str) -> str:
    if relation in REVERIFICATION_RELATIONS:
        return "reverification_required"
    if provider_state == "reverification_required":
        return "reverification_required"
    return "rebuild_required"


def propagate_states(
    consumers: dict[str, list[tuple[str, str]]], changed: set[str]
) -> dict[str, str]:
    states = {node_id: "changed" for node_id in changed}
    queue = collections.deque(sorted(changed))
    while queue:
        provider = queue.popleft()
        for consumer, relation in sorted(consumers.get(provider, [])):
            next_state = downstream_state(states[provider], relation)
            if states.get(consumer) in {"rebuild_required", next_state}:
                continue
            states[consumer] = next_state
            queue.append(consumer)
    return states


def impact_report(
    node_ids: set[str], changed: set[str], states: dict[str, str]
) -> dict[str, list[str]]:
    affected = set(states) - changed
    return {
        "changed": sorted(changed),
        "rebuild_required": sorted(
            node_id for node_id in affected if states[node_id] == "rebuild_required"
        ),
        "reverification_required": sorted(
            node_id
            for node_id in affected
            if states[node_id] == "reverification_required"
        ),
        "unaffected": sorted(node_ids - set(states)),
    }


def calculate_impact(manifest: object, changed: set[str]) -> dict[str, list[str]]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest_must_be_an_object")
    node_ids = manifest_node_ids(manifest)
    validate_changed_nodes(node_ids, changed)
    consumers = consumer_index(manifest, node_ids)
    states = propagate_states(consumers, changed)
    return impact_report(node_ids, changed, states)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate downstream impact from changed manifest nodes."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--changed", nargs="+", required=True)
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        impact = calculate_impact(manifest, set(args.changed))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    print(json.dumps(impact, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
