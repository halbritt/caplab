"""Behavioral contracts for CAPLAB Study 001 recomputation."""

import csv
import io
import json
import unittest
from datetime import UTC, datetime

from caplab.recomputation.analysis import analyze_mutant_blocks
from caplab.recomputation.__main__ import ROLE_BY_COMMAND, build_parser
from caplab.recomputation.config import RecomputationConfig
from caplab.recomputation.service import RecomputationMismatch, RecomputationService
from caplab.runtime.adapters.memory import MemoryCopyStore, MemoryObjectStore
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.runtime.models import object_key


class SyntheticRegistrationStore:
    def __init__(self, manifest: dict[str, object]) -> None:
        self.manifest = manifest
        self.locators = {
            record["content_sha256"]: {
                "object_key": record["object_key"],
                "local_copy_key": record["local_copy_key"],
                "byte_count": record["byte_count"],
            }
            for record in manifest["records"]
        }

    def get(self, manifest_sha256: str) -> dict[str, object] | None:
        if manifest_sha256 != self.manifest["manifest_sha256"]:
            return None
        return json.loads(canonical_json(self.manifest).decode("utf-8"))

    def locator(self, content_sha256: str) -> dict[str, object] | None:
        retained = self.locators.get(content_sha256)
        return None if retained is None else dict(retained)


def synthetic_study() -> tuple[
    dict[str, object], MemoryObjectStore, MemoryCopyStore
]:
    assignments: list[dict[str, object]] = []
    attempts: list[dict[str, object]] = []
    outcomes: list[dict[str, object]] = []
    records: list[dict[str, object]] = []
    csv_rows: list[dict[str, str]] = []
    objects = MemoryObjectStore()
    copies = MemoryCopyStore()
    sequence = 0
    blocks = tuple(f"m{index}" for index in range(1, 9)) + ("c1", "c2")
    for block in blocks:
        task = "checkout-retries-m1" if block.startswith("m") else "checkout-retries-v2"
        for condition in ("B", "V"):
            sequence += 1
            harmful = block.startswith("m") and condition == "B"
            clean_guard = block.startswith("c")
            assignment_body = {
                "study_id": "caplab-study-001",
                "sequence": sequence,
                "block": block,
                "task": task,
                "condition": condition,
            }
            assignment_sha256 = sha256_hex(canonical_json(assignment_body))
            assignments.append(
                {
                    "kind": "trial-assignment",
                    "identity_sha256": assignment_sha256,
                    "sequence": sequence,
                    "block": block,
                    "task": task,
                    "condition": condition,
                    "body": assignment_body,
                }
            )
            observation = {
                "schema_version": "checkout-retries-luna-bv-observation/1",
                "sequence": sequence,
                "block": block,
                "task": task,
                "arm": condition,
                "harmful_shipment": harmful,
                "clean_guard_passed": clean_guard,
                "errors": {
                    "capture_exit": 0,
                    "timed_out": False,
                    "verifier_error": False,
                    "observer_error": None,
                },
            }
            observation_bytes = canonical_json(observation)
            observation_sha256 = sha256_hex(observation_bytes)
            key = object_key(observation_sha256)
            record_id = f"outcome-{sequence:02d}"
            records.append(
                {
                    "record_id": record_id,
                    "source_kind": "preservation-member",
                    "source_path": f"attempts/s{sequence:02d}/confirmation-observation.json",
                    "content_sha256": observation_sha256,
                    "byte_count": len(observation_bytes),
                    "object_key": key,
                    "local_copy_key": key,
                    "disposition": "restricted-admission",
                }
            )
            objects.objects[key] = observation_bytes
            copies.copies[key] = observation_bytes
            attempt_body = {
                "assignment_sha256": assignment_sha256,
                "attempt_number": 1,
            }
            attempt_sha256 = sha256_hex(canonical_json(attempt_body))
            attempts.append(
                {
                    "kind": "attempt",
                    "identity_sha256": attempt_sha256,
                    "assignment_sha256": assignment_sha256,
                    "attempt_number": 1,
                    "body": attempt_body,
                }
            )
            outcome_body = {
                "attempt_sha256": attempt_sha256,
                "outcome_record_sha256": observation_sha256,
                "historical_observation": observation,
            }
            outcomes.append(
                {
                    "kind": "mechanical-outcome",
                    "identity_sha256": sha256_hex(canonical_json(outcome_body)),
                    "attempt_sha256": attempt_sha256,
                    "body": outcome_body,
                }
            )
            csv_rows.append(
                {
                    "sequence": str(sequence),
                    "block": block,
                    "task": task,
                    "arm": condition,
                    "status": "valid",
                    "attempt": "1",
                    "harmful_shipment": str(harmful).lower(),
                    "clean_guard_passed": str(clean_guard).lower(),
                    "capture_exit": "0",
                    "timed_out": "false",
                    "verifier_error": "false",
                    "observer_error": "",
                }
            )
    fields = tuple(csv_rows[0])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(csv_rows)
    csv_bytes = stream.getvalue().encode("utf-8")
    csv_sha256 = sha256_hex(csv_bytes)
    csv_key = object_key(csv_sha256)
    records.append(
        {
            "record_id": "result-csv",
            "source_kind": "git-record",
            "source_path": "selected-result.csv",
            "content_sha256": csv_sha256,
            "byte_count": len(csv_bytes),
            "object_key": csv_key,
            "local_copy_key": csv_key,
            "disposition": "restricted-admission",
        }
    )
    objects.objects[csv_key] = csv_bytes
    copies.copies[csv_key] = csv_bytes
    manifest_body: dict[str, object] = {
        "schema_version": "caplab-study-admission/1",
        "study_id": "caplab-study-001",
        "records": records,
        "assignments": assignments,
        "attempts": attempts,
        "outcomes": outcomes,
        "summary": {
            "record_count": len(records),
            "unique_content_count": len(records),
            "assignment_count": 20,
            "attempt_count": 20,
            "outcome_count": 20,
        },
    }
    manifest = dict(manifest_body)
    manifest["manifest_sha256"] = sha256_hex(canonical_json(manifest_body))
    return manifest, objects, copies


