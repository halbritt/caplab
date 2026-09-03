#!/usr/bin/env python3
"""Calibrate plan judges on audited control/mutant pairs (ranking memo, layer 1).

Before any pairwise ranking is read, every judge in the jury is shown pairs
whose truth is known: a sound control graph and the same graph with one
audited defect injected. The judge must prefer the control. Each pair runs in
both orders under two judges from families independent of the planner, and
an order-dependent verdict is a tie. Output: per judge and defect class,
catch with a Wilson interval, the share of pairs where the judge preferred
the defect, the tie share, the position-flip rate, and — read apart from the
defect classes — whether the judge's verdicts on the two size probes track
packet count.

Authorized by the Principal 2026-09-03 ("2 and 3 are authorized").

Usage:
  plan_judge_calibration.py --audit DIR --jury J1 J2 [J3] [--per-class N]
                            [--workers K] [--smoke N] [--out DIR]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import random
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from caplab.advisory import plan_judges as pj  # noqa: E402
from caplab.advisory import plan_operators as ops  # noqa: E402
from caplab.advisory.instrument_defects import NotApplicable  # noqa: E402
from caplab.advisory.pool_runner import ENVIRONMENT_VERSION, declared_lanes, load_declaration  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS = os.path.join(ROOT, "advisory", "pool-runs")
TASKS = os.path.join(ROOT, "advisory", "planning-tasks.jsonl")
BACKENDS = os.path.expanduser("~/git/striatum-next/backends")


def load_graphs() -> dict[str, dict]:
    """identity -> (graph, task_id) for every usable sweep graph."""
    out = {}
    for path in sorted(glob.glob(os.path.join(RUNS, "plan-*-20260827", "results.jsonl"))):
        if "calibration" in path:
            continue
        for line in open(path, encoding="utf-8"):
            row = json.loads(line)
            if row.get("usable") and isinstance(row.get("graph"), dict):
                out[f"{row['subject']}/{row['task_id']}"] = {
                    "graph": row["graph"], "task_id": row["task_id"]}
    return out


def regenerate_mutant(identity: str, operator: str, graph: dict, audit_seed: int) -> dict:
    """The exact mutant the audit admitted: same operator, same rng key."""
    body = json.dumps(graph, sort_keys=True)
    rng = random.Random(f"{audit_seed}:{identity}:{operator}")
    injection = ops.BY_NAME[operator](body, rng)
    return {"graph": json.loads(injection.body), "anchor": injection.element_anchor,
            "description": injection.description}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit", default=os.path.join(RUNS, "plan-operators-audit-20260902"))
    ap.add_argument("--jury", nargs="+", required=True,
                    help="judge backend ids in preference order; the first two "
                         "eligible for a pair judge it")
    ap.add_argument("--per-class", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20260903)
    ap.add_argument("--workers", type=int, default=1,
                    help="lanes per judge; capped by each declaration")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--smoke", type=int, default=0,
                    help="run only the first N pairs (a dry run of the plumbing)")
    ap.add_argument("--out", default=os.path.join(RUNS, "plan-judge-calibration-20260903"))
    args = ap.parse_args()

    audit_summary = json.load(open(os.path.join(args.audit, "summary.json")))
    audit_rows = [json.loads(l) for l in open(os.path.join(args.audit, "audit.jsonl")) if l.strip()]
    graphs = load_graphs()
    tasks = {t["task_id"]: t for t in (json.loads(l) for l in open(TASKS) if l.strip())}
    judges = [pj.judge_adapter(BACKENDS, j) for j in args.jury]
    classes = {j["judge_id"]: j["aliasing_class"] for j in judges}
    lanes = {j["judge_id"]: min(max(1, args.workers),
                                declared_lanes(load_declaration(BACKENDS, j["judge_id"])))
             for j in judges}

    pairs = pj.sample_pairs(audit_rows, per_class=args.per_class, seed=args.seed)
    if args.smoke:
        pairs = pairs[:args.smoke]
    planner_classes = {}
    for p in pairs:
        planner_classes.setdefault(p["planner"], pj.planner_class(BACKENDS, p["planner"]))

    os.makedirs(args.out, exist_ok=True)
    calls_path = os.path.join(args.out, "calls.jsonl")
    done = set()
    if os.path.isfile(calls_path):
        for line in open(calls_path, encoding="utf-8"):
            r = json.loads(line)
            if r.get("preferred") is not None:
                done.add((r["pair_id"], r["judge"], r["order"]))

    # Every call this run will make: (pair, judge, order).
    work = []
    for p in pairs:
        eligible = pj.eligible_judges(judges, planner_classes[p["planner"]], want=2)
        for judge in eligible:
            for order in ("control-first", "mutant-first"):
                if (p["pair_id"], judge["judge_id"], order) not in done:
                    work.append((p, judge, order))
    print(f"{len(pairs)} pairs, {len(work)} calls to make "
          f"(jury {[j['judge_id'] for j in judges]}, lanes {lanes}), "
          f"{len(done)} already done", flush=True)

    lock = threading.Lock()
    out = open(calls_path, "a", encoding="utf-8")

    def one(item):
        p, judge, order = item
        g = graphs[p["identity"]]
        mutant = regenerate_mutant(p["identity"], p["operator"], g["graph"],
                                   audit_summary["seed"])
        control = g["graph"]
        a, b = (control, mutant["graph"]) if order == "control-first" else (mutant["graph"], control)
        workspace = os.path.join(args.out, "workspace", p["pair_id"], judge["judge_id"], order)
        result = pj.judge_pair(judge, tasks[g["task_id"]], a, b, args.timeout, workspace)
        row = {"pair_id": p["pair_id"], "identity": p["identity"], "task_id": g["task_id"],
               "operator": p["operator"], "planner": p["planner"],
               "planner_class": planner_classes[p["planner"]], "size_probe": p["size_probe"],
               "judge": judge["judge_id"], "judge_class": judge["aliasing_class"],
               "judge_command_sha256": judge["command_sha256"], "order": order,
               "judge_profile": pj.JUDGE_PROFILE, "environment": ENVIRONMENT_VERSION,
               "mutant_anchor": mutant["anchor"], "mutant_description": mutant["description"],
               **result}
        with lock:
            out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            out.flush()
            print(f"  {p['operator']:<30} {judge['judge_id']:<28} {order:<13} "
                  f"-> {row['preferred']!s:<5} {row['seconds']:.0f}s "
                  f"{row['error'] or ''}", flush=True)

    # One executor per judge so a slow judge does not hold another's lanes.
    by_judge: dict[str, list] = {}
    for item in work:
        by_judge.setdefault(item[1]["judge_id"], []).append(item)
    threads = []
    for judge_id, items in by_judge.items():
        def run(items=items, n=lanes[judge_id]):
            with ThreadPoolExecutor(max_workers=n) as pool:
                list(pool.map(one, items))
        t = threading.Thread(target=run)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    out.close()

    # Resolve both orders into one verdict per (pair, judge) and summarize.
    calls = [json.loads(l) for l in open(calls_path, encoding="utf-8") if l.strip()]
    by_key: dict[tuple, dict] = {}
    for c in calls:
        by_key.setdefault((c["pair_id"], c["judge"]), {}).update({c["order"]: c})
    resolved = []
    for (pair_id, judge), orders in by_key.items():
        first = (orders.get("control-first") or {}).get("preferred")
        second = (orders.get("mutant-first") or {}).get("preferred")
        any_call = next(iter(orders.values()))
        resolved.append({"pair_id": pair_id, "judge": judge, "operator": any_call["operator"],
                         "planner": any_call["planner"], "size_probe": any_call["size_probe"],
                         "first": first, "second": second,
                         "resolved": pj.resolve_orders(first, second)})
    with open(os.path.join(args.out, "resolved.jsonl"), "w", encoding="utf-8") as f:
        for r in resolved:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    summary = {
        "judge_profile": pj.JUDGE_PROFILE, "environment": ENVIRONMENT_VERSION,
        "audit": os.path.basename(args.audit), "audit_seed": audit_summary["seed"],
        "oracle": audit_summary["oracle"], "registry_version": audit_summary["registry_version"],
        "seed": args.seed, "per_class": args.per_class, "pairs": len(pairs),
        "jury": [{"judge_id": j["judge_id"], "aliasing_class": j["aliasing_class"],
                  "command_sha256": j["command_sha256"], "command": j["command"]} for j in judges],
        "controls": "synthetic (sweep-produced graphs sound under the pinned oracle); "
                    "no production controls were available",
        "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "judges": pj.summarize(resolved),
    }
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(summary["judges"], indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
