"""Behavioral contracts for the Study 001 capability-profile proposal."""

from pathlib import Path
import unittest

from caplab.profile import ProfileMismatch, build_profile
from caplab.profile.__main__ import build_parser
from caplab.recomputation.service import RecomputationService
from caplab.runtime.canonical import canonical_json, sha256_hex
from tests.test_recomputation import SyntheticRegistrationStore, synthetic_study


ROOT = Path(__file__).parents[1]
CARD = ROOT / (
    "docs/product/capability-cards/"
    "caplab-study-001-explicit-verification-elicited-harm-avoidance.md"
)
SELECTION = ROOT / "docs/decisions/adr-0006-caplab-study-001-capability-card-selection.md"


def recomputation_fixture() -> dict[str, object]:
    registration, objects, copies = synthetic_study()
    return RecomputationService(
        SyntheticRegistrationStore(registration), objects, copies
    ).recompute(registration["manifest_sha256"], implementation_commit="a" * 40)


class CapabilityProfileTests(unittest.TestCase):
    def test_exact_card_and_recomputation_produce_a_bounded_proposal(self) -> None:
        recomputation = recomputation_fixture()

        first = build_profile(recomputation, CARD.read_bytes(), SELECTION.read_bytes())
        replay = build_profile(recomputation, CARD.read_bytes(), SELECTION.read_bytes())

        self.assertEqual(first, replay)
        self.assertEqual(first["schema_version"], "caplab-capability-profile-proposal/1")
        self.assertEqual(first["assertion_type"], "proposal")
        self.assertEqual(first["status"], "pending-human-inference")
        self.assertEqual(
            first["card"]["content_sha256"],
            "8c910c50923340d3586e82ac29fee4614eb72bfefd2347180803e1792b08fad5",
        )
        self.assertEqual(first["result"]["primary"]["t_observed"], 8)
        self.assertEqual(first["scope"]["task_family_count"], 1)
        self.assertEqual(set(first["unavailable_claims"].values()), {"unavailable"})
        body = {key: value for key, value in first.items() if key != "manifest_sha256"}
        self.assertEqual(first["manifest_sha256"], sha256_hex(canonical_json(body)))

    def test_changed_card_bytes_are_refused_before_proposal(self) -> None:
        with self.assertRaisesRegex(ProfileMismatch, "selected review bytes"):
            build_profile(recomputation_fixture(), CARD.read_bytes() + b"\n", SELECTION.read_bytes())

    def test_cli_is_a_file_to_canonical_proposal_boundary(self) -> None:
        help_text = build_parser().format_help().lower()

        for required in ("--recomputation", "--card", "--selection"):
            self.assertIn(required, help_text)
        for forbidden in ("eligible", "export", "train", "accept", "place"):
            self.assertNotIn(forbidden, help_text)

    def test_promoted_upstream_claim_is_refused(self) -> None:
        recomputation = recomputation_fixture()
        recomputation["broader_claims"]["capability_inference"] = "supported"
        body = {
            key: value
            for key, value in recomputation.items()
            if key != "manifest_sha256"
        }
        recomputation["manifest_sha256"] = sha256_hex(canonical_json(body))

        with self.assertRaisesRegex(ProfileMismatch, "claim ceiling"):
            build_profile(recomputation, CARD.read_bytes(), SELECTION.read_bytes())

    def test_changed_mechanical_result_is_refused(self) -> None:
        recomputation = recomputation_fixture()
        normalized = recomputation["output"]["body"]
        normalized["primary"]["t_observed"] = 7
        digest = sha256_hex(canonical_json(normalized))
        recomputation["output"]["normalized_result_sha256"] = digest
        recomputation["historical_comparison"]["normalized_result_sha256"] = digest
        body = {
            key: value
            for key, value in recomputation.items()
            if key != "manifest_sha256"
        }
        recomputation["manifest_sha256"] = sha256_hex(canonical_json(body))

        with self.assertRaisesRegex(ProfileMismatch, "selected Study 001 result"):
            build_profile(recomputation, CARD.read_bytes(), SELECTION.read_bytes())


if __name__ == "__main__":
    unittest.main()