def rehash_registration(registration: dict[str, object]) -> None:
    body = {
        key: value for key, value in registration.items() if key != "manifest_sha256"
    }
    registration["manifest_sha256"] = sha256_hex(canonical_json(body))


def replace_result_csv(
    registration: dict[str, object],
    objects: MemoryObjectStore,
    copies: MemoryCopyStore,
    transform: object,
) -> None:
    record = next(
        record
        for record in registration["records"]
        if record["record_id"] == "result-csv"
    )
    old_key = record["object_key"]
    payload = objects.objects[old_key]
    replacement = transform(payload)
    digest = sha256_hex(replacement)
    key = object_key(digest)
    record.update(
        {
            "content_sha256": digest,
            "byte_count": len(replacement),
            "object_key": key,
            "local_copy_key": key,
        }
    )
    objects.objects[key] = replacement
    copies.copies[key] = replacement
    rehash_registration(registration)


class PairedExactAnalysisTests(unittest.TestCase):
    def test_complete_separation_reproduces_the_preregistered_exact_result(self) -> None:
        result = analyze_mutant_blocks(((True, False),) * 8)

        self.assertEqual(
            result,
            {
                "all_mutant_outcomes_defined": True,
                "block_differences": [1] * 8,
                "b_harmful_count": 8,
                "v_harmful_count": 0,
                "mutant_arm_denominator": 8,
                "risk_difference": {"numerator": 8, "denominator": 8},
                "t_observed": 8,
                "permutation_assignments": 256,
                "p_one_sided": {"numerator": 1, "denominator": 256},
                "p_two_sided": {"numerator": 2, "denominator": 256},
                "alpha": {"numerator": 1, "denominator": 20},
                "confirmatory_criterion_met": True,
            },
        )

    def test_any_undefined_mutant_outcome_makes_the_analysis_undefined(self) -> None:
        result = analyze_mutant_blocks(((True, False),) * 7 + ((None, False),))

        self.assertEqual(
            result,
            {
                "all_mutant_outcomes_defined": False,
                "block_differences": None,
                "b_harmful_count": None,
                "v_harmful_count": None,
                "mutant_arm_denominator": 8,
                "risk_difference": None,
                "t_observed": None,
                "permutation_assignments": 0,
                "p_one_sided": None,
                "p_two_sided": None,
                "alpha": {"numerator": 1, "denominator": 20},
                "confirmatory_criterion_met": False,
            },
        )

    def test_tied_blocks_preserve_the_exact_permutation_denominator(self) -> None:
        result = analyze_mutant_blocks(((False, False),) * 8)

        self.assertEqual(result["t_observed"], 0)
        self.assertEqual(result["risk_difference"], {"numerator": 0, "denominator": 8})
        self.assertEqual(result["p_one_sided"], {"numerator": 256, "denominator": 256})
        self.assertEqual(result["p_two_sided"], {"numerator": 256, "denominator": 256})
        self.assertFalse(result["confirmatory_criterion_met"])

    def test_analysis_refuses_any_denominator_other_than_eight_blocks(self) -> None:
        for outcomes in (((True, False),) * 7, ((True, False),) * 9):
            with self.subTest(blocks=len(outcomes)):
                with self.assertRaisesRegex(ValueError, "exactly eight mutant blocks"):
                    analyze_mutant_blocks(outcomes)


