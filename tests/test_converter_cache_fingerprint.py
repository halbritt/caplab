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
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONVERT_BOOKS = REPOSITORY_ROOT / "scripts" / "convert-books"


def write_source(root: Path) -> None:
    sources = root / "sources"
    sources.mkdir()
    (sources / "Fixture Book.pdf").write_bytes(b"%PDF fixture")


def write_marker(path: Path) -> None:
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
            generation = os.environ["FAKE_MARKER_GENERATION"]
            (raw / f"{source.stem}.md").write_text(
                "# Fixture Book\\n\\nOpening.\\n\\n"
                f"# Chapter 1. Cache Identity\\n\\n{generation}.\\n",
                encoding="utf-8",
            )
            (raw / f"{source.stem}_meta.json").write_text(
                json.dumps({
                    "page_stats": [{
                        "page_id": 0,
                        "text_extraction_method": "pdftext",
                        "block_metadata": {"llm_request_count": 0},
                    }],
                    "table_of_contents": [],
                }),
                encoding="utf-8",
            )
            """
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def write_epub_source(root: Path) -> None:
    sources = root / "sources"
    sources.mkdir()
    with zipfile.ZipFile(sources / "Fixture Book.epub", "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr(
            "META-INF/container.xml",
            """<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles><rootfile full-path="OEBPS/content.opf"/></rootfiles>
            </container>""",
        )
        archive.writestr(
            "OEBPS/content.opf",
            """<package xmlns="http://www.idpf.org/2007/opf"
              xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0">
              <metadata><dc:title>Fixture EPUB</dc:title></metadata>
              <manifest><item id="chapter" href="chapter.xhtml"
                media-type="application/xhtml+xml"/></manifest>
              <spine><itemref idref="chapter"/></spine>
            </package>""",
        )
        archive.writestr(
            "OEBPS/chapter.xhtml",
            "<html><body><h1>Chapter One</h1><p>Fixture.</p></body></html>",
        )


def write_pandoc(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import os
            from pathlib import Path
            import sys

            counter = Path(os.environ["FAKE_PANDOC_COUNT"])
            count = int(counter.read_text() if counter.exists() else "0") + 1
            counter.write_text(str(count))
            output = Path(
                next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--output="))
            )
            generation = os.environ["FAKE_PANDOC_GENERATION"]
            output.write_text(
                "# Fixture EPUB\\n\\nOpening.\\n\\n"
                f"# Chapter One\\n\\n{generation}.\\n",
                encoding="utf-8",
            )
            """
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def run_partial_conversion(
    root: Path,
    marker: Path,
    counter: Path,
    *,
    version: str | None,
    generation: str,
    pipeline_fingerprint: str = "pipeline-v1",
    environment_overrides: dict[str, str] | None = None,
    extra_arguments: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(
        {
            "BOOKS_MARKER_PEECEE": str(marker),
            "BOOKS_PIPELINE_FINGERPRINT": pipeline_fingerprint,
            "BOOKS_SKIP_REMOTE_CLEAN": "1",
            "FAKE_MARKER_COUNT": str(counter),
            "FAKE_MARKER_GENERATION": generation,
        }
    )
    if version is None:
        environment.pop("BOOKS_MARKER_VERSION", None)
    else:
        environment["BOOKS_MARKER_VERSION"] = version
    environment.update(environment_overrides or {})
    return subprocess.run(
        [
            sys.executable,
            str(CONVERT_BOOKS),
            "--root",
            str(root),
            "--book",
            "Fixture Book.pdf",
            *extra_arguments,
        ],
        capture_output=True,
        text=True,
        env=environment,
    )


def run_partial_epub_conversion(
    root: Path,
    pandoc: Path,
    counter: Path,
    *,
    version: str,
    generation: str,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(
        {
            "BOOKS_PANDOC": str(pandoc),
            "BOOKS_PANDOC_VERSION": version,
            "BOOKS_PIPELINE_FINGERPRINT": "pipeline-v1",
            "FAKE_PANDOC_COUNT": str(counter),
            "FAKE_PANDOC_GENERATION": generation,
        }
    )
    return subprocess.run(
        [
            sys.executable,
            str(CONVERT_BOOKS),
            "--root",
            str(root),
            "--book",
            "Fixture Book.epub",
        ],
        capture_output=True,
        text=True,
        env=environment,
    )


def source_record_checksum(record: dict[str, object]) -> str:
    candidate = dict(record)
    candidate["record_sha256"] = None
    serialized = (
        json.dumps(candidate, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


class ConverterCacheFingerprintTests(unittest.TestCase):
    def test_changed_converter_version_reconverts_partial_book(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            first = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="first"
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            second = run_partial_conversion(
                root, marker, counter, version="marker-v2", generation="second"
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")

            chapter = (
                root
                / "books"
                / "fixture-book"
                / "chapters"
                / "002-chapter-1-cache-identity.md"
            )
            self.assertIn("second.", chapter.read_text(encoding="utf-8"))
            provenance = json.loads(
                (root / "books" / "fixture-book" / "source.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(provenance["converter_version"], "marker-v2")

    def test_unchanged_fingerprint_reuses_validated_raw_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            first = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="original"
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            chapter = (
                root
                / "books"
                / "fixture-book"
                / "chapters"
                / "002-chapter-1-cache-identity.md"
            )
            chapter.write_text("# manually edited\n", encoding="utf-8")

            second = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="original",
                extra_arguments=("--force",),
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("reusing validated converter output", second.stdout)
            self.assertEqual(counter.read_text(), "1")
            self.assertIn("original.", chapter.read_text(encoding="utf-8"))

    def test_fresh_converter_bypasses_unchanged_raw_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            first = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="first"
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            second = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="second",
                extra_arguments=("--fresh-converter",),
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")
            chapter = (
                root
                / "books"
                / "fixture-book"
                / "chapters"
                / "002-chapter-1-cache-identity.md"
            )
            self.assertIn("second.", chapter.read_text(encoding="utf-8"))

    def test_changed_converter_helper_reconverts_partial_book(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            first = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="first"
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            marker.write_text(
                marker.read_text(encoding="utf-8") + "\n# changed helper semantics\n",
                encoding="utf-8",
            )

            second = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="second"
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")

    def test_changed_conversion_stage_reconverts_partial_book(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            first = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="first",
                pipeline_fingerprint="pipeline-v1",
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            second = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="second",
                pipeline_fingerprint="pipeline-v2",
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")
            provenance = json.loads(
                (root / "books" / "fixture-book" / "source.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(provenance["pipeline_fingerprint"], "pipeline-v2")

    def test_changed_execution_environment_reconverts_partial_book(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            first = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="first",
                environment_overrides={"HOME": str(root / "home-v1")},
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            second = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="second",
                environment_overrides={"HOME": str(root / "home-v2")},
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")

    def test_source_provenance_records_raw_conversion_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            conversion = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="first"
            )
            self.assertEqual(conversion.returncode, 0, conversion.stderr)
            provenance = json.loads(
                (root / "books" / "fixture-book" / "source.json").read_text(
                    encoding="utf-8"
                )
            )

            identity = provenance["raw_conversion_identity"]
            self.assertEqual(len(provenance["raw_conversion_fingerprint"]), 64)
            self.assertEqual(identity["converter"], "marker")
            self.assertEqual(identity["conversion_stage_fingerprint"], "pipeline-v1")
            self.assertEqual(identity["converter_versions"]["peecee"], "marker-v1")
            self.assertEqual(identity["options"]["format"], "markdown")
            self.assertEqual(
                identity["helpers"]["peecee"][0]["resolved_path"],
                str(marker.resolve()),
            )
            self.assertEqual(len(identity["helpers"]["peecee"][0]["sha256"]), 64)
            version_environment = identity["environment"]["variables"][
                "BOOKS_MARKER_VERSION"
            ]
            self.assertEqual(set(version_environment), {"sha256"})
            self.assertEqual(len(version_environment["sha256"]), 64)
            self.assertNotIn("marker-v1", json.dumps(identity["environment"]))

    def test_unknown_converter_version_is_not_cache_reusable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            first = run_partial_conversion(
                root, marker, counter, version=None, generation="original"
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            chapter = (
                root
                / "books"
                / "fixture-book"
                / "chapters"
                / "002-chapter-1-cache-identity.md"
            )
            chapter.write_text("# manually edited\n", encoding="utf-8")

            second = run_partial_conversion(
                root,
                marker,
                counter,
                version=None,
                generation="second",
                extra_arguments=("--force",),
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")
            self.assertNotIn("reusing validated converter output", second.stdout)

    def test_check_rejects_raw_fingerprint_that_does_not_match_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            conversion = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="first"
            )
            self.assertEqual(conversion.returncode, 0, conversion.stderr)
            source_record_path = root / "books" / "fixture-book" / "source.json"
            source_record = json.loads(source_record_path.read_text(encoding="utf-8"))
            source_record["raw_conversion_fingerprint"] = "0" * 64
            source_record["record_sha256"] = source_record_checksum(source_record)
            source_record_path.write_text(
                json.dumps(source_record, indent=2, ensure_ascii=False, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )

            check = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="first",
                extra_arguments=("--check",),
            )
            self.assertEqual(check.returncode, 1)
            self.assertIn(
                "raw conversion fingerprint does not match identity", check.stderr
            )

    def test_check_rejects_fresh_converter_bypass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            conversion = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="first"
            )
            self.assertEqual(conversion.returncode, 0, conversion.stderr)
            check = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="first",
                extra_arguments=("--check", "--fresh-converter"),
            )
            self.assertEqual(check.returncode, 1)
            self.assertIn(
                "--fresh-converter cannot be combined with --check", check.stderr
            )

    def test_changed_pandoc_version_reconverts_partial_epub(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_epub_source(root)
            pandoc = root / "fake-pandoc"
            counter = root / "pandoc-count"
            write_pandoc(pandoc)

            first = run_partial_epub_conversion(
                root, pandoc, counter, version="pandoc-v1", generation="first"
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            second = run_partial_epub_conversion(
                root, pandoc, counter, version="pandoc-v2", generation="second"
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")
            provenance = json.loads(
                (root / "books" / "fixture-book" / "source.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(provenance["converter"], "pandoc")
            self.assertEqual(provenance["converter_version"], "pandoc-v2")

    def test_legacy_record_passes_check_but_forces_fresh_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_source(root)
            marker = root / "fake-marker"
            counter = root / "marker-count"
            write_marker(marker)

            first = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="first"
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            source_record_path = root / "books" / "fixture-book" / "source.json"
            source_record = json.loads(source_record_path.read_text(encoding="utf-8"))
            source_record.pop("raw_conversion_identity")
            source_record.pop("raw_conversion_fingerprint")
            source_record["pipeline_fingerprint"] = "legacy-pipeline"
            source_record["record_sha256"] = source_record_checksum(source_record)
            source_record_path.write_text(
                json.dumps(source_record, indent=2, ensure_ascii=False, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )

            check = run_partial_conversion(
                root,
                marker,
                counter,
                version="marker-v1",
                generation="first",
                extra_arguments=("--check",),
            )
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn("legacy-unverified", check.stderr)

            second = run_partial_conversion(
                root, marker, counter, version="marker-v1", generation="second"
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(counter.read_text(), "2")
            self.assertNotIn("reusing validated converter output", second.stdout)
            upgraded = json.loads(source_record_path.read_text(encoding="utf-8"))
            self.assertIn("raw_conversion_identity", upgraded)
            self.assertIn("raw_conversion_fingerprint", upgraded)


if __name__ == "__main__":
    unittest.main()
