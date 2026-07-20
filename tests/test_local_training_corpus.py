import json
import tempfile
import unittest
from pathlib import Path

from caplab.review_dissent.instrument import load_calibration_instrument
from caplab.review_dissent.local_training import (
    LocalTrainingContractError,
    build_local_review_prompt,
    build_local_training_corpus,
    grade_local_review,
    parse_local_review_output,
)
from caplab.review_dissent.local_training_live import load_local_training_manifest


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/product/studies/review-dissent-001"


class LocalTrainingCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instrument = load_calibration_instrument(STUDY)

    def test_prompt_exposes_every_task_file_and_exact_schema_without_oracle(self) -> None:
        prompt = build_local_review_prompt(self.instrument, "r01")
        self.assertIn('"critical" or "noncritical"', prompt)
        self.assertIn("ACCEPTANCE.md", prompt)
        self.assertIn("src/migration.py", prompt)
        self.assertIn("tests/test_migration.py", prompt)
        self.assertNotIn("reference_verdict", prompt)
        self.assertNotIn('"truth"', prompt)

    def test_parser_requires_one_exact_schema_valid_json_object(self) -> None:
        valid = {
            "verdict": "clear",
            "findings": [],
            "summary": "The supplied implementation satisfies the contract.",
        }
        self.assertEqual(parse_local_review_output(json.dumps(valid).encode()), valid)
        for bad in (
            b"```json\n{}\n```",
            b'{"verdict":"clear","findings":[],"summary":"ok"} trailing',
            b'{"verdict":"clear","findings":[],"summary":"ok","extra":1}',
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(LocalTrainingContractError):
                    parse_local_review_output(bad)

    def test_grade_binds_tuple_response_and_complete_presented_evidence(self) -> None:
        review = {
            "verdict": "clear",
            "findings": [],
            "summary": "The implementation satisfies the supplied acceptance contract.",
        }
        row = grade_local_review(
            self.instrument,
            cell_id="r01",
            review=review,
            response_sha256="a" * 64,
            tuple_id="local-qwen-35b-a3b-striatum-openai-lane-v1",
        )
        self.assertEqual(row["score"], "1.0")
        self.assertEqual(row["world_id"], "RD-D01")
        self.assertEqual(row["observed_reads"], [
            "ACCEPTANCE.md",
            "src/migration.py",
            "tests/test_migration.py",
        ])
        self.assertEqual(len(row["row_sha256"]), 64)

    def test_corpus_is_family_split_and_excludes_invalid_or_proprietary_rows(self) -> None:
        clean = {
            "verdict": "clear",
            "findings": [],
            "summary": "clear",
        }
        defect = {
            "verdict": "needs_revision",
            "findings": [{
                "severity": "critical",
                "criterion": "AC-1",
                "path": "src/publication.py",
                "summary": "Changed payloads are not written.",
            }],
            "summary": "revision required",
        }
        rows = [
            grade_local_review(self.instrument, cell_id="r01", review=clean,
                               response_sha256="a" * 64, tuple_id="local"),
            grade_local_review(self.instrument, cell_id="r06", review=defect,
                               response_sha256="b" * 64, tuple_id="local"),
        ]
        corpus = build_local_training_corpus(
            self.instrument,
            rows,
            campaign_manifest_sha256="c" * 64,
            export_authority="adr-0048",
        )
        self.assertEqual(corpus["splits"], {
            "train": ["RD-D01"],
            "development": ["RD-D02"],
            "test": ["RD-H01", "RD-H02"],
        })
        self.assertEqual({record["split"] for record in corpus["records"]}, {"train", "development"})
        self.assertTrue(all(record["source_kind"] == "local-open-model" for record in corpus["records"]))
        self.assertEqual(len(corpus["corpus_sha256"]), 64)

    def test_authorized_live_manifest_binds_both_runtime_sources(self) -> None:
        manifest = load_local_training_manifest(
            STUDY / "local-training-instrument.json", ROOT
        )
        self.assertEqual(manifest["limits"]["authorized_calls"], 8)
        self.assertFalse(manifest["limits"]["server_mutation"])


if __name__ == "__main__":
    unittest.main()
