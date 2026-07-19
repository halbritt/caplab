"""Behavioral tests for executable authority and receipt contracts."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "doctrine" / "tools" / "validate_assertions.py"


class AuthorityContractTests(unittest.TestCase):
    def run_validator(
        self, artifact: dict[str, object]
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "artifact.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_recommendation_requires_observation_or_inference_lineage(self) -> None:
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/2",
                "evidence": [],
                "assertions": [
                    {
                        "id": "recommend-change",
                        "type": "recommendation",
                        "text": "Change the boundary.",
                        "alternatives": ["Leave it unchanged."],
                        "tradeoffs": ["The change costs migration effort."],
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "recommendation_requires_observation_or_inference_dependency",
            result.stderr,
        )

    def test_assertion_evidence_must_resolve_to_a_typed_record(self) -> None:
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/2",
                "evidence": [
                    {
                        "id": "observed-check",
                        "schema_version": "evidence-record/1",
                        "evidence_class": "evidence-runtime-observation",
                        "summary": "Captured process exit status.",
                        "provenance": [
                            {
                                "locator": "run:17",
                                "method": "captured process exit status",
                            }
                        ],
                    }
                ],
                "assertions": [
                    {
                        "id": "check-failed",
                        "type": "observation",
                        "text": "The check failed.",
                        "evidence": ["missing-evidence"],
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("unknown_evidence: missing-evidence", result.stderr)

    def test_malformed_evidence_record_cannot_ground_an_observation(self) -> None:
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/2",
                "evidence": [
                    {
                        "id": "asserted-state",
                        "schema_version": "evidence-record/1",
                        "evidence_class": "claim-without-evidence-class",
                        "summary": "An unsupported assertion.",
                        "provenance": "trust me",
                    }
                ],
                "assertions": [
                    {
                        "id": "state-observed",
                        "type": "observation",
                        "text": "The state was observed.",
                        "evidence": ["asserted-state"],
                    }
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("invalid_evidence_class", result.stderr)
        self.assertIn("evidence_requires_provenance_array", result.stderr)

    def test_execution_scope_must_be_covered_by_authorization(self) -> None:
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/2",
                "evidence": [
                    {
                        "id": "repo-state",
                        "schema_version": "evidence-record/1",
                        "evidence_class": "evidence-static-source-structure",
                        "summary": "The target exists at the inspected revision.",
                        "provenance": [
                            {
                                "locator": "git:HEAD",
                                "method": "read repository tree",
                            }
                        ],
                    }
                ],
                "assertions": [
                    {
                        "id": "state-observed",
                        "type": "observation",
                        "text": "The target exists.",
                        "evidence": ["repo-state"],
                    },
                    {
                        "id": "change-recommended",
                        "type": "recommendation",
                        "text": "Change the target.",
                        "depends_on": ["state-observed"],
                        "alternatives": ["Leave it unchanged."],
                        "tradeoffs": ["The change carries regression risk."],
                    },
                    {
                        "id": "change-decided",
                        "type": "decision",
                        "text": "Select the change.",
                        "depends_on": ["change-recommended"],
                        "owner": "repository owner",
                        "authority": "explicit selection",
                    },
                    {
                        "id": "change-authorized",
                        "type": "authorization",
                        "text": "Authorize the change to books/a.",
                        "depends_on": ["change-decided"],
                        "owner": "repository owner",
                        "authority": "explicit execution authority",
                        "scope": ["books/a"],
                    },
                    {
                        "id": "change-executed",
                        "type": "execution",
                        "text": "Changed books/b.",
                        "depends_on": ["change-authorized"],
                        "scope": ["books/b"],
                    },
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("execution_scope_exceeds_authorization: books/b", result.stderr)

    def test_accepted_receipt_requires_authorized_acceptance_lineage(self) -> None:
        result = self.run_validator(
            {
                "schema_version": "decision-receipt/2",
                "receipt_id": "receipt-1",
                "question": "Should the result be accepted?",
                "scope": ["doctrine/runtime"],
                "status": "accepted",
                "authority_boundary": {
                    "owner": None,
                    "authority_source": None,
                    "authorized_scope": ["doctrine/runtime"],
                },
                "evidence": [],
                "assertions": [],
                "alternatives": [
                    {
                        "option": "Do not accept.",
                        "disposition": "rejected",
                        "evidence": [],
                    }
                ],
                "source_locators": ["doctrine/runtime/README.md"],
                "corpus_version": "sha256:test",
                "verification_criteria": ["runtime checks pass"],
                "reopening_conditions": ["runtime contract changes"],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("accepted_receipt_requires_owner", result.stderr)
        self.assertIn("receipt_status_requires_acceptance_assertion", result.stderr)

    def test_dependency_cycles_cannot_simulate_grounded_lineage(self) -> None:
        result = self.run_validator(
            {
                "schema_version": "assertion-artifact/2",
                "evidence": [],
                "assertions": [
                    {
                        "id": "cause-a",
                        "type": "inference",
                        "text": "A explains B.",
                        "depends_on": ["cause-b"],
                        "rivals": ["No causal relation."],
                    },
                    {
                        "id": "cause-b",
                        "type": "inference",
                        "text": "B explains A.",
                        "depends_on": ["cause-a"],
                        "rivals": ["No causal relation."],
                    },
                ],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("dependency_cycle: cause-a -> cause-b -> cause-a", result.stderr)
        self.assertIn("assertion[cause-a]: lineage_has_no_observation", result.stderr)

    def test_complete_authorized_verified_receipt_is_valid(self) -> None:
        evidence = {
            "id": "check-result",
            "schema_version": "evidence-record/1",
            "evidence_class": "evidence-tests",
            "summary": "The scoped runtime checks passed.",
            "provenance": [
                {
                    "locator": "run:authority-contract",
                    "method": "captured test result",
                }
            ],
        }
        result = self.run_validator(
            {
                "schema_version": "decision-receipt/2",
                "receipt_id": "receipt-valid",
                "question": "Should the scoped result be accepted?",
                "scope": ["doctrine/runtime"],
                "status": "accepted",
                "authority_boundary": {
                    "owner": "repository owner",
                    "authority_source": "explicit acceptance authority",
                    "authorized_scope": ["doctrine/runtime"],
                },
                "evidence": [evidence],
                "assertions": [
                    {
                        "id": "result-observed",
                        "type": "observation",
                        "text": "The runtime checks passed.",
                        "evidence": ["check-result"],
                    },
                    {
                        "id": "accept-recommended",
                        "type": "recommendation",
                        "text": "Accept the scoped result.",
                        "depends_on": ["result-observed"],
                        "alternatives": ["Request further changes."],
                        "tradeoffs": ["Acceptance retains residual risk."],
                    },
                    {
                        "id": "accept-decided",
                        "type": "decision",
                        "text": "Select acceptance after execution and verification.",
                        "depends_on": ["accept-recommended"],
                        "owner": "repository owner",
                        "authority": "explicit selection authority",
                    },
                    {
                        "id": "change-authorized",
                        "type": "authorization",
                        "text": "Authorize the scoped change.",
                        "depends_on": ["accept-decided"],
                        "owner": "repository owner",
                        "authority": "explicit execution authority",
                        "scope": ["doctrine/runtime"],
                    },
                    {
                        "id": "change-executed",
                        "type": "execution",
                        "text": "The scoped change was executed.",
                        "depends_on": ["change-authorized"],
                        "scope": ["doctrine/runtime"],
                    },
                    {
                        "id": "change-verified",
                        "type": "verification",
                        "text": "The scoped change meets its checks.",
                        "depends_on": ["change-executed"],
                        "criteria": ["runtime checks pass"],
                        "evidence": ["check-result"],
                    },
                    {
                        "id": "change-accepted",
                        "type": "acceptance",
                        "text": "The scoped result is accepted.",
                        "depends_on": ["change-verified"],
                        "owner": "repository owner",
                        "authority": "explicit acceptance authority",
                    },
                ],
                "alternatives": [
                    {
                        "option": "Accept the scoped result.",
                        "disposition": "selected",
                        "evidence": ["check-result"],
                    }
                ],
                "source_locators": ["doctrine/runtime/README.md"],
                "corpus_version": "sha256:test",
                "verification_criteria": ["runtime checks pass"],
                "reopening_conditions": ["runtime contract changes"],
            }
        )

        self.assertEqual(0, result.returncode, result.stderr)

    def test_receipt_alternative_evidence_must_resolve(self) -> None:
        result = self.run_validator(
            {
                "schema_version": "decision-receipt/2",
                "receipt_id": "receipt-recommended",
                "question": "Should this change proceed?",
                "scope": ["doctrine/runtime"],
                "status": "recommended",
                "authority_boundary": {
                    "owner": None,
                    "authority_source": None,
                    "authorized_scope": ["doctrine/runtime"],
                },
                "evidence": [
                    {
                        "id": "repo-state",
                        "schema_version": "evidence-record/1",
                        "evidence_class": "evidence-static-source-structure",
                        "summary": "The current runtime structure was inspected.",
                        "provenance": [{"locator": "git:HEAD"}],
                    }
                ],
                "assertions": [
                    {
                        "id": "state-observed",
                        "type": "observation",
                        "text": "The runtime structure exists.",
                        "evidence": ["repo-state"],
                    },
                    {
                        "id": "change-recommended",
                        "type": "recommendation",
                        "text": "Change the runtime contract.",
                        "depends_on": ["state-observed"],
                        "alternatives": ["Leave it unchanged."],
                        "tradeoffs": ["The change breaks old artifacts."],
                    },
                ],
                "alternatives": [
                    {
                        "option": "Change the runtime contract.",
                        "disposition": "selected",
                        "evidence": ["missing-evidence"],
                    }
                ],
                "source_locators": ["doctrine/runtime/README.md"],
                "corpus_version": "sha256:test",
                "reopening_conditions": ["new evidence appears"],
            }
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("unknown_evidence: missing-evidence", result.stderr)


if __name__ == "__main__":
    unittest.main()
