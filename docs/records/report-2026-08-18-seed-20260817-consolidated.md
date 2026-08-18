# Consolidated results — seed 20260817, synthetic-contract instrument

- Date: 2026-08-18
- Case set: seed 20260817, open partition, 57 breadth cases + 12 anchors,
  identical draws and injections for every Binding below.
- Runs: `sweep-agy-gemini-3-7-flash-high-20260817b` (repaired),
  `sweep-agy-gemini-3-7-flash-medium-20260817`,
  `sweep-claude-harm-fable-5-high-20260817b` (aborted, no claim).

## Scored claims

| Binding | claim | pairs | catch | false alarms | discrimination | anchored |
|---|---|---|---|---|---|---|
| agy-gemini-3-7-flash-high | `qc-fc8146093574b024` | 55 | 0.891 (0.78–0.95) | 0.130 (denom 54, 1 defective excluded, 7 unaudited) | 0.761 | 0.691 |
| agy-gemini-3-7-flash-medium | `qc-74e47b03b461d218` | 57 | 0.702 | 0.107 (denom 56) | 0.595 | 0.526 |
| claude-harm-fable-5-high | **no claim** | 27 clean of 57 | — | — | — | — |

The fable run aborted twice on the account's Fable sub-limit (9 consecutive
empty lanes each time) and yields no claim under the aborted-run rule. Its
27 cleanly measured breadth pairs read, descriptively only: catch 18/27,
false alarms 3/27. Twenty-one cases remain; one quota window finishes it.

## Matched contrasts — the campaign's product

**Established** (both runs complete, `advisory/comparisons/gemini-3-7-flash-high-vs-medium-20260817.json`):

- **high vs medium: distinguishable on catch, not on false alarms.**
  12 of 55 shared cases discriminate, 11–1 in high's favor, exact sign test
  p = 0.006. False alarms: 3–2 discordant, p = 1.0 (9 of those pairs on
  unaudited controls). The discordant cases span nine operators.

**Preview only** (fable side truncated by the abort; not claims, will be
superseded by the completed run):

- high vs fable, 26 shared clean pairs: catch discordance 8–1 in high's
  favor, p = 0.039; false alarms 5–2, p = 0.45. Direction agrees with the
  2026-08-15 dispatch-instrument finding that granted flash-high FRONTIER.
- medium vs fable, 27 shared: catch 5–5, p = 1.0. Indistinguishable.

## Within-Binding consistency is a property of the Binding

Anchor-set replicate agreement (refuse/clear, null pairs excluded), per
subject on the same 12 anchor cases:

| Binding | control pairwise (kappa) | mutant pairwise (kappa) |
|---|---|---|
| claude-harm-fable-5-high | 89% (0.68) | 89% (0.75) |
| agy-gemini-3-7-flash-medium | 89% (0.54) | 89% (0.60) |
| agy-gemini-3-7-flash-high | 69% (0.13) | 87% (0.22) |

What the reliability block measures is subject self-consistency, not a
property of the instrument alone: flash-high — the strongest catcher — is
also by far the least self-consistent, while fable reproduces its own
verdicts at kappa 0.68–0.75. Within-Binding variance limits confidence that
a between-Binding difference is real, so contrasts against flash-high need
more evidence per case than contrasts among its steadier siblings.

## Promotion gate

0 of 12 discordant cases promoted; all withheld as "reproduction not
established". One seed is one observation. The cheapest path to first
promotions is the same pair on a second seed.

## Control soundness, current ledger

Two controls adjudicated defective by mechanical oracle (`e57c4ab7`,
`ee05d12f`); six hash-mismatch refusal grounds refuted by production-
arithmetic replay (`advisory/checks/hashcheck/`); five refuted refusals
await the Principal's sound/defective call; four 2026-08-16 matched-run
refusals remain unaudited.

## What this does not establish

- Nothing claim-grade about fable-5-high on this instrument until its run
  completes.
- No promotion-grade separation: every contrast is one seed deep.
- The false-alarm axis still carries unaudited refusals on both gemini
  claims.
- Nothing about the sealed partition.
