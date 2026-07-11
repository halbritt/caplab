"""Behavioral tests for corpus and doctrine release invariants."""

import hashlib
import json
import copy
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "doctrine" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_doctrine  # noqa: E402


class LocatorIdentityTests(unittest.TestCase):
    def test_ambiguous_heading_requires_an_explicit_occurrence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            chapter = Path(temp_dir) / "chapter.md"
            chapter.write_text(
                "# Chapter\n\n## Repeated\n\nFirst.\n\n## Repeated\n\nSecond.\n",
                encoding="utf-8",
            )

            self.assertFalse(validate_doctrine.heading_exists(chapter, "Repeated"))
            self.assertTrue(
                validate_doctrine.heading_exists(chapter, "Repeated @@ occurrence=2")
            )


class SourceIdentityTests(unittest.TestCase):
    def test_registry_hash_and_generated_source_record_must_match_binary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            source = repository / "sources" / "book.pdf"
            source.parent.mkdir()
            source.write_bytes(b"original source")
            corpus = repository / "books" / "book"
            corpus.mkdir(parents=True)
            actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            (corpus / "source.json").write_text(
                json.dumps(
                    {
                        "source_path": "sources/book.pdf",
                        "source_sha256": actual_hash,
                        "source_format": "pdf",
                        "source_size_bytes": source.stat().st_size,
                    }
                ),
                encoding="utf-8",
            )
            registry_record = {
                "id": "SRC-TEST",
                "corpus_path": "books/book",
                "source_input_path": "sources/book.pdf",
                "source_sha256": "0" * 64,
                "source_format": "pdf",
            }
            result = validate_doctrine.Validation()

            validate_doctrine.validate_source_identity(
                result, registry_record, repository
            )

            self.assertTrue(
                any("binary sha256" in error for error in result.errors),
                result.errors,
            )
            self.assertTrue(
                any("source.json sha256" in error for error in result.errors),
                result.errors,
            )


class DoctrineConfidenceTests(unittest.TestCase):
    def test_universal_confidence_requires_two_independent_sources(self) -> None:
        concept = {
            "id": "universal-fixture",
            "confidence": "universal",
            "source_support": [
                {"source_id": "SRC-ONE"},
                {"source_id": "SRC-ONE"},
            ],
        }
        result = validate_doctrine.Validation()

        validate_doctrine.validate_concept_confidence(result, concept)

        self.assertEqual(
            [
                "concept universal-fixture: universal confidence requires support "
                "from at least two independent sources"
            ],
            result.errors,
        )


class ConflictRegistryTests(unittest.TestCase):
    def test_source_supported_position_cannot_have_empty_support(self) -> None:
        graph_schema = json.loads(
            (ROOT / "doctrine" / "schemas" / "graph.schema.json").read_text(
                encoding="utf-8"
            )
        )
        document = copy.deepcopy(
            validate_doctrine.load_yaml(ROOT / "doctrine" / "conflicts.yaml")
        )
        position = document["conflicts"][0]["positions"][0]
        position["source_support"] = []
        position["basis"]["kind"] = "source-supported"
        result = validate_doctrine.Validation()

        result.schema(
            document,
            validate_doctrine.ref_schema(graph_schema, "conflictDocument"),
            "doctrine/conflicts.yaml",
        )

        self.assertTrue(
            any("derived-inference" in error for error in result.errors),
            result.errors,
        )


class ChapterCoverageManifestTests(unittest.TestCase):
    def test_ledger_rows_become_exact_hashed_chapter_records(self) -> None:
        from build_chapter_coverage import parse_ledger

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            chapter = repository / "books" / "book" / "chapters" / "001.md"
            chapter.parent.mkdir(parents=True)
            chapter.write_text("# One\n", encoding="utf-8")
            ledger = repository / "ledger.md"
            ledger.write_text(
                "### TEST coverage (1/1 files)\n\n"
                "| Path | Converted title | Operational themes or disposition |\n"
                "|---|---|---|\n"
                "| `TEST_ROOT/chapters/001.md` | One | Substantive evidence. |\n",
                encoding="utf-8",
            )

            records = parse_ledger(
                ledger,
                repository,
                {"TEST": ("SRC-TEST", "books/book")},
            )

            self.assertEqual(
                [
                    {
                        "source_id": "SRC-TEST",
                        "chapter_path": "books/book/chapters/001.md",
                        "title": "One",
                        "disposition": "Substantive evidence.",
                        "sha256": hashlib.sha256(chapter.read_bytes()).hexdigest(),
                    }
                ],
                records,
            )

    def test_manifest_must_cover_the_exact_registered_chapter_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            chapters = repository / "books" / "book" / "chapters"
            chapters.mkdir(parents=True)
            first = chapters / "001.md"
            second = chapters / "002.md"
            first.write_text("# One\n", encoding="utf-8")
            second.write_text("# Two\n", encoding="utf-8")
            document = {
                "schema_version": "chapter-coverage/1",
                "chapters": [
                    {
                        "source_id": "SRC-TEST",
                        "chapter_path": "books/book/chapters/001.md",
                        "title": "One",
                        "disposition": "Substantive.",
                        "sha256": hashlib.sha256(first.read_bytes()).hexdigest(),
                    }
                ],
            }
            sources = {"SRC-TEST": {"corpus_path": "books/book"}}
            result = validate_doctrine.Validation()

            validate_doctrine.validate_chapter_coverage_records(
                result, document, sources, repository
            )

            self.assertIn(
                "chapter coverage missing filesystem chapters: books/book/chapters/002.md",
                result.errors,
            )


if __name__ == "__main__":
    unittest.main()
