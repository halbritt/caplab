"""Behavioral contracts for qualification delivery and custody."""

from __future__ import annotations

import errno
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from caplab.qualification.__main__ import _execute, build_parser
from caplab.qualification.export import build_export, write_export_exclusive
from caplab.qualification.ledger import (
    FilesystemQualificationLedger,
    QualificationLedgerError,
)
from caplab.runtime.canonical import canonical_json, sha256_hex

REPOSITORY_ROOT = Path(__file__).parents[1]
CONTRACTS_DIRECTORY = REPOSITORY_ROOT / "docs" / "product" / "contracts"
FAKE_CONSUMER = REPOSITORY_ROOT / "tools" / "fake_quartermaster_consumer.py"
QUARTERMASTER_PROJECTION_CONTRACT = (
    REPOSITORY_ROOT
    / "tests"
    / "fixtures"
    / "quartermaster"
    / "projection-contract.json"
)


def owned(document: object, _resolver: object) -> dict[str, object]:
    parsed = json.loads(canonical_json(document))
    if not isinstance(parsed, dict):
        raise TypeError("document must be an object")
    return parsed


def content_ref(label: str, kind: str, schema: str) -> dict[str, object]:
    digest = sha256_hex(label.encode("utf-8"))
    return {
        "kind": kind,
        "schema": schema,
        "media_type": "application/json",
        "sha256": digest,
        "byte_count": len(label.encode("utf-8")),
        "locator": f"objects/sha256/{digest[:2]}/{digest}",
        "registration_ref": f"registration:{digest}",
        "custody": None,
    }


def unmeasured_claim(*, supersedes: list[str] | None = None) -> dict[str, object]:
    binding: dict[str, object] = {
        "schema_version": "caplab-binding/1",
        "binding_id": "",
        "model": {
            "model_id": "synthetic-model",
            "revision": "immutable-r1",
            "weights_ref": content_ref("weights", "model-weights", "bytes/1"),
            "weights_unavailable_reason": None,
        },
        "provider_or_path": {
            "kind": "local-serving",
            "identifier": "synthetic",
            "revision": "r1",
            "resolution": "immutable",
            "observed_at": None,
            "route_ref": content_ref(
                "route", "provider-route", "caplab-provider-route/1"
            ),
        },
        "harness": {
            "harness_id": "synthetic-harness",
            "harness_version": "1",
            "executable_ref": content_ref(
                "executable", "harness-executable", "bytes/1"
            ),
            "executable_unavailable_reason": None,
            "command_ref": content_ref(
                "command",
                "native-harness-command",
                "caplab-native-harness-command/1",
            ),
            "version_probe_ref": content_ref(
                "probe",
                "native-harness-version-probe",
                "caplab-native-harness-version-probe/1",
            ),
        },
        "reasoning_effort": "fixed",
        "configuration": {
            f"{name}_ref": content_ref(
                name,
                kind,
                "caplab-binding-configuration/1",
            )
            for name, kind in {
                "inference": "inference-configuration",
                "instructions": "instructions",
                "knowledge": "knowledge",
                "tools": "tools",
                "permissions": "permissions",
                "sandbox": "sandbox",
                "runtime": "runtime",
            }.items()
        },
    }
    binding_body = {key: value for key, value in binding.items() if key != "binding_id"}
    binding["binding_id"] = f"bnd-{sha256_hex(canonical_json(binding_body))}"
    capability = {
        "name": "review.correctness",
        "version": "1",
        "role": "review",
        "domain": "json",
        "distribution": "json-integer-minimum/1",
        "card_ref": content_ref("card", "capability-card", "capability-card/1"),
    }
    claim: dict[str, object] = {
        "schema_version": "caplab-qualification-claim/1",
        "claim_id": "",
        "generated_at": "2026-08-14T18:00:00Z",
        "assertion_type": "recommendation",
        "binding": binding,
        "capability": capability,
        "qualification": {
            "status": "unmeasured",
            "policy_id": "pol-" + "a" * 64,
            "policy_name": "synthetic-policy",
            "policy_version": "1",
            "policy_ref": content_ref(
                "policy", "qualification-policy", "caplab-qualification-policy/1"
            ),
            "authorization": None,
            "criteria": [],
            "limitations": ["no eligible measurement"],
            "expires_at": None,
            "invalidation_triggers": ["new measurement"],
        },
        "measurement": None,
        "evidence": {"bundle_ref": None, "run_refs": []},
        "provenance": {
            "caplab_version": "0.1.0",
            "caplab_commit": "a" * 40,
            "caplab_package_sha256": "b" * 64,
            "source_refs": [],
        },
        "supersedes": supersedes or [],
    }
    claim_body = {
        key: value
        for key, value in claim.items()
        if key not in {"claim_id", "generated_at"}
    }
    claim["claim_id"] = f"claim-{sha256_hex(canonical_json(claim_body))}"
    return claim


