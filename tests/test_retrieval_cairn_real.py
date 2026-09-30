"""Real Cairn against a fresh disposable PostgreSQL cluster (opt-in integration test).

    CAPLAB_CAIRN_CHECKOUT=~/git/cairn PYTHONPATH=src python3 -m unittest tests.test_retrieval_cairn_real -v

Needs `git`, `go` and PostgreSQL 16+ binaries (CAPLAB_RETRIEVAL_PG_BIN, CAIRN_PG_BIN or
`pg_config`). The test clones the checkout at its HEAD and builds its binary with
scripts/retrieval_pin_cairn.py; the source checkout is only read. Nothing here can reach a
production database, API socket or profile: every store is a private cluster under /tmp on a
Unix socket, and the environment given to Cairn is rebuilt from scratch.
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

from caplab.retrieval import runner
from tests.retrieval_support import (QUERIES, StubArtifacts, command_arm, make_spec, read_attempts,
                                     write_retriever)

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = os.environ.get("CAPLAB_CAIRN_CHECKOUT", "")


def store_roots():
    """CAPLAB's store directories and the wrapper's disposable clusters."""
    return set(glob.glob("/tmp/caplab-rtv-*")) | set(glob.glob("/tmp/cairn-task-eval-pg.*"))


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
        StubArtifacts.instances.clear()

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
        report = runner.run_experiment(spec, self.tmp / "run", artifacts_factory=StubArtifacts)["report"]
        art = StubArtifacts.instances[-1]
        arms = report["summary"]["arms"]
        attempts = {}
        for attempt in art.attempts:
            attempts.setdefault(attempt["arm"], []).append(attempt)

        # Pins: the recorded binary is the one the operator script built from the clone's HEAD.
        pin = art.provenance["arms"]["cairn-lexical"]
        self.assertEqual(pin["binary"]["vcs_revision"], self.pins["vcs_revision"])
        self.assertEqual(pin["binary"]["sha256"], self.pins["binary_sha256"])
        self.assertEqual((pin["checkout"]["head"], pin["checkout"]["dirty"]), (self.pins["vcs_revision"], False))

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

        # Evidence from the isolated stores is retained, and nothing is left running.
        for arm in ("cairn-lexical", "cairn-semantic"):
            self.assertTrue(art.registered[f"arm.{arm}.postgres.log"])
            self.assertTrue(art.registered[f"arm.{arm}.api.log"])
            readiness = json.loads(art.registered[f"arm.{arm}.readiness.json"])
            self.assertEqual(readiness["semantic_requested"], arm == "cairn-semantic")
        self.assert_no_store_left()

    def test_a_modified_checkout_is_refused_before_any_store_exists(self):
        marker = Path(self.pins["checkout"]) / "UNCOMMITTED"
        marker.write_text("change\n")
        try:
            with self.assertRaises(runner.AdapterError) as caught:
                runner.run_experiment(make_spec([self.arm("cairn", "off")]), self.tmp / "run",
                                      artifacts_factory=StubArtifacts)
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
from tests.retrieval_support import StubArtifacts, make_spec
arm = dict(id="cairn", adapter="cairn", configuration=json.loads(sys.argv[1]))
report = runner.run_experiment(make_spec([arm]), Path(sys.argv[2]), artifacts_factory=StubArtifacts)
print("finished", report["report"]["summary"]["arms"]["cairn"]["coverage"]["by_status"])
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
        attempts = read_attempts(out)
        self.assertEqual(len(attempts), len(QUERIES))
        self.assertEqual({a["status"] for a in attempts}, {"not_started"})  # Interrupted before any assignment ran.
        self.assertTrue((out / "report.json").is_file())
        self.assertIn("'not_started': 4", stdout)
        self.assert_no_store_left()


if __name__ == "__main__":
    unittest.main()
