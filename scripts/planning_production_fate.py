#!/usr/bin/env python3
"""Per-producer planning fate from striatum's own ledger (a covariate, not a claim).

Council disposition 2026-09-04 §3.3: striatum already records what happened
to every packet, so a planner's downstream fate is observable at zero spend.
This script attributes each production plan to the binding that produced it
and follows the pass forward: the plan's own gates
(`implementation-plan-finishability`, `-review`, `-acceptance`), the work
graph's legality gate, and the packets' `packet-checks` and `packet-review`
outcomes under that pass prefix.

Two firewalls, both from the ubiquitous language:

- **Downstream fate is a covariate.** It is scheduler-routed (each producer
  planned different tasks, and different builders built its packets), so it
  is never an evidence basis for a qualification claim. It can inform an
  advisory routing objective and a regression alarm.
- **Attribution is by pass prefix, not by causal chain.** A packet under
  `striatum-next/passes/<pass>/packets/...` is attributed to the producer of
  the latest accepted implementation plan for `<pass>` before the packet's
  gate fired. A pass re-planned by a second producer mid-flight splits its
  packets at the re-plan seq. Where no accepted plan precedes a packet, the
  packet is counted under `unattributed`.

Usage:
  planning_production_fate.py --ledger ledger.jsonl [--out DIR]
"""

from __future__ import annotations

import argparse
import collections
import datetime as _dt
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLAN_GATES = ("implementation-plan-finishability", "implementation-plan-review",
              "implementation-plan-acceptance")
PACKET_GATES = ("packet-checks", "packet-review")
_PASS = re.compile(r"^(?P<prefix>.+?/passes/[^/]+)(?:/|$)")


