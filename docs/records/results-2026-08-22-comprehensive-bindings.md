# Comprehensive review-capability results across all Bindings

- Date: 2026-08-22 · Construct: `review.defect_discrimination/1`
- Sources: `advisory/claims.jsonl` (67 Scored claims), the contrast
  documents in `advisory/comparisons/`, the promotion gate, and the
  quartermaster projection (`objectives/striatum-draft/review.json`).

**How to read this.** Numbers are comparable only within one instrument,
one custody class, and one case seed. Two instruments exist: the
**dispatch-prompt** instrument (renders striatum's real dispatch) and the
**synthetic-contract** instrument (CAPLAB's own contract prompt over the
Tier 3 pool) — they measure different tasks. Two custody classes exist:
`historical-seed` (the pre-CAPLAB 2026-08-07 tuner sweep, single seed,
mostly n=13) and `caplab-advisory` (CAPLAB's own executions, 2026-08-15
onward). Catch = refusals of planted defects; false alarm (FA) = refusals
of sound controls; discrimination = catch − FA.

## 1. Headline picture

- **Strongest measured reviewer:** `codex-sol-high` — catch 0.965,
  discrimination 0.768 on the 57-case seed-20260819 matched set. It beats
  both flash tuples on paired catch (8–1 vs flash-high, p=0.039; 15–1 vs
  flash-medium, p=0.001) — the campaign's only completed cross-family
  contrasts. Caveats in §6.
- **Only reproduced, promoted finding:** within gemini-3-7-flash, effort
  buys catch. Seven (substrate, defect-class) cells separate high from
  medium in the same direction across two independent sweeps each; all
  seven controls adjudicated sound (2026-08-21). Five of seven are
  structural omissions.
- **Never established anywhere:** the false-alarm axis has not separated
  any pair on any seed.

## 2. Fresh CAPLAB-custody claims (2026-08-15 → today)

| Binding | seed | instrument | pairs | catch | FA | disc | anchored |
|---|---|---|---|---|---|---|---|
| **codex-sol-high** | 20260819 | synthetic | 57 | **0.965** | 0.196† | **0.768** | 0.772 |
| agy-gemini-3-7-flash-high | 20260815 | dispatch | 22 | 0.773 | 0.000 | 0.773 | 0.762 |
| agy-gemini-3-7-flash-high | 20260817 | synthetic | 55 | 0.891 | 0.130 | 0.761 | 0.691 |
| agy-gemini-3-7-flash-high | 20260819 | synthetic | 57 | 0.842 | 0.161 | 0.681 | 0.719 |
| claude-harm-fable-5-high | 20260817 | synthetic | 54 | 0.759 | 0.094 | 0.665 | 0.648 |
| agy-gemini-3-7-flash-medium | 20260815 | dispatch | 22 | 0.682 | 0.000 | 0.682 | 0.682 |
| agy-gemini-3-7-flash-medium | 20260817 | synthetic | 57 | 0.702 | 0.107 | 0.595 | 0.526 |
| agy-gemini-3-7-flash-medium | 20260819 | synthetic | 57 | 0.719 | 0.143 | 0.576 | 0.596 |
| claude-sonnet-5-high | 20260815 | dispatch | 14 | 0.571 | 0.429 | 0.143 | 0.143 |
| agy-gemini-3-7-flash-low | 20260815 | dispatch | 22 | 0.409 | 0.000 | 0.409 | 0.364 |

† All 11 of sol-high's false alarms sit on unaudited controls — the rate is
an upper bound until audited. (The 20260817 flash-high row shown is the
repaired 55-pair claim; two earlier partial derivations of that sweep
remain in the ledger.)

## 3. Matched contrasts (paired, same seed, same cases)

| contrast | seed | shared | catch discordance | p | verdict |
|---|---|---|---|---|---|
| flash-high vs flash-medium | 20260817 | 55 | 11–1 high | 0.006 | separates |
| flash-high vs flash-medium | 20260819 | 57 | 7–0 high | 0.016 | **reproduces** |
| flash-high vs flash-medium | 20260820 (targeted) | 19 | 7–0 high | — | 7 cells reproduce, 0 flips |
| **sol-high vs flash-high** | 20260819 | 57 | 8–1 sol | 0.039 | separates |
| **sol-high vs flash-medium** | 20260819 | 57 | 15–1 sol | 0.001 | separates |
| flash-high vs fable-5-high | 20260817 | 52 | — | n.s. | not established |
| flash-medium vs fable-5-high | 20260817 | 52 | — | n.s. | not established |
| flash-high vs sonnet-5-high | 20260816 | 13 | — | 0.375 | not established (n too small) |

False alarms: every contrast's FA sign test is non-significant (p ≥ 0.25).

## 4. Promoted discrimination corpus (7 cells)

All promote flash-high over flash-medium; all controls adjudicated sound
(1 mechanical oracle, 6 Principal rulings, 2026-08-21).

| substrate | defect class | sweeps |
|---|---|---|
| qs-5ebab1a249b89eb2 | dropped_section | 20260817, 20260820 |
| qs-8f41b707cb15f6d9 | dropped_section | 20260819, 20260820 |
| qs-afa3ff9b86200498 | dropped_section | 20260819, 20260820 |
| qs-aae295d9adf3871e | base_dropped | 20260817, 20260820 |
| qs-aba90dbe009e7ea2 | dangling_reference | 20260817, 20260820 |
| qs-d24d0d472c7a9316 | swapped_section_bodies | 20260819, 20260820 |
| qs-ec76afd5d7b27ffd | overclaimed_level | 20260819, 20260820 |

The new sol-pair separator cells (from §3) sit at one sweep each, awaiting
targeted reproduction — the same path this corpus took.

## 5. Quartermaster projection (review objective, derived ranking)

| rank | Binding | score | custody | seed | n |
|---|---|---|---|---|---|
| 1 | agy-gemini-3-7-flash-high | 0.843 | caplab-advisory | 20260815 | 22 |
| 2 | agy-gemini-3-7-flash-medium | 0.785 | caplab-advisory | 20260815 | 22 |
| 3 | claude-harm-fable-5-high | 0.768 | caplab-advisory | 20260817 | 54 |
| 4 | agy-gemini-3-7-flash-low | 0.585 | caplab-advisory | 20260815 | 22 |
| 5 | claude-fable-5-high | 0.533 | historical-seed | 20260807 | 21 |
| 6 | claude-fable-5-medium | 0.497 | historical-seed | 20260807 | 13 |

43 ranked in total; ranks 1–2 are the only matched comparison at the top
(shared custody, seed, instrument). **sol-high ranks 19th** — the
projection's `most-comparable` selection keys on the lead cohort's
dispatch-prompt instrument and so still spends sol-high's weak 20260807
historical claim, not its strong 20260819 one. The synthetic-contract
cohort at 20260819 holds 3 of the 5 subjects needed to take the lead
(fable-5-high + fable-5-medium at that seed would complete it). Notable
exclusions: codex-sol-max (FA 0.55 above the 0.5 ceiling), six tuples
below the 13-pair floor.

## 6. Historical-seed fleet sweep (2026-08-07, dispatch instrument)

Single seed, small n (mostly 13), pre-CAPLAB custody — priors, not
current measurement. Selected rows, best per family first:

| Binding | pairs | catch | FA | disc |
|---|---|---|---|---|
| codex-sol-max | 29 | 0.897 | 0.552 | 0.345 |
| codex-sol-high | 23 | 0.826 | 0.478 | 0.348 |
| claude-opus-5-low | 13 | 0.692 | 0.154 | 0.538 |
| claude-opus-5-medium | 13 | 0.923 | 0.615 | 0.308 |
| claude-fable-5-xhigh | 19 | 0.579 | 0.000 | 0.579 |
| claude-fable-5-high | 21 | 0.571 | 0.000 | 0.571 |
| claude-sonnet-5-high | 13 | 0.846 | 0.385 | 0.462 |
| codex-luna-high | 13 | 0.769 | 0.538 | 0.231 |
| codex-terra-xhigh | 13 | 0.615 | 0.231 | 0.385 |
| agy-gemini-3-1-pro-high | 35 | 0.457 | 0.143 | 0.314 |
| agy-gemini-3-6-flash-high | 7 | 0.143 | 0.000 | 0.143 |
| kimi-k3 | 30 | 0.400 | 0.067 | 0.333 |
| glm | 34 | 0.294 | 0.029 | 0.265 |
| deepseek-v4-flash | 47 | 0.213 | 0.128 | 0.085 |
| local-qwen | 39 | 0.154 | 0.051 | 0.103 |
| local-qwen-ft | 25 | 0.280 | 0.520 | −0.240 |

Two lessons this table already taught: the codex family's historical FA
rates (0.48–0.62) are why sol-max is excluded from the projection, and the
gemini-3-6-flash rows (catch ≤ 0.14) are the stale "incapable of review"
classification that the 3.7 fresh runs refuted.

## 7. Standing caveats

- **Instrument reliability:** anchor control-arm pairwise kappa —
  sol-high 0.76 (best measured), flash-high 0.67, flash-medium 0.29.
  Mutant arms sit near refuse-ceiling, kappa unreadable.
- **Anchor drift:** the anchor set has moved on three consecutive sweeps
  (~92% caught-agreement per subject per step). The instrument cannot say
  whether Bindings or the instrument changed. Uninvestigated.
- **False-alarm audit backlog:** sol-high 11 unaudited refusal pairs, plus
  12 from seed 20260819 and 3 from the 20260820 replay. After 8 of 8
  adjudicated queue controls proved sound, this backlog is where the next
  scoring error is most likely hiding.
- **Declarations:** `codex-sol-high` declares build-only with no review
  quality class — its review claim is fitness evidence a consumer cannot
  spend until the declaration is amended (Principal-owned). Effort cap
  stands: no xhigh/max sweeps (Principal, 2026-08-21).
- **Codex quotas:** primary codex account weekly limit resets 2026-08-27;
  codex-harm account window reopens 2026-08-22 15:49Z. Codex/claude
  runtimes remain supervised-only in the sweep config.
