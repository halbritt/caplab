#!/usr/bin/env python3
"""Step 1 of the review-instrument validation study (instruction 2026-09-07):
the criterion set from the striatum ledger, zero model spend.

Population: anchored-era production review runs (pass_id `review`, a
`materialized_base` input pin). Each run's verdict is read from its
review-ledger artifact (object store) and from the driver's review
gate_result; the two are reported side by side.

Strata are event predicates, reproducible here, never judgment:

  gold-defect   review cleared the artifact version (verdict accept or
                accept_with_findings, or review gate pass) AND a later
                Principal acceptance gate_result on the same artifact
                version has outcome fail.
  gold-clear    review refused the version (needs_revision/reject, or gate
                fail) AND a later Principal acceptance gate_result on the
                same version has outcome pass.
  silver-defect review cleared a change set AND a later integration_conflict
                names that change set as the losing pin with a conflict that
                is not "tree moved" (tree-moved is staleness of the base, a
                builder/timing event, reported separately and NOT counted),
                OR a later Principal cancellation_record on the request whose
                reason names a defect in that artifact.
  bronze-clear  review cleared a change set AND an application_record applied
                that change set AND no later acceptance fail, conflict, or
                cancellation names it.
  excluded      refused, then a later version of the same identity exists.

Usage: review_criterion_ledger_pass.py --ledger ledger.jsonl [--out advisory/criterion]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import statistics
import sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from caplab.advisory import materialize as M  # noqa: E402

CLEAR = {"accept", "accept_with_findings"}
REFUSE = {"needs_revision", "reject"}
DEFECT_WORDS = re.compile(r"defect|wrong|incorrect|false claim|fabricat|contradict|hollow|does not (deliver|implement|match)", re.I)


def T(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def artifact_class(identity: str) -> str:
    tail = identity.rsplit("/", 1)[-1]
    if tail == "change-set":
        return "change-set"
    return tail or "(unknown)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "advisory", "criterion"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    by = collections.defaultdict(list)
    with open(args.ledger, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                by[e["type"]].append(e)

    # --- population: anchored review runs
    runs = {}
    for e in by["pass_run_opened"]:
        p = e["payload"]; m = p.get("manifest") or {}
        pins = m.get("input_pins") or []
        if p.get("pass_id") != "review":
            continue
        mb = next((x["content_hash"] for x in pins if x.get("role") == "materialized_base"), None)
        if not mb:
            continue
        sp = m.get("subject_pin") or {}
        env = m.get("environment") or []
        contract = next((x["hash"] for x in env if x.get("kind") == "pass-contract"), None)
        runs[e["seq"]] = {
            "run": e["seq"], "opened": e["written_at"], "identity": sp.get("identity"),
            "content_hash": sp.get("content_hash"), "version_seq": sp.get("version_seq"),
            "class": artifact_class(sp.get("identity") or ""),
            "materialized_base": mb,
            "base_pin": next((x["content_hash"] for x in pins if x.get("role") == "base"), None),
            "contract_hash": contract, "contract_version": p.get("contract_version"),
            "prompt_assets": m.get("prompt_asset_hashes") or [],
            "request_ref": p.get("request_ref"),
        }
    closed = {e["payload"].get("run_ref"): e for e in by["pass_run_closed"]}
    lane = {e["payload"].get("run_ref"): e["payload"].get("backend_id") for e in by["lane_binding"]}
    sched = {e["payload"].get("run_ref"): e["payload"].get("backend_id") for e in by["scheduling_decision"]}
    for seq, r in runs.items():
        r["backend"] = lane.get(seq) or sched.get(seq) or "(unbound)"
        c = closed.get(seq)
        r["outcome"] = c["payload"].get("outcome") if c else None
        r["wall_s"] = (T(c["written_at"]) - T(r["opened"])).total_seconds() if c else None

    # --- verdicts: review-ledger bodies and review gate results
    for e in by["artifact_admitted"]:
        p = e["payload"]
        if p.get("kind") != "review-ledger" or p.get("produced_by_run") not in runs:
            continue
        body = p.get("body")
        doc = None
        if isinstance(body, dict) and body.get("content_hash"):
            raw = M.store_object(body["content_hash"])
            if raw:
                try:
                    doc = json.loads(raw)
                except ValueError:
                    doc = None
        r = runs[p["produced_by_run"]]
        r["review_artifact"] = p.get("identity")
        r["review_body_hash"] = (body or {}).get("content_hash") if isinstance(body, dict) else None
        if doc:
            r["verdict"] = doc.get("verdict")
            r["findings"] = [{"anchor": f.get("element_anchor") or f.get("anchor"), "text": (f.get("text") or f.get("finding") or "")[:300]}
                             for f in (doc.get("findings") or []) if isinstance(f, dict)]
            r["summary"] = (doc.get("summary") or "")[:400]
    for e in by["gate_result"]:
        p = e["payload"]
        if p.get("gate_class") != "review":
            continue
        for ev in p.get("evidence") or []:
            run = (ev.get("producing_run") or {}).get("run_ref")
            if run in runs:
                runs[run]["review_gate"] = p.get("outcome")
                runs[run]["review_gate_seq"] = e["seq"]

    def cleared(r):
        v = r.get("verdict")
        if v in CLEAR:
            return True
        if v in REFUSE:
            return False
        return {"pass": True, "fail": False}.get(r.get("review_gate"))

    # --- Principal acceptance rulings, by artifact version
    acceptance = collections.defaultdict(list)
    for e in by["gate_result"]:
        p = e["payload"]
        if p.get("gate_class") != "acceptance":
            continue
        if (p.get("authority") or {}).get("kind") != "principal":
            continue
        mat = (p.get("applicability") or {}).get("materialization") or {}
        acceptance[mat.get("content_hash")].append({"seq": e["seq"], "at": e["written_at"], "outcome": p.get("outcome"),
                                                    "detail": (p.get("detail") or "")[:600], "identity": mat.get("identity")})
    # --- integration conflicts and applications, by change-set hash
    conflicts = collections.defaultdict(list)
    for e in by["integration_conflict"]:
        p = e["payload"]
        h = (p.get("losing_change_set_pin") or {}).get("content_hash")
        d = p.get("detail") or ""
        kind = ("tree-moved" if "tree moved" in d else
                "anchored-delete-named-later-version" if "deletes over an anchored base" in d else
                "declares-vs-yields" if "declares" in d else
                "link-check" if p.get("conflict_class") == "link_check_failure" else "other")
        conflicts[h].append({"seq": e["seq"], "at": e["written_at"], "kind": kind, "detail": d[:300],
                             "conflicting_paths": p.get("conflicting_paths")})
    applied = collections.defaultdict(list)
    for e in by["application_record"]:
        p = e["payload"]
        applied[(p.get("change_set") or {}).get("content_hash")].append({"seq": e["seq"], "at": e["written_at"]})
    # --- Principal cancellations with defect wording, by request
    cancellations = collections.defaultdict(list)
    for e in by["cancellation_record"]:
        p = e["payload"]
        if (p.get("issuer") or {}).get("kind") != "principal":
            continue
        cancellations[p.get("request_ref")].append({"seq": e["seq"], "at": e["written_at"], "reason": (p.get("reason") or "")[:400],
                                                    "defect_words": bool(DEFECT_WORDS.search(p.get("reason") or ""))})
    # --- later versions of the same identity (revision)
    versions = collections.defaultdict(set)
    for r in runs.values():
        if r.get("identity") and r.get("version_seq") is not None:
            versions[r["identity"]].add(r["version_seq"])
    for e in by["head_movement"]:
        p = e["payload"]
        if p.get("identity") and p.get("to_version") is not None:
            versions[p["identity"]].add(p["to_version"])

    # --- strata
    strata = collections.defaultdict(list)
    tree_moved_after_clear = []
    for seq, r in sorted(runs.items()):
        c = cleared(r)
        r["cleared"] = c
        if c is None:
            strata["no-verdict"].append(r); continue
        later_acc = [a for a in acceptance.get(r["content_hash"], []) if a["at"] > r["opened"]]
        acc_fail = [a for a in later_acc if a["outcome"] == "fail"]
        acc_pass = [a for a in later_acc if a["outcome"] == "pass"]
        later_conf = [x for x in conflicts.get(r["content_hash"], []) if x["at"] > r["opened"]]
        real_conf = [x for x in later_conf if x["kind"] != "tree-moved"]
        moved = [x for x in later_conf if x["kind"] == "tree-moved"]
        later_app = [x for x in applied.get(r["content_hash"], []) if x["at"] > r["opened"]]
        canc = [x for x in cancellations.get(r["request_ref"], []) if x["at"] > r["opened"] and x["defect_words"]]
        later_versions = sorted(v for v in versions.get(r["identity"], set()) if r.get("version_seq") is not None and v > r["version_seq"])
        r["later"] = {"acceptance_fail": acc_fail, "acceptance_pass": acc_pass, "conflicts": real_conf,
                      "tree_moved": len(moved), "applied": later_app, "cancellations_with_defect_words": canc,
                      "later_versions": later_versions[:5]}
        if c and acc_fail:
            strata["gold-defect"].append(r)
        elif (not c) and acc_pass:
            strata["gold-clear"].append(r)
        elif c and (real_conf or canc):
            strata["silver-defect"].append(r)
        elif c and later_app and not acc_fail and not later_conf and not canc:
            strata["bronze-clear"].append(r)
        elif (not c) and later_versions:
            strata["excluded-refused-then-revised"].append(r)
        elif c and moved and not later_app:
            strata["unlabelled-cleared-tree-moved"].append(r); tree_moved_after_clear.append(r)
        elif c:
            strata["unlabelled-cleared-no-later-event"].append(r)
        else:
            strata["unlabelled-refused-no-later-event"].append(r)

    def table(rows, key):
        return dict(collections.Counter(key(r) for r in rows).most_common())
    report = {"population": len(runs), "strata": {}, "contracts": {}, "wall_clock_median_s": {}, "prompt_assets_retained": sum(1 for r in runs.values() if r["prompt_assets"]),
              "dispatch_dirs_retained": 0}
    for s, rows in strata.items():
        report["strata"][s] = {"n": len(rows),
                               "by_class": table(rows, lambda r: r["class"]),
                               "by_binding": table(rows, lambda r: r["backend"]),
                               "by_era": table(rows, lambda r: r["opened"][:7]),
                               "distinct_artifact_versions": len({(r["identity"], r["version_seq"]) for r in rows})}
    report["contracts"] = table(list(runs.values()), lambda r: f"{r['contract_hash']}@v{r['contract_version']}")
    wall = collections.defaultdict(list)
    for r in runs.values():
        if r.get("wall_s") and r.get("outcome") in ("submitted", "submitted_partial"):
            wall[r["backend"]].append(r["wall_s"])
    report["wall_clock_median_s"] = {b: {"median": round(statistics.median(v)), "n": len(v)} for b, v in sorted(wall.items()) if len(v) >= 5}
    report["verdict_sources"] = {"review_ledger_body": sum(1 for r in runs.values() if r.get("verdict")),
                                 "review_gate_only": sum(1 for r in runs.values() if not r.get("verdict") and r.get("review_gate")),
                                 "none": sum(1 for r in runs.values() if not r.get("verdict") and not r.get("review_gate"))}
    report["conflict_kinds_all"] = dict(collections.Counter(x["kind"] for v in conflicts.values() for x in v))
    report["principal_acceptance_rulings"] = {"total": sum(len(v) for v in acceptance.values()),
                                              "by_outcome": dict(collections.Counter(a["outcome"] for v in acceptance.values() for a in v)),
                                              "by_class": dict(collections.Counter(artifact_class(a["identity"] or "") for v in acceptance.values() for a in v))}
    with open(os.path.join(args.out, "review-criterion-summary.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "review-criterion-cases.jsonl"), "w", encoding="utf-8") as f:
        for s in ("gold-defect", "gold-clear", "silver-defect", "bronze-clear"):
            for r in strata.get(s, []):
                f.write(json.dumps({"stratum": s, **{k: v for k, v in r.items() if k != "prompt_assets"}}, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "wall_clock_median_s"}, indent=1)[:6000])
    print("wall clock", json.dumps(report["wall_clock_median_s"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
