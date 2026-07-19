"""Repository-level contracts for standalone CAPLAB."""

import hashlib
import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


class RepositoryContractTests(unittest.TestCase):
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
