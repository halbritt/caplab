import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine"
PYTHON_ASSEMBLER = DOCTRINE / "tools" / "assemble_packet.py"
INDEX_BUILDER = DOCTRINE / "tools" / "build_doctrine_index.py"

FINGERPRINT_PATHS = (
    "authority-model.yaml",
    "change-types.yaml",
    "conflicts.yaml",
    "context-lenses.yaml",
    "evidence-taxonomy.yaml",
    "graph/edges.yaml",
    "graph/formulations.yaml",
    "graph/nodes.yaml",
    "negative-doctrine.yaml",
    "procedures.yaml",
    "routing-index.yaml",
    "runtime/evidence-packet.schema.json",
    "runtime/evidence-record.schema.json",
    "sources.yaml",
    "traceability.yaml",
)

BASE_REQUEST = (
    "--role",
    "coding-agent",
    "--task",
    "implementation",
    "--question",
    "Should the parser accept the new format?",
)

SUCCESS_CASES = (
    ("compact-json", (*BASE_REQUEST, "--render", "json")),
    ("compact-markdown", (*BASE_REQUEST, "--render", "markdown")),
    (
        "full-json",
        (*BASE_REQUEST, "--detail", "full", "--render", "json"),
    ),
    (
        "aliases-deduplicate-repeated-inputs",
        (
            "--role",
            "implementation-agent",
            "--task",
            "feature-implementation",
            "--question",
            "Should this Go public API preserve caller compatibility?",
            "--signal",
            "public API",
            "--signal",
            "public API",
            "--language",
            "Go",
            "--language",
            "Go",
            "--risk",
            "compatibility",
            "--render",
            "json",
        ),
    ),
    (
        "specialist-variant-and-lens",
        (
            "--role",
            "domain-design-agent",
            "--task",
            "architecture-assessment",
            "--task-variant",
            "legacy-integration",
            "--question",
            "Should the local model use an Anticorruption Layer?",
            "--signal",
            "legacy API",
            "--lens",
            "lens-monolith",
            "--render",
            "json",
        ),
    ),
    (
        "signal-activation",
        (
            "--role",
            "repository-assessment-agent",
            "--task",
            "repository-assessment",
            "--question",
            "Where is coordinated change pressure visible?",
            "--signal",
            "coordinated edits",
            "--render",
            "json",
        ),
    ),
    (
        "signal-exclusion",
        (
            "--role",
            "repository-assessment-agent",
            "--task",
            "repository-assessment",
            "--question",
            "Where is coordinated change pressure visible?",
            "--signal",
            "coordinated edits",
            "--signal",
            "generated or vendored organization",
            "--render",
            "json",
        ),
    ),
    (
        "python-language-route",
        (
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "Should this Python protocol remain structurally compatible?",
            "--language",
            "Python",
            "--render",
            "json",
        ),
    ),
    (
        "go-language-and-risk-route",
        (
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "Should a goroutine own this resource lifecycle?",
            "--language",
            "Go",
            "--risk",
            "resource-lifecycle",
            "--render",
            "json",
        ),
    ),
    (
        "budget-pruning",
        (*BASE_REQUEST, "--budget", "6000", "--render", "json"),
    ),
    (
        "explicit-empty-risk",
        (*BASE_REQUEST, "--risk", "", "--render", "json"),
    ),
    (
        "unicode-word-boundary",
        (
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "Should Ⅻinterface remain one word?",
            "--render",
            "json",
        ),
    ),
    (
        "unicode-lowercase-expansion",
        (
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "Should İNTERFACE remain distinct under Unicode lowercase rules?",
            "--render",
            "json",
        ),
    ),
    (
        "python-control-whitespace",
        (
            "--role",
            "architecture-agent",
            "--task",
            "architecture-assessment",
            "--question",
            "Should interface\u001cpressure affect the boundary?",
            "--render",
            "json",
        ),
    ),
)


class GoPacketAssemblerParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)
        cls.index_path = cls.temp_path / "doctrine-index.sqlite3"
        cls.parity_binary_path = cls.temp_path / "assemble-packet-parity"
        cls.production_binary_path = cls.temp_path / "assemble-packet-production"

        index_result = subprocess.run(
            [
                sys.executable,
                str(INDEX_BUILDER),
                "--out",
                str(cls.index_path),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if index_result.returncode != 0:
            raise AssertionError(index_result.stderr or index_result.stdout)

        oracle = cls.run_python(*BASE_REQUEST, "--render", "json")
        if oracle.returncode != 0:
            raise AssertionError(oracle.stderr)
        cls.oracle_retriever_version = json.loads(oracle.stdout)["retriever_version"]
        cls.production_retriever_version = "retriever-" + hashlib.sha256(
            b"books-1-go-packet-assembler-production-test"
        ).hexdigest()[:16]

        cls.build_go_binary(
            cls.parity_binary_path,
            cls.oracle_retriever_version,
        )
        cls.build_go_binary(
            cls.production_binary_path,
            cls.production_retriever_version,
        )
        cls.write_evidence_fixtures()

    @classmethod
    def build_go_binary(cls, output_path, retriever_version):
        environment = os.environ.copy()
        environment.update(
            {
                "CGO_ENABLED": "0",
                "GOFLAGS": "-mod=readonly",
                "GOPROXY": "off",
                "GOTOOLCHAIN": "local",
            }
        )
        build_result = subprocess.run(
            [
                "go",
                "build",
                "-trimpath",
                "-ldflags",
                f"-X main.retrieverVersion={retriever_version}",
                "-o",
                str(output_path),
                "./cmd/assemble-packet",
            ],
            cwd=DOCTRINE,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if build_result.returncode != 0:
            raise AssertionError(build_result.stderr or build_result.stdout)

    @classmethod
    def write_evidence_fixtures(cls):
        cls.evidence_a = cls.temp_path / "a-evidence.json"
        cls.evidence_z = cls.temp_path / "z-evidence.json"
        cls.invalid_evidence = cls.temp_path / "invalid-evidence.json"
        cls.unknown_evidence = cls.temp_path / "unknown-evidence.json"
        cls.duplicate_evidence = cls.temp_path / "duplicate-evidence.json"
        cls.malformed_evidence = cls.temp_path / "malformed-evidence.json"
        cls.mistyped_evidence = cls.temp_path / "mistyped-evidence.json"
        cls.trailing_evidence = cls.temp_path / "trailing-evidence.json"

        records = {
            cls.evidence_a: {
                "schema_version": "evidence-record/1",
                "id": "a-evidence",
                "evidence_class": "evidence-explicit-user-requirements",
                "summary": "Café <caller> & Δ requires retry classification.\u2028Next line.",
                "provenance": [
                    {
                        "locator": "requirements.md#failure-policy",
                        "method": "repository inspection",
                    }
                ],
                "satisfies": ["caller recovery needs"],
            },
            cls.evidence_z: {
                "schema_version": "evidence-record/1",
                "id": "z-evidence",
                "evidence_class": "evidence-tests",
                "summary": "The retry policy was exercised with Unicode input.",
                "provenance": [
                    {
                        "locator": "tests/retry-policy#unicode",
                        "method": "captured test result",
                    }
                ],
                "satisfies": ["caller recovery needs"],
            },
            cls.invalid_evidence: {
                "schema_version": "evidence-record/1",
                "id": "missing-provenance",
                "evidence_class": "evidence-tests",
                "summary": "This record lacks required provenance.",
            },
            cls.unknown_evidence: {
                "schema_version": "evidence-record/1",
                "id": "unknown-class",
                "evidence_class": "evidence-not-registered",
                "summary": "This class is structurally shaped but unregistered.",
                "provenance": [{"locator": "fixture:unknown-class"}],
            },
            cls.duplicate_evidence: {
                "schema_version": "evidence-record/1",
                "id": "a-evidence",
                "evidence_class": "evidence-tests",
                "summary": "This repeats an earlier evidence identifier.",
                "provenance": [{"locator": "fixture:duplicate-id"}],
            },
            cls.mistyped_evidence: {
                "schema_version": 1,
                "id": ["not", "a", "string"],
                "evidence_class": "evidence-tests",
                "summary": {"not": "a string"},
                "provenance": [{"locator": 17}],
            },
        }
        for path, record in records.items():
            path.write_text(
                json.dumps(record, ensure_ascii=False),
                encoding="utf-8",
            )
        cls.malformed_evidence.write_text("{not-json", encoding="utf-8")
        cls.trailing_evidence.write_text(
            json.dumps(records[cls.evidence_a]) + "\n{}\n",
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    @staticmethod
    def run_python(*arguments):
        return subprocess.run(
            [sys.executable, str(PYTHON_ASSEMBLER), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    @classmethod
    def run_go(cls, *arguments, production=False):
        binary = (
            cls.production_binary_path if production else cls.parity_binary_path
        )
        return subprocess.run(
            [
                str(binary),
                "--index",
                str(cls.index_path),
                *arguments,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_success_parity(self, arguments):
        oracle = self.run_python(*arguments)
        candidate = self.run_go(*arguments)
        self.assertEqual(0, oracle.returncode, oracle.stderr)
        self.assertEqual(0, candidate.returncode, candidate.stderr)
        self.assertEqual(oracle.stderr, candidate.stderr)
        self.assertEqual(oracle.stdout.encode(), candidate.stdout.encode())
        return json.loads(candidate.stdout) if "json" in arguments else None

    def assert_success_case_contract(self, name, packet):
        if packet is None:
            return
        if name == "compact-json":
            self.assertNotIn("audit_views", packet)
        elif name == "full-json":
            self.assertIn("audit_views", packet)
        elif name == "aliases-deduplicate-repeated-inputs":
            context = packet["retrieval_context"]
            self.assertEqual("implementation-agent", context["requested_role"])
            self.assertEqual("coding-agent", context["canonical_role"])
            self.assertEqual(["Go"], context["languages"])
            self.assertEqual(["public API"], context["signals"])
        elif name == "specialist-variant-and-lens":
            self.assertIn(
                "domain-anticorruption-layer",
                packet["activated_concepts"],
            )
            self.assertIn("lens-monolith", packet["activated_lenses"])
        elif name == "signal-activation":
            self.assertIn(
                "architecture-change-locality-cohesion",
                packet["activated_concepts"],
            )
        elif name == "signal-exclusion":
            self.assertNotIn(
                "architecture-change-locality-cohesion",
                packet["activated_concepts"],
            )
        elif name == "python-language-route":
            self.assertIn("lens-python", packet["activated_lenses"])
        elif name == "go-language-and-risk-route":
            self.assertIn("lens-go", packet["activated_lenses"])
        elif name == "budget-pruning":
            self.assertTrue(packet["budget_excluded"])

    def test_representative_success_matrix_is_byte_identical_to_python(self):
        for name, arguments in SUCCESS_CASES:
            with self.subTest(case=name):
                packet = self.assert_success_parity(arguments)
                self.assert_success_case_contract(name, packet)

    def test_every_canonical_role_task_pair_is_byte_identical_to_python(self):
        routing = yaml.safe_load(
            (DOCTRINE / "routing-index.yaml").read_text(encoding="utf-8")
        )
        roles = sorted(bundle["role"] for bundle in routing["role_bundles"])
        tasks = sorted(bundle["task"] for bundle in routing["task_bundles"])
        self.assertEqual(72, len(roles) * len(tasks))

        for role in roles:
            for task in tasks:
                with self.subTest(role=role, task=task):
                    self.assert_success_parity(
                        (
                            "--role",
                            role,
                            "--task",
                            task,
                            "--question",
                            "Canonical role and task parity check.",
                            "--render",
                            "json",
                        )
                    )

    def test_typed_evidence_order_and_unicode_are_byte_identical(self):
        arguments = (
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "How should caller failures be handled?",
            "--signal",
            "caller recovery needs",
            "--evidence",
            str(self.evidence_z),
            "--evidence",
            str(self.evidence_a),
            "--budget",
            "16000",
            "--render",
            "json",
        )

        packet = self.assert_success_parity(arguments)

        self.assertEqual(
            ["a-evidence", "z-evidence"],
            [record["id"] for record in packet["evidence_records"]],
        )
        self.assertIn("Café <caller> & Δ", packet["evidence_records"][0]["summary"])
        self.assertIn("\u2028", packet["evidence_records"][0]["summary"])
        obligation = next(
            record
            for record in packet["evidence_obligations"]
            if record["requirement"] == "caller recovery needs"
        )
        self.assertEqual("satisfied", obligation["status"])
        self.assertEqual(["a-evidence", "z-evidence"], obligation["evidence_ids"])

    def test_render_none_writes_byte_identical_output_files(self):
        python_output = self.temp_path / "python-packet.json"
        go_output = self.temp_path / "go-packet.json"
        arguments = (*BASE_REQUEST, "--render", "none")

        oracle = self.run_python(*arguments, "--out", str(python_output))
        candidate = self.run_go(*arguments, "--out", str(go_output))

        self.assertEqual(0, oracle.returncode, oracle.stderr)
        self.assertEqual(0, candidate.returncode, candidate.stderr)
        self.assertEqual("", oracle.stdout)
        self.assertEqual("", candidate.stdout)
        self.assertEqual(oracle.stderr, candidate.stderr)
        self.assertEqual(python_output.read_bytes(), go_output.read_bytes())

    def test_production_identity_changes_only_identity_fields_and_rehashes(self):
        arguments = (*BASE_REQUEST, "--render", "json")
        oracle_result = self.run_python(*arguments)
        production_result = self.run_go(*arguments, production=True)
        self.assertEqual(0, oracle_result.returncode, oracle_result.stderr)
        self.assertEqual(0, production_result.returncode, production_result.stderr)
        oracle = json.loads(oracle_result.stdout)
        production = json.loads(production_result.stdout)

        self.assertNotEqual(oracle["retriever_version"], production["retriever_version"])
        self.assertEqual(
            self.production_retriever_version,
            production["retriever_version"],
        )
        self.assertRegex(production["retriever_version"], r"^retriever-[0-9a-f]{16}$")

        identity_fields = {
            "retriever_version",
            "packet_content_sha256",
            "packet_id",
        }
        oracle_semantics = {
            key: value for key, value in oracle.items() if key not in identity_fields
        }
        production_semantics = {
            key: value
            for key, value in production.items()
            if key not in identity_fields
        }
        self.assertEqual(oracle_semantics, production_semantics)

        unhashed = dict(production)
        unhashed.pop("packet_id")
        unhashed.pop("packet_content_sha256")
        canonical = json.dumps(
            unhashed,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        self.assertEqual(digest, production["packet_content_sha256"])
        self.assertEqual(f"pkt-{digest[:16]}", production["packet_id"])

    def test_index_is_read_only_versioned_and_refuses_stale_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            doctrine_root = temp_path / "doctrine"
            for relative in FINGERPRINT_PATHS:
                source = DOCTRINE / relative
                destination = doctrine_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            shutil.copytree(DOCTRINE / "concepts", doctrine_root / "concepts")

            read_only_index = temp_path / "read-only.sqlite3"
            shutil.copyfile(self.index_path, read_only_index)
            shutil.copyfile(
                Path(f"{self.index_path}.sha256"),
                Path(f"{read_only_index}.sha256"),
            )
            read_only_index.chmod(0o444)
            valid = subprocess.run(
                [
                    str(self.production_binary_path),
                    "--index",
                    str(read_only_index),
                    "--doctrine-root",
                    str(doctrine_root),
                    *BASE_REQUEST,
                    "--render",
                    "json",
                ],
                cwd=temp_path,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, valid.returncode, valid.stderr)
            self.assertFalse(Path(f"{read_only_index}-wal").exists())
            self.assertFalse(Path(f"{read_only_index}-shm").exists())
            self.assertFalse(Path(f"{read_only_index}-journal").exists())

            routing = doctrine_root / "routing-index.yaml"
            routing.write_bytes(routing.read_bytes() + b"\n# stale fixture\n")
            stale = subprocess.run(
                [
                    str(self.production_binary_path),
                    "--index",
                    str(read_only_index),
                    "--doctrine-root",
                    str(doctrine_root),
                    *BASE_REQUEST,
                ],
                cwd=temp_path,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(1, stale.returncode)
            self.assertIn("stale doctrine index", stale.stderr)

            incompatible_index = temp_path / "incompatible.sqlite3"
            shutil.copyfile(self.index_path, incompatible_index)
            with sqlite3.connect(incompatible_index) as database:
                database.execute(
                    "UPDATE meta SET value = ? WHERE key = ?",
                    ("doctrine-index/999", "index_schema_version"),
                )
            Path(f"{incompatible_index}.sha256").write_text(
                hashlib.sha256(incompatible_index.read_bytes()).hexdigest() + "\n",
                encoding="ascii",
            )
            incompatible = subprocess.run(
                [
                    str(self.production_binary_path),
                    "--index",
                    str(incompatible_index),
                    "--doctrine-root",
                    str(DOCTRINE),
                    *BASE_REQUEST,
                ],
                cwd=temp_path,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(1, incompatible.returncode)
            self.assertIn("unsupported doctrine index schema", incompatible.stderr)

            corrupted_index = temp_path / "corrupted.sqlite3"
            shutil.copyfile(self.index_path, corrupted_index)
            shutil.copyfile(
                Path(f"{self.index_path}.sha256"),
                Path(f"{corrupted_index}.sha256"),
            )
            with sqlite3.connect(corrupted_index) as database:
                database.execute(
                    "UPDATE concepts SET concept_json = ? WHERE concept_id = "
                    "(SELECT concept_id FROM concepts ORDER BY concept_id LIMIT 1)",
                    ('{"id":"corrupted"}',),
                )
            corrupted = subprocess.run(
                [
                    str(self.production_binary_path),
                    "--index",
                    str(corrupted_index),
                    "--doctrine-root",
                    str(DOCTRINE),
                    *BASE_REQUEST,
                ],
                cwd=temp_path,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(1, corrupted.returncode)
            self.assertIn("content hash", corrupted.stderr)

            missing_checksum_index = temp_path / "missing-checksum.sqlite3"
            shutil.copyfile(self.index_path, missing_checksum_index)
            missing_checksum = subprocess.run(
                [
                    str(self.production_binary_path),
                    "--index",
                    str(missing_checksum_index),
                    "--doctrine-root",
                    str(DOCTRINE),
                    *BASE_REQUEST,
                ],
                cwd=temp_path,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(1, missing_checksum.returncode)
            self.assertIn("file hash", missing_checksum.stderr)

    def test_index_paths_with_uri_metacharacters_are_opened_literally(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            index = Path(temp_dir) / "doctrine?literal.sqlite3"
            built = subprocess.run(
                [sys.executable, str(INDEX_BUILDER), "--out", str(index)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            result = subprocess.run(
                [
                    str(self.production_binary_path),
                    "--index",
                    str(index),
                    "--doctrine-root",
                    str(DOCTRINE),
                    *BASE_REQUEST,
                    "--render",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)

    def test_help_is_successful_and_does_not_emit_flag_panics(self):
        result = subprocess.run(
            [str(self.production_binary_path), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("assemble-packet", result.stderr)
        self.assertIn("-doctrine-root", result.stderr)
        self.assertNotIn("panic", result.stderr)

    def test_invalid_cli_and_evidence_inputs_fail_with_contract_errors(self):
        failure_cases = (
            (
                "unknown-role",
                (
                    "--role",
                    "shipping-agent",
                    "--task",
                    "implementation",
                    "--question",
                    "q",
                ),
                1,
                "unknown role 'shipping-agent'",
            ),
            (
                "unknown-task",
                (
                    "--role",
                    "coding-agent",
                    "--task",
                    "shipping",
                    "--question",
                    "q",
                ),
                1,
                "unknown task 'shipping'",
            ),
            (
                "unknown-task-variant",
                (
                    "--role",
                    "coding-agent",
                    "--task",
                    "implementation",
                    "--task-variant",
                    "not-a-real-variant",
                    "--question",
                    "q",
                ),
                1,
                "unknown task variant(s)",
            ),
            (
                "unknown-lens",
                (
                    "--role",
                    "coding-agent",
                    "--task",
                    "implementation",
                    "--lens",
                    "lens-not-real",
                    "--question",
                    "q",
                ),
                1,
                "unknown lens(es)",
            ),
            (
                "disallowed-lens",
                (
                    "--role",
                    "repository-assessment-agent",
                    "--task",
                    "repository-assessment",
                    "--lens",
                    "lens-monolith",
                    "--question",
                    "q",
                ),
                1,
                "lens(es) not applicable",
            ),
            (
                "zero-budget",
                (*BASE_REQUEST, "--budget", "0"),
                1,
                "retrieval budget must be positive",
            ),
            (
                "below-core-budget",
                (*BASE_REQUEST, "--budget", "1"),
                1,
                "below mandatory core cost",
            ),
            (
                "budget-trailing-text",
                (*BASE_REQUEST, "--budget", "6000junk"),
                2,
                "invalid",
            ),
            (
                "budget-fraction",
                (*BASE_REQUEST, "--budget", "6000.5"),
                2,
                "invalid",
            ),
            (
                "empty-language",
                (*BASE_REQUEST, "--language", ""),
                1,
                "ERROR",
            ),
            (
                "empty-signal",
                (*BASE_REQUEST, "--signal", ""),
                1,
                "ERROR",
            ),
            (
                "missing-evidence-provenance",
                (*BASE_REQUEST, "--evidence", str(self.invalid_evidence)),
                1,
                "provenance",
            ),
            (
                "unknown-evidence-class",
                (*BASE_REQUEST, "--evidence", str(self.unknown_evidence)),
                1,
                "unknown evidence_class",
            ),
            (
                "duplicate-evidence-id",
                (
                    *BASE_REQUEST,
                    "--evidence",
                    str(self.evidence_a),
                    "--evidence",
                    str(self.duplicate_evidence),
                ),
                1,
                "duplicate evidence record ID",
            ),
            (
                "malformed-evidence-json",
                (*BASE_REQUEST, "--evidence", str(self.malformed_evidence)),
                1,
                "unable to read evidence record",
            ),
            (
                "mistyped-evidence-fields",
                (*BASE_REQUEST, "--evidence", str(self.mistyped_evidence)),
                1,
                "string",
            ),
            (
                "trailing-evidence-json",
                (*BASE_REQUEST, "--evidence", str(self.trailing_evidence)),
                1,
                "unable to read evidence record",
            ),
            (
                "missing-required-options",
                (),
                2,
                "required",
            ),
        )

        for name, arguments, expected_exit, expected_error in failure_cases:
            with self.subTest(case=name):
                oracle = self.run_python(*arguments)
                candidate = self.run_go(*arguments)
                self.assertEqual(expected_exit, oracle.returncode, oracle.stderr)
                self.assertEqual(expected_exit, candidate.returncode, candidate.stderr)
                self.assertEqual("", oracle.stdout)
                self.assertEqual("", candidate.stdout)
                self.assertIn(expected_error, oracle.stderr)
                self.assertIn(expected_error, candidate.stderr)


if __name__ == "__main__":
    unittest.main()
