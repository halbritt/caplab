import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSERTION_CLI = ROOT / "doctrine" / "tools" / "validate_assertions.py"
SCENARIO_CLI = ROOT / "doctrine" / "tools" / "run_scenario.py"
IMPACT_CLI = ROOT / "doctrine" / "tools" / "dependency_impact.py"


class AssertionValidationTests(unittest.TestCase):
    def run_validator(self, artifact):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "artifact.json"
            artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(ASSERTION_CLI), str(artifact_path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_observation_without_evidence_is_rejected(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "observed-check-failure",
                        "type": "observation",
                        "text": "The repository check exited with status 1.",
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("observation_requires_evidence", result.stderr)

    def test_assertion_artifact_version_and_types_are_closed(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/99",
                "assertions": [
                    {
                        "id": "unsupported-claim",
                        "type": "fact",
                        "text": "This type is outside the ubiquitous language.",
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("unsupported_schema_version", result.stderr)
        self.assertIn("unsupported_assertion_type: fact", result.stderr)

    def test_inference_without_rivals_is_rejected(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "observed-check-failure",
                        "type": "observation",
                        "text": "The repository check exited with status 1.",
                        "evidence": ["run-17:exit-status"],
                    },
                    {
                        "id": "stale-index",
                        "type": "inference",
                        "text": "The corpus index may be stale.",
                        "depends_on": ["observed-check-failure"],
                    },
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("inference_requires_rivals", result.stderr)

    def test_decision_without_owner_and_authority_is_rejected(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "regenerate-index",
                        "type": "decision",
                        "text": "Regenerate the corpus index.",
                        "depends_on": ["inspect-before-regeneration"],
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("decision_requires_owner", result.stderr)
        self.assertIn("decision_requires_authority", result.stderr)

    def test_verification_cannot_promote_a_recommendation(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "regenerate-index",
                        "type": "recommendation",
                        "text": "Regenerate the corpus index.",
                        "alternatives": ["retain the current index"],
                        "tradeoffs": ["regeneration may discard manual edits"],
                    },
                    {
                        "id": "index-verified",
                        "type": "verification",
                        "text": "The regenerated index passed its check.",
                        "depends_on": ["regenerate-index"],
                        "criteria": ["repository check exits successfully"],
                        "evidence": ["run-18:exit-status"],
                    },
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("verification_requires_execution_dependency", result.stderr)

    def test_acceptance_requires_verification_and_acceptance_authority(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "accepted-index",
                        "type": "acceptance",
                        "text": "The corpus index is accepted.",
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("acceptance_requires_verification_dependency", result.stderr)
        self.assertIn("acceptance_requires_owner", result.stderr)
        self.assertIn("acceptance_requires_authority", result.stderr)

    def test_execution_requires_authorization_dependency(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "select-regeneration",
                        "type": "decision",
                        "text": "Regenerate the output.",
                        "owner": "repository owner",
                        "authority": "explicit selection authority",
                    },
                    {
                        "id": "regenerated-output",
                        "type": "execution",
                        "text": "The output was regenerated.",
                        "depends_on": ["select-regeneration"],
                    },
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("execution_requires_authorization_dependency", result.stderr)

    def test_assertion_ids_and_dependencies_must_be_resolvable(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "same-id",
                        "type": "observation",
                        "text": "First observation.",
                        "evidence": ["source:a"],
                    },
                    {
                        "id": "same-id",
                        "type": "inference",
                        "text": "An inference.",
                        "depends_on": ["missing-observation"],
                        "rivals": ["Another explanation."],
                    },
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("duplicate_assertion_id: same-id", result.stderr)
        self.assertIn("unknown_dependency: missing-observation", result.stderr)

    def test_authorization_requires_owner_authority_and_scope(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "authorize-regeneration",
                        "type": "authorization",
                        "text": "Regeneration is authorized.",
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("authorization_requires_owner", result.stderr)
        self.assertIn("authorization_requires_authority", result.stderr)
        self.assertIn("authorization_requires_scope", result.stderr)

    def test_recommendation_requires_alternatives_and_tradeoffs(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "recommend-regeneration",
                        "type": "recommendation",
                        "text": "Regenerate the output.",
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("recommendation_requires_alternatives", result.stderr)
        self.assertIn("recommendation_requires_tradeoffs", result.stderr)

    def test_verification_requires_criteria_and_evidence(self):
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/1",
                "assertions": [
                    {
                        "id": "authorize-regeneration",
                        "type": "authorization",
                        "text": "Regeneration is authorized.",
                        "owner": "repository owner",
                        "authority": "explicit authority",
                        "scope": ["affected output"],
                    },
                    {
                        "id": "regenerated-output",
                        "type": "execution",
                        "text": "The output was regenerated.",
                        "depends_on": ["authorize-regeneration"],
                    },
                    {
                        "id": "verified-output",
                        "type": "verification",
                        "text": "The output is verified.",
                        "depends_on": ["regenerated-output"],
                    },
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("verification_requires_criteria", result.stderr)
        self.assertIn("verification_requires_evidence", result.stderr)


class ScenarioReplayTests(unittest.TestCase):
    def run_scenario(self, scenario, result_artifact):
        with tempfile.TemporaryDirectory() as temp_dir:
            scenario_path = Path(temp_dir) / "scenario.json"
            result_path = Path(temp_dir) / "result.json"
            scenario_path.write_text(json.dumps(scenario), encoding="utf-8")
            result_path.write_text(json.dumps(result_artifact), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(SCENARIO_CLI),
                    str(scenario_path),
                    str(result_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_withdrawn_authority_forbids_decision_assertions(self):
        result = self.run_scenario(
            {
                "schema_version": "doctrine-scenario/1",
                "id": "authorization-withdrawn",
                "authority": {"authorization_granted": False},
                "evidence": [],
                "expected": {
                    "required_assertion_types": ["recommendation"],
                    "forbidden_assertion_types": [
                        "decision",
                        "authorization",
                        "execution",
                    ],
                    "required_retrieval_ids": [],
                    "forbidden_retrieval_ids": [],
                },
            },
            {
                "schema_version": "scenario-result/1",
                "retrieved_evidence_ids": [],
                "assertions": [
                    {
                        "id": "recommend-inspection",
                        "type": "recommendation",
                        "text": "Inspect the source hashes.",
                        "alternatives": ["take no action"],
                        "tradeoffs": ["inspection costs time"],
                    },
                    {
                        "id": "decide-regeneration",
                        "type": "decision",
                        "text": "Regenerate the output.",
                        "owner": "agent",
                        "authority": "repository access",
                    },
                ],
            },
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("forbidden_assertion_type: decision", result.stderr)

    def test_required_evidence_and_assertion_types_must_be_present(self):
        result = self.run_scenario(
            {
                "schema_version": "doctrine-scenario/1",
                "id": "authorized-regeneration",
                "authority": {"authorization_granted": True},
                "evidence": [{"id": "source-hash", "provenance": "source.json"}],
                "expected": {
                    "required_assertion_types": ["observation", "decision"],
                    "forbidden_assertion_types": [],
                    "required_retrieval_ids": ["source-hash"],
                    "forbidden_retrieval_ids": ["unrelated-evidence"],
                },
            },
            {
                "schema_version": "scenario-result/1",
                "retrieved_evidence_ids": [],
                "assertions": [],
            },
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("missing_assertion_type: observation", result.stderr)
        self.assertIn("missing_assertion_type: decision", result.stderr)
        self.assertIn("missing_retrieval: source-hash", result.stderr)


class DependencyImpactTests(unittest.TestCase):
    def test_changed_source_rebuilds_only_its_dependents(self):
        manifest = {
            "schema_version": "dependency-manifest/1",
            "nodes": [
                {"id": "source-a", "kind": "source", "content_hash": "sha256:a"},
                {"id": "chapter-a", "kind": "chapter", "content_hash": "sha256:b"},
                {"id": "concept-a", "kind": "concept", "content_hash": "sha256:c"},
                {"id": "prompt-a", "kind": "prompt", "content_hash": "sha256:d"},
                {"id": "evaluation-a", "kind": "evaluation", "content_hash": "sha256:e"},
                {"id": "source-b", "kind": "source", "content_hash": "sha256:f"},
                {"id": "chapter-b", "kind": "chapter", "content_hash": "sha256:g"},
            ],
            "edges": [
                {"consumer": "chapter-a", "provider": "source-a", "relation": "derives_from"},
                {"consumer": "concept-a", "provider": "chapter-a", "relation": "derives_from"},
                {"consumer": "prompt-a", "provider": "concept-a", "relation": "packages"},
                {"consumer": "evaluation-a", "provider": "prompt-a", "relation": "evaluates"},
                {"consumer": "chapter-b", "provider": "source-b", "relation": "derives_from"},
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(IMPACT_CLI),
                    str(manifest_path),
                    "--changed",
                    "source-a",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        impact = json.loads(result.stdout)
        self.assertEqual(
            ["chapter-a", "concept-a", "prompt-a"], impact["rebuild_required"]
        )
        self.assertEqual(["evaluation-a"], impact["reverification_required"])
        self.assertEqual(["chapter-b", "source-b"], impact["unaffected"])


class CheckedInScaffoldingTests(unittest.TestCase):
    def test_checked_in_authority_canaries_pass(self):
        fixture_root = ROOT / "doctrine" / "evaluations" / "fixtures"
        scenarios = sorted(fixture_root.glob("authority-*/scenario.json"))
        self.assertEqual(2, len(scenarios))

        for scenario_path in scenarios:
            with self.subTest(scenario=scenario_path.parent.name):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCENARIO_CLI),
                        str(scenario_path),
                        str(scenario_path.with_name("result.json")),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)

    def test_portable_contracts_are_versioned_json_schemas(self):
        schema_paths = sorted((ROOT / "doctrine" / "runtime").glob("*.schema.json"))
        schema_paths.extend(
            [
                ROOT / "doctrine" / "evaluations" / "result.schema.json",
                ROOT / "doctrine" / "evaluations" / "scenario.schema.json",
            ]
        )
        self.assertEqual(6, len(schema_paths))

        for schema_path in schema_paths:
            with self.subTest(schema=schema_path.name):
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    "https://json-schema.org/draft/2020-12/schema",
                    schema["$schema"],
                )
                self.assertTrue(schema["$id"].startswith("https://books.local/"))
                self.assertEqual("object", schema["type"])

    def test_checked_in_dependency_fixture_has_minimal_blast_radius(self):
        manifest_path = (
            ROOT
            / "doctrine"
            / "evaluations"
            / "fixtures"
            / "dependency-impact"
            / "manifest.json"
        )
        result = subprocess.run(
            [
                sys.executable,
                str(IMPACT_CLI),
                str(manifest_path),
                "--changed",
                "source-a",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        impact = json.loads(result.stdout)
        self.assertEqual(
            ["chapter-a", "concept-a", "prompt-a"], impact["rebuild_required"]
        )
        self.assertEqual(["evaluation-a"], impact["reverification_required"])
        self.assertEqual(["chapter-b", "source-b"], impact["unaffected"])


if __name__ == "__main__":
    unittest.main()
