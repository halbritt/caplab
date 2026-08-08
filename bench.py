#!/usr/bin/env python3
"""Measure a backend tuple on the held-out review split, through its own lane.

Replaces eval.py (endpoint-only, replayed foreign prompts) and eval_harness.py
(scored the newest file in outputs/, and ran harness lanes in empty workspaces
while the prompt named the real production exchange). It keeps their metric
functions verbatim, so rows produced here stay comparable with earlier ones.

Three commitments, each answering a defect the 2026-08-07 audit found:

  1. Production parity. Every tuple is measured through the `adapter.command`
     its declaration names, invoked the way the supervisor invokes it. Never by
     pointing an aggregator at the same weights a coding harness serves — same
     model, different lane, so the number would describe a lane that does not
     exist (Principal ruling, 2026-08-07).

  2. A visible subject. Prompts are re-rendered per example against a real
     per-example workspace with the sealed bundle materialized into it, for the
     lane class being measured. Every row records `subject_visible`; a row that
     could not see its subject is reported, never quietly averaged in.

  3. The declared output. A harness lane is scored on the output id the
     dispatch manifest marks required, read by name. Absent means absent.

Usage:
  python3 bench.py --backend kimi-k3 --out eval-runs/bench-kimi-k3-20260807
  python3 bench.py --backend codex-sol-max --limit 10 --out eval-runs/bench-codex
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import yaml

import lanes
from eval import VERDICTS, extract_json, side

DEFAULT_BACKENDS = os.path.expanduser("~/git/striatum-next/backends")
DEFAULT_EXCHANGE = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325"
)
# The lane binary that grew a machine-readable accounting channel in version 6.
# Appending its flag is the one deviation from the declared argv, it changes no
# request parameter that can affect the completion, and every row records it.
ACCOUNTING_LANE = "striatum-openai-lane"
ACCOUNTING_FLAG = "-usage-stderr"

# Measured on the 2026-08-07 K3 probe: a 36,496-byte review prompt billed
# 12,000 prompt tokens. Used only to decide which examples a tuple can hold;
# rows that run record the endpoint's own prompt_tokens.
BYTES_PER_TOKEN = 3.04


def declared_input_tokens(declaration: dict) -> int | None:
    profile = ((declaration.get("capabilities") or {}).get("context_profile") or {})
    return profile.get("practical_input_tokens")


def load_declaration(backends_root: str, backend_id: str) -> dict:
    path = os.path.join(backends_root, backend_id, "backend.yaml")
    with open(path) as f:
        declaration = yaml.safe_load(f)
    if declaration.get("id") != backend_id:
        raise SystemExit(f"bench: {path} declares id {declaration.get('id')!r}")
    return declaration


def accounting_from(stderr: str) -> tuple[dict, str]:
    """Pull the lane's accounting line out of stderr, keeping the rest.

    The accounting record is one JSON object on its own line; anything else the
    lane wrote is a real diagnostic and is preserved separately rather than
    being swallowed by the parse.
    """
    accounting, diagnostics = {}, []
    for line in (stderr or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("{") and not accounting:
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                diagnostics.append(line)
                continue
            if isinstance(parsed, dict):
                accounting = parsed
                continue
        diagnostics.append(line)
    return accounting, "\n".join(diagnostics)


def invoke(lane: lanes.Lane, prompt: bytes, workspace: str, timeout: int,
           want_accounting: bool) -> dict:
    argv = list(lane.command)
    if want_accounting and os.path.basename(argv[0]) == ACCOUNTING_LANE:
        argv.append(ACCOUNTING_FLAG)
        augmented = True
    else:
        augmented = False

    stdin_data = None
    if lane.prompt_mode == "arg":
        argv.append(prompt.decode("utf-8", errors="replace"))
    else:
        stdin_data = prompt

    started = time.time()
    try:
        completed = subprocess.run(
            argv, input=stdin_data, capture_output=True,
            timeout=timeout, cwd=workspace,
        )
        stdout = completed.stdout.decode("utf-8", errors="replace")
        stderr = completed.stderr.decode("utf-8", errors="replace")
        code = completed.returncode
    except subprocess.TimeoutExpired:
        stdout, stderr, code = "", f"timeout after {timeout}s", -1

    accounting, diagnostics = accounting_from(stderr)
    return {
        "argv_augmented": augmented,
        "stdout": stdout,
        "diagnostics": diagnostics,
        "accounting": accounting,
        "exit_code": code,
        "seconds": round(time.time() - started, 1),
    }


ANCHOR_IN_TEXT = re.compile(
    r"(?:\{#(el:[A-Za-z0-9_.\-/:]+)\}"           # {#el:slug}, the emitted form
    r"|element[ _]anchor[:=]\s*([^|\n,;]+)"       # "element anchor: <x>", prose
    r"|(?<![\w#])(#?el:[A-Za-z0-9_.\-/:]+))",     # a bare el:slug mention
    re.IGNORECASE)


def normalize_anchor(anchor: str) -> str:
    """An anchor reduced to the identity two lanes can be compared on.

    The previous form was `a.lstrip("#").lstrip("el:")`, and lstrip takes a
    character SET -- so `el:element-scoped-rule` normalized to
    `ment-scoped-rule`, mangling every anchor whose slug happens to begin
    with e, l or a colon.
    """
    text = anchor.strip().strip("`'\"").strip()
    text = text.removeprefix("{").removesuffix("}")
    text = text.removeprefix("#")
    text = text.removeprefix("el:")
    return text.strip().lower()


def anchors_of(findings: list) -> list[str]:
    """Every element anchor a review names, whatever shape it names it in.

    Only findings[].element_anchor was read before. codex writes its anchor
    inside the free-text finding -- "F1 | element anchor: <x> | Rationale:" --
    with no such field, so it emitted 51 anchors across 35 pairs and scored an
    anchor hit rate of exactly 0.000. That read as a lane that never grounds
    its findings; it was a lane whose findings were never parsed.
    """
    found: list[str] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        declared = finding.get("element_anchor")
        if isinstance(declared, str) and declared.strip():
            found.append(declared)
            continue
        for value in finding.values():
            if not isinstance(value, str):
                continue
            for groups in ANCHOR_IN_TEXT.findall(value):
                found.extend(g for g in groups if g and g.strip())
    return found


def anchor_hits(injected: str, emitted: list[str]) -> bool:
    """Whether any emitted anchor names the element the injection broke."""
    target = normalize_anchor(injected)
    if not target:
        return False
    for anchor in emitted:
        candidate = normalize_anchor(anchor)
        if candidate and (candidate in target or target in candidate):
            return True
    return False


def collect_content(lane: lanes.Lane, run: dict, workspace: str,
                    required: list[str]) -> tuple[str, str, list[str]]:
    """The artifact the lane produced, from the channel its declaration names.

    Returns (content, source, missing_required).
    """
    missing = []
    content, source = "", "absent"
    for output_id in required:
        path = os.path.join(workspace, "outputs", output_id)
        if not os.path.isfile(path):
            missing.append(output_id)
            continue
        if not content:
            with open(path, errors="replace") as f:
                content = f.read()
            source = os.path.join("outputs", output_id)
    if content or not lane.stdout_only:
        return content, source, missing

    # stdout_output=single-required-output is a FALLBACK, not a channel.
    # supervisor.go materializeStdoutOutput stats the required output first
    # and returns early when it exists -- the file always wins, and stdout is
    # bridged only when the lane wrote nothing. This read stdout
    # unconditionally instead, so the whole agy family was scored on Gemini's
    # chat summary ("The execution lane for pass review has completed...")
    # while its actual review-ledger sat unread in outputs/. Nine tuples
    # measured as silent because the harness looked at the wrong channel.
    return run["stdout"], "stdout", []


def score(doc, reference: dict, fate_record: dict) -> dict:
    verdict = doc.get("verdict") if isinstance(doc, dict) else None
    fate = fate_record.get("fate")
    return {
        "json_valid": isinstance(doc, dict),
        "verdict": verdict,
        "verdict_legal": verdict in VERDICTS,
        "reference_verdict": reference.get("verdict"),
        "verdict_exact_match": verdict == reference.get("verdict"),
        "side_match": side(verdict) is not None
        and side(verdict) == side(reference.get("verdict")),
        "fate": fate,
        "agrees_with_fate": (
            None if fate not in ("final", "revised") or side(verdict) is None
            else side(verdict) == ("accepting" if fate == "final" else "refusing")
        ),
    }


def ratio(rows: list[dict], key: str) -> float | None:
    return sum(1 for r in rows if r.get(key)) / len(rows) if rows else None


def discrimination(rows: list[dict]) -> dict:
    """Whether a reviewer is telling good work from bad, or just guessing one way.

    Raw fate_agreement cannot answer that on this corpus, because the answer is
    not evenly distributed: the examples that fit a small context are mostly
    `final` (accept is right) and the large ones are almost all `revised`
    (refuse is right). A model that always accepts scores 82% on the first group
    and 9% on the second, and neither number is skill. The 2026-08-07 audit read
    exactly that artifact as "codex-class".

    So report both halves separately and their mean. `balanced_accuracy` is 50%
    for any constant answer, whatever the class mix, which is the property raw
    agreement lacks.
    """
    scored = [r for r in rows if r.get("agrees_with_fate") is not None]
    revised = [r for r in scored if r["fate"] == "revised"]
    final = [r for r in scored if r["fate"] == "final"]
    # Sensitivity: of the work that genuinely needed revision, how much did the
    # reviewer refuse? Specificity: of the work that stood, how much did it accept?
    sensitivity = (sum(1 for r in revised if r["agrees_with_fate"]) / len(revised)
                   if revised else None)
    specificity = (sum(1 for r in final if r["agrees_with_fate"]) / len(final)
                   if final else None)
    balanced = ((sensitivity + specificity) / 2
                if sensitivity is not None and specificity is not None else None)
    accepting = sum(1 for r in scored
                    if r["verdict"] in ("accept", "accept_with_findings"))
    return {
        "balanced_accuracy": balanced,
        "caught_revised": sensitivity,
        "passed_final": specificity,
        "n_revised": len(revised),
        "n_final": len(final),
        "accept_rate": accepting / len(scored) if scored else None,
        "majority_class_rate": (
            max(len(revised), len(final)) / len(scored) if scored else None),
    }


def summarize(backend: str, transport: str, rows: list[dict]) -> dict:
    """Score only rows whose subject was visible.

    A row the model could not see the subject of measures the harness, not the
    model. Those rows are counted and reported, never averaged into the tuple's
    numbers — averaging them in is exactly how a codex-class reviewer came to
    read 27%.
    """
    measured = [r for r in rows if r.get("measured")]
    over_context = sum(1 for r in rows if r.get("over_context"))
    fair = [r for r in measured if r["subject_visible"]]
    blind = len(measured) - len(fair)
    scored_fate = [r for r in fair if r["agrees_with_fate"] is not None]
    costs = [r["cost"] for r in fair if r.get("cost") is not None]
    return {
        "backend": backend,
        "lane": "declared-adapter-command",
        "transport": transport,
        "n": len(fair),
        "eligible_of_split": f"{len(measured)}/{len(rows)}",
        "excluded_over_context": over_context,
        "excluded_subject_invisible": blind,
        "errors": sum(1 for r in fair if r["error"]),
        "json_valid": ratio(fair, "json_valid"),
        "verdict_legal": ratio(fair, "verdict_legal"),
        "verdict_exact_match": ratio(fair, "verdict_exact_match"),
        "side_match": ratio(fair, "side_match"),
        "fate_agreement": (
            sum(1 for r in scored_fate if r["agrees_with_fate"]) / len(scored_fate)
            if scored_fate else None
        ),
        "fate_scored": len(scored_fate),
        **discrimination(fair),
        "verdict_distribution": dict(collections.Counter(str(r["verdict"]) for r in fair)),
        "mean_seconds": round(sum(r["seconds"] or 0 for r in fair) / len(fair), 1) if fair else None,
        "cost_total_usd": round(sum(costs), 4) if costs else None,
        "cost_per_review_usd": round(sum(costs) / len(costs), 4) if costs else None,
        "cost_rows": len(costs),
        "mean_reasoning_tokens": (
            round(sum(r["reasoning_tokens"] for r in fair
                      if r.get("reasoning_tokens") is not None)
                  / max(1, sum(1 for r in fair if r.get("reasoning_tokens") is not None)))
            if any(r.get("reasoning_tokens") is not None for r in fair) else None
        ),
        "providers": dict(collections.Counter(
            str(r["provider"]) for r in fair if r.get("provider"))),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, help="backend id under --backends-root")
    ap.add_argument("--backends-root", default=DEFAULT_BACKENDS)
    ap.add_argument("--exchange", default=DEFAULT_EXCHANGE,
                    help="retained exchange root holding the sealed dispatch bundles")
    ap.add_argument("--eval", default="sft/review.eval.jsonl")
    ap.add_argument("--analysis", default="corpus/analysis.json")
    ap.add_argument("--transport", choices=("auto", "fair", "declared"), default="auto",
                    help="auto: inline-everything for stdout-only lanes, the declaration's "
                         "own transport for harness lanes")
    ap.add_argument("--context-bound", default="declared",
                    help="input-token budget deciding which examples an inline-rendered "
                         "lane can hold: 'declared' (the tuple's own "
                         "capabilities.context_profile.practical_input_tokens), an integer "
                         "token count, or 'none'. Ignored for lanes whose transport spills "
                         "bodies to files — a harness reads them selectively.")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-accounting", action="store_true",
                    help="do not append -usage-stderr; forfeits per-row cost and provider")
    ap.add_argument("--provider-override", default=None,
                    help="replace the declaration's -openrouter-provider pin with this exact "
                         "endpoint slug. Measures a configuration the declaration does not "
                         "currently name, so every row records it and the summary carries it.")
    ap.add_argument("--restrict-to", default=None,
                    help="path to another run's results.jsonl; measure exactly the dispatch "
                         "ids it measured. Use to compare lane classes on one sample — a "
                         "harness lane sees the whole split, so without this it would be "
                         "scored on different work than the endpoint tuples.")
    ap.add_argument("--workers", type=int, default=1,
                    help="concurrent lanes. Each measurement is a subprocess call to a "
                         "remote endpoint, so fan-out is bounded by the vendor rather than "
                         "this host. Rows are appended under a lock as they finish.")
    ap.add_argument("--summarize-only", action="store_true",
                    help="re-score an existing run at a different --context-bound without "
                         "calling anything. A run at a high bound contains every row a lower "
                         "bound would have measured, so one measurement serves both.")
    ap.add_argument("--out", required=True, help="output directory")
    args = ap.parse_args()

    declaration = load_declaration(args.backends_root, args.backend)
    if declaration.get("status", "accepted") != "accepted":
        print(f"note: {args.backend} is status {declaration.get('status')!r} — measuring anyway")
    lane = lanes.Lane.from_declaration(declaration)
    if args.provider_override:
        lane = lane.with_provider(args.provider_override)
        print(f"provider override: {args.provider_override} "
              f"(the declaration's own pin is not what is being measured)")
    transport = args.transport
    if transport == "auto":
        transport = "fair" if lane.stdout_only else "declared"

    # A one-shot endpoint reviews what fits in its context window and nothing
    # else. 64 of this split's 98 examples inline to 8-14MB — they pin an
    # expanded base repository tree — so "re-render everything inline and
    # measure all 98" is not a benchmark an endpoint tuple can sit for. The
    # bound is the tuple's own declared capacity, and what it excludes is
    # reported rather than quietly dropped.
    if transport != "fair" or args.context_bound == "none":
        context_bound = None
    elif args.context_bound == "declared":
        context_bound = declared_input_tokens(declaration)
        if context_bound is None:
            raise SystemExit(
                f"bench: {args.backend} declares no context_profile.practical_input_tokens; "
                f"pass --context-bound <tokens> or 'none'")
    else:
        context_bound = int(args.context_bound)
    if context_bound:
        print(f"context bound: {context_bound:,} input tokens "
              f"(~{int(context_bound * BYTES_PER_TOKEN):,} prompt bytes)")

    fate = {}
    if os.path.isfile(args.analysis):
        with open(args.analysis) as f:
            fate = {r["dispatch_id"]: r for r in json.load(f)["reviews"]}

    os.makedirs(args.out, exist_ok=True)
    results_path = os.path.join(args.out, "results.jsonl")
    done = set()
    if os.path.isfile(results_path):
        with open(results_path) as f:
            done = {json.loads(line)["dispatch_id"] for line in f}

    with open(args.eval) as f:
        examples = [json.loads(line) for line in f]
    if args.restrict_to:
        with open(args.restrict_to) as f:
            sample = {json.loads(line)["dispatch_id"] for line in f
                      if json.loads(line).get("measured")}
        examples = [e for e in examples if e["meta"]["dispatch_id"] in sample]
        print(f"restricted to {len(examples)} dispatch ids measured by {args.restrict_to}")
    if args.limit:
        examples = examples[: args.limit]

    def measure(indexed) -> dict | None:
        """Measure one example. Every lane call is a subprocess, so the work is
        IO-bound and threads parallelize it without touching the row logic."""
        i, example = indexed
        dispatch_id = example["meta"]["dispatch_id"]
        if dispatch_id in done:
            return None
        reference = json.loads(example["messages"][1]["content"])
        workspace = os.path.abspath(
            os.path.join(args.out, "workspaces", dispatch_id[:12], "work"))
        bundle_dir = os.path.join(args.exchange, "dispatch", dispatch_id)

        row = {
            "dispatch_id": dispatch_id,
            "backend_measured": args.backend,
            "backend_reference": example["meta"]["backend_id"],
            "transport": transport,
            "provider_override": args.provider_override,
        }
        try:
            with open(os.path.join(bundle_dir, "manifest.json")) as f:
                manifest = json.load(f)
            lanes.materialize(bundle_dir, workspace)
            prompt, dispositions = lanes.render_for(
                lane, manifest, bundle_dir, workspace, transport)
            visible = lanes.subject_visible(dispositions, workspace, manifest)
            required = lanes.required_outputs(manifest)

            estimated_tokens = int(len(prompt) / BYTES_PER_TOKEN)
            if context_bound and estimated_tokens > context_bound:
                row.update({
                    "measured": False, "over_context": True,
                    "subject_visible": visible, "prompt_bytes": len(prompt),
                    "estimated_input_tokens": estimated_tokens,
                    "context_bound": context_bound,
                    "error": f"over context bound: ~{estimated_tokens:,} > {context_bound:,}",
                })
                emit(row, f"[{i + 1}/{len(examples)}] {dispatch_id[:12]} "
                          f"skipped: ~{estimated_tokens:,} tokens over bound")
                return row

            run = invoke(lane, prompt, workspace, args.timeout,
                         want_accounting=not args.no_accounting)
            content, source, missing = collect_content(lane, run, workspace, required)
            error = None
            if run["exit_code"] != 0:
                error = run["diagnostics"][:500] or f"exit {run['exit_code']}"
            elif missing:
                error = f"missing required outputs: {missing}"
        except Exception as e:  # noqa: BLE001 — one bad example must not end the run
            run, content, source, missing = {}, "", "error", []
            visible, error = False, f"{type(e).__name__}: {e}"
            prompt, dispositions = b"", []

        accounting = run.get("accounting") or {}
        doc = extract_json(content)
        row.update({
            "measured": True,
            "over_context": False,
            "context_bound": context_bound,
            "estimated_input_tokens": int(len(prompt) / BYTES_PER_TOKEN),
            "error": error,
            "subject_visible": visible,
            "inlined_inputs": sum(1 for d in dispositions if d == "inline"),
            "spilled_inputs": sum(1 for d in dispositions if d != "inline"),
            "prompt_bytes": len(prompt),
            "content_source": source,
            "missing_required": missing,
            "exit_code": run.get("exit_code"),
            "seconds": run.get("seconds"),
            "argv_augmented": run.get("argv_augmented"),
            "provider": accounting.get("provider"),
            "served_model": accounting.get("model"),
            "finish_reason": accounting.get("finish_reason"),
            "native_finish_reason": accounting.get("native_finish_reason"),
            "prompt_tokens": accounting.get("prompt_tokens"),
            "completion_tokens": accounting.get("completion_tokens"),
            "reasoning_tokens": accounting.get("reasoning_tokens"),
            "cost": accounting.get("cost"),
            "diagnostics_head": (run.get("diagnostics") or "")[:500],
            "raw_content_head": content[:2000],
        })
        row.update(score(doc, reference, fate.get(dispatch_id) or {}))
        emit(row, f"[{i + 1}/{len(examples)}] {dispatch_id[:12]} "
                  f"verdict={row['verdict']} ref={reference.get('verdict')} "
                  f"visible={visible} {row['seconds']}s ${accounting.get('cost')}")
        return row

    if not args.summarize_only:
        write_lock = threading.Lock()
        spent = [0.0]
        with open(results_path, "a") as out:
            def emit(row: dict, line: str) -> None:
                """Append one row and report it. Rows land as they finish, so a
                killed run keeps everything already paid for."""
                with write_lock:
                    out.write(json.dumps(row, ensure_ascii=False) + "\n")
                    out.flush()
                    spent[0] += row.get("cost") or 0
                    print(f"{line} [run total ${spent[0]:.2f}]", flush=True)

            if args.workers > 1:
                print(f"fan-out: {args.workers} concurrent lanes")
                with ThreadPoolExecutor(max_workers=args.workers) as pool:
                    list(pool.map(measure, enumerate(examples)))
            else:
                for indexed in enumerate(examples):
                    measure(indexed)

    current = {ex["meta"]["dispatch_id"] for ex in examples}
    rows = [r for line in open(results_path)
            if (r := json.loads(line))["dispatch_id"] in current]

    # Re-apply the reporting bound. A row measured under a generous bound but
    # larger than the one being reported is excluded here exactly as it would
    # have been excluded at call time — that is what makes one run reportable
    # at several bounds without measuring twice.
    if context_bound:
        for row in rows:
            estimated = row.get("estimated_input_tokens")
            if row.get("measured") and estimated and estimated > context_bound:
                row["measured"], row["over_context"] = False, True

    summary = summarize(args.backend, transport, rows)
    summary["context_bound"] = context_bound
    summary["provider_override"] = args.provider_override
    name = f"summary-{context_bound // 1000}k.json" if context_bound else "summary.json"
    with open(os.path.join(args.out, name), "w") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    if summary["excluded_subject_invisible"]:
        print(f"\nNOTE: {summary['excluded_subject_invisible']} row(s) excluded — the prompt "
              f"did not put the review subject in reach. Those rows measure the harness.")


if __name__ == "__main__":
    main()
