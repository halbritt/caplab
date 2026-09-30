"""Hermetic tests for the real-Cairn adapter: a fake `cairn` binary and a fake lifecycle wrapper.

The adapter has no PostgreSQL code of its own. It runs Cairn's `scripts/trial-task-eval.sh --
COMMAND` (here a fake that creates a socket directory and removes it on exit) and the store
host, the real `python -m caplab.retrieval.cairn`, runs under it. These tests need no
PostgreSQL and no Cairn build. They inject the faults a healthy Cairn never produces (paging
stalls, discovery flipping mid-query, garbage output, hangs, a wrapper that leaks or ignores
SIGTERM) and check what the adapter records. The real-Cairn integration test is in
test_retrieval_cairn_real.py.
"""

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from pathlib import Path
from unittest import mock

from caplab.retrieval import cairn, contracts, runner
from tests.retrieval_support import (CORPUS, QUERIES, StubArtifacts, command_arm, make_fake_lifecycle,
                                     make_git_checkout, make_spec, read_invocations, wrapper_log, wrapper_roots,
                                     write_fake_cairn, write_retriever)

ROOT = Path(__file__).resolve().parents[1]
MANY = {"id": "q-many", "text": "the worker billing restart certificate ledger", "relevant_ids": ["n-restart"]}
TIES = [{"id": f"n-tie-{i:02d}", "body": "shared tie token"} for i in range(12)]  # Equal scores: only write time orders them.


class CairnCase(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)
        patch = mock.patch.dict(os.environ)
        patch.start()
        self.addCleanup(patch.stop)
        for name in (cairn.WRAPPER_ENV, "CAPLAB_RETRIEVAL_PG_BIN", "CAIRN_PG_BIN"):
            os.environ.pop(name, None)
        self.wrapper_text, self.wrapper_config, self.wrapper_runs = make_fake_lifecycle(self.tmp)
        self.checkout, self.head = make_git_checkout(self.tmp, wrapper=self.wrapper_text)
        self.fake = self.tmp / "fake"
        self.fake.mkdir()
        self.out = self.tmp / "run"
        self.adapters = []
        StubArtifacts.instances.clear()
        self.addCleanup(self.remove_leaked_stores)

    def remove_leaked_stores(self):
        """Remove only what this test's fake wrapper and adapters created, even when a test left them."""
        for root in wrapper_roots(self.wrapper_runs):
            shutil.rmtree(root, ignore_errors=True)
        for adapter in self.adapters:
            if adapter.root is not None:
                shutil.rmtree(adapter.root, ignore_errors=True)

    def binary(self, *, revision=None, **config):
        self.binary_path, self.log = write_fake_cairn(self.fake, revision or self.head, **config)
        return self.binary_path

    def wrapper_mode(self, mode):
        self.wrapper_config.write_text(json.dumps({"mode": mode}))

    def arm(self, arm_id="cairn", *, semantic_mode="off", worker=None, checkout=None):
        configuration = {"binary": str(self.binary_path), "checkout": str(checkout or self.checkout),
                         "semantic_mode": semantic_mode}
        if worker:
            configuration["semantic_worker"] = str(worker)
        return {"id": arm_id, "adapter": "cairn", "configuration": configuration}

    def adapter(self, arm, spec):
        adapter = cairn.CairnAdapter(arm, spec)
        self.adapters.append(adapter)
        return adapter

    def pinned_adapter(self, arm=None, **spec_kwargs):
        spec = contracts.validate_spec(make_spec([arm or self.arm()], **spec_kwargs))
        adapter = self.adapter(spec["arms"][0], spec)
        adapter.pin()
        return adapter

    def run_arms(self, arms, *, extra_adapters=None, **spec_kwargs):
        spec = make_spec(arms, **spec_kwargs)
        normalized = contracts.validate_spec(spec)
        adapters = {arm["id"]: self.adapter(arm, normalized) for arm in normalized["arms"] if arm["adapter"] == "cairn"}
        adapters.update(extra_adapters or {})
        result = runner.run_experiment(spec, self.out, artifacts_factory=StubArtifacts, adapters=adapters)
        return result["report"], StubArtifacts.instances[-1]

    def attempts(self, art, arm="cairn"):
        return [a for a in art.attempts if a["arm"] == arm]

    def worker(self):
        path = self.tmp / "worker"
        path.write_text("#!/bin/sh\n")
        path.chmod(0o755)
        return path

    def bystanders(self):
        """Two unrelated processes: one in this test's own process group, one in another session."""
        found = []
        for new_session in (False, True):
            proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)", f"cairn-bystander-{os.getpid()}"],
                                    start_new_session=new_session)
            self.addCleanup(lambda proc=proc: (proc.kill(), proc.wait()))
            found.append(proc)
        return found

    def assert_alive(self, processes):
        for proc in processes:
            self.assertIsNone(proc.poll(), f"unrelated process {proc.pid} was killed by cancellation")

    def interrupt_during_provisioning(self):
        """SIGINT this process once the host is inside `cairn migrate`, as Ctrl-C would."""
        stop = threading.Event()

        def watch():
            while not stop.is_set():
                if any(c["argv"] == ["migrate"] for c in read_invocations(self.log)):
                    os.kill(os.getpid(), signal.SIGINT)
                    return
                time.sleep(0.05)

        thread = threading.Thread(target=watch, daemon=True)
        thread.start()
        self.addCleanup(lambda: (stop.set(), thread.join(5)))

    def assert_released(self):
        """The wrapper's cluster directories and the adapters' store directories are gone."""
        for root in wrapper_roots(self.wrapper_runs):
            self.assertFalse(Path(root).exists(), f"wrapper cluster {root} was left behind")
        for adapter in self.adapters:
            if adapter.root is not None:
                self.assertFalse(adapter.root.exists(), f"store directory {adapter.root} was left behind")
        time.sleep(0.2)
        survivors = subprocess.run(["pgrep", "-f", str(self.fake / "cairn")], capture_output=True, text=True)
        self.assertNotEqual(survivors.returncode, 0, f"a cairn process was left running: {survivors.stdout}")

    def assert_wrapper_never_ran(self):
        self.assertFalse(self.wrapper_runs.exists())
        self.assertEqual([c["argv"] for c in read_invocations(self.log) if c["argv"] != ["version"]], [])


