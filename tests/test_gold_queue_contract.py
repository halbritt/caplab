import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "doctrine" / "tools" / "build_gold_queue.py"
INPUT_PATHS = (
    "doctrine/sources.yaml",
    "doctrine/graph/edges.yaml",
    "doctrine/graph/formulations.yaml",
    "doctrine/authority-model.yaml",
    "doctrine/context-lenses.yaml",
)
GOLD_STATIC_PATHS = (
    "doctrine/evaluations/gold/queue.schema.json",
    "doctrine/evaluations/gold/human-dispositions.schema.json",
    "doctrine/evaluations/gold/README.md",
)


def load_yaml(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected mapping in {path}")
    return value


def prepare_fixture(root: Path) -> None:
    for relative in (*INPUT_PATHS, *GOLD_STATIC_PATHS):
        source = ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def run_tool(root: Path, mode: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root), mode],
        capture_output=True,
        text=True,
    )


class GoldQueueContractTests(unittest.TestCase):
    def test_check_does_not_create_a_missing_gold_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            result = run_tool(root, "--check")

            self.assertEqual(result.returncode, 1)
            self.assertFalse((root / "doctrine" / "evaluations" / "gold").exists())

    def test_checked_in_queue_covers_every_required_calibration_axis(self) -> None:
        result = run_tool(ROOT, "--check")
        self.assertEqual(result.returncode, 0, result.stderr)

        gold = ROOT / "doctrine" / "evaluations" / "gold"
        queue = json.loads((gold / "queue.json").read_text(encoding="utf-8"))
        coverage = json.loads((gold / "coverage.json").read_text(encoding="utf-8"))
        dispositions = json.loads(
            (gold / "human-dispositions.json").read_text(encoding="utf-8")
        )

        sources = load_yaml(ROOT / "doctrine" / "sources.yaml")["sources"]
        edges = load_yaml(ROOT / "doctrine" / "graph" / "edges.yaml")["edges"]
        formulations = load_yaml(ROOT / "doctrine" / "graph" / "formulations.yaml")[
            "formulations"
        ]
        authority = load_yaml(ROOT / "doctrine" / "authority-model.yaml")
        lenses = load_yaml(ROOT / "doctrine" / "context-lenses.yaml")["lenses"]

        expected = {
            "source_ids": sorted(source["id"] for source in sources),
            "edge_relations": sorted({edge["relation"] for edge in edges}),
            "support_relationships": sorted(
                {
                    mapping["relationship_to_canonical"]
                    for formulation in formulations
                    for mapping in formulation["mappings"]
                }
            ),
            "agent_roles": sorted(authority["role_defaults"]),
            "risk_classes": sorted(
                {
                    risk
                    for lens in lenses
                    for risk in lens.get("routing", {}).get("risk_classes", [])
                }
            ),
            "authority_transitions": sorted(
                f"{transition['from']}->{transition['to']}"
                for transition in authority["transitions"]
            ),
            "outcomes": ["abstention", "insufficient-evidence", "no-change"],
        }
        self.assertEqual(coverage["required"], expected)
        self.assertEqual(coverage["covered"], expected)
        self.assertTrue(all(not values for values in coverage["missing"].values()))
        self.assertEqual(coverage["pending_human_count"], len(queue["records"]))
        self.assertEqual(coverage["adjudicated_human_count"], 0)
        self.assertEqual(dispositions["dispositions"], [])
        for record in queue["records"]:
            self.assertTrue(record["candidate"]["generated_only"])
            self.assertEqual(
                record["human_disposition"],
                {"reference": None, "status": "pending-human"},
            )

    def test_write_is_deterministic_and_check_detects_queue_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prepare_fixture(root)
            first = run_tool(root, "--write")
            self.assertEqual(first.returncode, 0, first.stderr)
            queue_path = root / "doctrine" / "evaluations" / "gold" / "queue.json"
            coverage_path = queue_path.with_name("coverage.json")
            before = (
                hashlib.sha256(queue_path.read_bytes()).hexdigest(),
                hashlib.sha256(coverage_path.read_bytes()).hexdigest(),
            )
            second = run_tool(root, "--write")
            self.assertEqual(second.returncode, 0, second.stderr)
            after = (
                hashlib.sha256(queue_path.read_bytes()).hexdigest(),
                hashlib.sha256(coverage_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(before, after)

            queue = json.loads(queue_path.read_text(encoding="utf-8"))
            queue["records"][0]["candidate"]["question"] = "manual drift"
            queue_path.write_text(json.dumps(queue), encoding="utf-8")
            check = run_tool(root, "--check")
            self.assertEqual(check.returncode, 1)
            self.assertIn("queue.json is stale", check.stderr)

    def test_machine_identity_cannot_create_a_human_disposition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prepare_fixture(root)
            written = run_tool(root, "--write")
            self.assertEqual(written.returncode, 0, written.stderr)
            gold = root / "doctrine" / "evaluations" / "gold"
            queue = json.loads((gold / "queue.json").read_text(encoding="utf-8"))
            dispositions_path = gold / "human-dispositions.json"
            dispositions = {
                "schema_version": "doctrine-gold-human-dispositions/1",
                "dispositions": [
                    {
                        "candidate_id": queue["records"][0]["id"],
                        "adjudicator": {"kind": "machine", "id": "model-output"},
                        "adjudicated_at": "2026-07-11T00:00:00Z",
                        "verdict": "supported",
                        "rationale": "Machine-generated screening output.",
                        "evidence_reviewed": ["machine-screening:test"],
                        "uncertainty": "Not reviewed by a human.",
                    }
                ],
            }
            dispositions_path.write_text(
                json.dumps(dispositions, indent=2) + "\n", encoding="utf-8"
            )

            result = run_tool(root, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("adjudicator.kind=human", result.stderr)


if __name__ == "__main__":
    unittest.main()