def replace_claim_identity(claim: dict[str, object]) -> None:
    binding = claim["binding"]
    assert isinstance(binding, dict)
    binding_body = {key: value for key, value in binding.items() if key != "binding_id"}
    binding["binding_id"] = f"bnd-{sha256_hex(canonical_json(binding_body))}"
    claim_body = {
        key: value
        for key, value in claim.items()
        if key not in {"claim_id", "generated_at"}
    }
    claim["claim_id"] = f"claim-{sha256_hex(canonical_json(claim_body))}"


def replace_export_identity(document: dict[str, object]) -> None:
    body = {key: value for key, value in document.items() if key != "export_id"}
    document["export_id"] = f"export-{sha256_hex(canonical_json(body))}"


class QualificationLedgerRegistrationTests(unittest.TestCase):
    def test_registered_document_round_trips_through_public_content_ref(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            document = {"schema_version": "example/1", "message": "Cafe\u0301"}

            first = ledger.register_document(
                document,
                kind="example",
                schema="example/1",
            )
            replay = ledger.register_document(
                document,
                kind="example",
                schema="example/1",
            )

            expected_bytes = canonical_json(document)
            expected_sha256 = sha256_hex(expected_bytes)
            self.assertEqual(first, replay)
            self.assertEqual(first["sha256"], expected_sha256)
            self.assertEqual(
                first["locator"],
                f"objects/sha256/{expected_sha256[:2]}/{expected_sha256}",
            )
            self.assertEqual(ledger.resolve(first), expected_bytes)
            registrations = (
                (Path(temporary_directory) / "qualification" / "registrations.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            )
            self.assertEqual(len(registrations), 1)
            self.assertEqual(
                json.loads(registrations[0])["registration_ref"],
                first["registration_ref"],
            )

    def test_registered_binary_round_trips_without_json_reencoding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            payload = b"\x00native executable\xff\n"

            reference = ledger.register_bytes(
                payload,
                kind="harness-executable",
                schema="opaque/1",
            )

            self.assertEqual(reference["media_type"], "application/octet-stream")
            self.assertEqual(ledger.resolve(reference), payload)

    def test_historical_custody_is_disabled_without_an_admission_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            custody = {
                "repository": "source/repository",
                "commit": "a" * 40,
                "path": "runs/result.json",
                "source_sha256": "b" * 64,
            }

            with self.assertRaisesRegex(
                ValueError, "historical_custody_registration_requires_admission_path"
            ):
                ledger.register_document(
                    {"result": "historical"},
                    kind="observation",
                    schema="observation/1",
                    custody=custody,
                )

    def test_tampered_object_invalidates_resolution_and_future_registration(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "qualification"
            ledger = FilesystemQualificationLedger(root)
            reference = ledger.register_document(
                {"schema_version": "example/1", "value": 1},
                kind="example",
                schema="example/1",
            )
            object_path = root / reference["locator"]
            object_path.chmod(0o640)
            object_path.write_bytes(b"tampered")

            with self.assertRaisesRegex(
                ValueError, "content_(byte_count|sha256)_mismatch"
            ):
                ledger.resolve(reference)
            with self.assertRaisesRegex(
                ValueError, "content_(byte_count|sha256)_mismatch"
            ):
                ledger.register_document(
                    {"schema_version": "example/1", "value": 2},
                    kind="example",
                    schema="example/1",
                )

    def test_symlinked_object_component_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "qualification"
            outside = Path(temporary_directory) / "outside"
            outside.mkdir()
            ledger = FilesystemQualificationLedger(root)
            (root / "objects").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(
                ValueError, "object_directory_not_real_directory"
            ):
                ledger.register_document(
                    {"schema_version": "example/1"},
                    kind="example",
                    schema="example/1",
                )
            self.assertEqual(list(outside.iterdir()), [])

    def test_registration_rejects_inexact_historical_custody(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            with self.assertRaisesRegex(ValueError, "content_ref_custody_invalid"):
                ledger.register_document(
                    {"schema_version": "example/1"},
                    kind="example",
                    schema="example/1",
                    custody={"repository": "source-without-provenance"},
                )


class QualificationLedgerStreamTests(unittest.TestCase):
    def test_failed_append_preserves_complete_prior_stream_and_canonical_error(
        self,
    ) -> None:
        class PartialWriteStream:
            def __init__(self, stream: object) -> None:
                self.stream = stream

            def __enter__(self) -> "PartialWriteStream":
                return self

            def __exit__(self, *exc_info: object) -> None:
                self.stream.close()

            def fileno(self) -> int:
                return self.stream.fileno()

            def write(self, payload: bytes) -> None:
                self.stream.write(payload[:11])
                self.stream.flush()
                raise OSError(errno.ENOSPC, "simulated full filesystem")

            def flush(self) -> None:
                self.stream.flush()

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "qualification"
            ledger = FilesystemQualificationLedger(root)
            ledger.append_measurement(
                {"measurement_id": "meas-" + "a" * 64, "index": 1},
                validator=owned,
            )
            stream_path = root / "measurements.jsonl"
            retained_image = stream_path.read_bytes()
            real_fdopen = os.fdopen

            def partial_append(descriptor: int, mode: str, **keywords: object):
                stream = real_fdopen(descriptor, mode, **keywords)
                if mode == "ab":
                    return PartialWriteStream(stream)
                return stream

            with mock.patch(
                "caplab.qualification.ledger.os.fdopen",
                side_effect=partial_append,
            ):
                with self.assertRaisesRegex(
                    QualificationLedgerError,
                    "ledger_stream_append_failed:measurements.jsonl",
                ):
                    ledger.append_measurement(
                        {"measurement_id": "meas-" + "b" * 64, "index": 2},
                        validator=owned,
                    )

            self.assertEqual(stream_path.read_bytes(), retained_image)
            self.assertEqual(list(root.glob(".qualification-*")), [])

    def test_directory_fsync_failure_leaves_one_complete_retryable_image(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "qualification"
            ledger = FilesystemQualificationLedger(root)
            first = {"measurement_id": "meas-" + "a" * 64, "index": 1}
            second = {"measurement_id": "meas-" + "b" * 64, "index": 2}
            ledger.append_measurement(first, validator=owned)
            real_fsync = os.fsync

            def fail_directory_fsync(descriptor: int) -> None:
                if stat.S_ISDIR(os.fstat(descriptor).st_mode):
                    raise OSError(errno.ENOSPC, "simulated directory fsync failure")
                real_fsync(descriptor)

            with mock.patch(
                "caplab.qualification.ledger.os.fsync",
                side_effect=fail_directory_fsync,
            ):
                with self.assertRaisesRegex(
                    QualificationLedgerError,
                    "ledger_stream_append_failed:measurements.jsonl",
                ):
                    ledger.append_measurement(second, validator=owned)

            replay = ledger.append_measurement(second, validator=owned)
            records = [
                json.loads(line)
                for line in (root / "measurements.jsonl").read_bytes().splitlines()
            ]
            self.assertEqual(replay, second)
            self.assertEqual(records, [first, second])

    def test_measurement_append_is_exactly_idempotent_and_rejects_id_collision(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            measurement = {
                "schema_version": "caplab-measurement/1",
                "measurement_id": "meas-" + "a" * 64,
                "observation": "first",
            }

            first = ledger.append_measurement(measurement, validator=owned)
            replay = ledger.append_measurement(measurement, validator=owned)

            self.assertEqual(first, replay)
            stream = (
                (Path(temporary_directory) / "qualification" / "measurements.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            )
            self.assertEqual(len(stream), 1)
            conflicting = {**measurement, "observation": "changed"}
            with self.assertRaisesRegex(ValueError, "measurement_identity_conflict"):
                ledger.append_measurement(conflicting, validator=owned)

    def test_policy_append_validates_the_complete_existing_stream(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "qualification"
            ledger = FilesystemQualificationLedger(root)
            policy = {
                "schema_version": "caplab-qualification-policy/1",
                "policy_id": "pol-" + "a" * 64,
                "name": "review-correctness",
                "version": "1",
            }
            ledger.append_policy(policy, validator=owned)
            with (root / "policies.jsonl").open("ab") as stream:
                stream.write(b"\n")

            with self.assertRaisesRegex(ValueError, "blank_ledger_line"):
                ledger.append_policy(
                    {**policy, "policy_id": "pol-" + "b" * 64},
                    validator=owned,
                )

    def test_policy_name_and_version_cannot_name_two_semantic_bodies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            first = {
                "schema_version": "caplab-qualification-policy/1",
                "policy_id": "pol-" + "a" * 64,
                "name": "review-correctness",
                "version": "1",
                "criteria": [{"threshold": "3/4"}],
            }
            second = {
                **first,
                "policy_id": "pol-" + "b" * 64,
                "criteria": [{"threshold": "9/10"}],
            }
            ledger.append_policy(first, validator=owned)

            with self.assertRaisesRegex(ValueError, "policy_name_version_conflict"):
                ledger.append_policy(second, validator=owned)

    def test_symlinked_stream_is_refused_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "qualification"
            ledger = FilesystemQualificationLedger(root)
            target = Path(temporary_directory) / "outside.jsonl"
            target.write_text("outside\n", encoding="utf-8")
            (root / "measurements.jsonl").symlink_to(target)

            with self.assertRaisesRegex(ValueError, "ledger_stream_not_regular"):
                ledger.append_measurement(
                    {"measurement_id": "meas-" + "a" * 64},
                    validator=owned,
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "outside\n")

    def test_concurrent_writers_preserve_each_unique_measurement_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "qualification"

            def append(index: int) -> str:
                ledger = FilesystemQualificationLedger(root)
                measurement_id = f"meas-{index:064x}"
                ledger.append_measurement(
                    {"measurement_id": measurement_id, "index": index},
                    validator=owned,
                )
                return measurement_id

            with ThreadPoolExecutor(max_workers=8) as executor:
                expected_ids = set(executor.map(append, range(24)))

            lines = (root / "measurements.jsonl").read_bytes().splitlines()
            records = [json.loads(line) for line in lines]
            self.assertEqual(len(records), 24)
            self.assertEqual(
                {record["measurement_id"] for record in records}, expected_ids
            )
            self.assertEqual(lines, [canonical_json(record) for record in records])


class QualificationClaimHistoryTests(unittest.TestCase):
    def test_later_unqualified_claim_supersedes_without_mutating_qualified_claim(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            capability = {
                "name": "review.correctness",
                "version": "1",
                "role": "review",
                "domain": "json",
                "distribution": "json-integer-minimum/1",
            }
            qualified = {
                "claim_id": "claim-" + "1" * 64,
                "binding": {"binding_id": "bnd-" + "a" * 64},
                "capability": capability,
                "qualification": {"status": "qualified"},
                "supersedes": [],
            }
            unqualified = {
                **qualified,
                "claim_id": "claim-" + "2" * 64,
                "qualification": {"status": "unqualified"},
                "supersedes": [qualified["claim_id"]],
            }

            retained_qualified = ledger.append_claim(qualified, validator=owned)
            ledger.append_claim(unqualified, validator=owned)
            history = ledger.history(
                qualified["binding"]["binding_id"],
                capability,
                validator=owned,
            )

            self.assertEqual(retained_qualified, qualified)
            self.assertEqual(history["claims"], [qualified, unqualified])
            self.assertEqual(history["head_claim_ids"], [unqualified["claim_id"]])
            self.assertFalse(history["ambiguous"])

    def test_dangling_self_and_cross_scope_supersession_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            first = {
                "claim_id": "claim-" + "1" * 64,
                "binding": {"binding_id": "bnd-" + "a" * 64},
                "capability": {"name": "review", "version": "1"},
                "supersedes": [],
            }
            ledger.append_claim(first, validator=owned)
            cases = (
                (
                    {
                        **first,
                        "claim_id": "claim-" + "2" * 64,
                        "supersedes": ["claim-" + "f" * 64],
                    },
                    "claim_dangling_supersession",
                ),
                (
                    {
                        **first,
                        "claim_id": "claim-" + "3" * 64,
                        "supersedes": ["claim-" + "3" * 64],
                    },
                    "claim_self_supersession",
                ),
                (
                    {
                        **first,
                        "claim_id": "claim-" + "4" * 64,
                        "binding": {"binding_id": "bnd-" + "b" * 64},
                        "supersedes": [first["claim_id"]],
                    },
                    "claim_cross_scope_supersession",
                ),
            )
            for claim, error in cases:
                with (
                    self.subTest(error=error),
                    self.assertRaisesRegex(ValueError, error),
                ):
                    ledger.append_claim(claim, validator=owned)

    def test_tampered_cycle_is_detected_during_history_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "qualification"
            ledger = FilesystemQualificationLedger(root)
            first_id = "claim-" + "1" * 64
            second_id = "claim-" + "2" * 64
            common = {
                "binding": {"binding_id": "bnd-" + "a" * 64},
                "capability": {"name": "review", "version": "1"},
            }
            records = [
                {**common, "claim_id": first_id, "supersedes": [second_id]},
                {**common, "claim_id": second_id, "supersedes": [first_id]},
            ]
            (root / "claims.jsonl").write_bytes(
                b"".join(canonical_json(record) + b"\n" for record in records)
            )

            with self.assertRaisesRegex(ValueError, "claim_supersession_cycle"):
                ledger.history(
                    common["binding"]["binding_id"],
                    common["capability"],
                    validator=owned,
                )

    def test_parallel_heads_are_reported_as_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            common = {
                "binding": {"binding_id": "bnd-" + "a" * 64},
                "capability": {"name": "review", "version": "1"},
                "supersedes": [],
            }
            claims = [
                {**common, "claim_id": "claim-" + digit * 64} for digit in ("1", "2")
            ]
            for claim in reversed(claims):
                ledger.append_claim(claim, validator=owned)

            history = ledger.history(
                common["binding"]["binding_id"],
                common["capability"],
                validator=owned,
            )

            self.assertEqual(history["claims"], claims)
            self.assertEqual(
                history["head_claim_ids"],
                [claim["claim_id"] for claim in claims],
            )
            self.assertTrue(history["ambiguous"])

    def test_claim_replay_preserves_first_generated_at(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            claim = {
                "claim_id": "claim-" + "1" * 64,
                "generated_at": "2026-08-14T18:00:00Z",
                "binding": {"binding_id": "bnd-" + "a" * 64},
                "capability": {"name": "review", "version": "1"},
                "supersedes": [],
            }
            first = ledger.append_claim(claim, validator=owned)

            replay = ledger.append_claim(
                {**claim, "generated_at": "2026-08-14T19:00:00Z"},
                validator=owned,
            )

            self.assertEqual(replay, first)
            self.assertEqual(
                (Path(temporary_directory) / "qualification" / "claims.jsonl")
                .read_text(encoding="utf-8")
                .count("\n"),
                1,
            )


class QualificationExportTests(unittest.TestCase):
    def test_export_is_content_identified_and_uses_rehashed_local_schema_catalog(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            claim = unmeasured_claim()
            ledger.append_claim(claim, validator=owned)
            contracts = Path(__file__).parents[1] / "docs" / "product" / "contracts"

            first = build_export(
                ledger,
                claim["binding"]["binding_id"],
                claim["capability"],
                contracts_directory=contracts,
                producer_version="0.1.0",
                producer_commit="b" * 40,
                producer_package_sha256="c" * 64,
                claim_validator=owned,
            )
            second = build_export(
                ledger,
                claim["binding"]["binding_id"],
                claim["capability"],
                contracts_directory=contracts,
                producer_version="0.1.0",
                producer_commit="b" * 40,
                producer_package_sha256="c" * 64,
                claim_validator=owned,
            )

            self.assertEqual(first, second)
            export_body = {
                key: value for key, value in first.items() if key != "export_id"
            }
            self.assertEqual(
                first["export_id"],
                f"export-{sha256_hex(canonical_json(export_body))}",
            )
            self.assertEqual(first["claims"], [claim])
            self.assertEqual(first["producer"]["commit"], "b" * 40)
            self.assertEqual(first["producer"]["package_sha256"], "c" * 64)
            self.assertEqual(
                set(first),
                {
                    "schema_version",
                    "export_id",
                    "selection",
                    "schemas",
                    "claims",
                    "producer",
                },
            )
            self.assertEqual(
                first["schemas"]["claim"]["sha256"],
                sha256_hex(
                    (contracts / "qualification-claim-v1.schema.json").read_bytes()
                ),
            )

    def test_export_write_is_exclusive_and_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "claim-export.json"
            document = {"schema_version": "example-export/1", "export_id": "first"}

            write_export_exclusive(path, document)

            self.assertEqual(path.read_bytes(), canonical_json(document) + b"\n")
            with self.assertRaisesRegex(ValueError, "export_output_exists"):
                write_export_exclusive(path, {**document, "export_id": "second"})
            self.assertEqual(path.read_bytes(), canonical_json(document) + b"\n")

    def test_export_write_does_not_publish_before_file_and_directory_fsync(
        self,
    ) -> None:
        document = {"schema_version": "example-export/1", "export_id": "first"}
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "claim-export.json"
            with (
                mock.patch(
                    "caplab.qualification.export.os.fsync",
                    side_effect=OSError("simulated file fsync failure"),
                ),
                self.assertRaisesRegex(ValueError, "export_output_write_failed"),
            ):
                write_export_exclusive(path, document)
            self.assertFalse(path.exists())
            self.assertEqual(list(Path(temporary_directory).iterdir()), [])

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "claim-export.json"
            real_fsync = os.fsync
            calls = 0

            def fail_directory_fsync(descriptor):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated directory fsync failure")
                return real_fsync(descriptor)

            with (
                mock.patch(
                    "caplab.qualification.export.os.fsync",
                    side_effect=fail_directory_fsync,
                ),
                self.assertRaisesRegex(
                    ValueError, "export_output_directory_fsync_failed"
                ),
            ):
                write_export_exclusive(path, document)
            self.assertFalse(path.exists())
            self.assertEqual(list(Path(temporary_directory).iterdir()), [])

    def test_export_refuses_catalog_resource_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger = FilesystemQualificationLedger(
                Path(temporary_directory) / "qualification"
            )
            claim = unmeasured_claim()
            ledger.append_claim(claim, validator=owned)
            copied_contracts = Path(temporary_directory) / "contracts"
            shutil.copytree(CONTRACTS_DIRECTORY, copied_contracts)
            export_schema = copied_contracts / "qualification-export-v1.schema.json"
            export_schema.write_bytes(export_schema.read_bytes() + b" ")

            with self.assertRaisesRegex(ValueError, "schema_catalog_hash_mismatch"):
                build_export(
                    ledger,
                    claim["binding"]["binding_id"],
                    claim["capability"],
                    contracts_directory=copied_contracts,
                    producer_version="0.1.0",
                    producer_commit="b" * 40,
                    producer_package_sha256="c" * 64,
                    claim_validator=owned,
                )


class FakeQuartermasterConsumerTests(unittest.TestCase):
    def _build_export(self, temporary_directory: str) -> dict[str, object]:
        ledger = FilesystemQualificationLedger(
            Path(temporary_directory) / "qualification"
        )
        claim = unmeasured_claim()
        ledger.append_claim(claim, validator=owned)
        return build_export(
            ledger,
            claim["binding"]["binding_id"],
            claim["capability"],
            contracts_directory=CONTRACTS_DIRECTORY,
            producer_version="0.1.0",
            producer_commit="b" * 40,
            producer_package_sha256="c" * 64,
            claim_validator=owned,
        )

    def _run(
        self,
        document: dict[str, object],
        temporary_directory: str,
        *,
        contracts_directory: Path = CONTRACTS_DIRECTORY,
        payload: bytes | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        export_path = Path(temporary_directory) / "export.json"
        export_path.write_bytes(
            canonical_json(document) + b"\n" if payload is None else payload
        )
        environment = {
            "PATH": "/usr/bin:/bin",
            "PYTHONPATH": "",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        return subprocess.run(
            [
                sys.executable,
                str(FAKE_CONSUMER),
                "--export",
                str(export_path),
                "--catalog",
                str(contracts_directory / "qualification-schema-catalog-v1.json"),
            ],
            cwd=temporary_directory,
            env=environment,
            capture_output=True,
            check=False,
        )

    def test_consumer_is_independent_and_emits_no_active_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            document = self._build_export(temporary_directory)

            result = self._run(document, temporary_directory)

            self.assertEqual(result.returncode, 0, result.stderr.decode())
            output = json.loads(result.stdout)
            projection_contract = json.loads(
                QUARTERMASTER_PROJECTION_CONTRACT.read_text(encoding="utf-8")
            )
            self.assertIsInstance(output, list)
            self.assertEqual(len(output), 1)
            self.assertEqual(set(output[0]), set(projection_contract["claim_fields"]))
            self.assertNotIn("current", result.stdout.decode())
            source = FAKE_CONSUMER.read_text(encoding="utf-8")
            self.assertNotIn("from caplab", source)
            self.assertNotIn("import caplab", source)

    def test_consumer_rejects_hostile_exports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            original = self._build_export(temporary_directory)
            cases: dict[str, tuple[dict[str, object], str]] = {}

            extra = json.loads(canonical_json(original))
            extra["unexpected"] = True
            replace_export_identity(extra)
            cases["extra-field"] = (extra, "additional_property")

            bad_hash = json.loads(canonical_json(original))
            bad_hash["schemas"]["claim"]["sha256"] = "0" * 64
            replace_export_identity(bad_hash)
            cases["bad-schema-hash"] = (bad_hash, "export_schema_reference_mismatch")

            duplicate = json.loads(canonical_json(original))
            duplicate["claims"].append(duplicate["claims"][0])
            replace_export_identity(duplicate)
            cases["duplicate-claim"] = (duplicate, "unique_items_failed")

            dangling = json.loads(canonical_json(original))
            dangling_claim = dangling["claims"][0]
            dangling_claim["supersedes"] = ["claim-" + "f" * 64]
            replace_claim_identity(dangling_claim)
            replace_export_identity(dangling)
            cases["dangling-supersession"] = (dangling, "dangling_supersession")

            self_supersession = json.loads(canonical_json(original))
            self_claim = self_supersession["claims"][0]
            self_claim["supersedes"] = [self_claim["claim_id"]]
            replace_export_identity(self_supersession)
            cases["self-supersession"] = (self_supersession, "self_supersession")

            cross_scope = json.loads(canonical_json(original))
            cross_claim = json.loads(canonical_json(cross_scope["claims"][0]))
            cross_claim["binding"]["model"]["model_id"] = "other-model"
            cross_claim["supersedes"] = [cross_scope["claims"][0]["claim_id"]]
            replace_claim_identity(cross_claim)
            cross_scope["claims"].append(cross_claim)
            cross_scope["claims"].sort(key=lambda claim: claim["claim_id"])
            replace_export_identity(cross_scope)
            cases["cross-scope-supersession"] = (
                cross_scope,
                "cross_scope_supersession",
            )

            cycle = json.loads(canonical_json(original))
            first = cycle["claims"][0]
            second = json.loads(canonical_json(first))
            second["generated_at"] = "2026-08-14T18:01:00Z"
            second["qualification"]["limitations"] = ["cycle fixture"]
            replace_claim_identity(second)
            first["supersedes"] = [second["claim_id"]]
            second["supersedes"] = [first["claim_id"]]
            cycle["claims"] = sorted(
                [first, second], key=lambda claim: claim["claim_id"]
            )
            replace_export_identity(cycle)
            cases["cycle"] = (cycle, "supersession_cycle")

            runtime = json.loads(canonical_json(original))
            runtime["current"] = {
                "health": "green",
                "quota": 1,
                "placement": "preferred",
                "Dispatch": "now",
            }
            replace_export_identity(runtime)
            cases["runtime-fields"] = (runtime, "additional_property")

            for name, (document, expected_error) in cases.items():
                with self.subTest(name=name):
                    result = self._run(document, temporary_directory)
                    self.assertEqual(result.returncode, 3, result.stderr.decode())
                    self.assertEqual(result.stdout, b"")
                    self.assertIn(expected_error, result.stderr.decode())

    def test_consumer_recomputes_each_catalog_resource_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            document = self._build_export(temporary_directory)
            copied_contracts = Path(temporary_directory) / "contracts"
            shutil.copytree(CONTRACTS_DIRECTORY, copied_contracts)
            claim_schema = copied_contracts / "qualification-claim-v1.schema.json"
            claim_schema.write_bytes(claim_schema.read_bytes() + b" ")

            result = self._run(
                document,
                temporary_directory,
                contracts_directory=copied_contracts,
            )

            self.assertEqual(result.returncode, 3)
            self.assertEqual(result.stdout, b"")

    def test_consumer_rejects_noncanonical_export_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            document = self._build_export(temporary_directory)
            pretty = json.dumps(document, indent=2).encode("utf-8") + b"\n"

            result = self._run(
                document,
                temporary_directory,
                payload=pretty,
            )

            self.assertEqual(result.returncode, 3)
            self.assertIn("export_not_canonical", result.stderr.decode())


class QualificationCliTests(unittest.TestCase):
    def test_root_register_smoke_emits_one_canonical_content_ref(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "document.json"
            ledger_path = Path(temporary_directory) / "ledger"
            input_path.write_text('{"schema_version":"example/1","value":1}\n')
            environment = {
                "PATH": "/usr/bin:/bin",
                "PYTHONPATH": str(REPOSITORY_ROOT / "src"),
                "PYTHONDONTWRITEBYTECODE": "1",
            }

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caplab",
                    "qualification",
                    "register",
                    "--input",
                    str(input_path),
                    "--kind",
                    "example",
                    "--schema",
                    "example/1",
                    "--ledger",
                    str(ledger_path),
                ],
                cwd=temporary_directory,
                env=environment,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode())
            reference = json.loads(result.stdout)
            self.assertEqual(result.stdout, canonical_json(reference) + b"\n")
            self.assertEqual(
                len((ledger_path / "registrations.jsonl").read_text().splitlines()),
                1,
            )

    def test_apply_binding_uses_cli_clock_and_null_measurement_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            binding_path = Path(temporary_directory) / "binding.json"
            policy_path = Path(temporary_directory) / "policy.json"
            ledger_path = Path(temporary_directory) / "ledger"
            binding = {
                "schema_version": "caplab-binding/1",
                "binding_id": "bnd-" + "a" * 64,
            }
            policy = {
                "schema_version": "caplab-qualification-policy/1",
                "policy_id": "pol-" + "b" * 64,
                "name": "fixture-policy",
                "version": "1",
            }
            binding_path.write_bytes(canonical_json(binding) + b"\n")
            policy_path.write_bytes(canonical_json(policy) + b"\n")
            captured: dict[str, object] = {}

            def build_claim(
                measurement: object,
                received_policy: object,
                **keywords: object,
            ) -> dict[str, object]:
                captured.update(
                    {
                        "measurement": measurement,
                        "policy": received_policy,
                        **keywords,
                    }
                )
                return {
                    "claim_id": "claim-" + "c" * 64,
                    "generated_at": keywords["generated_at"],
                    "binding": keywords["binding"],
                    "capability": {"name": "review", "version": "1"},
                    "qualification": {"status": "unmeasured"},
                    "supersedes": keywords["supersedes"],
                }

            core = SimpleNamespace(
                QualificationContractError=ValueError,
                validate_measurement=owned,
                validate_policy=owned,
                validate_claim=owned,
                build_claim=build_claim,
            )
            options = build_parser().parse_args(
                [
                    "apply",
                    "--binding",
                    str(binding_path),
                    "--policy",
                    str(policy_path),
                    "--ledger",
                    str(ledger_path),
                ]
            )

            document, read_only = _execute(
                options,
                clock=lambda: datetime(2026, 8, 14, 20, 30, tzinfo=UTC),
                core_loader=lambda: core,
                producer_identity=lambda: ("0.1.0", "d" * 40, "e" * 64),
            )

            self.assertFalse(read_only)
            self.assertEqual(document["qualification"]["status"], "unmeasured")
            self.assertIsNone(captured["measurement"])
            self.assertIsNone(captured["measurement_ref"])
            self.assertEqual(captured["binding"], binding)
            self.assertEqual(captured["generated_at"], "2026-08-14T20:30:00Z")
            self.assertEqual(captured["caplab_version"], "0.1.0")
            self.assertEqual(captured["caplab_commit"], "d" * 40)
            self.assertEqual(captured["caplab_package_sha256"], "e" * 64)

    def test_apply_requires_exactly_one_measurement_or_binding(self) -> None:
        parser = build_parser()
        common = ["--policy", "/policy.json", "--ledger", "/ledger"]
        with self.assertRaises(ValueError):
            parser.parse_args(["apply", *common])
        with self.assertRaises(ValueError):
            parser.parse_args(
                [
                    "apply",
                    "--measurement",
                    "/measurement.json",
                    "--binding",
                    "/binding.json",
                    *common,
                ]
            )


if __name__ == "__main__":
    unittest.main()
