import importlib.util
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import types
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock

from caplab.retrieval import contracts, runner
from tests.retrieval_support import (QUERIES, StubArtifacts, command_arm, make_git_checkout, make_spec,
                                     read_attempts, write_retriever)

ROOT = Path(__file__).resolve().parents[1]


class RunnerCase(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)
        self.scripts = self.tmp / "scripts"
        self.scripts.mkdir()
        self.out = self.tmp / "run"
        StubArtifacts.instances.clear()

    def arm(self, name, arm_id=None):
        return command_arm(arm_id or name, write_retriever(self.scripts, name))

    def run_spec(self, spec, **kwargs):
        # run_experiment returns the artifact store's finish() result; `report` is its report.
        self.result = runner.run_experiment(spec, self.out, artifacts_factory=StubArtifacts, **kwargs)
        return self.result["report"], StubArtifacts.instances[-1]

    def run_arms(self, names, **spec_kwargs):
        spec = make_spec([self.arm(name) for name in names], **spec_kwargs)
        report, artifacts = self.run_spec(spec)
        return spec, report, artifacts

    @staticmethod
    def by_arm(artifacts):
        grouped = {}
        for attempt in artifacts.attempts:
            grouped.setdefault(attempt["arm"], []).append(attempt)
        return grouped


class PlanAndRosterTests(RunnerCase):
    def test_plan_is_sealed_before_any_attempt_and_the_roster_is_complete(self):
        spec, report, art = self.run_arms(["good", "bad"], seeds=(0, 1))
        self.assertEqual(art.calls[0], "plan")
        first_attempt = next(i for i, call in enumerate(art.calls) if isinstance(call, tuple) and call[0] == "attempt")
        self.assertGreater(first_attempt, 0)
        roster = [a["assignment_id"] for a in contracts.assignments(contracts.validate_spec(spec))]
        self.assertEqual([call[1] for call in art.calls if isinstance(call, tuple) and call[0] == "attempt"], roster)
        self.assertEqual(len(roster), 2 * len(QUERIES) * 2)
        plan = json.loads((self.out / "plan.json").read_text())
        self.assertEqual(plan["spec_digest"], contracts.spec_digest(plan["spec"]))
        self.assertEqual(len(plan["roster"]), len(roster))
        self.assertTrue(art.finished)
        self.assertEqual(report["summary"]["arms"]["good"]["coverage"]["planned"], len(QUERIES) * 2)

    def test_the_artifact_stores_finish_result_is_returned_unchanged(self):
        _, report, art = self.run_arms(["good"])
        self.assertIs(art.finished, True)
        self.assertEqual(set(self.result), {"status", "complete", "run", "report", "manifest_sha256", "output",
                                            "report_path"})
        self.assertEqual((self.result["status"], self.result["complete"]), ("complete", True))
        self.assertIs(self.result["report"], report)
        self.assertEqual(self.result["output"], str(self.out))
        self.assertTrue(Path(self.result["report_path"]).is_file())

    def test_provenance_pins_each_arms_executable_and_script(self):
        _, _, art = self.run_arms(["good"])
        pins = art.provenance["arms"]["good"]
        self.assertEqual(pins["adapter"], "command")
        self.assertEqual(set(pins["files"]), {"argv[0]", "argv[1]"})
        self.assertTrue(all(f["sha256"].startswith("sha256:") for f in pins["files"].values()))

    def test_provenance_pins_the_harness_modules_that_were_actually_loaded(self):
        _, _, art = self.run_arms(["good"])
        identity = art.provenance["runner"]
        modules = identity["modules"]
        for name in ("caplab.retrieval.contracts", "caplab.retrieval.metrics", "caplab.retrieval.runner"):
            path = Path(sys.modules[name].__file__)
            self.assertEqual(modules[name], {"path": str(path.resolve()), "sha256": runner.file_sha256(path)})
        # The artifact store in use is pinned as well, from the module its class was loaded from.
        support = Path(sys.modules[StubArtifacts.__module__].__file__)
        self.assertEqual(modules[StubArtifacts.__module__]["sha256"], runner.file_sha256(support))
        # A module is pinned only if it was loaded: never a hash of a file that did not run.
        self.assertTrue(all(name in sys.modules for name in modules))
        with mock.patch.dict(sys.modules):
            sys.modules.pop("caplab.retrieval.compare", None)
            self.assertNotIn("caplab.retrieval.compare", runner._runner_identity()["modules"])
        self.assertEqual(set(identity["checkout"]), {"commit", "modified"} | (
            {"reason"} if identity["checkout"]["commit"] is None else set()))

    def test_the_pinned_bytes_are_the_bytes_that_ran(self):
        # Another copy of the runner with different bytes must produce a different pin.
        source = Path(runner.__file__)
        copy = self.tmp / "runner_copy.py"
        copy.write_bytes(source.read_bytes() + b"\n# edited\n")
        self.assertNotEqual(runner.file_sha256(copy), runner.file_sha256(source))
        with mock.patch.dict(sys.modules, {"caplab.retrieval.runner": types.SimpleNamespace(__file__=str(copy))}):
            modules = runner._runner_identity()["modules"]
        self.assertEqual(modules["caplab.retrieval.runner"]["sha256"], runner.file_sha256(copy))


    def test_a_normalized_spec_is_accepted_unchanged(self):
        spec = contracts.validate_spec(make_spec([self.arm("good")]))
        report, art = self.run_spec(spec)
        self.assertEqual(report["spec_digest"], contracts.spec_digest(spec))

    def test_every_seed_is_its_own_assignment_and_reaches_the_retriever(self):
        _, _, art = self.run_arms(["seeded"], seeds=(0, 1, 2))
        self.assertEqual(len(art.attempts), len(QUERIES) * 3)
        tops = {a["seed"]: a["ranked_ids"][0] for a in art.attempts if a["query_id"] == "q-backup"}
        self.assertEqual(len(set(tops.values())), 3)  # The fixture ranks differently per seed.


class GitStateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)

    def test_a_clean_checkout_reports_its_commit_and_is_not_modified(self):
        path, head = make_git_checkout(self.tmp)
        self.assertEqual(runner._git_state(path), {"commit": head, "modified": False})

    def test_an_edit_or_an_untracked_file_makes_the_checkout_modified(self):
        path, head = make_git_checkout(self.tmp)
        (path / "README").write_text("edited\n")
        self.assertEqual(runner._git_state(path), {"commit": head, "modified": True})
        (path / "README").write_text("fixture\n")
        (path / "new.py").write_text("x = 1\n")
        self.assertEqual(runner._git_state(path), {"commit": head, "modified": True})

    def test_a_directory_that_is_not_a_checkout_is_unknown_not_clean(self):
        state = runner._git_state(self.tmp)
        self.assertEqual((state["commit"], state["modified"]), (None, None))
        self.assertIn("reason", state)

    def test_reading_the_state_does_not_touch_the_checkout(self):
        path, _ = make_git_checkout(self.tmp)
        before = sorted(p.name for p in (path / ".git").iterdir())
        runner._git_state(path)
        self.assertEqual(sorted(p.name for p in (path / ".git").iterdir()), before)  # No index.lock or the like.


class EarlyFailureTests(RunnerCase):
    def test_contract_errors_raise_before_anything_is_created(self):
        spec = make_spec([self.arm("good")])
        spec["queries"] = spec["queries"] + [dict(spec["queries"][0])]  # duplicate query id
        with self.assertRaises(contracts.ContractError):
            runner.run_experiment(spec, self.out, artifacts_factory=StubArtifacts)
        self.assertFalse(self.out.exists())
        self.assertEqual(StubArtifacts.instances, [])

    def test_an_existing_output_directory_is_refused(self):
        self.out.mkdir()
        with self.assertRaises(FileExistsError):
            runner.run_experiment(make_spec([self.arm("good")]), self.out, artifacts_factory=StubArtifacts)
        self.assertEqual(list(self.out.iterdir()), [])  # Nothing was written into it.

    def test_an_unpinnable_arm_fails_closed_before_the_plan_is_sealed(self):
        arm = {"id": "ghost", "adapter": "command", "configuration": {"argv": [str(self.tmp / "missing")]}}
        with self.assertRaises(runner.AdapterError) as caught:
            runner.run_experiment(make_spec([arm]), self.out, artifacts_factory=StubArtifacts)
        self.assertEqual(caught.exception.code, "command_unavailable")
        self.assertFalse(self.out.exists())


