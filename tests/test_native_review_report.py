import json
from pathlib import Path
import tempfile
import unittest


def finding(path="runtime.py", **changes):
    return {
        "title": "A reported finding", "claim": "The response can finish late.",
        "trigger": "An active response continues beyond the deadline.",
        "expected_behavior": "Stop at the overall deadline.",
        "observed_or_predicted_behavior": "The body may finish later.",
        "change_attribution": "The new caller omits the overall deadline.",
        "evidence": "Source inspection only.", "claim_status": "uncertain",
        "acceptance_effect": "undetermined",
        "locations": [{"path": path, "start_line": 1, "end_line": 1}], **changes,
    }


def report(*findings):
    return json.dumps({"schema": "caplab.native-code-review-report/v1",
                       "findings": list(findings), "limitations": ["No live endpoint tested."]}).encode()


class NativeReviewReportTests(unittest.TestCase):
    def test_missing_stance_is_not_inferred_and_empty_report_is_not_clean_evidence(self):
        from caplab.native_review_report import inspect_report

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = finding()
            del missing["acceptance_effect"]
            with self.assertRaises(ValueError):
                inspect_report(report(missing), root)
            empty = inspect_report(report(), root)
            self.assertEqual(empty["findings"], [])
            self.assertFalse(empty["truth_assessed"])
            self.assertEqual(empty["limitations"], ["No live endpoint tested."])

    def test_duplicates_and_qualifications_survive_without_becoming_quality_scores(self):
        from caplab.native_review_report import inspect_report

        with tempfile.TemporaryDirectory() as directory:
            source = finding(claim="The branch might fail; I could not reproduce it.",
                             claim_status="uncertain", acceptance_effect="block", locations=[])
            result = inspect_report(report(source, source, finding(claim_status="withdrawn", acceptance_effect="advise")), Path(directory))
            self.assertEqual(len(result["findings"]), 3)
            first, repeated, withdrawn = result["findings"]
            self.assertEqual(first["reported"], source)
            self.assertEqual(first["finding_sha256"], repeated["finding_sha256"])
            self.assertNotEqual(first["finding_id"], repeated["finding_id"])
            self.assertEqual(withdrawn["reported"]["claim_status"], "withdrawn")
            self.assertFalse(result["truth_assessed"])

    def test_invalid_or_escaping_locations_remain_with_the_finding_without_outside_reads(self):
        from caplab.native_review_report import inspect_report

        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "source"
            root.mkdir()
            (parent / "outside").write_text("private fixture\n")
            (root / "escape").symlink_to(parent / "outside")
            (root / "runtime.py").write_text("value = 1\n")
            items = [finding("../outside"), finding("escape"), finding(locations=[
                {"path": "runtime.py", "start_line": 200, "end_line": 201}])]
            result = inspect_report(report(*items), root)
            self.assertEqual([row["location_checks"][0]["status"] for row in result["findings"]],
                             ["unsafe-path", "outside-source-root", "invalid-line-range"])
            self.assertNotIn("file_sha256", result["findings"][1]["location_checks"][0])
            self.assertEqual(result["findings"][2]["reported"], items[2])

    def test_duplicate_keys_cannot_change_a_blocker_or_erase_findings(self):
        from caplab.native_review_report import inspect_report

        raw = report(finding(acceptance_effect="block"))
        shadows = [
            raw.replace(b'"acceptance_effect": "block"', b'"acceptance_effect":"block","acceptance_effect":"advise"'),
            raw.replace(b'"limitations":', b'"findings":[],"limitations":'),
            raw.replace(b'"start_line": 1', b'"start_line":999,"start_line":1'),
        ]
        with tempfile.TemporaryDirectory() as directory:
            for malformed in shadows:
                with self.subTest(report=malformed), self.assertRaises(ValueError):
                    inspect_report(malformed, Path(directory))

    def test_each_finding_keeps_its_own_location_and_reported_acceptance_effect(self):
        from caplab.native_review_report import inspect_report

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "runtime.py").write_text("value = 1\n")
            wrong = finding("missing.py", title="Blocking issue", acceptance_effect="undetermined")
            other = finding(acceptance_effect="advise")
            result = inspect_report(report(wrong, other), root)
            self.assertEqual(result["findings"][0]["location_checks"][0]["status"], "missing")
            self.assertEqual(result["findings"][1]["location_checks"][0]["status"], "resolved")
            self.assertEqual(result["findings"][0]["reported"], wrong)
            self.assertEqual(result["findings"][0]["reported"]["acceptance_effect"], "undetermined")
            self.assertFalse(result["truth_assessed"])


if __name__ == "__main__":
    unittest.main()
