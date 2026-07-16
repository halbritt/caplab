"""Hermetic contracts for the separately authorized CAPLAB P5 custody surface."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from caplab.recovery.adapters.memory import MemoryCustodyStore, MemoryPurgeStore
from caplab.recovery.adapters.filesystem import FilesystemCustodyStore
from caplab.recovery.adapters.s3 import S3CustodyStore
from caplab.recovery.config import RecoveryConfig
from caplab.recovery.errors import (
    AuthorizationMismatch,
    DependencyRetained,
    RecoverySourceMismatch,
    UnknownPurgeIdentity,
)
from caplab.recovery.models import (
    P5Authority,
    P5Identity,
    PurgeRequest,
    build_orphan_inventory,
    observe_invalid_attempt,
)
from caplab.recovery.service import PurgeService, RecoveryService
from caplab.recovery.faults import InterruptAfterEvent
from caplab.recovery.__main__ import (
    build_parser as build_recovery_parser,
    identity_document,
)
from caplab.runtime.adapters.memory import (
    MemoryCopyStore,
    MemoryMetadataStore,
    MemoryObjectStore,
)
from caplab.runtime.models import RegistrationRequest
from caplab.runtime.registration import RegistrationService


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/recovery"
AUTHORIZATION_SHA256 = "9" * 64
EXPIRES_AT = datetime(2026, 7, 23, 23, 59, 59, tzinfo=UTC)


def authority() -> tuple[P5Authority, RegistrationRequest]:
    fixture = json.loads(
        (FIXTURES / "synthetic-attempt.json").read_text(encoding="utf-8")
    )
    request = RegistrationRequest(
        operation_id=fixture["operation_id"],
        campaign_id=fixture["campaign_id"],
        artifact_kind=fixture["artifact_kind"],
        media_type=fixture["media_type"],
        identity_layers=fixture["identity_layers"],
        payload=(FIXTURES / "synthetic-payload.json").read_bytes(),
    )
    return (
        P5Authority(
            identity=P5Identity.from_intent(request.intent()),
            authorization_sha256=AUTHORIZATION_SHA256,
            expires_at=EXPIRES_AT,
        ),
        request,
    )


class RecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.authority, self.request = authority()
        self.intent = self.request.intent()
        self.objects = MemoryCustodyStore()
        self.copies = MemoryCustodyStore()
        self.objects.replace(self.intent.object_key, self.intent.payload)
        self.copies.replace(self.intent.object_key, self.intent.payload)
        self.service = RecoveryService(self.authority, self.objects, self.copies)

    def test_restores_missing_or_altered_object_only_from_verified_copy(self) -> None:
        self.objects.remove(self.intent.object_key)
        report = self.service.restore_object()
        self.assertEqual(report.action, "object-restored")
        self.assertEqual(self.objects.read(self.intent.object_key), self.intent.payload)

        self.objects.replace(self.intent.object_key, b"altered")
        report = self.service.restore_object()
        self.assertEqual(report.action, "object-restored")
        self.assertEqual(self.objects.read(self.intent.object_key), self.intent.payload)

    def test_restores_missing_or_altered_copy_only_from_verified_object(self) -> None:
        self.copies.remove(self.intent.object_key)
        report = self.service.restore_copy()
        self.assertEqual(report.action, "copy-restored")
        self.assertEqual(self.copies.read(self.intent.object_key), self.intent.payload)

        self.copies.replace(self.intent.object_key, b"altered")
        report = self.service.restore_copy()
        self.assertEqual(report.action, "copy-restored")
        self.assertEqual(self.copies.read(self.intent.object_key), self.intent.payload)

    def test_refuses_recovery_from_a_mismatched_source(self) -> None:
        self.objects.remove(self.intent.object_key)
        self.copies.replace(self.intent.object_key, b"not-the-registered-payload")

        with self.assertRaises(RecoverySourceMismatch):
            self.service.restore_object()

        self.assertIsNone(self.objects.read(self.intent.object_key))

    def test_interruption_after_either_verified_byte_write_is_retryable(self) -> None:
        for event_type, expected_writes in (
            ("object-verified", (1, 0)),
            ("local-copy-verified", (1, 1)),
        ):
            with self.subTest(event_type=event_type):
                metadata = MemoryMetadataStore()
                objects = MemoryObjectStore()
                copies = MemoryCopyStore()
                service = RegistrationService(
                    InterruptAfterEvent(metadata, event_type),
                    objects,
                    copies,
                )

                with self.assertRaisesRegex(
                    RuntimeError, f"injected {event_type} interruption"
                ):
                    service.register(self.request)

                self.assertEqual(
                    (objects.write_count, copies.write_count), expected_writes
                )
                self.assertIsNone(
                    metadata.registration_for_operation(self.intent.operation_id)
                )
                receipt = RegistrationService(metadata, objects, copies).register(
                    self.request
                )
                self.assertTrue(receipt.idempotent_replay)
                self.assertEqual((objects.write_count, copies.write_count), (1, 1))


class CustodyAdapterTests(unittest.TestCase):
    class Body:
        def __init__(self, payload: bytes) -> None:
            self.payload = payload
            self.closed = False

        def read(self) -> bytes:
            return self.payload

        def close(self) -> None:
            self.closed = True

    class S3Client:
        def __init__(self) -> None:
            self.objects: dict[str, bytes] = {}

        def get_object(self, *, Bucket: str, Key: str) -> dict[str, object]:
            from botocore.exceptions import ClientError

            if Key not in self.objects:
                raise ClientError(
                    {"Error": {"Code": "NoSuchKey", "Message": "missing"}},
                    "GetObject",
                )
            return {"Body": CustodyAdapterTests.Body(self.objects[Key])}

        def put_object(self, *, Bucket: str, Key: str, Body: bytes) -> None:
            self.objects[Key] = bytes(Body)

        def delete_object(self, *, Bucket: str, Key: str) -> None:
            self.objects.pop(Key, None)

        def list_objects_v2(self, **arguments: object) -> dict[str, object]:
            prefix = str(arguments["Prefix"])
            return {
                "IsTruncated": False,
                "Contents": [
                    {"Key": key}
                    for key in sorted(self.objects)
                    if key.startswith(prefix)
                ],
            }

    def test_s3_custodian_can_replace_remove_and_inventory_only_canonical_keys(
        self,
    ) -> None:
        client = self.S3Client()
        store = S3CustodyStore(client, "caplab-v0")
        key = "objects/sha256/aa/" + "a" * 64

        store.replace(key, b"first")
        store.replace(key, b"altered")
        self.assertEqual(store.read(key), b"altered")
        self.assertEqual(store.keys(), {key})
        store.remove(key)
        self.assertIsNone(store.read(key))
        with self.assertRaises(ValueError):
            store.replace("../../outside", b"payload")

    def test_filesystem_custodian_replaces_and_removes_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o750)
            store = FilesystemCustodyStore(root)
            key = "objects/sha256/aa/" + "a" * 64

            store.replace(key, b"first")
            store.replace(key, b"altered")
            self.assertEqual(store.read(key), b"altered")
            self.assertEqual(store.keys(), {key})
            stored = root / key
            self.assertEqual(stored.stat().st_mode & 0o777, 0o440)
            self.assertEqual(stored.stat().st_gid, root.stat().st_gid)
            store.remove(key)
            store.remove(key)
            self.assertIsNone(store.read(key))

            (root / "objects/sha256/aa").rmdir()
            (root / "objects/sha256").rmdir()
            (root / "objects").rmdir()
            (root / "objects").symlink_to(Path(directory) / "elsewhere")
            with self.assertRaises(ValueError):
                store.replace(key, b"payload")


class InvalidAttemptObservationTests(unittest.TestCase):
    def test_invalid_and_ambiguous_attempts_are_separate_non_outcome_records(
        self,
    ) -> None:
        payload = (FIXTURES / "invalid-attempt.json").read_bytes()
        for disposition in ("invalid", "ambiguous"):
            with self.subTest(disposition=disposition):
                observation = observe_invalid_attempt(
                    observation_id=f"obs-p5-{disposition}",
                    campaign_id="caplab-p5-recovery-2026-07-16",
                    fixture_bytes=payload,
                    disposition=disposition,
                    reason_codes=("missing-verifier-result",),
                )
                record = observation.to_record()
                self.assertEqual(record["disposition"], disposition)
                self.assertEqual(record["fixture_byte_count"], len(payload))
                self.assertNotIn("outcome", record)
                self.assertNotIn("score", record)
                self.assertNotIn("result", record)

    def test_observation_refuses_valid_or_outcome_bearing_dispositions(self) -> None:
        with self.assertRaises(ValueError):
            observe_invalid_attempt(
                observation_id="obs-p5-valid",
                campaign_id="caplab-p5-recovery-2026-07-16",
                fixture_bytes=b"{}",
                disposition="valid",
                reason_codes=("not-invalid",),
            )


class RecoveryConfigurationTests(unittest.TestCase):
    def document(self, **changes: str) -> str:
        frozen, _ = authority()
        identity = frozen.identity
        values = {
            "campaign": identity.campaign_id,
            "expiry": "2026-07-23T23:59:59Z",
            "authorization": frozen.authorization_sha256,
            "runtime_commit": "a" * 40,
            "operation": identity.operation_id,
            "request": identity.request_sha256,
            "content": identity.content_sha256,
            "object_key": identity.object_key,
            "manifest": identity.manifest_sha256,
            "conninfo": "dbname=caplab host=/var/run/postgresql",
            "endpoint": "http://127.0.0.1:3900",
            "region": "garage",
            "bucket": "caplab-v0",
            "credentials": "/etc/caplab-p5/credentials",
            "copy_root": "/nvr/caplab/v0",
        }
        values.update(changes)
        identity_hashes = ", ".join(
            f'{layer} = "{identity.identity_sha256[layer]}"'
            for layer in identity.identity_sha256
        )
        return (
            f"""
