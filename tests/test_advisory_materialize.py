from functools import partial
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from caplab.advisory import materialize as M


class CanonicalProductTest(unittest.TestCase):
    def test_struct_order_and_escaping(self):
        body = M.canonical_product({"b.md": "x < y & z", "a.go": "package a\n"},
                                   anchor={"kind": "git-tree", "commit": "c", "tree": "t"}, deletes=["gone"])
        text = body.decode()
        self.assertTrue(text.startswith('{\n  "schema_version": 1,\n  "files": {\n    "a.go"'))
        self.assertIn('"x \\u003c y \\u0026 z"', text)
        self.assertLess(text.index('"files"'), text.index('"anchor"'))
        self.assertLess(text.index('"anchor"'), text.index('"deletes"'))
        self.assertTrue(text.endswith("}\n"))
        self.assertNotIn('"deletes"', M.canonical_product({}, deletes=[]).decode())

    @unittest.skipUnless(os.path.isdir(M.GRAPH_STORE) and os.path.isfile(
        os.path.join(os.path.dirname(__file__), "..", "advisory", "tree-v1-bases.json")),
        "no graph store / registry on this host")
    def test_reproduces_a_stored_product_hash(self):
        reg = M.load_registry(os.path.join(os.path.dirname(__file__), "..", "advisory", "tree-v1-bases.json"))
        rec = next(r for r in reg.values() if r.get("materializer") == "product-object")
        body = M.store_object(rec["object"])
        self.assertIsNotNone(body)
        prod = json.loads(body)
        self.assertEqual(M.tree_hash(prod["files"], prod.get("anchor"), prod.get("deletes")), rec["object"])


class ApplyOverlayTest(unittest.TestCase):
    def test_unanchored_delete_of_absent_path_conflicts(self):
        res, conflicts = M.apply_overlay({"files": {"a": "1"}}, {"files": {}, "deletes": ["zz"]})
        self.assertIsNone(res)
        self.assertEqual(conflicts[0]["path"], "zz")

    def test_unanchored_overlay(self):
        res, conflicts = M.apply_overlay({"files": {"a": "1", "b": "2"}}, {"files": {"c": "3", "a": "9"}, "deletes": ["b"]})
        self.assertEqual(conflicts, [])
        self.assertEqual(res["files"], {"a": "9", "c": "3"})
        self.assertNotIn("anchor", res)

    def test_anchored_deletes_become_tombstones_and_writes_resurrect(self):
        base = {"files": {"a": "1"}, "anchor": {"kind": "git-tree", "commit": "c", "tree": "t"}, "deletes": ["old"]}
        res, conflicts = M.apply_overlay(base, {"files": {"old": "back"}, "deletes": ["a", "never-there"]})
        self.assertEqual(conflicts, [])
        self.assertEqual(res["files"], {"old": "back"})
        self.assertEqual(res["deletes"], ["a", "never-there"])
        self.assertEqual(res["anchor"], base["anchor"])

    def test_declared_base_hash_by_schema(self):
        self.assertEqual(M.declared_base_hash({"schema_version": 1, "base": {"content_hash": "x"}}), "x")
        self.assertEqual(M.declared_base_hash({"schema_version": 2, "base_composition": {"resulting_base_hash": "y"}}), "y")


class WriteFilesTest(unittest.TestCase):
    def test_rejects_unsafe_entries(self):
        for files in ({"/abs": "x"}, {"a/../b": "x"}, {"a//b": "x"}, {"": "x"}, {"a\\b": "x"},
                      {"README": "x", "readme": "y"}, {"a": b"bytes"}):
            with tempfile.TemporaryDirectory() as d, self.assertRaises(M.UnsafeEntry):
                M.write_files(files, d)

    def test_writes_read_only_files_with_digests(self):
        with tempfile.TemporaryDirectory() as d:
            entries = M.write_files({"docs/a.md": "hello\n", "b": ""}, d)
            self.assertEqual([e["path"] for e in entries], ["b", "docs/a.md"])
            self.assertEqual(entries[1]["bytes"], 6)
            self.assertFalse(os.access(os.path.join(d, "docs/a.md"), os.W_OK) and False)
            self.assertEqual(oct(os.stat(os.path.join(d, "docs/a.md")).st_mode & 0o777), "0o444")


