from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from caplab.admission.models import GitRecord, SourceSet
from caplab.admission.adapters.memory import MemoryAdmissionStore
from caplab.admission.__main__ import build_parser
from caplab.admission.config import AdmissionConfig, ConfigurationError
from caplab.admission.service import AdmissionService
from caplab.admission.source import build_manifest
from caplab.runtime.adapters.memory import MemoryCopyStore, MemoryObjectStore


FIXTURE = Path(__file__).parent / "fixtures/admission"


class MappingGitReader:
    def __init__(self, records: dict[tuple[str, str], bytes]) -> None:
        self.records = records

    def read(self, commit: str, path: str) -> bytes:
        return self.records[(commit, path)]


class AdmissionSourceTests(unittest.TestCase):
    def test_build_manifest_verifies_and_accounts_for_every_source_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "attempts/s01").mkdir(parents=True)
            payload = b"hello\n"
            payload_sha = hashlib.sha256(payload).hexdigest()
            (root / "attempts/s01/trial.txt").write_bytes(payload)
            manifest = f"{payload_sha}  attempts/s01/trial.txt\n".encode()
            (root / "manifest.sha256").write_bytes(manifest)
            result = b"historical result\n"
            result_sha = hashlib.sha256(result).hexdigest()
            source = SourceSet(
                study_id="caplab-study-001",
                preservation_root=root,
                preservation_manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                git_records=(
                    GitRecord(
                        record_id="preregistration",
                        commit="a" * 40,
                        path="study.md",
                        content_sha256=payload_sha,
                        already_preserved_path="attempts/s01/trial.txt",
                    ),
                    GitRecord(
                        record_id="result-record",
                        commit="b" * 40,
                        path="result.md",
                        content_sha256=result_sha,
                    ),
                ),
                expected_preservation_records=1,
                expected_total_records=3,
                expected_attempts=0,
            )

            built = build_manifest(
                source,
                git_reader=MappingGitReader(
                    {
                        ("a" * 40, "study.md"): payload,
                        ("b" * 40, "result.md"): result,
                    }
                ),
            )

        self.assertEqual(built["schema_version"], "caplab-study-admission/1")
        self.assertEqual(len(built["records"]), 3)
        self.assertEqual(len({item["record_id"] for item in built["records"]}), 3)
        self.assertEqual(len({item["content_sha256"] for item in built["records"]}), 3)
        self.assertTrue(
            all(
                item["disposition"] == "restricted-admission"
                for item in built["records"]
            )
        )
        self.assertEqual(built["summary"]["record_count"], 3)
        self.assertEqual(built["summary"]["unique_content_count"], 3)
        self.assertRegex(built["manifest_sha256"], r"\A[0-9a-f]{64}\Z")

    def test_build_manifest_links_one_first_attempt_to_assignment_and_outcome(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trial_name = "s01-m1-B-attempt1"
            payloads = {
                "frozen-inputs/checkout-retries-luna-bv-confirmation-order.csv": (
                    b"sequence,block,task,arm\n1,m1,checkout-retries-m1,B\n"
                ),
                "frozen-inputs/checkout-retries-luna-bv-confirmation/experiment.json": b"{}\n",
                "frozen-inputs/checkout-retries-luna-bv-confirmation/treatment-manifest.json": b"{}\n",
                "frozen-inputs/checkout-retries-luna-bv-confirmation.md": b"preregistered\n",
                f"attempts/{trial_name}/trial-metadata.json": json.dumps(
                    {
                        "sequence": 1,
                        "block": "m1",
                        "task": "checkout-retries-m1",
                        "arm": "B",
                        "attempt": 1,
                        "sealed_at": "2026-07-14T15:15:31Z",
                        "model": "model-a",
                        "backend_id": "backend-a",
                        "reasoning_effort": "max",
                        "runtime_version": "runtime-a",
                        "execution_mode": "subscription-model",
                        "capture_binary_sha256": "1" * 64,
                        "observer_commit": "2" * 40,
                        "surface_hash": "3" * 64,
                        "task_content_hash": "4" * 64,
                    },
                    sort_keys=True,
                ).encode(),
                f"attempts/{trial_name}/trial.json": json.dumps(
                    {
                        "started": "2026-07-14T15:15:31Z",
                        "provenance": {"finished": "2026-07-14T15:18:11Z"},
                    },
                    sort_keys=True,
                ).encode(),
                f"attempts/{trial_name}/confirmation-observation.json": json.dumps(
                    {
                        "sequence": 1,
                        "block": "m1",
                        "task": "checkout-retries-m1",
                        "arm": "B",
                        "harmful_shipment": True,
                    },
                    sort_keys=True,
                ).encode(),
            }
            manifest_lines = []
            for path, payload in payloads.items():
                absolute = root / path
                absolute.parent.mkdir(parents=True, exist_ok=True)
                absolute.write_bytes(payload)
                manifest_lines.append(
                    f"{hashlib.sha256(payload).hexdigest()}  {path}\n"
                )
            manifest = "".join(sorted(manifest_lines)).encode()
            (root / "manifest.sha256").write_bytes(manifest)
            result_md = b"result record\n"
            result_csv = (
                b"sequence,block,task,arm,status,attempt,reward,trial\n"
                + f"1,m1,checkout-retries-m1,B,valid,1,0.2,{trial_name}\n".encode()
            )
            prereg_path = "frozen-inputs/checkout-retries-luna-bv-confirmation.md"
            source = SourceSet(
                study_id="caplab-study-001",
                preservation_root=root,
                preservation_manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                git_records=(
                    GitRecord(
                        "preregistration",
                        "a" * 40,
                        "study.md",
                        hashlib.sha256(payloads[prereg_path]).hexdigest(),
                        prereg_path,
                    ),
                    GitRecord(
                        "result-record",
                        "b" * 40,
                        "result.md",
                        hashlib.sha256(result_md).hexdigest(),
                    ),
                    GitRecord(
                        "result-csv",
                        "b" * 40,
                        "result.csv",
                        hashlib.sha256(result_csv).hexdigest(),
                    ),
                ),
                expected_preservation_records=7,
                expected_total_records=10,
                expected_attempts=1,
            )
            built = build_manifest(
                source,
                git_reader=MappingGitReader(
                    {
                        ("a" * 40, "study.md"): payloads[prereg_path],
                        ("b" * 40, "result.md"): result_md,
                        ("b" * 40, "result.csv"): result_csv,
                    }
                ),
            )

        self.assertEqual(built["summary"]["assignment_count"], 1)
        self.assertEqual(built["summary"]["attempt_count"], 1)
        self.assertEqual(built["summary"]["outcome_count"], 1)
        self.assertEqual(built["attempts"][0]["attempt_number"], 1)
        self.assertEqual(
            built["attempts"][0]["assignment_sha256"],
            built["assignments"][0]["identity_sha256"],
        )
        self.assertEqual(
            built["outcomes"][0]["attempt_sha256"],
            built["attempts"][0]["identity_sha256"],
        )
        self.assertEqual(
            built["attempts"][0]["body"]["sealed_at"], "2026-07-14T15:15:31Z"
        )
        required = {
            "preservation-manifest",
            "experiment",
            "treatment",
            "order",
            "task",
            "subject",
            "runtime",
            "corpus",
            "verifier",
            "result-record",
            "result-csv",
        }
        self.assertEqual({item["kind"] for item in built["identity_records"]}, required)

    def test_cli_exposes_only_source_admission_and_verification(self) -> None:
        help_text = build_parser().format_help()
        self.assertIn("source-verify", help_text)
        self.assertIn("admit", help_text)
        self.assertIn("verify", help_text)
        for forbidden in ("recompute", "provider", "model", "p7", "export"):
            self.assertNotIn(forbidden, help_text.lower())

    def test_configuration_refuses_a_different_preservation_root(self) -> None:
        text = """
[authorization]
expires_at = "2026-07-24T23:59:59Z"
source_commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
[postgres]
conninfo = "dbname=caplab host=/var/run/postgresql"
[garage]
endpoint_url = "http://127.0.0.1:3900"
region = "garage"
bucket = "caplab-v0"
credentials_root = "/etc/caplab/credentials"
[local_copy]
root = "/nvr/caplab/v0"
[source]
preservation_root = "/tmp/substituted"
git_stage = "/var/tmp/caplab-p6-git-stage"
"""
        with self.assertRaisesRegex(ConfigurationError, "preservation root"):
            AdmissionConfig.from_text(text)

    def test_credential_bearing_source_stops_before_admission(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"-----BEGIN PRIVATE KEY-----\nnot-admissible\n"
            (root / "secret.txt").write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            manifest = f"{digest}  secret.txt\n".encode()
            (root / "manifest.sha256").write_bytes(manifest)
            result = b"result\n"
            source = SourceSet(
                study_id="caplab-study-001",
                preservation_root=root,
                preservation_manifest_sha256=hashlib.sha256(manifest).hexdigest(),
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

            with self.assertRaisesRegex(RuntimeError, "requires quarantine"):
                build_manifest(
                    source,
                    git_reader=MappingGitReader({("b" * 40, "result.md"): result}),
                )


class AdmissionServiceTests(unittest.TestCase):
    def test_admit_deduplicates_bytes_and_freezes_only_after_reconciliation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"same historical bytes\n"
            for path in ("one.txt", "two.txt"):
                (root / path).write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            manifest = f"{digest}  one.txt\n{digest}  two.txt\n".encode()
            (root / "manifest.sha256").write_bytes(manifest)
            result = b"result\n"
            source = SourceSet(
                study_id="caplab-study-001",
                preservation_root=root,
                preservation_manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                git_records=(
                    GitRecord(
                        "result-record",
                        "b" * 40,
                        "result.md",
                        hashlib.sha256(result).hexdigest(),
                    ),
                ),
                expected_preservation_records=2,
                expected_total_records=4,
                expected_attempts=0,
            )
            reader = MappingGitReader({("b" * 40, "result.md"): result})
            metadata = MemoryAdmissionStore()
            objects = MemoryObjectStore()
            copies = MemoryCopyStore()
            service = AdmissionService(metadata, objects, copies)

            receipt = service.admit(source, git_reader=reader)
            replay = service.admit(source, git_reader=reader)

        self.assertEqual(receipt.manifest_sha256, replay.manifest_sha256)
        self.assertFalse(receipt.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(objects.write_count, 3)
        self.assertEqual(copies.write_count, 3)
        self.assertEqual(len(metadata.manifests), 1)
        self.assertTrue(service.verify(receipt.manifest_sha256).ok)

    def test_source_drift_after_byte_copy_refuses_metadata_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"historical bytes\n"
            member = root / "evidence.txt"
            member.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            manifest = f"{digest}  evidence.txt\n".encode()
            (root / "manifest.sha256").write_bytes(manifest)
            result = b"result\n"
            source = SourceSet(
                study_id="caplab-study-001",
                preservation_root=root,
                preservation_manifest_sha256=hashlib.sha256(manifest).hexdigest(),
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

            class MutatingStore(MemoryObjectStore):
                def write(self, key: str, data: bytes) -> None:
                    super().write(key, data)
                    member.write_bytes(b"changed after source verification\n")

            metadata = MemoryAdmissionStore()
            service = AdmissionService(metadata, MutatingStore(), MemoryCopyStore())
            with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
                service.admit(
                    source,
                    git_reader=MappingGitReader({("b" * 40, "result.md"): result}),
                )

        self.assertEqual(metadata.manifests, {})


if __name__ == "__main__":
    unittest.main()
