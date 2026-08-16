# Finding — the calibration harness is not measurement-equivalent

- Date: 2026-08-16
- Disposition: **instrument impeached, not the cases.** No case is
  quarantined on this evidence. Goal stop condition invoked: the instrument
  is fixed before any further scoring.

## The result that raised it

Strong-reference validation of the 11 `pending-strong-reference` cases
against `agy-gemini-3-7-flash-high` — the strongest reviewer CAPLAB has
measured (catch 77%, false alarms 0%, 88% of catches anchored) — returned 8
of 11 as strong misses. A binding that strong missing three quarters of a
sample is a claim about the sample, or about the harness. It was the
harness.

## The evidence

The same binding, on the same defect classes, measured two ways on the same
day:

| Defect class | Real instrument | Calibration harness |
|---|---|---|
| `dropped_section` | 3/3 caught | 0/2 |
| `hash_mismatch` | 3/3 | 0/1 |
| `overclaimed_level` | 2/2 | 0/1 |
| `contradicted_clause` | 4/4 | 1/1 |
| `dangling_reference` | 1/2 | 0/1 |
| `hollow_delivery` | 1/1 | 1/2 |

The classes that invert are exactly the **contract-relative** ones. Under
the real instrument the subject receives the striatum dispatch prompt: the
review posture, the stage contract, the manifest with its pins and expected
outputs. That is what makes "the required Consequences section is absent" or
"this declared hash does not match its content" a refusable finding.

`caplab.advisory.calibrate.REVIEW_PROMPT` supplies none of it. It says, in
substance, "review this artifact for defects." Given no contract, a document
missing a section it was never told it needed is a document with no visible
defect, and `accept` is a defensible answer rather than a miss. The harness
was measuring whether a reviewer can infer an unstated contract — a
different construct, and not the one under test.

## Disposition of the 11 cases

- 8 `strong-miss-quarantine-candidate` → **`unresolved-harness-not-equivalent`**.
  These verdicts are void for quarantine purposes and are retained only as a
  record of the harness defect.
- 3 `validated-hard` → **`validated-hard-weak-evidence`**. A catch under the
  compact prompt is still a catch; it evidences detectability *without* a
  contract, which is a weaker statement than detectability under the
  measurement prompt.

No case leaves the pool and none is admitted as validated on this run.

## Corrective

Calibration must run cases through the same prompt path the measurement
uses, or its verdicts cannot speak about measurement. Concretely:

1. **Exchange-sourced substrates** (387 of 587, and 4 of these 11) already
   have dispatch bundles, which is precisely what the instrument renders
   from. Wiring the case pool into the instrument's own case selection —
   rather than a parallel harness — makes their calibration equivalent by
   construction. The instrument's existing `--classes` restriction already
   supports per-class difficulty measurement on the real path.
2. **Repo-doc substrates** (200 of 587, and 7 of these 11) have no dispatch
   bundle and therefore no contract to render. They need a synthetic
   manifest that states a stage contract, or they are only usable for
   contract-free defect classes. Until then their difficulty is unknown, not
   high.
3. The compact-prompt harness is demoted to a **smoke test**: it can show
   that a reference answers and parses, and it can flag a noisy control. It
   cannot admit, quarantine, or rank.

## Note on what worked

The failure was caught because the floor rule was followed literally: known
bindings that should pass were run first, and when they did not, the test
was questioned before any case was scored. Had the 8 verdicts been trusted,
five repo-doc cases and three exchange cases — including classes the fleet's
best reviewer catches 100% of the time on the real path — would have been
quarantined as too hard, permanently biasing the pool toward the defects a
context-free reviewer happens to notice.
