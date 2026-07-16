"""Hermetic contracts for the CAPLAB P4 runtime."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from caplab.runtime.canonical import CanonicalizationError, canonical_json
from caplab.runtime.custody import build_cleanup_plan
from caplab.runtime.config import (
    ConfigurationError,
    RuntimeConfig,
    load_credentials,
    load_trusted_runtime_config,
)
from caplab.runtime.errors import (
    CopyMismatch,
    LocatorMismatch,
    ObjectMismatch,
    OperationConflict,
)
from caplab.runtime.migrations import ChecksumDrift, discover_migrations, pending_migrations
from caplab.runtime.models import RegistrationRequest
from caplab.runtime.registration import RegistrationService
from caplab.runtime.adapters.filesystem import FilesystemCopyStore
from caplab.runtime.adapters.s3 import S3ObjectStore
from caplab.runtime.adapters.memory import (
    MemoryCopyStore,
    MemoryMetadataStore,
    MemoryObjectStore,
)
from caplab.runtime.__main__ import (
    build_parser,
    load_registration_request,
    prepare_registration_request,
    run,
    write_exclusive,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/runtime"


def request(*, operation_id: str = "op-p4-0001", payload: bytes | None = None) -> RegistrationRequest:
    fixture = json.loads((FIXTURES / "synthetic-attempt.json").read_text(encoding="utf-8"))
    return RegistrationRequest(
        operation_id=operation_id,
        campaign_id=fixture["campaign_id"],
        artifact_kind=fixture["artifact_kind"],
        media_type=fixture["media_type"],
        identity_layers=fixture["identity_layers"],
        payload=payload if payload is not None else (FIXTURES / "synthetic-payload.json").read_bytes(),
    )


class CanonicalJsonTests(unittest.TestCase):
    def test_normalizes_unicode_and_preserves_non_ascii_utf8(self) -> None:
        composed = canonical_json({"label": "Caf\u00e9", "city": "Z\u00fcrich"})
        decomposed = canonical_json({"label": "Cafe\u0301", "city": "Zu\u0308rich"})

        self.assertEqual(composed, decomposed)
        self.assertIn("Caf\u00e9".encode(), composed)

    def test_rejects_ambiguous_normalized_keys_and_floats(self) -> None:
        with self.assertRaises(CanonicalizationError):
            canonical_json({"\u00e9": 1, "e\u0301": 2})
        with self.assertRaises(CanonicalizationError):
            canonical_json({"score": 0.2})


class RegistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = MemoryMetadataStore()
        self.objects = MemoryObjectStore()
        self.copies = MemoryCopyStore()
        self.service = RegistrationService(self.metadata, self.objects, self.copies)

    def test_round_trip_binds_distinct_identity_layers(self) -> None:
        receipt = self.service.register(request())
        retrieved = self.service.retrieve(receipt.operation_id)
        report = self.service.reconcile(receipt.operation_id)

        self.assertEqual(retrieved, request().payload)
        self.assertTrue(report.ok)
        self.assertEqual(set(receipt.identity_sha256), {
            "model",
            "agent_configuration",
            "administration",
            "trial_context",
            "trial_assignment",
            "attempt",
            "analysis",
        })
        self.assertEqual(len(set(receipt.identity_sha256.values())), 7)
        self.assertEqual(receipt.object_key, f"objects/sha256/{receipt.content_sha256[:2]}/{receipt.content_sha256}")
        self.assertFalse(receipt.idempotent_replay)

    def test_same_operation_replay_is_idempotent(self) -> None:
        first = self.service.register(request())
        writes = (self.objects.write_count, self.copies.write_count)
        second = self.service.register(request())

        self.assertEqual(first.content_sha256, second.content_sha256)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual((self.objects.write_count, self.copies.write_count), writes)

    def test_registration_emits_the_exact_inventory_event_contract_once(self) -> None:
        self.service.register(request())

        self.assertEqual(
            [event["event_type"] for event in self.metadata.events],
            ["requested", "object-verified", "local-copy-verified", "registered"],
        )
        self.assertEqual(
            [event["event_type"] for event in self.metadata.audit_events],
            ["registration-completed"],
        )

        self.service.register(request())

        self.assertEqual(len(self.metadata.events), 4)
        self.assertEqual(len(self.metadata.audit_events), 1)

    def test_conflicting_operation_is_refused_before_external_effects(self) -> None:
        self.service.register(request())
        object_effects = self.objects.effect_count
        copy_effects = self.copies.effect_count

        with self.assertRaises(OperationConflict):
            self.service.register(request(payload=b"different"))

        self.assertEqual(self.objects.effect_count, object_effects)
        self.assertEqual(self.copies.effect_count, copy_effects)

    def test_nonidentical_existing_object_fails_closed(self) -> None:
        intent = request().intent()
        self.objects.objects[intent.object_key] = b"wrong"

        with self.assertRaises(ObjectMismatch):
            self.service.register(request())

        self.assertIsNone(self.metadata.registration_for_operation("op-p4-0001"))

    def test_nonidentical_existing_copy_fails_closed(self) -> None:
        intent = request().intent()
        self.copies.copies[intent.object_key] = b"wrong"

        with self.assertRaises(CopyMismatch):
            self.service.register(request())

        self.assertIsNone(self.metadata.registration_for_operation("op-p4-0001"))

    def test_interrupted_finalization_is_retryable_without_rewriting_bytes(self) -> None:
        self.metadata.fail_finalization_once = True
        with self.assertRaisesRegex(RuntimeError, "injected finalization failure"):
            self.service.register(request())
        self.assertEqual((self.objects.write_count, self.copies.write_count), (1, 1))

        interrupted = self.service.reconcile("op-p4-0001")
        cleanup = self.service.cleanup_plan("op-p4-0001")
        self.assertEqual(interrupted.metadata_status, "incomplete")
        self.assertEqual(interrupted.object_status, "match")
        self.assertEqual(interrupted.local_copy_status, "match")
        self.assertFalse(interrupted.ok)
        self.assertEqual(cleanup["registration_status"], "incomplete")
        self.assertEqual(cleanup["retained"]["content_sha256"], request().intent().content_sha256)

        receipt = self.service.register(request())

        self.assertEqual((self.objects.write_count, self.copies.write_count), (1, 1))
        self.assertTrue(receipt.idempotent_replay)
        self.assertTrue(self.service.reconcile(receipt.operation_id).ok)

    def test_locator_substitution_is_detected(self) -> None:
        self.service.register(request())
        self.metadata.registrations["op-p4-0001"]["object_key"] = "objects/sha256/00/" + "0" * 64

        with self.assertRaises(LocatorMismatch):
            self.service.verify("op-p4-0001")

    def test_manifest_substitution_is_detected(self) -> None:
        self.service.register(request())
        self.metadata.registrations["op-p4-0001"]["manifest"]["campaign_id"] = "substituted"

        with self.assertRaisesRegex(RuntimeError, "manifest bytes differ"):
            self.service.verify("op-p4-0001")
        self.assertEqual(self.service.reconcile("op-p4-0001").metadata_status, "mismatch")

    def test_request_owns_nested_identity_values(self) -> None:
        mutable = {
            "model": {"values": ["original"]},
            "agent_configuration": {"value": "a"},
            "administration": {"value": "b"},
            "trial_context": {"value": "c"},
            "trial_assignment": {"value": "d"},
            "attempt": {"attempt": 1},
            "analysis": {"value": "e"},
        }
        owned = RegistrationRequest(
            operation_id="op-owned-001",
            campaign_id="campaign-owned",
            artifact_kind="sealed-attempt",
            media_type="application/json",
            identity_layers=mutable,
            payload=b"payload",
        )
        mutable["model"]["values"][0] = "changed"

        self.assertEqual(owned.identity_layers["model"]["values"], ("original",))

    def test_reconciliation_reports_missing_copy_without_repairing_it(self) -> None:
        receipt = self.service.register(request())
        del self.copies.copies[receipt.object_key]

        report = self.service.reconcile(receipt.operation_id)

        self.assertFalse(report.ok)
        self.assertEqual(report.local_copy_status, "missing")
        self.assertNotIn(receipt.object_key, self.copies.copies)

    def test_retrieve_returns_the_bytes_it_verified_without_a_second_object_read(self) -> None:
        receipt = self.service.register(request())

        class ChangingObjectStore:
            def __init__(self, payload: bytes) -> None:
                self.payload = payload
                self.reads = 0

            def read(self, key: str) -> bytes:
                self.reads += 1
                return self.payload if self.reads == 1 else b"changed-after-verification"

            def write(self, key: str, data: bytes) -> None:
                raise AssertionError("retrieve must not write")

        changing = ChangingObjectStore(request().payload)
        self.service.objects = changing

        self.assertEqual(self.service.retrieve(receipt.operation_id), request().payload)
        self.assertEqual(changing.reads, 1)

    def test_cleanup_plan_is_content_identified_and_applies_nothing(self) -> None:
        receipt = self.service.register(request())
        before = (dict(self.objects.objects), dict(self.copies.copies), dict(self.metadata.registrations))

        plan = build_cleanup_plan(receipt)

        self.assertEqual(plan["status"], "quarantine-required")
        self.assertFalse(plan["deletions_authorized"])
        self.assertRegex(plan["plan_sha256"], r"\A[0-9a-f]{64}\Z")
        self.assertEqual(before, (self.objects.objects, self.copies.copies, self.metadata.registrations))

    def test_reconciliation_binds_current_runtime_provenance(self) -> None:
        fixture = json.loads((FIXTURES / "synthetic-attempt.json").read_text(encoding="utf-8"))
        provenance = {
            "runtime_commit": "a" * 40,
            "requirements_lock_sha256": "b" * 64,
            "fixture_sha256": "c" * 64,
            "migrations": [{"filename": "0001_runtime_core.sql", "sha256": "d" * 64}],
        }
        registration = RegistrationRequest(
            operation_id="op-provenance-001",
            campaign_id=fixture["campaign_id"],
            artifact_kind=fixture["artifact_kind"],
            media_type=fixture["media_type"],
            identity_layers=fixture["identity_layers"],
            payload=(FIXTURES / "synthetic-payload.json").read_bytes(),
            runtime_provenance=provenance,
        )
        self.service.register(registration)

        self.assertEqual(
            self.service.reconcile("op-provenance-001", expected_runtime_provenance=provenance).provenance_status,
            "match",
        )
        changed = {**provenance, "runtime_commit": "e" * 40}
        report = self.service.reconcile(
            "op-provenance-001", expected_runtime_provenance=changed
        )
        self.assertEqual(report.provenance_status, "mismatch")
        self.assertFalse(report.ok)


class FilesystemCopyStoreTests(unittest.TestCase):
    def test_atomic_write_is_idempotent_and_refuses_changed_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o750)
            store = FilesystemCopyStore(root)
            key = "objects/sha256/aa/" + "a" * 64
            store.write(key, b"payload")
            store.write(key, b"payload")

            self.assertEqual(store.read(key), b"payload")
            stored = root / key
            self.assertEqual(stored.stat().st_gid, root.stat().st_gid)
            self.assertEqual(stored.stat().st_mode & 0o777, 0o440)
            with self.assertRaises(CopyMismatch):
                store.write(key, b"changed")

    def test_new_namespace_components_and_file_are_fsynced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o750)
            store = FilesystemCopyStore(root)
            key = "objects/sha256/aa/" + "a" * 64

            with patch(
                "caplab.runtime.adapters.filesystem.os.fsync", wraps=os.fsync
            ) as fsync:
                store.write(key, b"payload")

            self.assertGreaterEqual(fsync.call_count, 8)

    def test_rejects_paths_outside_content_addressed_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o750)
            store = FilesystemCopyStore(root)
            with self.assertRaises(ValueError):
                store.read("../../etc/passwd")

    def test_refuses_symlinked_copy_or_namespace_component(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            root.chmod(0o750)
            store = FilesystemCopyStore(root)
            content_sha256 = "a" * 64
            key = f"objects/sha256/aa/{content_sha256}"
            target = Path(directory) / "target"
            target.write_bytes(b"payload")
            leaf = root / "objects/sha256/aa" / content_sha256
            leaf.parent.mkdir(parents=True)
            leaf.symlink_to(target)
            with self.assertRaises(ValueError):
                store.read(key)

            leaf.unlink()
            (root / "objects/sha256/aa").rmdir()
            (root / "objects/sha256").rmdir()
            (root / "objects").rmdir()
            (root / "objects").symlink_to(Path(directory))
            with self.assertRaises(ValueError):
                store.write(key, b"payload")


class ConfigurationTests(unittest.TestCase):
    def test_loads_frozen_runtime_contract_and_checks_expiry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.toml"
            path.write_text(
                """
