# Confirmation — supplying the contract restores detection

- Date: 2026-08-16
- Follows:
  [`finding-2026-08-16-calibration-not-measurement-equivalent`](finding-2026-08-16-calibration-not-measurement-equivalent.md)
- Disposition: the finding's diagnosis is confirmed experimentally, and its
  proposed corrective is narrowed to something much cheaper.

## The experiment

The same reference binding (`agy-gemini-3-7-flash-high`), the same 11 cases,
the same injections, the same day. The only variable is the calibration
prompt: profile **v0** states "review this artifact for defects"; profile
**v1** additionally states the review contract — completeness for stage,
internal consistency, resolvable references, declared metadata matching
content, earned claims, and stage-appropriate scope — as general reviewer
obligations. v1 deliberately does not name any defect class.

| | caught | control false alarms | discrimination |
|---|---|---|---|
| v0 (no contract) | 3 / 11 | 0 | 0.27 |
| v1 (contract) | 8 / 11 | 0 | 0.73 |

Per case:

| operator | v0 | v1 |
|---|---|---|
| `dropped_section` ×2 | miss, miss | CATCH, CATCH |
| `swapped_section_bodies` | miss | CATCH |
| `requirement_inversion` | miss | CATCH |
| `hollow_delivery` ×2 | miss, CATCH | CATCH, CATCH |
| `contradicted_clause` | CATCH | CATCH |
| `broken_internal_crossref` | CATCH | CATCH |
| `overclaimed_level` | miss | miss |
| `hash_mismatch` | miss | miss |
| `dangling_reference` | miss | miss |

## Why the false-alarm column is the important one

A contract-bearing prompt could raise catches simply by making the reviewer
refuse more — a leading prompt, which would inflate detection and destroy
the measurement. The matched-pair design tests for exactly that: a reviewer
made trigger-happy refuses control arms too. **Controls stayed clean in both
profiles: zero false alarms across 22 control reviews.** The five flipped
cases are a gain in discrimination, not in strictness.

## Disposition of the 11 cases

- **8 → `validated-hard`.** Detectable by a strong reference when the
  contract is supplied, missed without it. They enter the pool.
- **3 remain pending** — `overclaimed_level`, `hash_mismatch`,
  `dangling_reference`. One strong reference missing a case does not
  quarantine it; governance requires 2–3 references, and the second must
  come from a different aliasing class than `google-gemini` to be
  independent. The strongest non-Google bindings are Anthropic-family, whose
  quota is currently exhausted, so these three stay pending rather than
  being resolved on a single family's opinion.

## Narrowing the corrective

The finding proposed wiring the case pool into the instrument's dispatch
prompt path, and noted repo-doc substrates would additionally need synthetic
manifests. This result shows the load-bearing ingredient is narrower than a
manifest: it is **the contract itself**. A stated contract restored
detection on repo-doc substrates that have no dispatch bundle at all.

That does not make v1 equal to the measurement prompt — the instrument
renders a specific posture, pins, and expected outputs, and cases validated
under v1 are validated for a contract-bearing review task rather than for
that exact dispatch. But it does mean:

- repo-doc substrates are calibratable today, and their earlier
  "unmeasurable" status is too strong — they are *unmeasurable by the
  instrument as currently wired*, not intrinsically;
- a synthetic contract is a viable route to making them measurable, and is
  far cheaper than synthesising whole manifests;
- profile v0 is confirmed unfit for admission decisions and remains a smoke
  test only.
