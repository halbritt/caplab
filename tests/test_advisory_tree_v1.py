"""tree-v1 (plan rev 2): contract v3 rendering, hash_mismatch v3, and the
runner's per-case materialization and scorability gate."""
import json
import os
import random
import subprocess
import tempfile
import unittest
from unittest import mock

from caplab.advisory import calibrate as C
from caplab.advisory import materialize as M
from caplab.advisory import operators as O
from caplab.advisory import pool_runner
from caplab.advisory.instrument_defects import NotApplicable

CHANGE_SET = {
    "schema_version": 2,
    "packet": {"work_graph_identity": "wg", "work_graph_version_hash": "a" * 64,
               "packet_anchor": "P1", "packet_element_hash": "b" * 64},
    "base_composition": {"observed_product": {"identity": "id", "version_seq": 1, "content_hash": "c" * 64},
                         "ancestors": [], "resulting_base_hash": "d" * 64},
    "files": {"docs/x.md": "hello " + "e" * 64},
    "deletes": [],
    "result_tree_hash": "f" * 64,
}


class PreambleV3Test(unittest.TestCase):
    def test_statement_per_base_class(self):
        ws = "/tmp/ws/case"
        whole = C.pinned_set_statement("whole-tree", {"file_count": 12, "evidence": []}, ws)
        self.assertIn("whole repository tree", whole)
        self.assertIn("12 files", whole)
        partial = C.pinned_set_statement("partial-product-tree", {"file_count": 3, "evidence": []}, ws)
        self.assertIn("not a finding", partial)
        none = C.pinned_set_statement("none-by-design", {"file_count": 0, "evidence": [
            {"path": "exchange/RQ-14418.json", "kind": "compilation_request"}]}, ws)
        self.assertIn("`base/` does not exist", none)
        self.assertIn("RQ-14418 (compilation request, `/tmp/ws/case/evidence/exchange/RQ-14418.json`)", none)
        lost = C.pinned_set_statement("lost", None, ws)
        self.assertIn("no longer recoverable", lost)
        with self.assertRaises(ValueError):
            C.pinned_set_statement("approximate", None, ws)

    def test_preamble_names_the_tree_only_when_mounted(self):
        with_tree = C.render_preamble_v3("whole-tree", {"file_count": 1, "evidence": []}, "/w")
        self.assertIn("is at `/w/base`, read-only", with_tree)
        self.assertNotIn("NOT available", with_tree)
        without = C.render_preamble_v3("none-by-design", {"file_count": 0, "evidence": []}, "/w")
        self.assertIn("`/w/base` does not exist", without)

    def test_tree_profiles_route_only_in_tree_mode(self):
        self.assertEqual(C.profile_for_artifact("# doc", tree=True), "v1-tree")
        self.assertEqual(C.profile_for_artifact(json.dumps(CHANGE_SET), tree=True), "v3-changeset")
        self.assertEqual(C.profile_for_artifact(json.dumps(CHANGE_SET)), "v2-changeset")
        self.assertIn("THE TREE IS THE BEFORE-STATE", C.TREE_PROFILE_BODIES["v1-tree"])
        self.assertNotIn("NOT available to you", C.TREE_PROFILE_BODIES["v3-changeset"])
        self.assertIn("ANCHORING IS INTACT", C.TREE_PROFILE_BODIES["v3-changeset"])


class HashMismatchV3Test(unittest.TestCase):
    def _fields(self, base_source, trials=40):
        seen = set()
        op = O.hash_mismatch_v3_for(base_source)
        for seed in range(trials):
            inj = op(json.dumps(CHANGE_SET), random.Random(seed))
            seen.add((inj.detail["field"], inj.detail["checkability"]))
            self.assertEqual(inj.detail["operator_version"], "v3")
            self.assertIn(inj.detail["now"], inj.body)
            self.assertNotIn(inj.detail["was"], inj.body)
        return seen

    def test_whole_tree_flips_base_or_result_never_packet_hashes(self):
        seen = self._fields("whole-tree")
        self.assertEqual(seen, {("content_hash", "base"), ("resulting_base_hash", "base"),
                                ("result_tree_hash", "result")})

    def test_partial_tree_cannot_check_the_result(self):
        seen = self._fields("partial-product-tree")
        self.assertEqual({c for _, c in seen}, {"base"})

    def test_lost_base_has_nothing_checkable_here(self):
        with self.assertRaises(NotApplicable):
            O.hash_mismatch_v3_for("lost")(json.dumps(CHANGE_SET), random.Random(1))

    def test_table_substitutes_only_under_tree_v1(self):
        self.assertIs(O.operators_for("iso-v1")["hash_mismatch"], O.BY_NAME["hash_mismatch"])
        self.assertIsNot(O.operators_for("tree-v1", "whole-tree")["hash_mismatch"], O.BY_NAME["hash_mismatch"])
        self.assertEqual(set(O.BASE_DEPENDENT_OPERATORS), {"base_dropped", "hash_mismatch"})


ECHO_ADAPTER = {"command": ["python3", "-c", (
    "import sys,os,json;p=sys.stdin.read();"
    "open(os.path.join(os.getcwd(),'prompt-seen.txt'),'a').write(p+'\\n=====\\n');"
    "print(json.dumps({'verdict':'accept','findings':[]}))")], "prompt_mode": "stdin"}


def _repo(d):
    subprocess.run(["git", "init", "-q", d], check=True)
    os.makedirs(os.path.join(d, "docs"))
    with open(os.path.join(d, "docs", "adr-0001.md"), "w") as f:
        f.write("# ADR 0001\n")
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "-C", d, "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", d, "commit", "-qm", "x"], check=True, env=env)
    return subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


