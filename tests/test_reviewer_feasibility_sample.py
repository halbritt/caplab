import copy
import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reviewer_feasibility_sample.py"
SPEC = importlib.util.spec_from_file_location("reviewer_feasibility_sample", SCRIPT)
sample = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sample)


class FeasibilitySampleTest(unittest.TestCase):
    def census(self):
        changes = [{"commit": str(index) * 40, "parents": ["a" * 40], "tree": "b" * 40,
                    "eligible": True, "changed_paths": [{"included_code": True, "added_lines": 10, "deleted_lines": 0}]}
                   for index in range(1, 6)]
        payload = {"schema": "caplab.reviewer-population-census/v1", "repositories": [
            {"name": "repo", "path": "/repo", "tip": "c" * 40, "commits": changes}]}
        return self.seal(payload)

    def seal(self, document):
        document.pop("content_sha256", None)
        document["content_sha256"] = sample.digest(document)
        return document

    def test_selection_is_order_independent_and_accounts_for_every_candidate(self):
        census = self.census()
        first = sample.select(census)
        census["repositories"][0]["commits"].reverse()
        second = sample.select(self.seal(census))
        self.assertEqual(first["cases"], second["cases"])
        selected = {row["commit"] for row in first["cases"]}
        excluded = set(first["strata"][0]["not_selected_commits"])
        self.assertEqual(len(selected), 2)
        self.assertFalse(selected & excluded)
        self.assertEqual(selected | excluded, {str(i) * 40 for i in range(1, 6)})

    def test_non_text_and_large_changes_are_not_silently_dropped(self):
        census = self.census()
        rows = census["repositories"][0]["commits"]
        rows[0]["changed_paths"][0]["added_lines"] = None
        rows[1]["changed_paths"][0]["added_lines"] = 50000
        selected = sample.select(self.seal(census))["cases"]
        self.assertIn("non-text", [row["size_stratum"] for row in selected])
        self.assertIn("501+", [row["size_stratum"] for row in selected])

    def test_tampering_and_duplicate_candidates_fail_closed(self):
        census = self.census()
        census["repositories"][0]["commits"][0]["eligible"] = False
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            sample.select(census)
        census = self.census()
        rows = census["repositories"][0]["commits"]
        rows.append(copy.deepcopy(rows[0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            sample.select(self.seal(census))


if __name__ == "__main__":
    unittest.main()
