#!/usr/bin/env python3
"""Recover production work-graph bodies from striatum's graph store.

The exchange spool that held the work-graph submissions on 2026-08-27 was
pruned, and the calibration file kept only the verdict flags. The bodies
still exist: every admitted artifact is an `artifact_admitted` ledger record
whose `body.address` names a content-addressed object (`SOB1` header, zstd
frame). This script reads the ledger through `striatum ledger cat`, decodes
every distinct work-graph object, and joins two later facts per hash: whether
a `head_movement` made it the accepted head, and whether the
`work-graph-legality` gate passed it.

Authorized by the Principal 2026-09-03 ("2 and 3 are authorized").

Usage:
  recover_production_work_graphs.py --striatum-bin PATH [--graph-store DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import collections
import datetime as _dt
import json
import os
import struct
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from caplab.advisory.planning_corpus import extract_work_graph  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRAPH_STORE = os.path.expanduser(
    "~/.local/share/striatum/graphs/019f22ef-0cb4-780f-9b82-b210bab24325")
OBJECT_HEADER = 16   # "SOB1" + "zstd" + uint64 uncompressed length


def read_object(store: str, content_hash: str) -> bytes | None:
    path = os.path.join(store, "objects", "sha256", content_hash[:2],
                        content_hash[2:4], content_hash + ".zst")
    if not os.path.isfile(path):
        return None
    raw = open(path, "rb").read()
    if raw[:4] != b"SOB1" or raw[4:8] != b"zstd":
        raise ValueError(f"{path}: unexpected object header {raw[:8]!r}")
    body = subprocess.run(["zstd", "-d", "-c"], input=raw[OBJECT_HEADER:],
                          capture_output=True, check=True).stdout
    (want,) = struct.unpack(">Q", raw[8:16])
    if len(body) != want:
        (want_le,) = struct.unpack("<Q", raw[8:16])
        if len(body) != want_le:
            raise ValueError(f"{path}: length {len(body)} != header {want}")
    return body


def ledger_events(striatum_bin: str, cwd: str):
    proc = subprocess.run([striatum_bin, "-json", "ledger", "cat"], cwd=cwd,
                          capture_output=True, text=True, check=True)
    for line in proc.stdout.splitlines():
        if line.strip():
            yield json.loads(line)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--striatum-bin", required=True,
                    help="a striatum binary built from the checkout whose catalog "
                         "is current (an old binary refuses to decode the catalog)")
    ap.add_argument("--striatum-repo", default=os.path.expanduser("~/git/striatum-next"))
    ap.add_argument("--graph-store", default=GRAPH_STORE)
    ap.add_argument("--out", default=os.path.join(
        ROOT, "advisory", "pool-runs", "production-work-graphs-20260903"))
    args = ap.parse_args()

    admitted: dict[str, dict] = {}
    accepted, legality_pass = set(), set()
    kinds = collections.Counter()
    n_events = 0
    for e in ledger_events(args.striatum_bin, args.striatum_repo):
        n_events += 1
        payload = e.get("payload") or {}
        t = e.get("type")
        if t == "artifact_admitted":
            kinds[payload.get("kind")] += 1
            if payload.get("kind") == "work-graph" and payload.get("content_hash"):
                attribution = payload.get("attribution") or {}
                admitted.setdefault(payload["content_hash"], {
                    "seq": e.get("seq"), "identity": payload.get("identity"),
                    "lifecycle_at_admission": payload.get("lifecycle"),
                    "level": payload.get("level"),
                    "backend": attribution.get("backend_id"),
                    "aliasing_class": attribution.get("aliasing_class"),
                    "production_mode": payload.get("production_mode")})
        elif t == "head_movement":
            cand = ((payload.get("effect") or {}).get("candidate") or {}).get("content_hash")
            if cand:
                accepted.add(cand)
        elif t == "gate_result" and payload.get("gate_id") == "work-graph-legality" \
                and payload.get("outcome") == "pass":
            h = (payload.get("subject") or {}).get("content_hash")
            if h:
                legality_pass.add(h)

    os.makedirs(args.out, exist_ok=True)
    counts = collections.Counter()
    with open(os.path.join(args.out, "graphs.jsonl"), "w", encoding="utf-8") as f:
        for h, meta in sorted(admitted.items(), key=lambda kv: kv[1]["seq"] or 0):
            body = read_object(args.graph_store, h)
            if body is None:
                counts["missing_object"] += 1
                continue
            graph = extract_work_graph(body.decode("utf-8", "replace"))
            if graph is None:
                counts["unparseable"] += 1
                continue
            row = {"content_hash": h, **meta, "accepted": h in accepted,
                   "legality_gate_pass": h in legality_pass, "graph": graph}
            counts["recovered"] += 1
            counts["accepted"] += int(row["accepted"])
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    summary = {"ledger_events": n_events, "artifact_kinds": dict(kinds),
               "distinct_work_graph_hashes": len(admitted), **counts,
               "graph_store": args.graph_store,
               "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat()}
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(summary, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
