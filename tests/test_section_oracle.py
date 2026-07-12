"""Release-gate oracle: map-aware extraction must recover full cited sections.

The frontier review (doctrine/evaluations/entailment/frontier-review.jsonl)
judged 17 screening flags to be artifacts of section extraction truncated at
conversion-flattened headings, quoting evidence read from the full chapters.
Two further human audits identified the same artifact on FSA sections. With
the tracked section maps in place, every one of those evidence quotes must be
contained in the freshly extracted section for the flag's locator.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doctrine" / "tools"))

import entailment_eval  # noqa: E402

FRONTIER = ROOT / "doctrine/evaluations/entailment/frontier-review.jsonl"
RESULTS = ROOT / "doctrine/evaluations/entailment/results.jsonl"
MAP_DIR = ROOT / "doctrine/section-maps"

# The two human-audited artifact flags predate the frontier review; expected
# phrases were verified against the full chapters during remediation.
AUDIT_ARTIFACT_CASES = [
    (
        "books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/"
        '024-chapter-18-choosing-the-appropriate-architecture-style.md :: '
        'Shifting "Fashion" in Architecture',
        "when to follow and when to make exceptions",
    ),
    (
        "books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/"
        "015-chapter-9-foundations.md :: Other Distributed Considerations",
        "Transactional sagas",
    ),
]


def quote_supported(quote: str, section_text: str) -> bool:
    outcome = {"verdict": "supported", "evidence_quote": quote}
    verified = entailment_eval.verify_evidence_quote(outcome, section_text)
    return verified["verdict"] == "supported"


class SectionOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not MAP_DIR.is_dir() or not any(MAP_DIR.glob("*.yaml")):
            raise unittest.SkipTest(
                "section maps not built yet (doctrine/section-maps is empty); "
                "run doctrine/tools/build_section_map.py --write"
            )
        cls.locator_by_key = {}
        for line in RESULTS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                cls.locator_by_key[record.get("key")] = record.get("locator")

    def test_frontier_artifact_quotes_recovered(self):
        reviews = [
            json.loads(line)
            for line in FRONTIER.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        artifacts = [
            review
            for review in reviews
            if review.get("local_verdict_assessment") == "artifact"
        ]
        self.assertEqual(17, len(artifacts))
        failures = []
        for review in artifacts:
            locator = self.locator_by_key.get(review["key"])
            self.assertIsNotNone(locator, review["concept_id"])
            resolution = entailment_eval.resolve_locator(ROOT, locator)
            self.assertIsNone(resolution.error, locator)
            if not quote_supported(
                review["evidence_quote"], resolution.section_text or ""
            ):
                failures.append((review["concept_id"], locator))
        self.assertEqual([], failures)

    def test_audited_artifact_sections_recovered(self):
        for locator, phrase in AUDIT_ARTIFACT_CASES:
            resolution = entailment_eval.resolve_locator(ROOT, locator)
            self.assertIsNone(resolution.error, locator)
            self.assertTrue(
                quote_supported(phrase, resolution.section_text or ""),
                f"{phrase!r} not recovered for {locator}",
            )


if __name__ == "__main__":
    unittest.main()
