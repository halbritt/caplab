import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONVERT_BOOKS = REPOSITORY_ROOT / "scripts" / "convert-books"
CATALOG_BEGIN = "<!-- BEGIN GENERATED SOURCE CATALOG -->"
CATALOG_END = "<!-- END GENERATED SOURCE CATALOG -->"


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def write_catalog_fixture(root: Path) -> tuple[Path, Path]:
    source = root / "sources" / "Fixture Book.pdf"
    source.parent.mkdir()
    source.write_bytes(b"%PDF fixture")

    slug = "fixture-book"
    book = root / "books" / slug
    chapter = book / "chapters" / "001-evidence.md"
    chapter.parent.mkdir(parents=True)
    chapter.write_text("# Legacy Extracted Title\n\nEvidence.\n", encoding="utf-8")

    metadata = {
        "schema_version": "books-corpus/1",
        "title": "Legacy Extracted Title",
        "authors": ["Misclassified Person"],
        "metadata_selection": {"title_source": "converted content"},
    }
    validation = {
        "schema_version": "books-corpus/1",
        "conversion_success": True,
        "converter_exit_status": 0,
        "chapter_count": 1,
        "errors": [],
        "warnings": [
            "warning one",
            "warning two",
            "warning three",
            "warning four",
            "warning five",
        ],
        "malformed_markdown": [],
        "broken_links": [],
        "missing_assets": [],
        "missing_chapters": [],
        "missing_sections": [],
        "missing_parts": [],
        "empty_chapters": [],
        "damaged_code": [
            {
                "file": "chapters/001-evidence.md",
                "line": 3,
                "reason": "probable conversion damage",
            }
        ],
        "unresolved_tables": [
            {
                "file": "chapters/001-evidence.md",
                "line": line,
                "reasons": ["empty table cell"],
            }
            for line in (5, 8)
        ],
        "duplicate_headings": {"entries": []},
        "low_confidence_chapter_boundaries": [
            {"title": "Fixture", "confidence": "medium"}
        ],
        "unresolved_navigation_anchors": [],
        "degraded_internal_links": [],
        "source_section_warnings": ["uncited source section warning"],
        "converter_reported_failures": [],
        "page_furniture_removed": [{"file": "chapters/001-evidence.md", "line": 1}],
    }
    write_json(book / "metadata.json", metadata)
    write_json(book / "validation.json", validation)

    generated_files = {
        path.relative_to(book).as_posix(): sha256_bytes(path.read_bytes())
        for path in sorted(book.rglob("*"))
        if path.is_file()
    }
    source_record = {
        "schema_version": "books-corpus/1",
        "source_path": "sources/Fixture Book.pdf",
        "source_filename": source.name,
        "source_sha256": sha256_bytes(source.read_bytes()),
        "source_format": "pdf",
        "source_size_bytes": source.stat().st_size,
        "pipeline": "scripts/convert-books",
        "pipeline_fingerprint": "legacy-pipeline",
        "converter": "marker",
        "execution_target": "peecee",
        "generated_files": generated_files,
        "generated_directories": ["chapters"],
        "record_sha256": None,
    }
    source_record["record_sha256"] = sha256_bytes(json_bytes(source_record))
    write_json(book / "source.json", source_record)

    evidence = "books/fixture-book/chapters/001-evidence.md"
    bibliography = {
        "schema_version": "books-bibliography/1",
        "metadata_policy": {
            "canonical_catalog": "this-manifest",
            "generated_book_metadata": "legacy-extracted-noncanonical",
        },
        "books": [
            {
                "source_id": "SRC-FIXTURE",
                "source_path": "sources/Fixture Book.pdf",
                "slug": slug,
                "title": "Canonical Fixture Book",
                "title_evidence": [evidence],
                "edition": {
                    "label": "Second edition",
                    "number": 2,
                    "support": "direct",
                    "evidence": [evidence],
                },
                "creators": [
                    {
                        "name": "Ada Author",
                        "role": "author",
                        "support": "direct",
                        "evidence": [evidence],
                    },
                    {
                        "name": "Casey Contributor",
                        "role": "contributor",
                        "support": "direct",
                        "evidence": [evidence],
                    },
                ],
                "generated_metadata_status": "legacy-extracted-noncanonical",
            }
        ],
    }
    write_json(root / "doctrine" / "bibliography.json", bibliography)
    (root / "doctrine" / "chapter-coverage.yaml").write_text(
        textwrap.dedent(
            """\
            schema_version: agent-doctrine-chapter-coverage/1
            chapters:
              - source_id: SRC-FIXTURE
                chapter_path: books/fixture-book/chapters/001-evidence.md
            """
        ),
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# Fixture repository\n\n"
        "## Source books\n\n"
        f"{CATALOG_BEGIN}\nStale catalog.\n{CATALOG_END}\n",
        encoding="utf-8",
    )

    converter_sentinel = root / "converter-was-invoked"
    converter = root / "must-not-run-marker"
    converter.write_text(
        f"#!/bin/sh\ntouch '{converter_sentinel}'\nexit 97\n",
        encoding="utf-8",
    )
    converter.chmod(converter.stat().st_mode | stat.S_IXUSR)
    return converter, converter_sentinel