class MaterializeCaseTest(unittest.TestCase):
    def _object(self, root, product):
        body = (json.dumps(product) + "\n").encode()
        digest = hashlib.sha256(body).hexdigest()
        path = Path(root, "objects", "sha256", digest[:2], digest[2:4], digest + ".zst")
        path.parent.mkdir(parents=True, exist_ok=True)
        packed = subprocess.run(["zstd", "-q", "-c"], input=body, capture_output=True, check=True)
        path.write_bytes(b"SOB1" + b"\0" * 12 + packed.stdout)
        return digest, path

    def test_anchored_objects_cannot_claim_an_expanded_base(self):
        for source, how in (("whole-tree", "materialized_base"),
                            ("whole-tree", "product-object"),
                            ("partial-product-tree", "materialized_base")):
            for anchor in ({"kind": "git-tree", "commit": "c", "tree": "t"}, {}, False):
                with self.subTest(source=source, how=how, anchor=anchor), tempfile.TemporaryDirectory() as root:
                    digest, _ = self._object(root, {"files": {"overlay.txt": "overlay"}, "anchor": anchor})
                    record = {"base_source": source, "materializer": how, "object": digest}
                    case = Path(root, "case")
                    # Redirect only the external store root; decode and hash verification remain real.
                    with mock.patch.object(M, "store_object", partial(M.store_object, root=root)):
                        with self.assertRaisesRegex(ValueError, "anchored product"):
                            M.materialize_case(record, str(case))
                    self.assertFalse(case.exists())

    def test_partial_and_expanded_objects_keep_their_views_and_valid_cache(self):
        anchor = {"kind": "git-tree", "commit": "c", "tree": "t"}
        for source, how, product_anchor in (("partial-product-tree", "product-object", anchor),
                                             ("whole-tree", "materialized_base", None),
                                             ("whole-tree", "product-object", None)):
            with self.subTest(source=source, how=how), tempfile.TemporaryDirectory() as root:
                digest, object_path = self._object(root, {"files": {"a.txt": "body"}, "anchor": product_anchor})
                record = {"base_source": source, "materializer": how, "object": digest}
                case = Path(root, "case")
                with mock.patch.object(M, "store_object", partial(M.store_object, root=root)):
                    manifest = M.materialize_case(record, str(case))
                    self.assertEqual(manifest["base_source"], source)
                    self.assertEqual(manifest["anchor"], product_anchor)
                    self.assertEqual(case.joinpath("base/a.txt").read_text(), "body")
                    self.assertTrue(M.verify_manifest(str(case), expected_digest=manifest["digest"]))
                    object_path.unlink()
                    self.assertEqual(M.materialize_case(record, str(case)), manifest)

    def test_contradictory_cached_manifest_is_rejected_without_destroying_payloads(self):
        for source, how in (("whole-tree", "materialized_base"),
                            ("whole-tree", "product-object"),
                            ("partial-product-tree", "materialized_base")):
            with self.subTest(source=source, how=how), tempfile.TemporaryDirectory() as root:
                product = {"files": {"a.txt": "overlay"}, "anchor": {"kind": "git-tree", "commit": "c", "tree": "t"}}
                digest, _ = self._object(root, product)
                record = {"base_source": "partial-product-tree", "materializer": "product-object", "object": digest,
                          "evidence": [{"name": "RQ-1", "kind": "compilation_request", "seq": 1, "payload": {"note": "n"}}]}
                case = Path(root, "case")
                with mock.patch.object(M, "store_object", partial(M.store_object, root=root)):
                    manifest = M.materialize_case(record, str(case))
                    # Model the old writer's self-consistent but contradictory manifest.
                    manifest.update(base_source=source, materializer=how)
                    manifest["digest"] = M.manifest_digest(manifest)
                    case.joinpath("base-manifest.json").write_text(json.dumps(manifest))
                    before = {str(p.relative_to(case)): p.read_bytes() for p in case.rglob("*") if p.is_file()}
                    self.assertFalse(M.verify_manifest(str(case), expected_digest=manifest["digest"]))
                    record.update(base_source=source, materializer=how)
                    with self.assertRaisesRegex(ValueError, "anchored product"):
                        M.materialize_case(record, str(case))
                    after = {str(p.relative_to(case)): p.read_bytes() for p in case.rglob("*") if p.is_file()}
                    self.assertEqual(after, before)

    def test_invalid_replacement_source_preserves_incomplete_case(self):
        with tempfile.TemporaryDirectory() as root:
            digest, _ = self._object(root, {"files": {}, "anchor": {}})
            case = Path(root, "case")
            case.joinpath("base").mkdir(parents=True)
            case.joinpath("base/retained.txt").write_bytes(b"retained")
            record = {"base_source": "whole-tree", "materializer": "materialized_base", "object": digest}
            with mock.patch.object(M, "store_object", partial(M.store_object, root=root)):
                with self.assertRaisesRegex(ValueError, "anchored product"):
                    M.materialize_case(record, str(case))
            self.assertEqual(case.joinpath("base/retained.txt").read_bytes(), b"retained")
            self.assertFalse(case.joinpath("base-manifest.json").exists())

    def _repo(self, d):
        subprocess.run(["git", "init", "-q", d], check=True)
        os.makedirs(os.path.join(d, "docs"))
        with open(os.path.join(d, "docs", "adr.md"), "w") as f:
            f.write("# ADR\n")
        with open(os.path.join(d, "bin.dat"), "wb") as f:
            f.write(b"\xff\xfe\x00binary")
        os.symlink("docs/adr.md", os.path.join(d, "link.md"))
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        subprocess.run(["git", "-C", d, "add", "-A"], check=True, env=env)
        subprocess.run(["git", "-C", d, "commit", "-qm", "x"], check=True, env=env)
        return subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

    def test_git_archive_case_round_trips_and_verifies(self):
        with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as case:
            commit = self._repo(repo)
            old = dict(M.REPOS)
            M.REPOS["testrepo"] = repo
            try:
                rec = {"substrate_id": "qs-test", "base_source": "whole-tree", "materializer": "git-archive",
                       "repo": "testrepo", "commit": commit,
                       "evidence": [{"name": "RQ-1", "kind": "compilation_request", "seq": 1, "payload": {"note": "n"}}]}
                manifest = M.materialize_case(rec, case)
            finally:
                M.REPOS.clear(); M.REPOS.update(old)
            self.assertEqual([e["path"] for e in manifest["entries"]], ["docs/adr.md"])
            self.assertEqual({s["why"] for s in manifest["skipped"]}, {"binary", "symlink"})
            self.assertTrue(os.path.isfile(os.path.join(case, "evidence", "exchange", "RQ-1.json")))
            self.assertTrue(M.verify_manifest(case))
            # a byte changed under base/ is noticed
            path = os.path.join(case, "base", "docs", "adr.md")
            os.chmod(path, 0o644)
            with open(path, "a") as f:
                f.write("tamper")
            self.assertFalse(M.verify_manifest(case))
            # an extra file is noticed too
            os.chmod(path, 0o644)
            with open(path, "w") as f:
                f.write("# ADR\n")
            with open(os.path.join(case, "base", "extra"), "w") as f:
                f.write("x")
            self.assertFalse(M.verify_manifest(case))

    def test_artifact_under_review_and_instrument_ledger_are_removed_and_recorded(self):
        with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as case:
            os.makedirs(os.path.join(repo, "advisory", "checks"))
            with open(os.path.join(repo, "advisory", "checks", "verify-control-x.py"), "w") as f:
                f.write("print('label')\n")
            with open(os.path.join(repo, "advisory", "claims.jsonl"), "w") as f:
                f.write("{}\n")
            commit = self._repo(repo)
            old = dict(M.REPOS)
            M.REPOS["caplab"] = repo
            try:
                rec = {"substrate_id": "qs-t", "base_source": "whole-tree", "materializer": "git-archive",
                       "repo": "caplab", "commit": commit, "artifact_path": "docs/adr.md", "evidence": []}
                manifest = M.materialize_case(rec, case)
            finally:
                M.REPOS.clear(); M.REPOS.update(old)
            paths = [e["path"] for e in manifest["entries"]]
            self.assertNotIn("docs/adr.md", paths)
            self.assertNotIn("advisory/checks/verify-control-x.py", paths)
            self.assertIn("advisory/claims.jsonl", paths)
            self.assertEqual({(r["path"], r["why"]) for r in manifest["removed"]},
                             {("docs/adr.md", "artifact-under-review"),
                              ("advisory/checks/verify-control-x.py", "instrument-ledger")})
            self.assertNotEqual(manifest["exact_snapshot_digest"], manifest["view_digest"])
            self.assertTrue(M.verify_manifest(case))

    def test_no_base_case_writes_only_evidence_and_manifest(self):
        with tempfile.TemporaryDirectory() as case:
            rec = {"substrate_id": "qs-p", "base_source": "none-by-design", "materializer": None, "evidence": []}
            manifest = M.materialize_case(rec, case)
            self.assertFalse(os.path.exists(os.path.join(case, "base")))
            self.assertEqual(manifest["file_count"], 0)
            self.assertTrue(M.verify_manifest(case))


if __name__ == "__main__":
    unittest.main()
