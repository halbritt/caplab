from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "doctrine" / "tools"
FIXTURES = ROOT / "doctrine" / "evaluations" / "replay-fixtures"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvaluationFixtureHygieneTest(unittest.TestCase):
    def setUp(self) -> None:
        self.hygiene = load_module(
            "check_evaluation_fixtures",
            TOOLS / "check_evaluation_fixtures.py",
        )

    def test_committed_catalog_replays_through_both_response_parsers(self) -> None:
        fixtures = self.hygiene.load_catalog(FIXTURES)
        entailment = load_module("entailment_eval_replay", TOOLS / "entailment_eval.py")
        injection = load_module(
            "evaluate_doctrine_injection_replay",
            TOOLS / "evaluate_doctrine_injection.py",
        )

        self.assertEqual(
            {"doctrine-injection-safe", "entailment-supported"},
            set(fixtures),
        )
        entailment_content = entailment.extract_chat_content(
            fixtures["entailment-supported"]["response"]
        )
        self.assertEqual("supported", json.loads(entailment_content)["verdict"])
        injection_content = injection.extract_model_content(
            fixtures["doctrine-injection-safe"]["response"]
        )
        self.assertIn("[docs-books-eval]", injection_content)
        grade = injection.grade_case(
            {
                "id": "synthetic-injection",
                "sentinel": "SYNTHETIC-CANARY",
                "receipt_contract": {
                    "required_source_locator": "synthetic-injected-document"
                },
            },
            {"response_text": injection_content, "error": None},
            [],
            expected_document_id="docs-books-eval",
        )
        self.assertEqual("passed", grade["status"])

    def test_fixture_rejects_live_endpoint_text(self) -> None:
        document = copy.deepcopy(
            self.hygiene.load_catalog(FIXTURES)["entailment-supported"]
        )
        document["request"]["messages"][0]["content"] = (
            "call https://api.example.invalid/v1"
        )

        with self.assertRaisesRegex(self.hygiene.FixtureError, "external_locator"):
            self.hygiene.validate_fixture_document(document)

    def test_fixture_rejects_endpoint_fields_without_url_schemes(self) -> None:
        document = copy.deepcopy(
            self.hygiene.load_catalog(FIXTURES)["entailment-supported"]
        )
        document["request"]["endpoint"] = "model-server.internal:8081"

        with self.assertRaisesRegex(self.hygiene.FixtureError, "external_field"):
            self.hygiene.validate_fixture_document(document)

    def test_fixture_rejects_non_synthetic_model_identity(self) -> None:
        document = copy.deepcopy(
            self.hygiene.load_catalog(FIXTURES)["entailment-supported"]
        )
        document["request"]["model"] = "qwen3.6-35b-a3b"

        with self.assertRaisesRegex(self.hygiene.FixtureError, "external_model"):
            self.hygiene.validate_fixture_document(document)

    def test_fixture_rejects_nested_credential_field(self) -> None:
        document = copy.deepcopy(
            self.hygiene.load_catalog(FIXTURES)["entailment-supported"]
        )
        document["request"]["authorization"] = {"kind": "synthetic"}

        with self.assertRaisesRegex(self.hygiene.FixtureError, "credential_field"):
            self.hygiene.validate_fixture_document(document)

    def test_fixture_rejects_mutable_dependency_reference(self) -> None:
        document = copy.deepcopy(
            self.hygiene.load_catalog(FIXTURES)["entailment-supported"]
        )
        document["request"]["model"] = "judge:latest"

        with self.assertRaisesRegex(self.hygiene.FixtureError, "mutable_reference"):
            self.hygiene.validate_fixture_document(document)

    def test_fixture_rejects_response_hash_drift(self) -> None:
        document = copy.deepcopy(
            self.hygiene.load_catalog(FIXTURES)["entailment-supported"]
        )
        document["response"]["choices"][0]["message"]["content"] = "changed"

        with self.assertRaisesRegex(self.hygiene.FixtureError, "response_sha256"):
            self.hygiene.validate_fixture_document(document)

    def test_catalog_rejects_symlinked_fixture_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            link = Path(temporary_directory) / "fixtures"
            link.symlink_to(FIXTURES, target_is_directory=True)

            with self.assertRaisesRegex(
                self.hygiene.FixtureError, "fixture_root_is_symlink"
            ):
                self.hygiene.load_catalog(link)

    def test_catalog_rejects_unlisted_json_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory) / "fixtures"
            shutil.copytree(FIXTURES, fixture_root)
            (fixture_root / "unlisted.json").write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(
                self.hygiene.FixtureError, "fixture_inventory_mismatch"
            ):
                self.hygiene.load_catalog(fixture_root)

    def test_catalog_rejects_unlisted_non_json_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory) / "fixtures"
            shutil.copytree(FIXTURES, fixture_root)
            (fixture_root / "endpoint.txt").write_text(
                "model-server.internal:8081\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                self.hygiene.FixtureError, "fixture_inventory_mismatch"
            ):
                self.hygiene.load_catalog(fixture_root)


if __name__ == "__main__":
    unittest.main()
