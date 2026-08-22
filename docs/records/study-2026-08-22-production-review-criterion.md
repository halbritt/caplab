# Study — production review against its downstream criterion

- Date: 2026-08-22. Source: the striatum ledger (253,757 records), all
  1,670 production `packet-review` gate results, every one attributed to
  its reviewer Binding via the review evidence's producing run.
  Reproducible: `scripts/production_review_study.py <ledger-dump>`.
- Origin: the build-corpus question "can anything be made from it?" — this
  is the criterion-validity study, redesigned after the pipeline's order
  made the naive version impossible.

## Finding 0 — review cannot predict packet-checks, by construction

Mechanical checks gate BEFORE judgment review: every reviewed subject
already passed `packet-checks`. "Does review predict the mechanical
outcome?" is unmeasurable in this pipeline — review's entire value is
what it adds beyond the mechanical gate. The measurable criterion is
downstream: what happened to the artifact after the verdict.

## Finding 1 — refusals are never noise: zero flip-flops in 461

Of 461 production refusals: **336 (73%) were vindicated** — the artifact's
content changed and the changed version passed; **0 were flip-flops** —
not one identical artifact was later waved through; 125 remain unresolved
(work pending or abandoned). Caveat stated plainly: vindication means the
refusal was *actionable*, not proven correct — an author may revise in
deference to any feedback. The zero-flip-flop count is the strong claim:
the process never overruled a refusal on unchanged content.

## Finding 2 — reviewer temperament spans 0% to 79% on the same pipeline

| reviewer | reviews | refusal | vindicated / refusals |
|---|---|---|---|
| codex-sol-max | 227 | 78.9% | 77 (+102 unresolved) |
| codex-harm-sol-max | 209 | 43.1% | 79 of 90 |
| codex (generic) | 118 | 57.6% | 61 of 68 |
| claude-fable-5-high | 29 | 48.3% | 14 of 14 |
| claude-harm-fable-5-high | 67 | 29.9% | 20 of 20 |
| claude-harm-opus-5-high | 82 | 20.7% | 17 of 17 |
| agy-gemini-3-1-pro-high | 291 | 10.7% | 31 of 31 |
| **agy-gemini-3-7-flash-high** | **66** | **0.0%** | — |
| agy-gemini-3-6-flash-* | 252 | ~3.5% | 8 of 9 |
| local-qwen | 116 | 5.2% | 6 of 6 |

Where refusals resolve, vindication runs 88–100% for every reviewer except
codex-sol-max (43% vindicated, 102 still unresolved from its refusal
sprees).

## Finding 3 — the Revbench↔production paradox

`agy-gemini-3-7-flash-high` — Revbench catch 0.842, discrimination 0.681,
the projection's dispatch-cohort leader — refused **zero** of 66 production
packets. The synthetic instrument shows it refuses 16% of *sound* controls;
production shows it refusing nothing that passed mechanical checks.
Meanwhile the codex family's Revbench FA excess reproduces exactly as
production temperament (43–79% refusal rates).

Two readings, not resolved by this data: (a) checks-passing production
work is genuinely clean and flash clears it correctly — in which case the
codex refusal sprees are largely production false alarms; (b) flash
under-refuses organic defects that don't resemble planted ones. The
natural-defect instrument (packet-checks-failed change sets as review
subjects, proposal #2 from the build-corpus assessment) is the experiment
that separates these readings.

What transfers from Revbench to production is **temperament** (FA/refusal
posture, cleanly); what does not visibly transfer is **catch** — because
the checks-gated population offers almost nothing organic to catch, or
because planted and organic defects differ. That question is now precise.

## Caveats

Assignment is non-random (the scheduler routes reviews); populations
differ per reviewer; vindication is deference-confounded; eras mix
declaration versions. No Scored claims are minted from this study — the
production refusal rate is temperament + assignment, not fitness, and
CAPLAB does not launder observations into claims.