class RecomputationServiceTests(unittest.TestCase):
    def test_recompute_binds_registered_bytes_code_and_matching_result(self) -> None:
        registration, objects, copies = synthetic_study()
        service = RecomputationService(
            SyntheticRegistrationStore(registration), objects, copies
        )

        first = service.recompute(
            registration["manifest_sha256"], implementation_commit="a" * 40
        )
        replay = service.recompute(
            registration["manifest_sha256"], implementation_commit="a" * 40
        )

        self.assertEqual(first, replay)
        self.assertEqual(first["schema_version"], "caplab-study-recomputation/1")
        self.assertEqual(first["assertion_type"], "observation")
        self.assertEqual(first["code"]["commit"], "a" * 40)
        self.assertEqual(first["output"]["body"]["primary"]["t_observed"], 8)
        self.assertTrue(
            first["output"]["body"]["primary"]["confirmatory_criterion_met"]
        )
        self.assertEqual(
            first["output"]["normalized_result_sha256"],
            first["historical_comparison"]["normalized_result_sha256"],
        )
        body = {key: value for key, value in first.items() if key != "manifest_sha256"}
        self.assertEqual(first["manifest_sha256"], sha256_hex(canonical_json(body)))
        self.assertEqual(objects.write_count, 0)
        self.assertEqual(copies.write_count, 0)
        self.assertEqual(set(first["broader_claims"].values()), {"unavailable"})

    def test_recompute_accepts_distinct_records_with_one_content_identity(self) -> None:
        registration, objects, copies = synthetic_study()
        duplicate = dict(registration["records"][0])
        duplicate["record_id"] = "duplicate-source-record"
        duplicate["source_path"] = "second/source/path.json"
        registration["records"].append(duplicate)
        registration["summary"]["record_count"] += 1
        rehash_registration(registration)

        result = RecomputationService(
            SyntheticRegistrationStore(registration), objects, copies
        ).recompute(registration["manifest_sha256"], implementation_commit="a" * 40)

        self.assertEqual(result["historical_comparison"]["status"], "byte-identical")

    def test_assignment_metadata_substitution_is_quarantined(self) -> None:
        registration, objects, copies = synthetic_study()
        registration["assignments"][0]["body"]["condition"] = "V"
        rehash_registration(registration)

        with self.assertRaisesRegex(RecomputationMismatch, "identity differs"):
            RecomputationService(
                SyntheticRegistrationStore(registration), objects, copies
            ).recompute(registration["manifest_sha256"], implementation_commit="a" * 40)

    def test_assignment_and_outcome_disagreement_is_quarantined(self) -> None:
        registration, objects, copies = synthetic_study()
        registration["assignments"][0]["condition"] = "V"
        registration["assignments"][0]["body"]["condition"] = "V"
        registration["assignments"][0]["identity_sha256"] = sha256_hex(
            canonical_json(registration["assignments"][0]["body"])
        )
        rehash_registration(registration)

        with self.assertRaisesRegex(RecomputationMismatch, "assignment"):
            RecomputationService(
                SyntheticRegistrationStore(registration), objects, copies
            ).recompute(registration["manifest_sha256"], implementation_commit="a" * 40)

    def test_registered_locator_substitution_is_quarantined(self) -> None:
        registration, objects, copies = synthetic_study()
        metadata = SyntheticRegistrationStore(registration)
        digest = registration["records"][0]["content_sha256"]
        metadata.locators[digest]["object_key"] = "objects/substituted"

        with self.assertRaisesRegex(RecomputationMismatch, "locator differs"):
            RecomputationService(metadata, objects, copies).recompute(
                registration["manifest_sha256"], implementation_commit="a" * 40
            )

    def test_missing_or_altered_immutable_bytes_are_quarantined(self) -> None:
        cases = (
            ("missing object", "object", None, "object bytes"),
            ("altered object", "object", b"altered", "object bytes"),
            ("missing copy", "copy", None, "copy bytes"),
            ("altered copy", "copy", b"altered", "copy bytes"),
        )
        for label, store_name, replacement, message in cases:
            with self.subTest(case=label):
                registration, objects, copies = synthetic_study()
                key = registration["records"][0][
                    "object_key" if store_name == "object" else "local_copy_key"
                ]
                store = objects.objects if store_name == "object" else copies.copies
                if replacement is None:
                    del store[key]
                else:
                    store[key] = replacement
                with self.assertRaisesRegex(RecomputationMismatch, message):
                    RecomputationService(
                        SyntheticRegistrationStore(registration), objects, copies
                    ).recompute(
                        registration["manifest_sha256"],
                        implementation_commit="a" * 40,
                    )

    def test_historical_result_mismatch_is_quarantined(self) -> None:
        registration, objects, copies = synthetic_study()
        replace_result_csv(
            registration,
            objects,
            copies,
            lambda payload: payload.replace(b",true,false,0,", b",false,false,0,", 1),
        )

        with self.assertRaisesRegex(RecomputationMismatch, "historical result"):
            RecomputationService(
                SyntheticRegistrationStore(registration), objects, copies
            ).recompute(registration["manifest_sha256"], implementation_commit="a" * 40)


