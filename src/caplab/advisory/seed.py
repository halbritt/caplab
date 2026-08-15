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


def seed_claims(runs_root: str, backends_root: str | None = None) -> dict:
    """Returns {"claims": [...], "skipped_incomplete": [...], "scored": {...}}."""
    run_dirs, skipped = eligible_run_dirs(runs_root)
    scored = score_backends(run_dirs)
    claims = []
    for backend, result in scored.items():
        matched = bool(
            backends_root
            and os.path.isfile(os.path.join(backends_root, backend, "backend.yaml")))
        evidence = [
            {"kind": "matched-pair-run", **run} for run in result["runs"]
        ]
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
