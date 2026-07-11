import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLE_CLI = ROOT / "doctrine" / "tools" / "assemble_packet.py"


def run_packet(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ASSEMBLE_CLI), *arguments, "--render", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_markdown(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ASSEMBLE_CLI), *arguments, "--render", "markdown"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class PacketRoutingContractTests(unittest.TestCase):
    def test_packet_schema_reuses_the_canonical_evidence_record_contract(self):
        packet_schema = json.loads(
            (ROOT / "doctrine" / "runtime" / "evidence-packet.schema.json").read_text(
                encoding="utf-8"
            )
        )
        evidence_schema = json.loads(
            (ROOT / "doctrine" / "runtime" / "evidence-record.schema.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            evidence_schema["$id"],
            packet_schema["properties"]["evidence_records"]["items"]["$ref"],
        )
        self.assertNotIn("evidenceRecord", packet_schema["$defs"])

    def test_compact_default_respects_representative_delivery_envelopes(self):
        scenarios = [
            (
                "coding-agent",
                "implementation",
                "How should this behavior be implemented?",
            ),
            (
                "architecture-agent",
                "architecture-assessment",
                "Should this architecture change?",
            ),
            (
                "legacy-code-agent",
                "legacy-change",
                "How can we safely change this poorly characterized legacy code?",
            ),
        ]
        for role, task, question in scenarios:
            with self.subTest(role=role, format="json"):
                result = run_packet(
                    "--role",
                    role,
                    "--task",
                    task,
                    "--question",
                    question,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertLessEqual(len(result.stdout.encode("utf-8")), 64 * 1024)
                packet = json.loads(result.stdout)
                self.assertEqual("evidence-packet/2", packet["schema_version"])
                self.assertEqual("compact", packet["retrieval_context"]["detail"])
                self.assertNotIn("audit_views", packet)
                self.assertTrue(packet["evidence_obligations"])
                self.assertTrue(packet["activation_reasons"])
                self.assertTrue(packet["provenance_links"])
            with self.subTest(role=role, format="markdown"):
                result = run_markdown(
                    "--role",
                    role,
                    "--task",
                    task,
                    "--question",
                    question,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertLessEqual(len(result.stdout.encode("utf-8")), 32 * 1024)
                self.assertLessEqual(len(result.stdout.split()), 3500)

    def test_compact_packet_preserves_safety_and_operational_layers(self):
        result = run_packet(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "How should this behavior be implemented?",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        packet = json.loads(result.stdout)
        safety_kernel = {
            "agent-conduct-authority-bounded-action",
            "universal-evidence-before-intervention",
            "universal-no-change-option",
            "universal-preserve-behavior-by-default",
            "universal-repository-contract-precedence",
            "universal-separate-semantic-structural-change",
        }
        routing = yaml.safe_load((ROOT / "doctrine" / "routing-index.yaml").read_text())
        self.assertEqual(
            safety_kernel,
            set(routing["always_load"]["concepts"]),
        )
        self.assertLessEqual(safety_kernel, set(packet["activated_concepts"]))
        for field in (
            "activated_procedures",
            "activated_prohibitions",
            "authority_constraints",
            "applicable_change_types",
            "evidence_obligations",
            "activation_reasons",
            "provenance_links",
        ):
            self.assertTrue(packet[field], field)
        self.assertEqual(
            "relative-routing-cost-unit", packet["retrieval_budget"]["unit"]
        )
        self.assertEqual(
            "activated-concept-selection-only",
            packet["retrieval_budget"]["scope"],
        )
        self.assertIn("not a byte", packet["retrieval_budget"]["meaning"])

    def test_full_detail_explicitly_adds_derived_audit_views(self):
        arguments = (
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "How should this behavior be implemented?",
        )
        compact_result = run_packet(*arguments)
        full_result = run_packet(*arguments, "--detail", "full")
        self.assertEqual(0, compact_result.returncode, compact_result.stderr)
        self.assertEqual(0, full_result.returncode, full_result.stderr)
        compact = json.loads(compact_result.stdout)
        full = json.loads(full_result.stdout)
        self.assertNotIn("audit_views", compact)
        self.assertEqual(
            {"formulations", "missing_evidence", "source_locators"},
            set(full["audit_views"]),
        )
        self.assertEqual(compact["activated_concepts"], full["activated_concepts"])
        self.assertEqual(compact["evidence_obligations"], full["evidence_obligations"])
        self.assertEqual(compact["provenance_links"], full["provenance_links"])
        self.assertEqual("full", full["retrieval_context"]["detail"])
        self.assertNotEqual(compact["packet_id"], full["packet_id"])
        self.assertGreater(len(full_result.stdout), len(compact_result.stdout))

    def test_all_machine_readable_role_and_concept_task_references_resolve(self):
        routing = yaml.safe_load((ROOT / "doctrine" / "routing-index.yaml").read_text())
        known_roles = {
            value
            for record in routing["role_registry"]
            for value in [record["role"], *record["aliases"]]
        }
        referenced_roles = {
            role
            for route in routing["concept_routes"]
            for role in route["activate_for_roles"]
        }
        lenses = yaml.safe_load((ROOT / "doctrine" / "context-lenses.yaml").read_text())
        referenced_roles.update(
            role for lens in lenses["lenses"] for role in lens["routing"]["roles"]
        )
        procedures = yaml.safe_load((ROOT / "doctrine" / "procedures.yaml").read_text())
        referenced_roles.update(
            role
            for procedure in procedures["procedures"]
            for role in procedure["roles"]
        )
        authority = yaml.safe_load(
            (ROOT / "doctrine" / "authority-model.yaml").read_text()
        )
        referenced_roles.update(authority["role_defaults"])
        self.assertEqual(set(), referenced_roles - known_roles)
        referenced_role_families = {
            role
            for route in routing["concept_routes"]
            for role in route["activate_for_role_families"]
        }
        canonical_roles = {record["role"] for record in routing["role_registry"]}
        self.assertEqual(set(), referenced_role_families - canonical_roles)

        known_families = {record["family"] for record in routing["task_registry"]}
        known_variants = {
            variant
            for record in routing["task_registry"]
            for variant in record["variants"]
        }
        referenced_variants = {
            task
            for route in routing["concept_routes"]
            for task in route["activate_for_tasks"]
        }
        self.assertEqual(set(), referenced_variants - known_variants)
        referenced_families = {
            task
            for route in routing["concept_routes"]
            for field in (
                "activate_for_task_families",
                "conditional_for_task_families",
            )
            for task in route[field]
        }
        self.assertEqual(set(), referenced_families - known_families)

    def test_all_declared_role_aliases_are_accepted(self):
        aliases = {
            "implementation-agent": "coding-agent",
            "architectural-agent": "architecture-agent",
            "domain-design-agent": "architecture-agent",
            "legacy-agent": "legacy-code-agent",
            "dependency-agent": "review-agent",
            "repair-agent": "debugging-and-repair-agent",
            "debugging-agent": "debugging-and-repair-agent",
        }
        for alias, canonical in aliases.items():
            with self.subTest(alias=alias):
                result = run_packet(
                    "--role",
                    alias,
                    "--task",
                    "implementation",
                    "--question",
                    "What doctrine applies?",
                )
                self.assertEqual(0, result.returncode, result.stderr)
                packet = json.loads(result.stdout)
                self.assertEqual(
                    canonical, packet["retrieval_context"]["canonical_role"]
                )

    def test_all_declared_task_aliases_resolve_to_their_families(self):
        routing = yaml.safe_load((ROOT / "doctrine" / "routing-index.yaml").read_text())
        for record in routing["task_registry"]:
            for alias in record["aliases"]:
                with self.subTest(alias=alias):
                    result = run_packet(
                        "--role",
                        "repository-assessment-agent",
                        "--task",
                        alias,
                        "--question",
                        "What doctrine applies?",
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    packet = json.loads(result.stdout)
                    self.assertEqual(
                        record["family"],
                        packet["retrieval_context"]["task_family"],
                    )

    def test_role_alias_and_task_variant_activate_specialist_doctrine(self):
        result = run_packet(
            "--role",
            "domain-design-agent",
            "--task",
            "architecture-assessment",
            "--task-variant",
            "legacy-integration",
            "--question",
            "Should the local model use an Anticorruption Layer?",
            "--signal",
            "legacy API",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        packet = json.loads(result.stdout)
        self.assertEqual(
            "architecture-agent", packet["retrieval_context"]["canonical_role"]
        )
        self.assertEqual(
            ["legacy-integration"], packet["retrieval_context"]["task_variants"]
        )
        self.assertIn("domain-anticorruption-layer", packet["activated_concepts"])

    def test_alias_only_source_role_routes_to_its_canonical_role(self):
        result = run_packet(
            "--role",
            "architecture-agent",
            "--task",
            "domain-design",
            "--question",
            "Should this data carrier own the domain invariant?",
            "--language",
            "Python",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        packet = json.loads(result.stdout)
        self.assertIn(
            "python-data-carrier-versus-domain-object",
            packet["activated_concepts"],
        )

    def test_packet_carries_every_activated_doctrine_layer(self):
        result = run_packet(
            "--role",
            "architecture-agent",
            "--task",
            "architecture-assessment",
            "--question",
            "Should this legacy boundary change?",
            "--lens",
            "lens-monolith",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        packet = json.loads(result.stdout)
        self.assertIn(
            "proc-assess-architectural-pressure", packet["activated_procedures"]
        )
        self.assertIn("lens-monolith", packet["activated_lenses"])
        self.assertIn(
            "prohibit-generic-doctrine-over-local-contract",
            packet["activated_prohibitions"],
        )
        self.assertIn(
            "evidence-accepted-design-decisions", packet["required_evidence_classes"]
        )
        self.assertEqual("recommend", packet["authority_constraints"]["usual_ceiling"])
        self.assertIn(
            "change-architectural-restructuring", packet["applicable_change_types"]
        )
        reasons = {
            entry["id"]: entry["reasons"] for entry in packet["activation_reasons"]
        }
        self.assertIn("universal-evidence-before-intervention", reasons)

    def test_packet_preserves_concept_level_source_provenance(self):
        result = run_packet(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "What evidence should precede intervention?",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        packet = json.loads(result.stdout)
        link = next(
            item
            for item in packet["provenance_links"]
            if item["concept_id"] == "universal-evidence-before-intervention"
        )
        self.assertTrue(link["formulation_ids"])
        self.assertTrue(link["source_support"])
        for support in link["source_support"]:
            self.assertTrue(support["source_id"].startswith("SRC-"))
            self.assertIn(
                support["relationship"],
                {
                    "direct_support",
                    "corroboration",
                    "refinement",
                    "derived_inference",
                    "terminology_variant",
                    "historical_precursor",
                    "tension",
                },
            )
            self.assertIn(" :: ", support["locator"])

    def test_only_typed_evidence_can_discharge_an_obligation(self):
        signal_only = run_packet(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "How should caller failures be handled?",
            "--signal",
            "caller recovery needs",
            "--budget",
            "16000",
        )
        self.assertEqual(0, signal_only.returncode, signal_only.stderr)
        signal_packet = json.loads(signal_only.stdout)
        signal_mapping = next(
            item
            for item in signal_packet["evidence_obligations"]
            if item["requirement"] == "caller recovery needs"
            and item["required_by"] == "implementation-explicit-failure-policy"
        )
        self.assertEqual("missing", signal_mapping["status"])
        self.assertEqual([], signal_mapping["evidence_ids"])

        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_path = Path(temp_dir) / "caller-contract.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "schema_version": "evidence-record/1",
                        "id": "caller-contract",
                        "evidence_class": "evidence-explicit-user-requirements",
                        "summary": "The caller retries only explicitly retryable failures.",
                        "provenance": [
                            {
                                "locator": "requirements.md#failure-policy",
                                "method": "repository inspection",
                            }
                        ],
                        "satisfies": ["caller recovery needs"],
                    }
                ),
                encoding="utf-8",
            )
            with_evidence = run_packet(
                "--role",
                "coding-agent",
                "--task",
                "implementation",
                "--question",
                "How should caller failures be handled?",
                "--signal",
                "caller recovery needs",
                "--evidence",
                str(evidence_path),
                "--budget",
                "16000",
            )

        self.assertEqual(0, with_evidence.returncode, with_evidence.stderr)
        evidence_packet = json.loads(with_evidence.stdout)
        evidence_mapping = next(
            item
            for item in evidence_packet["evidence_obligations"]
            if item["requirement"] == "caller recovery needs"
            and item["required_by"] == "implementation-explicit-failure-policy"
        )
        self.assertEqual("satisfied", evidence_mapping["status"])
        self.assertEqual(["caller-contract"], evidence_mapping["evidence_ids"])
        self.assertEqual(
            "caller-contract", evidence_packet["evidence_records"][0]["id"]
        )

    def test_invalid_evidence_record_is_rejected_before_assembly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_path = Path(temp_dir) / "invalid-evidence.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "schema_version": "evidence-record/1",
                        "id": "unsupported-claim",
                        "evidence_class": "evidence-tests",
                        "summary": "No provenance accompanies this assertion.",
                        "satisfies": ["caller recovery needs"],
                    }
                ),
                encoding="utf-8",
            )
            result = run_packet(
                "--role",
                "coding-agent",
                "--task",
                "implementation",
                "--question",
                "How should caller failures be handled?",
                "--evidence",
                str(evidence_path),
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid evidence", result.stderr)
        self.assertIn("provenance", result.stderr)

    def test_question_terms_explain_specialist_selection(self):
        generic = run_packet(
            "--role",
            "architecture-agent",
            "--task",
            "architecture-assessment",
            "--question",
            "Should this architecture change?",
        )
        specific = run_packet(
            "--role",
            "architecture-agent",
            "--task",
            "architecture-assessment",
            "--question",
            "Should we protect the local model with an Anticorruption Layer?",
        )
        self.assertEqual(0, generic.returncode, generic.stderr)
        self.assertEqual(0, specific.returncode, specific.stderr)
        generic_packet = json.loads(generic.stdout)
        specific_packet = json.loads(specific.stdout)
        self.assertNotIn(
            "domain-anticorruption-layer", generic_packet["activated_concepts"]
        )
        self.assertIn(
            "domain-anticorruption-layer", specific_packet["activated_concepts"]
        )
        reasons = {
            entry["id"]: entry["reasons"]
            for entry in specific_packet["activation_reasons"]
        }
        self.assertIn(
            "question term 'Anticorruption Layer'",
            reasons["domain-anticorruption-layer"],
        )

    def test_requested_budget_is_enforced_and_reports_omissions(self):
        small = run_packet(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "How should the parser implement this behavior?",
            "--budget",
            "6000",
        )
        large = run_packet(
            "--role",
            "coding-agent",
            "--task",
            "implementation",
            "--question",
            "How should the parser implement this behavior?",
            "--budget",
            "9000",
        )
        self.assertEqual(0, small.returncode, small.stderr)
        self.assertEqual(0, large.returncode, large.stderr)
        small_packet = json.loads(small.stdout)
        large_packet = json.loads(large.stdout)
        self.assertEqual(6000, small_packet["retrieval_budget"]["requested"])
        self.assertLessEqual(small_packet["retrieval_budget"]["used"], 6000)
        self.assertTrue(small_packet["budget_excluded"])
        self.assertLess(
            len(small_packet["activated_concepts"]),
            len(large_packet["activated_concepts"]),
        )

    def test_packet_and_doctrine_identities_are_content_addressed(self):
        result = run_packet(
            "--role",
            "implementation-agent",
            "--task",
            "implementation",
            "--question",
            "How should this behavior be implemented?",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        packet = json.loads(result.stdout)
        self.assertTrue(packet["doctrine_version"].startswith("doctrine-"))
        self.assertTrue(packet["retriever_version"].startswith("retriever-"))
        self.assertEqual(
            "implementation-agent", packet["retrieval_context"]["requested_role"]
        )

        content = dict(packet)
        content.pop("packet_id")
        content.pop("packet_content_sha256")
        canonical = json.dumps(
            content, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertEqual(digest, packet["packet_content_sha256"])
        self.assertEqual(f"pkt-{digest[:16]}", packet["packet_id"])

    def test_doctrine_change_changes_doctrine_and_packet_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            doctrine_copy = Path(temp_dir) / "doctrine"
            shutil.copytree(ROOT / "doctrine", doctrine_copy)
            cli = doctrine_copy / "tools" / "assemble_packet.py"
            arguments = [
                sys.executable,
                str(cli),
                "--role",
                "coding-agent",
                "--task",
                "implementation",
                "--question",
                "What doctrine applies?",
                "--render",
                "json",
            ]
            first_result = subprocess.run(
                arguments,
                cwd=temp_dir,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, first_result.returncode, first_result.stderr)
            first = json.loads(first_result.stdout)

            concept_path = doctrine_copy / "concepts" / "universal.yaml"
            concept_path.write_text(
                concept_path.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            second_result = subprocess.run(
                arguments,
                cwd=temp_dir,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, second_result.returncode, second_result.stderr)
            second = json.loads(second_result.stdout)

        self.assertEqual(first["corpus_version"], second["corpus_version"])
        self.assertNotEqual(first["doctrine_version"], second["doctrine_version"])
        self.assertNotEqual(first["packet_id"], second["packet_id"])


if __name__ == "__main__":
    unittest.main()
