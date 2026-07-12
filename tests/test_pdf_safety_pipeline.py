import hashlib
import json
import os
from pathlib import Path
import runpy
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock
import zlib


ROOT = Path(__file__).resolve().parents[1]
CONVERT_BOOKS = ROOT / "scripts" / "convert-books"
PDF_CDR = runpy.run_path(str(ROOT / "scripts" / "pdf-cdr"))


def executable(path: Path, body: str) -> None:
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def write_raster_profile_pdf(
    path: Path,
    *,
    content: bytes = b"1 0 0 1 0 0 cm\n/Im1 Do\n",
    page_contents_object: int = 6,
    page_image_object: int = 4,
    extra_objects: tuple[bytes, ...] = (),
) -> None:
    encoded_content = zlib.compress(content).hex().encode("ascii") + b">"
    image_payload = b"00>"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R /Info 3 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [7 0 R] >>",
        b"<< /Producer (GPL Ghostscript 10.02.1) "
        b"/CreationDate (D:19700101000000Z00'00') >>",
        (
            b"<< /Length 5 0 R /Subtype /Image /Width 1 /Height 1 "
            b"/ColorSpace /DeviceRGB /BitsPerComponent 8 "
            b"/Filter [/ASCIIHexDecode /LZWDecode] >>\nstream\n"
            + image_payload
            + b"\nendstream"
        ),
        str(len(image_payload)).encode("ascii"),
        (
            b"<< /Length 8 0 R /Filter [/ASCIIHexDecode /FlateDecode] >>\n"
            b"stream\n"
            + encoded_content
            + b"\nendstream"
        ),
        (
            b"<< /Type /Page /Parent 2 0 R "
            + f"/Contents {page_contents_object} 0 R ".encode("ascii")
            + b"/MediaBox [0 0 1 1] /Resources << /XObject << "
            + f"/Im1 {page_image_object} 0 R".encode("ascii")
            + b" >> >> >>"
        ),
        str(len(encoded_content)).encode("ascii"),
        *extra_objects,
    ]
    body = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_number, object_body in enumerate(objects, 1):
        offsets.append(len(body))
        body.extend(f"{object_number} 0 obj\n".encode("ascii"))
        body.extend(object_body)
        body.extend(b"\nendobj\n")
    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    identifier = b"0123456789ABCDEF0123456789ABCDEF"
    body.extend(
        b"trailer\n<< /Size "
        + str(len(objects) + 1).encode("ascii")
        + b" /Root 1 0 R /ID [<"
        + identifier
        + b"><"
        + identifier
        + b">] >>\nstartxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )
    path.write_bytes(body)


class PdfSafetyPipelineTests(unittest.TestCase):
    def test_dangerous_source_is_disarmed_before_marker_with_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            sources = root / "sources"
            sources.mkdir()
            original = b"%PDF-1.4\noriginal active bytes /JS\n"
            source = sources / "Fixture.pdf"
            source.write_bytes(original)

            xray = root / "fake-xray"
            executable(
                xray,
                """\
                #!/usr/bin/env python3
                import hashlib, json
                from pathlib import Path
                import sys
                path = Path(sys.argv[1])
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                print(json.dumps({
                    "schema_version": "pdf-skills/1",
                    "skill": "pdf-safe-ingest",
                    "source": {"path": str(path), "sha256": digest, "bytes": path.stat().st_size},
                    "safety": {
                        "verdict": "DANGEROUS",
                        "custody_id": digest[:16] + "-DANGEROUS",
                        "active_content": {"/JS": {"count": 1, "severity": "danger"}},
                        "bomb": None,
                        "note": None,
                        "decompression": {"pages": 1, "ceilings": {}},
                        "action": "disarm",
                    },
                }))
                raise SystemExit(3)
                """,
            )

            derivative = b"%PDF-1.4\ninert raster derivative\n"
            cdr = root / "fake-cdr"
            executable(
                cdr,
                f"""\
                #!/usr/bin/env python3
                import hashlib, json
                from pathlib import Path
                import sys
                source, output = map(Path, sys.argv[1:3])
                body = {derivative!r}
                output.write_bytes(body)
                source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
                derivative_hash = hashlib.sha256(body).hexdigest()
                print(json.dumps({{
                    "schema_version": "books-pdf-cdr/1",
                    "source_sha256": source_hash,
                    "source_size_bytes": source.stat().st_size,
                    "sandbox": {{
                        "transport": "bwrap",
                        "network": "none",
                        "host_filesystem": "allowlisted runtime paths only",
                    }},
                    "selected": {{
                        "dpi": 150,
                        "compression": "LZW",
                        "derivative_sha256": derivative_hash,
                        "derivative_size_bytes": len(body),
                        "custody_id": derivative_hash[:16] + "-CLEAN",
                        "verdict": "CLEAN",
                    }},
                    "attempts": [],
                }}))
                """,
            )

            marker = root / "fake-marker"
            seen = root / "marker-seen"
            executable(
                marker,
                """\
                #!/usr/bin/env python3
                import json, os
                from pathlib import Path
                import sys
                source = Path(sys.argv[1])
                Path(os.environ["MARKER_SEEN"]).write_bytes(source.read_bytes())
                output = Path(sys.argv[sys.argv.index("--out") + 1])
                raw = output / source.stem
                raw.mkdir(parents=True)
                (raw / f"{source.stem}.md").write_text(
                    "# Fixture Book\\n\\nOpening.\\n\\n# Chapter 1. Safe\\n\\nText.\\n", encoding="utf-8"
                )
                (raw / f"{source.stem}_meta.json").write_text(json.dumps({
                    "page_stats": [{
                        "page_id": 0,
                        "text_extraction_method": "ocr",
                        "block_metadata": {"llm_request_count": 0},
                    }],
                    "table_of_contents": [],
                }), encoding="utf-8")
                print(raw / f"{source.stem}.md")
                """,
            )

            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_PDF_XRAY": str(xray),
                    "BOOKS_PDF_CDR": str(cdr),
                    "BOOKS_MARKER_PEECEE": str(marker),
                    "BOOKS_MARKER_VERSION": "marker-test",
                    "BOOKS_PIPELINE_FINGERPRINT": "safety-test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                    "MARKER_SEEN": str(seen),
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CONVERT_BOOKS),
                    "--root",
                    str(root),
                    "--book",
                    source.name,
                ],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(original, source.read_bytes())
            self.assertEqual(derivative, seen.read_bytes())

            book = root / "books" / "fixture"
            provenance = json.loads((book / "source.json").read_text(encoding="utf-8"))
            self.assertEqual(hashlib.sha256(original).hexdigest(), provenance["source_sha256"])
            self.assertEqual("DANGEROUS", provenance["input_safety"]["verdict"])
            self.assertEqual("none", provenance["input_safety"]["sandbox"]["network"])
            self.assertEqual(
                {
                    "PDF_SAFE_MAX_DECOMP_MIB": "800",
                    "PDF_SAFE_MAX_PAGES": "5000",
                    "PDF_SAFE_MAX_RATIO": "120",
                },
                provenance["input_safety"]["policy"],
            )
            self.assertIn(
                "--force", provenance["input_safety"]["xray_command"]["argv"]
            )
            self.assertEqual("sandboxed-raster-cdr", provenance["input_safety"]["marker_input"])
            self.assertEqual(
                hashlib.sha256(derivative).hexdigest(),
                provenance["input_safety"]["cdr"]["selected"]["derivative_sha256"],
            )
            self.assertIn("/cdr/", provenance["command_executed"])
            validation = json.loads((book / "validation.json").read_text(encoding="utf-8"))
            self.assertTrue(
                any(
                    "CDR-CLEAN sandboxed raster derivative" in warning
                    for warning in validation["warnings"]
                )
            )

    def test_clean_source_stays_original_and_suspect_source_is_disarmed(
        self,
    ) -> None:
        for verdict in ("CLEAN", "SUSPECT"):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                sources = root / "sources"
                sources.mkdir()
                original = f"%PDF-1.4\n{verdict} fixture\n".encode("ascii")
                source = sources / f"Fixture {verdict}.pdf"
                source.write_bytes(original)

                xray = root / "fake-xray"
                executable(
                    xray,
                    """\
                    #!/usr/bin/env python3
                    import hashlib, json
                    from pathlib import Path
                    import sys
                    path = Path(sys.argv[1])
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    verdict = __VERDICT__
                    print(json.dumps({
                        "schema_version": "pdf-skills/1",
                        "skill": "pdf-safe-ingest",
                        "source": {"path": str(path), "sha256": digest, "bytes": path.stat().st_size},
                        "safety": {
                            "verdict": verdict,
                            "custody_id": digest[:16] + "-" + verdict,
                            "active_content": {},
                            "bomb": None,
                            "note": None,
                            "decompression": {"pages": 1, "ceilings": {}},
                            "action": "proceed",
                        },
                    }))
                    """.replace("__VERDICT__", repr(verdict)),
                )

                derivative = b"%PDF-1.4\ninert raster derivative\n"
                cdr = root / "fake-cdr"
                cdr_sentinel = root / "cdr-ran"
                executable(
                    cdr,
                    f"""\
                    #!/usr/bin/env python3
                    import hashlib, json
                    from pathlib import Path
                    import sys
                    source, output = map(Path, sys.argv[1:3])
                    body = {derivative!r}
                    output.write_bytes(body)
                    Path({str(cdr_sentinel)!r}).touch()
                    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
                    derivative_hash = hashlib.sha256(body).hexdigest()
                    print(json.dumps({{
                        "schema_version": "books-pdf-cdr/1",
                        "source_sha256": source_hash,
                        "source_size_bytes": source.stat().st_size,
                        "sandbox": {{
                            "transport": "bwrap",
                            "network": "none",
                            "host_filesystem": "allowlisted",
                        }},
                        "selected": {{
                            "dpi": 150,
                            "compression": "LZW",
                            "derivative_sha256": derivative_hash,
                            "derivative_size_bytes": len(body),
                            "custody_id": derivative_hash[:16] + "-CDR-CLEAN",
                            "verdict": "CDR-CLEAN",
                        }},
                        "attempts": [],
                    }}))
                    """,
                )

                marker = root / "fake-marker"
                marker_seen = root / "marker-seen"
                executable(
                    marker,
                    """\
                    #!/usr/bin/env python3
                    import json, os
                    from pathlib import Path
                    import sys
                    source = Path(sys.argv[1])
                    Path(os.environ["MARKER_SEEN"]).write_bytes(source.read_bytes())
                    output = Path(sys.argv[sys.argv.index("--out") + 1])
                    raw = output / source.stem
                    raw.mkdir(parents=True)
                    (raw / f"{source.stem}.md").write_text(
                        "# Fixture Book\\n\\nOpening.\\n\\n# Chapter 1. Body\\n\\nText.\\n",
                        encoding="utf-8",
                    )
                    (raw / f"{source.stem}_meta.json").write_text(json.dumps({
                        "page_stats": [{
                            "page_id": 0,
                            "text_extraction_method": "pdftext",
                            "block_metadata": {"llm_request_count": 0},
                        }],
                        "table_of_contents": [],
                    }), encoding="utf-8")
                    print(raw / f"{source.stem}.md")
                    """,
                )

                environment = os.environ.copy()
                environment.update(
                    {
                        "BOOKS_PDF_XRAY": str(xray),
                        "BOOKS_PDF_CDR": str(cdr),
                        "BOOKS_MARKER_PEECEE": str(marker),
                        "BOOKS_MARKER_VERSION": "marker-test",
                        "BOOKS_PIPELINE_FINGERPRINT": "safety-test",
                        "BOOKS_SKIP_REMOTE_CLEAN": "1",
                        "MARKER_SEEN": str(marker_seen),
                    }
                )
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(CONVERT_BOOKS),
                        "--root",
                        str(root),
                        "--book",
                        source.name,
                    ],
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertEqual(original, source.read_bytes())
                expected_marker_input = original if verdict == "CLEAN" else derivative
                self.assertEqual(expected_marker_input, marker_seen.read_bytes())
                self.assertEqual(verdict == "SUSPECT", cdr_sentinel.exists())

                slug = f"fixture-{verdict.casefold()}"
                provenance = json.loads(
                    (root / "books" / slug / "source.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(verdict, provenance["input_safety"]["verdict"])
                self.assertEqual(
                    (
                        "original-source-bytes"
                        if verdict == "CLEAN"
                        else "sandboxed-raster-cdr"
                    ),
                    provenance["input_safety"]["marker_input"],
                )
                validation = json.loads(
                    (root / "books" / slug / "validation.json").read_text(
                        encoding="utf-8"
                    )
                )
                suspect_warnings = [
                    warning
                    for warning in validation["warnings"]
                    if "SUSPECT" in warning
                ]
                self.assertEqual(verdict == "SUSPECT", bool(suspect_warnings))

    def test_cdr_sandbox_mounts_only_runtime_source_and_output_paths(self) -> None:
        raster_command = PDF_CDR["raster_command"]
        source = Path("/private/source.pdf")
        candidate = Path("/private/output/candidate.pdf")
        with mock.patch.dict(
            os.environ,
            {
                "BOOKS_PDF_BWRAP": "/usr/bin/bwrap",
                "BOOKS_PDF_GS": "/usr/bin/gs",
            },
        ):
            command = raster_command(source, candidate, 150, "LZW")
        self.assertFalse(
            any(
                command[index : index + 3] == ["--ro-bind", "/", "/"]
                for index in range(len(command) - 2)
            )
        )
        self.assertIn("--unshare-all", command)
        self.assertIn("--clearenv", command)
        self.assertIn(str(source), command)
        self.assertIn("/input/source.pdf", command)
        self.assertIn(str(candidate.parent), command)
        self.assertIn("/output", command)
        self.assertIn("-sOutputFile=/output/candidate.pdf", command)

    def test_normalization_and_validation_use_separate_networkless_sandboxes(
        self,
    ) -> None:
        normalization_command = PDF_CDR["normalization_command"]
        validation_command = PDF_CDR["validation_sandbox_command"]
        source = Path("/private/candidate.pdf")
        encoded = Path("/private/output/candidate.ascii.pdf")
        with mock.patch.dict(
            os.environ,
            {
                "BOOKS_PDF_BWRAP": "/usr/bin/bwrap",
                "BOOKS_PDF_MUTOOL": "/usr/bin/mutool",
                "BOOKS_PDF_XRAY": str(ROOT / "scripts" / "pdf-cdr"),
            },
        ):
            normalization = normalization_command(
                source, encoded, "a" * 64, 150, "LZW"
            )
            validation = validation_command(source)
        self.assertNotEqual(normalization, validation)
        for command in (normalization, validation):
            self.assertIn("--unshare-all", command)
            self.assertIn("--clearenv", command)
            self.assertIn(str(source), command)
            self.assertFalse(
                any(
                    command[index : index + 3] == ["--ro-bind", "/", "/"]
                    for index in range(len(command) - 2)
                )
            )
        self.assertIn("--normalize-child", normalization)
        self.assertIn("--validate-child", validation)

    def test_cdr_acceptance_requires_clean_xray_and_local_syntax(self) -> None:
        accepted_verdict = PDF_CDR["accepted_derivative_verdict"]
        structure = {"accepted": True, "page_count": 1}
        clean = {
            "verdict": "CLEAN",
            "bomb": None,
            "note": None,
            "active_content": {},
            "decompression": {"pages": 1},
        }
        suspect = {
            "verdict": "SUSPECT",
            "bomb": None,
            "note": None,
            "active_content": {"/AA": {"count": 1}},
            "decompression": {"pages": 1},
        }
        self.assertEqual("CLEAN", accepted_verdict(clean, structure))
        self.assertEqual("CDR-CLEAN", accepted_verdict(suspect, structure))
        self.assertIsNone(accepted_verdict(clean, {"accepted": False}))
        self.assertIsNone(
            accepted_verdict(
                {**clean, "bomb": {"reason": "limit"}}, structure
            )
        )
        self.assertIsNone(accepted_verdict({**suspect, "note": "deep scan failed"}, structure))
        self.assertIsNone(
            accepted_verdict(
                {**suspect, "active_content": {"/Unknown": {"count": 1}}},
                structure,
            )
        )

    def test_structural_validation_rejects_object_streams_and_escaped_actions(
        self,
    ) -> None:
        structural_validation = PDF_CDR["structural_pdf_validation"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "unsafe.pdf"
            path.write_bytes(
                b"%PDF-1.4\n"
                b"1 0 obj << /Type /Catalog /Open#41ction 2 0 R >> endobj\n"
                b"2 0 obj << /Type /ObjStm /Length 1 >>\nstream\nX\nendstream\nendobj\n"
            )
            record = structural_validation(path)
        self.assertFalse(record["accepted"])
        self.assertIn("/OpenAction", record["active_content"])
        self.assertIn("/ObjStm", record["forbidden_structure"])

    def test_structural_validation_rejects_action_bearing_extra_objects(self) -> None:
        structural_validation = PDF_CDR["structural_pdf_validation"]
        extra_objects = (
            b"<< /Type /Outlines /First 10 0 R >>",
            b"<< /Title (open) /Parent 9 0 R /A 11 0 R >>",
            b"<< /Type /Action /S /GoToE "
            b"/F << /Type /Filespec /F (payload.pdf) >> /D [0 /Fit] >>",
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "action-bearing.pdf"
            write_raster_profile_pdf(path, extra_objects=extra_objects)
            record = structural_validation(path)
        self.assertFalse(record["accepted"])
        self.assertTrue(record["unexpected_objects"])

    def test_structural_validation_rejects_noncanonical_page_content(self) -> None:
        structural_validation = PDF_CDR["structural_pdf_validation"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "extra-content-operator.pdf"
            write_raster_profile_pdf(
                path,
                content=b"1 0 0 1 0 0 cm\n/Im1 Do\n0 0 m 1 1 l S\n",
            )
            record = structural_validation(path)
        self.assertFalse(record["accepted"])
        self.assertTrue(
            any("content" in finding for finding in record["malformed"]),
            record,
        )

    def test_structural_validation_rejects_swapped_page_stream_references(self) -> None:
        structural_validation = PDF_CDR["structural_pdf_validation"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "swapped-references.pdf"
            write_raster_profile_pdf(
                path,
                page_contents_object=4,
                page_image_object=6,
            )
            record = structural_validation(path)
        self.assertFalse(record["accepted"])
        self.assertTrue(
            any("references" in finding for finding in record["malformed"]),
            record,
        )

    def test_structural_validation_accepts_exact_raster_profile(self) -> None:
        structural_validation = PDF_CDR["structural_pdf_validation"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "canonical.pdf"
            write_raster_profile_pdf(path)
            record = structural_validation(path)
        self.assertTrue(record["accepted"], record)
        self.assertEqual(1, record["page_count"])
        self.assertEqual(2, record["stream_count"])

    def test_cdr_rejects_xray_record_for_another_derivative(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            derivative = directory / "derivative.pdf"
            derivative.write_bytes(b"%PDF-1.4\nderivative\n")
            xray = directory / "wrong-xray"
            executable(
                xray,
                """\
                #!/usr/bin/env python3
                import json
                print(json.dumps({
                    "source": {"sha256": "0" * 64, "bytes": 1},
                    "safety": {"verdict": "CLEAN", "bomb": None},
                }))
                """,
            )
            scan_derivative = PDF_CDR["scan_derivative"]
            disarm_error = PDF_CDR["DisarmError"]
            with mock.patch.dict(os.environ, {"BOOKS_PDF_XRAY": str(xray)}):
                with self.assertRaisesRegex(disarm_error, "identity mismatch"):
                    scan_derivative(derivative)

    def test_safety_failures_stop_before_marker_and_record_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            sources = root / "sources"
            sources.mkdir()
            source = sources / "Fixture.pdf"
            source.write_bytes(b"%PDF-1.4\nfixture\n")
            xray = root / "broken-xray"
            executable(xray, "#!/bin/sh\necho broken >&2\nexit 1\n")
            marker = root / "marker-must-not-run"
            sentinel = root / "marker-ran"
            executable(marker, f"#!/bin/sh\ntouch {sentinel}\nexit 99\n")
            environment = os.environ.copy()
            environment.update(
                {
                    "BOOKS_PDF_XRAY": str(xray),
                    "BOOKS_MARKER_PEECEE": str(marker),
                    "BOOKS_MARKER_VERSION": "marker-test",
                    "BOOKS_SKIP_REMOTE_CLEAN": "1",
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CONVERT_BOOKS),
                    "--root",
                    str(root),
                    "--book",
                    source.name,
                ],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("PDF airlock failed", result.stderr)
            self.assertFalse(sentinel.exists())
            failure_records = list(
                (root / ".book-work").glob("*/conversion-failure.json")
            )
            self.assertEqual(1, len(failure_records))
            failure = json.loads(failure_records[0].read_text(encoding="utf-8"))
            self.assertEqual("pdf-airlock", failure["converter"])
            self.assertEqual("pdf-airlock", failure["attempts"][0]["phase"])
            self.assertEqual(1, failure["attempts"][0]["exit_status"])
            self.assertIn("broken", failure["attempts"][0]["stderr"])
            self.assertIn("scripts/pdf-cdr", failure["attempts"][0]["command"])
            self.assertIn(str(xray), failure["attempts"][0]["stderr"])

            executable(
                xray,
                """\
                #!/usr/bin/env python3
                import hashlib, json
                from pathlib import Path
                import sys
                source = Path(sys.argv[1])
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                print(json.dumps({
                    "schema_version": "pdf-skills/1",
                    "skill": "pdf-safe-ingest",
                    "source": {
                        "path": str(source),
                        "sha256": digest,
                        "bytes": source.stat().st_size,
                    },
                    "safety": {
                        "verdict": "DANGEROUS",
                        "custody_id": digest[:16] + "-DANGEROUS",
                        "active_content": {"/JS": {"count": 1}},
                        "bomb": None,
                        "note": None,
                        "decompression": {"pages": 1, "ceilings": {}},
                        "action": "disarm",
                    },
                }))
                raise SystemExit(3)
                """,
            )
            cdr = root / "broken-cdr"
            executable(cdr, "#!/bin/sh\necho cdr-broken >&2\nexit 2\n")
            environment["BOOKS_PDF_CDR"] = str(cdr)
            result = subprocess.run(
                [
                    sys.executable,
                    str(CONVERT_BOOKS),
                    "--root",
                    str(root),
                    "--book",
                    source.name,
                ],
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("sandboxed PDF disarmament failed", result.stderr)
            self.assertFalse(sentinel.exists())
            failure = json.loads(failure_records[0].read_text(encoding="utf-8"))
            self.assertEqual("pdf-cdr", failure["converter"])
            self.assertEqual("pdf-cdr", failure["attempts"][0]["phase"])
            self.assertEqual(2, failure["attempts"][0]["exit_status"])
            self.assertIn("cdr-broken", failure["attempts"][0]["stderr"])
            self.assertEqual(str(cdr), failure["attempts"][0]["argv"][0])


if __name__ == "__main__":
    unittest.main()