class PinTests(CairnCase):
    def test_the_pins_bind_the_binary_to_the_checkout_and_the_wrapper(self):
        self.binary()
        pins = self.pinned_adapter().pin()
        wrapper = self.checkout / cairn.WRAPPER
        self.assertEqual(pins["binary"]["vcs_revision"], self.head)
        self.assertEqual(pins["checkout"], {"path": str(self.checkout.resolve()), "head": self.head, "dirty": False})
        self.assertTrue(pins["binary"]["sha256"].startswith("sha256:"))
        self.assertEqual(pins["lifecycle_wrapper"], {"path": str(wrapper.resolve()), "sha256": runner.file_sha256(wrapper),
                                                     "from_environment": False})
        self.assertEqual(pins["semantic"], {"mode": "off", "worker": None})
        self.assertNotIn("postgres", pins)  # CAPLAB has no PostgreSQL of its own to pin.
        self.assert_wrapper_never_ran()  # Pinning creates no store.

    def test_each_identity_mismatch_refuses_the_run_before_any_store_exists(self):
        cases = {
            "binary built from another revision": dict(revision="0" * 40),
            "binary from a modified tree": dict(modified=True),
            "unstamped binary": dict(unstamped=True),
            "binary that does not say whether its tree was modified": dict(no_modified_flag=True),
        }
        for name, config in cases.items():
            with self.subTest(name):
                self.binary(**config)
                with self.assertRaises(runner.AdapterError) as caught:
                    self.pinned_adapter()
                self.assertEqual(caught.exception.code, "pin_mismatch")
        with self.subTest("checkout with uncommitted changes"):
            self.binary()
            (self.checkout / "README").write_text("edited\n")
            with self.assertRaises(runner.AdapterError) as caught:
                self.pinned_adapter()
            self.assertEqual(caught.exception.code, "pin_mismatch")
            self.assertIn("uncommitted", caught.exception.message)
        self.assert_wrapper_never_ran()

    def test_missing_inputs_are_unavailable_not_mismatched(self):
        self.binary()
        arm = self.arm()
        for what, configuration in (("binary", dict(arm["configuration"], binary=str(self.tmp / "nope"))),
                                    ("checkout", dict(arm["configuration"], checkout=str(self.tmp / "missing"))),
                                    ("worker", dict(arm["configuration"], semantic_worker=str(self.tmp / "no-worker")))):
            with self.subTest(what):
                spec = contracts.validate_spec(make_spec([dict(arm, configuration=configuration)]))
                with self.assertRaises(runner.AdapterError) as caught:
                    self.adapter(spec["arms"][0], spec).pin()
                self.assertEqual(caught.exception.code, "pin_unavailable")

    def test_a_checkout_without_the_wrapper_is_unavailable_unless_one_is_supplied(self):
        bare_dir = self.tmp / "bare"
        bare_dir.mkdir()
        bare, bare_head = make_git_checkout(bare_dir)
        self.binary(revision=bare_head)
        with self.assertRaises(runner.AdapterError) as caught:
            self.pinned_adapter(self.arm(checkout=bare))
        self.assertEqual(caught.exception.code, "pin_unavailable")
        self.assertIn(cairn.WRAPPER_ENV, caught.exception.message)

    def test_a_supplied_wrapper_is_pinned_and_marked_as_from_the_environment(self):
        bare_dir = self.tmp / "bare"
        bare_dir.mkdir()
        bare, bare_head = make_git_checkout(bare_dir)
        self.binary(revision=bare_head)
        supplied = self.tmp / "newer-wrapper.sh"
        supplied.write_text(self.wrapper_text)
        with mock.patch.dict(os.environ, {cairn.WRAPPER_ENV: str(supplied)}):
            pins = self.pinned_adapter(self.arm(checkout=bare)).pin()
        self.assertEqual(pins["lifecycle_wrapper"], {"path": str(supplied.resolve()),
                                                     "sha256": runner.file_sha256(supplied), "from_environment": True})

    def test_a_pin_that_moves_after_the_plan_is_sealed_is_refused_at_open(self):
        self.binary()
        with self.subTest("binary"):
            adapter = self.pinned_adapter()
            with self.binary_path.open("a") as handle:
                handle.write("\n# changed after the plan was sealed\n")
            with self.assertRaises(runner.AdapterError) as caught:
                adapter.open()
            self.assertEqual(caught.exception.code, "pin_changed")
        with self.subTest("wrapper in the checkout"):
            self.binary()
            adapter = self.pinned_adapter()
            with (self.checkout / cairn.WRAPPER).open("a") as handle:
                handle.write("\n# changed after the plan was sealed\n")
            with self.assertRaises(runner.AdapterError) as caught:
                adapter.open()
            self.assertEqual(caught.exception.code, "pin_changed")
            subprocess.run(["git", "-C", str(self.checkout), "checkout", "--quiet", "--", cairn.WRAPPER], check=True)
        with self.subTest("checkout commit"):
            adapter = self.pinned_adapter()
            subprocess.run(["git", "-C", str(self.checkout), "-c", "user.name=t", "-c", "user.email=t@t", "commit",
                            "--quiet", "--allow-empty", "-m", "moved"], check=True)
            with self.assertRaises(runner.AdapterError) as caught:
                adapter.open()
            self.assertEqual(caught.exception.code, "pin_changed")
        self.assert_wrapper_never_ran()
        self.assertTrue(all(adapter.root is None for adapter in self.adapters))

    def test_a_semantic_worker_that_changes_after_the_seal_is_refused_at_open(self):
        self.binary()
        worker = self.worker()
        adapter = self.pinned_adapter(self.arm(semantic_mode="on", worker=worker))
        worker.write_text("#!/bin/sh\n# another worker, swapped in after the plan was sealed\n")
        with self.assertRaises(runner.AdapterError) as caught:
            adapter.open()
        self.assertEqual(caught.exception.code, "pin_changed")
        self.assertIn("semantic worker", caught.exception.message)
        self.assert_wrapper_never_ran()

    def test_a_supplied_wrapper_that_changes_after_the_seal_is_refused(self):
        self.binary()
        supplied = self.tmp / "newer-wrapper.sh"
        supplied.write_text(self.wrapper_text)
        with mock.patch.dict(os.environ, {cairn.WRAPPER_ENV: str(supplied)}):
            adapter = self.pinned_adapter()
        supplied.write_text(self.wrapper_text + "\n# swapped\n")
        with self.assertRaises(runner.AdapterError) as caught:
            adapter.open()
        self.assertEqual(caught.exception.code, "pin_changed")
        self.assert_wrapper_never_ran()

    def test_a_modified_checkout_fails_the_whole_run_before_anything_is_written(self):
        self.binary()
        (self.checkout / "README").write_text("edited\n")
        with self.assertRaises(runner.AdapterError) as caught:
            self.run_arms([self.arm()])
        self.assertEqual(caught.exception.code, "pin_mismatch")
        self.assertFalse(self.out.exists())


