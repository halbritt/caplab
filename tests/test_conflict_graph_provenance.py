import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
PROJECTOR = ROOT / "doctrine" / "tools" / "sync_concepts_to_graph.py"
GRAPH_SCHEMA = ROOT / "doctrine" / "schemas" / "graph.schema.json"


class ConflictGraphProvenanceTests(unittest.TestCase):
    def make_doctrine(self, concepts, conflicts=None):
        temporary = tempfile.TemporaryDirectory()
        doctrine = Path(temporary.name) / "doctrine"
        (doctrine / "concepts").mkdir(parents=True)
        (doctrine / "graph").mkdir()
        (doctrine / "concepts" / "universal.yaml").write_text(
            yaml.safe_dump(
                {"schema_version": "agent-doctrine-concepts/1", "concepts": concepts},
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        if conflicts is not None:
            (doctrine / "conflicts.yaml").write_text(
                yaml.safe_dump(
                    {
                        "schema_version": "agent-doctrine-conflicts/1",
                        "interpretation": "Fixture conflicts retain their positions.",
                        "conflicts": conflicts,
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
        for filename, key, version in (
            ("nodes.yaml", "nodes", "agent-doctrine-graph-nodes/1"),
            (
                "formulations.yaml",
                "formulations",
                "agent-doctrine-graph-formulations/1",
            ),
            ("edges.yaml", "edges", "agent-doctrine-graph-edges/1"),
        ):
            (doctrine / "graph" / filename).write_text(
                yaml.safe_dump({"schema_version": version, key: []}, sort_keys=False),
                encoding="utf-8",
            )
        self.addCleanup(temporary.cleanup)
        return doctrine

    def run_projector(self, doctrine, mode):
        return subprocess.run(
            [
                sys.executable,
                str(PROJECTOR),
                mode,
                "--doctrine-root",
                str(doctrine),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    @staticmethod
    def concept(concept_id, contribution="Shared source formulation."):
        return {
            "id": concept_id,
            "title": concept_id.replace("-", " ").title(),
            "category": "universal",
            "claim": f"Claim for {concept_id}.",
            "why_it_matters": f"Why {concept_id} matters.",
            "applicable_when": ["the fixture condition holds"],
            "confidence": "strong",
            "retrieval_terms": [concept_id],
            "source_support": [
                {
                    "source_id": "SRC-CC",
                    "locator": "books/shared.md :: Shared heading",
                    "contribution": contribution,
                    "relationship": "direct_support",
                }
            ],
            "routing": {"related_concepts": []},
        }

    def test_conflict_registry_has_controlled_position_provenance(self):
        schema = json.loads(GRAPH_SCHEMA.read_text(encoding="utf-8"))
        conflict_schema = {
            "$schema": schema["$schema"],
            "$ref": "#/$defs/conflictDocument",
            "$defs": schema["$defs"],
        }
        conflicts = yaml.safe_load(
            (ROOT / "doctrine" / "conflicts.yaml").read_text(encoding="utf-8")
        )

        errors = list(
            jsonschema.Draft202012Validator(conflict_schema).iter_errors(conflicts)
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors))
        for conflict in conflicts["conflicts"]:
            aggregate_support = {
                (support["source_id"], support["locator"])
                for support in conflict["source_support"]
            }
            attributed_support = {
                (support["source_id"], support["locator"])
                for position in conflict["positions"]
                for support in position["source_support"]
            }
            self.assertEqual(
                aggregate_support,
                attributed_support,
                f"unattributed source support in {conflict['conflict_id']}",
            )

    def test_all_conflicts_are_reachable_graph_nodes_with_position_formulations(self):
        projection = self.run_projector(ROOT / "doctrine", "--check")
        self.assertEqual(0, projection.returncode, projection.stderr)
        conflicts = yaml.safe_load(
            (ROOT / "doctrine" / "conflicts.yaml").read_text(encoding="utf-8")
        )["conflicts"]
        nodes = yaml.safe_load(
            (ROOT / "doctrine" / "graph" / "nodes.yaml").read_text(encoding="utf-8")
        )["nodes"]
        formulations = yaml.safe_load(
            (ROOT / "doctrine" / "graph" / "formulations.yaml").read_text(
                encoding="utf-8"
            )
        )["formulations"]
        edges = yaml.safe_load(
            (ROOT / "doctrine" / "graph" / "edges.yaml").read_text(encoding="utf-8")
        )["edges"]

        conflict_ids = {record["conflict_id"] for record in conflicts}
        conflict_nodes = {
            node["id"]: node for node in nodes if node["kind"] == "conflict"
        }
        self.assertEqual(conflict_ids, set(conflict_nodes))
        self.assertEqual(25, len(conflict_nodes))
        position_formulations = [
            formulation for formulation in formulations if "conflict_ref" in formulation
        ]
        for formulation in position_formulations:
            self.assertIn(formulation["conflict_ref"], conflict_ids)
            self.assertTrue(formulation["position_ref"])
            self.assertIn(
                formulation["conflict_ref"],
                {mapping["node_id"] for mapping in formulation["mappings"]},
            )
        for record in conflicts:
            conflict_id = record["conflict_id"]
            expected_positions = {
                position["id"]
                for position in record["positions"]
                if position["source_support"]
            }
            actual_positions = {
                formulation["position_ref"]
                for formulation in position_formulations
                if formulation["conflict_ref"] == conflict_id
            }
            self.assertEqual(expected_positions, actual_positions, conflict_id)
            self.assertTrue(
                any(
                    edge["relation"] == "participates-in"
                    and edge["to"] == conflict_id
                    and edge["from"] in record["related_concepts"]
                    and edge.get("conflict_ref") == conflict_id
                    for edge in edges
                ),
                conflict_id,
            )

    def test_identical_source_formulation_is_converged_without_losing_mappings(self):
        alpha = self.concept("concept-alpha")
        beta = self.concept("concept-beta")
        beta["source_support"][0]["relationship"] = "refinement"
        doctrine = self.make_doctrine([alpha, beta])

        result = self.run_projector(doctrine, "--write")

        self.assertEqual(0, result.returncode, result.stderr)
        formulations = yaml.safe_load(
            (doctrine / "graph" / "formulations.yaml").read_text(encoding="utf-8")
        )["formulations"]
        nodes = {
            node["id"]: node
            for node in yaml.safe_load(
                (doctrine / "graph" / "nodes.yaml").read_text(encoding="utf-8")
            )["nodes"]
        }
        self.assertEqual(1, len(formulations))
        formulation = formulations[0]
        self.assertEqual(
            {
                "concept-alpha": "direct_support",
                "concept-beta": "refinement",
            },
            {
                mapping["node_id"]: mapping["relationship_to_canonical"]
                for mapping in formulation["mappings"]
            },
        )
        self.assertEqual([formulation["id"]], nodes["concept-alpha"]["formulations"])
        self.assertEqual([formulation["id"]], nodes["concept-beta"]["formulations"])
        self.assertEqual(0, self.run_projector(doctrine, "--check").returncode)

    def test_projector_rejects_source_supported_basis_without_source_support(self):
        conflict = {
            "conflict_id": "conflict-alpha-vs-beta",
            "disagreement_kind": "contextual",
            "positions": [
                {
                    "id": "alpha",
                    "claim": "Prefer alpha.",
                    "source_support": [],
                    "basis": {
                        "kind": "source-supported",
                        "rationale": "This incorrectly claims source support.",
                    },
                },
                {
                    "id": "beta",
                    "claim": "Prefer beta.",
                    "source_support": [],
                    "basis": {
                        "kind": "derived-inference",
                        "rationale": "This is explicitly inferred.",
                    },
                },
            ],
            "hidden_assumptions": ["Fixture assumption."],
            "evidence_favoring_each_position": {"alpha": ["A"], "beta": ["B"]},
            "decision_rule": "Select from repository evidence.",
            "unresolved_questions": ["Fixture uncertainty."],
            "roles_affected": ["coding-agent"],
            "related_concepts": ["concept-alpha"],
            "source_support": [
                {"source_id": "SRC-CC", "locator": "books/shared.md :: Heading"}
            ],
        }
        doctrine = self.make_doctrine([self.concept("concept-alpha")], [conflict])

        result = self.run_projector(doctrine, "--check")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("source-supported", result.stderr)


if __name__ == "__main__":
    unittest.main()
