# Seed 20260819 — does the separation reproduce?

- Date: 2026-08-19
- Case set: seed 20260819, open partition, 57 breadth cases + the 12 pinned
  anchors. Same instrument, sampling rule, replication (control r=3, mutant
  r=1), adjudication ledger and promotion gate as seed 20260817.
- Subjects: `agy-gemini-3-7-flash-high`, `agy-gemini-3-7-flash-medium`,
  `codex-harm-sol-max`.

The draw shares **zero dispatch ids** with seed 20260817 and only 12 of 640
substrates, so this is reproduction on independent cases, not a replay.

## The Sol Binding

The Principal named `gpt-5.6-sol-high`. The canonical tuple at that model and
effort is `codex-sol-high`, and it is the wrong Binding for this instrument
twice over: it is `status: disabled` on a quota-exhausted account (probed
2026-08-19, "try again at Aug 20th, 2026 3:41 AM"), and it declares
`supported_pass_types: [build]` with review forbidden and no review quality
class — a review claim on it is one Quartermaster could not spend.

`codex-harm-sol-max` is the accepted, live GPT-5.6 Sol tuple that declares
`review: strong`, so it is the Sol Binding this campaign can measure.

## Result: the effort separation reproduces

| contrast | shared | catch discordance | p | verdict |
|---|---|---|---|---|
| flash-high vs flash-medium, seed 20260817 | 55 | 11–1 | 0.006 | separates |
| flash-high vs flash-medium, **seed 20260819** | 57 | **7–0** | **0.016** | **separates** |
| flash-high vs sol-max | — | — | — | not computable |
| flash-medium vs sol-max | — | — | — | not computable |

Seed 20260819 is unanimous in direction: every one of the seven cases that
discriminated was caught by flash-high and missed by flash-medium. Two
independent draws, no shared cases, same direction, both significant.

The seven separators:

| substrate | defect class |
|---|---|
| `qs-5a60742a74305130` | dropped_section |
| `qs-8f41b707cb15f6d9` | dropped_section |
| `qs-afa3ff9b86200498` | dropped_section |
| `qs-a190c423a1dcce98` | hash_mismatch |
| `qs-cabbae40d5c96360` | hollow_delivery |
| `qs-d24d0d472c7a9316` | swapped_section_bodies |
| `qs-ec76afd5d7b27ffd` | overclaimed_level |

False alarms again separate nothing: 4 versus 3 discordant, p = 1.0. Across
two seeds the false-alarm axis has never distinguished any pair. On this
instrument, effort level buys detection and costs nothing measurable in
refusals of sound work.

## Scored claims

| Binding | claim | pairs | catch | false alarms | discrimination | anchored |
|---|---|---|---|---|---|---|
| agy-gemini-3-7-flash-high | `qc-887d2a252d0af193` | 57 | 0.842 | 0.161 (denom 56) | 0.681 | 0.719 |
| agy-gemini-3-7-flash-medium | `qc-7624ac455e0faac0` | 57 | 0.719 | 0.143 (denom 56) | 0.576 | 0.596 |

One control was excluded from the false-alarm denominator by the standing
`defective` adjudication carried over from the 2026-08-17 audit — the ledger
works across seeds without re-adjudication. Twelve pairs still carry
unaudited control refusals.

## Sol did not complete, and is reported as unmeasured

`codex-harm-sol-max` reached 34 usable rows (12 anchors, 22 breadth) before
the OpenAI account hit its window: probed after the abort, it answers "try
again at Aug 22nd, 2026 3:49 PM". A full 69-case sweep at max effort costs
more than one `codex-harm` rolling window holds. Any future Sol sweep needs a
lower-effort tuple, a smaller draw, or a split across windows.

`completed()` refuses an aborted run, so Sol yields no Scored claim and no
contrast. That guard is correct here and was not worked around: cases run in
plan order and plan order groups by operator, so Sol's surviving 22 breadth
rows are skewed by defect class rather than a random subsample of 57.
Contrasting Gemini against that slice would compare on a biased view of the
Construct. **The cross-family question this seed was meant to answer remains
unanswered.**