[campaign]
campaign_id = "{values["campaign"]}"
authorization_expires_at = "{values["expiry"]}"
authorization_sha256 = "{values["authorization"]}"
runtime_commit = "{values["runtime_commit"]}"

[identity]
operation_id = "{values["operation"]}"
request_sha256 = "{values["request"]}"
content_sha256 = "{values["content"]}"
object_key = "{values["object_key"]}"
manifest_sha256 = "{values["manifest"]}"
identity_sha256 = {{ {identity_hashes} }}

[postgres]
conninfo = "{values["conninfo"]}"

[garage]
endpoint_url = "{values["endpoint"]}"
region = "{values["region"]}"
bucket = "{values["bucket"]}"
credentials_root = "{values["credentials"]}"

[local_copy]
root = "{values["copy_root"]}"
""".strip()
            + "\n"
        )

    def test_config_is_pinned_to_the_exact_campaign_identity_and_namespaces(
        self,
    ) -> None:
        config = RecoveryConfig._from_text(self.document())
        config.require_active(datetime(2026, 7, 23, 23, 59, 58, tzinfo=UTC))

        self.assertEqual(config.authority.identity.operation_id, "op-p5-recovery-0001")
        self.assertEqual(config.credentials_root, Path("/etc/caplab-p5/credentials"))

    def test_config_refuses_campaign_identity_expiry_and_namespace_drift(self) -> None:
        for change in (
            {"campaign": "caplab-p4-roundtrip-2026-07-15"},
            {"expiry": "2026-07-24T23:59:59Z"},
            {"authorization": "8" * 63},
            {"object_key": "objects/sha256/00/" + "0" * 64},
            {"conninfo": "dbname=other host=/var/run/postgresql"},
            {"endpoint": "http://localhost:3900"},
            {"credentials": "/tmp/garage.json"},
            {"copy_root": "/tmp/copy"},
        ):
            with self.subTest(change=change), self.assertRaises(RuntimeError):
                RecoveryConfig._from_text(self.document(**change))

    def test_identity_bootstrap_binds_authorization_source_and_forward_migrations(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            authorization = Path(directory) / "authorization.md"
            authorization.write_text("authorized P5 purge\n", encoding="utf-8")
            document = identity_document(
                FIXTURES / "synthetic-attempt.json",
                FIXTURES / "synthetic-payload.json",
                authorization,
                runtime_commit="a" * 40,
            )

        self.assertEqual(
            document["authorization_sha256"],
            hashlib.sha256(b"authorized P5 purge\n").hexdigest(),
        )
        self.assertEqual(document["operation_id"], "op-p5-recovery-0001")
        self.assertEqual(
            [item["filename"] for item in document["runtime_provenance"]["migrations"]],
            ["0001_runtime_core.sql", "0002_p5_recovery_custody.sql"],
        )

    def test_recovery_cli_is_separate_from_the_ordinary_runtime(self) -> None:
        purge = build_recovery_parser().parse_args(
            ["purge", "--custody-request-id", "custody-p5-cli"]
        )
        restore = build_recovery_parser().parse_args(["restore-object"])
        self.assertEqual(purge.command, "purge")
        self.assertEqual(restore.command, "restore-object")


class OrphanInventoryTests(unittest.TestCase):
    def test_inventory_distinguishes_incomplete_unreferenced_and_dependent_state(
        self,
    ) -> None:
        key_a = "objects/sha256/aa/" + "a" * 64
        key_b = "objects/sha256/bb/" + "b" * 64
        inventory = build_orphan_inventory(
            operations={
                "op-p5-incomplete": {"object_key": key_a},
                "op-p5-registered": {"object_key": key_b},
            },
            registrations={
                "op-p5-registered": {"object_key": key_b, "local_copy_key": key_b}
            },
            object_keys={key_a, key_b, "objects/sha256/cc/" + "c" * 64},
            copy_keys={key_a, key_b, "objects/sha256/dd/" + "d" * 64},
            dependencies={"op-p5-registered": ("claim:claim-001",)},
        )

        self.assertEqual(inventory.incomplete_requests, ("op-p5-incomplete",))
        self.assertEqual(
            inventory.unreferenced_objects,
            (key_a, "objects/sha256/cc/" + "c" * 64),
        )
        self.assertEqual(
            inventory.unreferenced_copies,
            (key_a, "objects/sha256/dd/" + "d" * 64),
        )
        self.assertEqual(
            inventory.registered_dependencies,
            {"op-p5-registered": ("claim:claim-001",)},
        )


class GuardedPurgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.authority, self.request = authority()
        self.intent = self.request.intent()
        self.store = MemoryPurgeStore()
        self.store.add_registration(self.intent.registration_record())
        self.service = PurgeService(self.authority, self.store)

    def purge_request(self, **changes: str) -> PurgeRequest:
        values = {
            "custody_request_id": "custody-p5-0001",
            "operation_id": self.intent.operation_id,
            "campaign_id": self.intent.campaign_id,
            "request_sha256": self.intent.request_sha256,
            "content_sha256": self.intent.content_sha256,
            "manifest_sha256": self.intent.manifest_sha256,
            "authorization_sha256": AUTHORIZATION_SHA256,
            "expires_at": EXPIRES_AT,
        }
        values.update(changes)
        return PurgeRequest(**values)

    def test_refuses_unknown_mismatched_p4_and_non_p5_identities(self) -> None:
        with self.assertRaises(UnknownPurgeIdentity):
            self.service.purge(
                self.purge_request(operation_id="op-p5-unknown"),
                now=datetime(2026, 7, 16, tzinfo=UTC),
            )
        with self.assertRaises(AuthorizationMismatch):
            self.service.purge(
                self.purge_request(authorization_sha256="8" * 64),
                now=datetime(2026, 7, 16, tzinfo=UTC),
            )

        p4 = self.purge_request(
            operation_id="op-p4-0001",
            campaign_id="caplab-p4-roundtrip-2026-07-15",
        )
        with self.assertRaises(AuthorizationMismatch):
            self.service.purge(p4, now=datetime(2026, 7, 16, tzinfo=UTC))

    def test_refuses_retained_dependency_without_mutating_rows(self) -> None:
        self.store.dependencies[self.intent.operation_id] = {"dataset:dataset-001"}
        before = self.store.snapshot()

        with self.assertRaises(DependencyRetained):
            self.service.purge(
                self.purge_request(),
                now=datetime(2026, 7, 16, tzinfo=UTC),
            )

        self.assertEqual(self.store.snapshot(), before)

    def test_purge_is_exact_atomic_idempotence_refusing_and_retains_tombstone(
        self,
    ) -> None:
        tombstone = self.service.purge(
            self.purge_request(),
            now=datetime(2026, 7, 16, tzinfo=UTC),
        )

        self.assertEqual(tombstone.operation_id, self.intent.operation_id)
        self.assertEqual(tombstone.authorization_sha256, AUTHORIZATION_SHA256)
        self.assertNotIn(self.intent.operation_id, self.store.registrations)
        self.assertNotIn(self.intent.operation_id, self.store.operations)
        self.assertEqual(self.store.tombstones[self.intent.operation_id], tombstone)
        with self.assertRaises(UnknownPurgeIdentity):
            self.service.purge(
                self.purge_request(),
                now=datetime(2026, 7, 16, tzinfo=UTC),
            )


class RecoveryMigrationContractTests(unittest.TestCase):
    def test_forward_migration_adds_narrow_custody_surface_without_general_delete(
        self,
    ) -> None:
        sql = (
            ROOT / "src/caplab/runtime/migrations/0002_p5_recovery_custody.sql"
        ).read_text(encoding="utf-8")
        for table in (
            "invalid_attempt_observations",
            "custody_requests",
            "custody_dependency_events",
            "purge_tombstones",
        ):
            self.assertIn(f"CREATE TABLE caplab_v0.{table}", sql)
        self.assertIn("CREATE FUNCTION caplab_v0.purge_p5_operation", sql)
        self.assertIn("SECURITY DEFINER", sql)
        self.assertIn("caplab-p5-recovery-2026-07-16", sql)
        self.assertIn("GRANT EXECUTE ON FUNCTION caplab_v0.purge_p5_operation", sql)
        self.assertNotIn("GRANT DELETE ON", sql.upper())
        self.assertNotIn("TRUNCATE ", sql.upper())
        self.assertNotIn("DROP TABLE", sql.upper())
        self.assertNotIn("DISABLE TRIGGER", sql.upper())
