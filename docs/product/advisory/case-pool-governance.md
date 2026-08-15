# Case-pool governance

Rules for the expanded matched-pair case pool (Tier 3 of
advisory-selection-001). A **case** is `(substrate, operator, seed)`; the
registry of substrates is `advisory/substrates.jsonl`, harvested with
lineage from the striatum exchange (fate-final subjects only — the
exhaust-as-cases miner) and from owned repositories' structured documents.

## Why this exists

The historical sweep reused one fixed seed, so 97 runs and 1,006 pairs drew
from only 34 distinct injections, with base_dropped alone 29% of all pairs.
The pool now holds ~587 substrates across 14 operator classes; the rules
below keep that breadth honest.

## Partitions

Every substrate is deterministically assigned by identity hash: **sealed**
(~25%) or **open**. Sealed substrates are never sampled for advisory sweeps
and are reserved for later qualification-grade evaluation, so advisory
exposure cannot leak into a future qualification corpus. A substrate's
partition never changes — the hash decides, so re-harvesting cannot migrate
it. Descendants of a substrate (revisions, retries, same artifact family)
belong in the same partition; the harvest records lineage so this is
checkable.

## Per-sweep sampling

`sample_cases(sweep_seed, per_operator)` draws a class-balanced sample from
the open partition; injection seeds derive from `(sweep_seed, substrate,
operator)`, so distinct sweeps draw distinct injections from the same
substrate. Class balancing is the standing corrective for the historical
skew. A sweep records its seed and sample; two bindings compared within one
sweep see identical cases (matched pairs), and no ranking compares numbers
across sweeps without noting the case-set difference.

## Case admission: validate the test before it scores anyone

Principal guidance (2026-08-15): *when testing new cases, run known bindings
that should pass; if they don't, question the test — then sample cases to
find the floor below which bindings don't pass.*

Protocol:

1. **Mechanical gate** (always): the operator's checker must confirm the
   defect present in the mutant and absent from the control, or the case is
   discarded before any model sees it.
2. **Weak-reference calibration** (free, local): every sampled case runs
   against the local reference reviewer. A clean catch marks the case
   `at-or-below-easy-floor`; a control-arm refusal marks it
   `weak-reference-noisy` (suspect substrate: the "sound" control may carry
   a real latent defect); a miss leaves it `pending-strong-reference`.
3. **Strong-reference validation** (supervised sessions; burns subscription
   windows): `pending-strong-reference` cases run against 2–3 reference
   bindings with the best measured discrimination (fable-5-high class). A
   case that ALL strong references miss is quarantined `suspect-case` — the
   test is questioned, not the bindings — and only a human decision can
   admit it as a genuinely-hard case afterward.
4. **The floor**: per-case difficulty estimates accumulate across
   calibrations. Cases below the floor (nothing passes) are excluded from
   scoring pools; cases below the easy floor (the weak reference passes)
   still count but cannot alone distinguish strong bindings, and per-sweep
   sampling keeps a difficulty mix.

Calibration results are case QA and never become scored claims about any
binding.

## New operators

CAPLAB-authored operators (`operators.py`) ship `validation: pending` and
must clear the admission protocol on a sample of their cases before their
defect class enters a scored sweep. The vendored instrument classes carry a
grandfather note: their behavior in the historical sweep is itself evidence
of detectability at strong bindings.
