import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX_CLI = ROOT / "doctrine" / "tools" / "build_doctrine_index.py"


class DoctrineIndexTests(unittest.TestCase):
    def build_index(self, path, *arguments):
        return subprocess.run(
            [sys.executable, str(INDEX_CLI), "--out", str(path), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def rewrite_checksum(self, path):
        Path(f"{path}.sha256").write_text(
            hashlib.sha256(path.read_bytes()).hexdigest() + "\n",
            encoding="ascii",
        )

    def test_build_creates_queryable_index_with_required_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "doctrine-index.sqlite3"

            result = self.build_index(output)

            self.assertEqual(0, result.returncode, result.stderr)
            checksum = Path(f"{output}.sha256")
            self.assertEqual(
                hashlib.sha256(output.read_bytes()).hexdigest() + "\n",
                checksum.read_text(encoding="ascii"),
            )
            with sqlite3.connect(output) as database:
                tables = {
                    row[0]
                    for row in database.execute(
                        "SELECT name FROM sqlite_schema WHERE type = 'table'"
                    )
                }
                self.assertTrue(
                    {
                        "meta",
                        "documents",
                        "routes",
                        "concepts",
                        "source_support",
                        "nodes",
                        "formulations",
                        "formulation_mappings",
                        "edges",
                    }.issubset(tables)
                )
                meta = dict(database.execute("SELECT key, value FROM meta"))
                self.assertEqual("doctrine-index/1", meta["index_schema_version"])
                self.assertRegex(meta["corpus_version"], r"^corpus-")
                self.assertRegex(meta["doctrine_version"], r"^doctrine-[0-9a-f]{16}$")
                self.assertRegex(meta["index_content_hash"], r"^[0-9a-f]{64}$")
                self.assertRegex(meta["source_fingerprint"], r"^[0-9a-f]{64}$")
                self.assertEqual(
                    "ok", database.execute("PRAGMA integrity_check").fetchone()[0]
                )

    def test_index_preserves_authoritative_records_and_hot_path_routes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "doctrine-index.sqlite3"
            result = self.build_index(output)
            self.assertEqual(0, result.returncode, result.stderr)

            concept_documents = [
                yaml.safe_load(path.read_text(encoding="utf-8"))
                for path in sorted((ROOT / "doctrine" / "concepts").glob("*.yaml"))
            ]
            expected_concepts = [
                concept
                for document in concept_documents
                for concept in document["concepts"]
            ]
            nodes = yaml.safe_load(
                (ROOT / "doctrine" / "graph" / "nodes.yaml").read_text(
                    encoding="utf-8"
                )
            )["nodes"]
            formulations = yaml.safe_load(
                (ROOT / "doctrine" / "graph" / "formulations.yaml").read_text(
                    encoding="utf-8"
                )
            )["formulations"]
            edges = yaml.safe_load(
                (ROOT / "doctrine" / "graph" / "edges.yaml").read_text(
                    encoding="utf-8"
                )
            )["edges"]

            with sqlite3.connect(output) as database:
                self.assertEqual(
                    len(expected_concepts),
                    database.execute("SELECT count(*) FROM concepts").fetchone()[0],
                )
                self.assertEqual(
                    sum(
                        len(concept["source_support"])
                        for concept in expected_concepts
                    ),
                    database.execute(
                        "SELECT count(*) FROM source_support"
                    ).fetchone()[0],
                )
                self.assertEqual(
                    len(nodes),
                    database.execute("SELECT count(*) FROM nodes").fetchone()[0],
                )
                self.assertEqual(
                    len(formulations),
                    database.execute("SELECT count(*) FROM formulations").fetchone()[0],
                )
                self.assertEqual(
                    sum(len(record["mappings"]) for record in formulations),
                    database.execute(
                        "SELECT count(*) FROM formulation_mappings"
                    ).fetchone()[0],
                )
                self.assertEqual(
                    len(edges),
                    database.execute("SELECT count(*) FROM edges").fetchone()[0],
                )

                concept_id = "universal-repository-contract-precedence"
                concept_json = database.execute(
                    "SELECT concept_json FROM concepts WHERE concept_id = ?",
                    (concept_id,),
                ).fetchone()[0]
                expected_concept = next(
                    concept
                    for concept in expected_concepts
                    if concept["id"] == concept_id
                )
                self.assertEqual(expected_concept, json.loads(concept_json))
                retrieval_terms_json = database.execute(
                    "SELECT retrieval_terms_json FROM concepts WHERE concept_id = ?",
                    (concept_id,),
                ).fetchone()[0]
                self.assertEqual(
                    expected_concept["retrieval_terms"],
                    json.loads(retrieval_terms_json),
                )
                route_kinds = {
                    row[0]
                    for row in database.execute(
                        "SELECT DISTINCT route_kind FROM routes"
                    )
                }
                self.assertEqual(
                    {"concept", "role", "task", "language", "risk", "always-load"},
                    route_kinds,
                )
                self.assertEqual(
                    concept_id,
                    database.execute(
                        "SELECT concept_id FROM routes "
                        "WHERE route_kind = 'concept' AND route_key = ?",
                        (concept_id,),
                    ).fetchone()[0],
                )

                document_keys = {
                    row[0]
                    for row in database.execute("SELECT document_key FROM documents")
                }
                self.assertEqual(
                    {
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
                    },
                    document_keys,
                )
                stored_routing = json.loads(
                    database.execute(
                        "SELECT document_json FROM documents "
                        "WHERE document_key = 'routing-index.yaml'"
                    ).fetchone()[0]
                )
                expected_routing = yaml.safe_load(
                    (ROOT / "doctrine" / "routing-index.yaml").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(expected_routing, stored_routing)
                sources_json = database.execute(
                    "SELECT document_json FROM documents "
                    "WHERE document_key = 'sources.yaml'"
                ).fetchone()[0]
                self.assertIn("Bartłomiej Płotka", sources_json)
                self.assertNotIn(r"\u0142", sources_json)
                self.assertEqual(
                    [], database.execute("PRAGMA foreign_key_check").fetchall()
                )

    def test_content_hash_is_recomputable_from_logical_rows_without_self_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "doctrine-index.sqlite3"
            result = self.build_index(output)
            self.assertEqual(0, result.returncode, result.stderr)

            with sqlite3.connect(output) as database:
                meta = dict(database.execute("SELECT key, value FROM meta"))
                expected_hash = meta.pop("index_content_hash")
                queries = {
                    "documents": (
                        "SELECT document_key, schema_version, document_json "
                        "FROM documents ORDER BY document_key"
                    ),
                    "concepts": (
                        "SELECT concept_id, artifact_path, ordinal, "
                        "retrieval_terms_json, concept_json "
                        "FROM concepts ORDER BY concept_id"
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
                        "SELECT formulation_id, ordinal, node_id, relationship, "
                        "mapping_json FROM formulation_mappings "
                        "ORDER BY formulation_id, ordinal"
                    ),
                    "edges": (
                        "SELECT edge_id, from_node_id, relation, to_node_id, "
                        "conflict_ref, edge_json FROM edges ORDER BY edge_id"
                    ),
                }
                tables = {
                    name: database.execute(query).fetchall()
                    for name, query in queries.items()
                }
            logical_content = json.dumps(
                {"meta": meta, "tables": tables},
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            self.assertEqual(expected_hash, hashlib.sha256(logical_content).hexdigest())

    def test_fresh_builds_are_byte_identical_and_unchanged_output_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.sqlite3"
            second = Path(temp_dir) / "second.sqlite3"

            first_result = self.build_index(first)
            second_result = self.build_index(second)

            self.assertEqual(0, first_result.returncode, first_result.stderr)
            self.assertEqual(0, second_result.returncode, second_result.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(
                Path(f"{first}.sha256").read_bytes(),
                Path(f"{second}.sha256").read_bytes(),
            )
            before = first.stat()
            checksum_before = Path(f"{first}.sha256").stat()

            unchanged_result = self.build_index(first)

            self.assertEqual(0, unchanged_result.returncode, unchanged_result.stderr)
            self.assertIn("doctrine index: current", unchanged_result.stdout)
            after = first.stat()
            checksum_after = Path(f"{first}.sha256").stat()
            self.assertEqual(before.st_ino, after.st_ino)
            self.assertEqual(before.st_mtime_ns, after.st_mtime_ns)
            self.assertEqual(checksum_before.st_ino, checksum_after.st_ino)
            self.assertEqual(checksum_before.st_mtime_ns, checksum_after.st_mtime_ns)

    def test_writer_version_only_difference_is_current_and_preserved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "doctrine-index.sqlite3"
            built = self.build_index(output)
            self.assertEqual(0, built.returncode, built.stderr)

            database_bytes = bytearray(output.read_bytes())
            writer_version = int.from_bytes(database_bytes[96:100], "big")
            database_bytes[96:100] = (writer_version - 1).to_bytes(4, "big")
            output.write_bytes(database_bytes)
            self.rewrite_checksum(output)
            expected_bytes = output.read_bytes()
            before = output.stat()
            checksum_before = Path(f"{output}.sha256").stat()

            current = self.build_index(output, "--check")

            self.assertEqual(0, current.returncode, current.stderr)
            self.assertIn("doctrine index: current", current.stdout)
            unchanged = self.build_index(output)
            self.assertEqual(0, unchanged.returncode, unchanged.stderr)
            self.assertIn("doctrine index: current", unchanged.stdout)
            self.assertEqual(expected_bytes, output.read_bytes())
            after = output.stat()
            checksum_after = Path(f"{output}.sha256").stat()
            self.assertEqual(before.st_ino, after.st_ino)
            self.assertEqual(before.st_mtime_ns, after.st_mtime_ns)
            self.assertEqual(checksum_before.st_ino, checksum_after.st_ino)
            self.assertEqual(checksum_before.st_mtime_ns, checksum_after.st_mtime_ns)

    def test_logical_row_change_with_current_checksum_is_stale(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "doctrine-index.sqlite3"
            built = self.build_index(output)
            self.assertEqual(0, built.returncode, built.stderr)

            with sqlite3.connect(output) as database:
                database.execute(
                    "UPDATE concepts SET concept_json = '{}' "
                    "WHERE concept_id = 'universal-repository-contract-precedence'"
                )
                database.commit()
            self.rewrite_checksum(output)
            mutated_bytes = output.read_bytes()

            stale = self.build_index(output, "--check")

            self.assertEqual(1, stale.returncode)
            self.assertIn("missing or stale", stale.stderr)
            self.assertEqual(mutated_bytes, output.read_bytes())

    def test_check_reports_current_missing_and_stale_without_mutating_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "doctrine-index.sqlite3"
            missing = self.build_index(output, "--check")
            self.assertEqual(1, missing.returncode)
            self.assertFalse(output.exists())
            self.assertFalse(Path(f"{output}.sha256").exists())

            built = self.build_index(output)
            self.assertEqual(0, built.returncode, built.stderr)
            current = self.build_index(output, "--check")
            self.assertEqual(0, current.returncode, current.stderr)
            self.assertIn("doctrine index: current", current.stdout)

            output.write_bytes(output.read_bytes() + b"stale")
            stale_bytes = output.read_bytes()
            stale = self.build_index(output, "--check")

            self.assertEqual(1, stale.returncode)
            self.assertIn("missing or stale", stale.stderr)
            self.assertEqual(stale_bytes, output.read_bytes())

            output.write_bytes(output.read_bytes()[:-5])
            Path(f"{output}.sha256").write_text("0" * 64 + "\n", encoding="ascii")
            stale_checksum = self.build_index(output, "--check")
            self.assertEqual(1, stale_checksum.returncode)
            self.assertIn("missing or stale", stale_checksum.stderr)


if __name__ == "__main__":
    unittest.main()