class DiscriminationTests(RunnerCase):
    def test_good_bad_empty_and_failing_retrievers_are_discriminated(self):
        _, report, art = self.run_arms(["good", "bad", "empty", "failing"])
        arms = report["summary"]["arms"]

        def recall(arm, k="1"):
            # A Mean is the exact fraction of the mean recall over `count` scored queries.
            block = arms[arm]["cutoffs"][k]["answerable"]["conditional"]["recall"]
            return Fraction(block["numerator"], block["denominator"]), block["count"]

        self.assertEqual(recall("good"), (1, 3))  # All three answerable queries found their note at rank 1.
        self.assertEqual(recall("bad"), (0, 3))
        self.assertEqual(recall("empty"), (0, 3))
        # The failing arm produced nothing scorable: its failures are not quality or abstention.
        self.assertEqual(arms["failing"]["coverage"]["scorable"], 0)
        self.assertEqual(arms["failing"]["coverage"]["failures"], len(QUERIES))
        clean = {arm: arms[arm]["cutoffs"]["3"]["controls"]["clean_all_assignments"]["numerator"]
                 for arm in ("empty", "failing")}
        self.assertEqual(clean, {"empty": 1, "failing": 0})  # An empty list abstains; a failure does not.
        failing = self.by_arm(art)["failing"]
        self.assertTrue(all(a["status"] == "error" and a["ranked_ids"] == [] for a in failing))
        self.assertTrue(all(a["error"]["code"] == "nonzero_exit" and a["error"]["exit_code"] == 3 for a in failing))
        self.assertIn("retriever exploded", failing[0]["error"]["stderr_tail"])


class ClassifiedFailureTests(RunnerCase):
    CASES = {
        "malformed": ("malformed_response", None),
        "nan": ("malformed_response", None),
        "wrong_schema": ("schema_mismatch", None),
        "extra_field": ("schema_mismatch", None),
        "duplicate": ("invalid_response", "DUPLICATE_ID"),
        "unknown": ("invalid_response", "UNKNOWN_ID"),
        "not_list": ("schema_mismatch", None),
    }

    def test_each_bad_response_is_a_classified_failure_with_its_raw_bytes_kept(self):
        _, report, art = self.run_arms(list(self.CASES))
        for arm, (code, contract_code) in self.CASES.items():
            with self.subTest(arm=arm):
                attempts = self.by_arm(art)[arm]
                self.assertEqual({a["status"] for a in attempts}, {"error"})
                self.assertEqual({a["error"]["code"] for a in attempts}, {code})
                if contract_code:
                    self.assertEqual({a["error"]["contract_code"] for a in attempts}, {contract_code})
                self.assertTrue(all(a["ranked_ids"] == [] and a["delivered_ids"] is None for a in attempts))
                folder = self.out / "raw" / attempts[0]["assignment_id"].replace(":", "__")
                self.assertTrue((folder / "stdout").is_file() and (folder / "request").is_file())
                self.assertEqual(report["summary"]["arms"][arm]["coverage"]["failures"], len(QUERIES))

    def test_a_string_is_never_split_into_note_ids(self):
        # With one-character note IDs, coercing "ab" to ["a", "b"] would pass the contract.
        corpus = [{"id": "a", "body": "alpha note"}, {"id": "b", "body": "beta note"}]
        queries = [{"id": "q", "text": "alpha", "relevant_ids": ["a"]}]
        script = self.scripts / "string.py"
        script.write_text("import json, sys\njson.load(sys.stdin)\n"
                          "print(json.dumps(dict(schema_version='caplab-retrieval-response/1', ranked_ids='ab')))\n")
        spec = make_spec([command_arm("str", script)], corpus=corpus, queries=queries)
        _, art = self.run_spec(spec)
        attempt = art.attempts[0]
        self.assertEqual((attempt["status"], attempt["error"]["code"]), ("error", "schema_mismatch"))
        self.assertEqual(attempt["ranked_ids"], [])

    def test_oversized_output_is_killed_and_classified(self):
        with mock.patch.object(runner, "MAX_OUTPUT_BYTES", 100_000):
            _, _, art = self.run_arms(["flood"])
        attempts = art.attempts
        self.assertEqual({a["error"]["code"] for a in attempts}, {"output_too_large"})
        folder = self.out / "raw" / attempts[0]["assignment_id"].replace(":", "__")
        self.assertEqual((folder / "stdout").stat().st_size, 100_000)  # The retained bytes are capped.

    def test_a_timeout_is_recorded_and_the_process_group_is_killed(self):
        token = f"caplab-grandchild-{os.getpid()}-{time.monotonic_ns()}"
        script = write_retriever(self.scripts, "grandchild")
        arm = {"id": "hang", "adapter": "command",
               "configuration": {"argv": [sys.executable, str(script), token]}}
        # The grandchild's command line carries the token so its survival is observable.
        script.write_text(script.read_text().replace("'import time; time.sleep(120)'",
                                                     "'import time; time.sleep(120)', sys.argv[1]"))
        spec = make_spec([arm], timeout_seconds=1, queries=QUERIES[:1])
        started = time.monotonic()
        _, art = self.run_spec(spec)
        self.assertLess(time.monotonic() - started, 8)
        attempt = art.attempts[0]
        self.assertEqual((attempt["status"], attempt["error"]["code"]), ("timeout", "timeout"))
        self.assertGreaterEqual(attempt["latency_ns"], 1_000_000_000)
        time.sleep(0.3)
        self.assertNotEqual(subprocess.run(["pgrep", "-f", token], capture_output=True).returncode, 0,
                            "a descendant of the timed-out retriever survived")


