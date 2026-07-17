"""Explicit integration gates for PostgreSQL and the authorized local P4 stores."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from caplab.runtime.adapters.memory import MemoryCopyStore, MemoryObjectStore
from caplab.runtime.adapters.postgres import PostgresMetadataStore, PostgresMigrator
from caplab.runtime.canonical import sha256_hex
from caplab.runtime.errors import OperationConflict
from caplab.runtime.migrations import discover_migrations
from caplab.runtime.models import RegistrationRequest
from caplab.runtime.registration import RegistrationService
from caplab.recovery.adapters.postgres import PostgresCustodyStore
from caplab.recovery.errors import DependencyRetained
from caplab.recovery.models import P5Authority, P5Identity, PurgeRequest
from caplab.recovery.service import PurgeService
from caplab.admission.adapters.postgres import PostgresAdmissionStore
from caplab.admission.models import GitRecord, SourceSet
from caplab.admission.service import AdmissionService

from tests.test_runtime import FIXTURES, ROOT, request


POSTGRES_DSN = os.environ.get("CAPLAB_TEST_POSTGRES_DSN")
LIVE_ENABLED = os.environ.get("CAPLAB_P4_LIVE") == "1"


@unittest.skipUnless(
    POSTGRES_DSN, "set CAPLAB_TEST_POSTGRES_DSN for PostgreSQL integration"
)
class PostgresRuntimeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import psycopg
        from psycopg import sql

        with psycopg.connect(POSTGRES_DSN, autocommit=True) as connection:
            database, data_directory = connection.execute(
                "SELECT current_database(), current_setting('data_directory')"
            ).fetchone()
            if (
                database != "caplab_ephemeral_test"
                or not Path(data_directory).resolve().is_relative_to(Path("/tmp"))
                or "pg_virtualenv." not in str(Path(data_directory).resolve())
            ):
                raise RuntimeError(
                    "PostgreSQL integration requires the caplab_ephemeral_test database "
                    "inside pg_virtualenv"
                )
            for role in (
                "caplab_owner",
                "caplab_writer",
                "caplab_reader",
                "caplab_verifier",
                "caplab_custodian",
            ):
                connection.execute(
                    f"""
                    DO $$ BEGIN
                        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{role}') THEN
                            CREATE ROLE {role} NOLOGIN;
                        END IF;
                    END $$
                    """
                )
            database = connection.execute("SELECT current_database()").fetchone()[0]
            connection.execute(
                sql.SQL("ALTER DATABASE {} OWNER TO caplab_owner").format(
                    sql.Identifier(database)
                )
            )
        cls.migrator = PostgresMigrator(
            POSTGRES_DSN,
            ROOT / "src/caplab/runtime/migrations",
            "a" * 40,
        )

    def test_migration_and_registration_are_repeatable(self) -> None:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: self.migrator.apply(), range(2)))
        self.assertEqual(
            sorted(item.filename for result in results for item in result),
            [
                "0001_runtime_core.sql",
                "0002_p5_recovery_custody.sql",
                "0003_study_admission.sql",
            ],
        )
        self.assertEqual(self.migrator.apply(), [])
        import psycopg

        with psycopg.connect(POSTGRES_DSN) as connection:
            privileges = connection.execute(
                """
                SELECT
                    has_table_privilege('caplab_writer', 'caplab_v0.schema_migrations', 'INSERT'),
                    has_table_privilege('caplab_writer', 'caplab_v0.schema_migrations', 'SELECT'),
                    has_table_privilege('caplab_reader', 'caplab_v0.registrations', 'INSERT'),
                    has_table_privilege('caplab_verifier', 'caplab_v0.registrations', 'INSERT'),
                    has_table_privilege('caplab_writer', 'caplab_v0.registrations', 'UPDATE'),
                    has_table_privilege('caplab_writer', 'caplab_v0.registrations', 'DELETE')
                """
            ).fetchone()
        self.assertEqual(privileges, (False, True, False, False, False, False))

        objects = MemoryObjectStore()
        copies = MemoryCopyStore()

        def connect_as_writer(conninfo: str, *, autocommit: bool = False):
            connection = psycopg.connect(POSTGRES_DSN, autocommit=True)
            connection.execute("SET ROLE caplab_writer")
            connection.autocommit = autocommit
            return connection

        service = RegistrationService(
            PostgresMetadataStore(POSTGRES_DSN, connect=connect_as_writer),
            objects,
            copies,
        )

        first = service.register(request(operation_id="op-postgres-0001"))
        replay = service.register(request(operation_id="op-postgres-0001"))

        with psycopg.connect(POSTGRES_DSN) as connection:
            event_types = [
                row[0]
                for row in connection.execute(
                    """
                    SELECT event_type FROM caplab_v0.operation_events
                    WHERE operation_id = 'op-postgres-0001'
                    ORDER BY event_id
                    """
                )
            ]
            audit_types = [
                row[0]
                for row in connection.execute(
                    """
                    SELECT event_type FROM caplab_v0.audit_events
                    WHERE operation_id = 'op-postgres-0001'
                    ORDER BY audit_id
                    """
                )
            ]

        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(
            event_types,
            ["requested", "object-verified", "local-copy-verified", "registered"],
        )
        self.assertEqual(audit_types, ["registration-completed"])
        self.assertTrue(service.reconcile(first.operation_id).ok)
        with self.assertRaises(OperationConflict):
            service.register(
                request(operation_id="op-postgres-0001", payload=b"changed")
            )

        fixture_path = FIXTURES / "synthetic-attempt.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        migrations = discover_migrations(ROOT / "src/caplab/runtime/migrations")
        provenance = {
            "runtime_commit": "a" * 40,
            "requirements_lock_sha256": sha256_hex(
                (ROOT / "src/caplab/runtime/requirements.lock").read_bytes()
            ),
            "fixture_sha256": sha256_hex(fixture_path.read_bytes()),
            "migrations": [
                {"filename": migration.filename, "sha256": migration.sha256}
                for migration in migrations
            ],
        }
        with_provenance = RegistrationRequest(
            operation_id="op-postgres-provenance-0001",
            campaign_id=fixture["campaign_id"],
            artifact_kind=fixture["artifact_kind"],
            media_type=fixture["media_type"],
            identity_layers=fixture["identity_layers"],
            payload=(FIXTURES / "synthetic-payload.json").read_bytes(),
            runtime_provenance=provenance,
        )
        service.register(with_provenance)
        self.assertTrue(
            service.reconcile(
                with_provenance.operation_id,
                expected_runtime_provenance=provenance,
            ).ok
        )

    def test_p5_guarded_purge_is_transactional_narrow_and_preserves_p4(self) -> None:
        self.migrator.apply()
        import psycopg

        def connect_as_writer(conninfo: str, *, autocommit: bool = False):
            connection = psycopg.connect(POSTGRES_DSN, autocommit=True)
            connection.execute("SET ROLE caplab_writer")
            connection.autocommit = autocommit
            return connection

        service = RegistrationService(
            PostgresMetadataStore(POSTGRES_DSN, connect=connect_as_writer),
            MemoryObjectStore(),
            MemoryCopyStore(),
        )
        p4 = service.register(request(operation_id="op-postgres-p4-control"))
        fixture_root = ROOT / "tests/fixtures/recovery"
        fixture = json.loads(
            (fixture_root / "synthetic-attempt.json").read_text(encoding="utf-8")
        )
        p5_request = RegistrationRequest(
            operation_id="op-postgres-p5-purge",
            campaign_id=fixture["campaign_id"],
            artifact_kind=fixture["artifact_kind"],
            media_type=fixture["media_type"],
            identity_layers=fixture["identity_layers"],
            payload=(fixture_root / "synthetic-payload.json").read_bytes(),
        )
        p5 = service.register(p5_request)
        p5_intent = p5_request.intent()

        def connect_as_custodian(conninfo: str):
            connection = psycopg.connect(POSTGRES_DSN, autocommit=True)
            connection.execute("SET ROLE caplab_custodian")
            connection.autocommit = False
            return connection

        custody = PostgresCustodyStore(POSTGRES_DSN, connect=connect_as_custodian)
        purge_request = PurgeRequest(
            custody_request_id="custody-postgres-p5-purge",
            operation_id=p5.operation_id,
            campaign_id=p5.campaign_id,
            request_sha256=p5.request_sha256,
            content_sha256=p5.content_sha256,
            manifest_sha256=p5.manifest_sha256,
            authorization_sha256="9" * 64,
            expires_at=datetime(2026, 7, 23, 23, 59, 59, tzinfo=UTC),
        )
        purge_service = PurgeService(
            P5Authority(
                identity=P5Identity.from_intent(p5_intent),
                authorization_sha256="9" * 64,
                expires_at=datetime(2026, 7, 23, 23, 59, 59, tzinfo=UTC),
            ),
            custody,
        )
        custody.request_purge(purge_request)
        custody.record_dependency(
            operation_id=p5.operation_id,
            dependency_kind="dataset",
            dependency_identity="dataset-p5-test",
            event_type="retained",
        )

        with self.assertRaisesRegex(DependencyRetained, "retained dependency"):
            purge_service.purge(
                purge_request,
                now=datetime(2026, 7, 16, tzinfo=UTC),
            )

        custody.record_dependency(
            operation_id=p5.operation_id,
            dependency_kind="dataset",
            dependency_identity="dataset-p5-test",
            event_type="released",
        )
        tombstone = purge_service.purge(
            purge_request,
            now=datetime(2026, 7, 16, tzinfo=UTC),
        )

        with psycopg.connect(POSTGRES_DSN) as connection:
            state = connection.execute(
                """
                SELECT
                    EXISTS (
                        SELECT 1 FROM caplab_v0.registrations
                        WHERE operation_id = %s
                    ),
                    EXISTS (
                        SELECT 1 FROM caplab_v0.registrations
                        WHERE operation_id = %s
                    ),
                    EXISTS (
                        SELECT 1 FROM caplab_v0.purge_tombstones
                        WHERE operation_id = %s
                    ),
                    has_table_privilege(
                        'caplab_custodian',
                        'caplab_v0.registrations',
                        'DELETE'
                    ),
                    has_table_privilege(
                        'caplab_writer',
                        'caplab_v0.registrations',
                        'DELETE'
                    ),
                    has_function_privilege(
                        'caplab_custodian',
                        'caplab_v0.purge_p5_operation(text)',
                        'EXECUTE'
                    )
                """,
                (p5.operation_id, p4.operation_id, p5.operation_id),
            ).fetchone()

        self.assertEqual(tombstone.operation_id, p5.operation_id)
        self.assertEqual(state, (False, True, True, False, False, True))

    def test_study_admission_freezes_normalized_links_and_is_idempotent(self) -> None:
        self.migrator.apply()
        import psycopg
        import tempfile

        class Reader:
            def __init__(self, payload: bytes) -> None:
                self.payload = payload

            def read(self, commit: str, path: str) -> bytes:
                return self.payload

        def connect_as_writer(conninfo: str):
            connection = psycopg.connect(POSTGRES_DSN, autocommit=True)
            connection.execute("SET ROLE caplab_writer")
            return connection

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"historical evidence\n"
            digest = hashlib.sha256(payload).hexdigest()
            (root / "evidence.txt").write_bytes(payload)
            manifest_bytes = f"{digest}  evidence.txt\n".encode()
            (root / "manifest.sha256").write_bytes(manifest_bytes)
            result = b"historical result\n"
            source = SourceSet(
                study_id="caplab-study-test",
                preservation_root=root,
                preservation_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                git_records=(
                    GitRecord(
                        "result-record",
                        "b" * 40,
                        "result.md",
                        hashlib.sha256(result).hexdigest(),
                    ),
                ),
                expected_preservation_records=1,
                expected_total_records=3,
                expected_attempts=0,
            )
            service = AdmissionService(
                PostgresAdmissionStore(POSTGRES_DSN, connect=connect_as_writer),
                MemoryObjectStore(),
                MemoryCopyStore(),
            )
            first = service.admit(source, git_reader=Reader(result))
            replay = service.admit(source, git_reader=Reader(result))

        with psycopg.connect(POSTGRES_DSN) as connection:
            counts = connection.execute(
                """
                SELECT
                    (SELECT count(*) FROM caplab_v0.study_registrations WHERE study_id = 'caplab-study-test'),
                    (SELECT count(*) FROM caplab_v0.study_evidence_records WHERE manifest_sha256 = %s),
                    (SELECT count(*) FROM caplab_v0.study_objects),
                    has_table_privilege('caplab_reader', 'caplab_v0.study_registrations', 'INSERT'),
                    has_table_privilege('caplab_verifier', 'caplab_v0.study_registrations', 'INSERT'),
                    has_table_privilege('caplab_writer', 'caplab_v0.study_registrations', 'UPDATE')
                """,
                (first.manifest_sha256,),
            ).fetchone()
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(counts, (1, 3, 3, False, False, False))
        self.assertTrue(service.verify(first.manifest_sha256).ok)


@unittest.skipUnless(
    LIVE_ENABLED, "set CAPLAB_P4_LIVE=1 only inside the authorized P4 campaign"
)
class AuthorizedLocalRoundTripTests(unittest.TestCase):
    operation_id = "op-caplab-p4-roundtrip-0001"

    @classmethod
    def setUpClass(cls) -> None:
        cls.python = Path(os.environ["CAPLAB_P4_PYTHON"])
        cls.config = Path(os.environ["CAPLAB_P4_CONFIG"])
        cls.output_root = Path(os.environ["CAPLAB_P4_OUTPUT_ROOT"])
        if (
            not cls.python.is_file()
            or not cls.config.is_file()
            or not cls.output_root.is_dir()
        ):
            raise RuntimeError("live P4 paths must exist before the integration gate")

    def command(
        self,
        role: str,
        command: str,
        *arguments: str,
        expected: int = 0,
    ) -> dict[str, object]:
        result = subprocess.run(
            [
                "sudo",
                "-n",
                "-u",
                role,
                "--",
                "/usr/bin/env",
                "-i",
                "PYTHONNOUSERSITE=1",
                str(self.python),
                "-m",
                "caplab.runtime",
                command,
                "--config",
                str(self.config),
                *arguments,
            ],
            check=False,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            result.returncode,
            expected,
            msg=f"{command} returned {result.returncode}: {result.stderr}",
        )
        output = result.stdout if expected == 0 else result.stderr
        document = json.loads(output)
        self.assertNotIn("secret", output.lower())
        self.assertNotIn("access_key", output.lower())
        return document

    def test_authorized_round_trip(self) -> None:
        fixture = FIXTURES / "synthetic-attempt.json"
        payload = FIXTURES / "synthetic-payload.json"
        conflicting_payload = FIXTURES / "synthetic-payload-conflict.json"
        common = (
            "--operation-id",
            self.operation_id,
            "--fixture",
            str(fixture),
            "--payload",
            str(payload),
        )
        first = self.command("caplab_writer", "register", *common)
        replay = self.command("caplab_writer", "register", *common)
        conflict = self.command(
            "caplab_writer",
            "register",
            "--operation-id",
            self.operation_id,
            "--fixture",
            str(fixture),
            "--payload",
            str(conflicting_payload),
            expected=2,
        )
        retrieved = self.output_root / "retrieved-synthetic-payload.json"
        read_receipt = self.command(
            "caplab_reader",
            "retrieve",
            "--operation-id",
            self.operation_id,
            "--output",
            str(retrieved),
        )
        verified = self.command(
            "caplab_verifier", "verify", "--operation-id", self.operation_id
        )
        reconciled = self.command(
            "caplab_verifier",
            "reconcile",
            "--operation-id",
            self.operation_id,
            "--fixture",
            str(fixture),
        )
        cleanup_path = self.output_root / "cleanup-plan.json"
        cleanup = self.command(
            "caplab_verifier",
            "cleanup-plan",
            "--operation-id",
            self.operation_id,
            "--output",
            str(cleanup_path),
        )

        expected_sha256 = hashlib.sha256(payload.read_bytes()).hexdigest()
        self.assertEqual(first["content_sha256"], expected_sha256)
        self.assertIs(first["idempotent_replay"], False)
        self.assertIs(replay["idempotent_replay"], True)
        self.assertEqual(conflict["error_type"], "OperationConflict")
        self.assertEqual(retrieved.read_bytes(), payload.read_bytes())
        self.assertEqual(read_receipt["content_sha256"], expected_sha256)
        self.assertEqual(verified["content_sha256"], expected_sha256)
        self.assertIs(reconciled["ok"], True)
        self.assertRegex(str(cleanup["plan_sha256"]), r"\A[0-9a-f]{64}\Z")
        cleanup_document = json.loads(cleanup_path.read_text(encoding="utf-8"))
        self.assertIs(cleanup_document["deletions_authorized"], False)
        self.assertEqual(cleanup_document["status"], "quarantine-required")


if __name__ == "__main__":
    unittest.main()
