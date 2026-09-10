import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reviewer_population.py"
SPEC = importlib.util.spec_from_file_location("reviewer_population", SCRIPT)
population = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(population)


class ReviewerPopulationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repository = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Census test")
        self.git("config", "user.email", "census@example.invalid")
        self.commit("README.md", "initial\n", "2026-08-01T00:00:00Z")

    def git(self, *arguments, date=None):
        environment = dict(os.environ)
        if date:
            environment.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        return subprocess.run(["git", "-C", str(self.repository), *arguments], env=environment,
                              check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, path, content, date, message="change"):
        destination = self.repository / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
        self.git("add", "--", path)
        self.git("-c", "commit.gpgsign=false", "commit", "-m", message, date=date)
        return self.git("rev-parse", "HEAD")

    def report(self, tip=None):
        source = {"name": "test", "path": str(self.repository), "tip": tip or self.git("rev-parse", "HEAD")}
        return population.census([source], "2026-09-01T00:00:00Z", "2026-09-10T00:00:00Z")

    def test_pinned_tip_ignores_later_commits_worktree_and_messages(self):
        tip = self.commit("work.py", "x = 1\n", "2026-09-01T00:00:00Z", "not a fix")
        before = self.report(tip)
        self.commit("other.go", "package other\n", "2026-09-02T00:00:00Z", "fix defect")
        (self.repository / "work.py").write_text("uncommitted\n")
        self.assertEqual(before, self.report(tip))
        rows = before["repositories"][0]["commits"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["commit"], tip)
        self.assertNotIn("message", rows[0])

    def test_nonmonotonic_dates_are_filtered_without_losing_ancestors(self):
        inside = self.commit("work.py", "x = 1\n", "2026-09-02T00:00:00Z")
        self.commit("work.py", "x = 2\n", "2026-08-30T00:00:00Z")
        self.commit("work.py", "x = 3\n", "2026-09-10T00:00:00Z")
        rows = self.report()["repositories"][0]["commits"]
        self.assertEqual([row["commit"] for row in rows], [inside])

    def test_local_replace_refs_cannot_change_the_pinned_history(self):
        tip = self.commit("work.py", "x = 1\n", "2026-09-02T00:00:00Z")
        before = self.report(tip)
        replacement = self.git("commit-tree", tip + "^{tree}", "-m", "replacement", date="2026-09-03T00:00:00Z")
        self.git("replace", tip, replacement)
        self.assertEqual(before, self.report(tip))

    def test_exclusions_and_unusual_paths_retain_exact_blob_identity(self):
        self.commit("history/old.py", "historical\n", "2026-09-02T00:00:00Z")
        self.commit("notes.md", "docs\n", "2026-09-03T00:00:00Z")
        strange = "src/a\tline\nb.py"
        tip = self.commit(strange, "x = 3\n", "2026-09-04T00:00:00Z")
        report = self.report()["repositories"][0]
        self.assertEqual(report["eligible_commits"], 1)
        self.assertEqual(report["mainline_commits_in_window"], 3)
        self.assertEqual(report["commits"][0]["changed_paths"][0]["exclusion"], "excluded-prefix:history/")
        entry = report["commits"][2]["changed_paths"][0]
        self.assertEqual(entry["path"], strange)
        self.assertEqual(entry["after_blob"], self.git("rev-parse", tip + ":" + strange))
        self.assertEqual(entry["added_lines"], 1)

    def test_merge_is_one_change_against_first_parent(self):
        self.git("checkout", "-b", "side")
        side = self.commit("side.py", "x = 1\n", "2026-09-02T00:00:00Z")
        self.git("checkout", "main")
        self.commit("main.py", "x = 2\n", "2026-09-03T00:00:00Z")
        self.git("-c", "commit.gpgsign=false", "merge", "--no-ff", "side", "-m", "merge", date="2026-09-04T00:00:00Z")
        rows = self.report()["repositories"][0]["commits"]
        self.assertEqual(len(rows), 2)
        self.assertNotIn(side, [row["commit"] for row in rows])
        self.assertEqual(len(rows[-1]["parents"]), 2)
        self.assertEqual([p["path"] for p in rows[-1]["changed_paths"]], ["side.py"])

    def test_deleted_code_is_still_an_eligible_change(self):
        self.commit("work.py", "x = 1\n", "2026-08-02T00:00:00Z")
        self.git("rm", "work.py")
        self.git("-c", "commit.gpgsign=false", "commit", "-m", "remove", date="2026-09-03T00:00:00Z")
        row = self.report()["repositories"][0]["commits"][0]
        self.assertTrue(row["eligible"])
        self.assertEqual(row["changed_paths"][0]["status"], "D")
        self.assertEqual(row["changed_paths"][0]["deleted_lines"], 1)

    def test_rejects_unpinned_sources_duplicate_repos_and_naive_time(self):
        source = {"name": "test", "path": str(self.repository), "tip": "main"}
        with self.assertRaisesRegex(ValueError, "full commit"):
            population.validate_sources([source])
        source["tip"] = self.git("rev-parse", "HEAD")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            population.validate_sources([source, {**source, "name": "second"}])
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            population.timestamp("2026-09-01")


if __name__ == "__main__":
    unittest.main()