class CancellationScopeTests(RunnerCase):
    """Cancelling one retriever's process group must never touch unrelated processes."""

    def bystander(self, *, new_session):
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)", f"bystander-{os.getpid()}-{new_session}"],
                                start_new_session=new_session)
        self.addCleanup(lambda: (proc.kill(), proc.wait()))
        return proc

    def test_a_timeout_and_an_interruption_leave_unrelated_processes_alone(self):
        own_group, other_group = self.bystander(new_session=False), self.bystander(new_session=True)
        self.assertEqual(os.getpgid(own_group.pid), os.getpgrp())  # Shares this test process's own group.
        arm = {"id": "hang", "adapter": "command",
               "configuration": {"argv": [sys.executable, str(write_retriever(self.scripts, "grandchild"))]}}
        _, art = self.run_spec(make_spec([arm], timeout_seconds=1, queries=QUERIES[:1]))
        self.assertEqual(art.attempts[0]["status"], "timeout")
        stubs = {"a": AdapterFailureTests.Stub(interrupt_at=1)}
        runner.run_experiment(make_spec([dict(self.arm("good"), id="a")], queries=QUERIES[:2]), self.tmp / "second",
                              artifacts_factory=StubArtifacts, adapters=stubs)
        time.sleep(0.3)
        self.assertIsNone(own_group.poll(), "a process in the runner's own group was killed")
        self.assertIsNone(other_group.poll(), "an unrelated process was killed")

    def test_each_call_runs_in_its_own_session_so_a_group_kill_cannot_reach_the_runner(self):
        script = self.scripts / "group.py"
        script.write_text("import json, os, sys\njson.load(sys.stdin)\n"
                          "print(json.dumps(dict(schema_version='caplab-retrieval-response/1', ranked_ids=[],"
                          " observation=dict(pid=os.getpid(), pgid=os.getpgrp(), sid=os.getsid(0)))))\n")
        _, art = self.run_spec(make_spec([command_arm("g", script)], queries=QUERIES[:1]))
        seen = art.attempts[0]["observation"]["reported"]
        self.assertEqual((seen["pgid"], seen["sid"]), (seen["pid"], seen["pid"]))  # Its own group and session.
        self.assertNotEqual(seen["pgid"], os.getpgrp())


class IsolationTests(RunnerCase):
    def test_labels_never_reach_the_retriever(self):
        _, _, art = self.run_arms(["echo_request"], queries=QUERIES)
        for attempt in art.attempts:
            reported = attempt["observation"]["reported"]
            self.assertEqual(reported["request_keys"], ["corpus", "cutoff", "query", "query_id", "schema_version", "seed"])
            self.assertLessEqual(set(reported["note_keys"]), {"id", "body", "kind", "shareable", "repo", "supersede_with"})
            folder = self.out / "raw" / attempt["assignment_id"].replace(":", "__")
            request = (folder / "request").read_text()
            for label in ("relevant_ids", "forbidden_ids", "stratum"):
                self.assertNotIn(label, request)
            self.assertEqual(json.loads(request)["cutoff"], 3)  # The deepest declared cutoff.

    def test_retrievers_get_a_scrubbed_environment_and_an_empty_working_directory(self):
        secrets = {"CAIRN_DATABASE_URL": "postgres://production", "ANTHROPIC_API_KEY": "sk-secret",
                   "AWS_SECRET_ACCESS_KEY": "secret", "CAIRN_HOME": "/home/someone/.local/share/cairn"}
        with mock.patch.dict(os.environ, secrets):
            _, _, art = self.run_arms(["echo_env"], queries=QUERIES[:1])
        reported = art.attempts[0]["observation"]["reported"]
        self.assertLessEqual(set(reported["env"]), {"PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ", "HOME", "TMPDIR",
                                                    "PYTHONDONTWRITEBYTECODE"})
        self.assertTrue(Path(reported["cwd"]).name.startswith("caplab-cmd-"))
        self.assertFalse(Path(reported["cwd"]).exists())  # Removed after the call.


