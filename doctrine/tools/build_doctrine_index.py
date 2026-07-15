#!/usr/bin/env python3
"""Compile authoritative doctrine YAML into a deterministic SQLite read model."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

DOCTRINE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = DOCTRINE_ROOT / "runtime" / "doctrine-index.sqlite3"
INDEX_SCHEMA_VERSION = "doctrine-index/1"
SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

DOCTRINE_VERSION_PATHS = (
    "routing-index.yaml",
    "procedures.yaml",
    "context-lenses.yaml",
    "negative-doctrine.yaml",
    "conflicts.yaml",
    "evidence-taxonomy.yaml",
    "authority-model.yaml",
    "change-types.yaml",
    "runtime/evidence-packet.schema.json",
    "runtime/evidence-record.schema.json",
    "graph/nodes.yaml",
    "graph/formulations.yaml",
    "graph/edges.yaml",
)

DOCUMENT_PATHS = (
    "routing-index.yaml",
    "conflicts.yaml",
    "procedures.yaml",
    "context-lenses.yaml",
    "negative-doctrine.yaml",
    "evidence-taxonomy.yaml",
    "authority-model.yaml",
    "change-types.yaml",
    "sources.yaml",
    "traceability.yaml",
)

LOGICAL_PRIMARY_KEYS = {
    "documents": lambda row: (row[0],),
    "concepts": lambda row: (row[0],),
    "routes": lambda row: (row[0], row[1], row[3]),
    "source_support": lambda row: (row[0], row[1]),
    "nodes": lambda row: (row[0],),
    "formulations": lambda row: (row[0],),
    "formulation_mappings": lambda row: (row[0], row[1]),
    "edges": lambda row: (row[0],),
}

LOGICAL_TABLE_QUERIES = {
    "documents": (
        "SELECT document_key, schema_version, document_json "
        "FROM documents ORDER BY document_key"
    ),
    "concepts": (
        "SELECT concept_id, artifact_path, ordinal, retrieval_terms_json, "
        "concept_json FROM concepts ORDER BY concept_id"
    ),
    "routes": (
        "SELECT route_kind, route_key, concept_id, ordinal, route_json "
        "FROM routes ORDER BY route_kind, route_key, ordinal"
    ),
    "source_support": (
        "SELECT concept_id, ordinal, source_id, relationship, locator, "
        "support_json FROM source_support ORDER BY concept_id, ordinal"
    ),
    "nodes": (
        "SELECT node_id, node_kind, label, status, node_json "
        "FROM nodes ORDER BY node_id"
    ),
    "formulations": (
        "SELECT formulation_id, source_id, locator, formulation_json "
        "FROM formulations ORDER BY formulation_id"
    ),
    "formulation_mappings": (
        "SELECT formulation_id, ordinal, node_id, relationship, mapping_json "
        "FROM formulation_mappings ORDER BY formulation_id, ordinal"
    ),
    "edges": (
        "SELECT edge_id, from_node_id, relation, to_node_id, conflict_ref, "
        "edge_json FROM edges ORDER BY edge_id"
    ),
}


def load_yaml(relative_path: str) -> dict[str, Any]:
    path = DOCTRINE_ROOT / relative_path
    with path.open(encoding="utf-8") as stream:
        document = yaml.load(stream, Loader=SAFE_LOADER)
    if not isinstance(document, dict):
        raise ValueError(f"{path}: expected a mapping at document root")
    return document


def hash_paths(relative_paths: list[str]) -> str:
    digest = hashlib.sha256()
    for relative_path in sorted(relative_paths):
        path = DOCTRINE_ROOT / relative_path
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def doctrine_version() -> str:
    paths = [*DOCTRINE_VERSION_PATHS]
    paths.extend(
        str(path.relative_to(DOCTRINE_ROOT))
        for path in sorted((DOCTRINE_ROOT / "concepts").glob("*.yaml"))
    )
    return "doctrine-" + hash_paths(paths)[:16]


def corpus_version() -> str:
    sources = load_yaml("sources.yaml").get("sources", [])
    source_hashes = sorted(source["source_sha256"] for source in sources)
    digest = hashlib.sha256("\n".join(source_hashes).encode("utf-8")).hexdigest()
    snapshot_date = load_yaml("traceability.yaml")["corpus_snapshot_date"]
    return f"corpus-{snapshot_date}-{digest[:12]}"


def source_fingerprint() -> str:
    paths = sorted(set((*DOCTRINE_VERSION_PATHS, *DOCUMENT_PATHS)))
    paths.extend(
        str(path.relative_to(DOCTRINE_ROOT))
        for path in sorted((DOCTRINE_ROOT / "concepts").glob("*.yaml"))
    )
    return hash_paths(paths)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        default=str,
    )


def metadata(records: dict[str, list[tuple[Any, ...]]]) -> dict[str, str]:
    values = {
        "index_schema_version": INDEX_SCHEMA_VERSION,
        "corpus_version": corpus_version(),
        "doctrine_version": doctrine_version(),
        "source_fingerprint": source_fingerprint(),
    }
    logical_tables = {
        table_name: sorted(rows, key=LOGICAL_PRIMARY_KEYS[table_name])
        for table_name, rows in records.items()
    }
    values["index_content_hash"] = hashlib.sha256(
        canonical_json({"meta": values, "tables": logical_tables}).encode("utf-8")
    ).hexdigest()
    return values


def flattened_routes(
    routing: dict[str, Any],
) -> list[tuple[str, str, str, int, str]]:
    rows: list[tuple[str, str, str, int, str]] = []
    for ordinal, route in enumerate(routing["concept_routes"]):
        rows.append(
            (
                "concept",
                route["concept_id"],
                route["concept_id"],
                ordinal,
                canonical_json(route),
            )
        )

    bundle_shapes = (
        (
            "role",
            "role_bundles",
            "role",
            ("core_concepts", "default_concepts", "conditional_concepts"),
        ),
        (
            "task",
            "task_bundles",
            "task",
            ("primary_concepts", "conditional_concepts"),
        ),
        ("language", "language_bundles", "language", ("concepts",)),
        ("risk", "risk_routes", "risk_class", ("concepts",)),
    )
    for route_kind, bundle_key, key_field, membership_fields in bundle_shapes:
        for bundle in routing[bundle_key]:
            ordinal = 0
            for membership in membership_fields:
                for concept_id in bundle.get(membership, []):
                    rows.append(
                        (
                            route_kind,
                            bundle[key_field],
                            concept_id,
                            ordinal,
                            canonical_json({"membership": membership}),
                        )
                    )
                    ordinal += 1

    always_load = routing["always_load"]
    for ordinal, concept_id in enumerate(always_load["concepts"]):
        rows.append(
            (
                "always-load",
                always_load["policy"],
                concept_id,
                ordinal,
                canonical_json({"membership": "concepts"}),
            )
        )
    return rows


def compile_records() -> dict[str, list[tuple[Any, ...]]]:
    records: dict[str, list[tuple[Any, ...]]] = {
        "documents": [],
        "concepts": [],
        "routes": [],
        "source_support": [],
        "nodes": [],
        "formulations": [],
        "formulation_mappings": [],
        "edges": [],
    }

    for relative_path in DOCUMENT_PATHS:
        document = load_yaml(relative_path)
        records["documents"].append(
            (
                relative_path,
                str(document["schema_version"]),
                canonical_json(document),
            )
        )

    concept_ordinal = 0
    for path in sorted((DOCTRINE_ROOT / "concepts").glob("*.yaml")):
        relative_path = str(path.relative_to(DOCTRINE_ROOT))
        document = load_yaml(relative_path)
        for concept in document["concepts"]:
            concept_id = concept["id"]
            records["concepts"].append(
                (
                    concept_id,
                    relative_path,
                    concept_ordinal,
                    canonical_json(concept["retrieval_terms"]),
                    canonical_json(concept),
                )
            )
            for support_ordinal, support in enumerate(concept["source_support"]):
                records["source_support"].append(
                    (
                        concept_id,
                        support_ordinal,
                        support["source_id"],
                        support["relationship"],
                        support["locator"],
                        canonical_json(support),
                    )
                )
            concept_ordinal += 1

    routing = load_yaml("routing-index.yaml")
    records["routes"].extend(flattened_routes(routing))

    for node in load_yaml("graph/nodes.yaml")["nodes"]:
        records["nodes"].append(
            (
                node["id"],
                node["kind"],
                node["label"],
                node["status"],
                canonical_json(node),
            )
        )

    for formulation in load_yaml("graph/formulations.yaml")["formulations"]:
        formulation_id = formulation["id"]
        records["formulations"].append(
            (
                formulation_id,
                formulation["source_id"],
                formulation["locator"],
                canonical_json(formulation),
            )
        )
        for ordinal, mapping in enumerate(formulation["mappings"]):
            records["formulation_mappings"].append(
                (
                    formulation_id,
                    ordinal,
                    mapping["node_id"],
                    mapping["relationship_to_canonical"],
                    canonical_json(mapping),
                )
            )

    for edge in load_yaml("graph/edges.yaml")["edges"]:
        records["edges"].append(
            (
                edge["id"],
                edge["from"],
                edge["relation"],
                edge["to"],
                edge.get("conflict_ref"),
                canonical_json(edge),
            )
        )

    return records


SCHEMA = """
CREATE TABLE meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE documents (
    document_key TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    document_json TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE concepts (
    concept_id TEXT PRIMARY KEY,
    artifact_path TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    retrieval_terms_json TEXT NOT NULL,
    concept_json TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE routes (
    route_kind TEXT NOT NULL CHECK (
        route_kind IN ('concept', 'role', 'task', 'language', 'risk', 'always-load')
    ),
    route_key TEXT NOT NULL,
    concept_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    route_json TEXT NOT NULL,
    PRIMARY KEY (route_kind, route_key, ordinal),
    FOREIGN KEY (concept_id) REFERENCES concepts(concept_id)
) WITHOUT ROWID;

CREATE INDEX routes_by_concept
    ON routes (concept_id, route_kind, route_key, ordinal);

CREATE TABLE source_support (
    concept_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    source_id TEXT NOT NULL,
    relationship TEXT NOT NULL,
    locator TEXT NOT NULL,
    support_json TEXT NOT NULL,
    PRIMARY KEY (concept_id, ordinal),
    FOREIGN KEY (concept_id) REFERENCES concepts(concept_id)
) WITHOUT ROWID;

CREATE INDEX source_support_by_source
    ON source_support (source_id, concept_id, ordinal);

CREATE TABLE nodes (
    node_id TEXT PRIMARY KEY,
    node_kind TEXT NOT NULL,
    label TEXT NOT NULL,
    status TEXT NOT NULL,
    node_json TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE formulations (
    formulation_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    locator TEXT NOT NULL,
    formulation_json TEXT NOT NULL
) WITHOUT ROWID;

CREATE INDEX formulations_by_source
    ON formulations (source_id, formulation_id);

CREATE TABLE formulation_mappings (
    formulation_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    relationship TEXT NOT NULL,
    mapping_json TEXT NOT NULL,
    PRIMARY KEY (formulation_id, ordinal),
    FOREIGN KEY (formulation_id) REFERENCES formulations(formulation_id),
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
) WITHOUT ROWID;

CREATE INDEX formulation_mappings_by_node
    ON formulation_mappings (node_id, formulation_id, ordinal);

CREATE TABLE edges (
    edge_id TEXT PRIMARY KEY,
    from_node_id TEXT NOT NULL,
    relation TEXT NOT NULL,
    to_node_id TEXT NOT NULL,
    conflict_ref TEXT,
    edge_json TEXT NOT NULL,
    FOREIGN KEY (from_node_id) REFERENCES nodes(node_id),
    FOREIGN KEY (to_node_id) REFERENCES nodes(node_id)
) WITHOUT ROWID;

CREATE INDEX edges_from_node
    ON edges (from_node_id, relation, to_node_id, edge_id);

CREATE INDEX edges_to_node
    ON edges (to_node_id, relation, from_node_id, edge_id);
"""


def create_database(
    path: Path, records: dict[str, list[tuple[Any, ...]]] | None = None
) -> None:
    if records is None:
        records = compile_records()
    with sqlite3.connect(path) as database:
        database.execute("PRAGMA page_size = 4096")
        database.execute("PRAGMA journal_mode = OFF")
        database.execute("PRAGMA synchronous = OFF")
        database.execute("PRAGMA temp_store = MEMORY")
        database.execute("PRAGMA foreign_keys = ON")
        database.executescript(SCHEMA)
        database.executemany(
            "INSERT INTO documents(document_key, schema_version, document_json) "
            "VALUES (?, ?, ?)",
            records["documents"],
        )
        database.executemany(
            "INSERT INTO concepts("
            "concept_id, artifact_path, ordinal, retrieval_terms_json, concept_json"
            ") VALUES (?, ?, ?, ?, ?)",
            records["concepts"],
        )
        database.executemany(
            "INSERT INTO routes(route_kind, route_key, concept_id, ordinal, route_json) "
            "VALUES (?, ?, ?, ?, ?)",
            records["routes"],
        )
        database.executemany(
            "INSERT INTO source_support("
            "concept_id, ordinal, source_id, relationship, locator, support_json"
            ") VALUES (?, ?, ?, ?, ?, ?)",
            records["source_support"],
        )
        database.executemany(
            "INSERT INTO nodes(node_id, node_kind, label, status, node_json) "
            "VALUES (?, ?, ?, ?, ?)",
            records["nodes"],
        )
        database.executemany(
            "INSERT INTO formulations("
            "formulation_id, source_id, locator, formulation_json"
            ") VALUES (?, ?, ?, ?)",
            records["formulations"],
        )
        database.executemany(
            "INSERT INTO formulation_mappings("
            "formulation_id, ordinal, node_id, relationship, mapping_json"
            ") VALUES (?, ?, ?, ?, ?)",
            records["formulation_mappings"],
        )
        database.executemany(
            "INSERT INTO edges("
            "edge_id, from_node_id, relation, to_node_id, conflict_ref, edge_json"
            ") VALUES (?, ?, ?, ?, ?, ?)",
            records["edges"],
        )
        database.executemany(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            sorted(metadata(records).items()),
        )
        database.commit()
        database.execute("VACUUM")


def checksum_path(index: Path) -> Path:
    return Path(f"{index}.sha256")


def checksum_bytes(index: Path) -> bytes:
    return (hashlib.sha256(index.read_bytes()).hexdigest() + "\n").encode("ascii")


def checksum_is_current(index: Path) -> bool:
    checksum = checksum_path(index)
    try:
        return index.is_file() and checksum.is_file() and (
            checksum.read_bytes() == checksum_bytes(index)
        )
    except OSError:
        return False


def schema_signature(database: sqlite3.Connection) -> list[tuple[Any, ...]]:
    return database.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_schema "
        "ORDER BY type, name"
    ).fetchall()


def expected_schema_signature() -> list[tuple[Any, ...]]:
    with sqlite3.connect(":memory:") as database:
        database.executescript(SCHEMA)
        return schema_signature(database)


def database_is_logically_current(
    index: Path, records: dict[str, list[tuple[Any, ...]]]
) -> bool:
    if not index.is_file():
        return False
    try:
        uri = f"{index.resolve().as_uri()}?mode=ro&immutable=1"
        with sqlite3.connect(uri, uri=True) as database:
            if database.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                return False
            if database.execute("PRAGMA foreign_key_check").fetchall():
                return False
            if schema_signature(database) != expected_schema_signature():
                return False
            if database.execute(
                "SELECT key, value FROM meta ORDER BY key"
            ).fetchall() != sorted(metadata(records).items()):
                return False
            for table_name, query in LOGICAL_TABLE_QUERIES.items():
                expected_rows = sorted(
                    records[table_name], key=LOGICAL_PRIMARY_KEYS[table_name]
                )
                if database.execute(query).fetchall() != expected_rows:
                    return False
    except (OSError, sqlite3.Error):
        return False
    return True


def write_index(output: Path) -> bool:
    output.parent.mkdir(parents=True, exist_ok=True)
    records = compile_records()
    checksum = checksum_path(output)
    if database_is_logically_current(output, records):
        expected_checksum = checksum_bytes(output)
        if checksum.is_file() and checksum.read_bytes() == expected_checksum:
            return False
        checksum_descriptor, checksum_temporary_name = tempfile.mkstemp(
            prefix=f".{checksum.name}.", suffix=".tmp", dir=output.parent
        )
        os.close(checksum_descriptor)
        checksum_temporary = Path(checksum_temporary_name)
        try:
            checksum_temporary.write_bytes(expected_checksum)
            os.replace(checksum_temporary, checksum)
            return True
        finally:
            checksum_temporary.unlink(missing_ok=True)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    checksum_descriptor, checksum_temporary_name = tempfile.mkstemp(
        prefix=f".{checksum.name}.", suffix=".tmp", dir=output.parent
    )
    os.close(checksum_descriptor)
    checksum_temporary = Path(checksum_temporary_name)
    try:
        temporary.unlink()
        create_database(temporary, records)
        checksum_temporary.write_bytes(checksum_bytes(temporary))
        os.replace(temporary, output)
        os.replace(checksum_temporary, checksum)
        return True
    finally:
        temporary.unlink(missing_ok=True)
        checksum_temporary.unlink(missing_ok=True)


def check_index(output: Path) -> bool:
    if not checksum_is_current(output):
        return False
    return database_is_logically_current(output, compile_records())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_INDEX)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit nonzero when the requested index is missing or stale; never write it",
    )
    return parser


def main(arguments: list[str] | None = None) -> int:
    options = build_parser().parse_args(arguments)
    output = options.out.resolve()
    if options.check:
        if check_index(output):
            print(f"doctrine index: current ({output})")
            return 0
        print(f"doctrine index: missing or stale ({output})", file=sys.stderr)
        return 1

    changed = write_index(output)
    disposition = "wrote" if changed else "current"
    print(f"doctrine index: {disposition} ({output})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
