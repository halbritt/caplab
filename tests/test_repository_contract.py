"""Repository-level contracts for standalone CAPLAB."""

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


class RepositoryContractTests(unittest.TestCase):
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

    def test_active_decisions_bind_standalone_p4_and_p5_authority(self) -> None:
        adr_0007 = (
            ROOT / "docs/decisions/adr-0007-caplab-v0-cli-runtime.md"
        ).read_text(encoding="utf-8")
        adr_0008 = (
            ROOT / "docs/decisions/adr-0008-standalone-repository.md"
        ).read_text(encoding="utf-8")
        adr_0009 = (
            ROOT / "docs/decisions/adr-0009-caplab-p5-failure-and-recovery-campaign.md"
        ).read_text(encoding="utf-8")
        plan = (
            ROOT / "docs/product/plans/plan-agent-capability-lab-v0.md"
        ).read_text(encoding="utf-8")

        self.assertIn("status: decided", adr_0007)
        self.assertIn("status: decided", adr_0008)
        self.assertIn("status: decided", adr_0009)
        self.assertIn("status: authorized", plan)
        for record in (adr_0007, adr_0008):
            self.assertIn("2026-07-22T23:59:59Z", record)
            self.assertIn("P4", record)
        for record in (adr_0009, plan):
            self.assertIn("2026-07-23T23:59:59Z", record)
            self.assertIn("P5", record)
        self.assertIn("src/caplab/runtime/**", plan)
        self.assertIn("P6 and later checkpoints", plan)

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
        self.assertEqual(manifest["admission_status"], "not_admitted")
        self.assertIs(manifest["historical_evidence_copied"], False)
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
