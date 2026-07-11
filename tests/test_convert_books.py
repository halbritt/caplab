import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONVERT_BOOKS = REPOSITORY_ROOT / "scripts" / "convert-books"


def source_path(root: Path, filename: str) -> Path:
    directory = root / "sources"
    directory.mkdir(exist_ok=True)
    return directory / filename


def write_source(root: Path, filename: str, content: bytes) -> Path:
    source = source_path(root, filename)
    source.write_bytes(content)
    return source


def write_counting_marker(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import os
            from pathlib import Path
            import sys

            counter = Path(os.environ["FAKE_MARKER_COUNT"])
            count = int(counter.read_text() if counter.exists() else "0") + 1
            counter.write_text(str(count))
            source = Path(sys.argv[1])
            output = Path(sys.argv[sys.argv.index("--out") + 1])
            raw = output / source.stem
            raw.mkdir(parents=True)
            (raw / f"{source.stem}.md").write_text(
                "# Fixture Book\\n\\nOpening.\\n\\n# Chapter 1. Stable\\n\\nText.\\n",
                encoding="utf-8",
            )
            (raw / f"{source.stem}_meta.json").write_text(
                json.dumps({
                    "page_stats": [{
                        "page_id": 0,
                        "text_extraction_method": "pdftext",
                        "block_metadata": {"llm_request_count": 0},
                    }],
                    "table_of_contents": [{"title": "Chapter 1. Stable", "page_id": 0}],
                }),
                encoding="utf-8",
            )
            print(raw / f"{source.stem}.md")
            """
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def write_marker_with_markdown(path: Path, markdown: str) -> None:
    encoded_markdown = repr(markdown)
    path.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import json
            from pathlib import Path
            import sys

            source = Path(sys.argv[1])
            output = Path(sys.argv[sys.argv.index("--out") + 1])
            raw = output / source.stem
            raw.mkdir(parents=True)
            (raw / f"{{source.stem}}.md").write_text({encoded_markdown}, encoding="utf-8")
            (raw / f"{{source.stem}}_meta.json").write_text(json.dumps({{
                "page_stats": [{{
                    "page_id": 0,
                    "text_extraction_method": "pdftext",
                    "block_metadata": {{"llm_request_count": 0}},
                }}],
                "table_of_contents": [],
            }}), encoding="utf-8")
            """
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def tree_snapshot(path: Path) -> dict[str, tuple[str, int]]:
    return {
        child.relative_to(path).as_posix(): (
            __import__("hashlib").sha256(child.read_bytes()).hexdigest(),
            child.stat().st_mtime_ns,
        )
        for child in path.rglob("*")
        if child.is_file()
    }


class ConvertBooksTests(unittest.TestCase):
    def test_missing_or_empty_sources_directory_reports_a_clear_error(self) -> None:
        cases = [
            (False, "sources/ is missing or is not a directory"),
            (True, "sources/ contains no direct PDF or EPUB files"),
        ]
        for create_directory, expected_error in cases:
            with self.subTest(create_directory=create_directory):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory)
                    if create_directory:
                        (root / "sources").mkdir()
                    result = subprocess.run(
                        [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(expected_error, result.stderr)

    def test_pdf_filename_supplies_explicit_title_and_author_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = write_source(
                root,
                "Domain Driven Design Tackling Complexity - Eric Evans.pdf",
                b"%PDF fixture",
            )
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Domain-Driven DISSIGN\n\n"
                "Tackling Complexity\n\nEric Evans\nForeword by Martin Fowler\n\n"
                "# Chapter 1: Knowledge\n\nBody.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads(
                (
                    root
                    / "books"
                    / "domain-driven-design-tackling-complexity-eric-evans"
                    / "metadata.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                metadata["title"], "Domain Driven Design Tackling Complexity"
            )
            self.assertEqual(metadata["authors"], ["Eric Evans"])
            self.assertEqual(
                metadata["metadata_selection"]["title_source"], "source filename"
            )
            validation = json.loads(
                (
                    root
                    / "books"
                    / "domain-driven-design-tackling-complexity-eric-evans"
                    / "validation.json"
                ).read_text(encoding="utf-8")
            )
            self.assertTrue(
                any(
                    "foreword" in warning.casefold()
                    for warning in validation["warnings"]
                )
            )

    def test_sources_pdf_becomes_a_structured_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = write_source(
                root, "Fixture  Engineering Book.pdf", b"%PDF-1.4\nfixture\n"
            )
            (root / "Ignored Root Book.pdf").write_bytes(b"%PDF-1.4\nroot decoy\n")
            nested = root / "sources" / "incoming"
            nested.mkdir()
            (nested / "Nested Book.pdf").write_bytes(b"%PDF-1.4\nnested\n")

            converter = root / "fake-marker"
            converter.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    from pathlib import Path
                    import sys

                    source = Path(sys.argv[1])
                    output = Path(sys.argv[sys.argv.index("--out") + 1])
                    raw = output / source.stem
                    raw.mkdir(parents=True)
                    (raw / f"{source.stem}.md").write_text(
                        "### **Fixture Engineering Book**\\n\\n"
                        "by Ada Example\\n\\n"
                        "![](diagram.png)\\n\\n"
                        "# **Foreword**\\n\\nOpening words.\\n\\n"
                        "# **Chapter 1. A Real Chapter**\\n\\n"
                        "## **Section**\\n\\nText.\\n\\n"
                        "```python\\nvalue  =  1  # preserve spacing\\n```\\n\\n"
                        "# **References**\\n\\n[Example] A reference.\\n",
                        encoding="utf-8",
                    )
                    (raw / f"{source.stem}_meta.json").write_text(
                        json.dumps({
                            "debug_data_path": "debug",
                            "page_stats": [{
                                "page_id": 0,
                                "text_extraction_method": "pdftext",
                                "block_metadata": {
                                    "llm_request_count": 0,
                                    "llm_error_count": 0,
                                    "llm_tokens_used": 0,
                                },
                            }],
                            "table_of_contents": [
                                {"title": "Foreword", "page_id": 0, "heading_level": None},
                                {"title": "Chapter 1. A Real Chapter", "page_id": 0, "heading_level": None},
                                {"title": "References", "page_id": 0, "heading_level": None},
                            ],
                        }, indent=2),
                        encoding="utf-8",
                    )
                    (raw / "diagram.png").write_bytes(b"fixture image")
                    print(raw / f"{source.stem}.md")
                    """
                ),
                encoding="utf-8",
            )
            converter.chmod(converter.stat().st_mode | stat.S_IXUSR)

            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "marker-pdf 9.9-test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            corpus = root / "books" / "fixture-engineering-book"
            chapters = sorted((corpus / "chapters").glob("*.md"))
            self.assertEqual(
                [chapter.name for chapter in chapters],
                [
                    "001-fixture-engineering-book.md",
                    "002-foreword.md",
                    "003-chapter-1-a-real-chapter.md",
                    "004-references.md",
                ],
            )
            for chapter in chapters:
                h1_lines = re.findall(
                    r"(?m)^# .+$", chapter.read_text(encoding="utf-8")
                )
                self.assertEqual(len(h1_lines), 1, chapter)

            chapter_text = chapters[2].read_text(encoding="utf-8")
            self.assertIn(
                "```python\nvalue  =  1  # preserve spacing\n```", chapter_text
            )
            front_matter = chapters[0].read_text(encoding="utf-8")
            self.assertIn("![](../assets/diagram.png)", front_matter)
            self.assertEqual(
                (corpus / "assets" / "diagram.png").read_bytes(), b"fixture image"
            )

            metadata = json.loads(
                (corpus / "metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["title"], "Fixture Engineering Book")
            self.assertEqual(metadata["authors"], ["Ada Example"])

            provenance = json.loads(
                (corpus / "source.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                provenance["source_path"], source.relative_to(root).as_posix()
            )
            self.assertEqual(provenance["source_filename"], source.name)
            self.assertEqual(provenance["converter"], "marker")
            self.assertEqual(provenance["execution_target"], "peecee")
            self.assertEqual(provenance["converter_version"], "marker-pdf 9.9-test")
            self.assertIn(str(converter), provenance["command_executed"])

            validation = json.loads(
                (corpus / "validation.json").read_text(encoding="utf-8")
            )
            self.assertTrue(validation["conversion_success"])
            self.assertEqual(validation["broken_links"], [])
            self.assertEqual(validation["missing_assets"], [])
            self.assertEqual(validation["damaged_code"], [])
            self.assertFalse(validation["ocr_usage"]["used"])
            self.assertFalse((root / "books" / "ignored-root-book").exists())
            self.assertFalse((root / "books" / "nested-book").exists())
            self.assertTrue((root / "books" / "README.md").is_file())

    def test_long_source_name_uses_a_windows_safe_hash_qualified_stem(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = source_path(
                root,
                "Software Design Analysis and Architecture Patterns " * 3 + ".pdf"
            )
            source.write_bytes(b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Long Name Book\n\nOpening.\n\n# Chapter 1\n\nText.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            corpus = (
                root
                / "books"
                / re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-")
            )
            provenance = json.loads(
                (corpus / "source.json").read_text(encoding="utf-8")
            )
            staged_argument = next(
                argument
                for argument in provenance["command_argv"]
                if str(argument).endswith(".pdf")
            )
            staged_name = Path(staged_argument).name
            self.assertLessEqual(len(staged_name), 65)
            self.assertRegex(Path(staged_name).stem, r"-[0-9a-f]{12}$")

    def test_unchanged_input_is_a_true_no_op_and_manual_edits_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Fixture Book.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            counter = root / "marker-count"
            write_counting_marker(converter)
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "pipeline-v1",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                    "FAKE_MARKER_COUNT": str(counter),
                }
            )
            command = [sys.executable, str(CONVERT_BOOKS), "--root", str(root)]
            first = subprocess.run(
                command, capture_output=True, text=True, env=environment
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            before = tree_snapshot(root / "books")

            second = subprocess.run(
                command, capture_output=True, text=True, env=environment
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("up to date", second.stdout)
            self.assertEqual(counter.read_text(), "1")
            self.assertEqual(tree_snapshot(root / "books"), before)

            chapter = (
                root / "books" / "fixture-book" / "chapters" / "002-chapter-1-stable.md"
            )
            chapter.write_text(
                chapter.read_text(encoding="utf-8") + "Manual note.\n", encoding="utf-8"
            )
            refused = subprocess.run(
                command, capture_output=True, text=True, env=environment
            )
            self.assertEqual(refused.returncode, 1)
            self.assertIn(
                "refusing to start while generated outputs contain unexpected edits",
                refused.stderr,
            )
            self.assertTrue(
                chapter.read_text(encoding="utf-8").endswith("Manual note.\n")
            )
            self.assertEqual(counter.read_text(), "1")

    def test_pipeline_fingerprint_change_rebuilds_an_intact_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Fixture Book.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            counter = root / "marker-count"
            write_counting_marker(converter)
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "pipeline-v1",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                    "FAKE_MARKER_COUNT": str(counter),
                }
            )
            command = [sys.executable, str(CONVERT_BOOKS), "--root", str(root)]
            first = subprocess.run(
                command, capture_output=True, text=True, env=environment
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            environment["BOOKS_PIPELINE_FINGERPRINT"] = "pipeline-v2"
            second = subprocess.run(
                command, capture_output=True, text=True, env=environment
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")
            provenance = json.loads(
                (root / "books" / "fixture-book" / "source.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(provenance["pipeline_fingerprint"], "pipeline-v2")

    def test_remote_infrastructure_failure_uses_and_records_local_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Fixture Book.pdf", b"%PDF fixture")
            remote = root / "failing-remote"
            remote.write_text(
                "#!/bin/sh\necho 'ssh: connect to host peecee: Connection timed out' >&2\nexit 1\n",
                encoding="utf-8",
            )
            remote.chmod(remote.stat().st_mode | stat.S_IXUSR)
            local = root / "local-marker"
            counter = root / "local-count"
            write_counting_marker(local)
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(remote),
                    "BOOKS_MARKER_LOCAL": str(local),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                    "FAKE_MARKER_COUNT": str(counter),
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            provenance = json.loads(
                (root / "books" / "fixture-book" / "source.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(provenance["execution_target"], "local")
            self.assertEqual(len(provenance["attempts"]), 2)
            self.assertEqual(provenance["fallbacks_used"][0]["from"], "peecee")
            self.assertEqual(provenance["fallbacks_used"][0]["to"], "local")
            self.assertEqual(counter.read_text(), "1")

    def test_document_failure_does_not_trigger_local_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Fixture Book.pdf", b"%PDF fixture")
            remote = root / "failing-remote"
            remote.write_text(
                "#!/bin/sh\necho 'invalid document structure' >&2\nexit 1\n",
                encoding="utf-8",
            )
            remote.chmod(remote.stat().st_mode | stat.S_IXUSR)
            local = root / "local-marker"
            counter = root / "local-count"
            write_counting_marker(local)
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(remote),
                    "BOOKS_MARKER_LOCAL": str(local),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                    "FAKE_MARKER_COUNT": str(counter),
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Marker failed on peecee", result.stderr)
            self.assertFalse(counter.exists())

    def test_epub_uses_opf_navigation_and_pandoc_without_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = source_path(root, "Native Structure.epub")
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("mimetype", "application/epub+zip")
                archive.writestr(
                    "META-INF/container.xml",
                    """<?xml version="1.0"?>
                    <container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
                      <rootfiles><rootfile full-path="OEBPS/content.opf"
                        media-type="application/oebps-package+xml"/></rootfiles>
                    </container>""",
                )
                archive.writestr(
                    "OEBPS/content.opf",
                    """<?xml version="1.0"?>
                    <package xmlns="http://www.idpf.org/2007/opf"
                      xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0">
                      <metadata>
                        <dc:title>Native Fixture</dc:title>
                        <dc:creator>Ada Example</dc:creator>
                        <dc:language>en</dc:language>
                      </metadata>
                      <manifest>
                        <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
                        <item id="one" href="one.xhtml" media-type="application/xhtml+xml"/>
                        <item id="two" href="two.xhtml" media-type="application/xhtml+xml"/>
                      </manifest>
                      <spine><itemref idref="one"/><itemref idref="two"/></spine>
                    </package>""",
                )
                archive.writestr(
                    "OEBPS/nav.xhtml",
                    """<html xmlns="http://www.w3.org/1999/xhtml"
                      xmlns:epub="http://www.idpf.org/2007/ops"><body>
                      <nav epub:type="toc"><ol>
                        <li><a href="one.xhtml">Opening Concepts</a></li>
                        <li><a href="two.xhtml">Deep Practice</a></li>
                      </ol></nav></body></html>""",
                )
                archive.writestr(
                    "OEBPS/one.xhtml",
                    "<html><body><h1>Opening Concepts</h1></body></html>",
                )
                archive.writestr(
                    "OEBPS/two.xhtml",
                    "<html><body><h1>Deep Practice</h1></body></html>",
                )

            pandoc = root / "fake-pandoc"
            pandoc.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    from pathlib import Path
                    import sys

                    output = Path(next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--output=")))
                    media = Path(next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--extract-media=")))
                    output.parent.mkdir(parents=True, exist_ok=True)
                    media.joinpath("media").mkdir(parents=True, exist_ok=True)
                    media.joinpath("media", "cover.png").write_bytes(b"cover")
                    output.write_text(
                        "# Native Fixture\\n\\nFront matter.\\n\\n"
                        "# Opening Concepts\\n\\nFirst.\\n\\n![](assets/media/cover.png)\\n\\n"
                        "# Deep Practice\\n\\n## Detail\\n\\nSecond.\\n",
                        encoding="utf-8",
                    )
                    """
                ),
                encoding="utf-8",
            )
            pandoc.chmod(pandoc.stat().st_mode | stat.S_IXUSR)
            marker = root / "marker-must-not-run"
            marker.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
            marker.chmod(marker.stat().st_mode | stat.S_IXUSR)
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_PANDOC": str(pandoc),
                    "BOOKS_PANDOC_VERSION": "pandoc test",
                    "BOOKS_MARKER_PEECEE": str(marker),
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            corpus = root / "books" / "native-structure"
            self.assertEqual(
                [path.name for path in sorted((corpus / "chapters").glob("*.md"))],
                [
                    "001-native-fixture.md",
                    "002-opening-concepts.md",
                    "003-deep-practice.md",
                ],
            )
            metadata = json.loads(
                (corpus / "metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["title"], "Native Fixture")
            self.assertEqual(metadata["authors"], ["Ada Example"])
            navigation = metadata["source_document_metadata"]["navigation"]
            self.assertEqual(
                [entry["title"] for entry in navigation],
                ["Opening Concepts", "Deep Practice"],
            )
            provenance = json.loads(
                (corpus / "source.json").read_text(encoding="utf-8")
            )
            self.assertEqual(provenance["converter"], "pandoc")
            self.assertEqual(provenance["execution_target"], "local")
            self.assertEqual(
                (corpus / "assets" / "media" / "cover.png").read_bytes(), b"cover"
            )

    def test_ordered_numeric_headings_are_chapters_but_rogue_h1_is_not(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Numbered Book.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Numbered Book\n\nFront.\n\n"
                "# 1 Design\n\nOne.\n\n"
                "# 2 Boundaries\n\nTwo.\n\n"
                "# A Rogue Section\n\nStill chapter two.\n\n"
                "# 3 Testing\n\nThree.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "numbered-book" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [path.name for path in chapters],
                [
                    "001-numbered-book.md",
                    "002-1-design.md",
                    "003-2-boundaries.md",
                    "004-3-testing.md",
                ],
            )
            second = chapters[2].read_text(encoding="utf-8")
            self.assertIn("## A Rogue Section", second)
            self.assertEqual(len(re.findall(r"(?m)^# .+$", second)), 1)

    def test_epub2_ncx_anchors_split_plain_pandoc_output_and_rewrite_links(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = source_path(root, "Anchored Book.epub")
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("mimetype", "application/epub+zip")
                archive.writestr(
                    "META-INF/container.xml",
                    """<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
                    <rootfiles><rootfile full-path="OEBPS/content.opf"/></rootfiles></container>""",
                )
                archive.writestr(
                    "OEBPS/content.opf",
                    """<package xmlns="http://www.idpf.org/2007/opf"
                      xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
                      <metadata><dc:title>Anchored Book</dc:title></metadata>
                      <manifest>
                        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
                        <item id="cover" href="part0000.xhtml" media-type="application/xhtml+xml"/>
                        <item id="chapter" href="part0001.xhtml" media-type="application/xhtml+xml"/>
                      </manifest>
                      <spine toc="ncx"><itemref idref="cover"/><itemref idref="chapter"/></spine>
                    </package>""",
                )
                archive.writestr(
                    "OEBPS/toc.ncx",
                    """<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/">
                      <navMap>
                        <navPoint id="cover"><navLabel><text>Cover Page</text></navLabel>
                          <content src="part0000.xhtml"/></navPoint>
                        <navPoint id="chapter"><navLabel><text>1: Introduction</text></navLabel>
                          <content src="part0001.xhtml"/></navPoint>
                      </navMap></ncx>""",
                )
                archive.writestr(
                    "OEBPS/part0000.xhtml", "<html><body>Cover</body></html>"
                )
                archive.writestr(
                    "OEBPS/part0001.xhtml", "<html><body>Chapter</body></html>"
                )

            pandoc = root / "fake-pandoc"
            pandoc.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    from pathlib import Path
                    import sys

                    output = Path(next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--output=")))
                    media = Path(next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--extract-media=")))
                    media.mkdir(parents=True, exist_ok=True)
                    media.joinpath("cover.png").write_bytes(b"cover")
                    absolute_image = media.resolve() / "cover.png"
                    output.write_text(
                        '<span id="part0000.xhtml"></span>\\n\\n'
                        f'![]({absolute_image})\\n\\n'
                        '[Introduction](#part0001.xhtml)\\n\\n'
                        '<span id="part0001.xhtml"></span>\\n\\n'
                        'Styled plain-text title\\n\\nChapter text.\\n',
                        encoding="utf-8",
                    )
                    """
                ),
                encoding="utf-8",
            )
            pandoc.chmod(pandoc.stat().st_mode | stat.S_IXUSR)
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_PANDOC": str(pandoc),
                    "BOOKS_PANDOC_VERSION": "pandoc test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            corpus = root / "books" / "anchored-book"
            chapters = sorted((corpus / "chapters").glob("*.md"))
            self.assertEqual(
                [path.name for path in chapters],
                ["001-cover-page.md", "002-1-introduction.md"],
            )
            cover = chapters[0].read_text(encoding="utf-8")
            self.assertIn("![](../assets/cover.png)", cover)
            self.assertIn("[Introduction](002-1-introduction.md#part0001.xhtml)", cover)
            self.assertNotIn(".book-work", cover)
            validation = json.loads(
                (corpus / "validation.json").read_text(encoding="utf-8")
            )
            self.assertEqual(validation["broken_links"], [])
            self.assertEqual(validation["missing_assets"], [])

    def test_nested_shorter_fence_is_preserved_inside_longer_fence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Fence Book.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            nested_example = (
                "# Fence Book\n\nFront.\n\n# Chapter 1. Fences\n\n"
                "````markdown\n```python\n* x must stay an asterisk\n```\n````\n"
            )
            write_marker_with_markdown(converter, nested_example)
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapter = (
                root / "books" / "fence-book" / "chapters" / "002-chapter-1-fences.md"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "````markdown\n```python\n* x must stay an asterisk\n```\n````",
                chapter,
            )
            validation = json.loads(
                (root / "books" / "fence-book" / "validation.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(validation["damaged_code"], [])

    def test_pdf_toc_recovers_missing_chapter_labels_and_preserves_heading_anchors(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "TOC Book.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# TOC Book\n\n[First](#chapter-one)\n\n"
                "| Chapter 1: First Topic 3 |\n"
                "|  | Chapter 2: Second Topic<br>9 |\n"
                "| Chapter 3: Building<br>Python 3<br>15 |\n\n"
                '## <span id="chapter-one"></span>**First Topic With Detail**\n\nOne.\n\n'
                "## **Chapter 2**\n\n## Second Topic\n\nTwo.\n\n"
                "## **Building Python 3**\n\nThree.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted((root / "books" / "toc-book" / "chapters").glob("*.md"))
            self.assertEqual(
                [path.name for path in chapters],
                [
                    "001-toc-book.md",
                    "002-chapter-1-first-topic-with-detail.md",
                    "003-chapter-2-second-topic.md",
                    "004-chapter-3-building-python-3.md",
                ],
            )
            first_chapter = chapters[1].read_text(encoding="utf-8")
            self.assertIn('<span id="chapter-one"></span>', first_chapter)
            self.assertIn("# Chapter 1: First Topic With Detail", first_chapter)
            front = chapters[0].read_text(encoding="utf-8")
            self.assertIn(
                "[First](002-chapter-1-first-topic-with-detail.md#chapter-one)", front
            )

    def test_pdf_heading_toc_uses_linked_body_anchors_and_degrades_absent_pages(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Linked TOC.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Linked TOC\n\nTitle page.\n\n"
                "## Contents\n\n"
                "#### Chapter 1 [First Topic](#page-10-0)\n\n"
                "#### [Chapter](#page-20-0) 2 Second Topic\n\n"
                "#### Chapter 3 [Building Python 3](#page-30-0)\n\n"
                "## Foreword\n\nFront matter.\n\n"
                '# <span id="page-10-0"></span>1 FIRST TOPIC\n\n'
                "See the missing code [image](#page-999-0).\n\n"
                "## Discover Encoding\n\nDetails.\n\n"
                '# <span id="page-20-0"></span>2 A SECOND TOPIC WITH DETAIL\n\n'
                "See [Discover](file:///tmp/chapter.html#discover).\n\n"
                '# <span id="page-30-0"></span>3 BUILDING PYTHON 3\n\n'
                "Three.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted((root / "books" / "linked-toc" / "chapters").glob("*.md"))
            chapter_names = [path.name for path in chapters]
            self.assertIn("004-chapter-1-first-topic.md", chapter_names)
            self.assertIn("005-chapter-2-a-second-topic-with-detail.md", chapter_names)
            self.assertIn("006-chapter-3-building-python-3.md", chapter_names)
            first = chapters[chapter_names.index("004-chapter-1-first-topic.md")]
            first_text = first.read_text(encoding="utf-8")
            self.assertIn("missing code image.", first_text)
            self.assertNotIn("#page-999-0", first_text)
            second = chapters[
                chapter_names.index("005-chapter-2-a-second-topic-with-detail.md")
            ].read_text(encoding="utf-8")
            self.assertIn("004-chapter-1-first-topic.md#discover-encoding", second)
            self.assertNotIn("file:///", second)
            validation = json.loads(
                (root / "books" / "linked-toc" / "validation.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(validation["missing_chapters"], [])
            self.assertEqual(validation["broken_links"], [])
            self.assertEqual(len(validation["degraded_internal_links"]), 2)

    def test_linked_structural_headings_require_body_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Anchored Boundaries.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Anchored Boundaries\n\nTitle page.\n\n"
                '## <span id="page-1"></span>**[Preface](#toc-preface)**\n\n'
                "Opening.\n\n"
                "## **[Part I. Prologue](#page-10)**\n\n"
                "A linked contents summary, not a body boundary.\n\n"
                '# <span id="page-10"></span>Part I. Prologue\n\n'
                "Part body.\n\n"
                '## <span id="page-20"></span>**[Index](#toc-index)**\n\n'
                "Index body.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "anchored-boundaries" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [chapter.name for chapter in chapters],
                [
                    "001-anchored-boundaries.md",
                    "002-preface.md",
                    "003-part-i-prologue.md",
                    "004-index.md",
                ],
            )
            preface = chapters[1].read_text(encoding="utf-8")
            self.assertIn("Part I. Prologue", preface)
            self.assertIn("linked contents summary", preface)

    def test_level_three_named_front_and_back_matter_are_units(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Lower Boundaries.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Lower Boundaries\n\nCover.\n\n"
                "### Acknowledgments\n\nThanks.\n\n"
                "# Chapter 1: One\n\nOne.\n\n"
                "# Chapter 2: Two\n\nTwo.\n\n"
                "# Chapter 3: Three\n\nThree.\n\n"
                "# Index\n\nIndex entries.\n\n"
                "### About the Author\n\nBiography.\n\n"
                "### Colophon\n\nProduction notes.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "lower-boundaries" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [chapter.name for chapter in chapters],
                [
                    "001-lower-boundaries.md",
                    "002-acknowledgments.md",
                    "003-chapter-1-one.md",
                    "004-chapter-2-two.md",
                    "005-chapter-3-three.md",
                    "006-index.md",
                    "007-about-the-author.md",
                    "008-colophon.md",
                ],
            )

    def test_terminal_generated_page_navigation_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Navigation Tail.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            link_lines = "\n".join(
                f"- [{index}. Topic {index}](#page-{index})" for index in range(1, 13)
            )
            write_marker_with_markdown(
                converter,
                "# Navigation Tail\n\nBook body.\n\n"
                "# About the Author\n\nA real biography.\n\n"
                "# 1. [Preface](#page-1)\n\n"
                + link_lines
                + "\n\n# 2. [Chapter One](#page-2)\n\n"
                + link_lines
                + "\n\n# 3. [Index](#page-3)\n\n"
                + link_lines
                + "\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            corpus = root / "books" / "navigation-tail"
            chapters = sorted((corpus / "chapters").glob("*.md"))
            self.assertEqual(
                [chapter.name for chapter in chapters],
                ["001-navigation-tail.md", "002-about-the-author.md"],
            )
            about = chapters[-1].read_text(encoding="utf-8")
            self.assertIn("A real biography.", about)
            self.assertNotIn("Topic 12", about)
            validation = json.loads(
                (corpus / "validation.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(validation["page_furniture_removed"]), 1)

    def test_pdf_body_chapter_labels_recover_titles_without_a_printed_toc(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Body Labels.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Body Labels\n\nIntroduction.\n\n"
                "#### Chapter 1\n\n# First Topic\n\nOne.\n\n"
                "#### Chapter 2\n\n# Second Topic\n\nTwo.\n\n"
                "#### Chapter 3\n\n# Third Topic\n\nThree.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "body-labels" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [path.name for path in chapters],
                [
                    "001-body-labels.md",
                    "002-chapter-1-first-topic.md",
                    "003-chapter-2-second-topic.md",
                    "004-chapter-3-third-topic.md",
                ],
            )
            first = chapters[1].read_text(encoding="utf-8")
            self.assertEqual(first.count("First Topic"), 1)
            self.assertIn("# Chapter 1: First Topic", first)

    def test_pdf_word_numbered_chapter_headings_are_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Word Chapters.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Word Chapters\n\nOpening.\n\n"
                "# Chapter One. First Topic\n\n"
                "Use genericSortBasic[<type>]([]<type>) here.\n\n"
                "# Chapter Two. Second Topic\n\nTwo.\n\n"
                "# Chapter Three. Third Topic\n\nThree.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "word-chapters" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [path.name for path in chapters],
                [
                    "001-word-chapters.md",
                    "002-chapter-1-first-topic.md",
                    "003-chapter-2-second-topic.md",
                    "004-chapter-3-third-topic.md",
                ],
            )
            self.assertIn(
                "genericSortBasic[<type>]([]<type>)",
                chapters[1].read_text(encoding="utf-8"),
            )

    def test_pdf_numbered_contents_table_recovers_chapters_and_appendices(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Numbered Contents.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Contents\n\n"
                "|  | The World of Testing | ix |\n"
                "| 1. | First Topic | 3 |\n"
                "| 2. | Second Topic | 9 |\n"
                "| 3. | Third Topic | 15 |\n"
                "| A1. | Supporting Material | 21 |\n\n"
                "# The World of Testing\n\nFront matter.\n\n"
                "# First Topic\n\nOne.\n\n"
                "# Second Topic\n\nTwo.\n\n"
                "# Third Topic\n\nThree.\n\n"
                "# Supporting Material\n\nAppendix body.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "numbered-contents" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [path.name for path in chapters],
                [
                    "001-contents.md",
                    "002-the-world-of-testing.md",
                    "003-chapter-1-first-topic.md",
                    "004-chapter-2-second-topic.md",
                    "005-chapter-3-third-topic.md",
                    "006-appendix-a1-supporting-material.md",
                ],
            )
            validation = json.loads(
                (root / "books" / "numbered-contents" / "validation.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(validation["missing_chapters"], [])
            self.assertEqual(validation["missing_sections"], [])

    def test_appendix_chapter_question_headings_stay_inside_appendix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Assessment Book.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Table of Contents\n\n"
                "| 1. | Introduction | 3 |\n"
                "| 2. | Architectural Thinking | 9 |\n"
                "| 3. | Modularity | 15 |\n\n"
                "## Preface: Invalidating Axioms\n\nPreface body.\n\n"
                "## Introduction\n\nChapter one body.\n\n"
                "## Architectural Thinking\n\nChapter two body.\n\n"
                "## Modularity\n\nChapter three body.\n\n"
                '# <span id="page-20"></span>Self-Assessment Questions\n\n'
                '## <span id="page-21"></span>[Chapter 1:](#page-3) Introduction\n\n'
                "- Question one.\n\n"
                '## <span id="page-21-1"></span>[Chapter 2:](#page-9) Architectural Thinking\n\n'
                "- Question two.\n\n"
                '## <span id="page-22"></span>[Chapter 3:](#page-15) Modularity\n\n'
                "- Question three.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "assessment-book" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [chapter.name for chapter in chapters],
                [
                    "001-table-of-contents.md",
                    "002-preface-invalidating-axioms.md",
                    "003-chapter-1-introduction.md",
                    "004-chapter-2-architectural-thinking.md",
                    "005-chapter-3-modularity.md",
                    "006-self-assessment-questions.md",
                ],
            )
            appendix = chapters[-1].read_text(encoding="utf-8")
            self.assertIn("## Chapter 1: Introduction", appendix)
            self.assertIn("## Chapter 3: Modularity", appendix)

    def test_numbered_contents_parts_split_before_duplicate_chapter_titles(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Part Evidence.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Table of Contents\n\n"
                "| 1.<br>Introduction 1 |  |  |\n"
                "|  | Part I. Foundations | 5 |\n"
                "| 2.<br>Core Ideas | 7 |  |\n"
                "|  | Part II. Architecture Styles | 15 |\n"
                "| 3. | Architecture Styles | 17 |\n"
                "| 4. | Part III.<br>Techniques and Soft Skills<br>Leadership | 27 |\n\n"
                "# Introduction\n\nIntroduction body.\n\n"
                "# Part I\n\n"
                "## Foundations\n\n"
                "# Core Ideas\n\nCore body.\n\n"
                "# Part II\n\n"
                "## Architecture Styles\n\n"
                "# Architecture Styles\n\nStyles body.\n\n"
                "## Techniques and Soft Skills\n\n"
                "# Leadership\n\nLeadership body.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "part-evidence" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [chapter.name for chapter in chapters],
                [
                    "001-table-of-contents.md",
                    "002-chapter-1-introduction.md",
                    "003-part-i-foundations.md",
                    "004-chapter-2-core-ideas.md",
                    "005-part-ii-architecture-styles.md",
                    "006-chapter-3-architecture-styles.md",
                    "007-part-iii-techniques-and-soft-skills.md",
                    "008-chapter-4-leadership.md",
                ],
            )
            validation = json.loads(
                (root / "books" / "part-evidence" / "validation.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(validation["missing_parts"], [])
            self.assertEqual(len(validation["structural_dividers"]), 3)

    def test_pdf_merges_title_only_duplicate_boundary_into_following_unit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Glossary Book.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Glossary Book\n\nFront matter.\n\n"
                '# Glossary\n\n<span id="glossary"></span>\n\n'
                "# Glossary\n\nTerm\n: Definition.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "glossary-book" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [path.name for path in chapters],
                ["001-glossary-book.md", "002-glossary.md"],
            )
            glossary = chapters[1].read_text(encoding="utf-8")
            self.assertEqual(glossary.count("# Glossary"), 1)
            self.assertIn('<span id="glossary"></span>', glossary)
            validation = json.loads(
                (root / "books" / "glossary-book" / "validation.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(validation["empty_chapters"], [])
            self.assertEqual(validation["duplicate_headings"]["entries"], [])

    def test_pdf_does_not_hide_a_genuinely_empty_chapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Empty Chapter.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Empty Chapter\n\nFront.\n\n"
                "# Chapter 1\n\nOne.\n\n"
                '# Chapter 2\n\n<span id="page-2"></span><span id="page-2-0"></span>\n\n'
                "# Chapter 3\n\nThree.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty chapter files remain", result.stderr)

    def test_pdf_splits_common_front_matter_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root, "Front Matter.pdf", b"%PDF fixture")
            converter = root / "fake-marker"
            write_marker_with_markdown(
                converter,
                "# Preface\n\nPreface body.\n\n"
                "# Acknowledgments\n\nThanks.\n\n"
                "# Introduction\n\nIntroduction body.\n\n"
                "# Chapter 1\n\nChapter body.\n",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_MARKER_PEECEE": str(converter),
                    "BOOKS_MARKER_VERSION": "test",
                    "BOOKS_PIPELINE_FINGERPRINT": "test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [sys.executable, str(CONVERT_BOOKS), "--root", str(root)],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            chapters = sorted(
                (root / "books" / "front-matter" / "chapters").glob("*.md")
            )
            self.assertEqual(
                [path.name for path in chapters],
                [
                    "001-preface.md",
                    "002-acknowledgments.md",
                    "003-introduction.md",
                    "004-chapter-1.md",
                ],
            )


if __name__ == "__main__":
    unittest.main()
