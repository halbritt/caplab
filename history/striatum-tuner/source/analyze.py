#!/usr/bin/env python3
"""Verdict-vs-fate analysis: how often did each backend's review verdict agree
with what actually happened to the reviewed candidate?

Fate of a reviewed candidate (identity, content_hash), from the ledger's
artifact_admitted stream:
  - "revised":  a later admission of the same identity carries different
                content — the candidate was superseded.
  - "final":    the candidate is the last admitted content for its identity.
  - "unknown":  the identity never admitted (candidate refused pre-admission,
                or an evidence-only subject).

A verdict "agrees" with fate when accept/accept_with_findings met "final" or
needs_revision/reject met "revised". This is a coarse ground truth (a later
revision can exist for reasons other than review findings, e.g. tree-moved
rebuilds), but it is computed identically for every backend, so it ranks them
fairly — including the incumbent local-qwen against the frontier lanes.

Writes analysis.json (fate per corpus record + per-backend table).
"""

from __future__ import annotations

import argparse
import collections
import json

ACCEPTING = {"accept", "accept_with_findings"}
REFUSING = {"needs_revision", "reject", "revise"}


def load_admissions(ledger_path: str):
    """identity -> [(ledger_seq, content_hash)] in admission order."""
    admitted = collections.defaultdict(list)
    with open(ledger_path) as f:
        for line in f:
            r = json.loads(line)
            if r["type"] != "artifact_admitted":
                continue
            p = r["payload"]
            if p.get("identity") and p.get("content_hash"):
                admitted[p["identity"]].append((r["seq"], p["content_hash"]))
    return admitted


def candidate_fate(admitted, identity: str, content_hash: str) -> str:
    versions = admitted.get(identity)
    if not versions:
        return "unknown"
    hashes = [h for _, h in versions]
    if content_hash not in hashes:
        # Reviewed pre-admission and never admitted under this content.
        # If anything was admitted after, the candidate did not survive.
        return "revised" if hashes else "unknown"
    last_idx = max(i for i, h in enumerate(hashes) if h == content_hash)
    later = set(hashes[last_idx + 1:]) - {content_hash}
    return "revised" if later else "final"


def review_verdict(record) -> str | None:
    out = record["outputs"].get("review-ledger")
    if not out:
        return None
    try:
        doc = json.loads(out["body"])
    except json.JSONDecodeError:
        return None
    return doc.get("verdict") if isinstance(doc, dict) else None


def primary_input(record):
    """The reviewed candidate: the first non-diagnostic pinned input that is
    not base/work-graph staging."""
    for i in record.get("inputs") or []:
        path = i.get("path") or ""
        name = path.split("/", 1)[-1]
        if name.startswith(("90-", "91-", "9")) and "diagnostic" in name:
            continue
        if name in ("00-base-pin", "01-base") or name.startswith("02-work-graph"):
            continue
        return i
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus/corpus.jsonl")
    ap.add_argument("--ledger-jsonl", required=True)
    ap.add_argument("--out", default="corpus/analysis.json")
    args = ap.parse_args()

    admitted = load_admissions(args.ledger_jsonl)

    per_backend = collections.defaultdict(collections.Counter)
    rows = []
    with open(args.corpus) as f:
        for line in f:
            r = json.loads(line)
            if r["pass"] != "review":
                continue
            verdict = review_verdict(r)
            pin = primary_input(r)
            if not verdict or not pin or not pin.get("content_hash"):
                continue
            fate = candidate_fate(admitted, pin["identity"], pin["content_hash"])
            agree = None
            if fate == "final":
                agree = verdict in ACCEPTING
            elif fate == "revised":
                agree = verdict in REFUSING
            rows.append({
                "dispatch_id": r["dispatch_id"],
                "backend_id": r["backend_id"],
                "written_at": r["written_at"],
                "candidate_identity": pin["identity"],
                "candidate_hash": pin["content_hash"],
                "verdict": verdict,
                "fate": fate,
                "agrees_with_fate": agree,
                "admitted": r["labels"]["admitted"],
            })
            b = per_backend[r["backend_id"]]
            b["n"] += 1
            b[f"fate:{fate}"] += 1
            if agree is not None:
                b["scored"] += 1
                if agree:
                    b["agree"] += 1

    table = []
    for backend, c in sorted(per_backend.items(), key=lambda kv: -kv[1]["n"]):
        scored = c["scored"]
        table.append({
            "backend": backend,
            "reviews": c["n"],
            "scored": scored,
            "fate_agreement": round(c["agree"] / scored, 3) if scored else None,
        })

    with open(args.out, "w") as f:
        json.dump({"per_backend": table, "reviews": rows}, f, indent=2)

    print(f"{'backend':38} {'reviews':>7} {'scored':>7} {'agree':>7}")
    for t in table:
        fa = f"{t['fate_agreement']:.1%}" if t["fate_agreement"] is not None else "-"
        print(f"{t['backend']:38} {t['reviews']:>7} {t['scored']:>7} {fa:>7}")


if __name__ == "__main__":
    main()
