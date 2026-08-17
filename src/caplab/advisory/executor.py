"""Advisory-grade execution: CAPLAB-directed matched-pair runs.

The advisory-grade profile (v0) executes the pinned striatum-tuner
matched-pair instrument (`revbench.py`) as a subprocess under CAPLAB
direction, against the exact adapter command the subject's striatum-next
declaration pins. What makes the result `caplab-advisory` custody rather
than `historical-seed` is direction and capture: CAPLAB chooses the subject,
pairs target, seed, and output root; records the instrument repo commit and
full argv in a receipt; and scores the captured run with its own scorer.

Stated limits (this is not the sealed qualification path): no custody-domain
one-shot guarantee, no provider-authenticated identity, no credential
quarantine. Blinding is the instrument's own — the two arms are never shown
together and nothing marks which is which.

Budget: the pair target bounds spend (each pair is two lane calls); the
instrument's own `--abort-after-empty` stops error storms. `max_pairs` here
is a hard refusal, not a suggestion — a caller asking for more than the
authorized bound gets an exception before any subprocess.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess

from .claims import REVIEW_DEFECT_DISCRIMINATION, build_claim
from .scoring import completed, score_backends

DEFAULT_INSTRUMENT_REPO = os.path.expanduser("~/git/striatum-tuner")
#: Notes are provenance, so they must name the instrument that actually ran.
#: A pool run does not execute the tuner instrument, and a claim that says it
#: did misdescribes how its own numbers were produced.
ADVISORY_NOTE_COMMON = (
    "caplab-advisory: CAPLAB-directed advisory-grade execution through the "
    "subject's declared adapter command; no sealed custody domain, no "
    "provider-authenticated identity.")
ADVISORY_NOTES_BY_INSTRUMENT = {
    "matched-pair defect injection": (
        "dispatch-prompt profile: the pinned striatum-tuner instrument renders "
        "striatum's own dispatch prompt, with its posture, pins, and expected "
        "outputs."),
    "matched-pair defect injection (synthetic contract)": (
        "synthetic-contract profile: CAPLAB draws the cases and renders its own "
        "prompt carrying a stated review contract. This is a contract-bearing "
        "review task, not striatum's exact dispatch, and its numbers are not "
        "interchangeable with dispatch-prompt numbers."),
}
ADVISORY_NOTES = [ADVISORY_NOTE_COMMON]


class BudgetRefusal(RuntimeError):
    pass


def instrument_commit(repo: str) -> str:
    out = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def prune_workspaces(out_dir: str) -> int:
    """Retain only what scoring needs from a completed run's arms.

    Keeps `arms/<id>/*-ws/work/outputs/` (the subject's written review, which
    anchored-detection rescoring reads) and drops the materialized bundle
    copies and workspace scratch — those are byte-reproducible from the
    recorded (dispatch_id, operator, seed) and would otherwise import
    thousands of foreign documents into this repository's tree.
    """
    import shutil

    removed = 0
    arms_root = os.path.join(out_dir, "arms")
    if not os.path.isdir(arms_root):
        return 0
    for arm_id in os.listdir(arms_root):
        arm_dir = os.path.join(arms_root, arm_id)
        for entry in os.listdir(arm_dir):
            path = os.path.join(arm_dir, entry)
            if entry.endswith("-ws"):
                work = os.path.join(path, "work")
                for sub in (os.listdir(work) if os.path.isdir(work) else []):
                    if sub != "outputs":
                        shutil.rmtree(os.path.join(work, sub),
                                      ignore_errors=True)
                        removed += 1
            else:
                shutil.rmtree(path, ignore_errors=True)
                removed += 1
    return removed


def run_advisory(*, backend: str, pairs: int, out_dir: str,
                 instrument_repo: str = DEFAULT_INSTRUMENT_REPO,
                 instrument_script: str = "revbench.py",
                 seed: int = 20260815, workers: int = 2, timeout: int = 1800,
                 max_pairs: int = 21, abort_after_empty: int = 8,
                 extra_args: list[str] | None = None) -> dict:
    if pairs > max_pairs:
        raise BudgetRefusal(
            f"pairs={pairs} exceeds the authorized bound max_pairs={max_pairs}")
    os.makedirs(out_dir, exist_ok=True)
    argv = ["python3", instrument_script,
            "--backend", backend,
            "--pairs", str(pairs),
            "--seed", str(seed),
            "--workers", str(workers),
            "--timeout", str(timeout),
            "--abort-after-empty", str(abort_after_empty),
            "--out", os.path.abspath(out_dir)]
    argv += extra_args or []
    receipt = {
        "profile": "caplab-advisory-execution/0",
        "backend": backend,
        "instrument_repo": instrument_repo,
        "instrument_commit": instrument_commit(instrument_repo),
        "argv": argv,
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    log_path = os.path.join(out_dir, "caplab-run.log")
    with open(log_path, "a", encoding="utf-8") as log:
        proc = subprocess.run(argv, cwd=instrument_repo,
                              stdout=log, stderr=subprocess.STDOUT)
    aborted = None
    summary_path = os.path.join(out_dir, "summary.json")
    if os.path.isfile(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            aborted = json.load(f).get("aborted")
    receipt.update({
        "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "exit_code": proc.returncode,
        # completed() is the single authority and already refuses an aborted
        # run; the exit code is recorded beside it so the receipt shows why.
        "completed": completed(out_dir) and proc.returncode == 0,
        "aborted": aborted,
        "log": log_path,
        "pruned_workspace_entries": prune_workspaces(out_dir),
    })
    with open(os.path.join(out_dir, "caplab-receipt.json"), "w",
              encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write("\n")
    return receipt


def claims_from_runs(run_dirs: list[str], backends_root: str | None,
                     as_of: str | None = None) -> list[dict]:
    """Score completed CAPLAB-directed runs into caplab-advisory claims.

    `as_of` defaults to the newest receipt's `finished_at`, never the wall
    clock, so re-deriving claims from the same runs is idempotent — the
    ledger's content-hash dedupe only works if identical evidence produces
    identical bytes.
    """
    usable_dirs = [d for d in run_dirs if completed(d)]
    if as_of is None:
        stamps = []
        for run_dir in usable_dirs:
            receipt_path = os.path.join(run_dir, "caplab-receipt.json")
            if os.path.isfile(receipt_path):
                with open(receipt_path, encoding="utf-8") as f:
                    stamp = json.load(f).get("finished_at")
                if stamp:
                    stamps.append(stamp)
        as_of = max(stamps) if stamps else _dt.datetime.now(
            _dt.timezone.utc).isoformat()
    scored = score_backends(usable_dirs)
    claims = []
    for backend, result in scored.items():
        matched = bool(
            backends_root
            and os.path.isfile(os.path.join(backends_root, backend, "backend.yaml")))
        evidence = []
        for run in result["runs"]:
            entry = {"kind": "matched-pair-run", **run}
            receipt_path = None
            run_dir_for_entry = None
            for run_dir in usable_dirs:
                if os.path.basename(run_dir) == run["run"]:
                    receipt_path = os.path.join(run_dir, "caplab-receipt.json")
                    run_dir_for_entry = run_dir
            if receipt_path and os.path.isfile(receipt_path):
                with open(receipt_path, encoding="utf-8") as f:
                    receipt = json.load(f)
                entry["instrument_commit"] = receipt.get("instrument_commit")
                entry["profile"] = receipt.get("profile")
                # The sweep seed determines which substrates were drawn and
                # which injection each received. Two subjects share a case
                # set only if they share this seed and this instrument
                # commit, so a consumer cannot verify a matched comparison
                # without it recorded on the claim.
                argv = receipt.get("argv") or []
                if "--seed" in argv:
                    entry["sweep_seed"] = argv[argv.index("--seed") + 1]
            # A pool run writes no launcher receipt; its summary records the
            # seed, the instrument and the prompt profile directly. Without
            # these a consumer cannot tell a matched comparison from a
            # coincidental one, nor a contract-bearing task from a dispatch.
            if run_dir_for_entry:
                summary_path = os.path.join(run_dir_for_entry, "summary.json")
                if os.path.isfile(summary_path):
                    with open(summary_path, encoding="utf-8") as f:
                        summary = json.load(f)
                    if summary.get("sweep_seed") is not None:
                        entry.setdefault("sweep_seed", str(summary["sweep_seed"]))
                    if summary.get("instrument"):
                        entry["instrument"] = summary["instrument"]
                    if summary.get("calibration_profile"):
                        entry["prompt_profile"] = summary["calibration_profile"]
            evidence.append(entry)
        notes = list(ADVISORY_NOTES)
        for instrument in result.get("instruments") or []:
            notes.append(f"instrument: {instrument}")
            described = ADVISORY_NOTES_BY_INSTRUMENT.get(instrument)
            notes.append(described if described else
                         f"no profile description is recorded for {instrument}")
        if result.get("profiles"):
            notes.append("prompt profile(s): " + ", ".join(result["profiles"]))
        rel = result.get("instrument_reliability") or {}
        if rel.get("anchor_cases"):
            notes.append(
                f"instrument reliability from {rel['anchor_cases']} replayed "
                f"anchor cases (excluded from these metrics): control arm "
                f"unanimous on {rel['control_unanimous_share']:.0%} of cases, "
                f"mutant arm {rel['mutant_unanimous_share']:.0%}")
        if result["repeated_case_trials"]:
            notes.append(
                f"repeated case trials: {result['repeated_case_trials']} of "
                f"{result['metrics']['n_pairs']['value']} pairs")
        claims.append(build_claim(
            subject_source_id=backend,
            subject_matched=matched,
            construct=REVIEW_DEFECT_DISCRIMINATION,
            metrics=result["metrics"],
            custody="caplab-advisory",
            as_of=as_of,
            evidence=evidence,
            notes=notes,
        ))
    return claims