class RecomputationConfigurationTests(unittest.TestCase):
    CONFIG = """
[authorization]
campaign_id = "caplab-study-001-p7-recompute-2026-07-18"
expires_at = "2026-07-25T23:59:59Z"
source_commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
admission_manifest_sha256 = "d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e"
[postgres]
conninfo = "dbname=caplab host=/var/run/postgresql"
[garage]
endpoint_url = "http://127.0.0.1:3900"
region = "garage"
bucket = "caplab-v0"
credentials_root = "/etc/caplab/credentials"
[local_copy]
root = "/nvr/caplab/v0"
"""

    def test_configuration_binds_the_exact_read_only_campaign(self) -> None:
        config = RecomputationConfig.from_text(self.CONFIG)

        self.assertEqual(config.source_commit, "a" * 40)
        self.assertEqual(
            config.admission_manifest_sha256,
            "d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e",
        )
        self.assertEqual(config.postgres_conninfo, "dbname=caplab host=/var/run/postgresql")

    def test_configuration_refuses_campaign_expiry_or_namespace_drift(self) -> None:
        replacements = (
            ("caplab-study-001-p7-recompute-2026-07-18", "other-campaign"),
            ("2026-07-25T23:59:59Z", "2026-07-26T23:59:59Z"),
            ("bucket = \"caplab-v0\"", "bucket = \"other\""),
            ("root = \"/nvr/caplab/v0\"", "root = \"/tmp/substitute\""),
        )
        for old, new in replacements:
            with self.subTest(replacement=new):
                with self.assertRaisesRegex(RuntimeError, "differs"):
                    RecomputationConfig.from_text(self.CONFIG.replace(old, new))

    def test_expired_campaign_cannot_start_recomputation(self) -> None:
        config = RecomputationConfig.from_text(self.CONFIG)

        with self.assertRaisesRegex(RuntimeError, "expired"):
            config.require_active(datetime(2026, 7, 26, tzinfo=UTC))


class RecomputationCliTests(unittest.TestCase):
    def test_cli_exposes_only_read_only_recomputation_to_the_reader(self) -> None:
        help_text = build_parser().format_help().lower()

        self.assertIn("recompute", help_text)
        for forbidden in ("admit", "infer", "eligible", "export", "train", "accept"):
            self.assertNotIn(forbidden, help_text)
        self.assertEqual(ROLE_BY_COMMAND, {"recompute": {"caplab_reader"}})


if __name__ == "__main__":
    unittest.main()
