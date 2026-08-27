#!/usr/bin/env python3
"""Per-subject tables for the Arm 1 qualification sweep.

Rates alone rank a degenerate planner first: a one-packet work graph that
names a real check set parses, indexes, stays acyclic and resolves — it
clears every mechanical gate the oracle has, while planning nothing. So
structure is printed beside every rate, and the count of trivially small
graphs is printed beside that.
"""

from __future__ import annotations

import itertools
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from caplab.advisory.wilson import wilson  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS = os.path.join(ROOT, "advisory", "pool-runs")

#: A work graph this small is not a packetization of a real engineering
#: step. It is not scored as a failure — the oracle has no promise-coverage
#: check and inventing a threshold would be inventing a metric — but it is
#: counted and printed so no rate can be read without it.
DEGENERATE_PACKETS = 2


def parsed(rows):
    """Rows whose graph parsed.

    The oracle reports zero packets for a graph it could not parse, so
    structure read over unparsed rows counts parse failures as degenerate
    plans — two different defects wearing one number.
    """
    return [r for r in rows if r.get("parse_ok")]


def _scopes(packet):
    return [w for w in (packet.get("write_scope") or []) if w]


def _overlap(a, b):
    return any(x == y or x.startswith(y) or y.startswith(x)
               for x in a for y in b)


def scope_diagnostics(row):
    """Size-normalized disjointness, and the collision no tree would excuse.

    The binary legality verdict fails a graph if any one packet pair
    collides, and a k-packet graph has k(k-1)/2 pairs — so the rate falls
    with how much the planner actually decomposed the work. The share of
    pairs that collide does not carry that bias. Reported beside it: whether
    two packets declared the *identical* write scope, which is a planner's
    choice rather than an artifact of not being able to see the tree.
    """
    packets = (row.get("graph") or {}).get("packets") or []
    pairs = list(itertools.combinations(packets, 2))
    if not pairs:
        return None
    collide = sum(1 for a, b in pairs if _overlap(_scopes(a), _scopes(b)))
    duplicate = any(_scopes(a) and sorted(_scopes(a)) == sorted(_scopes(b))
                    for a, b in pairs)
    return {"disjointness": 1 - collide / len(pairs), "duplicate_scope": duplicate}


