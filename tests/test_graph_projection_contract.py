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


def concept(concept_id, related=()):
    return {
        "id": concept_id,
        "title": concept_id.replace("-", " ").title(),
        "category": "universal",
        "claim": f"Claim for {concept_id}.",
        "why_it_matters": f"Why {concept_id} matters.",
        "applicable_when": ["the concept is activated"],
        "confidence": "strong",
        "retrieval_terms": [concept_id],
        "source_support": [
            {
                "source_id": "SRC-CC",
                "locator": f"books/{concept_id}.md :: Heading",
                "contribution": f"Source contribution for {concept_id}.",
                "relationship": "direct_support",
            }
        ],
        "routing": {"related_concepts": list(related)},
    }


class GraphProjectionContractTests(unittest.TestCase):
    def make_doctrine(self, concepts):
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

    def test_routing_adjacency_is_written_outside_semantic_edges(self):
        doctrine = self.make_doctrine(
            [concept("concept-alpha", ["concept-beta"]), concept("concept-beta")]
        )

        result = self.run_projector(doctrine, "--write")

        self.assertEqual(0, result.returncode, result.stderr)
        semantic_edges = yaml.safe_load(
            (doctrine / "graph" / "edges.yaml").read_text(encoding="utf-8")
        )["edges"]
        self.assertEqual([], semantic_edges)
        routing = yaml.safe_load(
            (doctrine / "routing-graph" / "links.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual("agent-doctrine-routing-graph/1", routing["schema_version"])
        self.assertEqual(
            [
                {
                    "id": routing["links"][0]["id"],
                    "from": "concept-alpha",
                    "relation": "co-retrieved-with",
                    "to": "concept-beta",
                    "semantic": False,
                    "declared_by": ["concept-alpha"],
                }
            ],
            routing["links"],
        )

    def test_check_passes_only_when_the_complete_projection_is_current(self):
        doctrine = self.make_doctrine(
            [concept("concept-alpha", ["concept-beta"]), concept("concept-beta")]
        )
        written = self.run_projector(doctrine, "--write")
        self.assertEqual(0, written.returncode, written.stderr)
        projected_paths = [
            doctrine / "graph" / "nodes.yaml",
            doctrine / "graph" / "formulations.yaml",
            doctrine / "graph" / "edges.yaml",
            doctrine / "routing-graph" / "links.yaml",
        ]
        before = {path: path.read_bytes() for path in projected_paths}

        checked = self.run_projector(doctrine, "--check")
        rewritten = self.run_projector(doctrine, "--write")

        self.assertEqual(0, checked.returncode, checked.stderr)
        self.assertIn("projection is current", checked.stdout)
        self.assertEqual(0, rewritten.returncode, rewritten.stderr)
        self.assertEqual(before, {path: path.read_bytes() for path in projected_paths})

    def test_changed_concept_replaces_owned_node_and_formulation_content(self):
        doctrine = self.make_doctrine([concept("concept-alpha")])
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        before = yaml.safe_load(
            (doctrine / "graph" / "formulations.yaml").read_text(encoding="utf-8")
        )["formulations"]
        old_formulation_id = before[0]["id"]
        concept_path = doctrine / "concepts" / "universal.yaml"
        document = yaml.safe_load(concept_path.read_text(encoding="utf-8"))
        document["concepts"][0]["title"] = "Changed title"
        document["concepts"][0]["claim"] = "Changed canonical claim."
        document["concepts"][0]["source_support"][0]["contribution"] = (
            "Changed source contribution."
        )
        concept_path.write_text(
            yaml.safe_dump(document, sort_keys=False), encoding="utf-8"
        )

        stale = self.run_projector(doctrine, "--check")
        repaired = self.run_projector(doctrine, "--write")

        self.assertEqual(1, stale.returncode)
        self.assertEqual(0, repaired.returncode, repaired.stderr)
        nodes = yaml.safe_load(
            (doctrine / "graph" / "nodes.yaml").read_text(encoding="utf-8")
        )["nodes"]
        self.assertEqual("Changed title", nodes[0]["label"])
        self.assertEqual("Changed canonical claim.", nodes[0]["definition"])
        formulations = yaml.safe_load(
            (doctrine / "graph" / "formulations.yaml").read_text(encoding="utf-8")
        )["formulations"]
        self.assertEqual(1, len(formulations))
        self.assertNotEqual(old_formulation_id, formulations[0]["id"])
        self.assertEqual("Changed source contribution.", formulations[0]["paraphrase"])
        self.assertEqual(
            {
                "conditions": "canonical-mapping",
                "caveats": "canonical-policy",
            },
            formulations[0]["context_basis"],
        )
        self.assertIn("not attributed to the source", formulations[0]["conditions"])
        self.assertEqual(0, self.run_projector(doctrine, "--check").returncode)

    def test_curated_concept_node_tracks_record_confidence_and_status(self):
        doctrine = self.make_doctrine([concept("concept-alpha")])
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        node_path = doctrine / "graph" / "nodes.yaml"
        formulation_path = doctrine / "graph" / "formulations.yaml"
        node_document = yaml.safe_load(node_path.read_text(encoding="utf-8"))
        formulation_document = yaml.safe_load(
            formulation_path.read_text(encoding="utf-8")
        )
        node = node_document["nodes"][0]
        node.pop("projection")
        node["label"] = "Curated label"
        curated_formulation = {
            "id": "F-SRC-CC-CURATED-ALPHA",
            "source_id": "SRC-CC",
            "locator": "books/shared.md#Curated heading",
            "mappings": [
                {
                    "node_id": "concept-alpha",
                    "relationship_to_canonical": "direct_support",
                }
            ],
            "paraphrase": "Curated formulation.",
            "conditions": "The curated condition holds.",
            "caveats": "The curated caveat applies.",
        }
        formulation_document["formulations"].insert(0, curated_formulation)
        node["formulations"].insert(0, curated_formulation["id"])
        node_path.write_text(
            yaml.safe_dump(node_document, sort_keys=False), encoding="utf-8"
        )
        formulation_path.write_text(
            yaml.safe_dump(formulation_document, sort_keys=False), encoding="utf-8"
        )
        concept_path = doctrine / "concepts" / "universal.yaml"
        concept_document = yaml.safe_load(concept_path.read_text(encoding="utf-8"))
        concept_document["concepts"][0]["confidence"] = "contextual"
        concept_path.write_text(
            yaml.safe_dump(concept_document, sort_keys=False), encoding="utf-8"
        )

        result = self.run_projector(doctrine, "--write")

        self.assertEqual(0, result.returncode, result.stderr)
        projected = yaml.safe_load(node_path.read_text(encoding="utf-8"))["nodes"][0]
        self.assertEqual("Curated label", projected["label"])
        self.assertEqual("contextual", projected["confidence"])
        self.assertEqual("contextual", projected["status"])
        formulations = yaml.safe_load(formulation_path.read_text(encoding="utf-8"))[
            "formulations"
        ]
        curated = next(
            item for item in formulations if item["id"] == curated_formulation["id"]
        )
        self.assertEqual(
            {"conditions": "source-specific", "caveats": "source-specific"},
            curated["context_basis"],
        )
        self.assertEqual(0, self.run_projector(doctrine, "--check").returncode)

    def test_deleted_concept_removes_every_owned_projection_record(self):
        doctrine = self.make_doctrine(
            [concept("concept-alpha", ["concept-beta"]), concept("concept-beta")]
        )
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        concept_path = doctrine / "concepts" / "universal.yaml"
        document = yaml.safe_load(concept_path.read_text(encoding="utf-8"))
        document["concepts"] = [document["concepts"][0]]
        concept_path.write_text(
            yaml.safe_dump(document, sort_keys=False), encoding="utf-8"
        )

        stale = self.run_projector(doctrine, "--check")
        repaired = self.run_projector(doctrine, "--write")

        self.assertEqual(1, stale.returncode)
        self.assertEqual(0, repaired.returncode, repaired.stderr)
        nodes = yaml.safe_load(
            (doctrine / "graph" / "nodes.yaml").read_text(encoding="utf-8")
        )["nodes"]
        formulations = yaml.safe_load(
            (doctrine / "graph" / "formulations.yaml").read_text(encoding="utf-8")
        )["formulations"]
        links = yaml.safe_load(
            (doctrine / "routing-graph" / "links.yaml").read_text(encoding="utf-8")
        )["links"]
        self.assertEqual(["concept-alpha"], [node["id"] for node in nodes])
        self.assertEqual(
            ["concept-alpha"],
            [formulation["mappings"][0]["node_id"] for formulation in formulations],
        )
        self.assertEqual([], links)
        self.assertEqual(0, self.run_projector(doctrine, "--check").returncode)

    def test_added_concept_is_detected_and_projected_reciprocally(self):
        doctrine = self.make_doctrine([concept("concept-alpha")])
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        concept_path = doctrine / "concepts" / "universal.yaml"
        document = yaml.safe_load(concept_path.read_text(encoding="utf-8"))
        document["concepts"].append(concept("concept-beta"))
        concept_path.write_text(
            yaml.safe_dump(document, sort_keys=False), encoding="utf-8"
        )

        stale = self.run_projector(doctrine, "--check")
        repaired = self.run_projector(doctrine, "--write")

        self.assertEqual(1, stale.returncode)
        self.assertEqual(0, repaired.returncode, repaired.stderr)
        nodes = {
            node["id"]: node
            for node in yaml.safe_load(
                (doctrine / "graph" / "nodes.yaml").read_text(encoding="utf-8")
            )["nodes"]
        }
        formulations = {
            formulation["id"]: formulation
            for formulation in yaml.safe_load(
                (doctrine / "graph" / "formulations.yaml").read_text(encoding="utf-8")
            )["formulations"]
        }
        beta_formulation_id = nodes["concept-beta"]["formulations"][0]
        self.assertEqual(
            "concept-beta",
            formulations[beta_formulation_id]["mappings"][0]["node_id"],
        )
        self.assertEqual(0, self.run_projector(doctrine, "--check").returncode)

    def test_broken_owned_formulation_node_reciprocity_fails_check(self):
        doctrine = self.make_doctrine([concept("concept-alpha")])
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        node_path = doctrine / "graph" / "nodes.yaml"
        document = yaml.safe_load(node_path.read_text(encoding="utf-8"))
        document["nodes"][0]["formulations"] = []
        node_path.write_text(
            yaml.safe_dump(document, sort_keys=False), encoding="utf-8"
        )

        stale = self.run_projector(doctrine, "--check")
        repaired = self.run_projector(doctrine, "--write")

        self.assertEqual(1, stale.returncode)
        self.assertEqual(0, repaired.returncode, repaired.stderr)
        node = yaml.safe_load(node_path.read_text(encoding="utf-8"))["nodes"][0]
        formulation = yaml.safe_load(
            (doctrine / "graph" / "formulations.yaml").read_text(encoding="utf-8")
        )["formulations"][0]
        self.assertEqual([formulation["id"]], node["formulations"])
        self.assertEqual(node["id"], formulation["mappings"][0]["node_id"])

    def test_schema_separates_nonsemantic_routing_from_semantic_edges(self):
        schema = json.loads(
            (ROOT / "doctrine" / "schemas" / "graph.schema.json").read_text(
                encoding="utf-8"
            )
        )
        routing_schema = {
            "$schema": schema["$schema"],
            "$ref": "#/$defs/routingLink",
            "$defs": schema["$defs"],
        }
        routing_link = {
            "id": "R-ROUTE-abc123abc123",
            "from": "concept-alpha",
            "relation": "co-retrieved-with",
            "to": "concept-beta",
            "semantic": False,
            "declared_by": ["concept-alpha"],
        }
        jsonschema.validate(routing_link, routing_schema)
        invalid_routing = dict(routing_link, semantic=True)
        self.assertTrue(
            list(
                jsonschema.Draft202012Validator(routing_schema).iter_errors(
                    invalid_routing
                )
            )
        )
        routing_graph_schema = {
            "$schema": schema["$schema"],
            "$ref": "#/$defs/routingGraph",
            "$defs": schema["$defs"],
        }
        routing_document = yaml.safe_load(
            (ROOT / "doctrine" / "routing-graph" / "links.yaml").read_text(
                encoding="utf-8"
            )
        )
        jsonschema.validate(routing_document, routing_graph_schema)

        edge_schema = {
            "$schema": schema["$schema"],
            "$ref": "#/$defs/edge",
            "$defs": schema["$defs"],
        }
        legacy_routing_edge = {
            "id": "E-ROUTE-abc123",
            "from": "concept-alpha",
            "relation": "composes-with",
            "to": "concept-beta",
            "claim": "These concepts share a retrieval route.",
            "conditions": ["a route selects both"],
            "derivation": "synthesized",
            "confidence": "contextual",
            "provenance": ["F-CONCEPT-CC-abc123"],
        }
        self.assertTrue(
            list(
                jsonschema.Draft202012Validator(edge_schema).iter_errors(
                    legacy_routing_edge
                )
            )
        )

    def test_synthesized_semantic_edge_requires_an_auditable_inference(self):
        schema = json.loads(
            (ROOT / "doctrine" / "schemas" / "graph.schema.json").read_text(
                encoding="utf-8"
            )
        )
        edge_schema = {
            "$schema": schema["$schema"],
            "$ref": "#/$defs/edge",
            "$defs": schema["$defs"],
        }
        edge = {
            "id": "E-semantic-synthesis",
            "from": "concept-alpha",
            "relation": "requires",
            "to": "concept-beta",
            "claim": "Alpha requires beta under the stated condition.",
            "conditions": ["the bounded condition holds"],
            "derivation": "synthesized",
            "confidence": "contextual",
            "provenance": ["F-CONCEPT-CC-abc123"],
        }
        validator = jsonschema.Draft202012Validator(edge_schema)
        self.assertTrue(list(validator.iter_errors(edge)))

        edge["synthesis"] = {
            "origin": "curated",
            "rationale": "The cited premises jointly support the conditional relation.",
            "rivals": ["The concepts may apply independently outside the condition."],
            "falsifiers": ["Alpha succeeds without beta while the condition holds."],
        }
        self.assertEqual([], list(validator.iter_errors(edge)))

    def test_projector_adds_deterministic_audit_to_synthesized_semantic_edges(self):
        doctrine = self.make_doctrine(
            [concept("concept-alpha"), concept("concept-beta")]
        )
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        formulations = yaml.safe_load(
            (doctrine / "graph" / "formulations.yaml").read_text(encoding="utf-8")
        )["formulations"]
        provenance = [formulation["id"] for formulation in formulations]
        edge_path = doctrine / "graph" / "edges.yaml"
        edge_document = yaml.safe_load(edge_path.read_text(encoding="utf-8"))
        edge_document["edges"] = [
            {
                "id": "E-semantic-synthesis",
                "from": "concept-alpha",
                "relation": "requires",
                "to": "concept-beta",
                "claim": "Alpha conditionally requires beta.",
                "conditions": ["the bounded condition holds"],
                "derivation": "synthesized",
                "confidence": "contextual",
                "provenance": provenance,
            }
        ]
        edge_path.write_text(
            yaml.safe_dump(edge_document, sort_keys=False), encoding="utf-8"
        )

        written = self.run_projector(doctrine, "--write")

        self.assertEqual(0, written.returncode, written.stderr)
        edge = yaml.safe_load(edge_path.read_text(encoding="utf-8"))["edges"][0]
        self.assertEqual("projected", edge["synthesis"]["origin"])
        self.assertIn("concept-alpha", edge["synthesis"]["rationale"])
        self.assertIn("concept-beta", edge["synthesis"]["rationale"])
        self.assertTrue(edge["synthesis"]["rivals"])
        self.assertTrue(edge["synthesis"]["falsifiers"])
        self.assertEqual(0, self.run_projector(doctrine, "--check").returncode)

    def test_semantic_edge_provenance_must_cover_both_endpoints(self):
        doctrine = self.make_doctrine(
            [concept("concept-alpha"), concept("concept-beta")]
        )
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        formulations = yaml.safe_load(
            (doctrine / "graph" / "formulations.yaml").read_text(encoding="utf-8")
        )["formulations"]
        alpha_formulation = next(
            item
            for item in formulations
            if item["mappings"][0]["node_id"] == "concept-alpha"
        )
        edge_path = doctrine / "graph" / "edges.yaml"
        edge_document = yaml.safe_load(edge_path.read_text(encoding="utf-8"))
        edge_document["edges"] = [
            {
                "id": "E-incomplete-provenance",
                "from": "concept-alpha",
                "relation": "requires",
                "to": "concept-beta",
                "claim": "Alpha requires beta.",
                "conditions": ["the bounded condition holds"],
                "derivation": "direct",
                "confidence": "strong",
                "provenance": [alpha_formulation["id"]],
            }
        ]
        edge_path.write_text(
            yaml.safe_dump(edge_document, sort_keys=False), encoding="utf-8"
        )

        result = self.run_projector(doctrine, "--check")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("does not cover endpoint concept-beta", result.stderr)

    def test_locator_occurrence_disambiguation_does_not_churn_formulation_id(self):
        doctrine = self.make_doctrine([concept("concept-alpha")])
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        formulation_path = doctrine / "graph" / "formulations.yaml"
        original_id = yaml.safe_load(formulation_path.read_text(encoding="utf-8"))[
            "formulations"
        ][0]["id"]
        concept_path = doctrine / "concepts" / "universal.yaml"
        document = yaml.safe_load(concept_path.read_text(encoding="utf-8"))
        document["concepts"][0]["source_support"][0]["locator"] += " @@ occurrence=1"
        concept_path.write_text(
            yaml.safe_dump(document, sort_keys=False), encoding="utf-8"
        )

        self.assertEqual(1, self.run_projector(doctrine, "--check").returncode)
        self.assertEqual(0, self.run_projector(doctrine, "--write").returncode)
        formulation = yaml.safe_load(formulation_path.read_text(encoding="utf-8"))[
            "formulations"
        ][0]
        self.assertEqual(original_id, formulation["id"])
        self.assertTrue(formulation["locator"].endswith("#Heading @@ occurrence=1"))


if __name__ == "__main__":
    unittest.main()