class MeasurementTests(CairnCase):
    def test_actual_rank_availability_and_latency_are_recorded_against_the_controls(self):
        self.binary()
        report, art = self.run_arms([self.arm()], seeds=(0, 1), cutoffs=(1, 3))
        by_query = {a["query_id"]: a for a in self.attempts(art) if a["seed"] == 0}
        self.assertEqual(by_query["q-restart"]["ranked_ids"][0], "n-restart")
        self.assertEqual(by_query["q-backup"]["ranked_ids"][0], "n-backup")
        # Access and supersession controls: never delivered by the store, whatever their text says.
        every_ranked = {i for a in self.attempts(art) for i in a["ranked_ids"]}
        self.assertFalse(every_ranked & {"n-local", "n-other", "n-cert-old"})
        attempt = by_query["q-restart"]
        self.assertEqual(attempt["status"], "ok")
        self.assertIsNone(attempt["delivered_ids"])  # Previews only; delivery is never inferred from rank.
        self.assertGreater(attempt["latency_ns"], 0)
        observation = attempt["observation"]
        self.assertEqual((observation["adapter"], observation["seed_applied"]), ("cairn", False))
        self.assertEqual(observation["rankings"], ["binary-idf-scope-recency/1"])
        self.assertEqual(observation["semantic"], {"requested": False, "worker_configured": False, "state": None,
                                                   "fallback": None, "discovery": None})
        self.assertGreater(observation["response_bytes"], 0)
        coverage = report["summary"]["arms"]["cairn"]["coverage"]
        self.assertEqual((coverage["planned"], coverage["scorable"], coverage["failures"]), (8, 8, 0))
        folder = self.out / "raw" / "cairn__q-restart__0"
        self.assertTrue((folder / "search-page-001.json").is_file())
        self.assert_released()

    def test_labels_never_reach_the_store(self):
        self.binary()
        self.run_arms([self.arm()], queries=QUERIES[:1])
        seen = json.dumps(read_invocations(self.log))
        for label in ("relevant_ids", "forbidden_ids", "stratum", "n-restart"):
            self.assertNotIn(label, seen)  # Note IDs are CAPLAB's names; the store sees only request IDs.

    def test_one_seeding_procedure_serves_every_arm_and_keeps_the_controls(self):
        self.binary()
        self.run_arms([self.arm("arm-a"), self.arm("arm-b")])
        stores = {}
        for call in read_invocations(self.log):
            argv = call["argv"]
            if argv[0] in ("remember", "preview-retract", "supersede"):
                store = stores.setdefault(call["env"]["CAIRN_HOME"], {"remember": [], "preview-retract": 0, "supersede": 0})
                if argv[0] == "remember":
                    store["remember"].append((argv[argv.index("--request-id") + 1], "--shareable" in argv,
                                              argv[argv.index("--repo") + 1], argv[argv.index("--kind") + 1]))
                else:
                    store[argv[0]] += 1
        self.assertEqual(len(stores), 2)  # One disposable store per arm.
        first, second = stores.values()
        self.assertEqual(sorted(first["remember"]), sorted(second["remember"]))  # Identical for every arm.
        self.assertEqual(len(first["remember"]), len(CORPUS))
        self.assertEqual(len({item[0] for item in first["remember"]}), len(CORPUS))
        self.assertEqual(sum(not item[1] for item in first["remember"]), 1)  # Only the local-only control is withheld.
        self.assertEqual(sum(item[2] == "other-collection" for item in first["remember"]), 1)
        self.assertEqual((first["preview-retract"], first["supersede"]), (1, 1))
        self.assertEqual((second["preview-retract"], second["supersede"]), (1, 1))

    def test_equal_scoring_notes_rank_identically_for_every_arm_because_seeding_is_sequential(self):
        # Cairn breaks score ties by write time (newest first). Concurrent inserts would let completion
        # order decide; the jitter in the fake makes that visible. Sequential, corpus-order seeding puts
        # the last note in the corpus first, for every arm and every run.
        self.binary(remember_jitter=0.12)
        queries = [{"id": "q-tie", "text": "shared tie token", "relevant_ids": ["n-tie-00"]}]
        _, art = self.run_arms([self.arm("arm-a"), self.arm("arm-b")], corpus=TIES, queries=queries, cutoffs=(12,))
        expected = [note["id"] for note in reversed(TIES)]
        for arm in ("arm-a", "arm-b"):
            self.assertEqual(self.attempts(art, arm)[0]["ranked_ids"], expected, arm)

    def test_the_seeding_policy_and_order_are_provenance(self):
        self.binary()
        _, art = self.run_arms([self.arm()], queries=QUERIES[:1])
        seeding = art.provenance["arms"]["cairn"]["seeding"]
        ids = [note["id"] for note in CORPUS]
        self.assertEqual(seeding, {"policy": cairn.SEED_POLICY, "notes": len(CORPUS),
                                   "note_order_sha256": "sha256:" + hashlib.sha256(contracts.canonical_json(ids)).hexdigest()})
        retained = json.loads(art.registered["arm.cairn.seeding.json"])
        self.assertEqual([entry["note_id"] for entry in retained["order"]], ids)  # The order actually used.
        self.assertEqual(len({entry["record_id"] for entry in retained["order"]}), len(ids))
        remembers = [c for c in read_invocations(self.log) if c["argv"][0] == "remember"]
        order = [c["argv"][c["argv"].index("--request-id") + 1] for c in remembers]
        self.assertEqual(len(order), len(CORPUS))
        self.assertEqual(order, sorted(order, key=order.index))  # One call per note, none repeated.

    def test_paging_reaches_the_requested_depth_and_stops_there(self):
        self.binary(search={"page_size": 2})
        _, art = self.run_arms([self.arm()], cutoffs=(1, 3), queries=[MANY])
        attempt = self.attempts(art)[0]
        self.assertEqual(attempt["status"], "ok")
        self.assertEqual(len(attempt["ranked_ids"]), 3)
        self.assertEqual(attempt["observation"]["pages"], 2)  # The third page was never requested.
        self.assertEqual(attempt["observation"]["depth_returned"], 4)  # Whole pages are read; results are cut at the depth.
        self.assertFalse(attempt["observation"]["exhausted"])

    def test_a_short_result_reports_that_the_result_set_was_exhausted(self):
        self.binary()
        _, art = self.run_arms([self.arm()], cutoffs=(1, 50))
        self.assertTrue(all(a["observation"]["exhausted"] for a in self.attempts(art)))

    def test_the_postgres_binaries_chosen_for_the_run_reach_the_wrapper(self):
        self.binary()
        with mock.patch.dict(os.environ, {"CAPLAB_RETRIEVAL_PG_BIN": "/opt/pg16/bin"}):
            self.run_arms([self.arm()], queries=QUERIES[:1])
        self.assertEqual(wrapper_log(self.wrapper_runs, "pgbin"), ["/opt/pg16/bin"])