class AdapterFailureTests(RunnerCase):
    class Stub(runner.Adapter):
        def __init__(self, *, opens=None, raises=None, close_raises=None, interrupt_at=None):
            self.opens, self.raises, self.close_raises, self.interrupt_at = opens, raises, close_raises, interrupt_at
            self.calls, self.closed = 0, False

        def open(self):
            if self.opens:
                raise self.opens

        def retrieve(self, query, seed, cutoff, timeout):
            self.calls += 1
            if self.interrupt_at and self.calls == self.interrupt_at:
                raise KeyboardInterrupt
            if self.raises:
                raise self.raises
            return runner.Outcome(ranked_ids=["n-restart"], observation={"stub": True})

        def close(self):
            self.closed = True
            if self.close_raises:
                raise self.close_raises
            return {"store.log": b"stub log"}

    def setUp(self):
        super().setUp()
        good = self.arm("good")
        self.spec = make_spec([dict(good, id="a"), dict(good, id="b")], queries=QUERIES[:2])

    def test_a_non_list_result_from_any_adapter_is_not_coerced_into_ids(self):
        # The command adapter checks types itself; this guards every other adapter. With one-character
        # note IDs, coercing "ab" to ["a", "b"] would pass the contract and fabricate a ranking.
        class Stringy(runner.Adapter):
            def retrieve(self, query, seed, cutoff, timeout):
                return runner.Outcome(ranked_ids="ab")

        corpus = [{"id": "a", "body": "alpha note"}, {"id": "b", "body": "beta note"}]
        queries = [{"id": "q", "text": "alpha", "relevant_ids": ["a"]}]
        spec = make_spec([self.arm("good")], corpus=corpus, queries=queries)
        _, art = self.run_spec(spec, adapters={"good": Stringy()})
        attempt = art.attempts[0]
        self.assertEqual((attempt["status"], attempt["error"]["code"], attempt["error"]["contract_code"]),
                         ("error", "invalid_response", "TYPE"))
        self.assertEqual(attempt["ranked_ids"], [])

    def test_an_arm_that_cannot_open_fails_its_assignments_without_a_fake_result(self):
        stubs = {"a": self.Stub(opens=runner.AdapterError("store_failed", "cluster did not start")), "b": self.Stub()}
        _, art = self.run_spec(self.spec, adapters=stubs)
        grouped = self.by_arm(art)
        self.assertEqual({x["status"] for x in grouped["a"]}, {"error"})
        self.assertEqual({(x["error"]["code"], x["error"]["cause"]) for x in grouped["a"]},
                         {("adapter_unavailable", "store_failed")})
        self.assertEqual({x["status"] for x in grouped["b"]}, {"ok"})  # Other arms are unaffected.

    def test_a_crashing_adapter_is_recorded_not_propagated(self):
        stubs = {"a": self.Stub(raises=RuntimeError("boom")), "b": self.Stub()}
        _, art = self.run_spec(self.spec, adapters=stubs)
        errors = {(x["error"]["code"], x["error"]["type"]) for x in self.by_arm(art)["a"]}
        self.assertEqual(errors, {("adapter_exception", "RuntimeError")})

    def test_a_failure_to_close_leaves_the_run_unfinished_with_its_evidence(self):
        stubs = {"a": self.Stub(close_raises=OSError("cluster still running")), "b": self.Stub()}
        with self.assertRaises(runner.RunnerCleanupError) as caught:
            self.run_spec(self.spec, adapters=stubs)
        art = StubArtifacts.instances[-1]
        error = caught.exception
        self.assertEqual((error.code, error.output), ("cleanup_failed", self.out))
        self.assertEqual(error.failures, {"a": "OSError: cluster still running"})
        self.assertIn("arm a", str(error))
        # Not a success: nothing was finished, reported or given a manifest.
        self.assertFalse(art.finished)
        self.assertNotIn("finish", art.calls)
        self.assertFalse((self.out / "report.json").exists())
        # What was measured and every piece of evidence is retained, unaltered.
        self.assertEqual([(a["assignment_id"], a["status"]) for a in art.attempts],
                         [("a:q-restart:0", "ok"), ("a:q-backup:0", "ok"), ("b:q-restart:0", "ok"), ("b:q-backup:0", "ok")])
        self.assertIn("OSError: cluster still running", art.registered["arm.a.close-error.txt"].decode())
        self.assertEqual(art.registered["arm.b.store.log"], b"stub log")

    def test_an_adapter_cleanup_error_keeps_the_evidence_it_carries(self):
        failing = self.Stub(close_raises=runner.AdapterCleanupError("postgres may still be running",
                                                                    {"api.log": b"api tail"}))
        with self.assertRaises(runner.RunnerCleanupError) as caught:
            self.run_spec(self.spec, adapters={"a": failing, "b": self.Stub()})
        art = StubArtifacts.instances[-1]
        self.assertEqual(caught.exception.failures, {"a": "postgres may still be running"})
        self.assertEqual(art.registered["arm.a.api.log"], b"api tail")
        self.assertEqual(art.registered["arm.a.close-error.txt"], b"postgres may still be running")
        self.assertFalse(art.finished)

    def test_every_arm_is_closed_even_when_an_earlier_close_fails(self):
        stubs = {"a": self.Stub(close_raises=OSError("first")), "b": self.Stub(close_raises=OSError("second"))}
        with self.assertRaises(runner.RunnerCleanupError) as caught:
            self.run_spec(self.spec, adapters=stubs)
        self.assertTrue(stubs["a"].closed and stubs["b"].closed)
        self.assertEqual(set(caught.exception.failures), {"a", "b"})

    def test_an_interrupted_run_whose_cleanup_fails_is_still_unfinished(self):
        stubs = {"a": self.Stub(interrupt_at=2, close_raises=OSError("cluster still running")), "b": self.Stub()}
        with self.assertRaises(runner.RunnerCleanupError):
            self.run_spec(self.spec, adapters=stubs)
        art = StubArtifacts.instances[-1]
        self.assertEqual([a["status"] for a in art.attempts], ["ok", "interrupted", "not_started", "not_started"])
        self.assertFalse(art.finished)
        self.assertIn("arm.a.close-error.txt", art.registered)

    def test_a_clean_close_of_an_interrupted_run_finishes_it_with_the_failures_visible(self):
        _, art = self.run_spec(self.spec, adapters={"a": self.Stub(interrupt_at=2), "b": self.Stub()})
        self.assertEqual((self.result["status"], self.result["complete"]), ("completed_with_failures", False))

    def test_interruption_records_the_running_assignment_then_marks_the_rest_not_started(self):
        stubs = {"a": self.Stub(interrupt_at=2), "b": self.Stub()}
        report, art = self.run_spec(self.spec, adapters=stubs)
        self.assertTrue(art.finished)
        statuses = [(a["assignment_id"], a["status"]) for a in art.attempts]
        self.assertEqual(statuses, [("a:q-restart:0", "ok"), ("a:q-backup:0", "interrupted"),
                                    ("b:q-restart:0", "not_started"), ("b:q-backup:0", "not_started")])
        interrupted = art.attempts[1]
        self.assertEqual(interrupted["error"]["code"], "interrupted")
        self.assertIsInstance(interrupted["latency_ns"], int)
        self.assertIsNone(art.attempts[2]["latency_ns"])
        self.assertTrue(stubs["a"].closed)  # The store is released on the way out.
        coverage = report["summary"]["arms"]["b"]["coverage"]
        self.assertEqual((coverage["not_started"], coverage["scorable"]), (2, 0))

    def test_a_real_sigterm_leaves_durable_evidence_and_no_orphan(self):
        token = f"caplab-sigterm-{os.getpid()}"
        code = f"""
import sys
from pathlib import Path
from caplab.retrieval import runner
from tests.retrieval_support import StubArtifacts, command_arm, make_spec, write_retriever
scripts = Path(sys.argv[1]); scripts.mkdir(exist_ok=True)
slow = write_retriever(scripts, "grandchild")
slow.write_text(slow.read_text().replace("'import time; time.sleep(120)'", "'import time; time.sleep(120)', '{token}'"))
arm = dict(id="hang", adapter="command", configuration=dict(argv=[sys.executable, str(slow)]))
spec = make_spec([arm], timeout_seconds=60)
report = runner.run_experiment(spec, Path(sys.argv[2]), artifacts_factory=StubArtifacts)
print("finished", report["report"]["summary"]["arms"]["hang"]["coverage"]["by_status"])
"""
        out = self.tmp / "sigterm-run"
        env = dict(os.environ, PYTHONPATH=f"{ROOT / 'src'}:{ROOT}")
        proc = subprocess.Popen([sys.executable, "-c", code, str(self.tmp / "s"), str(out)], cwd=ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline and not (out / "plan.json").exists():
                time.sleep(0.05)
            time.sleep(1.0)  # Let the first assignment start.
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=30)
        finally:
            if proc.poll() is None:
                proc.kill()
        self.assertEqual(proc.returncode, 0, stderr)
        attempts = read_attempts(out)
        self.assertEqual(attempts[0]["status"], "interrupted")
        self.assertEqual({a["status"] for a in attempts[1:]}, {"not_started"})
        self.assertEqual(len(attempts), len(QUERIES))
        self.assertTrue((out / "report.json").is_file())
        self.assertIn("'interrupted': 1", stdout)
        time.sleep(0.3)
        self.assertNotEqual(subprocess.run(["pgrep", "-f", token], capture_output=True).returncode, 0,
                            "the retriever's descendant survived the interruption")


