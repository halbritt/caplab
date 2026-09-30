"""Reviewer-readable retrieval reports: context first, honest denominators, no invented verdicts."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caplab.retrieval import contracts, metrics
from caplab.retrieval.artifacts import verify_run
from caplab.retrieval.report import REPORT_SCHEMA, build_report, render_markdown, run_status

from retrieval_evidence_support import make_spec, write_run


class ReportFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def report(self, **kwargs):
        kwargs.setdefault("raw", False)
        run, _ = write_run(self.root, "run", **kwargs)
        return verify_run(run.output, allow_unfinished=True)["report"]


class ReportContentTests(ReportFixture):
    def test_reviewer_context_comes_before_any_metric(self):
        report = self.report()
        keys = list(report)
        self.assertEqual(keys[:3], ["schema_version", "reviewer_context", "run"])
        self.assertLess(keys.index("reviewer_context"), keys.index("summary"))
        self.assertEqual(report["schema_version"], REPORT_SCHEMA)
        context = report["reviewer_context"]
        tested = context["what_was_tested"]
        self.assertEqual((tested["corpus_notes"], tested["queries"]["total"], tested["planned_assignments"]), (6, 3, 12))
        self.assertEqual(tested["queries"]["by_stratum"], {"answerable": 2, "no_answer": 1})
        self.assertEqual([arm["id"] for arm in tested["arms"]], ["good", "bad"])
        self.assertIn("never passed to a retrieval adapter", context["labelled_truth"]["source"])
        for pin in ("spec_sha256", "corpus_sha256", "cases_sha256", "roster_sha256"):
            self.assertTrue(context["labelled_truth"][pin].startswith("sha256:"))

    def test_summary_is_exactly_the_metrics_summary_and_denominators_come_from_it(self):
        report = self.report()
        attempts = verify_run(self.root / "run")["attempts"]
        spec = verify_run(self.root / "run")["spec"]
        self.assertEqual(report["summary"], metrics.summarize(spec, attempts))
        for arm, coverage in report["denominators"].items():
            self.assertEqual(coverage, report["summary"]["arms"][arm]["coverage"])
            self.assertEqual(coverage["planned"], 6)

    def test_limitations_state_what_the_report_does_not_claim(self):
        text = " ".join(self.report()["limitations"])
        for phrase in ("not a caplab-measurement/1 record", "no pass threshold", "downstream task completion",
                       "not independent new cases", "never a successful abstention", "never inferred from rank",
                       "do not authenticate"):
            self.assertIn(phrase, text.replace("\n", " "))

    def test_incomplete_and_failed_runs_say_so_in_the_limitations(self):
        report = self.report(skip={"good:q1:0"}, overrides={("bad", "q2", 1): {"status": "error"}})
        notes = " ".join(report["limitations"])
        self.assertIn("1 planned assignment(s) have no recorded attempt", notes)
        self.assertIn("1 recorded attempt(s) failed", notes)
        self.assertEqual(report["run"]["status"], "incomplete")

    def test_the_report_is_plain_json_and_finite(self):
        report = self.report()
        json.dumps(report, allow_nan=False)


class RunStatusTests(unittest.TestCase):
    def plan_and_attempts(self, statuses):
        spec = contracts.validate_spec(make_spec(arms=("good",), seeds=(0,)))
        plan = {"roster": contracts.assignments(spec)}
        attempts = []
        for row, status in zip(plan["roster"], statuses):
            if status is not None:
                attempts.append({**row, "status": status, "error": {"code": "E"} if status == "error" else None})
        return plan, attempts

    def test_status_transitions(self):
        self.assertEqual(run_status(*self.plan_and_attempts(["ok"] * 3))["status"], "complete")
        self.assertEqual(run_status(*self.plan_and_attempts(["ok", "ok", "not_started"]))["status"], "completed_with_failures")
        self.assertEqual(run_status(*self.plan_and_attempts(["ok", "error", "ok"]))["status"], "completed_with_failures")
        incomplete = run_status(*self.plan_and_attempts(["ok", None, "error"]))
        self.assertEqual((incomplete["status"], incomplete["missing_assignments"]), ("incomplete", ["good:q2:0"]))
        self.assertEqual(incomplete["failures"][0]["error_code"], "E")
        self.assertEqual((incomplete["planned"], incomplete["recorded"], incomplete["ok"]), (3, 2, 1))


class MarkdownTests(ReportFixture):
    def test_sections_appear_in_reviewer_order_and_metrics_come_last(self):
        text = render_markdown(self.report())
        order = ["## What was tested", "## Labelled truth and provenance", "## Run status and denominators",
                 "## How to read this report", "## Limitations", "## Metrics"]
        positions = [text.index(heading) for heading in order]
        self.assertEqual(positions, sorted(positions))
        self.assertTrue(text.startswith("# Retrieval evaluation report: fixture"))

    def test_rates_keep_numerators_and_denominators(self):
        text = render_markdown(self.report())
        self.assertIn("6/6 (1.0000)", text)            # scorable rate
        self.assertIn("**Cutoff k=1**", text)
        self.assertIn("| recall | 3/4 (0.7500) |", text)  # good arm: (1 + 1/2) / 2 over answerable assignments
        self.assertIn("precision@k always divides by k".lower(), text.lower())

    def test_failures_and_missing_work_are_listed_by_name(self):
        text = render_markdown(self.report(spec=make_spec(arms=("good", "failing")), skip={"good:q3:1"}))
        self.assertIn("**incomplete**", text)
        self.assertIn("### Failed or not-started assignments", text)
        self.assertIn("| failing:q1:0 | timeout | timeout |", text)
        self.assertIn("### Missing assignments", text)
        self.assertIn("`good:q3:1`", text)

    def test_unfinished_runs_are_labelled_unfinished(self):
        run, _ = write_run(self.root, "partial", finish=False, raw=False, skip={"bad:q1:0"})
        text = render_markdown(verify_run(run.output, allow_unfinished=True)["report"])
        self.assertIn("(run not finished)", text)

    def test_table_cells_escape_pipes(self):
        spec = make_spec(arms=("good",))
        spec["arms"][0]["configuration"]["argv"] = ["sh", "-c", "a | b"]
        text = render_markdown(self.report(spec=spec))
        self.assertIn("a \\| b", text)

    def test_unknown_documents_are_not_rendered_as_reports(self):
        for document in ({"schema_version": "caplab-measurement/1"}, {}, []):
            with self.assertRaises(contracts.ContractError) as caught:
                render_markdown(document)  # type: ignore[arg-type]
            self.assertEqual(caught.exception.code, "UNKNOWN_SCHEMA")

    def test_build_report_is_deterministic(self):
        run, _ = write_run(self.root, "again", raw=False)
        loaded = verify_run(run.output)
        rebuilt = build_report(loaded["plan"], loaded["attempts"], loaded["report"]["summary"], finished=True,
                               references=loaded["report"]["references"])
        self.assertEqual(rebuilt, loaded["report"])


if __name__ == "__main__":
    unittest.main()