class SemanticDiscoveryTests(CairnCase):
    def ranked_observation(self, **kwargs):
        _, art = self.run_arms([self.arm(**kwargs)], queries=QUERIES[:1])
        return self.attempts(art)[0]["observation"]

    def test_semantic_requested_without_a_worker_records_labelled_fallback(self):
        self.binary()
        observation = self.ranked_observation(semantic_mode="on")
        semantic = observation["semantic"]
        self.assertEqual((semantic["requested"], semantic["state"], semantic["fallback"]), (True, "unavailable", True))
        self.assertEqual(observation["rankings"], ["lexical-scope-recency/4"])  # The fallback ranker differs.
        self.assertEqual(observation["status"], ["DEGRADED_NO_EMBEDDINGS"])
        self.assertIn("--semantic", [a for c in read_invocations(self.log) for a in c["argv"]])

    def test_a_ready_worker_is_recorded_with_its_identity_and_no_fallback(self):
        self.binary(search={"semantic_state": "ready"})
        observation = self.ranked_observation(semantic_mode="on", worker=self.worker())
        semantic = observation["semantic"]
        self.assertEqual((semantic["state"], semantic["fallback"], semantic["worker_configured"]), ("ready", False, True))
        self.assertEqual(semantic["discovery"]["algorithm"], "fake-embed/1")
        serve = next(c for c in read_invocations(self.log) if c["argv"][0] == "serve")
        self.assertIn("--semantic-stream-command", serve["argv"])

    def test_off_with_a_worker_keeps_discovery_off(self):
        self.binary()
        observation = self.ranked_observation(semantic_mode="off", worker=self.worker())
        self.assertEqual(observation["semantic"]["requested"], False)
        self.assertTrue(observation["semantic"]["worker_configured"])
        self.assertNotIn("--semantic", [a for c in read_invocations(self.log) for a in c["argv"]])

    def test_the_readiness_observed_before_any_assignment_is_kept_as_evidence(self):
        self.binary()
        _, art = self.run_arms([self.arm(semantic_mode="on")], queries=QUERIES[:1])
        readiness = art.registered["arm.cairn.readiness.json"]
        self.assertIn(b'"state":"unavailable"', readiness)
        self.assertEqual(json.loads(readiness)["postgres"], "pg_ctl (PostgreSQL) 99.0")
        self.assertEqual(art.registered["arm.cairn.postgres.log"], b"fake postgres log\n")
        self.assertIn(b"fake api listening", art.registered["arm.cairn.api.log"])

    def test_discovery_changing_between_pages_is_a_classified_failure(self):
        self.binary(search={"page_size": 2, "semantic_state": "ready", "flip_state_on_offset": 2})
        _, art = self.run_arms([self.arm(semantic_mode="on", worker=self.worker())], cutoffs=(5,), queries=[MANY])
        attempt = self.attempts(art)[0]
        self.assertEqual((attempt["status"], attempt["error"]["code"]), ("error", "discovery_changed"))
        self.assertEqual(attempt["ranked_ids"], [])  # Incomparable pages are not stitched into a ranking.
        self.assertEqual(attempt["error"]["states"], ["ready", "unavailable"])


