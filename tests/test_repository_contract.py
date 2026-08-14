"""Repository-level contracts for standalone CAPLAB."""

import hashlib
import json
import re
import tomllib
import unittest
from pathlib import Path

from caplab.subject_identity import (
    NativeAgentSystemContractError,
    load_native_agent_system_policy,
    validate_native_agent_systems,
)
from caplab.ladder_subject import validate_ladder_subject


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


class RepositoryContractTests(unittest.TestCase):
    def test_native_agent_system_contract_uses_native_striatum_tuples(self) -> None:
        policy_path = ROOT / "docs/product/contracts/native-agent-systems.json"
        policy = load_native_agent_system_policy(policy_path)
        self.assertEqual(policy["policy"], "native-harness-required")
        self.assertEqual(
            policy["source_observation"]["commit"],
            "9178e74314ed3d65328b60cec0650471cc15e6b3",
        )
        validate_native_agent_systems(
            policy,
            {
                "fable": {
                    "tuple_id": "claude-fable-5-max",
                    "model_id": "claude-fable-5",
                    "native_harness_id": "claude-code",
                    "effort": "max",
                    "command": [
                        "/usr/bin/env",
                        "CLAUDE_CONFIG_DIR=/tmp/caplab-claude",
                        "claude",
                        "-p",
                        "--model",
                        "claude-fable-5",
                        "--effort",
                        "max",
                        "--output-format",
                        "text",
                    ],
                    "version_command": [
                        "/usr/bin/env",
                        "CLAUDE_CONFIG_DIR=/tmp/caplab-claude",
                        "claude",
                        "--version",
                    ],
                },
                "gpt": {
                    "tuple_id": "codex-terra-max",
                    "model_id": "gpt-5.6-terra",
                    "native_harness_id": "codex",
                    "effort": "max",
                    "command": [
                        "/usr/bin/env",
                        "CODEX_HOME=/tmp/caplab-codex",
                        "codex",
                        "exec",
                        "-m",
                        "gpt-5.6-terra",
                        "-c",
                        "model_reasoning_effort=max",
                    ],
                    "version_command": [
                        "/usr/bin/env",
                        "CODEX_HOME=/tmp/caplab-codex",
                        "codex",
                        "--version",
                    ],
                },
            },
        )

    def test_shared_proxy_harness_cannot_impersonate_native_systems(self) -> None:
        policy = load_native_agent_system_policy(
            ROOT / "docs/product/contracts/native-agent-systems.json"
        )
        proxy = {
            "fable": {
                "tuple_id": "claude-fable-5-max",
                "model_id": "claude-fable-5",
                "native_harness_id": "terminus-2",
                "effort": "max",
                "command": ["harbor", "exec", "--model", "openrouter/anthropic/claude-fable-5"],
                "version_command": ["harbor", "--version"],
            }
        }
        with self.assertRaisesRegex(
            NativeAgentSystemContractError, "native_agent_tuple_mismatch"
        ):
            validate_native_agent_systems(policy, proxy)

    def test_advisory_ladder_maps_every_native_codex_tuple(self) -> None:
        base_policy = ROOT / "docs/product/contracts/native-agent-systems.json"
        tuple_policy = (
            ROOT
            / "docs/product/studies/advisory-selection-001/native-agent-systems.json"
        )
        for model in ("luna", "terra", "sol"):
            for effort in ("low", "medium", "high", "xhigh"):
                validate_ladder_subject(
                    base_policy,
                    tuple_policy,
                    f"gpt-5.6-{model}",
                    effort,
                    [
                        "codex",
                        "exec",
                        "-m",
                        f"gpt-5.6-{model}",
                        "-c",
                        f"model_reasoning_effort={effort}",
                    ],
                )

    def test_proxy_live_manifests_are_withdrawn(self) -> None:
        for relative in (
            "docs/product/studies/preference-001/live-manifest.json",
            "docs/product/studies/review-dissent-001/live-manifest.json",
        ):
            manifest = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "withdrawn")
            self.assertEqual(manifest["withdrawal_authority"], "adr-0039")

    def test_canonical_repository_identity_is_caplab(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(
            metadata["project"]["urls"]["Repository"],
            "https://github.com/halbritt/caplab",
        )
        decision = (
            ROOT / "docs/decisions/adr-0019-canonical-caplab-repository.md"
        ).read_text(encoding="utf-8")
        self.assertIn("status: decided", decision)
        self.assertIn("/home/halbritt/git/caplab", decision)
        self.assertIn("history/ethogram/", decision)

    def test_ci_installs_locked_runtime_before_repository_gate(self) -> None:
        # GitHub Actions run 29702961943 failed when botocore was absent.
        workflow = (ROOT / ".github/workflows/check.yml").read_text(encoding="utf-8")
        self.assertIn("uses: actions/checkout@v6", workflow)
        self.assertIn("uses: actions/setup-python@v6", workflow)
        install = (
            "python -m pip install --require-hashes "
            "-r src/caplab/runtime/requirements.lock"
        )
        self.assertIn(install, workflow)
        self.assertLess(workflow.index(install), workflow.index("make check"))

    def test_caplab_runtime_has_no_books_or_doctrine_dependency(self) -> None:
        forbidden_import = re.compile(
            r"^\s*(?:from|import)\s+(?:books|pincite|doctrine)(?:\.|\s|$)",
            re.MULTILINE,
        )
        violations: list[str] = []
        for module in sorted((ROOT / "src/caplab").rglob("*.py")):
            if forbidden_import.search(module.read_text(encoding="utf-8")):
                violations.append(str(module.relative_to(ROOT)))

        self.assertEqual(violations, [])

    def test_qualification_contract_pins_artifact_not_runtime_registry(self) -> None:
        claim_schema = json.loads(
            (
                ROOT
                / "docs/product/contracts/qualification-claim-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        export_schema = json.loads(
            (
                ROOT
                / "docs/product/contracts/qualification-export-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        contract = (
            ROOT / "docs/product/contracts/caplab-qualification-contract-v1.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            claim_schema["properties"]["schema_version"]["const"],
            "caplab-qualification-claim/1",
        )
        self.assertEqual(
            claim_schema["$defs"]["qualification"]["properties"]["status"][
                "enum"
            ],
            ["qualified", "unqualified", "advisory", "unmeasured"],
        )
        self.assertEqual(
            export_schema["properties"]["schema_version"]["const"],
            "caplab-qualification-export/1",
        )
        self.assertEqual(
            export_schema["properties"]["producer"]["properties"]["product"],
            {"const": "caplab"},
        )
        for forbidden in (
            "mutable `current` flag",
            "provider health",
            "quota",
            "placement",
            "Dispatch policy",
        ):
            self.assertIn(forbidden, contract)
        self.assertIn(
            "The reserved covariate name for migrated tuner outcomes is\n"
            "`downstream_fate`",
            contract,
        )

    def test_qualification_schema_catalog_pins_local_bytes(self) -> None:
        contracts = ROOT / "docs/product/contracts"
        catalog = json.loads(
            (contracts / "qualification-schema-catalog-v1.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            catalog["schema_version"], "caplab-qualification-schema-catalog/1"
        )
        paths = [resource["path"] for resource in catalog["resources"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        for resource in catalog["resources"]:
            schema_bytes = (contracts / resource["path"]).read_bytes()
            schema = json.loads(schema_bytes)
            self.assertEqual(schema["$id"], resource["id"])
            self.assertEqual(
                hashlib.sha256(schema_bytes).hexdigest(), resource["sha256"]
            )

    def test_active_decisions_bind_ordered_standalone_p4_p5_and_p6_authority(
        self,
    ) -> None:
        adr_0007 = (
            ROOT / "docs/decisions/adr-0007-caplab-v0-cli-runtime.md"
        ).read_text(encoding="utf-8")
        adr_0008 = (
            ROOT / "docs/decisions/adr-0008-standalone-repository.md"
        ).read_text(encoding="utf-8")
        adr_0009 = (
            ROOT / "docs/decisions/adr-0009-caplab-p5-failure-and-recovery-campaign.md"
        ).read_text(encoding="utf-8")
        adr_0010 = (
            ROOT / "docs/decisions/adr-0010-caplab-p5-corrective-continuation.md"
        ).read_text(encoding="utf-8")
        adr_0014 = (
            ROOT / "docs/decisions/adr-0014-caplab-p5-purge-and-p6-admission.md"
        ).read_text(encoding="utf-8")
        adr_0016 = (
            ROOT
            / "docs/decisions/adr-0016-caplab-backlog-drain-afk-implementation.md"
        ).read_text(encoding="utf-8")
        plan = (
            ROOT / "docs/product/plans/plan-agent-capability-lab-v0.md"
        ).read_text(encoding="utf-8")

        self.assertIn("status: decided", adr_0007)
        self.assertIn("status: decided", adr_0008)
        self.assertIn("status: decided", adr_0009)
        self.assertIn("status: decided", adr_0010)
        self.assertIn("status: decided", adr_0014)
        self.assertIn("status: decided", adr_0016)
        self.assertIn("status: authorized", plan)
        for record in (adr_0007, adr_0008):
            self.assertIn("2026-07-22T23:59:59Z", record)
            self.assertIn("P4", record)
        for record in (adr_0009, adr_0010, plan):
            self.assertIn("2026-07-23T23:59:59Z", record)
            self.assertIn("P5", record)
        for record in (adr_0014, plan):
            self.assertIn("2026-07-24T23:59:59Z", record)
            self.assertIn("CAPLAB-24/P6", record)
        self.assertIn("does not authorize CAPLAB-25/P7", adr_0014)
        for checkpoint in ("CAPLAB-25/P7", "CAPLAB-26/P8", "CAPLAB-28/P10"):
            self.assertIn(checkpoint, adr_0016)
        self.assertIn("Stage A creates no database row", adr_0016)
        self.assertIn("live P7 data", plan)
        self.assertIn("access remains unavailable", plan)
        self.assertIn("Human inference, eligibility", plan)
        self.assertIn("unauthorized", plan)
        self.assertIn("src/caplab/runtime/**", plan)
        self.assertIn("src/caplab/admission/**", plan)

    def test_local_markdown_links_resolve(self) -> None:
        missing: list[str] = []
        for document in sorted(ROOT.rglob("*.md")):
            for target in MARKDOWN_LINK.findall(document.read_text(encoding="utf-8")):
                path_text = target.split("#", 1)[0]
                if not path_text or "://" in path_text:
                    continue
                target_path = (document.parent / path_text).resolve()
                if not target_path.exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {target}")

        self.assertEqual(missing, [])

    def test_dashboard_source_binding_identifies_projection_and_external_sources(self) -> None:
        manifest_path = ROOT / "docs/manifests/dashboard-study-001-source.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        projection = manifest["projection"]
        projection_bytes = (ROOT / projection["path"]).read_bytes()

        self.assertEqual(manifest["manifest_version"], "caplab-source-binding/1")
        self.assertEqual(manifest["admission_status"], "restricted_admitted")
        self.assertIs(manifest["historical_evidence_copied"], True)
        self.assertEqual(
            manifest["registration"],
            {
                "manifest_sha256": "d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e",
                "record_count": 684,
                "unique_content_count": 325,
                "assignment_count": 20,
                "attempt_count": 20,
                "outcome_count": 20,
                "disposition": "restricted-admission",
                "verification_status": "pass",
            },
        )
        self.assertEqual(hashlib.sha256(projection_bytes).hexdigest(), projection["sha256"])
        self.assertEqual(projection["origin_repository"], "halbritt/books")
        self.assertEqual(
            projection["origin_commit"],
            "e4636d2628adbbfca953734d4dc7cdfa91d72b04",
        )
        self.assertEqual(
            projection["origin_path"],
            "caplab/dashboard/studies/caplab-study-001.json",
        )
        self.assertEqual(
            [source["artifact"] for source in manifest["sources"]],
            ["preregistration", "result_record", "trial_csv"],
        )
        for source in manifest["sources"]:
            self.assertEqual(source["repository"], "halbritt/books")
            self.assertTrue(source["path"])
            self.assertRegex(source["commit"], r"\A[0-9a-f]{40}\Z")
            self.assertRegex(source["sha256"], r"\A[0-9a-f]{64}\Z")


if __name__ == "__main__":
    unittest.main()
