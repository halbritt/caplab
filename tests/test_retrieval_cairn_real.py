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

import json
import os
import re
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
from caplab.retrieval import artifacts, cairn, contracts, report as report_module, runner
from tests.retrieval_support import QUERIES, command_arm, make_spec, write_retriever

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = os.environ.get("CAPLAB_CAIRN_CHECKOUT", "")


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


def source_strings(checkout, pattern):
    """Every string matching `pattern` in the non-test Go source of the pinned checkout.

    Ranking and status labels are read from the source that was built, never assumed: a newer Cairn
    may report another version of the same ranking family.
    """
    found = set()
    for path in Path(checkout).rglob("*.go"):
        if not path.name.endswith("_test.go"):
            found |= set(re.findall(pattern, path.read_text(errors="replace")))
    return found


def processes_mentioning(paths):
    """Running processes whose command line names one of `paths` (a cairn server, a postgres or a wrapper)."""
    paths = [str(p) for p in paths if p]
    if not paths:
        return []
    done = subprocess.run(["pgrep", "-af", "|".join(re.escape(p) for p in paths)], capture_output=True, text=True)
    return [line for line in done.stdout.splitlines() if "pgrep" not in line]


def spec_adapters(spec, arms):
    """Explicit Cairn adapters, so a test knows exactly which store directories it created."""
    normalized = contracts.validate_spec(spec)
    return {arm["id"]: cairn.CairnAdapter(arm, normalized) for arm in normalized["arms"] if arm["id"] in arms}


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

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def arm(self, arm_id, semantic_mode):
        return {"id": arm_id, "adapter": "cairn", "configuration": {
            "binary": self.pins["binary"], "checkout": self.pins["checkout"], "semantic_mode": semantic_mode}}

    def assert_released(self, *adapters):
        """Exactly the directories and processes these adapters created are gone (other agents may run their own)."""
        paths = [path for adapter in adapters for path in (adapter.root, adapter.pg_root) if path]
        for path in paths:
            self.assertFalse(Path(path).exists(), f"{path} was left behind")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and processes_mentioning(paths):
            time.sleep(0.2)
        self.assertEqual(processes_mentioning(paths), [], "a postgres, cairn or wrapper process was left")

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
        adapters = spec_adapters(spec, {"cairn-lexical", "cairn-semantic"})
        result = runner.run_experiment(spec, out, adapters=adapters)  # The actual artifact store.
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

        # Semantic requested with no worker: labelled lexical fallback, recorded truthfully. The ranking
        # versions are taken from the pinned source: the lexical arm uses the binary-idf family, the
        # fallback its own lexical family, and each arm reports one consistent version.
        idf_versions = source_strings(self.pins["checkout"], r"binary-idf-scope-recency/\d+")
        fallback_versions = source_strings(self.pins["checkout"], r"lexical-scope-recency/\d+")
        self.assertTrue(idf_versions and fallback_versions, "no ranking versions found in the pinned source")
        self.assertIn("DEGRADED_NO_EMBEDDINGS", source_strings(self.pins["checkout"], r"DEGRADED_NO_EMBEDDINGS"))
        for attempt in attempts["cairn-semantic"]:
            semantic = attempt["observation"]["semantic"]
            self.assertEqual((semantic["requested"], semantic["state"], semantic["fallback"]), (True, "unavailable", True))
            self.assertEqual(len(attempt["observation"]["rankings"]), 1)
            self.assertLessEqual(set(attempt["observation"]["rankings"]), fallback_versions)
            self.assertEqual(attempt["observation"]["status"], ["DEGRADED_NO_EMBEDDINGS"])
        lexical_rankings = {tuple(a["observation"]["rankings"]) for a in lexical}
        self.assertEqual(len(lexical_rankings), 1, lexical_rankings)
        self.assertLessEqual(set(next(iter(lexical_rankings))), idf_versions)
        self.assertEqual({r for a in attempts["cairn-semantic"] for r in a["observation"]["rankings"]} & idf_versions, set())
        readiness_ranking = json.loads(named["arm.cairn-lexical.readiness.json"])["ranking"]
        self.assertEqual([readiness_ranking], list(next(iter(lexical_rankings))))  # The probe saw the same ranker.

        # The fixtures are discriminated by the same metrics.
        def recall(arm):
            block = arms[arm]["cutoffs"]["1"]["answerable"]["conditional"]["recall"]
            return block["numerator"] / block["denominator"]

        self.assertEqual((recall("good"), recall("bad"), recall("empty"), recall("cairn-lexical")), (1, 0, 0, 1))
        self.assertEqual(arms["failing"]["coverage"]["scorable"], 0)

        # Every arm's store was seeded identically and in corpus order; the order is recorded.
        order = [note["id"] for note in spec["corpus"]]
        for arm in ("cairn-lexical", "cairn-semantic"):
            self.assertEqual([e["note_id"] for e in json.loads(named[f"arm.{arm}.seeding.json"])["order"]], order)
            self.assertEqual(verified["plan"]["provenance"]["arms"][arm]["seeding"]["notes"], len(order))

        # Evidence from the isolated stores is retained in the run's ledger, and nothing is left running.
        for arm in ("cairn-lexical", "cairn-semantic"):
            self.assertTrue(named[f"arm.{arm}.postgres.log"])
            self.assertTrue(named[f"arm.{arm}.api.log"])
            readiness = json.loads(named[f"arm.{arm}.readiness.json"])
            self.assertEqual(readiness["semantic_requested"], arm == "cairn-semantic")
            self.assertTrue(adapters[arm].pg_root and adapters[arm].root)  # What the release check inspects.
        # The exact bytes Cairn returned are retained and agree with the recorded ranking.
        restart = next(a for a in lexical if (a["query_id"], a["seed"]) == ("q-restart", 0))
        entries = json.loads(raw[("cairn-lexical:q-restart:0", "search-page-001.json")])["data"]["index"]
        self.assertGreaterEqual(len(entries), len(restart["ranked_ids"]))
        self.assertTrue(all(entry["record_id"] for entry in entries))
        self.assert_released(*adapters.values())
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
        spec = make_spec([self.arm("cairn", "off")], queries=QUERIES[:2])
        with mock.patch.dict(os.environ, {cairn.WRAPPER_ENV: str(override)}):
            adapters = spec_adapters(spec, {"cairn"})
            with self.assertRaises(runner.RunnerCleanupError) as caught:
                runner.run_experiment(spec, out, adapters=adapters)
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
        self.assert_released(*adapters.values())  # The real wrapper did remove its cluster; the failure is its status.

    def test_a_modified_checkout_is_refused_before_any_store_exists(self):
        marker = Path(self.pins["checkout"]) / "UNCOMMITTED"
        marker.write_text("change\n")
        spec = make_spec([self.arm("cairn", "off")])
        adapters = spec_adapters(spec, {"cairn"})
        try:
            with self.assertRaises(runner.AdapterError) as caught:
                runner.run_experiment(spec, self.tmp / "run", adapters=adapters)
        finally:
            marker.unlink()
        self.assertEqual(caught.exception.code, "pin_mismatch")
        self.assertFalse((self.tmp / "run").exists())
        self.assertIsNone(adapters["cairn"].root)  # No store directory was ever created.
        self.assertEqual(processes_mentioning([Path(self.pins["checkout"]) / cairn.WRAPPER]), [])  # No wrapper ran.

    def test_sigterm_during_a_real_run_leaves_evidence_and_no_orphans(self):
        code = """
import json, sys
from pathlib import Path
from caplab.retrieval import cairn, contracts, runner
from tests.retrieval_support import make_spec
arm = dict(id="cairn", adapter="cairn", configuration=json.loads(sys.argv[1]))
spec = make_spec([arm])
adapter = cairn.CairnAdapter(contracts.validate_spec(spec)["arms"][0], contracts.validate_spec(spec))
result = runner.run_experiment(spec, Path(sys.argv[2]), adapters={"cairn": adapter})
print("finished", result["status"], result["report"]["summary"]["arms"]["cairn"]["coverage"]["by_status"])
print("stores", json.dumps([str(adapter.root), adapter.pg_root]))
"""
        configuration = {"binary": self.pins["binary"], "checkout": self.pins["checkout"], "semantic_mode": "off"}
        out = self.tmp / "sigterm-run"
        wrapper = Path(self.pins["checkout"]) / cairn.WRAPPER  # Unique to this test class: only our wrapper matches.
        env = dict(os.environ, PYTHONPATH=f"{ROOT / 'src'}:{ROOT}")
        proc = subprocess.Popen([sys.executable, "-c", code, json.dumps(configuration), str(out)], cwd=ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline and not processes_mentioning([wrapper]):
                time.sleep(0.05)  # The wrapper is running: the cluster is being built.
            self.assertTrue(processes_mentioning([wrapper]), "the wrapper never started")
            time.sleep(0.6)
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=90)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()
        self.assertEqual(proc.returncode, 0, stderr)
        verified = artifacts.verify_run(out)  # The interrupted run was still finished and verifies.
        self.assertEqual(len(verified["attempts"]), len(QUERIES))
        self.assertEqual({a["status"] for a in verified["attempts"]}, {"not_started"})  # Before any assignment ran.
        self.assertIn("finished completed_with_failures", stdout)
        self.assertIn("'not_started': 4", stdout)
        root, pg_root = json.loads(stdout.splitlines()[-1].split(" ", 1)[1])
        self.assertTrue(root != "None", "the store directory was never created")
        self.assertFalse(Path(root).exists())
        if pg_root:
            self.assertFalse(Path(pg_root).exists())
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and processes_mentioning([root, pg_root, wrapper]):
            time.sleep(0.2)
        self.assertEqual(processes_mentioning([root, pg_root, wrapper]), [], "a postgres, cairn or wrapper process was left")


if __name__ == "__main__":
    unittest.main()
