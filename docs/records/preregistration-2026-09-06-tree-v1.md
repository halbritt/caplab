# Pre-registration for the tree-v1 review cohort (plan §5)

- Date: 2026-09-06, before the dry run. Environment `tree-v1`; seed
  20260819; 69 cases; labels as revalidated on 2026-09-06
  (`revalidation-2026-09-06-tree-v1-labels.md`). Base classes from
  `advisory/tree-v1-bases.json` (sha256 recorded on every run summary).
- Order: Sol (`codex-sol-high`) and Gemini 3.8 (`agy-gemini-3-8-flash-high`)
  first, two lanes each. The stop rule is read on their decision-grade cells
  before any other binding runs.

## Cells and denominators

The draw by profile and base class. "Sound controls" uses the scoring key
(`advisory_control_context`: repo-doc controls by substrate id, exchange
controls by dispatch id, with the 2026-09-04 aliases), the same key
`scripts/tree_v1_stoprule.py` reads; the pairs are those both arms answered
in the iso-v1 run, so tree-v1 denominators are read at run time from the
same tool and may differ by a pair or two.

| profile | base class | pairs (draw) | sound controls (iso-v1, Sol/Gemini 3.8) | grade |
|---|---|---|---|---|
| v1-tree (repo-doc) + v3-changeset | whole-tree | 33 | 16 | **decision** |
| v1-tree (prose) | none-by-design | 18 | 15 | **decision** (coverage reading, see below) |
| v3-changeset | partial-product-tree | 8 | 3 | diagnostic |
| v3-changeset | lost | 10 → 7 scorable | 4 | diagnostic |

(Whole-tree pools the 26 repo-docs and the 7 whole-tree change sets; the
iso-v1 rows count 27 whole-tree pairs because iso-v1 scored the change
sets under v2. The paired reading uses the intersection.) Three `lost`
pairs (2 `base_dropped`, 1 `hash_mismatch`) are unscorable by rule and
appear in no denominator. Every per-operator cell within a class has
n ≤ 3 and is diagnostic-only.

**Floor.** The confidence method is the exact two-sided sign test on
discordant pairs, the method the board already uses for "established". Two
sides at 0.05 need 6 one-directional discordant pairs (2·0.5⁶ = 0.031; 5
give 0.0625). A cell is decision-grade only if its denominator is ≥ 6 on
the direction read; the two decision-grade classes are read as paired
changes from the same binding's `iso-v1` rows on the same cases, never
against a global historical figure.

## iso-v1 baselines on the same cases (audited labels, scoring key)

| binding | class | catch | refusals of sound controls |
|---|---|---|---|
| Sol | whole-tree | 25/27 | **16/16** |
| Sol | none-by-design | 17/17 | **15/15** |
| Sol | partial | 4/5 | 3/3 |
| Sol | lost | 6/8 | 0/4 |
| Gemini 3.8 | whole-tree | 23/27 | 2/16 |
| Gemini 3.8 | none-by-design | 14/17 | 2/15 |
| Gemini 3.8 | partial | 3/5 | 0/3 |
| Gemini 3.8 | lost | 4/8 | 0/4 |

*Amendment, same day, before any tree-v1 row:* the first draft of this
table read 21/21, 17/17, 5/5 and 4/8 for Sol, counted with a looser
control key (substrate id, then dispatch id, unaliased) that left five
adjudicated-defective controls in the sound denominator. The numbers above
are from the scoring key. The bounds below were restated on them.

## Pre-registered expectations and the stop rule

**Sol, whole-tree (decision-grade, both directions).**
- Refusals of sound controls fall from 16/16 to **at most 4/16** (the
  pre-isolation rate on this seed was 0.196). The paired reading: at least
  6 sound controls Sol refused under `iso-v1` are cleared under `tree-v1`
  with none moving the other way (p ≤ 0.031).
- Catch held: no established fall. Pooled catch on the 33 whole-tree pairs
  **≥ 27/33 (0.82)**, and the paired sign test on shared cases does not
  establish a decrease.
- Stop: refusals stay above 4/16 with references that resolve in `base/`
  → the plan stops for a rethink ("tree present, still refusing"). Catch
  below the floor → a separate rethink; no auto-continue.

**Sol, none-by-design (decision-grade for FA; a coverage reading).**
- Production pinned nothing for these; the contract says so. Expectation:
  refusals fall only to the extent the statement is honoured. Recorded as
  a **finding about the production affordance**, not a stop, whatever the
  number. High refusals here with §3 coverage at zero is exactly what
  `finding-2026-09-06-prose-reviews-world-blind.md` predicts.

**Gemini 3.8, whole-tree.** Refusals stay ≤ 3/16 (no rise established);
catch ≥ 23/27 on shared cases (no fall established). `dangling_reference`
and `hash_mismatch` v3 are expected to rise but are diagnostic cells.

**Every agentic binding (diagnostic, read at step 8).** Structural catch
rises; `hash_mismatch` v3 caught by at least the top three bindings on the
whole-tree change sets (1 pair each — direction only); `base_dropped`
caught by all on whole-tree; `anchored` rises.

**The two one-shot lanes** (`or-gemini-3-7-flash-high`,
`glm-5-3-max` lane if run): no material change (a single API call cannot
open `base/`; the declaration states this). A material change would be a
contamination finding, not a result.

**Tier-1 question** (Gemini 3.8 vs fable 5.1): asked again on this cohort;
no expectation recorded.

## What is not pre-registered

Operator-level cells, the partial and lost classes, and every contrast
between bindings other than the two named above are reported
descriptively. They can neither trip nor pass the stop rule.
