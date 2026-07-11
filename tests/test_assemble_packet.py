import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLE_CLI = ROOT / "doctrine" / "tools" / "assemble_packet.py"
PACKET_SCHEMA = ROOT / "doctrine" / "runtime" / "evidence-packet.schema.json"

_RUN_CACHE = {}


def run_assembler(*arguments):
    key = tuple(arguments)
    if key not in _RUN_CACHE:
        _RUN_CACHE[key] = subprocess.run(
            [sys.executable, str(ASSEMBLE_CLI), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    return _RUN_CACHE[key]


def packet_for(*arguments):
    result = run_assembler(*arguments, "--render", "json")
    if result.returncode != 0:
        raise AssertionError(f"assembler failed: {result.stderr}")
    return json.loads(result.stdout)


class PacketAssemblyTests(unittest.TestCase):
    def test_assembled_packet_validates_against_schema(self):
        import jsonschema

        packet = packet_for(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "Should the parser accept the new format?",
        )
        schema = json.loads(PACKET_SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(packet)
        self.assertEqual("evidence-packet/2", packet["schema_version"])
        self.assertTrue(packet["packet_id"].startswith("pkt-"))
        self.assertTrue(packet["corpus_version"].startswith("corpus-"))
        snapshot_date = yaml.safe_load(
            (ROOT / "doctrine" / "traceability.yaml").read_text(encoding="utf-8")
        )["corpus_snapshot_date"]
        self.assertIn(str(snapshot_date), packet["corpus_version"])
        self.assertTrue(packet["activated_concepts"])
        self.assertTrue(packet["provenance_links"])
        self.assertTrue(packet["evidence_obligations"])
        self.assertNotIn("audit_views", packet)

    def test_identical_invocations_produce_byte_identical_output(self):
        arguments = [
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "Should the parser accept the new format?",
            "--signal",
            "coordinated edits",
            "--render",
            "none",
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.json"
            second = Path(temp_dir) / "second.json"
            for out_path in (first, second):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ASSEMBLE_CLI),
                        *arguments,
                        "--out",
                        str(out_path),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual("", result.stdout)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_role_and_task_selection_narrows_the_packet(self):
        implementation = packet_for(
            "--role", "coding-agent", "--task", "implementation", "--question", "q"
        )
        assessment = packet_for(
            "--role",
            "repository-assessment-agent",
            "--task",
            "repository-assessment",
            "--question",
            "q",
        )
        # Both packets carry the always-load core.
        for packet in (implementation, assessment):
            self.assertIn(
                "universal-evidence-before-intervention", packet["activated_concepts"]
            )
        # Implementation doctrine is not routed to the assessment packet.
        self.assertIn("implementation-readiness", implementation["activated_concepts"])
        self.assertNotIn("implementation-readiness", assessment["activated_concepts"])
        self.assertNotEqual(
            set(implementation["activated_concepts"]),
            set(assessment["activated_concepts"]),
        )

    def test_signal_activates_route_that_role_and_task_alone_do_not(self):
        without_signal = packet_for(
            "--role",
            "repository-assessment-agent",
            "--task",
            "repository-assessment",
            "--question",
            "q",
        )
        with_signal = packet_for(
            "--role",
            "repository-assessment-agent",
            "--task",
            "repository-assessment",
            "--question",
            "q",
            "--signal",
            "coordinated edits",
        )
        self.assertNotIn(
            "architecture-change-locality-cohesion",
            without_signal["activated_concepts"],
        )
        self.assertIn(
            "architecture-change-locality-cohesion", with_signal["activated_concepts"]
        )

    def test_exclusion_produces_excluded_candidate_with_reason(self):
        packet = packet_for(
            "--role",
            "repository-assessment-agent",
            "--task",
            "repository-assessment",
            "--question",
            "q",
            "--signal",
            "coordinated edits",
            "--signal",
            "generated or vendored organization",
        )
        self.assertNotIn(
            "architecture-change-locality-cohesion", packet["activated_concepts"]
        )
        excluded = {
            entry["id"]: entry["reason"] for entry in packet["excluded_candidates"]
        }
        self.assertIn("architecture-change-locality-cohesion", excluded)
        self.assertIn(
            "generated or vendored organization",
            excluded["architecture-change-locality-cohesion"],
        )

    def test_signal_nomination_blocked_by_role_and_task_mismatch_is_recorded(self):
        packet = packet_for(
            "--role",
            "performance-agent",
            "--task",
            "performance-optimization",
            "--question",
            "q",
            "--signal",
            "coordinated edits",
        )
        excluded = {
            entry["id"]: entry["reason"] for entry in packet["excluded_candidates"]
        }
        self.assertIn("architecture-change-locality-cohesion", excluded)
        reason = excluded["architecture-change-locality-cohesion"]
        self.assertIn("not in activate_for_roles", reason)
        self.assertIn("not in activate_for_tasks", reason)

    def test_language_gate_filters_and_activates_language_doctrine(self):
        default_packet = packet_for(
            "--role", "coding-agent", "--task", "implementation", "--question", "q"
        )
        python_packet = packet_for(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "q",
            "--language",
            "Python",
        )
        self.assertNotIn(
            "python-protocol-conformance", default_packet["activated_concepts"]
        )
        excluded = {
            entry["id"]: entry["reason"]
            for entry in default_packet["excluded_candidates"]
        }
        self.assertIn("python-protocol-conformance", excluded)
        self.assertIn("language-independent", excluded["python-protocol-conformance"])
        self.assertIn(
            "python-protocol-conformance", python_packet["activated_concepts"]
        )
        # Go doctrine stays excluded when only Python is evidenced.
        self.assertNotIn(
            "go-package-api-simplicity", python_packet["activated_concepts"]
        )

    def test_unknown_role_exits_nonzero_and_lists_vocabulary(self):
        result = run_assembler(
            "--role", "shipping-agent", "--task", "implementation", "--question", "q"
        )
        self.assertNotEqual(0, result.returncode)
        for role in ("coding-agent", "repository-assessment-agent", "review-agent"):
            self.assertIn(role, result.stderr)

    def test_unknown_task_exits_nonzero_and_lists_vocabulary(self):
        result = run_assembler(
            "--role", "coding-agent", "--task", "shipping", "--question", "q"
        )
        self.assertNotEqual(0, result.returncode)
        for task in ("implementation", "refactoring", "repository-assessment"):
            self.assertIn(task, result.stderr)

    def test_conflicts_are_loaded_for_activated_concepts(self):
        packet = packet_for(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "Should we introduce an earned abstraction?",
        )
        # The explicit question activates earned-abstraction doctrine and its conflict.
        self.assertIn("universal-earned-abstraction", packet["activated_concepts"])
        self.assertIn("conflict-abstraction-vs-duplication", packet["conflicts"])

    def test_unevidenced_prerequisites_become_unmet_obligations(self):
        packet = packet_for(
            "--role",
            "refactoring-agent",
            "--task",
            "refactoring",
            "--question",
            "How can we preserve behavior during this refactoring?",
        )
        self.assertTrue(
            any(
                obligation["requirement"] == "target repository and task scope"
                and obligation["required_by"]
                == "universal-repository-contract-precedence"
                and obligation["status"] == "missing"
                for obligation in packet["evidence_obligations"]
            )
        )
        # A concept-record prerequisite is pulled into the packet, not listed as missing.
        self.assertIn(
            "refactoring-change-type-classification", packet["activated_concepts"]
        )

    def test_markdown_render_starts_with_question_and_precedence(self):
        result = run_assembler(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "Should the parser accept the new format?",
            "--render",
            "markdown",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Should the parser accept the new format?", result.stdout)
        self.assertIn("retrieval never creates authority", result.stdout)
        self.assertIn("## Activated concepts", result.stdout)
        self.assertIn("## Operational layers", result.stdout)
        self.assertIn("## Conflicts", result.stdout)
        self.assertIn("## Unmet evidence obligations", result.stdout)
        self.assertNotIn("## Expanded audit views", result.stdout)


if __name__ == "__main__":
    unittest.main()
