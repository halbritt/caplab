#!/usr/bin/env python3
"""Per-binding review admission gate (instruction 2026-09-07 §2.d).

Pass/fail for one binding, never a ranking, never a claim. Runs only for a
new binding or a binding the Principal names; `--plan` spends nothing.

Cells, from advisory/gate/review-gate-20260819.json:
  1. the five natural-analog operators on the seed-20260819 draw (16 cells),
     under tree-v1 with the Stage B mount, 3 control replicates + 1 mutant;
  2. the natural case (cancellation 320479) verbatim, 3 replicates, rendered
     under the production review pass contract with the tree-v1 preamble
     and pinned-set statement, its declared base materialized read-only;
  3. contract conformance, checked mechanically on the natural-case outputs.

Usage:
  review_gate.py --plan <binding>
  review_gate.py --run  <binding> [--out advisory/pool-runs/gate-<binding>-<date>]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from caplab.advisory import materialize as M  # noqa: E402
from caplab.advisory import pool_runner  # noqa: E402
from caplab.advisory.calibrate import render_preamble_v3  # noqa: E402
from caplab.advisory.review_response import attempt_error, response_error  # noqa: E402

GATE = os.path.join(ROOT, "advisory", "gate", "review-gate-20260819.json")
BACKENDS = os.path.expanduser("~/git/striatum-next/backends")
REGISTRY = os.path.join(ROOT, "advisory", "substrates.jsonl")
VERDICTS = {"accept", "accept_with_findings", "needs_revision", "reject"}
REFUSING = {"needs_revision", "reject"}
DISCIPLINE = re.compile(r"D\d{4}|clause|falsif|violat|harm", re.I)


def load_gate() -> dict:
    with open(GATE, encoding="utf-8") as f:
        return json.load(f)


def plan(gate: dict) -> dict:
    cells = gate["cells"]
    rep = gate["replication"]
    calls = len(cells) * (rep["control"] + rep["mutant"]) + len(gate["natural_cases"]) * rep["natural_case"]
    return {"cells": len(cells), "operators": sorted({c["operator"] for c in cells}),
            "natural_cases": [n["id"] for n in gate["natural_cases"]],
            "replication": rep, "calls_per_binding": calls,
            "environment": gate["environment"], "floors": gate["floors"]}


def conformance(doc: dict | None) -> dict:
    out = {"parses": isinstance(doc, dict)}
    if not isinstance(doc, dict) or not doc:
        return {**out, "verdict_valid": False, "refusal_has_anchor": None, "rationales_disciplined": None, "ok": False}
    verdict = doc.get("verdict")
    findings = doc.get("findings")
    out["verdict_valid"] = isinstance(verdict, str) and verdict in VERDICTS
    if response_error(doc) is not None:
        return {**out, "refusal_has_anchor": False, "rationales_disciplined": False, "ok": False}
    out["refusal_has_anchor"] = (any(isinstance(f.get("element_anchor"), str)
                                     and f["element_anchor"].strip() for f in findings)
                                 if isinstance(verdict, str) and verdict in REFUSING else None)
    texts = [(f.get("rationale") or f.get("text") or "") for f in findings]
    out["rationales_disciplined"] = all(isinstance(t, str) and DISCIPLINE.search(t)
                                        for t in texts) if texts else None
    out["ok"] = bool(out["verdict_valid"] and out["refusal_has_anchor"] is not False
                     and out["rationales_disciplined"] is not False)
    return out


def observed_verdict(attempt: dict) -> str | None:
    """An output alone cannot establish a completed, contained observation."""
    if attempt.get("sandbox") == "bwrap" and attempt_error(attempt, require_manifest=True) is None:
        return attempt["doc"]["verdict"]
    return None


def summarize_cells(gate: dict, rows: list[dict], adj, sources: dict) -> dict:
    """Account for the planned population; report counts without adopting floors."""
    expected = {(c["substrate_id"], c["operator"]) for c in gate["cells"]}
    if len(expected) != len(gate["cells"]):
        raise ValueError("duplicate gate cell in specification")
    by_cell = {}
    for row in rows:
        key = (row.get("substrate_id"), row.get("defect_class"))
        if key not in expected or key in by_cell:
            raise ValueError(f"unexpected or duplicate gate cell: {key}")
        by_cell[key] = row
    result = {"cells_planned": len(expected), "cells_scorable": 0,
              "cells_missing": 0, "cells_not_applicable": 0, "cells_incomplete": 0,
              "missed": 0, "cell_observations": [],
              "controls_by_disposition": {d: {"expected": 0, "observed": 0,
                                                "refused": 0, "unavailable": 0}
                                          for d in ("sound", "defective", "unadjudicated")}}
    for substrate, operator in sorted(expected):
        row = by_cell.get((substrate, operator))
        cell = {"substrate_id": substrate, "operator": operator}
        if row is None:
            status = "missing"
            disposition = adj.disposition(sources.get(substrate) or substrate)
            counts = result["controls_by_disposition"][disposition]
            counts["expected"] += gate["replication"]["control"]
            counts["unavailable"] += gate["replication"]["control"]
            cell["control_disposition"] = disposition
        elif (not row.get("usable") and str(row.get("error", "")).startswith("not applicable:")
              and not row.get("control_attempts") and not row.get("mutant_attempts")):
            status = "not_applicable"
        else:
            if row.get("environment") not in (None, "tree-v1"):
                raise ValueError("gate observations require tree-v1")
            verdicts = {}
            for arm in ("control", "mutant"):
                attempts = row.get(f"{arm}_attempts", [])
                if len(attempts) > gate["replication"][arm]:
                    raise ValueError(f"excess {arm} attempts for {substrate}:{operator}")
                verdicts[arm] = [observed_verdict(a) if row.get("environment") == "tree-v1"
                                 else None for a in attempts]
                cell[f"{arm}_observed"] = sum(v is not None for v in verdicts[arm])
            disposition = adj.disposition(sources.get(substrate) or substrate)
            counts = result["controls_by_disposition"][disposition]
            counts["expected"] += gate["replication"]["control"]
            counts["observed"] += cell["control_observed"]
            counts["refused"] += sum(v in REFUSING for v in verdicts["control"])
            counts["unavailable"] += gate["replication"]["control"] - cell["control_observed"]
            cell["control_disposition"] = disposition
            complete = all(cell[f"{arm}_observed"] == gate["replication"][arm]
                           for arm in ("control", "mutant"))
            status = "scorable" if row.get("usable") and complete else "incomplete"
            if status == "scorable":
                result["missed"] += not any(v in REFUSING for v in verdicts["mutant"])
        result[f"cells_{status}"] += 1
        cell.update(status=status, error=row.get("error") if row else "no retained row")
        result["cell_observations"].append(cell)
    return result


def run_natural_case(nc: dict, adapter: dict, out_dir: str, timeout: int, replicates: int) -> dict:
    case_dir = os.path.join(out_dir, "workspace", nc["id"])
    os.makedirs(case_dir, exist_ok=True)
    record = {"substrate_id": nc["id"], "base_source": "partial-product-tree",
              "materializer": "product-object", "object": nc["pinned_base"]["object"], "evidence": []}
    manifest = M.materialize_case(record, case_dir)
    body = M.store_object(nc["change_set"]["content_hash"])
    if body is None:
        raise RuntimeError("natural case change set left the store")
    with open(os.path.join(ROOT, nc["contract"].split(" ")[0]), encoding="utf-8") as f:
        contract_text = f.read()
    prompt = (render_preamble_v3("partial-product-tree", manifest, case_dir)
              + "You are reviewing one change set under striatum's review pass contract, reproduced "
                "below verbatim. Respond with ONLY a JSON review-ledger object: "
                '{"posture": "adversarial", "verdict": ..., "findings": [{"id": "RV-001", "severity": ..., '
                '"element_anchor": ..., "rationale": ...}], "summary": ...}.\n\nPASS CONTRACT:\n'
              + contract_text + "\n\nCHANGE SET:\n" + body.decode("utf-8", errors="replace"))
    readonly = [os.path.join(case_dir, "base"), os.path.join(case_dir, "evidence")]
    runs = []
    for _ in range(replicates):
        before = M.verify_manifest(case_dir)
        r = pool_runner.invoke(adapter, prompt, timeout, workspace=case_dir, readonly=readonly)
        after = M.verify_manifest(case_dir)
        r["manifest_verified"] = before and after
        doc = r.get("doc")
        findings = doc.get("findings") if isinstance(doc, dict) else None
        anchors = [f["element_anchor"] for f in findings
                   if isinstance(f, dict) and isinstance(f.get("element_anchor"), str)] if isinstance(findings, list) else []
        verdict = observed_verdict(r)
        runs.append({**r, "verdict": doc.get("verdict") if isinstance(doc, dict) else None,
                     "observed": verdict is not None, "anchors": anchors,
                     "anchored_hit": any(nc["expected"]["anchored_finding"] in a for a in anchors),
                     "refused": verdict in REFUSING,
                     "conformance": conformance(doc), "seconds": r["seconds"], "exit_code": r["exit_code"],
                     "timed_out": r["timed_out"], "manifest_verified": before and after,
                     "raw_head": (r.get("raw_head") or "")[:300]})
    return {"id": nc["id"], "base_manifest_digest": manifest["digest"], "replicates": runs,
            "unavailable": sum(1 for r in runs if not r["observed"]),
            "refused_and_anchored": sum(1 for r in runs if r["refused"] and r["anchored_hit"]),
            "conforming": sum(1 for r in runs if r["observed"] and r["conformance"]["ok"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("binding")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    gate = load_gate()
    if args.plan:
        print(json.dumps({"binding": args.binding, **plan(gate)}, indent=1))
        return 0
    if not pool_runner.sandbox_available():
        print("the Stage B mount is the only environment a gate run may use; bwrap is unavailable", file=sys.stderr)
        return 2
    if not pool_runner.tree_mode():
        ap.error("gate runs require tree-v1")
    out_dir = args.out or os.path.join(ROOT, "advisory", "pool-runs",
                                       f"gate-{args.binding}-{_dt.date.today().strftime('%Y%m%d')}")
    os.makedirs(out_dir, exist_ok=False)
    cells_doc = {"selection": "admission-gate", "cells": gate["cells"]}
    cells_path = os.path.join(out_dir, "cells.json")
    with open(cells_path, "w", encoding="utf-8") as f:
        json.dump(cells_doc, f, indent=1)
    rep = gate["replication"]
    summary = pool_runner.run_pool(backend=args.binding, backends_root=BACKENDS, registry_path=REGISTRY,
                                   out_dir=out_dir, sweep_seed=20260819, per_operator=1, timeout=args.timeout,
                                   max_cases=len(gate["cells"]), anchor_path=None, workers=1,
                                   replicates=rep["control"], mutant_replicates=rep["mutant"],
                                   cases_path=cells_path)
    declaration = pool_runner.load_declaration(BACKENDS, args.binding)
    natural = ([{"id": nc["id"], "replicates": [], "unavailable": rep["natural_case"],
                 "refused_and_anchored": 0, "conforming": 0,
                 "error": f"pool aborted: {summary['aborted']}"} for nc in gate["natural_cases"]]
               if summary.get("aborted") else
               [run_natural_case(nc, declaration["adapter"], out_dir, args.timeout, rep["natural_case"])
                for nc in gate["natural_cases"]])
    with open(os.path.join(out_dir, "results.jsonl"), encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    with open(GATE, "rb") as f:
        gate_sha256 = hashlib.sha256(f.read()).hexdigest()
    from caplab.advisory.executor import advisory_control_context
    adj, sources = advisory_control_context(os.path.join(ROOT, "advisory", "control-adjudications.jsonl"))
    result = {
        "record": "caplab-review-admission-gate-result/2", "binding": args.binding,
        "gate_sha256": gate_sha256,
        "environment": summary.get("environment"), "as_of": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        **summarize_cells(gate, rows, adj, sources),
        "pool_aborted": summary.get("aborted"),
        "natural_cases": natural,
        "floors": gate["floors"],
        "note": "Observations only; floors proposed, not adopted. Control dispositions are recorded ledger labels, not proof of tree-v1 revalidation. No admission decision, ranking, or claim.",
    }
    with open(os.path.join(out_dir, "gate-result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    print(json.dumps({k: v for k, v in result.items() if k != "natural_cases"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
