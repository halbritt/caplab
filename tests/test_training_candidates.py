"""Behavioral contracts for governed Study 001 training candidates."""

import unittest

from caplab.recomputation.service import RecomputationService
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.training_candidates import CandidateManifestMismatch, build_candidate_manifest
from caplab.training_candidates.__main__ import build_parser
from tests.test_recomputation import (
    SyntheticRegistrationStore,
    rehash_registration,
    synthetic_study,
)


def candidate_fixture() -> tuple[dict[str, object], dict[str, object]]:
    registration, objects, copies = synthetic_study()
    recomputation = RecomputationService(
        SyntheticRegistrationStore(registration), objects, copies
    ).recompute(registration["manifest_sha256"], implementation_commit="a" * 40)
    return recomputation, registration


class TrainingCandidateManifestTests(unittest.TestCase):
    def test_sealed_lineage_produces_candidates_without_eligibility(self) -> None:
        recomputation, registration = candidate_fixture()

        first = build_candidate_manifest(recomputation, registration)
        replay = build_candidate_manifest(recomputation, registration)

        self.assertEqual(first, replay)
        self.assertEqual(first["schema_version"], "caplab-training-candidate-manifest/1")
        self.assertEqual(first["assertion_type"], "candidate-manifest")
        self.assertEqual(first["status"], "eligibility-unavailable")
        self.assertEqual(len(first["candidates"]), 20)
        self.assertEqual(first["exclusions"], [])
        self.assertEqual(
            {candidate["split_group"] for candidate in first["candidates"]},
            {"checkout-retries-study-001"},
        )
        for candidate in first["candidates"]:
            self.assertEqual(candidate["candidate_status"], "derived-not-eligible")
            self.assertEqual(
                candidate["human_disposition"]["recorded_value"], "not-recorded"
            )
            self.assertEqual(
                candidate["leakage_review"], "unavailable-pending-human-eligibility"
            )
        body = {key: value for key, value in first.items() if key != "manifest_sha256"}
        self.assertEqual(first["manifest_sha256"], sha256_hex(canonical_json(body)))

    def test_verifier_identity_that_omits_an_outcome_is_refused(self) -> None:
        registration, objects, copies = synthetic_study()
        verifier = next(
            item for item in registration["identity_records"] if item["kind"] == "verifier"
        )
        verifier["body"]["outcome_record_sha256"].pop()
        verifier["identity_sha256"] = sha256_hex(canonical_json(verifier["body"]))
        rehash_registration(registration)
        recomputation = RecomputationService(
            SyntheticRegistrationStore(registration), objects, copies
        ).recompute(registration["manifest_sha256"], implementation_commit="a" * 40)

        with self.assertRaisesRegex(CandidateManifestMismatch, "verifier lineage"):
            build_candidate_manifest(recomputation, registration)

    def test_cli_is_a_file_to_candidate_manifest_boundary(self) -> None:
        help_text = build_parser().format_help().lower()

        self.assertIn("--recomputation", help_text)
        self.assertIn("--registration", help_text)
        for forbidden in ("--eligible", "--export", "--model", "--accept"):
            self.assertNotIn(forbidden, help_text)

    def test_missing_human_disposition_lineage_excludes_the_candidate(self) -> None:
        registration, objects, copies = synthetic_study()
        outcome = registration["outcomes"][0]
        del outcome["body"]["human_disposition"]
        outcome["identity_sha256"] = sha256_hex(canonical_json(outcome["body"]))
        rehash_registration(registration)
        recomputation = RecomputationService(
            SyntheticRegistrationStore(registration), objects, copies
        ).recompute(registration["manifest_sha256"], implementation_commit="a" * 40)

        result = build_candidate_manifest(recomputation, registration)

        self.assertEqual(len(result["candidates"]), 19)
        self.assertEqual(
            result["exclusions"][0]["reason"],
            "incomplete-or-ambiguous-human-lineage",
        )


if __name__ == "__main__":
    unittest.main()
