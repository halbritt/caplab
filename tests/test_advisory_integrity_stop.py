"""Tree failures stop local review attempts without inventing reviewer answers."""
import builtins
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from caplab.advisory import materialize as M, pool_runner
import test_review_gate as gate_fixtures

GATE = gate_fixtures.review_gate
BODY = json.dumps({"summary": "See `docs/decision.md` for the decision."})


class IntegrityStopTest(unittest.TestCase):
    def run_case(self, caller, *, before=False, after=None, replace_manifest=False,
                 malformed_manifest=False):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        captured = []
        materialize = M.materialize_case

        def corrupt(workspace):
            if malformed_manifest:
                (Path(workspace) / "base-manifest.json").write_text("[]")
                return
            path = Path(workspace) / "base/docs/decision.md"
            path.chmod(0o644)
            path.write_text("different tree\n")
            if replace_manifest:
                manifest_path = Path(workspace) / "base-manifest.json"
                manifest = json.loads(manifest_path.read_text())
                import hashlib
                manifest["entries"][0]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                manifest["digest"] = M.manifest_digest(manifest)
                manifest_path.write_text(json.dumps(manifest))
                self.assertTrue(M.verify_manifest(str(workspace)))

        def prepare(record, workspace):
            manifest = materialize(record, workspace)
            if before:
                corrupt(workspace)
            return manifest

        def invoke(adapter, prompt, timeout, workspace=None, readonly=None):
            captured.append(prompt)
            if after == len(captured):
                corrupt(workspace)
            return {"doc": {"verdict": "accept", "findings": []}, "exit_code": 0,
                    "timed_out": False, "error": None, "sandbox": "bwrap", "seconds": 1,
                    "transport": "stdin", "prompt_bytes": len(prompt.encode()), "raw_head": "retained capture"}

        with mock.patch.object(M, "base_files", return_value=(
                {"docs/decision.md": "original tree\n"}, [], {"base_source": "partial-product-tree"})), \
                mock.patch.object(M, "materialize_case", side_effect=prepare), \
                mock.patch.object(M, "store_object", return_value=BODY.encode()), \
                mock.patch.object(pool_runner, "ENVIRONMENT_VERSION", "tree-v1"), \
                mock.patch.object(pool_runner, "invoke", side_effect=invoke):
            if caller == "pool":
                row = pool_runner.measure_case(
                    {"substrate_id": "fixture", "operator": "dangling_reference", "seed": 3,
                     "source": {"kind": "repo-doc"}}, BODY, {}, 10, replicates=3, mutant_replicates=1,
                    workspace=str(root), base_record={"base_source": "partial-product-tree"})
            else:
                nc = {"id": "fixture", "pinned_base": {"object": "a" * 64},
                      "change_set": {"content_hash": "b" * 64},
                      "contract": GATE.load_gate()["natural_cases"][0]["contract"],
                      "expected": {"anchored_finding": "result_tree_hash"}}
                row = GATE.run_natural_case(nc, {}, str(root), 10, 3)
        return row, captured

    def test_failed_precheck_prevents_all_pool_invocations(self):
        row, captured = self.run_case("pool", before=True)
        self.assertEqual(len(captured), 0)
        self.assertFalse(row["usable"])
        self.assertEqual(row["control_attempts"], [])
        self.assertEqual(row["mutant_attempts"], [])
        self.assertEqual(row["control_unattempted_replicates"], 3)
        self.assertEqual(row["mutant_unattempted_replicates"], 1)
        self.assertEqual(row["integrity_failure"]["phase"], "before")
        summary = GATE.summarize_cells(
            {"cells": [{"substrate_id": "fixture", "operator": "dangling_reference"}],
             "replication": {"control": 3, "mutant": 1}},
            [row], gate_fixtures.Adjudications(), {})
        self.assertEqual(summary["cells_incomplete"], 1)
        self.assertEqual(summary["controls_by_disposition"]["unadjudicated"],
                         {"expected": 3, "observed": 0, "refused": 0, "unavailable": 3})

    def test_failed_postcheck_stops_pool_and_retains_returned_capture(self):
        row, captured = self.run_case("pool", after=1)
        self.assertEqual(len(captured), 1)
        retained = row["control_attempts"] + row["mutant_attempts"]
        self.assertEqual(len(retained), 1)
        self.assertEqual(retained[0]["raw_head"], "retained capture")
        self.assertFalse(retained[0]["manifest_verified"])
        self.assertEqual(retained[0]["review_error"], "manifest-not-verified")
        self.assertEqual(row["control_unattempted_replicates"] + row["mutant_unattempted_replicates"], 3)
        self.assertEqual(row["integrity_failure"]["phase"], "after")
        self.assertFalse(row["usable"])

    def test_natural_precheck_stops_without_shrinking_denominator(self):
        row, captured = self.run_case("natural", before=True)
        self.assertEqual(len(captured), 0)
        self.assertEqual(row["replicates"], [])
        self.assertEqual(row["expected_replicates"], 3)
        self.assertEqual(row["unattempted_replicates"], 3)
        self.assertEqual(row["unavailable"], 3)
        self.assertEqual(row["mechanical_checks_passed"], 0)

    def test_natural_postcheck_retains_earlier_observations_and_stops(self):
        row, captured = self.run_case("natural", after=2)
        self.assertEqual(len(captured), 2)
        self.assertEqual(len(row["replicates"]), 2)
        self.assertEqual([r["observed"] for r in row["replicates"]], [True, False])
        self.assertEqual(row["unavailable"], 2)
        self.assertEqual(row["unattempted_replicates"], 1)
        self.assertEqual(row["replicates"][1]["raw_head"], "retained capture")

    def test_self_consistent_replacement_cannot_change_the_pinned_manifest(self):
        for caller in ("pool", "natural"):
            with self.subTest(caller=caller):
                row, captured = self.run_case(caller, before=True, replace_manifest=True)
                self.assertEqual(len(captured), 0)

    def test_postcheck_rejects_replacement_and_malformed_manifests_without_losing_capture(self):
        for caller in ("pool", "natural"):
            for changes in ({"replace_manifest": True}, {"malformed_manifest": True}):
                with self.subTest(caller=caller, changes=changes):
                    row, captured = self.run_case(caller, after=1, **changes)
                    self.assertEqual(len(captured), 1)
                    retained = (row["control_attempts"] + row["mutant_attempts"]
                                if caller == "pool" else row["replicates"])
                    self.assertEqual(retained[0]["raw_head"], "retained capture")
                    self.assertFalse(retained[0]["manifest_verified"])
                    self.assertEqual(row["integrity_failure"]["phase"], "after")

    def test_valid_tree_runs_every_assignment(self):
        for caller, expected in (("pool", 4), ("natural", 3)):
            with self.subTest(caller=caller):
                row, captured = self.run_case(caller)
                self.assertEqual(len(captured), expected)
                if caller == "pool":
                    self.assertTrue(row["usable"])
                    self.assertEqual(row["control_unattempted_replicates"], 0)
                    self.assertEqual(row["mutant_unattempted_replicates"], 0)
                else:
                    self.assertEqual(row["unavailable"], 0)
                    self.assertEqual(row["unattempted_replicates"], 0)

    def test_postcheck_read_error_preserves_the_returned_response(self):
        with tempfile.TemporaryDirectory() as workspace:
            manifest = M.materialize_case({"base_source": "none-by-design", "evidence": [
                {"name": "FIXTURE", "kind": "fixture", "payload": {"content": "original"}},
            ]}, workspace)
            evidence = str(Path(workspace) / "evidence/exchange/FIXTURE.json")
            opened = builtins.open
            invoked = []

            def read(path, *args, **kwargs):
                if str(path) == evidence and invoked:
                    raise OSError("fixture read failure")
                return opened(path, *args, **kwargs)

            def invoke(*args, **kwargs):
                invoked.append(True)
                return {"doc": {"verdict": "accept", "findings": []}, "raw_head": "retained capture"}

            with mock.patch("builtins.open", side_effect=read), \
                    mock.patch.object(pool_runner, "invoke", side_effect=invoke):
                result = pool_runner.invoke_with_manifest({}, "prompt", 10, workspace=workspace,
                    readonly=[], manifest_digest=manifest["digest"])
            self.assertEqual(len(invoked), 1)
            self.assertEqual(result["raw_head"], "retained capture")
            self.assertTrue(result["manifest_before"])
            self.assertFalse(result["manifest_after"])
            self.assertFalse(result["manifest_verified"])


if __name__ == "__main__":
    unittest.main()
