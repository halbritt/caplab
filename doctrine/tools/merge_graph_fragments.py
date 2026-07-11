#!/usr/bin/env python3
"""Merge validated edge fragments into the canonical graph without deletion."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
EDGE_PATH = ROOT / "graph" / "edges.yaml"
FRAGMENTS = ROOT / "_work" / "graph-fragments"


def load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def dump(value: dict[str, Any]) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=1000)


def merged() -> tuple[dict[str, Any], int]:
    document = load(EDGE_PATH)
    edges = document["edges"]
    by_id = {item["id"]: item for item in edges}
    additions = 0
    for path in sorted(FRAGMENTS.glob("*-edges.yaml")):
        for edge in load(path).get("edges", []):
            prior = by_id.get(edge["id"])
            if prior is not None and prior != edge:
                raise ValueError(f"edge collision with different content: {edge['id']} from {path}")
            if prior is None:
                edges.append(edge)
                by_id[edge["id"]] = edge
                additions += 1
    return document, additions


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document, additions = merged()
    if args.check:
        if additions:
            print(f"STALE: {additions} fragment edges not merged", file=sys.stderr)
            return 1
        print("OK: graph fragments are merged")
        return 0
    EDGE_PATH.write_text(dump(document), encoding="utf-8")
    print(f"UPDATED: merged {additions} graph fragment edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
