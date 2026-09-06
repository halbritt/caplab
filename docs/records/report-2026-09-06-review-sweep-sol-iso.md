# Sol under isolation: catches 91%, refuses 90% — the instrument's clearest rejecter

- Date: 2026-09-06. `codex-sol-high` on matched-pair defect injection
  (synthetic contract), seed `20260819`, environment `iso-v1`, two lanes,
  `scripts/supervise_sweep.py`. Run root
  `advisory/pool-runs/iso-codex-sol-high-20260819/`, 69/69 usable. Claim
  `qc-e46247d9e3ec8681`. Contrasts
  `advisory/comparisons/iso-codex-sol-high-vs-*-20260906.json`.
- Every one of Sol's 65 control refusals is adjudicated
  (`adjudication-dossiers-2026-09-06-sol-iso.md`); the false-alarm rate
  below is not an upper bound.

## Results (iso-v1 cohort, 57 scored pairs)

| binding | catch | false alarm | catch − FA | anchored |
|---|---|---|---|---|
| `codex-sol-high` | **0.912** | **0.895** (34 of 38 sound controls) | **0.018** | 0.526 |
| `agy-gemini-3-8-flash-high` | 0.772 | 0.100 | 0.672 | 0.579 |
| `claude-fable-5-1-high` | 0.667 | 0.098 | 0.569 | 0.579 |
| `agy-gemini-3-7-flash-high` | 0.596 | 0.026 | 0.570 | 0.526 |

Matched contrasts, Sol against each of the seven: catch **established in
Sol's favour every time** (10–2 over Gemini 3.8, p=0.039; 16–2 over fable 5.1;
20–2 to 24–1 over the rest, p ≤ 0.001); false alarm **established against
Sol every time** (27–0 to 34–0 discordant pairs, p < 0.001). Eight
established splits; no leads.

## What happened

Sol refused 65 of 69 controls. Of those, 19 sat on controls the audits have
proven defective — Sol was right there, as it was in August — and 34 sat on
adjudicated-sound controls. Its refusals of sound controls have one shape:
*the referenced document is not included in or reachable from the artifact,
so the claim cannot be verified.* Under `iso-v1` the base tree is withheld
and the review preamble says to judge only the material presented; Sol
complies by treating every unresolvable reference as a blocker. Sixteen of
its seventeen freshly audited refusals were of that kind (the seventeenth,
the architecture-lint entrypoint packet, was a genuine catch).

Before isolation, on the same seed with the live checkout visible, Sol
measured catch 0.965, false alarm 0.196, catch − FA 0.77 — the best number on
the fleet. Isolation did not touch its catch. It moved its false-alarm rate
from 0.20 to 0.90 by removing the tree it used to resolve references
against.

## Reading

**This is the environment interacting with a review posture, and it is real.**
A reviewer that refuses whenever it cannot verify is exactly right when the
tree is there and exactly useless when it is not; the instrument measured
that, correctly. Under `iso-v1` Sol is a rejecter, not a discriminating
reviewer: its discrimination is 0.02, and its catch rate says nothing on its
own because it would have refused the mutants whether or not they carried a
defect.

**It does not follow that Sol is a bad reviewer.** It follows that Sol's
declared placement (`review: frontier` on the pre-isolation 0.768) describes
a binding with checkout access, and that the isolation cohort describes a
task Sol treats as unanswerable. Which of the two is the production task is
striatum's question: production review lanes have the tree, so the
pre-isolation number is the closer analogue for placement — while the
isolation number is the one that compares to the other seven on this board.
The board shows Sol as a split against everyone and says why; it does not
put Sol in a tier.

**Structural catch is not the story here.** Sol caught 31/33 structural and
24/24 semantic defects — but so would a binding that refused everything.

## Findings for the instrument

- The `iso-v1` environment plus the "judge only what is presented" preamble
  makes *reference resolvability* a dominant refusal ground for a binding
  with Sol's posture. A `tree-mounted` successor (the base materialized in
  the workspace, as the P2b record already proposed for planning) would
  separate "cannot verify" from "verified false" and is the right next
  environment for review as well.
- Sixteen sound-control audits in one day were the same out-of-contract
  allegation. The audit standard handled them mechanically, but a control
  set that invites the same refusal sixteen times is measuring the
  environment's reference density more than the reviewer.

## Owed

- `tree-mounted` review environment, then Sol re-measured on it.
- `claude-opus-5-high` under `iso-v1` (running, launched 2026-09-06).
