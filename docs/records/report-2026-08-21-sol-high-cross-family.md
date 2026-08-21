# Sol-high, seed 20260819 — the first completed cross-family contrasts

- Date: 2026-08-21
- Subject: `codex-sol-high` (primary codex account, re-enabled 2026-08-21 by
  delegated adjudication after its dated disable's exit condition was met).
  Chosen per the Principal's direction of this day: sweep sol-high, never
  xhigh or max — those tuples over-think, carry higher latency and token
  burn, and are not merited until the corpus discriminates with much
  greater confidence.
- Case set: sweep seed 20260819 — the identical 57 breadth + 12 anchor cases
  both flash tuples completed on 2026-08-19, so both contrasts below are
  matched. Same instrument, replication (control r=3, mutant r=1), ledger.
- Run: **69/69 usable in a single attempt, no aborts, no quota trips** —
  despite the account banner reading 100% of its weekly limit at re-enable
  time. The probe-gated supervisor would have stopped cleanly on a wall; it
  never saw one.

## Result: Sol leads both flash tuples on catch

| contrast | shared | discordance | p | direction |
|---|---|---|---|---|
| sol-high vs flash-high | 57 | 8–1 | **0.039** | sol |
| sol-high vs flash-medium | 57 | 15–1 | **0.001** | sol |

The campaign has run three seeds asking the cross-family question; these are
its first two completed answers. On matched cases, `codex-sol-high` catches
what `agy-gemini-3-7-flash-high` misses (8 cases against 1) and dominates
flash-medium outright.

Scored claim (breadth cases only, anchors excluded):

| metric | value | note |
|---|---|---|
| catch | 0.965 (CI95 0.88–0.99) | vs flash-high 0.842, flash-medium 0.719 |
| false alarms | 0.196 (denom 56) | 11 refusals, ALL on unaudited controls |
| discrimination | 0.768 | vs 0.684 / 0.579 on the shared set |
| anchored | 0.772 | |

## The cost, and the standing blind spot

Sol refuses more sound work than either flash tuple (11 false alarms vs 9
and 8 on shared cases) — but the false-alarm axis separates nothing here
either (p = 0.79 / 0.58), extending its perfect record of never
distinguishing any pair. The real debt is the audit: all 11 of Sol's
control refusals sit on unaudited controls, and the pairwise contrasts
carry 17 and 16 unaudited-alarm pairs. After the 2026-08-21 adjudications
proved one heavily-refused control sound and seven others sound, this
backlog is the next place a scoring error could hide. Until it is audited,
Sol's false-alarm rate is an upper bound, not an established number.

## Instrument blocks

Sol's anchor control-arm reliability is the best yet measured on this
instrument: pairwise kappa 0.76 (flash-high's best is 0.67). Mutant-arm
kappa 0.47. One anchor observation worth keeping: Sol *missed* the
`duplicated_section` anchor mutant that the flash tuples catch — at 95.7%
breadth catch, its rare misses are visible only because the anchor set
replays.

## Promotion and projection: both unchanged, both correctly

The gate still holds 7 promoted (the flash effort corpus). The new
sol-pair discordant cells enter at one sweep each and are withheld for
reproduction — a targeted-reproduction sweep against Sol is the path to
promoting cross-family separators, exactly as it was for the flash pair.

The claim is derived, appended to the ledger, and ingested into
quartermaster — and the projection still ranks sol-high on its 20260807
historical-seed claim, because `most-comparable` keys on the lead cohort's
dispatch-prompt instrument. The synthetic-contract cohort at seed 20260819
now carries 3 subjects (flash-high, flash-medium, sol-high) of the 5 needed
to take the lead. Fable-5-high and fable-5-medium at this seed, on the
claude account, would complete it.

## Caveat for the Principal

`codex-sol-high`'s declaration lists `supported_pass_types: [build]` and
declares no review quality class. This measurement is honest CAPLAB fitness
evidence — fitness is deliberately separate from placement — but no
consumer can spend a review claim on this Binding until its declaration is
amended, which is Principal-owned. Given catch 0.965 / discrimination 0.768
on a 57-case matched set, that amendment now has a measured basis if wanted.

Artifacts: run `advisory/pool-runs/sweep-codex-sol-high-20260819/`;
contrasts `advisory/comparisons/sol-high-vs-flash-{high,medium}-20260819.json`;
report reproducible via `scripts/sol_20260819_report.py`.
