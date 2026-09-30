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

from caplab.qualification.ledger import FilesystemQualificationLedger
from caplab.retrieval.native_task import (EVIDENCE_MEDIA_TYPE, SCHEMA, TaskEvidenceError, _evidence_bytes,
                                          import_task_run, verify_task_run)
from caplab.runtime.canonical import canonical_json

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
                 correct=["clean_clone"], mistake=[], model="synthetic-model", harness="claude", seconds=41.37,
                 memory={"delivered": ["T-rule"], "context_bytes": 812, "outcomes": [{"status": "ok", "seconds": 0.429}],
                         "recall": [{"latency_s": 7.93, "selector_cost_usd": 0.0031}]}),
            dict(run_id="deploy.candidate.s0", case="deploy", arm="candidate", seed=0, outcome="mistake", stratum="completion",
                 correct=[], mistake=["dirty_build"], model="synthetic-model", harness="claude"),
            dict(run_id="boundary.baseline.s0", case="boundary", arm="baseline", seed=0, outcome="incomplete", stratum="scope",
                 model="synthetic-model", harness="claude", seconds=12.5),
            dict(run_id="boundary.candidate.s0", case="boundary", arm="candidate", seed=0, outcome="correct", stratum="decision",
                 model="synthetic-model", harness="claude", seconds=9.25),
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
        self.assertEqual(doc["counts"], {"planned": 6, "recorded": 5, "not_started": 1, "missing": 0,
                                         "streams_retained": 2, "streams_missing": 3})
        rows = {a["run_id"]: a for a in doc["assignments"]}
        self.assertEqual(rows["deploy.baseline.s0"]["original"]["outcome"], "correct")
        self.assertEqual(rows["deploy.baseline.s0"]["delivery"]["body_notes"], ["T-rule"])
        self.assertEqual(rows["deploy.candidate.s0"]["original"]["mistake"], ["dirty_build"])
        self.assertEqual(rows["deploy.candidate.s0"]["delivery"], {"observed": False, "reason": "missing_stream"})
        self.assertEqual(rows["boundary.baseline.s0"]["stratum_class"], "boundary_or_abstention")
        self.assertEqual(rows["old.baseline.s0"]["stratum_class"], "unknown")
        self.assertEqual(rows["old.candidate.s0"]["status"], "not_started")
        # A labelled stratum without a known boundary meaning stays unknown.
        self.assertEqual(rows["boundary.candidate.s0"]["stratum_class"], "unknown")
        self.assertEqual(rows["boundary.candidate.s0"]["original"]["stratum"], "decision")
        # Native floats survive untouched in the retained evidence.
        self.assertEqual(rows["deploy.baseline.s0"]["original"]["seconds"], 41.37)
        self.assertEqual(rows["deploy.baseline.s0"]["original_memory"]["recall"][0]["latency_s"], 7.93)
        retained = json.loads((self.root / "out/evidence.json").read_bytes())
        self.assertEqual(retained["assignments"][0]["original_memory"]["outcomes"][0]["seconds"], 0.429)
        self.assertEqual(doc["strata"]["unknown"], {"harness_error": 1})
        self.assertIsNone(doc["identity"]["binding"])
        self.assertEqual(doc["sources"]["parser"]["pin"]["path"], "scripts/trial_task_evidence.py")
        report_ref = doc["sources"]["report"]
        self.assertEqual(report_ref["sha256"], hashlib.sha256((self.run_dir / "agent.json").read_bytes()).hexdigest())
        verified = verify_task_run(self.root / "out")
        self.assertTrue(verified["verified"])
        self.assertEqual(verified["evidence"], json.loads((self.root / "out/evidence.json").read_bytes()))
        self.assertEqual(verified["evidence"]["counts"], verified["counts"])
        self.assertEqual(verified["objects"], 4 + 2 + 1)  # report, plan, corpus, parser, 2 streams, evidence
        manifest = json.loads((self.root / "out/manifest.json").read_bytes())
        self.assertEqual(manifest["evidence"]["media_type"], "application/vnd.caplab.retrieval-task-evidence+json")

    def test_present_native_fields_agree_and_absent_ones_are_optional(self):
        self.report["records"][0]["order"] = 0  # matches plan position
        del self.report["admission"]["not_started"][0]["run_id"]
        del self.report["admission"]["not_started"][0]["order"]
        self.write()
        self.assertEqual(self.run_import()["counts"]["not_started"], 1)

    def test_missing_planned_run_is_counted(self):
        self.report["records"] = [r for r in self.report["records"] if r["run_id"] != "boundary.candidate.s0"]
        self.write()
        doc = self.run_import()
        self.assertEqual((doc["counts"]["missing"], doc["counts"]["recorded"]), (1, 4))
        self.assertEqual({a["run_id"]: a["status"] for a in doc["assignments"]}["boundary.candidate.s0"], "missing")

    def forge(self, mutate, name="out"):
        """A coherent forgery: edit evidence, re-register it and rewrite the manifest."""
        out = self.root / name
        document = json.loads((out / "evidence.json").read_bytes())
        mutate(document)
        data = _evidence_bytes(document)
        ref = FilesystemQualificationLedger(out / "ledger").register_bytes(
            data, kind="retrieval-task-evidence", schema=SCHEMA, media_type=EVIDENCE_MEDIA_TYPE)
        for file, payload in (("evidence.json", data),
                              ("manifest.json", canonical_json({"schema_version": SCHEMA + "+manifest", "evidence": ref}))):
            os.chmod(out / file, 0o600)
            (out / file).write_bytes(payload)
        return out

    def test_coherently_reregistered_forgeries_are_refused(self):
        self.run_import()
        pristine = (self.root / "out/evidence.json").read_bytes()
        forgeries = {
            "grade": lambda d: d["assignments"][0]["original"].update(outcome="mistake"),
            "memory": lambda d: d["assignments"][0]["original_memory"].update(context_bytes=1),
            "stratum_class": lambda d: d["assignments"][2].update(stratum_class="completion"),
            "status": lambda d: d["assignments"][5].update(status="missing"),
            "order": lambda d: d["assignments"][0].update(order=1),
            "counts": lambda d: d["counts"].update(recorded=6),
            "outcomes": lambda d: d["outcomes"].update(correct=9),
            "strata": lambda d: d["strata"].pop("unknown"),
            "admission": lambda d: d["admission"].update(state="complete"),
            "identity": lambda d: d["identity"]["reported"].update(model="other-model"),
            "binding": lambda d: d["identity"].update(binding="fabricated"),
            "dropped_assignment": lambda d: d["assignments"].pop(3),
            "parser_report_hash": lambda d: d["parser_analysis"].update(report_sha256="0" * 64),
            "parser_corpus_hash": lambda d: d["parser_analysis"].update(corpus_sha256="0" * 64),
            "stream_flipped_unobserved": lambda d: d["assignments"][0].update(delivery={"observed": False, "reason": "missing_stream"}),
            "limits": lambda d: d["limits"].pop(),
        }
        for label, mutate in forgeries.items():
            with self.subTest(label):
                (self.root / "out/evidence.json").chmod(0o600)
                self.forge(mutate)
                with self.assertRaises(TaskEvidenceError) as caught:
                    verify_task_run(self.root / "out")
                self.assertIn(caught.exception.code, ("INTEGRITY", "IDENTITY_MISMATCH"))
                self.forge(lambda d: d.clear() or d.update(json.loads(pristine)))  # restore for the next case
        self.assertTrue(verify_task_run(self.root / "out")["verified"])

    def test_forged_delivery_needs_trusted_parser_to_detect(self):
        self.run_import()
        result = verify_task_run(self.root / "out", trusted_parser_checkout=CAIRN)
        self.assertEqual(result["verification"]["parser_derived"], "re-executed with trusted checkout; matched")
        self.forge(lambda d: d["assignments"][0]["delivery"].update(body_notes=["D-other"]))
        hash_bound = verify_task_run(self.root / "out")  # honestly labelled: parser output is hash-bound only
        self.assertEqual(hash_bound["verification"]["parser_derived"], "hash-bound; not re-executed")
        with self.assertRaises(TaskEvidenceError) as caught:
            verify_task_run(self.root / "out", trusted_parser_checkout=CAIRN)
        self.assertEqual(caught.exception.code, "INTEGRITY")

    def test_trusted_checkout_must_match_retained_parser(self):
        self.run_import()
        other = self.root / "other-checkout/scripts"
        other.mkdir(parents=True)
        (other / "trial_task_evidence.py").write_bytes((CAIRN / "scripts/trial_task_evidence.py").read_bytes() + b"\n# edited\n")
        with self.assertRaises(TaskEvidenceError) as caught:
            verify_task_run(self.root / "out", trusted_parser_checkout=self.root / "other-checkout")
        self.assertEqual(caught.exception.code, "PARSER_CONTRACT")

    def test_forged_run_id_cannot_write_outside_scratch(self):
        self.run_import()
        sentinel = self.root / "sentinel-outside"  # test-owned; never a real user path
        for forged_id in (str(sentinel / "x"), "../../sentinel-traversal/x", "deploy.baseline.s0/../../escape"):
            with self.subTest(forged_id=forged_id):
                self.forge(lambda d: d["assignments"][0].update(run_id=forged_id))
                for trusted in (None, CAIRN):
                    with self.assertRaises(TaskEvidenceError) as caught:
                        verify_task_run(self.root / "out", trusted_parser_checkout=trusted)
                    self.assertEqual(caught.exception.code, "INTEGRITY")
                self.assertFalse(sentinel.exists())
                self.assertFalse((self.root / "sentinel-traversal").exists())
                self.forge(lambda d: d["assignments"][0].update(run_id="deploy.baseline.s0"))
        # Reordered, duplicated or dropped roster rows are refused before any path use.
        for mutate in (lambda d: d["assignments"].reverse(),
                       lambda d: d["assignments"].__setitem__(1, dict(d["assignments"][0])),
                       lambda d: d["assignments"].pop()):
            self.forge(mutate)
            with self.assertRaises(TaskEvidenceError):
                verify_task_run(self.root / "out", trusted_parser_checkout=CAIRN)

    def test_mismatched_trusted_parser_never_executes(self):
        self.run_import()
        marker = self.root / "parser-executed-marker"  # test-owned side effect
        other = self.root / "hostile-checkout/scripts"
        other.mkdir(parents=True)
        (other / "trial_task_evidence.py").write_text(
            f"open({str(marker)!r}, 'w').write('ran')\n" + (CAIRN / "scripts/trial_task_evidence.py").read_text())
        with self.assertRaises(TaskEvidenceError) as caught:
            verify_task_run(self.root / "out", trusted_parser_checkout=self.root / "hostile-checkout")
        self.assertEqual(caught.exception.code, "PARSER_CONTRACT")
        self.assertFalse(marker.exists())

    def test_colliding_derived_run_ids_are_refused(self):
        # (a.b, c) and (a, b.c) both derive run_id a.b.c.s0 and would share one stream.
        self.plan.update(arms=["c", "b.c"], runs=[["a.b", "c", 0, 0], ["a", "b.c", 0, 1]])
        self.report.update(arms=["c", "b.c"], admission=dict(state="complete", planned=2, admitted=2, not_started=[]),
                           records=[dict(run_id="a.b.c.s0", case="a.b", arm="c", seed=0, outcome="correct"),
                                    dict(run_id="a.b.c.s0", case="a", arm="b.c", seed=0, outcome="mistake")])
        self.write()
        self.assertRefused("DUPLICATE_RUN")

    def test_nonfinite_or_unsafe_inputs_fail_before_any_output(self):
        self.report["records"][0]["seconds"] = float("nan")
        self.write()
        self.assertRefused("MALFORMED")
        self.report["records"][0]["seconds"] = 41.37
        for path in ("/etc/observed.json", "../observed.json", "a/../../x.json"):
            self.report["observed_corpus"] = self.plan["observed_corpus"] = {"path": path, "sha256": "0" * 64}
            self.write()
            with self.subTest(path=path):
                self.assertRefused("UNSAFE_PATH")
                self.assertFalse((self.root / "refused").exists())

    def test_dangling_symlink_output_is_typed(self):
        os.symlink(self.root / "nowhere", self.root / "dangling")
        with self.assertRaises(TaskEvidenceError) as caught:
            self.run_import("dangling")
        self.assertEqual(caught.exception.code, "OUTPUT_EXISTS")

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
        os.chmod(path, 0o600)  # retained files are written read-only; a tamperer can still change them
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
            # Native position semantics (agent-251 integration probes and neighbours).
            (lambda: self.plan["runs"][0].__setitem__(3, "wrong"), "MALFORMED"),
            (lambda: self.plan["runs"][0].__setitem__(3, True), "MALFORMED"),
            (lambda: self.plan["runs"][0].__setitem__(3, 2), "MALFORMED"),
            (lambda: self.plan["runs"][0].__setitem__(3, -1), "MALFORMED"),
            (lambda: self.plan["runs"][1].__setitem__(3, 0), "IDENTITY_MISMATCH"),
            (lambda: self.report["records"][0].update(order=999), "IDENTITY_MISMATCH"),
            (lambda: self.report["records"][0].update(order=1), "IDENTITY_MISMATCH"),
            (lambda: self.report["admission"]["not_started"][0].update(run_id="different.candidate.s0"), "IDENTITY_MISMATCH"),
            (lambda: self.report["admission"]["not_started"][0].update(order=0), "IDENTITY_MISMATCH"),
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
