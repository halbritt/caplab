"""Real Cairn against a fresh disposable PostgreSQL cluster, recorded by the real artifact store.

    CAPLAB_CAIRN_CHECKOUT=~/git/cairn PYTHONPATH=src:. python3 -m unittest tests.test_retrieval_cairn_real -v

Needs `git`, `go` and PostgreSQL 16+ binaries (CAPLAB_RETRIEVAL_PG_BIN, CAIRN_PG_BIN or
`pg_config`). The checkout must contain Cairn's `scripts/trial-task-eval.sh -- COMMAND` mode.
The test clones the checkout at its HEAD and builds its binary with
scripts/retrieval_pin_cairn.py; the source checkout is only read. Nothing here can reach a
production database, API socket or profile: every store is a private cluster under /tmp on a
Unix socket, and the environment given to Cairn is rebuilt from scratch.

Every run is written by the actual `RunArtifacts` and re-read with `verify_run`. Set
CAPLAB_RETRIEVAL_EVIDENCE_DIR to a directory to keep the main measured run there (as
`run/`, with `verify.json` and `report.md`) for review.
"""

import glob
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from unittest import mock

from caplab.qualification.ledger import FilesystemQualificationLedger
from caplab.retrieval import artifacts, cairn, report as report_module, runner
from tests.retrieval_support import QUERIES, command_arm, make_spec, write_retriever

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = os.environ.get("CAPLAB_CAIRN_CHECKOUT", "")


def store_roots():
    """CAPLAB's store directories and the wrapper's disposable clusters."""
    return set(glob.glob("/tmp/caplab-rtv-*")) | set(glob.glob("/tmp/cairn-task-eval-pg.*"))


def retained(output):
    """Every artifact and raw byte the run retained, read back through its ledger: ({name: bytes}, {(assignment, role): bytes})."""
    ledger = FilesystemQualificationLedger(Path(output) / "ledger")
    named, raw = {}, {}
    for line in (Path(output) / "evidence.jsonl").read_text().splitlines():
        entry = json.loads(line)
        if entry["kind"] == "artifact":
            named[entry["name"]] = ledger.resolve(entry["ref"])
        else:
            for role, ref in entry["raw"].items():
                raw[(entry["assignment_id"], role)] = ledger.resolve(ref)
    return named, raw


def postgres_left(roots):
    done = subprocess.run(["pgrep", "-af", "caplab-rtv-|cairn-task-eval-pg"], capture_output=True, text=True)
    return [line for line in done.stdout.splitlines() if any(root in line for root in roots) and "pgrep" not in line]