class SearchFailureTests(CairnCase):
    def failing(self, **search):
        self.binary(search=search)
        _, art = self.run_arms([self.arm()], queries=QUERIES[:1], timeout_seconds=1 if search.get("sleep") else 10)
        return self.attempts(art)[0], art

    def test_a_refusal_is_a_classified_failure_with_cairns_own_status(self):
        attempt, _ = self.failing(error=True)
        self.assertEqual((attempt["status"], attempt["error"]["code"]), ("error", "search_failed"))
        self.assertEqual(attempt["error"]["cairn_status"], "INVALID_REQUEST")
        self.assertEqual(attempt["ranked_ids"], [])

    def test_garbage_output_is_malformed_and_its_bytes_are_kept(self):
        attempt, _ = self.failing(garbage=True)
        self.assertEqual(attempt["error"]["code"], "malformed_response")
        self.assertEqual((self.out / "raw" / "cairn__q-restart__0" / "search-page-001.json").read_bytes(),
                         b"not json at all\n")

    def test_an_unseeded_record_is_refused_not_guessed(self):
        attempt, _ = self.failing(unknown_record=True)
        self.assertEqual(attempt["error"]["code"], "unknown_record")

    def test_a_stalled_cursor_does_not_loop_forever(self):
        self.binary(search={"page_size": 1, "stall": True})
        _, art = self.run_arms([self.arm()], cutoffs=(5,), queries=[MANY])
        self.assertEqual(self.attempts(art)[0]["error"]["code"], "paging_stalled")

    def test_a_hung_search_times_out_within_the_budget(self):
        started = time.monotonic()
        attempt, _ = self.failing(sleep=30)
        self.assertLess(time.monotonic() - started, 20)
        self.assertEqual((attempt["status"], attempt["error"]["code"]), ("timeout", "timeout"))
        self.assert_released()


class StoreFailureTests(CairnCase):
    """A store that cannot be built fails only its arm; nothing it created is left behind."""

    def run_with_fixture_arm(self):
        scripts = self.tmp / "scripts"
        scripts.mkdir(exist_ok=True)
        good = command_arm("good", write_retriever(scripts, "good"))
        report, art = self.run_arms([self.arm(), good], queries=QUERIES[:2])
        return report, art

    def assert_arm_unavailable(self, art, cause):
        cairn_attempts = self.attempts(art)
        self.assertEqual({(a["status"], a["error"]["code"], a["error"]["cause"]) for a in cairn_attempts},
                         {("error", "adapter_unavailable", cause)})
        self.assertEqual({a["status"] for a in self.attempts(art, "good")}, {"ok"})  # Other arms are unaffected.
        self.assert_released()
        return cairn_attempts[0]["error"]

    def test_a_failed_migration_is_a_classified_store_failure(self):
        self.binary(migrate_fail=True)
        report, art = self.run_with_fixture_arm()
        error = self.assert_arm_unavailable(art, "store_failed")
        self.assertIn("migrate", error["message"])
        self.assertEqual(report["summary"]["arms"]["cairn"]["coverage"]["scorable"], 0)

    def test_a_failed_createdb_reports_the_tool_output(self):
        self.binary()
        (self.tmp / "pgbin" / "createdb-fails").write_text("")
        _, art = self.run_with_fixture_arm()
        error = self.assert_arm_unavailable(art, "store_failed")
        self.assertIn("fake failure", error["stderr_tail"])

    def test_an_api_that_never_starts_is_reported_with_its_log(self):
        self.binary(serve_fail=True)
        _, art = self.run_with_fixture_arm()
        error = self.assert_arm_unavailable(art, "api_unavailable")
        self.assertIn("cannot listen", error["log_tail"])

    def test_an_api_that_answers_with_prose_is_not_ready(self):
        self.binary(search={"probe_garbage": True})
        _, art = self.run_with_fixture_arm()
        self.assert_arm_unavailable(art, "api_unavailable")

    def test_a_store_that_fails_to_build_and_leaks_its_cluster_leaves_the_run_unfinished(self):
        # open() failed, so the runner never calls close(); the leak still has to surface.
        self.binary(migrate_fail=True)
        self.wrapper_mode("leak_cluster")
        with self.assertRaises(runner.RunnerCleanupError) as caught:
            self.run_with_fixture_arm()
        art = StubArtifacts.instances[-1]
        self.assertIn(wrapper_roots(self.wrapper_runs)[0], caught.exception.failures["cairn"])
        self.assertFalse(art.finished)
        self.assertEqual({(a["status"], a["error"]["cause"]) for a in self.attempts(art)}, {("error", "store_failed")})
        self.assertEqual({a["status"] for a in self.attempts(art, "good")}, {"ok"})  # Other arms still ran.
        self.assertIn(b"still exists", art.registered["arm.cairn.close-error.txt"])

    def test_a_checkout_whose_wrapper_has_no_command_mode_says_so(self):
        self.binary()
        self.wrapper_mode("old")
        _, art = self.run_with_fixture_arm()
        error = self.assert_arm_unavailable(art, "host_failed")
        self.assertIn("trial-task-eval.sh -- COMMAND", error["message"])
        self.assertIn(cairn.WRAPPER_ENV, error["message"])
        self.assertIn("invalid choice", error["stderr_tail"])  # The wrapper's own complaint is kept.
        self.assertEqual(wrapper_roots(self.wrapper_runs), [])  # It refused before creating a cluster.

    def test_a_checkout_without_command_mode_runs_with_a_supplied_newer_wrapper(self):
        bare_dir = self.tmp / "bare"
        bare_dir.mkdir()
        bare, bare_head = make_git_checkout(bare_dir)
        self.binary(revision=bare_head)
        supplied = self.tmp / "newer-wrapper.sh"
        supplied.write_text(self.wrapper_text)
        with mock.patch.dict(os.environ, {cairn.WRAPPER_ENV: str(supplied)}):
            _, art = self.run_arms([self.arm(checkout=bare)], queries=QUERIES[:2])
        self.assertEqual({a["status"] for a in self.attempts(art)}, {"ok"})
        self.assertTrue(art.provenance["arms"]["cairn"]["lifecycle_wrapper"]["from_environment"])
        self.assert_released()


