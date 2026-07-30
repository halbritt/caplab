#!/usr/bin/env python3
"""Extract a fine-tuning corpus from a striatum graph.

Joins the provenance ledger (labels) with the retained exchange spool
(sealed dispatch bundles + submission bundles), re-renders the exact prompt
every lane attempt saw (render.py, verified against each attempt closure's
rendered_prompt_hash), and emits one JSONL record per submission.

Usage:
  python3 extract.py --repo ~/git/striatum-next \
      --graph 019f22ef-0cb4-780f-9b82-b210bab24325 \
      --out corpus/ [--passes review,implementation-planning,...]

The ledger is read via `striatum ledger cat` run inside --repo (or supply
--ledger-jsonl with a pre-dumped file).
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import subprocess
import sys

import render

DEFAULT_PASSES = "review,implementation-planning,design-convergence,proposal-generation"
MAX_PROMPT_BYTES = 8 << 20   # keep even fat stdin-mode prompts; filter at dataset build
MAX_OUTPUT_BYTES = 8 << 20


def load_ledger(args) -> list[dict]:
    if args.ledger_jsonl:
        with open(args.ledger_jsonl) as f:
            return [json.loads(line) for line in f]
    out = subprocess.run(
        ["striatum", "ledger", "cat"],
        cwd=os.path.expanduser(args.repo),
        capture_output=True, text=True, check=True,
    )
    return [json.loads(line) for line in out.stdout.splitlines() if line.strip()]


def index_ledger(records: list[dict]) -> dict:
    idx = {
        "runs": {},              # run_ref -> {pass, written_at, request_ref}
        "bindings": {},          # dispatch_id -> {run_ref, backend_id, attempt}
        "closures": collections.defaultdict(list),    # run_ref -> [outcome]
        "admissions": collections.defaultdict(list),  # dispatch_id -> [{decision,...}]
        "admissions_by_run": collections.defaultdict(list),  # run_ref -> [{decision,...}]
        "refusals": collections.defaultdict(list),    # dispatch_id -> [detail]
        "gate_verdicts": collections.defaultdict(list),  # producing run_ref -> [{gate_id, verdict, outcome}]
    }
    for r in records:
        t, p = r["type"], r.get("payload") or {}
        if t == "pass_run_opened":
            idx["runs"][r["seq"]] = {
                "pass": p.get("pass_id") or p.get("pass")
                or (p.get("manifest") or {}).get("pass_id")
                or (p.get("manifest") or {}).get("pass"),
                "written_at": r.get("written_at"),
                "request_ref": p.get("request_ref"),
            }
        elif t == "lane_binding":
            did = p.get("dispatch_id")
            if did:
                idx["bindings"][did] = {
                    "run_ref": p.get("run_ref"),
                    "backend_id": p.get("backend_id"),
                    "attempt": p.get("attempt"),
                }
        elif t == "pass_run_closed":
            rr = p.get("run_ref") or p.get("run")
            if rr is not None:
                idx["closures"][rr].append(p.get("outcome") or p.get("status"))
        elif t == "admission_decision":
            entry = {
                "decision": p.get("decision"),
                "refusal_code": p.get("refusal_code"),
                "detail": p.get("detail"),
                "output_id": (p.get("output") or {}).get("output_id"),
            }
            did = p.get("dispatch_id")
            if did:
                idx["admissions"][did].append(entry)
            elif p.get("run_ref") is not None:
                idx["admissions_by_run"][p["run_ref"]].append(entry)
        elif t == "submission_refused":
            did = p.get("dispatch_id")
            if did:
                idx["refusals"][did].append(p.get("detail") or p.get("reason"))
        elif t == "gate_result":
            entry = {
                "gate_id": p.get("gate_id"),
                "gate_class": p.get("gate_class"),
                "verdict": p.get("verdict"),
                "outcome": p.get("outcome"),
            }
            seen = set()
            pr = (p.get("producing_run") or {}).get("run_ref")
            if pr is not None:
                idx["gate_verdicts"][pr].append(entry)
                seen.add(pr)
            for ev in p.get("evidence") or []:
                er = (ev.get("producing_run") or {}).get("run_ref")
                if er is not None and er not in seen:
                    idx["gate_verdicts"][er].append(entry)
                    seen.add(er)
    return idx


def decode(b: bytes) -> tuple[str, bool]:
    try:
        return b.decode("utf-8"), True
    except UnicodeDecodeError:
        return b.decode("utf-8", errors="replace"), False


def load_prompt_modes(repo: str) -> dict[str, str]:
    """backend id -> adapter prompt_mode, from backends/<id>/backend.yaml."""
    import re

    modes = {}
    backends_dir = os.path.join(os.path.expanduser(repo), "backends")
    if not os.path.isdir(backends_dir):
        return modes
    for entry in os.listdir(backends_dir):
        path = os.path.join(backends_dir, entry, "backend.yaml")
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            m = re.search(r"^\s*prompt_mode:\s*(\S+)", f.read(), re.MULTILINE)
        if m:
            modes[entry] = m.group(1).strip("\"'")
    return modes


def extract_submission(exchange: str, dispatch_id: str, idx: dict, passes: set[str],
                       prompt_modes: dict[str, str], stats):
    sub_dir = os.path.join(exchange, "spool", "submissions", dispatch_id)
    manifest_path = os.path.join(sub_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        stats["no_submission_manifest"] += 1
        return None
    with open(manifest_path) as f:
        sub = json.load(f)

    run_ref = sub.get("run_ref")
    run = idx["runs"].get(run_ref) or {}
    pass_id = run.get("pass")
    if pass_id not in passes:
        stats[f"skipped_pass:{pass_id}"] += 1
        return None

    bundle_dir = os.path.join(exchange, "dispatch", dispatch_id)
    if not os.path.isfile(os.path.join(bundle_dir, "manifest.json")):
        stats["no_dispatch_bundle"] += 1
        return None
    with open(os.path.join(bundle_dir, "manifest.json")) as f:
        dispatch = json.load(f)

    attribution = sub.get("attribution") or {}
    attempts = attribution.get("attempts") or []
    work_dir = os.path.join(exchange, "workspaces", dispatch_id, "work")

    # Render the final attempt's prompt (the one that produced the submitted
    # outputs); fall back to attempt 0 semantics when closures are absent.
    prompt_bytes = b""
    verified = False
    transport = None
    render_error = None
    if attempts:
        att = attempts[-1]
        transport = att.get("transport")
        corrective = b""
        ch = att.get("corrective_hash")
        if ch:
            for ex in sub.get("exhaust") or []:
                if ex.get("content_hash") == ch:
                    with open(os.path.join(sub_dir, ex["path"]), "rb") as f:
                        corrective = f.read()
                    break
        dispositions = [e.get("disposition") for e in att.get("source_map") or []]
        try:
            prompt_bytes = render.render_prompt(
                dispatch, bundle_dir, work_dir, corrective, dispositions or None
            )
            verified = render.prompt_hash(prompt_bytes) == att.get("rendered_prompt_hash")
        except (OSError, ValueError) as e:
            render_error = str(e)
    else:
        # Legacy submission without attempt closures: infer the transport from
        # the backend declaration and replay the inline-selection/spill logic.
        transport = prompt_modes.get(
            (idx["bindings"].get(dispatch_id) or {}).get("backend_id")
            or attribution.get("backend_id"),
            "arg",
        )
        corrective = b""
        if attribution.get("internal_relaunches"):
            correctives = sorted(
                (ex for ex in sub.get("exhaust") or []
                 if ex.get("label", "").startswith("corrective-")),
                key=lambda ex: ex["label"],
            )
            if correctives:
                with open(os.path.join(sub_dir, correctives[-1]["path"]), "rb") as f:
                    corrective = f.read()
        try:
            prompt_bytes, _ = render.render_with_spill(
                dispatch, bundle_dir, work_dir, corrective, transport
            )
            verified = render.prompt_hash(prompt_bytes) == attribution.get("rendered_prompt_hash")
        except (OSError, ValueError) as e:
            render_error = str(e)

    stats["rendered"] += 1
    stats["verified" if verified else "hash_mismatch"] += 1
    if render_error:
        stats["render_error"] += 1

    outputs = {}
    for out in sub.get("outputs") or []:
        if out.get("status") != "present" or not out.get("path"):
            continue
        path = os.path.join(sub_dir, out["path"])
        try:
            with open(path, "rb") as f:
                body = f.read(MAX_OUTPUT_BYTES + 1)
        except OSError:
            continue
        truncated = len(body) > MAX_OUTPUT_BYTES
        text, clean = decode(body[:MAX_OUTPUT_BYTES])
        outputs[out["output_id"]] = {
            "kind": out.get("kind"),
            "body": text,
            "utf8_clean": clean,
            "truncated": truncated,
        }

    prompt_text, prompt_clean = decode(prompt_bytes[:MAX_PROMPT_BYTES])
    binding = idx["bindings"].get(dispatch_id) or {}
    admissions = idx["admissions"].get(dispatch_id) or idx["admissions_by_run"].get(run_ref) or []
    admitted = bool(admissions) and all(a["decision"] == "admitted" for a in admissions)

    return {
        "dispatch_id": dispatch_id,
        "run_ref": run_ref,
        "pass": pass_id,
        "written_at": run.get("written_at"),
        "request_ref": run.get("request_ref"),
        "backend_id": binding.get("backend_id") or attribution.get("backend_id"),
        "aliasing_class": attribution.get("aliasing_class"),
        "agent_runtime": attribution.get("agent_runtime_id"),
        "internal_relaunches": attribution.get("internal_relaunches"),
        "transport": transport,
        "status": sub.get("status"),
        "prompt": prompt_text,
        "prompt_bytes": len(prompt_bytes),
        "prompt_utf8_clean": prompt_clean,
        "prompt_truncated": len(prompt_bytes) > MAX_PROMPT_BYTES,
        "prompt_hash_verified": verified,
        "render_error": render_error,
        "outputs": outputs,
        "diagnostics": sub.get("diagnostics"),
        "labels": {
            "admitted": admitted,
            "admission_decisions": admissions,
            "submission_refused": idx["refusals"].get(dispatch_id) or [],
            "run_closures": idx["closures"].get(run_ref) or [],
            "gate_verdicts": idx["gate_verdicts"].get(run_ref) or [],
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="~/git/striatum-next")
    ap.add_argument("--graph", default="019f22ef-0cb4-780f-9b82-b210bab24325")
    ap.add_argument("--data-home", default="~/.local/share/striatum")
    ap.add_argument("--ledger-jsonl", help="pre-dumped `striatum ledger cat` output")
    ap.add_argument("--passes", default=DEFAULT_PASSES)
    ap.add_argument("--out", default="corpus")
    ap.add_argument("--limit", type=int, default=0, help="stop after N submissions (debug)")
    args = ap.parse_args()

    passes = set(args.passes.split(","))
    exchange = os.path.join(os.path.expanduser(args.data_home), "exchange", args.graph)
    os.makedirs(args.out, exist_ok=True)

    print("loading ledger...", file=sys.stderr)
    idx = index_ledger(load_ledger(args))
    print(f"  {len(idx['runs'])} runs, {len(idx['bindings'])} bindings", file=sys.stderr)
    prompt_modes = load_prompt_modes(args.repo)

    stats = collections.Counter()
    corpus_path = os.path.join(args.out, "corpus.jsonl")
    n = 0
    with open(corpus_path, "w") as out:
        submissions = sorted(os.listdir(os.path.join(exchange, "spool", "submissions")))
        for i, dispatch_id in enumerate(submissions):
            rec = extract_submission(exchange, dispatch_id, idx, passes, prompt_modes, stats)
            if rec is not None:
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
            if args.limit and n >= args.limit:
                break
            if (i + 1) % 500 == 0:
                print(f"  {i + 1}/{len(submissions)} scanned, {n} extracted", file=sys.stderr)

    # Per-pass/backend verification summary over what we wrote.
    per = collections.Counter()
    with open(corpus_path) as f:
        for line in f:
            r = json.loads(line)
            per[(r["pass"], r["backend_id"], r["prompt_hash_verified"], r["labels"]["admitted"])] += 1

    stats_path = os.path.join(args.out, "stats.json")
    with open(stats_path, "w") as f:
        json.dump(
            {
                "counters": dict(stats),
                "records": n,
                "per_pass_backend": [
                    {"pass": k[0], "backend": k[1], "verified": k[2], "admitted": k[3], "n": v}
                    for k, v in sorted(per.items(), key=lambda x: -x[1])
                ],
            },
            f, indent=2,
        )
    print(f"wrote {n} records to {corpus_path}", file=sys.stderr)
    print(json.dumps(dict(stats), indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
