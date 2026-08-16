"""Seed admission: the striatum-tuner 2026-08 sweep as historical evidence.

Scans a runs root (default: the live striatum-tuner working tree's
`eval-runs/`) for completed matched-pair defect-injection runs, scores them
with the shared scorer, and emits scored advisory claims with custody
`historical-seed`. The claims say exactly what they are: evidence executed
before CAPLAB directed the runs, admitted because discarding a fleet-wide
matched-pair sweep would leave the initial ranking empty, and labeled so
every consumer can weight that provenance down or out.

`SEED_AS_OF` is a documented constant, not a wall-clock read: the sweep's
final measurements landed 2026-08-09, and admission must be replayable.
"""

from __future__ import annotations

import json
import os

from .claims import REVIEW_DEFECT_DISCRIMINATION, build_claim
from .scoring import eligible_run_dirs, score_backends

SEED_AS_OF = "2026-08-09T00:00:00+00:00"

SEED_NOTES = [
    "historical-seed: executed by striatum-tuner (pre-CAPLAB custody), "
    "2026-08-07..09 fleet sweep; admitted under advisory-selection-001.",
    "case pool is small and shared across bindings: distinct injections "
    "number in the tens, so treat fine rank distinctions as noise.",
    "anchored_detection, where present, is rescored from retained arms on "
    "the corrected anchor path; pre-correction row fields were never read.",
]


#: The instrument's own default seed, and the value the 2026-08 sweep's draws
#: reproduce. Historical runs recorded no seed, so it is verified rather than
#: assumed: replaying the instrument's candidate selection under this seed
#: reproduces the exact dispatch ids each run drew, and no other tried seed
#: does. See `verify_sweep_seed`.
HISTORICAL_SWEEP_SEED = 20260807

DEFAULT_EXCHANGE = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DEFAULT_ANALYSIS = os.path.expanduser("~/git/striatum-tuner/corpus/analysis.json")


def candidate_pool(exchange_root: str, analysis_path: str,
                   seed: int) -> list[str]:
    """The instrument's known-sound candidate order under one seed."""
    import random

    with open(analysis_path, encoding="utf-8") as f:
        reviews = json.load(f)["reviews"]
    sound = [
        r["dispatch_id"] for r in reviews
        if r.get("fate") == "final"
        and os.path.isfile(os.path.join(exchange_root, "dispatch",
                                        r["dispatch_id"], "manifest.json"))
    ]
    random.Random(seed).shuffle(sound)
    return sound


def verify_sweep_seed(run_dir: str, seed: int, exchange_root: str,
                      analysis_path: str, slack: int = 8) -> bool:
    """Whether this run's drawn cases are reproduced by that seed.

    The instrument draws from a seeded shuffle of the known-sound pool, so a
    run's dispatch ids must all fall inside the pool prefix that seed
    produces. `slack` allows for the oversampling the instrument performs
    when a case is discarded.
    """
    results_path = os.path.join(run_dir, "results.jsonl")
    if not os.path.isfile(results_path):
        return False
    with open(results_path, encoding="utf-8") as f:
        drawn = [json.loads(line)["dispatch_id"] for line in f if line.strip()]
    if not drawn:
        return False
    prefix = set(candidate_pool(exchange_root, analysis_path,
                                seed)[: len(drawn) + slack])
    return all(dispatch in prefix for dispatch in drawn)


def seed_claims(runs_root: str, backends_root: str | None = None,
                exchange_root: str | None = None,
                analysis_path: str | None = None) -> dict:
    """Returns {"claims": [...], "skipped_incomplete": [...], "scored": {...}}."""
    run_dirs, skipped = eligible_run_dirs(runs_root)
    scored = score_backends(run_dirs)
    verifiable = bool(exchange_root and analysis_path
                      and os.path.isfile(analysis_path))
    claims = []
    for backend, result in scored.items():
        matched = bool(
            backends_root
            and os.path.isfile(os.path.join(backends_root, backend, "backend.yaml")))
        evidence = []
        for run in result["runs"]:
            entry = {"kind": "matched-pair-run", **run}
            if verifiable:
                run_dir = os.path.join(runs_root, run["run"])
                if verify_sweep_seed(run_dir, HISTORICAL_SWEEP_SEED,
                                     exchange_root, analysis_path):
                    entry["sweep_seed"] = str(HISTORICAL_SWEEP_SEED)
                    entry["sweep_seed_basis"] = "reconstructed-and-verified"
            evidence.append(entry)
        claims.append(build_claim(
            subject_source_id=backend,
            subject_matched=matched,
            construct=REVIEW_DEFECT_DISCRIMINATION,
            metrics=result["metrics"],
            custody="historical-seed",
            as_of=SEED_AS_OF,
            evidence=evidence,
            notes=SEED_NOTES + ([
                f"repeated case trials: {result['repeated_case_trials']} of "
                f"{result['metrics']['n_pairs']['value']} pairs re-measure a "
                "case already measured for this subject"]
                if result["repeated_case_trials"] else []),
        ))
    return {
        "claims": claims,
        "skipped_incomplete": [os.path.basename(d) for d in skipped],
        "scored": scored,
    }