Its anchor block is still informative, because the anchor set is invariant
and Sol completed all 12: control pairwise 83% (kappa 0.56), mutant 94%.

## Within-Binding reliability

Anchor replicate pairwise agreement, refuse/clear, null replicates excluded:

| Binding | control | mutant |
|---|---|---|
| agy-gemini-3-7-flash-high | 79% (kappa 0.53) | 100% (kappa undefined, arm at ceiling) |
| agy-gemini-3-7-flash-medium | 83% (kappa 0.50) | 87% (kappa −0.17) |
| codex-harm-sol-max | 83% (kappa 0.56) | 94% (kappa −0.03) |

flash-high's control-arm consistency improved sharply from seed 20260817
(kappa 0.13 → 0.53). The mutant-arm kappas are not readable as agreement:
all three subjects refuse nearly every anchor mutant, so chance agreement is
at or near 1.0 and kappa has no room to measure. Where it is undefined the
claim now says so rather than printing a number.

Cross-seed anchor drift on the same 12 cases, 20260817 → 20260819:

| Binding | caught agreement | false-alarm agreement |
|---|---|---|
| agy-gemini-3-7-flash-high | 92% | 83% |
| agy-gemini-3-7-flash-medium | 83% | 83% |

Both anchors moved. That is the instrument's own warning that the Binding or
the instrument changed between seeds, and it does not say which.

## Promotion gate: still zero, for a structural reason

0 promoted, 19 withheld, every one for "reproduction not established: seen in
1 sweep(s)".

This is not bad luck and another seed will not fix it. The gate keys on
`(substrate_id, defect_class, Binding pair)`, and the sampler draws without
replacement from 640 substrates, so two independent seeds share almost no
cells: of 57 drawn cells, **2** recurred across 20260817 and 20260819, and
neither was a separator in either sweep. The diagnostic that relaxes the key
to the substrate alone — the reading `discrimination.py`'s own docstring
describes, "the same substrate separating the same pair under different
injections" — finds **zero** repeats too.

So the corpus cannot fill by drawing more random seeds. Reproduction has to
be *targeted*: replay the cases that separated a pair, the way the anchor set
is replayed, rather than waiting for a random draw to revisit them. The 19
withheld separators from these two seeds are the natural first replay set.

The docstring/key mismatch is left as found. Changing the gate mid-campaign
would change the product, and which reading is meant is the Principal's call.

## Projection: unchanged, and correctly so

Ingested 2 claims; `matched_prefix_depth` stays 2 and ranks 1–2 still resolve
to the **20260815 dispatch-prompt** claims, not to either synthetic-contract
seed. `claim_selection: most-comparable` prefers the widest matched cohort,
and the cohorts are 20260815 with 4 subjects, 20260817 with 3, 20260819 with
2. A second seed on two subjects narrows the cohort instead of widening it.

Even a completed Sol run would have left 20260819 at 3. The synthetic-contract
instrument reaches the projection lead only when one seed carries claims for 5
subjects, or when the 20260815 cohort ages out of the 120-day window on
2026-12-14.

## Defect found and fixed

Claim derivation crashed formatting a null kappa (`TypeError: unsupported
format string passed to NoneType.__format__`). An arm that refuses every
anchor replicate has chance agreement 1.0, so kappa is undefined —
flash-high's mutant arm did exactly that this seed. Fixed test-first;
the note now reads "kappa undefined, arm at ceiling".

## What this establishes, and what it does not

Established: within the gemini-3-7-flash family, effort level separates on
catch, on two independent case draws, unanimously in direction. This is the
campaign's first reproduced separation.

Not established: anything across families. Sol is unmeasured, and fable's
single seed came back "not established" at n=52. The one cross-family
contrast this campaign has ever completed remains its only one.

Also unchanged: the false-alarm axis has never separated any pair, the
promotion corpus is empty and cannot fill by random sampling, and the
projection still ranks on an older instrument.