@unittest.skipUnless(CHECKOUT and Path(CHECKOUT).is_dir(), "set CAPLAB_CAIRN_CHECKOUT to run against real Cairn")
@unittest.skipUnless(shutil.which("go") and shutil.which("git"), "go and git are required to build the pinned binary")
class RealCairnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (os.environ.get("CAPLAB_RETRIEVAL_PG_BIN") or os.environ.get("CAIRN_PG_BIN") or shutil.which("pg_config")):
            raise unittest.SkipTest("PostgreSQL is not available to Cairn's wrapper: set CAPLAB_RETRIEVAL_PG_BIN or CAIRN_PG_BIN")
        cls.temp = tempfile.TemporaryDirectory(prefix="caplab-real-")
        cls.addClassCleanup(cls.temp.cleanup)
        done = subprocess.run([sys.executable, str(ROOT / "scripts/retrieval_pin_cairn.py"), "--checkout", CHECKOUT,
                               "--output", str(Path(cls.temp.name) / "pin")], capture_output=True, text=True,
                              timeout=1800)
        assert done.returncode == 0, done.stderr
        cls.pins = json.loads(done.stdout)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=self.temp.name))
        self.roots_before = store_roots()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def arm(self, arm_id, semantic_mode):
        return {"id": arm_id, "adapter": "cairn", "configuration": {
            "binary": self.pins["binary"], "checkout": self.pins["checkout"], "semantic_mode": semantic_mode}}

    def assert_no_store_left(self):
        leaked = store_roots() - self.roots_before
        self.assertEqual(leaked, set(), "a disposable store directory was left behind")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and postgres_left(self.roots_before | store_roots()):
            time.sleep(0.2)
        self.assertEqual(postgres_left(self.roots_before | store_roots()), [], "a postgres or cairn process was left")

    def test_real_cairn_is_measured_against_controls_beside_fixture_retrievers(self):
        scripts = self.tmp / "scripts"
        scripts.mkdir()
        fixtures = [command_arm(name, write_retriever(scripts, name)) for name in ("good", "bad", "empty", "failing")]
        queries = QUERIES + [{"id": "q-zebra", "text": "zebra quartz waltz", "relevant_ids": [],
                              "stratum": "no-answer"}]
        spec = make_spec([self.arm("cairn-lexical", "off"), self.arm("cairn-semantic", "on")] + fixtures,
                         queries=queries, seeds=(0, 1), cutoffs=(1, 3))
        evidence = os.environ.get("CAPLAB_RETRIEVAL_EVIDENCE_DIR")
        out = Path(evidence) / "run" if evidence else self.tmp / "run"
        result = runner.run_experiment(spec, out)  # The actual artifact store.
        self.assertEqual((result["status"], result["complete"]), ("completed_with_failures", False))  # The failing fixture.
        verified = artifacts.verify_run(out)  # Re-hashes every file and ledger object and recomputes the report.
        self.assertTrue(verified["finished"])
        self.assertEqual(verified["manifest_sha256"], result["manifest_sha256"])
        arms = verified["report"]["summary"]["arms"]
        named, raw = retained(out)
        attempts = {}
        for attempt in verified["attempts"]:
            attempts.setdefault(attempt["arm"], []).append(attempt)

        # Pins: the recorded binary is the one the operator script built from the clone's HEAD.
        pin = verified["plan"]["provenance"]["arms"]["cairn-lexical"]
        self.assertEqual(pin["binary"]["vcs_revision"], self.pins["vcs_revision"])
        self.assertEqual(pin["binary"]["sha256"], self.pins["binary_sha256"])
        self.assertEqual((pin["checkout"]["head"], pin["checkout"]["dirty"]), (self.pins["vcs_revision"], False))
        self.assertEqual(pin["lifecycle_wrapper"]["sha256"],
                         runner.file_sha256(Path(self.pins["checkout"]) / "scripts/trial-task-eval.sh"))
        self.assertFalse(pin["lifecycle_wrapper"]["from_environment"])
        harness = verified["plan"]["provenance"]["runner"]
        for name in ("runner", "cairn", "contracts", "metrics", "artifacts", "report"):
            self.assertIn(f"caplab.retrieval.{name}", harness["modules"])  # The modules that scored and recorded it.

        # Real retrieval: every assignment ran, answerable queries found their note first.
        lexical = attempts["cairn-lexical"]
        self.assertEqual({a["status"] for a in lexical}, {"ok"})
        first = {a["query_id"]: a["ranked_ids"] for a in lexical if a["seed"] == 0}
        self.assertEqual([first[q][0] for q in ("q-restart", "q-backup", "q-cert")], ["n-restart", "n-backup", "n-cert"])
        self.assertTrue(all(a["latency_ns"] > 0 and a["delivered_ids"] is None for a in lexical))

        # Controls honoured by the store itself: superseded, local-only and other-collection notes are never delivered.
        delivered = {note for a in lexical + attempts["cairn-semantic"] for note in a["ranked_ids"]}
        self.assertFalse(delivered & {"n-cert-old", "n-local", "n-other"}, delivered)

        # No-answer controls: Cairn's lexical ranker returns a weak match for "office wifi password"
        # (a measured false positive) and nothing for nonsense words.
        self.assertTrue(first["q-none"], "expected a lexical false positive on the office query")
        self.assertEqual(first["q-zebra"], [])
        # The metric counts control assignments (two controls x two seeds); derive the expected counts
        # from the recorded attempts rather than assuming them.
        controls = [a for a in lexical if a["query_id"] in ("q-none", "q-zebra")]
        expected = (sum(bool(a["ranked_ids"][:3]) for a in controls), len(controls))
        fp = arms["cairn-lexical"]["cutoffs"]["3"]["controls"]["false_positive_rate"]
        self.assertEqual((fp["numerator"], fp["denominator"]), expected)
        self.assertEqual(expected, (2, 4))  # q-none answers weakly under both seeds; q-zebra is always clean.
        empty = arms["empty"]["cutoffs"]["3"]["controls"]["false_positive_rate"]
        self.assertEqual((empty["numerator"], empty["denominator"]), (0, 4))

        # Semantic requested with no worker: labelled lexical fallback, recorded truthfully.
        for attempt in attempts["cairn-semantic"]:
            semantic = attempt["observation"]["semantic"]
            self.assertEqual((semantic["requested"], semantic["state"], semantic["fallback"]), (True, "unavailable", True))
            self.assertEqual(attempt["observation"]["rankings"], ["lexical-scope-recency/4"])
            self.assertEqual(attempt["observation"]["status"], ["DEGRADED_NO_EMBEDDINGS"])
        self.assertEqual(lexical[0]["observation"]["rankings"], ["binary-idf-scope-recency/1"])

        # The fixtures are discriminated by the same metrics.
        def recall(arm):
            block = arms[arm]["cutoffs"]["1"]["answerable"]["conditional"]["recall"]
            return block["numerator"] / block["denominator"]

        self.assertEqual((recall("good"), recall("bad"), recall("empty"), recall("cairn-lexical")), (1, 0, 0, 1))
        self.assertEqual(arms["failing"]["coverage"]["scorable"], 0)

        # Evidence from the isolated stores is retained in the run's ledger, and nothing is left running.
        for arm in ("cairn-lexical", "cairn-semantic"):
            self.assertTrue(named[f"arm.{arm}.postgres.log"])
            self.assertTrue(named[f"arm.{arm}.api.log"])
            readiness = json.loads(named[f"arm.{arm}.readiness.json"])
            self.assertEqual(readiness["semantic_requested"], arm == "cairn-semantic")
        # The exact bytes Cairn returned are retained and agree with the recorded ranking.
        restart = next(a for a in lexical if (a["query_id"], a["seed"]) == ("q-restart", 0))
        entries = json.loads(raw[("cairn-lexical:q-restart:0", "search-page-001.json")])["data"]["index"]
        self.assertGreaterEqual(len(entries), len(restart["ranked_ids"]))
        self.assertTrue(all(entry["record_id"] for entry in entries))
        self.assert_no_store_left()
        if evidence:
            (Path(evidence) / "verify.json").write_text(json.dumps({
                "manifest_sha256": verified["manifest_sha256"], "finished": verified["finished"],
                "verification": verified["verification"], "status": result["status"]}, indent=2, sort_keys=True))
            (Path(evidence) / "report.md").write_text(report_module.render_markdown(verified["report"]))

    def test_a_wrapper_that_reports_a_failed_cleanup_leaves_a_real_run_unfinished(self):
        real = Path(self.pins["checkout"]) / cairn.WRAPPER
        override = self.tmp / "failing-cleanup-wrapper.sh"
        override.write_text(f'#!/usr/bin/env bash\nbash {real} "$@"; status=$?\n'
                            'echo "cleanup failed: injected after the real cluster was removed" >&2\n'
                            'exit $(( status == 0 ? 1 : status ))\n')
        override.chmod(0o755)
        out = self.tmp / "run"
        with mock.patch.dict(os.environ, {cairn.WRAPPER_ENV: str(override)}):
            with self.assertRaises(runner.RunnerCleanupError) as caught:
                runner.run_experiment(make_spec([self.arm("cairn", "off")], queries=QUERIES[:2]), out)
        self.assertIn("exited with status 1 after a clean stop", caught.exception.failures["cairn"])
        with self.assertRaises(artifacts.ArtifactIntegrityError) as refused:
            artifacts.verify_run(out)
        self.assertEqual(refused.exception.code, "RUN_NOT_FINISHED")
        verified = artifacts.verify_run(out, allow_unfinished=True)
        self.assertFalse(verified["finished"])
        self.assertEqual([a["status"] for a in verified["attempts"]], ["ok", "ok"])  # Real measurements, untouched.
        named, _ = retained(out)
        self.assertIn(b"cleanup failed: injected", named["arm.cairn.host.stderr"])
        self.assertTrue(named["arm.cairn.postgres.log"])
        self.assertFalse((out / "report.json").exists())
        self.assert_no_store_left()  # The real wrapper did remove its cluster; the failure is what it reported.

    def test_a_modified_checkout_is_refused_before_any_store_exists(self):
        marker = Path(self.pins["checkout"]) / "UNCOMMITTED"
        marker.write_text("change\n")
        try:
            with self.assertRaises(runner.AdapterError) as caught:
                runner.run_experiment(make_spec([self.arm("cairn", "off")]), self.tmp / "run")
        finally:
            marker.unlink()
        self.assertEqual(caught.exception.code, "pin_mismatch")
        self.assertFalse((self.tmp / "run").exists())
        self.assertEqual(store_roots() - self.roots_before, set())

    def test_sigterm_during_a_real_run_leaves_evidence_and_no_orphans(self):
        code = """
import json, sys
from pathlib import Path
from caplab.retrieval import runner
from tests.retrieval_support import make_spec
arm = dict(id="cairn", adapter="cairn", configuration=json.loads(sys.argv[1]))
result = runner.run_experiment(make_spec([arm]), Path(sys.argv[2]))
print("finished", result["status"], result["report"]["summary"]["arms"]["cairn"]["coverage"]["by_status"])
"""
        configuration = {"binary": self.pins["binary"], "checkout": self.pins["checkout"], "semantic_mode": "off"}
        out = self.tmp / "sigterm-run"
        env = dict(os.environ, PYTHONPATH=f"{ROOT / 'src'}:{ROOT}")
        proc = subprocess.Popen([sys.executable, "-c", code, json.dumps(configuration), str(out)], cwd=ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline and not (out / "plan.json").exists():
                time.sleep(0.05)
            time.sleep(0.6)  # Inside provisioning: the cluster is being built.
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=90)
        finally:
            if proc.poll() is None:
                proc.kill()
        self.assertEqual(proc.returncode, 0, stderr)
        verified = artifacts.verify_run(out)  # The interrupted run was still finished and verifies.
        self.assertEqual(len(verified["attempts"]), len(QUERIES))
        self.assertEqual({a["status"] for a in verified["attempts"]}, {"not_started"})  # Before any assignment ran.
        self.assertIn("finished completed_with_failures", stdout)
        self.assertIn("'not_started': 4", stdout)
        self.assert_no_store_left()


if __name__ == "__main__":
    unittest.main()