[runtime]
campaign_id = "caplab-p4-roundtrip-2026-07-15"
authorization_expires_at = "2026-07-22T23:59:59Z"
runtime_commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

[postgres]
conninfo = "dbname=caplab host=/var/run/postgresql"

[garage]
endpoint_url = "http://127.0.0.1:3900"
region = "garage"
bucket = "caplab-v0"
credentials_root = "/etc/caplab/credentials"

[local_copy]
root = "/nvr/caplab/v0"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            config = RuntimeConfig.from_toml(path)

        config.require_active(datetime(2026, 7, 22, 23, 59, 58, tzinfo=UTC))
        with self.assertRaises(ConfigurationError):
            config.require_active(datetime(2026, 7, 23, tzinfo=UTC))
        self.assertEqual(config.garage_bucket, "caplab-v0")

    def test_rejects_runtime_namespace_or_connection_overrides(self) -> None:
        template = """
[runtime]
campaign_id = "{campaign}"
authorization_expires_at = "2026-07-22T23:59:59Z"
runtime_commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
[postgres]
conninfo = "{conninfo}"
[garage]
endpoint_url = "{endpoint}"
region = "{region}"
bucket = "{bucket}"
credentials_root = "{credentials}"
[local_copy]
root = "{copy_root}"
"""
        valid = {
            "campaign": "caplab-p4-roundtrip-2026-07-15",
            "conninfo": "dbname=caplab host=/var/run/postgresql",
            "endpoint": "http://127.0.0.1:3900",
            "region": "garage",
            "bucket": "caplab-v0",
            "credentials": "/etc/caplab/credentials",
            "copy_root": "/nvr/caplab/v0",
        }
        invalid = (
            {"campaign": "another-campaign"},
            {"expiry": "2099-07-22T23:59:59Z"},
            {"conninfo": "dbname=caplab host=/var/run/postgresql user=postgres"},
            {"conninfo": "dbname=other host=/var/run/postgresql"},
            {"endpoint": "http://localhost:3900"},
            {"region": "other"},
            {"bucket": "other"},
            {"credentials": "/tmp/credentials"},
            {"copy_root": "/tmp/copy"},
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.toml"
            for change in invalid:
                values = {**valid, **change}
                document = template.format(**values)
                if "expiry" in change:
                    document = document.replace(
                        "2026-07-22T23:59:59Z", str(change["expiry"])
                    )
                path.write_text(document, encoding="utf-8")
                with self.subTest(change=change), self.assertRaises(ConfigurationError):
                    RuntimeConfig.from_toml(path)

    def test_credentials_require_private_mode_and_exact_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "garage.json"
            path.write_text(
                json.dumps({"access_key_id": "GK-test", "secret_access_key": "private"}),
                encoding="utf-8",
            )
            os.chmod(path, 0o400)
            credentials = load_credentials(path)
            self.assertEqual(credentials.access_key_id, "GK-test")
            os.chmod(path, 0o440)
            with self.assertRaises(ConfigurationError):
                load_credentials(path)

    def test_cli_refuses_libpq_or_proxy_environment_influence_before_config(self) -> None:
        args = build_parser().parse_args(["migrate", "--config", "/does/not/exist"])
        for setting in ("PGUSER", "PGSERVICEFILE", "HTTP_PROXY", "HTTPS_PROXY"):
            with self.subTest(setting=setting), patch.dict(
                os.environ, {setting: "untrusted"}, clear=True
            ), self.assertRaisesRegex(ConfigurationError, "clean transport environment"):
                run(args)

    def test_live_config_is_opened_once_without_symlinks_and_has_frozen_custody(self) -> None:
        document = b"""
[runtime]
campaign_id = "caplab-p4-roundtrip-2026-07-15"
authorization_expires_at = "2026-07-22T23:59:59Z"
runtime_commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
[postgres]
conninfo = "dbname=caplab host=/var/run/postgresql"
[garage]
endpoint_url = "http://127.0.0.1:3900"
region = "garage"
bucket = "caplab-v0"
credentials_root = "/etc/caplab/credentials"
[local_copy]
root = "/nvr/caplab/v0"
""".strip() + b"\n"
        with tempfile.TemporaryFile() as stream:
            stream.write(document)
            stream.seek(0)
            descriptor = os.dup(stream.fileno())
            metadata = SimpleNamespace(
                st_mode=stat.S_IFREG | 0o640,
                st_uid=0,
                st_gid=123,
                st_size=len(document),
            )
            with patch("caplab.runtime.config.os.open", return_value=descriptor) as opened, patch(
                "caplab.runtime.config.os.fstat", return_value=metadata
            ), patch(
                "caplab.runtime.config.grp.getgrnam",
                return_value=SimpleNamespace(gr_gid=123),
            ):
                config = load_trusted_runtime_config(Path("/etc/caplab/runtime.toml"))

        self.assertEqual(config.runtime_commit, "a" * 40)
        self.assertEqual(opened.call_count, 1)
        self.assertTrue(opened.call_args.args[1] & os.O_NOFOLLOW)
        with self.assertRaises(ConfigurationError):
            load_trusted_runtime_config(Path("/tmp/runtime.toml"))

    def test_live_config_refuses_wrong_owner_group_or_mode(self) -> None:
        for metadata in (
            SimpleNamespace(st_mode=stat.S_IFREG | 0o640, st_uid=1000, st_gid=123),
            SimpleNamespace(st_mode=stat.S_IFREG | 0o640, st_uid=0, st_gid=456),
            SimpleNamespace(st_mode=stat.S_IFREG | 0o660, st_uid=0, st_gid=123),
        ):
            descriptor = os.open("/dev/null", os.O_RDONLY)
            with self.subTest(metadata=metadata), patch(
                "caplab.runtime.config.os.open", return_value=descriptor
            ), patch(
                "caplab.runtime.config.os.fstat", return_value=metadata
            ), patch(
                "caplab.runtime.config.grp.getgrnam",
                return_value=SimpleNamespace(gr_gid=123),
            ), self.assertRaises(ConfigurationError):
                load_trusted_runtime_config(Path("/etc/caplab/runtime.toml"))


class S3ObjectStoreTests(unittest.TestCase):
    class Body:
        def __init__(self, payload: bytes) -> None:
            self.payload = payload
            self.closed = False

        def read(self) -> bytes:
            return self.payload

        def close(self) -> None:
            self.closed = True

    class Client:
        def __init__(self) -> None:
            self.objects: dict[str, bytes] = {}
            self.last_body: S3ObjectStoreTests.Body | None = None

        def get_object(self, *, Bucket: str, Key: str) -> dict[str, object]:
            if Key not in self.objects:
                error = RuntimeError("not found")
                error.response = {"Error": {"Code": "NoSuchKey"}}  # type: ignore[attr-defined]
                raise error
            self.last_body = S3ObjectStoreTests.Body(self.objects[Key])
            return {"Body": self.last_body}

        def put_object(self, *, Bucket: str, Key: str, Body: bytes) -> None:
            self.objects[Key] = bytes(Body)

    def test_validates_content_key_and_closes_streaming_body(self) -> None:
        client = self.Client()
        store = S3ObjectStore(client, "caplab-v0")
        payload = b"payload"
        key = "objects/sha256/23/239f59ed55e737c77147cf55ad0c1b030b6d7ee748a7426952f9b852d5a935e5"

        store.write(key, payload)
        self.assertEqual(store.read(key), payload)
        self.assertTrue(client.last_body and client.last_body.closed)
        with self.assertRaises(ValueError):
            store.write("objects/sha256/00/" + "0" * 64, payload)

    def test_factory_disables_environment_proxy_resolution(self) -> None:
        with patch("boto3.client") as client:
            S3ObjectStore.from_settings(
                endpoint_url="http://127.0.0.1:3900",
                region="garage",
                bucket="caplab-v0",
                access_key_id="GK-test",
                secret_access_key="private",
            )

        config = client.call_args.kwargs["config"]
        self.assertEqual(config.proxies, {})

    def test_only_s3_missing_key_errors_become_absence(self) -> None:
        from botocore.exceptions import ClientError

        class MissingClient:
            def get_object(self, *, Bucket: str, Key: str) -> None:
                raise ClientError(
                    {"Error": {"Code": "NoSuchKey", "Message": "missing"}},
                    "GetObject",
                )

        key = (
            "objects/sha256/23/"
            "239f59ed55e737c77147cf55ad0c1b030b6d7ee748a7426952f9b852d5a935e5"
        )
        self.assertIsNone(S3ObjectStore(MissingClient(), "caplab-v0").read(key))


class MigrationContractTests(unittest.TestCase):
    def test_migrations_are_lexical_and_checksum_drift_stops(self) -> None:
        migrations = discover_migrations(ROOT / "src/caplab/runtime/migrations")
        self.assertEqual(
            [item.filename for item in migrations],
            ["0001_runtime_core.sql", "0002_p5_recovery_custody.sql"],
        )
        self.assertEqual(pending_migrations(migrations, {}), migrations)
        with self.assertRaises(ChecksumDrift):
            pending_migrations(migrations, {"0001_runtime_core.sql": "0" * 64})
        self.assertEqual(
            pending_migrations(
                migrations,
                {migrations[0].filename: migrations[0].sha256},
            ),
            [migrations[1]],
        )
        self.assertEqual(
            pending_migrations(
                migrations,
                {migration.filename: migration.sha256 for migration in migrations},
            ),
            [],
        )

    def test_core_migration_contains_selected_tables_and_append_only_guards(self) -> None:
        sql = (ROOT / "src/caplab/runtime/migrations/0001_runtime_core.sql").read_text(encoding="utf-8")
        for table in (
            "schema_migrations", "operation_requests", "operation_events",
            "model_identities", "agent_configurations", "administrations",
            "trial_contexts", "trial_assignments", "attempts", "artifacts",
            "attempt_artifacts", "manifests", "registrations", "audit_events",
        ):
            self.assertIn(f"CREATE TABLE caplab_v0.{table}", sql)
        self.assertIn("reject_mutation", sql)
        self.assertIn("pg_advisory_xact_lock", sql)
        self.assertNotIn("DROP SCHEMA PUBLIC", sql.upper())

    def test_runtime_lock_is_fully_pinned_and_hashed(self) -> None:
        lock = (ROOT / "src/caplab/runtime/requirements.lock").read_text(encoding="utf-8")
        requirements = [line for line in lock.splitlines() if line and not line.startswith("#")]
        self.assertTrue(requirements)
        for line in requirements:
            self.assertRegex(line, r"^[a-z0-9-]+==[^ ]+ --hash=sha256:[0-9a-f]{64}$")

    def test_runtime_distribution_includes_lock_and_migration(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('"caplab.runtime" = ["requirements.lock", "migrations/*.sql"]', pyproject)


class RuntimeCliTests(unittest.TestCase):
    def test_exposes_only_selected_command_groups(self) -> None:
        parser = build_parser()
        commands = {
            parser.parse_args([command, "--config", "/tmp/runtime.toml", *arguments]).command
            for command, arguments in (
                ("migrate", []),
                (
                    "register",
                    [
                        "--operation-id",
                        "op-p4-0001",
                        "--fixture",
                        "f",
                        "--payload",
                        "p",
                    ],
                ),
                ("retrieve", ["--operation-id", "op-p4-0001", "--output", "o"]),
                ("verify", ["--operation-id", "op-p4-0001"]),
                (
                    "reconcile",
                    ["--operation-id", "op-p4-0001", "--fixture", "f"],
                ),
                (
                    "cleanup-plan",
                    ["--operation-id", "op-p4-0001", "--output", "o"],
                ),
            )
        }
        self.assertEqual(
            commands,
            {"migrate", "register", "retrieve", "verify", "reconcile", "cleanup-plan"},
        )

    def test_fixture_loader_binds_campaign_and_payload_bytes(self) -> None:
        fixture = FIXTURES / "synthetic-attempt.json"
        payload = FIXTURES / "synthetic-payload.json"

        loaded = load_registration_request(
            fixture,
            payload,
            operation_id="op-p4-0001",
            expected_campaign="caplab-p4-roundtrip-2026-07-15",
        )

        self.assertEqual(loaded.operation_id, "op-p4-0001")
        self.assertEqual(loaded.payload, payload.read_bytes())
        with self.assertRaises(ValueError):
            load_registration_request(
                fixture,
                payload,
                operation_id="op-p4-0001",
                expected_campaign="different-campaign",
            )

    def test_registration_provenance_and_request_share_one_fixture_read(self) -> None:
        fixture_bytes = (FIXTURES / "synthetic-attempt.json").read_bytes()
        payload_bytes = (FIXTURES / "synthetic-payload.json").read_bytes()

        class OneRead:
            def __init__(self, payload: bytes) -> None:
                self.payload = payload
                self.reads = 0

            def read_bytes(self) -> bytes:
                self.reads += 1
                if self.reads > 1:
                    raise AssertionError("input was read more than once")
                return self.payload

        fixture = OneRead(fixture_bytes)
        payload = OneRead(payload_bytes)
        config = RuntimeConfig(
            campaign_id="caplab-p4-roundtrip-2026-07-15",
            authorization_expires_at=datetime(2026, 7, 22, 23, 59, 59, tzinfo=UTC),
            runtime_commit="a" * 40,
            postgres_conninfo="dbname=caplab host=/var/run/postgresql",
            garage_endpoint_url="http://127.0.0.1:3900",
            garage_region="garage",
            garage_bucket="caplab-v0",
            credentials_root=Path("/etc/caplab/credentials"),
            local_copy_root=Path("/nvr/caplab/v0"),
        )

        loaded = prepare_registration_request(
            fixture,  # type: ignore[arg-type]
            payload,  # type: ignore[arg-type]
            operation_id="op-p4-0001",
            config=config,
        )

        self.assertEqual(fixture.reads, 1)
        self.assertEqual(payload.reads, 1)
        self.assertEqual(
            loaded.runtime_provenance["fixture_sha256"],
            hashlib.sha256(fixture_bytes).hexdigest(),
        )

    def test_output_is_exclusive_and_fsynced_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            write_exclusive(path, b"first\n", mode=0o440)
            self.assertEqual(path.read_bytes(), b"first\n")
            self.assertEqual(path.stat().st_mode & 0o777, 0o440)
            with self.assertRaises(FileExistsError):
                write_exclusive(path, b"second\n", mode=0o440)


if __name__ == "__main__":
    unittest.main()