def pass_prefix(identity: str | None) -> str | None:
    if not identity:
        return None
    m = _PASS.match(identity)
    return m.group("prefix") if m else None


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def analyze(events: list[dict]) -> dict:
    # 1. Producers of implementation plans, by content hash, with seq.
    plans: dict[str, dict] = {}
    for e in events:
        p = e.get("payload") or {}
        if e.get("type") == "artifact_admitted" and p.get("kind") == "implementation-plan":
            plans[p["content_hash"]] = {
                "seq": e["seq"], "identity": p.get("identity"),
                "prefix": pass_prefix(p.get("identity")),
                "producer": (p.get("attribution") or {}).get("backend_id") or "unknown"}
    # 2. Which plans became accepted heads, and when.
    accepted_at: dict[str, int] = {}
    for e in events:
        if e.get("type") != "head_movement":
            continue
        cand = ((e.get("payload") or {}).get("effect") or {}).get("candidate") or {}
        h = cand.get("content_hash")
        if h in plans and h not in accepted_at:
            accepted_at[h] = e["seq"]
    # per pass prefix: sorted list of (accepted_seq, producer, hash)
    heads: dict[str, list[tuple[int, str, str]]] = collections.defaultdict(list)
    for h, seq in accepted_at.items():
        heads[plans[h]["prefix"]].append((seq, plans[h]["producer"], h))
    for v in heads.values():
        v.sort()

    def producer_for(prefix: str | None, at_seq: int) -> str:
        if prefix is None or prefix not in heads:
            return "unattributed"
        current = "unattributed"
        for seq, producer, _ in heads[prefix]:
            if seq <= at_seq:
                current = producer
            else:
                break
        return current

    # 3. Gate outcomes.
    plan_gates = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    packet_gates = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    packet_first_pass = collections.defaultdict(lambda: collections.Counter())
    seen_packet_check: dict[tuple, str] = {}
    for e in events:
        if e.get("type") != "gate_result":
            continue
        p = e.get("payload") or {}
        gate, outcome = p.get("gate_id"), p.get("outcome")
        subject = p.get("subject") or {}
        identity, h = subject.get("identity"), subject.get("content_hash")
        if gate in PLAN_GATES:
            producer = plans.get(h, {}).get("producer") or producer_for(pass_prefix(identity), e["seq"])
            plan_gates[producer][gate][outcome] += 1
        elif gate in PACKET_GATES:
            producer = producer_for(pass_prefix(identity), e["seq"])
            packet_gates[producer][gate][outcome] += 1
            if gate == "packet-checks":
                # First result per packet identity is the first-pass outcome.
                key = (producer, identity)
                if key not in seen_packet_check:
                    seen_packet_check[key] = outcome
                    packet_first_pass[producer][outcome] += 1
    quarantines = collections.Counter()
    for e in events:
        if e.get("type") == "packet_quarantine":
            p = e.get("payload") or {}
            identity = (p.get("packet") or {}).get("identity") or p.get("identity")
            quarantines[producer_for(pass_prefix(identity), e["seq"])] += 1

    producers = sorted(set(plan_gates) | set(packet_gates) | set(quarantines))
    out = {}
    for producer in producers:
        pg = plan_gates.get(producer, {})
        kg = packet_gates.get(producer, {})
        fp = packet_first_pass.get(producer, collections.Counter())
        fp_n = sum(fp.values())
        pc = kg.get("packet-checks", collections.Counter())
        pr = kg.get("packet-review", collections.Counter())
        out[producer] = {
            "plans_produced": sum(1 for v in plans.values() if v["producer"] == producer),
            "plans_accepted": sum(1 for h in accepted_at if plans[h]["producer"] == producer),
            "plan_gates": {g: dict(pg.get(g, {})) for g in PLAN_GATES},
            "packets_first_pass": {"n": fp_n, "pass": fp.get("pass", 0),
                                   "rate": (fp.get("pass", 0) / fp_n) if fp_n else None},
            # packet-checks fires on every re-evaluation of a packet, not only
            # on rebuilds, so results-per-packet is churn, not rework. Reported
            # under that name until a rebuild-only count exists.
            "packet_checks_all_results": {"pass": pc.get("pass", 0), "fail": pc.get("fail", 0),
                                          "results_per_packet": ((pc.get("pass", 0) + pc.get("fail", 0)) / fp_n)
                                          if fp_n else None},
            "packet_review": {"pass": pr.get("pass", 0), "fail": pr.get("fail", 0),
                              "fail_rate": (pr.get("fail", 0) / (pr.get("pass", 0) + pr.get("fail", 0)))
                              if (pr.get("pass", 0) + pr.get("fail", 0)) else None},
            "packet_quarantines": quarantines.get(producer, 0),
        }
    return {"producers": out, "plans_total": len(plans), "plans_accepted_total": len(accepted_at),
            "passes_with_accepted_plan": len(heads)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", required=True, help="a `striatum -json ledger cat` dump")
    ap.add_argument("--out", default=os.path.join(ROOT, "advisory", "pool-runs",
                                                  "planning-production-fate-20260904"))
    args = ap.parse_args()
    events = load(args.ledger)
    result = analyze(events)
    result.update({"ledger_events": len(events),
                   "label_class": "downstream fate (covariate; scheduler-routed; not a claim basis)",
                   "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat()})
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"{'producer':<28}{'plans':>6}{'acc':>5}{'fin p/f':>10}{'rev p/f':>10}{'acc p/f':>10}"
          f"{'pkts':>6}{'1st-pass':>9}{'chk/pkt':>8}{'prv fail':>9}{'quar':>5}")
    for producer, r in sorted(result["producers"].items(),
                              key=lambda kv: -kv[1]["packets_first_pass"]["n"]):
        g = r["plan_gates"]
        def pf(name):
            c = g[name]
            return f"{c.get('pass', 0)}/{c.get('fail', 0)}"
        fp = r["packets_first_pass"]
        print(f"{producer:<28}{r['plans_produced']:>6}{r['plans_accepted']:>5}"
              f"{pf('implementation-plan-finishability'):>10}{pf('implementation-plan-review'):>10}"
              f"{pf('implementation-plan-acceptance'):>10}{fp['n']:>6}"
              f"{(fp['rate'] if fp['rate'] is not None else float('nan')):>9.2f}"
              f"{(r['packet_checks_all_results']['results_per_packet'] or float('nan')):>8.2f}"
              f"{(r['packet_review']['fail_rate'] if r['packet_review']['fail_rate'] is not None else float('nan')):>9.2f}"
              f"{r['packet_quarantines']:>5}")


if __name__ == "__main__":
    main()
