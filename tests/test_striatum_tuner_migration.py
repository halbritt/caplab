"""Conformance checks for the non-destructive tuner absorption boundary."""

from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "history/striatum-tuner/migration-manifest.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class StriatumTunerMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_no_historical_run_was_admitted_or_destructively_migrated(self) -> None:
        self.assertEqual(
            self.manifest["schema_version"],
            "caplab-striatum-tuner-migration/1",
        )
        self.assertEqual(self.manifest["class_a_admissions"], [])
        effects = self.manifest["effects"]
        for key in (
            "copied_historical_measurements",
            "registered_historical_evidence",
            "deleted_source_paths",
            "rewritten_historical_evidence",
        ):
            self.assertEqual(effects[key], [], key)
        self.assertFalse(
            self.manifest["compatibility_assessment"][
                "live_executable_or_import_dependency_found"
            ]
        )
        self.assertEqual(
            self.manifest["compatibility_assessment"]["result"],
            "no-compatibility-adapter-or-service-created",
        )

    def test_every_classification_has_pinned_custody_or_an_explicit_noninventory(self) -> None:
        vocabulary = set(self.manifest["classification_vocabulary"])
        self.assertEqual(vocabulary, {"A", "B", "C", "D", "E"})
        identifiers: set[str] = set()
        for item in self.manifest["classifications"]:
            self.assertNotIn(item["id"], identifiers)
            identifiers.add(item["id"])
            self.assertIn(item["class"], vocabulary)
            self.assertNotEqual(item["class"], "A")
            if "source_paths" in item:
                self.assertGreater(len(item["source_paths"]), 0)
                for source in item["source_paths"]:
                    self.assertRegex(source["sha256"], SHA256)
                    self.assertFalse(Path(source["path"]).is_absolute())
            elif "git_ls_tree_sha256" in item:
                self.assertRegex(item["git_ls_tree_sha256"], SHA256)
            else:
                self.assertEqual(item["class"], "E")
                self.assertIsNone(item["content_hash"])
                self.assertIn("not-enumerated", item["disposition"])

        active_ports = [
            item for item in self.manifest["classifications"] if "caplab_target" in item
        ]
        self.assertEqual([item["id"] for item in active_ports], ["revbench-injector-and-scorer"])
        self.assertEqual(active_ports[0]["class"], "C")
        self.assertEqual(active_ports[0]["caplab_target"], "src/caplab/revbench")

    def test_active_python_has_no_tuner_import_or_compatibility_authority(self) -> None:
        forbidden_modules = {"striatum_tuner", "striatum-tuner"}
        violations: list[str] = []
        for source in sorted((ROOT / "src/caplab").rglob("*.py")):
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module is not None:
                    names = [node.module]
                if any(name.split(".", 1)[0] in forbidden_modules for name in names):
                    violations.append(str(source.relative_to(ROOT)))

        self.assertEqual(violations, [])
        self.assertTrue((ROOT / "src/caplab/revbench").is_dir())
        self.assertFalse((ROOT / "src/caplab/striatum_tuner").exists())
        self.assertFalse((ROOT / "src/caplab/tuner_compat.py").exists())


if __name__ == "__main__":
    unittest.main()
