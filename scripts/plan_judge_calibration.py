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


RECOVERED = os.path.join(RUNS, "production-work-graphs-20260903", "graphs.jsonl")


def load_graphs() -> dict[str, dict]:
    """audit identity -> {graph, task_id | pass_prefix} for every control the
    audit could have drawn from: the sweep graphs and the recovered
    production graphs, keyed exactly as the audit keys them."""
    out = {}
    for path in sorted(glob.glob(os.path.join(RUNS, "plan-*-20260827", "results.jsonl"))):
        if "calibration" in path:
            continue
        for line in open(path, encoding="utf-8"):
            row = json.loads(line)
            if row.get("usable") and isinstance(row.get("graph"), dict):
                out[f"{row['subject']}/{row['task_id']}"] = {
                    "graph": row["graph"], "task_id": row["task_id"]}
    if os.path.isfile(RECOVERED):
        for line in open(RECOVERED, encoding="utf-8"):
            row = json.loads(line)
            out[f"{row['identity']}@{row['content_hash'][:12]}"] = {
                "graph": row["graph"], "task_id": None,
                "pass_prefix": row["identity"].rsplit("/work-graph", 1)[0]}
    return out


def context_task(entry: dict, tasks: dict[str, dict]) -> dict | None:
    """The planning task whose design a judge reads beside this graph.

    A sweep graph answers one task. A production work graph was lowered
    from that pass's accepted plan, and the implementation-planning task of
    the same pass carries the accepted design as its input — the latest
    such task is used. No task, no context, no pair."""
    if entry.get("task_id"):
        return tasks.get(entry["task_id"])
    prefix = entry.get("pass_prefix")
    if not prefix:
        return None
    candidates = [t for t in tasks.values()
                  if (t.get("step_id") or "").split("/implementation-plan")[0]
                  .removeprefix("produce/").removeprefix("revise/") == prefix]
    if not candidates:
        return None
    return max(candidates, key=lambda t: t.get("run_ref") or 0)


def planner_class_of(pair_planner: str, declared: str | None) -> str | None:
    """A production graph carries its class from attribution; a sweep graph's
    planner is a declared backend. `local` is deterministic lowering with no
    model family, so every judge is independent of it."""
    if declared:
        return declared
    if pair_planner in (None, "local"):
        return None
    path = os.path.join(BACKENDS, pair_planner, "backend.yaml")
    return pj.planner_class(BACKENDS, pair_planner) if os.path.isfile(path) else None


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
    ap.add_argument("--populations", nargs="+",
                    default=["sweep", "production-accepted"],
                    help="audit populations to draw controls from")
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

    audit_rows = [r for r in audit_rows if r.get("population") in args.populations]
    for r in audit_rows:                       # the audit carries the planner
        r["planner"] = r.get("planner") or r["identity"].split("/", 1)[0]
    pairs = pj.sample_pairs(audit_rows, per_class=args.per_class, seed=args.seed)
    declared = {r["identity"]: r.get("planner_class") for r in audit_rows}
    for p in pairs:
        p["planner"] = next(r["planner"] for r in audit_rows
                            if r["identity"] == p["identity"])
    # A pair without a design context cannot be judged; drop it before counting.
    pairs = [p for p in pairs if context_task(graphs[p["identity"]], tasks) is not None]
    if args.smoke:
        pairs = pairs[:args.smoke]
    planner_classes = {}
    for p in pairs:
        planner_classes.setdefault(
            p["planner"], planner_class_of(p["planner"], declared.get(p["identity"])))

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
        task = context_task(g, tasks)
        result = pj.judge_pair(judge, task, a, b, args.timeout, workspace)
        row = {"pair_id": p["pair_id"], "identity": p["identity"], "task_id": task.get("task_id"),
               "population": next(r["population"] for r in audit_rows
                                  if r["identity"] == p["identity"]),
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
        "populations": args.populations,
        "controls": "sweep-produced graphs (synthetic) and recovered production work "
                    "graphs that became accepted heads, each sound under the pinned oracle",
        "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "judges": pj.summarize(resolved),
    }
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(summary["judges"], indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