def median(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


def load(run_dir):
    path = os.path.join(run_dir, "results.jsonl")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    dirs = sorted(d for d in os.listdir(RUNS)
                  if d.startswith("plan-") and "calibration" not in d)
    print(f"{'subject':<30}{'n':>4}{'yield':>7}{'finish':>8}{'ci95':>16}"
          f"{'legal':>7}{'resolv':>8}{'pkts':>6}{'dxw':>6}{'triv':>6}")
    print("-" * 98)
    for d in dirs:
        rows = load(os.path.join(RUNS, d))
        if not rows:
            continue
        usable = [r for r in rows if r.get("usable")]
        subject = rows[0]["subject"]
        if not usable:
            print(f"{subject:<30}{len(rows):>4}   no usable graph")
            continue
        n = len(usable)
        ok = sum(1 for r in usable if r["all_checks_ok"])
        lo, hi = wilson(ok, n)
        legal = sum(1 for r in usable if r["parse_ok"] and r["index_ok"]
                    and r["legality_ok"])
        res = sum(1 for r in usable if r["resolvable_ok"])
        struct = parsed(usable)
        triv = sum(1 for r in struct
                   if (r.get("packets") or 0) <= DEGENERATE_PACKETS)
        print(f"{subject:<30}{n:>4}{n / len(rows):>7.2f}{ok / n:>8.2f}"
              f"{f'[{lo:.2f},{hi:.2f}]':>16}{legal / n:>7.2f}{res / n:>8.2f}"
              f"{median(r['packets'] for r in struct):>6.0f}"
              f"{median(r['depth_width_product'] for r in struct):>6.0f}"
              f"{triv:>6}")

    print("\nn = usable graphs; yield = usable/attempted; finish = every "
          f"mechanical check; triv = graphs with <= {DEGENERATE_PACKETS} "
          "packets.\nWrite-scope and atomicity are 'tree-not-provided' in the "
          "design-only environment\nand are excluded from every rate.\n")

    for d in dirs:
        rows = load(os.path.join(RUNS, d))
        usable = [r for r in rows if r.get("usable")]
        if not usable:
            continue
        fails = Counter()
        for r in usable:
            for cls in (r.get("legality_failures") or []):
                fails["legality:" + str(cls)] += 1
            if r.get("parse_ok") is False:
                fails["parse:" + str(r.get("parse_error"))[:60]] += 1
            if r.get("resolvable_ok") is False:
                for check in (r.get("unresolvable_checks") or [])[:3]:
                    fails["unresolvable:" + str(check)] += 1
        dead = Counter(r.get("error") for r in rows if not r.get("usable"))
        if fails or dead:
            print(f"{rows[0]['subject']}:")
            for k, v in fails.most_common(8):
                print(f"    {v:>3}  {k}")
            for k, v in dead.most_common(4):
                print(f"    {v:>3}  DISCARDED {k}")

    print("\npacket-count distribution per subject:")
    for d in dirs:
        rows = [r for r in load(os.path.join(RUNS, d)) if r.get("usable")]
        if not rows:
            continue
        counts = sorted(r["packets"] for r in parsed(rows))
        print(f"    {rows[0]['subject']:<30}{counts}")

    # The construct's central risk, measured rather than asserted: if the
    # mechanical rate falls as graphs get bigger, then the rate rewards not
    # planning and must never be read without the structure beside it.
    pooled = []
    for d in dirs:
        pooled += parsed([r for r in load(os.path.join(RUNS, d))
                          if r.get("usable")])
    if pooled:
        print("\npooled pass rate by graph size (all subjects):")
        buckets = [(1, 2, "1-2 packets"), (3, 5, "3-5 packets"),
                   (6, 9, "6-9 packets"), (10, 10 ** 6, "10+ packets")]
        for lo, hi, label in buckets:
            grp = [r for r in pooled if lo <= (r.get("packets") or 0) <= hi]
            if not grp:
                continue
            ok = sum(1 for r in grp if r["all_checks_ok"])
            wlo, whi = wilson(ok, len(grp))
            print(f"    {label:<14} n={len(grp):>3}  pass={ok / len(grp):.2f}"
                  f"  [{wlo:.2f},{whi:.2f}]")

    print("\nsize-normalized scope diagnostics (graphs with >= 2 packets):")
    print(f"    {'subject':<30}{'n':>4}{'disjointness':>14}{'exact-dup':>11}")
    for d in dirs:
        graphs = [r for r in parsed([r for r in load(os.path.join(RUNS, d))
                                     if r.get("usable")])
                  if (r.get("packets") or 0) >= 2]
        diag = [(r, scope_diagnostics(r)) for r in graphs]
        diag = [(r, x) for r, x in diag if x]
        if not diag:
            continue
        dup = sum(1 for _, x in diag if x["duplicate_scope"])
        print(f"    {diag[0][0]['subject']:<30}{len(diag):>4}"
              f"{median(x['disjointness'] for _, x in diag):>14.2f}"
              f"{f'{dup}/{len(diag)}':>11}")

    cal = os.path.join(RUNS, "plan-calibration-20260827", "calibration-summary.json")
    if os.path.isfile(cal):
        with open(cal, encoding="utf-8") as f:
            c = json.load(f)
        n = c["n_identities"]
        print(f"\ncalibration (production work graphs, {n} identities): "
              f"parse {c['parse_ok']}/{n}, legality {c['legality_ok']}/{n}, "
              f"resolvable {c['resolvable_ok']}/{n}, "
              f"all checks {c['all_checks_ok']}/{n}")
        print("    population is 67/68 `local` (the deterministic backend that "
              "owns packetization);\n    it calibrates the oracle and is not a "
              "per-task control.")


if __name__ == "__main__":
    main()
