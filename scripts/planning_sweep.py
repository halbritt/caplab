#!/usr/bin/env python3
"""Arm 1 of the planning constructs: the qualification sweep (P2b).

One subject plans each drawn task once, under the `plan-v2` contract, in the
`iso-v1` sandbox; `striatum-plan-oracle` scores the produced work graph and
the binary's sha256 rides every row.

What this measures, stated once so the record can repeat it: the corpus is
the `implementation-planning` pass (design -> prose plan, D2), while the
oracle mechanizes the `work-graph-legality` gate of `packetization`
(plan -> work graph, D1). No production lane performed the design-to-work-graph
composite `plan-v2` asks for, so there is no per-task production reference.
The production work graphs are scored separately as an oracle-calibration
population (`calibrate` below), never as per-task controls.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from caplab.advisory.planning_corpus import (  # noqa: E402
    PLANNING_PROFILE, extract_work_graph, normalize_graph, oracle_identity,
    render_task_prompt, resolvable_check_sets, sample_planning_tasks,
    score_graph, step_pass)
from caplab.advisory.pool_runner import (  # noqa: E402
    ENVIRONMENT_VERSION, declared_lanes, invoke, load_declaration)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TASKS = os.path.join(ROOT, "advisory", "planning-tasks.jsonl")
RUNS = os.path.join(ROOT, "advisory", "pool-runs")
BACKENDS = os.path.expanduser("~/git/striatum-next/backends")
REGISTRY = os.path.expanduser("~/git/striatum-next/policy/checks/repository.json")
EXCHANGE = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")

#: Design-only: the base blob is 98% of the corpus's bytes and a no-tools lane
#: could never read it anyway, so excluding it keeps lane subjects comparable.
#: The cost is named on every claim — the oracle runs without `-tree`, so its
#: write-scope and atomicity verdicts stay `tree-not-provided` and measure
#: nothing about the planner.
PROMPT_ENVIRONMENT = "design-only"


def load_tasks() -> list[dict]:
    with open(TASKS, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _verdict_flags(verdict: dict) -> dict:
    """The scored booleans, and the structure that keeps them honest.

    A plan emitting one trivial packet passes every mechanical check, so
    `structure` travels beside the rates always (fa-rewards-silence's
    planning analogue).
    """
    parse = (verdict.get("parse") or {}).get("ok")
    index = (verdict.get("application_index") or {}).get("ok")
    legality = (verdict.get("legality") or {}).get("ok")
    res = verdict.get("resolvability") or {}
    resolvable = (None if res.get("status") != "checked"
                  else not res.get("unresolvable"))
    structure = verdict.get("structure") or {}
    return {
        "parse_ok": parse,
        # The reason matters: a graph that fails to parse reports zero
        # packets, so a row's structure is meaningless without it and the
        # diagnosis would otherwise cost a re-spend.
        "parse_error": (verdict.get("parse") or {}).get("error"),
        "index_ok": index,
        "legality_ok": legality,
        "resolvability_status": res.get("status"),
        "resolvable_ok": resolvable,
        "unresolvable_checks": [u.get("check") for u in
                                (res.get("unresolvable") or [])][:12],
        "legality_failures": [f.get("class") for f in
                              ((verdict.get("legality") or {}).get("failures") or [])][:12],
        "all_checks_ok": bool(parse and index and legality and resolvable),
        "packets": structure.get("packets"),
        "max_depth": structure.get("max_depth"),
        "max_width": structure.get("max_width"),
        "depth_width_product": structure.get("depth_width_product"),
        "write_scope_status": (verdict.get("write_scope") or {}).get("status"),
        "atomicity_status": (verdict.get("atomicity") or {}).get("status"),
    }


def calibrate(out_dir: str) -> dict:
    """Score every production work graph on the exchange.

    Scar tissue 1, adapted: the analogue of auditing controls before scoring
    anyone. This population cannot be a per-task control (different pass,
    different inputs), but it establishes that the oracle discriminates at
    all, and it exposes registry drift — a graph authored against an older
    checks registry fails resolvability for reasons that are the
    instrument's, not the planner's.

    Deduplicated by output identity: 121 submissions collapse to 68
    identities and one identity alone carries 35 of them.
    """
    ident = oracle_identity()
    subs = os.path.join(EXCHANGE, "spool", "submissions")
    seen, rows = set(), []
    for dispatch in sorted(os.listdir(subs)):
        manifest_path = os.path.join(subs, dispatch, "manifest.json")
        if not os.path.isfile(manifest_path):
            continue
        try:
            manifest = json.load(open(manifest_path, encoding="utf-8"))
        except (ValueError, OSError):
            continue
        for output in manifest.get("outputs", []):
            if output.get("kind") != "work-graph" or output.get("status") != "present":
                continue
            identity = output.get("identity")
            if identity in seen:
                continue
            body_path = os.path.join(subs, dispatch, output.get("path", ""))
            if not os.path.isfile(body_path):
                continue
            seen.add(identity)
            with open(body_path, encoding="utf-8", errors="replace") as f:
                graph = extract_work_graph(f.read())
            if graph is None:
                rows.append({"identity": identity, "dispatch_id": dispatch,
                             "unparseable_body": True})
                continue
            verdict = score_graph(graph, registry_path=REGISTRY)
            rows.append({
                "identity": identity, "dispatch_id": dispatch,
                "production_backend": (manifest.get("attribution") or {}).get("backend_id"),
                **_verdict_flags(verdict),
            })
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "production-work-graphs.jsonl"), "w",
              encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    scored = [r for r in rows if not r.get("unparseable_body")]
    summary = {
        "population": "production work-graph submissions, deduplicated by output identity",
        "purpose": "oracle calibration, not per-task controls",
        "oracle": ident,
        "registry": REGISTRY,
        "n_identities": len(rows),
        "parse_ok": sum(1 for r in scored if r["parse_ok"]),
        "legality_ok": sum(1 for r in scored if r["legality_ok"]),
        "resolvable_ok": sum(1 for r in scored if r["resolvable_ok"]),
        "all_checks_ok": sum(1 for r in scored if r["all_checks_ok"]),
        "by_backend": {},
    }
    for row in scored:
        summary["by_backend"][row.get("production_backend")] = \
            summary["by_backend"].get(row.get("production_backend"), 0) + 1
    with open(os.path.join(out_dir, "calibration-summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    return summary


def run(subject: str, seed: int, n: int, timeout: int, workers: int,
        out_dir: str | None = None) -> dict:
    declaration = load_declaration(BACKENDS, subject)
    adapter = declaration["adapter"]
    ident = oracle_identity()
    check_sets = resolvable_check_sets(REGISTRY)
    if not check_sets:
        raise SystemExit("no check set resolves; refusing to render plan-v2")

    tasks = load_tasks()

    def eligible(task: dict) -> bool:
        # Budget is decided on the rendered prompt, never by truncating one.
        try:
            return render_task_prompt(task, check_sets=check_sets,
                                      include_base=False) is not None
        except ValueError:
            return False

    drawn = sample_planning_tasks(tasks, seed=seed, n=n, eligible=eligible)
    out_dir = out_dir or os.path.join(RUNS, f"plan-{subject}-{seed}")
    os.makedirs(out_dir, exist_ok=True)
    results_path = os.path.join(out_dir, "results.jsonl")
    done = set()
    if os.path.isfile(results_path):
        with open(results_path, encoding="utf-8") as f:
            done = {json.loads(line)["task_id"] for line in f if line.strip()}

    lanes = min(max(1, workers), declared_lanes(declaration))
    lock = threading.Lock()
    started_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
    print(f"{subject}: {len(drawn)} tasks, {lanes} lanes "
          f"(declaration permits {declared_lanes(declaration)}), "
          f"{len(check_sets)} resolvable check sets", flush=True)

    with open(results_path, "a", encoding="utf-8") as out:
        def one(indexed):
            index, task = indexed
            if task["task_id"] in done:
                return
            prompt = render_task_prompt(task, check_sets=check_sets,
                                        include_base=False)
            workspace = os.path.abspath(
                os.path.join(out_dir, "workspace", task["task_id"]))
            result = invoke(adapter, prompt, timeout, workspace=workspace)
            row = {
                "task_id": task["task_id"],
                "dispatch_id": task["dispatch_id"],
                "step_id": task.get("step_id"),
                "step_pass": step_pass(task),
                "step_kind": (task.get("step_id") or "?").split("/")[0],
                "production_backend": task.get("production_backend"),
                "production_outcome": task.get("production_outcome"),
                "subject": subject,
                "prompt_profile": PLANNING_PROFILE,
                "prompt_environment": PROMPT_ENVIRONMENT,
                "environment": ENVIRONMENT_VERSION,
                "oracle_sha256": ident["sha256"],
                "oracle_version": ident["version"],
                "registry_version": json.load(open(REGISTRY))["registry_version"],
                "prompt_bytes": result["prompt_bytes"],
                "seconds": result["seconds"],
                "exit_code": result["exit_code"],
                "timed_out": result["timed_out"],
                "sandbox": result["sandbox"],
                "transport": result["transport"],
                "invoke_error": result["error"],
            }
            graph = result["doc"] if isinstance(result["doc"], dict) else None
            if graph is not None and "packets" not in graph and "plan" not in graph:
                graph = None
            if graph is None:
                row.update({"usable": False,
                            "error": "no parseable work graph",
                            "raw_head": result["raw_head"]})
            else:
                # The plan pin is driver bookkeeping a subject cannot know;
                # normalization is stamped on every scored row.
                normalized = normalize_graph(graph, task)
                verdict = score_graph(normalized, registry_path=REGISTRY)
                if verdict.get("oracle_failed"):
                    row.update({"usable": False,
                                "error": "oracle failed: " + verdict["oracle_failed"]})
                else:
                    row.update({"usable": True, "error": None,
                                "normalized": True,
                                "graph": normalized,
                                **_verdict_flags(verdict)})
            with lock:
                out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                out.flush()
                os.fsync(out.fileno())
                print(f"[{index}/{len(drawn)}] {task['task_id']:22} "
                      f"{'ok ' if row.get('usable') else row.get('error', '')[:34]:36}"
                      f"{'PASS' if row.get('all_checks_ok') else ''}"
                      f" packets={row.get('packets')} dxw={row.get('depth_width_product')}",
                      flush=True)

        if lanes > 1:
            with ThreadPoolExecutor(max_workers=lanes) as pool:
                list(pool.map(one, enumerate(drawn, 1)))
        else:
            for indexed in enumerate(drawn, 1):
                one(indexed)

    with open(results_path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    usable = [r for r in rows if r.get("usable")]
    summary = {
        "subject": subject,
        "construct": "planning.finishability/1",
        "prompt_profile": PLANNING_PROFILE,
        "prompt_environment": PROMPT_ENVIRONMENT,
        "environment": ENVIRONMENT_VERSION,
        "oracle": ident,
        "registry": REGISTRY,
        "check_sets_offered": len(check_sets),
        "seed": seed,
        "drawn": len(drawn),
        "passes_drawn": len({r["step_pass"] for r in rows}),
        "usable": len(usable),
        "discarded": len(rows) - len(usable),
        "parse_ok": sum(1 for r in usable if r["parse_ok"]),
        "legality_ok": sum(1 for r in usable if r["legality_ok"]),
        "resolvable_ok": sum(1 for r in usable if r["resolvable_ok"]),
        "all_checks_ok": sum(1 for r in usable if r["all_checks_ok"]),
        "started_at": started_at,
        "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    return summary


PLANNING_FINISHABILITY = "planning.finishability/1"


def _median(values: list) -> float | None:
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    return float(vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2)


def build_claims(run_dirs: list[str], as_of: str) -> list[dict]:
    """One planning.finishability/1 claim per subject.

    Structure travels beside every rate. A plan emitting one trivial packet
    clears every mechanical check, so a pass rate without the packet count
    and the depth-by-width product beside it can be read as competence when
    it is degeneracy (fa-rewards-silence, in planning's dialect).
    """
    from caplab.advisory.claims import build_claim
    from caplab.advisory.wilson import wilson

    claims = []
    for run_dir in run_dirs:
        with open(os.path.join(run_dir, "summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        with open(os.path.join(run_dir, "results.jsonl"), encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        usable = [r for r in rows if r.get("usable")]
        if not usable:
            continue
        n = len(usable)
        metrics = {}
        for name, ok in (("finishability_pass_rate",
                          lambda r: r["all_checks_ok"]),
                         ("legality_pass_rate",
                          lambda r: bool(r["parse_ok"] and r["index_ok"]
                                         and r["legality_ok"])),
                         ("resolvability_pass_rate",
                          lambda r: bool(r["resolvable_ok"]))):
            hits = sum(1 for r in usable if ok(r))
            lo, hi = wilson(hits, n)
            metrics[name] = {"value": hits / n, "denominator": n,
                             "ci95": [lo, hi]}
        # Production yield: a task the subject never produced a graph for is
        # not a passing task, and hiding it in the denominator of nothing
        # would let a subject that answers twice score like one that answers
        # every time.
        attempted = len(rows)
        lo, hi = wilson(n, attempted)
        metrics["graph_yield_rate"] = {"value": n / attempted,
                                       "denominator": attempted,
                                       "ci95": [lo, hi]}
        metrics["n_pairs"] = {"value": n}
        # Structure is read over graphs that parsed. The oracle reports zero
        # packets for a graph it could not parse, so including those counts a
        # parse failure as a zero-packet plan and drags the median down —
        # two different defects wearing one number.
        structural = [r for r in usable if r.get("parse_ok")]
        metrics["median_packets"] = {
            "value": _median([r.get("packets") for r in structural]),
            "denominator": len(structural)}
        metrics["median_depth_width_product"] = {
            "value": _median([r.get("depth_width_product") for r in structural]),
            "denominator": len(structural)}
        claims.append(build_claim(
            subject_source_id=summary["subject"],
            subject_matched=True,
            construct=PLANNING_FINISHABILITY,
            custody="caplab-advisory",
            as_of=as_of,
            metrics=metrics,
            evidence=[{
                "kind": "caplab-planning-sweep",
                "run_root": os.path.basename(run_dir),
                "prompt_profile": summary["prompt_profile"],
                "prompt_environment": summary["prompt_environment"],
                "environment": summary["environment"],
                "oracle_sha256": summary["oracle"]["sha256"],
                "oracle_version": summary["oracle"]["version"],
                "registry_version": usable[0].get("registry_version"),
                "check_sets_offered": summary["check_sets_offered"],
                "seed": summary["seed"],
                "tasks_drawn": summary["drawn"],
                "passes_drawn": summary["passes_drawn"],
            }],
            notes=[
                "caplab-advisory custody: CAPLAB drew the tasks, rendered the "
                f"{summary['prompt_profile']} contract, invoked the subject "
                f"through its declared adapter under {summary['environment']}, "
                "and scored the produced work graph with striatum-plan-oracle. "
                "No model judgment is in the labelling loop.",
                "SYNTHETIC COMPOSITE: the corpus is the implementation-planning "
                "pass (design -> prose plan, D2) while the oracle mechanizes the "
                "work-graph-legality gate of packetization (plan -> work graph, "
                "D1). No production lane performed this design-to-work-graph "
                "task, so no per-task production reference exists and these "
                "numbers are not comparable to production plan-review rates.",
                f"{summary['prompt_environment']} environment: the base tree is "
                "withheld, so the oracle runs without -tree and its write-scope "
                "and atomicity verdicts are 'tree-not-provided' — they measure "
                "nothing about the planner and are excluded from every rate.",
                "The draw is seeded and pass-disjoint (one task per step pass, "
                "balanced across produce/revise); selection never reads "
                "production outcome.",
                "Resolvability is scored against the 42 registry check sets "
                "verified resolvable by the oracle at sweep time and listed in "
                "the prompt; a subject naming anything else is naming a gate "
                "the plan does not have.",
                "Report structure beside the rates: median_packets and "
                "median_depth_width_product are on the claim because a "
                "single-trivial-packet plan clears every mechanical check.",
                "NOT COMPARABLE to planning.independent_acceptance/1's "
                "finishability_pass_rate despite the shared word. That metric "
                "is striatum's implementation-plan-finishability gate, applied "
                "by independent-family model review to the prose plan; this one "
                "is mechanical work-graph legality with no model in the "
                "labelling loop. A subject may sit high here and low there "
                "without either number being wrong.",
            ]))
    return claims


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--subject")
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out-dir")
    ap.add_argument("--calibrate", action="store_true",
                    help="score the production work graphs and exit")
    ap.add_argument("--claims", nargs="+", metavar="RUN_DIR",
                    help="build planning.finishability/1 claims from run roots")
    ap.add_argument("--as-of")
    ap.add_argument("--append", action="store_true",
                    help="append the built claims to advisory/claims.jsonl")
    args = ap.parse_args()
    if args.claims:
        from caplab.advisory.claims import Ledger
        as_of = args.as_of or _dt.datetime.now(_dt.timezone.utc).isoformat()
        built = build_claims(args.claims, as_of)
        print(json.dumps(built, indent=2, sort_keys=True))
        if args.append:
            print(json.dumps(Ledger(
                os.path.join(ROOT, "advisory", "claims.jsonl")).append(built)))
        return
    if args.calibrate:
        out = args.out_dir or os.path.join(RUNS, "plan-calibration-20260827")
        print(json.dumps(calibrate(out), indent=2, sort_keys=True))
        return
    if not args.subject:
        ap.error("--subject is required unless --calibrate")
    print(json.dumps(run(args.subject, args.seed, args.n, args.timeout,
                         args.workers, args.out_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
