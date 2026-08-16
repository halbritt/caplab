# AFK campaign report — advisory-selection-001 — 2026-08-15

Endorsed scope: Tier 1 (offline pipeline) + Tier 2 (bounded Gemini 3.7 Flash
live runs, ≤21 pairs × 3 tiers, ~$10 cap) + Tier 3 (corpus expansion, added
mid-flight with the case-validation floor rule). All three tiers completed.
Everything below is committed and pushed (caplab branch
`advisory-selection-001-scaffold`, quartermaster `master`).

## Headline results

**Gemini 3.7 Flash is not "incapable of review" — it is currently the
strongest measured review family in the fleet.** Fresh advisory-grade
matched-pair runs (22 usable pairs each, zero false alarms across all 66):

| Tier | Catch | False alarms | Anchored (of caught) | Discrimination |
|---|---|---|---|---|
| low | 41% | 0% | 89% | 0.41 |
| medium | 68% | 0% | ~100% of catches anchored (claim: anchored_detection 0.68) | 0.68 |
| high | **77%** | **0%** | 88% | **0.77** |

For scale: the best historical-seed binding is claude-fable-5-high at catch
57% / fa 0% / discrimination 0.57 (n=21). Cross-custody caveat: fresh runs
drew cases with sweep seed 20260815 vs the seed corpus's 20260807 — case
sets differ, so claude-class bindings deserve fresh supervised runs before
firm cross-family ordering. The declared `review: baseline` classes on the
3.7-flash declarations (inherited from 3.6 siblings) are contradicted by
this evidence; updating them is striatum's decision, not CAPLAB's.

## What now exists

- **quartermaster** (`halbritt/quartermaster`, private): consumer-neutral
  registry. 82 binding projections from striatum-next backends@3e59360,
  availability observations, 58 scored claims (55 historical-seed + 3
  caplab-advisory), objective-spec projection CLI, example objective +
  derived ranking. 8 tests green.
- **caplab.advisory**: shared scorer (corrected-anchor rescoring from
  retained arms only), seed admission verified against the tuner rescore,
  advisory-grade executor profile v0 (receipts, completed-run marker, hard
  pair-budget refusal), sweep planner (`caplab.advisory sweep`,
  supervised-only guard for claude/codex, plan-by-default, no timers),
  export `caplab-advisory-export/1`. Repo gate `make check` green.
- **Corpus (Tier 3)**: substrate registry of 587 (387 fate-final exchange
  subjects + owned-repo docs), sealed(146)/open(441) hash partition,
  class-balanced per-sweep sampling, 5 new checkable operators, calibration
  harness. First weak-reference batch: 23/28 calibrated; all five new
  operators produced weak-reference-catchable cases; 11 pending strong
  reference; 1 noisy control flagged. Key finding: the historical 34-
  distinct-injection ceiling was the fixed sweep seed, not the pool — the
  pool supports thousands of distinct cases.
- **Docs**: advisory README, case-pool governance (with your floor rule as
  the admission protocol), code-review construct design scaffold (T3.4),
  ADR 0064 **draft awaiting your acceptance**.

## Incident: live-tree branch switch (unresolved author)

At 19:15:51Z, ~/git/striatum-next was checked out from `main` (3e59360) to
`test-branch` (e17177a, an Aug-14 state) — stranding a live agy lane whose
declaration file vanished, and removing today's bootstrap pin and scheduler
v27 from the tree the 5-minute wake timers plan from. I restored `main` at
~19:44Z (test-branch preserved as a ref; nothing lost) and notified the
striatum drive-loop peer session, which verified the restore and audited the
window damage (two qualification-filter escalations individually adjudicated
and re-planned; stale packet-check attempts handled mechanically). **The
drive-loop session states the checkout was not its doing, and it was not
mine: the author is unidentified.** Worth your review; if it was your own
pre-AFK action, the repo's worktree discipline (one worktree per branch,
outside the checkout) is the safe way to repeat it.

## Spend and boundaries

- Paid API: 3 × ~22 pairs + 1 smoke + 1 probe through agy (gemini-flash
  class; agy exposes no per-call cost — bounded by pair count, well inside
  the ~$10 cap).
- Local: calibration batch on the llama.cpp endpoint (free).
- Zero claude/codex live runs; striatum-next never modified (the restore
  returned it to its own state); no timers enabled; no qualification
  artifacts created.

## Recommended next steps (yours to pick up)

1. Accept/amend ADR 0064; decide whether striatum's 3.7-flash declarations
   get re-based on this evidence (striatum's call).
2. Supervised session: fresh claude/codex-class runs (`caplab.advisory
   sweep` already plans them as supervised-only) for firm cross-family
   ordering, and strong-reference validation of the 11 pending calibration
   cases.
3. Investigate the test-branch checkout author (shell history, other
   sessions).
4. When ready: council/UIPass objective specs against quartermaster; the
   example spec shows the pattern.