@unittest.skipUnless(importlib.util.find_spec("caplab.retrieval.artifacts"), "the artifact store is not present")
class RealArtifactsTests(RunnerCase):
    """The runner against the actual RunArtifacts store, not the stand-in: sealing, evidence chain, verification."""

    Stub = AdapterFailureTests.Stub

    def setUp(self):
        super().setUp()
        from caplab.retrieval import artifacts
        self.artifacts = artifacts
        good = self.arm("good")
        self.spec = make_spec([dict(good, id="a"), dict(good, id="b")], queries=QUERIES[:2])

    def run_real(self, spec, **kwargs):
        return runner.run_experiment(spec, self.out, **kwargs)  # The default factory is RunArtifacts.

    def test_a_complete_run_is_finished_and_verifies(self):
        result = self.run_real(self.spec)
        self.assertEqual((result["status"], result["complete"]), ("complete", True))
        verified = self.artifacts.verify_run(self.out)
        self.assertTrue(verified["finished"])
        self.assertEqual(len(verified["attempts"]), 4)
        self.assertEqual(result["manifest_sha256"], verified["manifest_sha256"])
        self.assertEqual(verified["verification"]["unexpected_files"], [])

    def test_failures_are_reported_not_hidden_and_the_raw_bytes_are_retained(self):
        spec = make_spec([self.arm("good"), self.arm("failing")], queries=QUERIES[:2])
        result = self.run_real(spec)
        self.assertEqual((result["status"], result["complete"]), ("completed_with_failures", False))
        verified = self.artifacts.verify_run(self.out)
        failing = [a for a in verified["attempts"] if a["arm"] == "failing"]
        self.assertEqual({(a["status"], a["error"]["code"]) for a in failing}, {("error", "nonzero_exit")})
        roles = {(r["assignment_id"], r["role"]) for r in verified["report"]["references"]["raw_artifacts"]
                 if "assignment_id" in r}
        self.assertIn(("failing:q-restart:0", "stderr"), roles)

    def test_an_interrupted_run_verifies_with_its_not_started_assignments_accounted_for(self):
        result = self.run_real(self.spec, adapters={"a": self.Stub(interrupt_at=2), "b": self.Stub()})
        self.assertEqual((result["status"], result["complete"]), ("completed_with_failures", False))
        verified = self.artifacts.verify_run(self.out)
        self.assertEqual([a["status"] for a in verified["attempts"]], ["ok", "interrupted", "not_started", "not_started"])

    def test_invalid_observations_keep_raw_evidence_and_do_not_abort_the_roster(self):
        from caplab.qualification.ledger import FilesystemQualificationLedger

        prefix = b'{"schema_version":"caplab-retrieval-response/1","ranked_ids":[],"observation":'
        cases = {
            "overflow": (prefix + b'{"n":1e400}}', "invalid_response"),
            "deep-observation": (prefix + b'{"n":' + b'[' * 40 + b'0' + b']' * 40 + b'}}', "invalid_response"),
            "parser-depth": (b'[' * 100000, "malformed_response"),
        }
        for name, (payload, code) in cases.items():
            with self.subTest(name=name):
                script = self.scripts / f"{name}.py"
                script.write_text(f"import sys\nsys.stdin.buffer.read()\nsys.stdout.buffer.write({payload!r})\n")
                spec = make_spec([command_arm("malformed", script), self.arm("good")], queries=QUERIES[:2])
                output = self.tmp / name
                result = runner.run_experiment(spec, output)
                self.assertEqual(result["status"], "completed_with_failures")
                verified = self.artifacts.verify_run(output)
                self.assertEqual(verified["report"]["run"]["missing"], 0)
                self.assertEqual([a["status"] for a in verified["attempts"]], ["error", "error", "ok", "ok"])
                failures = [a for a in verified["attempts"] if a["arm"] == "malformed"]
                self.assertEqual([a["error"]["code"] for a in failures], [code, code])
                self.assertEqual(verified["report"]["summary"]["arms"]["malformed"]["coverage"]["scorable"], 0)
                ledger = FilesystemQualificationLedger(output / "ledger")
                entries = [json.loads(line) for line in (output / "evidence.jsonl").read_text().splitlines()]
                malformed = [e for e in entries if e.get("assignment_id", "").startswith("malformed:")]
                self.assertEqual(len(malformed), 2)
                for entry in malformed:
                    self.assertEqual(ledger.resolve(entry["raw"]["stdout"]), payload)

    def test_a_cleanup_failure_leaves_a_run_that_only_verifies_as_unfinished(self):
        stubs = {"a": self.Stub(close_raises=runner.AdapterCleanupError("postgres may still be running",
                                                                       {"postgres.log": b"log tail"})),
                 "b": self.Stub()}
        with self.assertRaises(runner.RunnerCleanupError) as caught:
            self.run_real(self.spec, adapters=stubs)
        self.assertEqual(caught.exception.output, self.out)
        self.assertFalse((self.out / "manifest.json").exists())
        self.assertFalse((self.out / "report.json").exists())
        with self.assertRaises(self.artifacts.ArtifactIntegrityError) as refused:
            self.artifacts.verify_run(self.out)
        self.assertEqual(refused.exception.code, "RUN_NOT_FINISHED")
        verified = self.artifacts.verify_run(self.out, allow_unfinished=True)
        self.assertFalse(verified["finished"])
        self.assertEqual([a["status"] for a in verified["attempts"]], ["ok"] * 4)  # The measurements are intact.
        names = {r["name"] for r in verified["report"]["references"]["raw_artifacts"] if "name" in r}
        self.assertEqual(names, {"arm.a.postgres.log", "arm.a.close-error.txt", "arm.b.store.log"})

    def test_the_sealed_plan_carries_the_pins_of_the_modules_that_ran(self):
        self.run_real(self.spec)
        plan = self.artifacts.verify_run(self.out)["plan"]
        modules = plan["provenance"]["runner"]["modules"]
        for name in ("contracts", "metrics", "artifacts", "report", "runner"):
            module = sys.modules[f"caplab.retrieval.{name}"]
            self.assertEqual(modules[f"caplab.retrieval.{name}"]["sha256"], runner.file_sha256(Path(module.__file__)))
        self.assertIn("commit", plan["provenance"]["runner"]["checkout"])
        self.assertEqual(set(plan["provenance"]["arms"]), {"a", "b"})


class BoundedRunTests(unittest.TestCase):
    def test_output_is_capped_and_the_child_is_killed(self):
        done = runner.bounded_run([sys.executable, "-c", "import sys; sys.stdout.write('y' * 10_000_000)"],
                                  timeout=20, limit=50_000)
        self.assertTrue(done.truncated)
        self.assertEqual(len(done.stdout), 50_000)

    def test_unread_stdin_does_not_deadlock_the_caller(self):
        started = time.monotonic()
        done = runner.bounded_run([sys.executable, "-c", "import time; time.sleep(0.2)"],
                                  stdin=b"z" * 20_000_000, timeout=20)
        self.assertEqual(done.returncode, 0)
        self.assertLess(time.monotonic() - started, 10)

    def test_timeout_reports_and_reaps(self):
        done = runner.bounded_run([sys.executable, "-c", "import time; time.sleep(60)"], timeout=0.5)
        self.assertTrue(done.timed_out)
        self.assertLess(done.elapsed_ns, 5_000_000_000)


if __name__ == "__main__":
    unittest.main()
