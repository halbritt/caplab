"""Conformance checks for the non-destructive tuner absorption boundary."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "history/striatum-tuner/migration-manifest.json"
SOURCE_ROOT = ROOT / "history/striatum-tuner/source"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class StriatumTunerMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    @staticmethod
    def _git(*args: str) -> bytes:
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout

    def test_tracked_history_is_imported_exactly_without_evidence_admission(
        self,
    ) -> None:
        self.assertEqual(
            self.manifest["schema_version"],
            "caplab-striatum-tuner-migration/1",
        )
        self.assertEqual(self.manifest["class_a_admissions"], [])
        source = self.manifest["source"]
        imported = self.manifest["historical_import"]
        self.assertEqual(source["tracked_file_count"], 188)
        self.assertEqual(imported["tree"], source["tree"])
        self.assertFalse(imported["active_python_package"])
        self.assertFalse(imported["ci_root"])
        self.assertFalse(imported["caplab_evidence_registration"])

        imported_tree = (
            self._git("rev-parse", "HEAD:history/striatum-tuner/source")
            .decode("ascii")
            .strip()
        )
        self.assertEqual(imported_tree, source["tree"])
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", source["commit"], "HEAD"],
            cwd=ROOT,
            check=True,
        )

        tracked_listing = self._git("ls-tree", "-r", source["commit"])
        tracked_names = self._git("ls-tree", "-r", "--name-only", source["commit"])
        self.assertEqual(len(tracked_names.splitlines()), source["tracked_file_count"])
        self.assertEqual(
            hashlib.sha256(tracked_listing).hexdigest(),
            source["git_ls_tree_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(tracked_names).hexdigest(),
            source["name_inventory_sha256"],
        )

        effects = self.manifest["effects"]
        self.assertEqual(
            effects["imported_tracked_source_path"],
            "history/striatum-tuner/source",
        )
        self.assertEqual(effects["imported_tracked_source_tree"], source["tree"])
        for key in (
            "admitted_historical_measurements",
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

    def test_every_classification_has_pinned_custody_or_an_explicit_noninventory(
        self,
    ) -> None:
        vocabulary = set(self.manifest["classification_vocabulary"])
        self.assertEqual(vocabulary, {"A", "B", "C", "D", "E"})
        identifiers: set[str] = set()
        class_d_paths: set[str] = set()
        tracked_names = {
            line.decode("utf-8")
            for line in self._git(
                "ls-tree",
                "-r",
                "--name-only",
                self.manifest["source"]["commit"],
            ).splitlines()
        }
        classified_names: set[str] = set()
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
                    source_bytes = (SOURCE_ROOT / source["path"]).read_bytes()
                    self.assertEqual(
                        hashlib.sha256(source_bytes).hexdigest(),
                        source["sha256"],
                        source["path"],
                    )
                    if item["class"] == "D":
                        class_d_paths.add(source["path"])
                    classified_names.add(source["path"])
                if item["class"] == "D":
                    class_d_paths.update(item.get("related_mixed_paths", []))
            elif "git_ls_tree_sha256" in item:
                self.assertRegex(item["git_ls_tree_sha256"], SHA256)
                paths = [
                    part.strip().removesuffix("/")
                    for part in item["source_path"].split(";")
                ]
                listing = self._git(
                    "ls-tree", "-r", self.manifest["source"]["commit"], "--", *paths
                )
                self.assertEqual(
                    hashlib.sha256(listing).hexdigest(),
                    item["git_ls_tree_sha256"],
                    item["id"],
                )
                for path in paths:
                    classified_names.update(
                        name
                        for name in tracked_names
                        if name == path or name.startswith(path + "/")
                    )
            else:
                self.assertEqual(item["class"], "E")
                self.assertIsNone(item["content_hash"])
                self.assertIn("not-enumerated", item["disposition"])

            if item["id"] != "generated-private-and-untracked-material":
                self.assertIn("imported", item["disposition"], item["id"])

        self.assertEqual(classified_names, tracked_names)

        excluded_class_d_paths = {
            path
            for item in self.manifest["classifications"]
            for path in item.get("excluded_class_d_paths", [])
        }
        self.assertLessEqual(excluded_class_d_paths, class_d_paths)
        self.assertIn("jobs/qwen35b_moe/score_fate.py", class_d_paths)
        self.assertIn("train/review_dpo.yaml", class_d_paths)
        self.assertIn("eval.py", class_d_paths)
        self.assertIn(
            "README.md",
            {
                source["path"]
                for item in self.manifest["classifications"]
                for source in item.get("source_paths", [])
            },
        )
        self.assertIn(
            ".gitignore",
            {
                source["path"]
                for item in self.manifest["classifications"]
                for source in item.get("source_paths", [])
            },
        )
        self.assertIn(
            "tests/test_qwen35b_moe_job.py",
            {
                source["path"]
                for item in self.manifest["classifications"]
                for source in item.get("source_paths", [])
            },
        )

        active_ports = [
            item for item in self.manifest["classifications"] if "caplab_target" in item
        ]
        self.assertEqual(
            [item["id"] for item in active_ports], ["revbench-injector-and-scorer"]
        )
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
        for package_surface in ("pyproject.toml", "setup.py", "Makefile"):
            self.assertNotIn(
                "history/striatum-tuner/source",
                (ROOT / package_surface).read_text(encoding="utf-8"),
                package_surface,
            )


if __name__ == "__main__":
    unittest.main()
