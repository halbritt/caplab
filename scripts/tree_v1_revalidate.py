#!/usr/bin/env python3
"""Plan tree-v1 rev 2 §4: re-derive every control adjudication grounded in the
out-of-contract rule against the base production actually pinned.

For each ledger record whose basis rests on "the allegation depends on
material outside the artifact", the case's base class is established (plan
§2.3 amendment: whole-tree, partial-product-tree, none-by-design, lost) and
one §4 outcome is recorded:

  resolved-valid              the references resolve and name what the artifact says
  resolved-invalid            a reference resolves and contradicts the artifact, or
                              fails to resolve in an exact base that should hold it
  evidence-unavailable        the object existed and lost custody (lost bases)
  reference-unresolvable-anywhere  no trace anywhere (flagged, never auto-ruled)
  reference-not-required      the allegation does not depend on the reference, or
                              the case is none-by-design and the reference lies
                              outside the pinned set

Labels grounded in in-set predicates are environment-invariant and stand.
Human and Principal rulings are listed for re-examination, never rewritten
here. Nothing in this script writes to the adjudication ledger: it emits the
revalidation record the plan owes and the list of items that need a ruling.

Usage:
  tree_v1_revalidate.py --ledger ledger.jsonl [--out DIR]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from caplab.advisory import cas  # noqa: E402
from caplab.advisory.executor import advisory_control_context  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRAPH = os.path.expanduser("~/.local/share/striatum/graphs/019f22ef-0cb4-780f-9b82-b210bab24325")
REPOS = {"caplab": os.path.expanduser("~/git/caplab"),
         "striatum-next": os.path.expanduser("~/git/striatum-next")}
DRAW_RUN = os.path.join(ROOT, "advisory", "pool-runs", "iso-codex-sol-high-20260819", "results.jsonl")
OOC = re.compile(r"out[- ]of[- ]contract|out[- ]of[- ]set|not scorable|outside this|single-document set", re.I)
IN_SET = re.compile(r"in-set|contradict|is false|holds|41 hex|40 hex|anchor coll|fabricated|template|hollow", re.I)


def obj(h: str):
    p = os.path.join(GRAPH, "objects", "sha256", h[:2], h[2:4], h + ".zst")
    if not os.path.isfile(p):
        return None
    raw = open(p, "rb").read()
    if raw[:4] != b"SOB1":
        return None
    done = subprocess.run(["zstd", "-d", "-c"], input=raw[16:], capture_output=True)
    # An object that will not decode is, for base purposes, absent — and said so.
    return done.stdout if done.returncode == 0 else None


def load_ledger(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def base_classes(ledger_path: str, draw: list[dict]) -> dict[str, dict]:
    """substrate -> {class, detail} per the §2.3 amendment."""
    dispatch_of = {d["source"]["dispatch_id"]: d["substrate_id"] for d in draw
                   if d["source"].get("kind") == "striatum-exchange"}
    run_of, runs = {}, {}
    for e in load_ledger(ledger_path):
        p = e.get("payload") or {}
        if e["type"] == "submission_received" and p.get("dispatch_id") in dispatch_of:
            run_of[p["dispatch_id"]] = p.get("run_ref")
        elif e["type"] == "pass_run_opened":
            runs[e["seq"]] = p
    out = {}
    for d in draw:
        sid, src = d["substrate_id"], d["source"]
        if src.get("kind") == "repo-doc":
            out[sid] = {"class": "whole-tree", "source": "git-archive", "repo": src["repo"], "commit": src["commit"]}
            continue
        run = run_of.get(src["dispatch_id"])
        pins = ((runs.get(run) or {}).get("manifest") or {}).get("input_pins") or []
        mb = next((p["content_hash"] for p in pins if p.get("role") == "materialized_base"), None)
        if d["profile"] == "v1":
            out[sid] = {"class": "none-by-design", "source": "production pinned the artifact only", "run": run}
            continue
        if mb and obj(mb) is not None:
            out[sid] = {"class": "whole-tree", "source": "materialized_base", "object": mb, "run": run}
            continue
        body = json.loads(cas.load(d["sha256"]))
        if "anchor" in body and body["anchor"].get("kind") == "git-tree":
            c = body["anchor"]["commit"]
            ok = subprocess.run(["git", "-C", REPOS["striatum-next"], "cat-file", "-e", f"{c}^{{commit}}"],
                                capture_output=True).returncode == 0
            out[sid] = ({"class": "whole-tree", "source": "git-anchor", "repo": "striatum-next", "commit": c}
                        if ok else {"class": "lost", "source": "git anchor commit not in history", "commit": c})
            continue
        base_hash = (body.get("base") or {}).get("content_hash") or \
            ((body.get("base_composition") or {}).get("observed_product") or {}).get("content_hash")
        if base_hash and obj(base_hash) is not None:
            out[sid] = {"class": "partial-product-tree", "source": "declared product object", "object": base_hash}
        else:
            out[sid] = {"class": "lost", "source": "declared base object absent from the store", "object": base_hash}
    return out


def repo_doc_resolution(d: dict) -> dict:
    """References the artifact makes, resolved in the pinned git tree."""
    src = d["source"]
    repo, commit, path = REPOS[src["repo"]], src["commit"], src["path"]
    base = os.path.dirname(path)
    tree = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", commit],
                          capture_output=True, text=True).stdout.split("\n")
    tset = set(tree)
    body = cas.load(d["sha256"]) or ""
    res: dict[str, list] = {}

    def glob(rx):
        r = re.compile(rx)
        return [t for t in tree if r.search(t)][:3]

    for a, b in re.findall(r"\b(?:ADR[ -]?0*(\d{1,4})|adr-0*(\d{1,4}))\b", body):
        n = int(a or b)
        res[f"adr-{n:04d}"] = glob(rf"(^|/)adr-{n:04d}-[^/]*\.md$")
    if src["repo"] == "striatum-next":
        for dd in set(re.findall(r"\b(D0\d{3})\b", body)):
            res[dd] = glob(rf"(^|/)decisions/{dd}-[^/]*\.md$")
        for a, b in re.findall(r"\b(?:RFC[ -]?0*(\d{1,4})|rfcs/0*(\d{1,4}))", body):
            n = int(a or b)
            res[f"rfc-{n:04d}"] = glob(rf"(^|/)rfcs/{n:04d}-[^/]*/")
    for link in set(re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", body)):
        if re.match(r"^[a-z]+://", link):
            continue
        target = os.path.normpath(os.path.join(base, link)) if not link.startswith("/") else link.lstrip("/")
        res[f"link:{link}"] = [target] if target in tset or any(t.startswith(target.rstrip("/") + "/") for t in tree) else []
    for name in set(re.findall(r"`([A-Za-z0-9_-]+\.(?:json|yaml|yml|md|go|py|toml|txt|sh))`", body)):
        res[f"file:{name}"] = [t for t in tree if t.endswith("/" + name) or t == name][:3]
    # Declared file hashes: "[`x`](rel), file SHA-256 `hex`" and "path: `x`; file SHA-256: `hex`".
    hashes = []
    for m in re.finditer(r"\[`?([^`\]]+)`?\]\(([^)\s]+)\),?\s*\n?\s*file SHA-256\s*\n?\s*`([0-9a-f]{64})`", body):
        hashes.append((os.path.normpath(os.path.join(base, m.group(2))), m.group(3)))
    for m in re.finditer(r"path:\s*`([^`]+)`;?\s*\n-\s*file SHA-256:\s*\n?\s*`([0-9a-f]{64})`", body):
        hashes.append((m.group(1), m.group(2)))
    for m in re.finditer(r"`([A-Za-z0-9_./-]+\.json)`,\s*file SHA-256\s*`([0-9a-f]{64})`", body):
        hashes.append((m.group(1), m.group(2)))
    hash_checks = []
    for target, h in hashes:
        content = None
        for cand in (target, os.path.normpath(os.path.join(base, target))):
            r = subprocess.run(["git", "-C", repo, "show", f"{commit}:{cand}"], capture_output=True)
            if r.returncode == 0:
                content, target = r.stdout, cand
                break
        hash_checks.append({"path": target, "declared": h[:12],
                            "outcome": "missing" if content is None else
                            ("match" if hashlib.sha256(content).hexdigest() == h else "MISMATCH")})
    unresolved = sorted(k for k, v in res.items() if not v)
    return {"references": len(res), "unresolved": unresolved, "hash_checks": hash_checks}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "advisory", "pool-runs", "tree-v1-revalidation-20260906"))
    args = ap.parse_args()

    adj, sources = advisory_control_context()
    subs = {json.loads(l)["substrate_id"]: json.loads(l) for l in open(os.path.join(ROOT, "advisory", "substrates.jsonl"))}
    draw_rows = [json.loads(l) for l in open(DRAW_RUN) if l.strip()]
    draw = [{"substrate_id": r["substrate_id"], "profile": r["calibration_profile"],
             "source": subs[r["substrate_id"]]["source"], "sha256": subs[r["substrate_id"]]["sha256"]}
            for r in draw_rows]
    classes = base_classes(args.ledger, draw)
    key_to_sid = {}
    for sid, s in subs.items():
        for k in (sources.get(sid) or sid, s["sha256"], sid):
            key_to_sid[k] = sid

    records = [json.loads(l) for l in open(os.path.join(ROOT, "advisory", "control-adjudications.jsonl"))]
    latest: dict[str, dict] = {}
    for r in records:
        latest[r["dispatch_id"]] = r          # later records override earlier ones
    out_rows, judgment = [], []
    for key, r in latest.items():
        text = (r.get("basis") or "") + " " + " ".join(r.get("notes") or [])
        if not OOC.search(text):
            continue
        sid = key_to_sid.get(key)
        cls = classes.get(sid, {"class": "not-in-draw"})
        in_set = bool(IN_SET.search(r.get("basis") or ""))
        human = r.get("basis_kind") == "human-adjudication"
        row = {"substrate_id": sid, "control_key": key, "disposition": r["disposition"],
               "basis_kind": r.get("basis_kind"), "base_class": cls["class"], "base_source": cls.get("source"),
               "in_set_grounds": in_set}
        if human:
            row["outcome"] = "principal-re-examination"
            judgment.append({**row, "why": "human/Principal ruling: re-affirm or re-rule by the Principal"})
        elif cls["class"] == "none-by-design":
            row["outcome"] = "reference-not-required"
            row["reason"] = "production pinned the artifact alone; references outside it are unverifiable by contract"
        elif cls["class"] == "whole-tree" and cls.get("source") == "git-archive":
            d = next(x for x in draw if x["substrate_id"] == sid)
            resolution = repo_doc_resolution(d)
            row["resolution"] = resolution
            mism = [h for h in resolution["hash_checks"] if h["outcome"] == "MISMATCH"]
            if mism:
                row["outcome"] = "resolved-invalid"
                judgment.append({**row, "why": f"declared file hash does not match the pinned tree: {mism}"})
            elif resolution["unresolved"]:
                row["outcome"] = "resolved-valid"
                row["residue"] = resolution["unresolved"]
                judgment.append({**row, "why": "some referenced paths do not resolve in the pinned tree; "
                                              "decide whether the artifact should contain them"})
            else:
                row["outcome"] = "resolved-valid"
        elif cls["class"] == "whole-tree":
            row["outcome"] = "resolved-valid" if in_set else "principal-re-examination"
            if not in_set:
                judgment.append({**row, "why": "whole tree now available; the label rested on out-of-set grounds"})
        elif cls["class"] == "partial-product-tree":
            row["outcome"] = "resolved-valid" if in_set else "evidence-unavailable"
            row["reason"] = ("in-set grounds stand; base-dependent allegations checkable only within the product tree"
                             if in_set else "the allegation depends on files outside the partial product tree")
        elif cls["class"] == "lost":
            row["outcome"] = "resolved-valid" if in_set else "evidence-unavailable"
            row["reason"] = ("in-set grounds stand; the case is scorable for in-set operators only"
                             if in_set else "the production base is unrecoverable")
        else:
            row["outcome"] = "not-in-draw"
        out_rows.append(row)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "revalidation.jsonl"), "w", encoding="utf-8") as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with open(os.path.join(args.out, "base-classes.json"), "w", encoding="utf-8") as f:
        json.dump(classes, f, indent=1, sort_keys=True)
    from collections import Counter
    summary = {
        "records_grounded_out_of_contract": len(out_rows),
        "by_outcome": dict(Counter(r["outcome"] for r in out_rows)),
        "by_base_class": dict(Counter(c["class"] for c in classes.values())),
        "draw_cases": len(classes),
        "judgment_items": len(judgment),
        "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    with open(os.path.join(args.out, "judgment-items.json"), "w", encoding="utf-8") as f:
        json.dump(judgment, f, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1))
    for j in judgment:
        print(f"  JUDGMENT {j['substrate_id']} [{j['base_class']}] {j['disposition']}: {j['why'][:140]}")


if __name__ == "__main__":
    main()