class CleanupFailureTests(CairnCase):
    """A store that cannot be fully released must not yield a complete run."""

    def test_a_leaked_cluster_leaves_the_run_unfinished_with_the_evidence_and_the_results(self):
        self.binary()
        self.wrapper_mode("leak_cluster")
        with self.assertRaises(runner.RunnerCleanupError) as caught:
            self.run_arms([self.arm()], queries=QUERIES[:2])
        art = StubArtifacts.instances[-1]
        self.assertIn("still exists", caught.exception.failures["cairn"])
        self.assertIn(wrapper_roots(self.wrapper_runs)[0], caught.exception.failures["cairn"])
        self.assertFalse(art.finished)
        self.assertFalse((self.out / "report.json").exists())
        self.assertEqual([a["status"] for a in art.attempts], ["ok", "ok"])  # What was measured is intact.
        self.assertIn(b"still exists", art.registered["arm.cairn.close-error.txt"])
        for name in ("api.log", "postgres.log", "readiness.json"):
            self.assertTrue(art.registered[f"arm.cairn.{name}"], name)
        self.assertFalse(self.adapters[0].root.exists())  # CAPLAB's own directory is still removed.

    def test_a_wrapper_that_reports_its_own_cleanup_failure_fails_the_run(self):
        # Cairn's wrapper exits nonzero when it could not stop or remove its cluster; the host itself exited 0.
        self.binary()
        self.wrapper_mode("cleanup_status")
        with self.assertRaises(runner.RunnerCleanupError) as caught:
            self.run_arms([self.arm()], queries=QUERIES[:2])
        art = StubArtifacts.instances[-1]
        message = caught.exception.failures["cairn"]
        self.assertIn("exited with status 1 after a clean stop", message)
        self.assertIn("cleanup failed: fake wrapper status", message)
        self.assertFalse(art.finished)
        self.assertEqual([a["status"] for a in art.attempts], ["ok", "ok"])  # The measurements are not altered.
        self.assertIn(b"cleanup failed: fake wrapper status", art.registered["arm.cairn.host.stderr"])
        self.assert_released()  # The fake removed the cluster; the failure is the reported status.

    def test_a_wrapper_that_ignores_sigterm_is_killed_and_reported(self):
        self.binary()
        self.wrapper_mode("stubborn")
        bystanders = self.bystanders()
        with mock.patch.object(cairn, "HOST_EXIT_TIMEOUT", 1), mock.patch.object(cairn, "HOST_TERM_TIMEOUT", 1):
            started = time.monotonic()
            with self.assertRaises(runner.RunnerCleanupError) as caught:
                self.run_arms([self.arm()], queries=QUERIES[:1])
            self.assertLess(time.monotonic() - started, 30)
        message = caught.exception.failures["cairn"]
        self.assertIn("did not exit within 1 seconds of stdin closing", message)
        self.assertIn("did not exit within 1 seconds of SIGTERM; killed", message)
        self.assertFalse(StubArtifacts.instances[-1].finished)
        time.sleep(0.3)
        survivors = subprocess.run(["pgrep", "-f", str(self.checkout / cairn.WRAPPER)], capture_output=True)
        self.assertNotEqual(survivors.returncode, 0, "the wrapper survived SIGKILL")
        self.assert_alive(bystanders)  # Escalation reached only the wrapper's own group.

    def test_an_interruption_during_provisioning_with_a_leak_is_not_hidden(self):
        self.binary(migrate_sleep=30)
        self.wrapper_mode("leak_cluster")
        spec = contracts.validate_spec(make_spec([self.arm()], queries=QUERIES[:2]))
        adapter = self.adapter(spec["arms"][0], spec)
        self.interrupt_during_provisioning()
        with self.assertRaises(runner.RunnerCleanupError) as caught:
            runner.run_experiment(make_spec([self.arm()], queries=QUERIES[:2]), self.out,
                                  artifacts_factory=StubArtifacts, adapters={"cairn": adapter})
        art = StubArtifacts.instances[-1]
        self.assertEqual([a["status"] for a in art.attempts], ["not_started", "not_started"])  # The interruption stands.
        self.assertIn(wrapper_roots(self.wrapper_runs)[0], caught.exception.failures["cairn"])
        self.assertFalse(art.finished)
        self.assertIsNone(adapter.host)  # The host was stopped on the way out.
        self.assertFalse(adapter.root.exists())  # CAPLAB's own directory is still removed.

    def test_a_clean_interruption_during_provisioning_reports_no_leftovers(self):
        self.binary(migrate_sleep=30)
        spec = contracts.validate_spec(make_spec([self.arm()], queries=QUERIES[:2]))
        adapter = self.adapter(spec["arms"][0], spec)
        self.interrupt_during_provisioning()
        result = runner.run_experiment(make_spec([self.arm()], queries=QUERIES[:2]), self.out,
                                       artifacts_factory=StubArtifacts, adapters={"cairn": adapter})
        self.assertEqual([a["status"] for a in StubArtifacts.instances[-1].attempts], ["not_started", "not_started"])
        self.assertEqual(adapter.unreleased(), [])
        self.assertEqual(result["status"], "completed_with_failures")
        self.assert_released()


