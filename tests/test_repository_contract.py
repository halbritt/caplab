"""Repository-level contracts for standalone CAPLAB."""

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path

from caplab.ladder_subject import validate_ladder_subject
from caplab.subject_identity import (
    CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256,
    NativeAgentSystemContractError,
    load_native_agent_system_policy,
    validate_native_agent_systems,
)
from caplab.runtime.canonical import canonical_json, sha256_hex

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")
HISTORICAL_CUSTODY_ROOTS = (
    ROOT / "history/ethogram",
    ROOT / "history/striatum-tuner/source",
    # Advisory run captures: subject-visible inputs and written outputs held
    # verbatim as evidence. Their links belong to the artifacts under review,
    # not to this repository's documentation, and rewriting them would
    # falsify the capture. Completed runs are pruned to arms outputs; an
    # in-flight run additionally holds materialized workspaces.
    ROOT / "advisory/runs",
)


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
                        (
                            "CLAUDE_CONFIG_DIR=/home/halbritt/.local/share/"
                            "striatum/harness-config/claude-code"
                        ),
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
                        (
                            "CLAUDE_CONFIG_DIR=/home/halbritt/.local/share/"
                            "striatum/harness-config/claude-code"
                        ),
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
                        (
                            "CODEX_HOME=/home/halbritt/.local/share/"
                            "striatum/harness-config/codex"
                        ),
                        "codex",
                        "exec",
                        "-m",
                        "gpt-5.6-terra",
                        "-c",
                        "model_reasoning_effort=max",
                    ],
                    "version_command": [
                        "/usr/bin/env",
                        (
                            "CODEX_HOME=/home/halbritt/.local/share/"
                            "striatum/harness-config/codex"
                        ),
                        "codex",
                        "--version",
                    ],
                },
            },
        )

        self.assertEqual(
            sha256_hex(canonical_json(policy)),
            CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256,
        )

    def test_native_agent_identity_rejects_late_selector_overrides(self) -> None:
        policy = load_native_agent_system_policy(
            ROOT / "docs/product/contracts/native-agent-systems.json"
        )
        subjects = {
            "codex-model": ["--model", "swapped/model"],
            "codex-compact-model": ["-mswapped/model"],
            "codex-effort": ["-c", "model_reasoning_effort=low"],
            "codex-compact-provider": ["-cmodel_provider=local"],
            "codex-provider": ["--config", "model_provider=local"],
            "codex-profile": ["--profile", "attacker"],
            "codex-compact-profile": ["-pattacker"],
        }
        for subject_id, override in subjects.items():
            with self.subTest(subject_id=subject_id):
                subject = {
                    "tuple_id": "codex-terra-max",
                    "model_id": "gpt-5.6-terra",
                    "native_harness_id": "codex",
                    "effort": "max",
                    "command": [
                        "codex",
                        "exec",
                        "-m",
                        "gpt-5.6-terra",
                        "-c",
                        "model_reasoning_effort=max",
                        *override,
                    ],
                    "version_command": ["codex", "--version"],
                }
                with self.assertRaisesRegex(
                    NativeAgentSystemContractError,
                    "native_agent_command_identity_override",
                ):
                    validate_native_agent_systems(policy, {subject_id: subject})

        claude = {
            "tuple_id": "claude-fable-5-max",
            "model_id": "claude-fable-5",
            "native_harness_id": "claude-code",
            "effort": "max",
            "command": [
                "claude",
                "-p",
                "--model",
                "claude-fable-5",
                "--effort",
                "max",
                "--effort=low",
            ],
            "version_command": ["claude", "--version"],
        }
        with self.assertRaisesRegex(
            NativeAgentSystemContractError,
            "native_agent_command_identity_override",
        ):
            validate_native_agent_systems(policy, {"claude-effort": claude})

        for override in (["-mswapped/model"], ["--settings", "/tmp/attacker.json"]):
            with self.subTest(claude_override=override):
                changed = dict(claude)
                changed["command"] = [*claude["command"][:-1], *override]
                with self.assertRaisesRegex(
                    NativeAgentSystemContractError,
                    "native_agent_command_identity_override",
                ):
                    validate_native_agent_systems(policy, {"claude": changed})

    def test_native_agent_identity_rejects_wrapper_and_environment_overrides(
        self,
    ) -> None:
        policy = load_native_agent_system_policy(
            ROOT / "docs/product/contracts/native-agent-systems.json"
        )
        subject = {
            "tuple_id": "codex-terra-max",
            "model_id": "gpt-5.6-terra",
            "native_harness_id": "codex",
            "effort": "max",
            "command": [
                "/tmp/codex",
                "exec",
                "-m",
                "gpt-5.6-terra",
                "-c",
                "model_reasoning_effort=max",
            ],
            "version_command": ["/tmp/codex", "--version"],
        }
        with self.assertRaisesRegex(
            NativeAgentSystemContractError, "native_agent_executable_mismatch"
        ):
            validate_native_agent_systems(policy, {"wrapper": subject})

        for environment_prefix in (
            ["/usr/bin/env", "OPENAI_MODEL=swapped/model"],
            ["/usr/bin/env", "PATH=/tmp/native-wrapper-bin"],
            ["/usr/bin/env", "LD_PRELOAD=/tmp/hostile.so"],
            ["/usr/bin/env", "CODEX_HOME=/tmp/hostile"],
            ["/usr/bin/env", "CLAUDE_CODE_USE_BEDROCK=1"],
            ["/usr/bin/env", "CLAUDE_CODE_USE_VERTEX=1"],
            ["/usr/bin/env", "--split-string=/tmp/native-wrapper"],
        ):
            with self.subTest(environment_prefix=environment_prefix):
                subject["command"] = [
                    *environment_prefix,
                    "codex",
                    "exec",
                    "-m",
                    "gpt-5.6-terra",
                    "-c",
                    "model_reasoning_effort=max",
                ]
                subject["version_command"] = ["codex", "--version"]
                with self.assertRaisesRegex(
                    NativeAgentSystemContractError,
                    "native_agent_environment_identity_override",
                ):
                    validate_native_agent_systems(policy, {"environment": subject})

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
                "command": [
                    "harbor",
                    "exec",
                    "--model",
                    "openrouter/anthropic/claude-fable-5",
                ],
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
                    observed_harness_version="codex-cli 0.146.0",
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
                ROOT / "docs/product/contracts/qualification-claim-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        export_schema = json.loads(
            (
                ROOT / "docs/product/contracts/qualification-export-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        records_schema = json.loads(
            (
                ROOT / "docs/product/contracts/qualification-records-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        revbench_schema = json.loads(
            (ROOT / "docs/product/contracts/revbench-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        contract = (
            ROOT / "docs/product/contracts/caplab-qualification-contract-v1.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            claim_schema["properties"]["schema_version"]["const"],
            "caplab-qualification-claim/1",
        )
        self.assertEqual(
            claim_schema["$defs"]["qualification"]["properties"]["status"]["enum"],
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
        self.assertEqual(
            records_schema["$defs"]["basis_authorization"]["required"],
            [
                "schema_version",
                "authorization_id",
                "authority_source_ref",
                "authorized_by",
                "delegate_or_mechanism",
                "binding_ids",
                "capability",
                "experiment",
                "protocol_ref",
                "corpus_ref",
                "case_selection_ref",
                "method_ref",
                "basis_kind",
                "basis_role",
                "valid_from",
                "valid_until",
            ],
        )
        self.assertEqual(
            records_schema["$defs"]["case_selection"]["properties"]["schema_version"][
                "const"
            ],
            "caplab-case-selection-manifest/1",
        )
        self.assertIn("(--measurement MEASUREMENT | --binding BINDING)", contract)
        self.assertEqual(
            revbench_schema["$defs"]["native_attempt_attestation"]["required"],
            [
                "schema_version",
                "attestation_id",
                "experiment_id",
                "case_id",
                "arm",
                "assignment_index",
                "observed_at",
                "observed_binding",
                "native_system_contract_ref",
                "execution_authorization_ref",
                "version_observation_ref",
                "capture_ref",
                "prompt_ref",
                "output_ref",
            ],
        )
        self.assertEqual(
            revbench_schema["$defs"]["native_review_attempt"]["properties"][
                "attempt_id"
            ]["pattern"],
            "^attempt-[0-9a-f]{64}$",
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
        self.assertIn("revbench-error-v1.schema.json", paths)
        self.assertIn("revbench-live-native-v1.schema.json", paths)
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        for resource in catalog["resources"]:
            schema_bytes = (contracts / resource["path"]).read_bytes()
            schema = json.loads(schema_bytes)
            self.assertEqual(schema["$id"], resource["id"])
            self.assertEqual(
                hashlib.sha256(schema_bytes).hexdigest(), resource["sha256"]
            )

    def test_ordinary_wheel_stamps_commit_and_packages_live_contracts(self) -> None:
        system_python = Path("/usr/bin/python3")
        python = (
            str(system_python) if system_python.is_file() else shutil.which("python3")
        )
        if python is None:
            self.fail("python3 is required for the wheel contract")
        expected_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        contracts = (
            "qualification-schema-catalog-v1.json",
            "qualification-claim-v1.schema.json",
            "qualification-export-v1.schema.json",
            "qualification-records-v1.schema.json",
            "revbench-error-v1.schema.json",
            "revbench-live-native-v1.schema.json",
            "revbench-v1.schema.json",
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wheels = root / "wheels"
            wheels.mkdir()
            subprocess.run(
                [
                    python,
                    "-m",
                    "pip",
                    "wheel",
                    ".",
                    "--no-deps",
                    "--no-build-isolation",
                    "--wheel-dir",
                    str(wheels),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            artifacts = list(wheels.glob("*.whl"))
            self.assertEqual(len(artifacts), 1)
            with zipfile.ZipFile(artifacts[0]) as wheel:
                self.assertEqual(
                    wheel.read("caplab/_source_commit.txt"),
                    (expected_commit + "\n").encode("ascii"),
                )
                for live_member in (
                    "codex-native-bundle-v1.json",
                    "resolv-public-v1.conf",
                    "nsswitch-public-v1.conf",
                ):
                    bundle = f"caplab/revbench/contracts/{live_member}"
                    self.assertEqual(
                        wheel.read(bundle),
                        (ROOT / "src" / bundle).read_bytes(),
                    )
                for filename in contracts:
                    self.assertEqual(
                        wheel.read(f"caplab/qualification/contracts/{filename}"),
                        (ROOT / "docs/product/contracts" / filename).read_bytes(),
                    )
                installed = root / "ambient" / "site-packages"
                wheel.extractall(installed)

            observed = subprocess.run(
                [
                    python,
                    "-I",
                    "-c",
                    (
                        "import json,sys;"
                        f"sys.path.insert(0,{str(installed)!r});"
                        "from caplab.producer import producer_identity;"
                        "print(json.dumps(producer_identity()))"
                    ),
                ],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(json.loads(observed.stdout)[1], expected_commit)

            stamp = installed / "caplab" / "_source_commit.txt"
            stamp.write_text("$Format:%H$\n", encoding="ascii")
            ambient = root / "ambient"
            subprocess.run(["git", "init", "-q"], cwd=ambient, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=CAPLAB",
                    "-c",
                    "user.email=x@x",
                    "commit",
                    "--allow-empty",
                    "-qm",
                    "ambient",
                ],
                cwd=ambient,
                check=True,
            )
            refused = subprocess.run(
                [
                    python,
                    "-I",
                    "-c",
                    (
                        "import sys;"
                        f"sys.path.insert(0,{str(installed)!r});"
                        "from caplab.producer import producer_identity;"
                        "producer_identity()"
                    ),
                ],
                cwd=ambient,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("producer_commit_checkout_invalid", refused.stderr)

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
            ROOT / "docs/decisions/adr-0016-caplab-backlog-drain-afk-implementation.md"
        ).read_text(encoding="utf-8")
        plan = (ROOT / "docs/product/plans/plan-agent-capability-lab-v0.md").read_text(
            encoding="utf-8"
        )

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
            if any(
                document.is_relative_to(custody_root)
                for custody_root in HISTORICAL_CUSTODY_ROOTS
            ):
                continue
            for target in MARKDOWN_LINK.findall(document.read_text(encoding="utf-8")):
                path_text = target.split("#", 1)[0]
                if not path_text or "://" in path_text:
                    continue
                target_path = (document.parent / path_text).resolve()
                if not target_path.exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {target}")

        self.assertEqual(missing, [])

    def test_dashboard_source_binding_identifies_projection_and_external_sources(
        self,
    ) -> None:
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
        self.assertEqual(
            hashlib.sha256(projection_bytes).hexdigest(), projection["sha256"]
        )
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
