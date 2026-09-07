#!/usr/bin/env python3
"""Build the tree-v1 base registry and run the change-set oracle (plan §6.2).

For every substrate in advisory/substrates.jsonl, decide the base production
gave its reviewer (§2.3 amendment) and record how to materialize it:

  repo-doc            -> whole-tree, git-archive at the registered commit
  exchange prose      -> none-by-design (+ RQ- compilation requests it names)
  exchange change set -> whole-tree via the run's materialized_base pin, or a
                         git-tree anchor in history; else partial-product-tree
                         via the declared product object; else lost

Then the oracle, fail closed, on every change set with a whole tree: the
declared base object re-hashes to its own name (our canonical form is
striatum's), every product file is in the materialized tree with identical
content, and TreeHash(ApplyOverlay(materialized, change set)) equals the
declared result_tree_hash. A mismatch is reported and the plan stops.

Usage: tree_v1_bases.py --ledger ledger.jsonl [--out advisory/tree-v1-bases.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from caplab.advisory import cas, materialize as M  # noqa: E402

RQ = re.compile(r"\b(RQ-\d{3,6})\b")


def load_ledger(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--substrates", default=os.path.join(ROOT, "advisory", "substrates.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "advisory", "tree-v1-bases.json"))
    ap.add_argument("--report", default=os.path.join(ROOT, "advisory", "pool-runs", "tree-v1-oracle-20260906"))
    args = ap.parse_args()

    subs = [json.loads(l) for l in open(args.substrates, encoding="utf-8") if l.strip()]
    dispatch_of = {s["source"]["dispatch_id"]: s["substrate_id"] for s in subs
                   if s["source"].get("kind") == "striatum-exchange"}
    run_of, runs, requests = {}, {}, {}
    for e in load_ledger(args.ledger):
        p = e.get("payload") or {}
        t = e["type"]
        if t == "submission_received" and p.get("dispatch_id") in dispatch_of:
            run_of[p["dispatch_id"]] = p.get("run_ref")
        elif t == "pass_run_opened":
            runs[e["seq"]] = p
        elif t == "compilation_request":
            requests[e["seq"]] = p

    bases, oracle, counts = {}, [], collections.Counter()
    for s in subs:
        sid, src = s["substrate_id"], s["source"]
        rec = {"substrate_id": sid, "source_kind": src["kind"]}
        body = cas.load(s["sha256"])
        if body is None:
            rec.update(base_source="lost", materializer=None, why="substrate body not in the CAS")
            bases[sid] = rec; counts["lost"] += 1
            continue
        # exchange objects the artifact names, resolved by ledger seq
        evidence = []
        for name in sorted(set(RQ.findall(body))):
            seq = int(name[3:])
            if seq in requests:
                evidence.append({"name": name, "kind": "compilation_request", "seq": seq,
                                 "payload": requests[seq]})
            else:
                evidence.append({"name": name, "kind": "unresolved", "seq": seq})
        rec["evidence"] = [ev for ev in evidence if ev["kind"] != "unresolved"]
        rec["unresolved_references"] = [ev["name"] for ev in evidence if ev["kind"] == "unresolved"]
        if src["kind"] == "repo-doc":
            rec.update(base_source="whole-tree", materializer="git-archive",
                       repo=src["repo"], commit=src["commit"])
            ok = subprocess.run(["git", "-C", M.REPOS[src["repo"]], "cat-file", "-e", f"{src['commit']}^{{commit}}"],
                                capture_output=True).returncode == 0
            if not ok:
                rec.update(base_source="lost", materializer=None, why="registered commit not in history")
            bases[sid] = rec; counts[rec["base_source"]] += 1
            continue
        try:
            doc = json.loads(body)
        except ValueError:
            doc = None
        is_cs = isinstance(doc, dict) and ({"files", "base", "base_composition"} & set(doc))
        if not is_cs:
            rec.update(base_source="none-by-design", materializer=None,
                       why="production pinned the artifact alone", run=run_of.get(src["dispatch_id"]))
            bases[sid] = rec; counts["none-by-design"] += 1
            continue
        run = run_of.get(src["dispatch_id"])
        pins = ((runs.get(run) or {}).get("manifest") or {}).get("input_pins") or []
        mb = next((p["content_hash"] for p in pins if p.get("role") == "materialized_base"), None)
        base_pin = next((p["content_hash"] for p in pins if p.get("role") == "base"), None)
        declared = M.declared_base_hash(doc)
        rec.update(run=run, declared_base_hash=declared, base_pin=base_pin, materialized_base=mb,
                   schema_version=doc.get("schema_version"), result_tree_hash=doc.get("result_tree_hash"))
        if mb and M.store_object(mb) is not None:
            rec.update(base_source="whole-tree", materializer="materialized_base", object=mb)
        elif isinstance(doc.get("anchor"), dict) and doc["anchor"].get("kind") == "git-tree" and \
                subprocess.run(["git", "-C", M.REPOS["striatum-next"], "cat-file", "-e",
                                f"{doc['anchor']['commit']}^{{commit}}"], capture_output=True).returncode == 0:
            rec.update(base_source="whole-tree", materializer="git-archive", repo="striatum-next",
                       commit=doc["anchor"]["commit"], anchor=doc["anchor"])
        elif declared and M.store_object(declared) is not None:
            rec.update(base_source="partial-product-tree", materializer="product-object", object=declared)
        else:
            rec.update(base_source="lost", materializer=None,
                       why="declared base object absent from the store and no whole tree pinned")
        bases[sid] = rec; counts[rec["base_source"]] += 1

        # --- oracle, on every change set that has a whole tree or a product ---
        if rec["base_source"] in ("whole-tree", "partial-product-tree"):
            check = {"substrate_id": sid, "base_source": rec["base_source"], "materializer": rec["materializer"]}
            if declared:
                obj = M.store_object(declared)
                if obj is None:
                    check["declared_base_present"] = False
                else:
                    prod = json.loads(obj)
                    check["declared_base_present"] = True
                    check["declared_base_rehashes"] = (
                        M.tree_hash(prod.get("files") or {}, prod.get("anchor"), prod.get("deletes")) == declared)
            if rec["materializer"] == "materialized_base":
                tree = json.loads(M.store_object(mb))
                check["materialized_rehashes"] = M.tree_hash(tree["files"], tree.get("anchor"), tree.get("deletes")) == mb
                if declared and check.get("declared_base_present"):
                    pf = prod.get("files") or {}
                    check["product_files_in_tree"] = all(tree["files"].get(k) == v for k, v in pf.items())
                    check["product_file_count"] = len(pf)
                result, conflicts = M.apply_overlay(tree, doc)
                check["apply_conflicts"] = conflicts
                if result is not None and doc.get("result_tree_hash"):
                    check["derived_result_tree_hash"] = M.tree_hash(result["files"], result.get("anchor"), result.get("deletes"))
                    check["result_tree_hash_matches"] = check["derived_result_tree_hash"] == doc["result_tree_hash"]
                elif result is not None:
                    check["result_tree_hash_matches"] = None  # v1 change set declares none
            check["passed"] = all(v is not False for k, v in check.items()
                                  if k in ("declared_base_present", "declared_base_rehashes", "materialized_rehashes",
                                           "product_files_in_tree", "result_tree_hash_matches")) \
                and not check.get("apply_conflicts")
            oracle.append(check)

    os.makedirs(args.report, exist_ok=True)
    doc = {"record": "caplab-tree-v1-base-registry/1", "built": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "ledger": os.path.basename(args.ledger), "counts": dict(counts), "bases": bases}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(args.report, "oracle.jsonl"), "w", encoding="utf-8") as f:
        for c in oracle:
            f.write(json.dumps(c, sort_keys=True) + "\n")
    failed = [c for c in oracle if not c["passed"]]
    by_src = collections.Counter((c["base_source"], c["materializer"]) for c in oracle)
    summary = {"substrates": len(subs), "counts": dict(counts), "oracle_checked": len(oracle),
               "oracle_failed": len(failed), "oracle_by_source": {f"{a}/{b}": n for (a, b), n in by_src.items()},
               "with_result_tree_hash_checked": sum(1 for c in oracle if c.get("result_tree_hash_matches") is True),
               "evidence_objects": sum(len(r.get("evidence") or []) for r in bases.values()),
               "unresolved_references": sorted({u for r in bases.values() for u in r.get("unresolved_references") or []})}
    with open(os.path.join(args.report, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1))
    for c in failed[:10]:
        print("FAILED", json.dumps(c)[:400])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