class IsolationTests(CairnCase):
    PRODUCTION = {"CAIRN_DATABASE_URL": "host=/var/run/postgresql dbname=cairn", "CAIRN_HOME": "/srv/production-cairn-home",
                  "CAIRN_TEST_DATABASE_URL": "host=/prod", "ANTHROPIC_API_KEY": "sk-secret",
                  "CAIRN_TASK_EVAL_PG": "/var/run/postgresql"}

    def test_the_environment_is_rebuilt_and_names_only_the_stores_own_paths(self):
        self.binary()
        with mock.patch.dict(os.environ, self.PRODUCTION):
            self.run_arms([self.arm()], queries=QUERIES[:1])
        cluster = wrapper_roots(self.wrapper_runs)[0]
        calls = read_invocations(self.log)
        pinning = [call for call in calls if call["argv"] == ["version"]]
        self.assertEqual(len(pinning), 1)  # The pin-time identity read runs before any store exists.
        self.assertFalse([k for k in pinning[0]["env"] if k.startswith("CAIRN_") or "KEY" in k])
        seen = 0
        for call in calls:
            env, argv = call["env"], call["argv"]
            everything = json.dumps(env)
            for value in ("/srv/production-cairn-home", "/var/run/postgresql", "sk-secret", "host=/prod"):
                self.assertNotIn(value, everything, f"{argv[0]}: production value {value} reached the environment")
            for name in ("CAIRN_TEST_DATABASE_URL", "ANTHROPIC_API_KEY"):
                self.assertNotIn(name, env)
            if call in pinning:
                continue
            seen += 1
            self.assertTrue(env["CAIRN_HOME"].startswith("/tmp/caplab-rtv-"), env["CAIRN_HOME"])
            self.assertTrue(env["HOME"].startswith("/tmp/caplab-rtv-"))
            if argv[0] == "agent":
                # Measurement runs with no database access at all.
                self.assertNotIn("CAIRN_DATABASE_URL", env)
                self.assertNotIn("CAIRN_TASK_EVAL_PG", env)
                self.assertTrue(argv[argv.index("--socket") + 1].startswith("/tmp/caplab-rtv-"))
                self.assertTrue(argv[argv.index("--token-file") + 1].startswith("/tmp/caplab-rtv-"))
            else:
                self.assertEqual(env["CAIRN_DATABASE_URL"], f"host={cluster}/socket dbname=caplab_retrieval sslmode=disable")
        self.assertGreater(seen, 10)
        # The wrapper and the host were started from a rebuilt environment too.
        wrapper_env = "\n".join(wrapper_log(self.wrapper_runs, "env"))
        for value in ("/srv/production-cairn-home", "/var/run/postgresql", "sk-secret", "ANTHROPIC_API_KEY",
                      "CAIRN_DATABASE_URL", "CAIRN_TEST_DATABASE_URL"):
            self.assertNotIn(value, wrapper_env)

    def test_a_database_outside_the_wrappers_cluster_is_refused(self):
        self.binary()
        root = Path(tempfile.mkdtemp(prefix=cairn.ROOT_PREFIX, dir="/tmp"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        cluster = types.SimpleNamespace(socket=Path("/tmp/cairn-task-eval-pg.fake/socket"),
                                        create_database=lambda name: "host=/var/run/postgresql dbname=cairn_production")
        store = cairn.CairnStore(self.binary_path, collection="c", label="x", worker=None, root=root, cluster=cluster)
        with self.assertRaises(runner.AdapterError) as caught:
            store.provision([])
        self.assertEqual(caught.exception.code, "store_unsafe")
        self.assertEqual(read_invocations(self.log), [])  # No Cairn command ran against it.

    def test_a_store_outside_the_adapters_temporary_directory_is_refused(self):
        self.binary()
        cluster = types.SimpleNamespace(socket=Path("/tmp/cairn-task-eval-pg.fake/socket"),
                                        create_database=lambda name: "host=/tmp/cairn-task-eval-pg.fake/socket dbname=x")
        store = cairn.CairnStore(self.binary_path, collection="c", label="x", worker=None, root=self.tmp, cluster=cluster)
        store.home.mkdir()
        with self.assertRaises(runner.AdapterError) as caught:
            store._build_env("host=/tmp/cairn-task-eval-pg.fake/socket dbname=x")
        self.assertEqual(caught.exception.code, "store_unsafe")

    def test_the_store_host_refuses_to_run_outside_the_wrapper(self):
        for label, environ in (("no cluster", {}), ("production socket", {"CAIRN_TASK_EVAL_PG": "/var/run/postgresql",
                                                                         "CAIRN_TASK_EVAL_PG_BIN": "/usr/bin"}),
                               ("cluster that does not exist", {"CAIRN_TASK_EVAL_PG": "/tmp/cairn-task-eval-pg.nope/socket",
                                                                "CAIRN_TASK_EVAL_PG_BIN": "/usr/bin"})):
            with self.subTest(label):
                with self.assertRaises(runner.AdapterError) as caught:
                    cairn.ExternalCluster(environ)
                self.assertEqual(caught.exception.code, "store_unsafe")

    def test_the_host_process_reports_a_refusal_as_one_protocol_line(self):
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
        for name in ("CAIRN_TASK_EVAL_PG", "CAIRN_TASK_EVAL_PG_BIN"):
            env.pop(name, None)
        done = subprocess.run([sys.executable, "-m", "caplab.retrieval.cairn"], input="{}\n", capture_output=True,
                              text=True, env=env, cwd=self.tmp, timeout=60)
        self.assertEqual(done.returncode, 1)
        self.assertEqual(json.loads(done.stdout)["error"]["code"], "store_unsafe")

    def test_the_host_refuses_a_store_root_it_was_not_given_by_the_adapter(self):
        cluster = Path(tempfile.mkdtemp(prefix="cairn-task-eval-pg.", dir="/tmp"))
        self.addCleanup(shutil.rmtree, cluster, ignore_errors=True)
        (cluster / "socket").mkdir()
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), CAIRN_TASK_EVAL_PG=str(cluster / "socket"),
                   CAIRN_TASK_EVAL_PG_BIN="/usr/bin")
        request = {"binary": "/bin/true", "collection": "c", "label": "x", "worker": None, "root": str(self.tmp),
                   "corpus": []}
        done = subprocess.run([sys.executable, "-m", "caplab.retrieval.cairn"], input=json.dumps(request) + "\n",
                              capture_output=True, text=True, env=env, cwd=self.tmp, timeout=60)
        self.assertEqual(done.returncode, 1)
        messages = [json.loads(line) for line in done.stdout.splitlines()]
        self.assertEqual(messages[-1]["error"]["code"], "store_unsafe")  # After the cluster line, nothing is provisioned.
        self.assertFalse(any("ready" in message for message in messages))

    def test_an_exception_while_the_host_cleans_up_is_a_nonzero_exit_not_a_silent_success(self):
        self.binary()
        cluster = Path(tempfile.mkdtemp(prefix="cairn-task-eval-pg.", dir="/tmp"))
        root = Path(tempfile.mkdtemp(prefix=cairn.ROOT_PREFIX, dir="/tmp"))
        self.addCleanup(shutil.rmtree, cluster, ignore_errors=True)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self.addCleanup(subprocess.run, ["pkill", "-f", f"{self.fake}/cairn serve"])  # The fake API it never stopped.
        (cluster / "socket").mkdir()
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), CAIRN_TASK_EVAL_PG=str(cluster / "socket"),
                   CAIRN_TASK_EVAL_PG_BIN=str(self.tmp / "pgbin"))
        code = ("import sys; from caplab.retrieval import cairn\n"
                "def boom(self): raise RuntimeError('stop exploded')\n"
                "cairn.CairnStore.stop = boom\nsys.exit(cairn.host_main())")
        request = {"binary": str(self.binary_path), "collection": "c", "label": "x", "worker": None, "root": str(root),
                   "corpus": CORPUS[:2]}
        with subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=env, cwd=self.tmp, text=True) as host:
            host.stdin.write(json.dumps(request) + "\n")
            host.stdin.flush()
            first = json.loads(host.stdout.readline())
            self.assertEqual(set(first), {"cluster"})  # The wrapper's cluster is reported before provisioning.
            self.assertIn("ready", json.loads(host.stdout.readline()))
            host.stdin.close()  # The adapter's clean stop.
            host.wait(timeout=60)
            stdout, stderr = host.stdout.read(), host.stderr.read()
        self.assertNotEqual(host.returncode, 0)
        self.assertIn("stop exploded", stderr)
        self.assertNotIn("closed", stdout)  # The host never claims a clean close it did not make.

    def test_the_store_is_torn_down_after_an_interruption(self):
        self.binary()
        spec = contracts.validate_spec(make_spec([self.arm()], queries=QUERIES[:3]))
        adapter = self.adapter(spec["arms"][0], spec)
        original = adapter.retrieve
        calls = []

        def interrupted(query, seed, cutoff, timeout):
            calls.append(query["id"])
            if len(calls) == 2:
                raise KeyboardInterrupt
            return original(query, seed, cutoff, timeout)

        adapter.retrieve = interrupted
        bystanders = self.bystanders()
        result = runner.run_experiment(spec, self.out, artifacts_factory=StubArtifacts, adapters={"cairn": adapter})
        self.assert_alive(bystanders)
        statuses = [a["status"] for a in StubArtifacts.instances[-1].attempts]
        self.assertEqual(statuses, ["ok", "interrupted", "not_started"])
        self.assert_released()
        self.assertEqual(result["report"]["summary"]["arms"]["cairn"]["coverage"]["not_started"], 1)

    def test_a_real_sigterm_during_provisioning_leaves_evidence_and_nothing_running(self):
        self.binary(migrate_sleep=60)
        code = """
import json, sys
from pathlib import Path
from caplab.retrieval import runner
from tests.retrieval_support import StubArtifacts, make_spec
arm = dict(id="cairn", adapter="cairn", configuration=json.loads(sys.argv[1]))
result = runner.run_experiment(make_spec([arm]), Path(sys.argv[2]), artifacts_factory=StubArtifacts)
print("finished", result["report"]["summary"]["arms"]["cairn"]["coverage"]["by_status"])
"""
        configuration = self.arm()["configuration"]
        bystanders = self.bystanders()
        out = self.tmp / "sigterm-run"
        env = dict(os.environ, PYTHONPATH=f"{ROOT / 'src'}:{ROOT}")
        proc = subprocess.Popen([sys.executable, "-c", code, json.dumps(configuration), str(out)], cwd=ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline and not any(c["argv"] == ["migrate"] for c in read_invocations(self.log)):
                time.sleep(0.05)  # The host is now inside provisioning, with a migration running.
            self.assertTrue(any(c["argv"] == ["migrate"] for c in read_invocations(self.log)))
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=90)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()
        self.assertEqual(proc.returncode, 0, stderr)
        attempts = [json.loads(line) for line in (out / "attempts.jsonl").read_text().splitlines()]
        self.assertEqual(len(attempts), len(QUERIES))
        self.assertEqual({a["status"] for a in attempts}, {"not_started"})  # Interrupted before any assignment ran.
        self.assert_alive(bystanders)
        self.assertTrue((out / "report.json").is_file())
        self.assertIn("'not_started': 4", stdout)
        for root in wrapper_roots(self.wrapper_runs):
            self.assertFalse(Path(root).exists())
        # The store directory of the run that was interrupted (named by the migration's own environment) is gone.
        homes = {c["env"]["CAIRN_HOME"] for c in read_invocations(self.log) if c["argv"] == ["migrate"]}
        self.assertEqual(len(homes), 1)
        self.assertFalse(Path(homes.pop()).parent.exists())
        time.sleep(0.3)
        survivors = subprocess.run(["pgrep", "-f", str(self.fake / "cairn")], capture_output=True)
        self.assertNotEqual(survivors.returncode, 0, "a fake cairn process survived the interruption")


if __name__ == "__main__":
    unittest.main()
