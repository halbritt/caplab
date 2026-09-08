import copy
import unittest

from caplab.advisory.anchor import drift


def anchor(identity="a", *, caught=True, false_alarm=False, usable=True):
    return {"dispatch_id": identity, "anchor": True, "usable": usable,
            "caught": caught, "false_alarm": false_alarm}


class AnchorDriftTest(unittest.TestCase):
    def test_false_alarm_change_prevents_agreement_reading(self):
        result = drift([anchor(false_alarm=True)], [anchor()])
        self.assertEqual(result["caught_agreement"], 1.0)
        self.assertEqual(result["false_alarm_agreement"], 0.0)
        self.assertEqual(result["status"], "observed-change")
        self.assertIn("sampling variation", result["reading"])
        self.assertNotIn("anchor stable", result["reading"])

    def test_agreement_is_scoped_to_recorded_rows(self):
        result = drift([anchor()], [anchor()])
        self.assertEqual(result["schema_version"], "caplab-anchor-drift/2")
        self.assertEqual(result["status"], "observed-agreement")
        self.assertEqual(result["shared_anchor_cases"], 1)
        self.assertEqual(result["coverage"]["current_anchor_cases"], 1)
        self.assertIn("not verified", result["comparison_basis"])
        self.assertNotIn("anchor stable", result["reading"])

    def test_unusable_and_unmatched_cases_remain_visible(self):
        before = [anchor(), anchor("failed"), anchor("gone")]
        after = [anchor(), anchor("failed", usable=False), anchor("new")]
        result = drift(after, before)
        self.assertEqual(result["status"], "agreement-on-subset")
        self.assertEqual(result["shared_anchor_cases"], 1)
        self.assertEqual(result["coverage"], {
            "current_anchor_cases": 3, "previous_anchor_cases": 3,
            "shared_recorded_cases": 2,
            "current_only_ids": ["new"], "previous_only_ids": ["gone"],
            "current_unavailable": {"failed": "row-not-usable"},
            "previous_unavailable": {},
        })

    def test_changes_are_reported_even_with_partial_coverage(self):
        result = drift([anchor(caught=False)], [anchor(), anchor("gone")])
        self.assertEqual(result["status"], "observed-change")
        self.assertEqual(result["coverage"]["previous_only_ids"], ["gone"])

    def test_no_comparable_cases_is_unavailable(self):
        for after, before in [([], []), ([anchor("new")], [anchor("gone")]),
                              ([anchor(usable=False)], [anchor()])]:
            with self.subTest(after=after, before=before):
                result = drift(after, before)
                self.assertEqual(result["status"], "unavailable")
                self.assertEqual(result["shared_anchor_cases"], 0)
                self.assertIsNone(result["caught_agreement"])
                self.assertIsNone(result["false_alarm_agreement"])

    def test_unknown_outcomes_never_agree_as_boolean_results(self):
        for field in ("caught", "false_alarm"):
            for value in (None, 0, 1, "false", [], {}):
                with self.subTest(field=field, value=value):
                    row = anchor()
                    row[field] = value
                    result = drift([row], [row])
                    self.assertEqual(result["status"], "unavailable")
                    self.assertEqual(result["coverage"]["current_unavailable"],
                                     {"a": "missing-or-invalid-outcomes"})
            row = anchor()
            del row[field]
            self.assertEqual(drift([row], [anchor()])["status"], "unavailable")

    def test_duplicate_ids_are_rejected_before_usable_filtering(self):
        rows = [anchor(), anchor(usable=False)]
        for current, previous in ((rows, []), ([], rows),
                                  (list(reversed(rows)), [])):
            with self.subTest(current=current, previous=previous):
                with self.assertRaisesRegex(ValueError, "duplicate.*anchor.*a"):
                    drift(current, previous)

    def test_missing_anchor_identity_is_rejected(self):
        for value in (None, "", " ", 1):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "anchor.*dispatch_id"):
                    drift([anchor(value)], [])

    def test_non_anchor_rows_are_ignored_and_inputs_preserved(self):
        before = [anchor("b"), anchor("a"), {"anchor": False}]
        after = [anchor("b", false_alarm=True), anchor("a"), {}]
        originals = copy.deepcopy((after, before))
        result = drift(after, before)
        self.assertEqual(result, drift(list(reversed(after)), list(reversed(before))))
        self.assertEqual(result["shared_anchor_cases"], 2)
        self.assertEqual((after, before), originals)


if __name__ == "__main__":
    unittest.main()
