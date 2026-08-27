#!/usr/bin/env python3
"""Per-subject tables for the Arm 1 qualification sweep.

Rates alone rank a degenerate planner first: a one-packet work graph that
names a real check set parses, indexes, stays acyclic and resolves — it
clears every mechanical gate the oracle has, while planning nothing. So
structure is printed beside every rate, and the count of trivially small
graphs is printed beside that.
"""

from __future__ import annotations

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
