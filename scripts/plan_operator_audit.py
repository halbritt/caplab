#!/usr/bin/env python3
"""Audit the plan-defect operators over real work graphs before anyone is scored.

Scar tissue 1 of the planning card, applied to Arm 2: the controls are
audited first, and so are the operators. For every candidate control this
script asks the pinned oracle whether the control is sound (every mechanical
check passes), then applies every operator to every sound control and
records, per operator:

- applicability (how many controls it bites on);
- checker discipline (the checker fires on the mutant and not the control);
- the oracle contract: the three oracle-visible classes must flip the
  verdict they owe, and the oracle-silent classes must leave parse, index
  and legality exactly as the control had them — a "silent" operator that
  trips the oracle is a defect in the operator, not in the plan.

Two control populations, kept apart because they are different things: the
production work graphs on the exchange (real accepted plans, the card's
controls) and the graphs the 20260827 planning sweep produced (synthetic,
one contract, eight planners — the material the pairwise ranking would judge).

Usage:
  plan_operator_audit.py --registry <checks.json> --oracle-dir <dir> [--out DIR]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from caplab.advisory import plan_operators as ops  # noqa: E402
from caplab.advisory.instrument_defects import NotApplicable  # noqa: E402
from caplab.advisory.planning_corpus import (extract_work_graph,  # noqa: E402
                                             oracle_identity, score_graph)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS = os.path.join(ROOT, "advisory", "pool-runs")
EXCHANGE = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")


def _mechanical(verdict: dict) -> tuple:
    return (bool((verdict.get("parse") or {}).get("ok")),
            bool((verdict.get("application_index") or {}).get("ok")),
            bool((verdict.get("legality") or {}).get("ok")))


def _sound(verdict: dict) -> bool:
    res = verdict.get("resolvability") or {}
    return all(_mechanical(verdict)) and res.get("status") == "checked" \
        and not res.get("unresolvable")


def production_graphs() -> list[dict]:
    subs = os.path.join(EXCHANGE, "spool", "submissions")
    seen, out = set(), []
    if not os.path.isdir(subs):
        return out
    for dispatch in sorted(os.listdir(subs)):
        path = os.path.join(subs, dispatch, "manifest.json")
        try:
            manifest = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for output in manifest.get("outputs", []):
            if output.get("kind") != "work-graph" or output.get("status") != "present":
                continue
            if output.get("identity") in seen:
                continue
            body_path = os.path.join(subs, dispatch, output.get("path", ""))
            if not os.path.isfile(body_path):
                continue
            seen.add(output.get("identity"))
            graph = extract_work_graph(open(body_path, encoding="utf-8",
                                            errors="replace").read())
            if graph is not None:
                out.append({"population": "production", "source": dispatch,
                            "identity": output.get("identity"), "graph": graph})
    return out


def sweep_graphs() -> list[dict]:
    out = []
    for path in sorted(glob.glob(os.path.join(RUNS, "plan-*-20260827", "results.jsonl"))):
        if "calibration" in path:
            continue
        for line in open(path, encoding="utf-8"):
            row = json.loads(line)
            if row.get("usable") and isinstance(row.get("graph"), dict):
                out.append({"population": "sweep", "source": row["subject"],
                            "identity": f"{row['subject']}/{row['task_id']}",
                            "graph": row["graph"]})
    return out


def audit(controls: list[dict], registry: str, seed: int) -> tuple[list, dict]:
    rows, summary = [], defaultdict(Counter)
    sound = []
    for c in controls:
        verdict = score_graph(c["graph"], registry_path=registry)
        c["sound"] = _sound(verdict)
        c["verdict"] = verdict
        summary[c["population"]]["controls"] += 1
        if c["sound"]:
            summary[c["population"]]["sound"] += 1
            sound.append(c)
    for c in sound:
        body = json.dumps(c["graph"], sort_keys=True)
        for op in ops.PLAN_OPERATORS:
            rng = random.Random(f"{seed}:{c['identity']}:{op.__name__}")
            key = (c["population"], op.__name__)
            try:
                inj = op(body, rng)
            except NotApplicable as e:
                rows.append({"identity": c["identity"], "population": c["population"],
                             "operator": op.__name__, "applied": False,
                             "reason": str(e)[:160]})
                summary[key]["not_applicable"] += 1
                continue
            mutant = json.loads(inj.body)
            mverdict = score_graph(mutant, registry_path=registry)
            present_m = ops.check_present(inj, inj.body)
            present_c = ops.check_present(inj, body)
            expect = ops.ORACLE_EXPECTATION[op.__name__]
            flip = ops.oracle_flip(c["verdict"], mverdict, op.__name__)
            silent_ok = (expect is not None) or \
                (_mechanical(mverdict) == _mechanical(c["verdict"]))
            row = {"identity": c["identity"], "population": c["population"],
                   "operator": op.__name__, "applied": True,
                   "anchor": inj.element_anchor,
                   "checker_mutant": present_m, "checker_control": present_c,
                   "oracle_expectation": expect, "oracle_flip": flip,
                   "silent_stays_legal": silent_ok,
                   "mutant_legality_failures": [f.get("class") for f in
                                                ((mverdict.get("legality") or {}).get("failures") or [])][:6],
                   "packets_control": len(c["graph"]["packets"]),
                   "packets_mutant": len(mutant["packets"])}
            row["admissible"] = bool(present_m and not present_c and silent_ok
                                     and (flip is None or flip))
            rows.append(row)
            summary[key]["applied"] += 1
            summary[key]["checker_ok"] += int(bool(present_m and not present_c))
            if expect is not None:
                summary[key]["oracle_flipped"] += int(bool(flip))
            else:
                summary[key]["stayed_legal"] += int(silent_ok)
            summary[key]["admissible"] += int(row["admissible"])
    return rows, {("%s|%s" % k if isinstance(k, tuple) else k): dict(v)
                  for k, v in summary.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--oracle-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260902)
    ap.add_argument("--out", default=os.path.join(RUNS, "plan-operators-audit-20260902"))
    args = ap.parse_args()
    os.environ["PATH"] = os.path.abspath(args.oracle_dir) + os.pathsep + os.environ["PATH"]
    ident = oracle_identity()
    controls = production_graphs() + sweep_graphs()
    rows, summary = audit(controls, os.path.abspath(args.registry), args.seed)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "audit.jsonl"), "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    doc = {"oracle": ident, "registry": os.path.abspath(args.registry),
           "registry_version": json.load(open(args.registry))["registry_version"],
           "seed": args.seed, "operators": [op.__name__ for op in ops.PLAN_OPERATORS],
           "oracle_expectation": ops.ORACLE_EXPECTATION,
           "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
           "summary": summary}
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(doc["summary"], indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