def run_catalog(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    converter, _ = write_catalog_fixture(root)
    environment = os.environ.copy()
    environment["BOOKS_MARKER_PEECEE"] = str(converter)
    return subprocess.run(
        [
            sys.executable,
            str(CONVERT_BOOKS),
            "--root",
            str(root),
            *arguments,
        ],
        capture_output=True,
        text=True,
        env=environment,
    )


class CorpusCatalogContractTests(unittest.TestCase):
    def test_checked_in_bibliography_covers_sources_with_role_provenance(self) -> None:
        path = REPOSITORY_ROOT / "doctrine" / "bibliography.json"
        self.assertTrue(path.is_file())
        manifest = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "books-bibliography/1")
        self.assertEqual(
            manifest["metadata_policy"]["generated_book_metadata"],
            "legacy-extracted-noncanonical",
        )
        records = manifest["books"]
        source_registry = yaml.safe_load(
            (REPOSITORY_ROOT / "doctrine" / "sources.yaml").read_text(encoding="utf-8")
        )["sources"]
        self.assertEqual(
            {record["source_id"] for record in records},
            {record["id"] for record in source_registry},
        )
        self.assertEqual(
            {record["source_path"] for record in records},
            {
                path.relative_to(REPOSITORY_ROOT).as_posix()
                for path in (REPOSITORY_ROOT / "sources").iterdir()
                if path.suffix.lower() in {".pdf", ".epub"}
            },
        )
        for record in records:
            with self.subTest(source=record["source_path"]):
                self.assertTrue(record["title"].strip())
                self.assertTrue(record["title_evidence"])
                self.assertTrue(record["edition"]["label"].strip())
                self.assertIn(
                    record["edition"]["support"], {"direct", "derived-inference"}
                )
                self.assertTrue(record["edition"]["evidence"])
                self.assertTrue(record["creators"])
                self.assertIn(
                    "author", {creator["role"] for creator in record["creators"]}
                )
                for creator in record["creators"]:
                    self.assertTrue(creator["evidence"])
                self.assertEqual(
                    record["generated_metadata_status"],
                    "legacy-extracted-noncanonical",
                )

    def test_catalog_only_uses_canonical_metadata_and_exposes_quality_states(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            result = run_catalog(root, "--catalog-only")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("catalogs updated", result.stdout)
            self.assertFalse((root / "converter-was-invoked").exists())

            index = (root / "books" / "README.md").read_text(encoding="utf-8")
            self.assertIn("Canonical Fixture Book", index)
            self.assertIn("Second edition", index)
            self.assertIn("Ada Author (author)", index)
            self.assertIn("Casey Contributor (contributor)", index)
            self.assertNotIn("Misclassified Person", index)
            self.assertIn("| yes | yes | review-required | not-recorded |", index)
            self.assertIn("errors=0; warnings=5; notices=1", index)
            self.assertIn("3 findings across 1 cited chapter", index)
            self.assertIn("warning one; warning two; warning three", index)
            self.assertIn("+2 more", index)
            self.assertIn(
                "[all warning evidence](./fixture-book/validation.json)", index
            )

            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("Canonical Fixture Book", readme)
            self.assertIn("Second edition", readme)
            self.assertIn("Ada Author (author)", readme)
            self.assertIn("Casey Contributor (contributor)", readme)
            self.assertIn("legacy extraction evidence and is noncanonical", readme)

    def test_check_rejects_a_stale_canonical_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = run_catalog(root, "--catalog-only")
            self.assertEqual(first.returncode, 0, first.stderr)
            manifest_path = root / "doctrine" / "bibliography.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["books"][0]["title"] = "Changed Canonical Title"
            write_json(manifest_path, manifest)

            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root), "--check"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("books/README.md is missing or stale", result.stderr)

    def test_check_rejects_a_manually_edited_root_source_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = run_catalog(root, "--catalog-only")
            self.assertEqual(first.returncode, 0, first.stderr)
            readme_path = root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "Canonical Fixture Book", "Hand-Edited Fixture Book"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root), "--check"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("README.md source catalog is stale", result.stderr)


if __name__ == "__main__":
    unittest.main()
