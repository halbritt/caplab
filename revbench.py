#!/usr/bin/env python3
"""Measure reviewer quality by matched-pair defect injection.

Design: docs/design/REVIEWER_QUALITY_EVAL_2026-08-07.md

For each selected candidate the runner dispatches two prompts through the
tuple's own declared lane, identical except that one carries a single injected
defect at a known element:

  control  -> a refusing verdict is a FALSE ALARM
  mutant   -> a refusing verdict is a CATCH (and its anchor is checked)

`discrimination = catch_rate - false_alarm_rate` is the headline. It is zero for
any constant reviewer in either direction, which is the property the fate-based
corpus lacked — there, a reviewer that always refused scored 83% because the
label was a copy of a refusing reviewer's own verdict.

The two arms are never shown together and nothing marks which is which. The
mutant's manifest is re-pinned to its mutated body, because `content_hash` and
`subject_content_hash` are printed in the prompt: leaving the original pin would
hand the model a mechanical tell that this arm had been edited, and we would be
measuring edit detection rather than review.

Usage:
  python3 revbench.py --backend deepseek-v4-flash --pairs 40 --workers 6 \
      --out eval-runs/revbench-deepseek-20260807
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import random
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import bench
import defects
import lanes

ACCEPTING = {"accept", "accept_with_findings"}
REFUSING = {"needs_revision", "reject"}


def repin(manifest: dict, old_hash: str, new_hash: str) -> dict:
    """Point every pin that named the original body at the mutated one.

    Without this the prompt carries a content_hash that does not match the body
    it accompanies — an artificial defect we did not intend to inject, and a
    reliable signal of which arm the model is looking at.
    """
    manifest = json.loads(json.dumps(manifest))

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if value == old_hash:
                    node[key] = new_hash
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)
    return manifest


def build_arm(bundle_dir: str, arm_root: str, injection: defects.Injection | None,
              input_index: int = 0) -> str:
    """Materialize a dispatch bundle, optionally with the defect injected."""
    if os.path.isdir(arm_root):
        shutil.rmtree(arm_root)
    shutil.copytree(bundle_dir, arm_root)
    if injection is None:
        return arm_root

    with open(os.path.join(arm_root, "manifest.json")) as f:
        manifest = json.load(f)
    target = (manifest.get("inputs") or [])[input_index]
    path = os.path.join(arm_root, target["path"])
    with open(path, "rb") as f:
        old_hash = hashlib.sha256(f.read()).hexdigest()
    body = injection.body.encode()
    with open(path, "wb") as f:
        f.write(body)
    manifest = repin(manifest, old_hash, hashlib.sha256(body).hexdigest())
    with open(os.path.join(arm_root, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return arm_root


def review_of(content: str) -> dict | None:
    doc = bench.extract_json(content)
    return doc if isinstance(doc, dict) else None


def findings_of(doc: dict | None) -> list:
    if not doc:
        return []
    found = doc.get("findings")
    return found if isinstance(found, list) else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True)
    ap.add_argument("--backends-root", default=bench.DEFAULT_BACKENDS)
    ap.add_argument("--exchange", default=bench.DEFAULT_EXCHANGE)
    ap.add_argument("--eval", default="sft/review.eval.jsonl")
    ap.add_argument("--analysis", default="corpus/analysis.json")
    ap.add_argument("--pairs", type=int, default=40)
    ap.add_argument("--context-bound", type=int, default=0,
                    help="drop candidates whose rendered prompt exceeds this many "
                         "input tokens (0 = no bound)")
    ap.add_argument("--classes", default=None,
                    help="comma-separated defect operator names to restrict to")
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--provider-override", default=None)
    ap.add_argument("--no-accounting", action="store_true")
    ap.add_argument("--abort-after-empty", type=int, default=8,
                    help="stop the run after this many consecutive attempts in "
                         "which the lane returned nothing parseable on either "
                         "arm (0 = never abort)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    declaration = bench.load_declaration(args.backends_root, args.backend)
    lane = lanes.Lane.from_declaration(declaration)
    if args.provider_override:
        lane = lane.with_provider(args.provider_override)
    transport = "fair" if lane.stdout_only else "declared"
    only = args.classes.split(",") if args.classes else None

    # Known-sound population. `fate == final` is unusable as a quality label
    # (it re-encodes the reviewer's verdict) but is exactly right as a filter
    # for "nothing further happened to this artifact", which is all a control
    # needs. A latent defect nobody found would cost a reviewer a false alarm it
    # did not deserve — biased against good reviewers, the safe direction.
    # Sourced from the whole corpus, not the held-out review split: this
    # instrument needs no reference verdict, because ground truth is the defect
    # we injected. The split existed to compare against other reviewers, which
    # is exactly the circularity being escaped.
    with open(args.analysis) as f:
        reviews = json.load(f)["reviews"]
    sound = [
        {"meta": {"dispatch_id": r["dispatch_id"]}} for r in reviews
        if r.get("fate") == "final"
        and os.path.isfile(os.path.join(args.exchange, "dispatch",
                                        r["dispatch_id"], "manifest.json"))
    ]
    if not sound:
        raise SystemExit("revbench: no known-sound candidates; check --analysis")
    random.Random(args.seed).shuffle(sound)

    os.makedirs(args.out, exist_ok=True)
    results_path = os.path.join(args.out, "results.jsonl")
    done = set()
    if os.path.isfile(results_path):
        with open(results_path) as f:
            done = {json.loads(line)["dispatch_id"] for line in f}

    print(f"{len(sound)} known-sound candidates available; targeting {args.pairs} pairs")
    write_lock = threading.Lock()
    spent = [0.0]
    out = open(results_path, "a")

    def emit(row, line):
        with write_lock:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            spent[0] += (row.get("control_cost") or 0) + (row.get("mutant_cost") or 0)
            print(f"{line} [total ${spent[0]:.2f}]", flush=True)

    def run_arm(arm_bundle: str, workspace: str) -> dict:
        with open(os.path.join(arm_bundle, "manifest.json")) as f:
            manifest = json.load(f)
        lanes.materialize(arm_bundle, workspace)
        prompt, dispositions = lanes.render_for(
            lane, manifest, arm_bundle, workspace, transport)
        tokens = int(len(prompt) / bench.BYTES_PER_TOKEN)
        if args.context_bound and tokens > args.context_bound:
            return {"skipped": True, "estimated_input_tokens": tokens}
        run = bench.invoke(lane, prompt, workspace, args.timeout,
                           want_accounting=not args.no_accounting)
        content, source, missing = bench.collect_content(
            lane, run, workspace, lanes.required_outputs(manifest))
        accounting = run.get("accounting") or {}
        return {
            "skipped": False,
            "estimated_input_tokens": tokens,
            "content": content,
            "content_source": source,
            "missing_required": missing,
            "exit_code": run.get("exit_code"),
            "seconds": run.get("seconds"),
            "cost": accounting.get("cost"),
            "provider": accounting.get("provider"),
            "diagnostics": (run.get("diagnostics") or "")[:300],
            # For a file-output lane, collect_content reads outputs/ and drops
            # stdout -- which is exactly where a CLI that never got as far as
            # writing a file says why ("You've hit your session limit").
            "stdout_head": (run.get("stdout") or "")[:300],
        }

    def measure(indexed):
        i, example = indexed
        dispatch_id = example["meta"]["dispatch_id"]
        if dispatch_id in done:
            return None
        bundle_dir = os.path.join(args.exchange, "dispatch", dispatch_id)
        arm_dir = os.path.join(args.out, "arms", dispatch_id[:12])
        row = {"dispatch_id": dispatch_id, "backend_measured": args.backend,
               "transport": transport, "provider_override": args.provider_override}
        try:
            with open(os.path.join(bundle_dir, "manifest.json")) as f:
                manifest = json.load(f)
            inputs = manifest.get("inputs") or []
            if not inputs:
                raise defects.NotApplicable("dispatch pins no inputs")
            source_path = os.path.join(bundle_dir, inputs[0]["path"])
            with open(source_path, errors="replace") as f:
                original = f.read()

            injection = defects.inject(original, seed=args.seed + i, only=only)

            # Instrument check 1: the mutation must actually break something,
            # and the control must not already be broken. A no-op mutation
            # scored as a defect would be a phantom miss.
            mutant_broken = defects.check_present(injection, injection.body)
            control_clean = defects.check_present(injection, original)
            if mutant_broken is False or control_clean is True:
                row.update({"usable": False,
                            "error": "injection failed its mechanical check",
                            "defect_class": injection.defect_class})
                emit(row, f"[{i + 1}] {dispatch_id[:12]} discarded: check failed")
                return row

            control_bundle = build_arm(bundle_dir, os.path.join(arm_dir, "control"), None)
            mutant_bundle = build_arm(bundle_dir, os.path.join(arm_dir, "mutant"), injection)

            control = run_arm(control_bundle, os.path.join(arm_dir, "control-ws", "work"))
            if control["skipped"]:
                row.update({"usable": False, "error": "over context bound",
                            "estimated_input_tokens": control["estimated_input_tokens"]})
                emit(row, f"[{i + 1}] {dispatch_id[:12]} skipped: over bound")
                return row
            mutant = run_arm(mutant_bundle, os.path.join(arm_dir, "mutant-ws", "work"))

            control_doc, mutant_doc = review_of(control["content"]), review_of(mutant["content"])

            # A lane that answered nothing is not a reviewer that caught
            # nothing. agy-gemini produced 24 empty completions on 2026-08-07
            # and they scored as discrimination 0.000, which reads as a
            # measurement and is not one. Discard instead.
            if control_doc is None and mutant_doc is None:
                row.update({
                    "usable": False,
                    "error": "lane produced no parseable review on either arm",
                    "defect_class": injection.defect_class,
                    "control_exit": control.get("exit_code"),
                    "mutant_exit": mutant.get("exit_code"),
                    "control_diagnostics": control.get("diagnostics", "")[:200],
                    # The unparseable body itself, kept verbatim. On 2026-08-08
                    # five confirmatory runs returned 144-of-160 empty and the
                    # cause -- "You've hit your session limit" on stdout, exit
                    # 1, stderr empty -- was recoverable only by probing the
                    # account live, hours later. The row that discards a body
                    # is the only place that body still exists.
                    "control_head": (control.get("content")
                                     or control.get("stdout_head") or "")[:300],
                    "mutant_head": (mutant.get("content")
                                    or mutant.get("stdout_head") or "")[:300],
                })
                emit(row, f"[{i + 1}] {dispatch_id[:12]} discarded: lane returned nothing")
                return row
            control_verdict = (control_doc or {}).get("verdict")
            mutant_verdict = (mutant_doc or {}).get("verdict")
            mutant_findings = findings_of(mutant_doc)

            anchors = [str(f.get("element_anchor") or "") for f in mutant_findings
                       if isinstance(f, dict)]
            hit = any(injection.element_anchor.lstrip("#").lstrip("el:") in a
                      or a and a in injection.element_anchor for a in anchors)
            grounded = [defects.anchor_resolves(a, injection.body) for a in anchors]

            row.update({
                "usable": True,
                "defect_class": injection.defect_class,
                "defect_severity": injection.severity,
                "defect_anchor": injection.element_anchor,
                "defect_description": injection.description,
                "defect_checkable": injection.checkable,
                "estimated_input_tokens": control["estimated_input_tokens"],
                "control_verdict": control_verdict,
                "mutant_verdict": mutant_verdict,
                "false_alarm": control_verdict in REFUSING,
                "caught": mutant_verdict in REFUSING,
                "anchor_hit": bool(hit),
                "anchors_resolved": sum(1 for g in grounded if g),
                "anchors_total": len(anchors),
                # Kept verbatim: on 2026-08-07 anchor_resolves read 0.0 for
                # claude-harm and codex while both caught defects with correct
                # verdicts, so the metric was measuring anchor *convention*
                # rather than fabrication. Without the raw values that could
                # not be diagnosed after the fact.
                "anchors_emitted": anchors[:8],
                "mutant_findings": len(mutant_findings),
                "control_json_valid": control_doc is not None,
                "mutant_json_valid": mutant_doc is not None,
                "control_seconds": control["seconds"], "mutant_seconds": mutant["seconds"],
                "control_cost": control["cost"], "mutant_cost": mutant["cost"],
                "provider": mutant.get("provider"),
                "error": None,
            })
            emit(row, f"[{i + 1}] {dispatch_id[:12]} {injection.defect_class:20} "
                      f"control={control_verdict} mutant={mutant_verdict} "
                      f"{'CAUGHT' if row['caught'] else 'missed'}"
                      f"{' anchored' if hit else ''}"
                      f"{' FALSE-ALARM' if row['false_alarm'] else ''}")
            return row
        except Exception as e:  # noqa: BLE001
            row.update({"usable": False, "error": f"{type(e).__name__}: {e}"})
            emit(row, f"[{i + 1}] {dispatch_id[:12]} error: {e}")
            return row

    # Oversample: pairs are discarded when the artifact exceeds the context
    # bound or an injection fails its mechanical check, and the target is a
    # count of usable pairs rather than of attempts.
    pool_input = list(enumerate(sound[: args.pairs * 4]))
    remaining = [args.pairs]
    # A lane that is failing wholesale is not a slow lane. On 2026-08-08 an
    # account session limit turned five 40-pair runs into 152 empty attempts
    # each, and every one of them exited 0 -- a clean-looking run directory
    # holding no measurement. Stop at a run of consecutive empty lanes and
    # exit nonzero, so the failure is loud while the cause is still live.
    empty_streak = [0]
    aborted = [None]

    def measure_bounded(indexed):
        with write_lock:
            if remaining[0] <= 0 or aborted[0]:
                return None
        result = measure(indexed)
        if result:
            with write_lock:
                if result.get("usable"):
                    remaining[0] -= 1
                    empty_streak[0] = 0
                elif result.get("error", "").startswith("lane produced no parseable"):
                    empty_streak[0] += 1
                    if (args.abort_after_empty
                            and empty_streak[0] >= args.abort_after_empty):
                        aborted[0] = (
                            f"{empty_streak[0]} consecutive empty lanes; last body: "
                            f"{(result.get('control_head') or '(nothing)')[:120]!r}")
        return result
    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(measure_bounded, pool_input))
    else:
        for indexed in pool_input:
            measure_bounded(indexed)
    out.close()

    rows = [json.loads(line) for line in open(results_path)]
    usable = [r for r in rows if r.get("usable")]
    summary = summarize(args, usable, rows)
    summary["aborted"] = aborted[0]
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    if aborted[0]:
        print(f"ABORTED: {aborted[0]}", file=sys.stderr)
        raise SystemExit(2)


def _bands(usable: list[dict]) -> dict:
    bands: dict = collections.defaultdict(lambda: {"n": 0, "caught": 0, "false_alarms": 0})
    for r in usable:
        tokens = r.get("estimated_input_tokens") or 0
        key = "<25k" if tokens < 25000 else "25k-100k" if tokens < 100000 else ">=100k"
        bands[key]["n"] += 1
        bands[key]["caught"] += int(r["caught"])
        bands[key]["false_alarms"] += int(r["false_alarm"])
    return {k: dict(v) for k, v in bands.items()}


def summarize(args, usable: list[dict], rows: list[dict]) -> dict:
    n = len(usable)
    caught = sum(1 for r in usable if r["caught"])
    alarms = sum(1 for r in usable if r["false_alarm"])
    catch_rate = caught / n if n else None
    false_alarm_rate = alarms / n if n else None
    anchors_total = sum(r["anchors_total"] for r in usable)
    anchors_ok = sum(r["anchors_resolved"] for r in usable)
    by_class = collections.defaultdict(lambda: {"n": 0, "caught": 0, "anchored": 0})
    for r in usable:
        entry = by_class[r["defect_class"]]
        entry["n"] += 1
        entry["caught"] += int(r["caught"])
        entry["anchored"] += int(r["anchor_hit"])
    cost = sum((r.get("control_cost") or 0) + (r.get("mutant_cost") or 0) for r in usable)
    return {
        "backend": args.backend,
        "instrument": "matched-pair defect injection",
        "pairs_usable": n,
        "pairs_discarded": len(rows) - n,
        # The headline. Zero for any constant reviewer, in either direction.
        "discrimination": (catch_rate - false_alarm_rate) if n else None,
        "catch_rate": catch_rate,
        "false_alarm_rate": false_alarm_rate,
        "anchor_hit_rate_of_caught": (
            sum(1 for r in usable if r["caught"] and r["anchor_hit"]) / caught
            if caught else None),
        "anchor_resolves_rate": anchors_ok / anchors_total if anchors_total else None,
        "findings_per_mutant": (
            sum(r["mutant_findings"] for r in usable) / n if n else None),
        "json_valid_control": (
            sum(1 for r in usable if r["control_json_valid"]) / n if n else None),
        "json_valid_mutant": (
            sum(1 for r in usable if r["mutant_json_valid"]) / n if n else None),
        "by_defect_class": {k: dict(v) for k, v in sorted(by_class.items())},
        # Instrument check 4: in the fate corpus, outcome tracked prompt size
        # almost perfectly. If catch_rate splits by band here, the eval is
        # measuring size again rather than review.
        "by_size_band": _bands(usable),
        "mean_seconds": (
            sum((r["control_seconds"] or 0) + (r["mutant_seconds"] or 0)
                for r in usable) / (2 * n) if n else None),
        "cost_total_usd": round(cost, 4) if cost else None,
        "cost_per_defect_caught_usd": round(cost / caught, 4) if caught else None,
        "provider_override": args.provider_override,
        "context_bound": args.context_bound or None,
    }


if __name__ == "__main__":
    main()