class TreeModeMeasureCaseTest(unittest.TestCase):
    PROSE = ("# Design\n\n## Decision\nWe do X. See docs/adr-0001.md.\n\n## Consequences\n"
             "Y follows from X. The scheduler stops retrying after three failures. "
             "Each failure is recorded with its cause. The operator reads the record before "
             "any manual restart. Nothing else changes in this stage.\n\n## Constraints\n"
             "The change must not touch the ledger format. It must keep the existing receipts "
             "readable. It must be reversible by a single revert. The tests named in the "
             "verification section must stay green. No new dependency is introduced.\n")

    def _case(self, operator, substrate="qs-t1", seed=3):
        return {"substrate_id": substrate, "operator": operator, "seed": seed,
                "source": {"kind": "repo-doc"}}

    def test_whole_tree_case_is_materialized_and_the_prompt_says_so(self):
        with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as ws, \
                mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "tree-v1"), \
                mock.patch.dict(M.REPOS, {"testrepo": repo}), \
                mock.patch.dict(os.environ, {"CAPLAB_NO_SANDBOX": "1"}):
            commit = _repo(repo)
            record = {"substrate_id": "qs-t1", "base_source": "whole-tree", "materializer": "git-archive",
                      "repo": "testrepo", "commit": commit, "evidence": []}
            row = pool_runner.measure_case(self._case("truncated_tail"), self.PROSE, ECHO_ADAPTER, 30,
                                           workspace=ws, base_record=record)
            self.assertTrue(row["usable"], row.get("error"))
            self.assertEqual(row["base_source"], "whole-tree")
            self.assertEqual(row["calibration_profile"], "v1-tree")
            self.assertEqual(row["review_preamble"], 3)
            self.assertEqual(row["operator_version"], "v3")
            self.assertTrue(row["base_manifest_verified"])
            self.assertEqual(row["workspace_isolation"], 2)
            case_dir = os.path.join(ws, "qs-t1-truncated_tail-3")
            self.assertTrue(os.path.isfile(os.path.join(case_dir, "base", "docs", "adr-0001.md")))
            self.assertTrue(M.verify_manifest(case_dir))
            with open(os.path.join(case_dir, "base-manifest.json")) as f:
                self.assertEqual(json.load(f)["digest"], row["base_manifest_digest"])
            with open(os.path.join(case_dir, "prompt-seen.txt")) as f:
                seen = f.read()
            self.assertIn(f"is at `{case_dir}/base`, read-only", seen)
            self.assertIn("PINNED FOR THIS CASE: the whole repository tree", seen)
            self.assertIn("THE TREE IS THE BEFORE-STATE", seen)

    def test_lost_base_with_a_base_dependent_operator_is_unscorable(self):
        with tempfile.TemporaryDirectory() as ws, \
                mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "tree-v1"):
            record = {"substrate_id": "qs-t2", "base_source": "lost", "materializer": None, "evidence": []}
            row = pool_runner.measure_case(self._case("hash_mismatch", "qs-t2"), json.dumps(CHANGE_SET),
                                           ECHO_ADAPTER, 30, workspace=ws, base_record=record)
            self.assertFalse(row["usable"])
            self.assertEqual(row["error"], "unscorable_missing_base")
            self.assertEqual(row["base_source"], "lost")

    def test_none_by_design_case_has_no_base_and_says_so(self):
        with tempfile.TemporaryDirectory() as ws, \
                mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "tree-v1"), \
                mock.patch.dict(os.environ, {"CAPLAB_NO_SANDBOX": "1"}):
            record = {"substrate_id": "qs-t3", "base_source": "none-by-design", "materializer": None,
                      "evidence": [{"name": "RQ-7", "kind": "compilation_request", "seq": 7, "payload": {"note": "n"}}]}
            row = pool_runner.measure_case(self._case("truncated_tail", "qs-t3"), self.PROSE, ECHO_ADAPTER, 30,
                                           workspace=ws, base_record=record)
            self.assertTrue(row["usable"], row.get("error"))
            case_dir = os.path.join(ws, "qs-t3-truncated_tail-3")
            self.assertFalse(os.path.exists(os.path.join(case_dir, "base")))
            self.assertTrue(os.path.isfile(os.path.join(case_dir, "evidence", "exchange", "RQ-7.json")))
            with open(os.path.join(case_dir, "prompt-seen.txt")) as f:
                seen = f.read()
            self.assertIn("`base/` does not exist", seen)
            self.assertIn("RQ-7 (compilation request", seen)

    def test_missing_registry_record_refuses_the_case(self):
        with tempfile.TemporaryDirectory() as ws, \
                mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "tree-v1"):
            row = pool_runner.measure_case(self._case("truncated_tail"), self.PROSE, ECHO_ADAPTER, 30,
                                           workspace=ws, base_record=None)
            self.assertFalse(row["usable"])
            self.assertIn("no base registry record", row["error"])

    def test_iso_mode_is_untouched(self):
        with tempfile.TemporaryDirectory() as ws, mock.patch.dict(os.environ, {"CAPLAB_NO_SANDBOX": "1"}), \
                mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "iso-v1"):
            row = pool_runner.measure_case(self._case("truncated_tail"), self.PROSE, ECHO_ADAPTER, 30, workspace=ws)
            self.assertTrue(row["usable"], row.get("error"))
            self.assertEqual(row["calibration_profile"], "v1")
            self.assertEqual(row["review_preamble"], 2)
            self.assertIsNone(row["base_manifest_verified"])
            self.assertNotIn("base_source", row)


if __name__ == "__main__":
    unittest.main()
