#!/usr/bin/env python3
"""Build the exact, hashed chapter-coverage manifest from extraction ledgers."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys
from typing import Any

import yaml


DOCTRINE = Path(__file__).resolve().parents[1]
REPOSITORY = DOCTRINE.parent
OUTPUT = DOCTRINE / "chapter-coverage.yaml"
LEDGERS = (
    DOCTRINE / "_work" / "extractions" / "implementation-sources.md",
    DOCTRINE / "_work" / "extractions" / "architecture-domain-sources.md",
    DOCTRINE / "_work" / "extractions" / "language-performance-sources.md",
    DOCTRINE / "_work" / "extractions" / "change-legacy-sources.md",
    DOCTRINE / "_work" / "extractions" / "operations-sources.md",
    DOCTRINE / "_work" / "extractions" / "testing-sources.md",
    DOCTRINE / "_work" / "extractions" / "go-concurrency-sources.md",
    DOCTRINE / "_work" / "extractions" / "data-sources.md",
    DOCTRINE / "_work" / "extractions" / "organization-python-sources.md",
)
SOURCE_ALIASES = {
    "ADP": "SRC-ADPCH3",
    "APOSD": "SRC-APOSD",
    "APWP": "SRC-APWP",
    "CA": "SRC-CA",
    "CC": "SRC-CC",
    "CIG": "SRC-CIG",
    "DDD": "SRC-DDD",
    "DDIA": "SRC-DDIA2",
    "EGO": "SRC-EGO",
    "FP": "SRC-FP",
    "FSA": "SRC-FSA",
    "GO": "SRC-100GO",
    "PP": "SRC-PP",
    "REF": "SRC-REF",
    "RI": "SRC-RI",
    "SDX": "SRC-SDX",
    "SEAG": "SRC-SEAG",
    "UT": "SRC-UT",
    "WELC": "SRC-WELC",
}
ROW_RE = re.compile(
    r"^\|\s*`(?P<path>[A-Z]+_ROOT/chapters/[^`]+)`\s*"
    r"\|\s*(?P<title>.*?)\s*\|\s*(?P<disposition>.*?)\s*\|\s*$"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a mapping")
    return value


def source_aliases(doctrine: Path = DOCTRINE) -> dict[str, tuple[str, str]]:
    registry = load_yaml(doctrine / "sources.yaml").get("sources", [])
    by_id = {record["id"]: record for record in registry}
    return {
        alias: (source_id, by_id[source_id]["corpus_path"])
        for alias, source_id in SOURCE_ALIASES.items()
    }


def parse_ledger(
    ledger: Path,
    repository: Path,
    aliases: dict[str, tuple[str, str]],
) -> list[dict[str, str]]:
    """Parse chapter table rows into exact repository-native coverage records."""
    records: list[dict[str, str]] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        raw_path = match.group("path")
        alias, suffix = raw_path.split("_ROOT/", 1)
        if alias not in aliases:
            raise ValueError(f"{ledger}: unknown source alias {alias}")
        source_id, corpus_path = aliases[alias]
        chapter_path = f"{corpus_path}/{suffix}"
        path = repository / chapter_path
        if not path.is_file():
            raise ValueError(f"{ledger}: covered chapter missing: {chapter_path}")
        records.append(
            {
                "source_id": source_id,
                "chapter_path": chapter_path,
                "title": match.group("title").strip().strip("`"),
                "disposition": match.group("disposition").strip(),
                "sha256": sha256_file(path),
            }
        )
    return records


def build_document(
    repository: Path = REPOSITORY,
    doctrine: Path = DOCTRINE,
    ledgers: tuple[Path, ...] = LEDGERS,
) -> dict[str, Any]:
    aliases = source_aliases(doctrine)
    records = [
        record
        for ledger in ledgers
        for record in parse_ledger(ledger, repository, aliases)
    ]
    paths = [record["chapter_path"] for record in records]
    if len(paths) != len(set(paths)):
        duplicates = sorted(path for path in set(paths) if paths.count(path) > 1)
        raise ValueError(f"duplicate covered chapter paths: {duplicates}")
    return {
        "schema_version": "chapter-coverage/1",
        "generated_from": [
            {
                "ledger": ledger.relative_to(repository).as_posix(),
                "sha256": sha256_file(ledger),
            }
            for ledger in ledgers
        ],
        "chapters": sorted(records, key=lambda record: record["chapter_path"]),
    }


def serialized(document: dict[str, Any]) -> str:
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=120)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        document = build_document()
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"chapter coverage: {error}", file=sys.stderr)
        return 1
    expected = serialized(document)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("chapter coverage: manifest is stale; run --write", file=sys.stderr)
            return 1
        print(f"chapter coverage: current ({len(document['chapters'])} chapters)")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"chapter coverage: wrote {OUTPUT} ({len(document['chapters'])} chapters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
