"""Native task-evidence bridge over newly constructed synthetic fixtures and the real Cairn parser.

All fixture evidence here is synthetic and labelled as such; no historical
campaign is imported and no model or service is called.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from caplab.retrieval.native_task import TaskEvidenceError, import_task_run, verify_task_run

CAIRN = Path(os.environ.get("CAIRN_CHECKOUT", Path.home() / "git/cairn"))
HAVE_CAIRN = (CAIRN / "scripts/trial_task_evidence.py").is_file()
FROZEN = {"cases_sha256": "0" * 64, "labels_sha256": "1" * 64, "label_version": 2, "corpus_sha256": None,
          "note": "SYNTHETIC FIXTURE: not campaign evidence"}
NOTES = [{"id": "T-rule", "body": "SYNTHETIC: always build from a clean clone before deploying."},
         {"id": "D-other", "body": "SYNTHETIC distractor about printers."}]


def claude_stream(body):
    """One completed cairn_pull returning a full body from the trial collection."""
    use = {"message": {"content": [{"type": "tool_use", "id": "toolu_1", "name": "mcp__cairn__cairn_pull", "input": {}}]}}
    payload = {"selection": {"record": {"record_id": "r1", "version": 1, "scope": {"repo": "trial:task-eval"}, "body": body}}}
    result = {"message": {"content": [{"type": "tool_result", "tool_use_id": "toolu_1",
                                       "content": [{"type": "text", "text": json.dumps(payload)}]}]}}
    return (json.dumps(use) + "\n" + json.dumps(result) + "\n").encode()


@unittest.skipUnless(HAVE_CAIRN, "needs a Cairn checkout with scripts/trial_task_evidence.py (set CAIRN_CHECKOUT)")
class NativeTaskBridge(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.run_dir = self.root / "run"
        (self.run_dir / "runs").mkdir(parents=True)
        corpus = json.dumps({"notes": NOTES}).encode()
        self.corpus = self.root / "corpus.json"
        self.corpus.write_bytes(corpus)
        frozen = dict(FROZEN, corpus_sha256=hashlib.sha256(corpus).hexdigest())
        identity = dict(model="synthetic-model", harness="claude", reasoning_effort=None, wording="task",
                        harness_version="0.0 synthetic", evaluator_sha256="2" * 64)
        runs = [["deploy", "baseline", 0, 0], ["deploy", "candidate", 0, 1], ["boundary", "baseline", 0, 0],
                ["boundary", "candidate", 0, 1], ["old", "baseline", 0, 0], ["old", "candidate", 0, 1]]
        self.plan = dict(frozen=frozen, arms=["baseline", "candidate"], runs=runs, **identity)
        records = [
            dict(run_id="deploy.baseline.s0", case="deploy", arm="baseline", seed=0, outcome="correct", stratum="completion",
                 correct=["clean_clone"], mistake=[], model="synthetic-model", harness="claude"),
            dict(run_id="deploy.candidate.s0", case="deploy", arm="candidate", seed=0, outcome="mistake", stratum="completion",
                 correct=[], mistake=["dirty_build"], model="synthetic-model", harness="claude"),
            dict(run_id="boundary.baseline.s0", case="boundary", arm="baseline", seed=0, outcome="incomplete", stratum="scope",
                 model="synthetic-model", harness="claude"),
            dict(run_id="old.baseline.s0", case="old", arm="baseline", seed=0, outcome="harness_error",
                 error="synthetic provider stop", model="synthetic-model", harness="claude"),  # no stratum: unknown
        ]
        self.report = dict(schema="cairn.task-eval.agent/1", records=records, admission=dict(
            state="stopped_provider_failure", stop={"run_id": "old.baseline.s0"}, planned=6, admitted=5,
            not_started=[dict(run_id="old.candidate.s0", case="old", arm="candidate", seed=0, order=1)]),
            **{k: v for k, v in self.plan.items() if k != "runs"})
        self.write()
        for run_id, body in (("deploy.baseline.s0", NOTES[0]["body"]), ("boundary.baseline.s0", NOTES[1]["body"])):
            (self.run_dir / "runs" / run_id).mkdir()
            (self.run_dir / "runs" / run_id / "stream.jsonl").write_bytes(claude_stream(body))
        # deploy.candidate.s0 and old.baseline.s0 have no stream: unknown evidence, not zero delivery.

    def write(self):
        (self.run_dir / "agent.json").write_text(json.dumps(self.report))
        (self.run_dir / "plan.json").write_text(json.dumps(self.plan))

    def run_import(self, name="out"):
        return import_task_run(self.run_dir / "agent.json", plan_path=self.run_dir / "plan.json", corpus_path=self.corpus,
                               cairn_checkout=CAIRN, output=self.root / name)

    def assertRefused(self, code):
        with self.assertRaises(TaskEvidenceError) as caught:
            self.run_import("refused")
        self.assertEqual(caught.exception.code, code, caught.exception)

    def test_import_preserves_grades_streams_and_unknowns(self):
        doc = self.run_import()
        self.assertEqual(doc["counts"], {"planned": 6, "recorded": 4, "not_started": 1, "missing": 1,
                                         "streams_retained": 2, "streams_missing": 2})
        rows = {a["run_id"]: a for a in doc["assignments"]}
        self.assertEqual(rows["deploy.baseline.s0"]["original"]["outcome"], "correct")
        self.assertEqual(rows["deploy.baseline.s0"]["delivery"]["body_notes"], ["T-rule"])
        self.assertEqual(rows["deploy.candidate.s0"]["original"]["mistake"], ["dirty_build"])
        self.assertEqual(rows["deploy.candidate.s0"]["delivery"], {"observed": False, "reason": "missing_stream"})
        self.assertEqual(rows["boundary.baseline.s0"]["stratum_class"], "boundary_or_abstention")
        self.assertEqual(rows["old.baseline.s0"]["stratum_class"], "unknown")
        self.assertEqual(rows["old.candidate.s0"]["status"], "not_started")
        self.assertEqual(rows["boundary.candidate.s0"]["status"], "missing")
        self.assertEqual(doc["strata"]["unknown"], {"harness_error": 1})
        self.assertIsNone(doc["identity"]["binding"])
        self.assertEqual(doc["sources"]["parser"]["pin"]["path"], "scripts/trial_task_evidence.py")
        report_ref = doc["sources"]["report"]
        self.assertEqual(report_ref["sha256"], hashlib.sha256((self.run_dir / "agent.json").read_bytes()).hexdigest())
        verified = verify_task_run(self.root / "out")
        self.assertTrue(verified["verified"])
        self.assertEqual(verified["objects"], 4 + 2 + 1)  # report, plan, corpus, parser, 2 streams, evidence

    def test_tampering_is_detected(self):
        self.run_import()
        objects = sorted((self.root / "out/ledger/objects").rglob("*"))
        victim = next(p for p in objects if p.is_file())
        os.chmod(victim, 0o600)
        victim.write_bytes(victim.read_bytes() + b" ")
        with self.assertRaises(TaskEvidenceError) as caught:
            verify_task_run(self.root / "out")
        self.assertEqual(caught.exception.code, "INTEGRITY")

    def test_evidence_json_tampering_is_detected(self):
        self.run_import()
        path = self.root / "out/evidence.json"
        path.write_bytes(path.read_bytes().replace(b'"correct"', b'"mistake"', 1))
        with self.assertRaises(TaskEvidenceError):
            verify_task_run(self.root / "out")

    def test_identity_mismatches_fail_closed(self):
        mutations = [
            (lambda: self.plan.update(model="other-model"), "IDENTITY_MISMATCH"),
            (lambda: self.plan.update(reasoning_effort="high"), "IDENTITY_MISMATCH"),
            (lambda: self.plan["frozen"].update(labels_sha256="9" * 64), "IDENTITY_MISMATCH"),
            (lambda: self.plan.update(arms=["baseline"]), "IDENTITY_MISMATCH"),
            (lambda: self.report["records"][0].update(model="swapped"), "IDENTITY_MISMATCH"),
            (lambda: self.report["records"][0].update(run_id="deploy.baseline.s1"), "IDENTITY_MISMATCH"),
            (lambda: self.report["records"].append(dict(self.report["records"][0])), "DUPLICATE_RUN"),
            (lambda: self.report["records"].append(dict(self.report["records"][0], case="ghost", run_id="ghost.baseline.s0")), "UNPLANNED_RUN"),
            (lambda: self.plan["runs"].append(["deploy", "baseline", 0, 0]), "DUPLICATE_RUN"),
            (lambda: self.report["admission"]["not_started"].append(dict(case="deploy", arm="baseline", seed=0)), "IDENTITY_MISMATCH"),
            (lambda: self.report.update(schema="cairn.task-eval.agent/2"), "UNKNOWN_SCHEMA"),
            (lambda: self.report["records"][0].update(case="../x", run_id="../x.baseline.s0"), "UNSAFE_PATH"),
        ]
        pristine_plan, pristine_report = json.dumps(self.plan), json.dumps(self.report)
        for mutate, code in mutations:
            self.plan, self.report = json.loads(pristine_plan), json.loads(pristine_report)
            mutate()
            self.write()
            with self.subTest(code=code):
                self.assertRefused(code)
                self.assertFalse((self.root / "refused").exists())

    def test_corpus_drift_and_existing_output(self):
        (self.root / "out").mkdir()
        self.assertRaisesRegex(TaskEvidenceError, "OUTPUT_EXISTS", self.run_import)
        self.corpus.write_text(json.dumps({"notes": NOTES[:1]}))
        self.assertRefused("IDENTITY_MISMATCH")

    def test_parser_refusal_is_surfaced(self):
        # A pull outside the trial collection is refused by the real Cairn parser, not papered over.
        stream = self.run_dir / "runs/deploy.baseline.s0/stream.jsonl"
        stream.write_bytes(stream.read_bytes().replace(b"trial:task-eval", b"production"))
        self.assertRefused("PARSER_REFUSED")

    def test_parser_checkout_is_explicit(self):
        with self.assertRaises(TaskEvidenceError) as caught:
            import_task_run(self.run_dir / "agent.json", plan_path=self.run_dir / "plan.json", corpus_path=self.corpus,
                            cairn_checkout=self.root / "no-checkout", output=self.root / "x")
        self.assertEqual(caught.exception.code, "UNSAFE_PATH")


if __name__ == "__main__":
    unittest.main()
