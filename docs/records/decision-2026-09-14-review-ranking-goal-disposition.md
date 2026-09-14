# Stop the reviewer ranking goal; file the striatum request

- Date: 2026-09-14. **Principal decision**, not a delegated one: the owner
  asked whether to proceed with CAPLAB, and then directed the filing and this
  record. ADR 0026 does not cover cancelling an owner-activated goal.
- Supersedes the goal activated in ADR 0066 (thread
  `01a08054-82f9-7a32-b0c1-a62c395cd320`). Does not supersede the confirmed
  [review-instrument disposition](report-2026-09-07-review-instrument-disposition.md),
  whose standing orders remain in force with no end date.

## Decision

1. **The striatum request is filed.** The draft
   [request](request-2026-09-07-striatum-review-outcome-events.md), held since
   2026-09-07 for the Principal's signature, is filed as Cairn record
   `4c75c6e0-e5d5-46c6-bb3a-680b75a1eaa5` (kind `decision`, shareable,
   repository scope), reachable by a striatum-next agent. Filing transmits a
   request; it grants striatum no authority and imposes no schedule.
2. **`reviewer-ranking-001` stops as a ranking campaign.** No further case
   admission, witness construction, scorer challenge, or comparative design.
   The queued
   [preview-claims investigation](authorization-2026-09-10-reviewer-preview-claims-witness.md)
   does not run. Nothing is deleted: the census, the 13 bounded witnesses, the
   credit policy, the completion/advisory accounting and the native capture
   substrate are retained as source custody and remain reusable.
3. **CAPLAB keeps three things**, exactly as the 2026-09-07 disposition
   specified: the per-binding admission gate on request only (pass/fail, 67
   calls, not a ranking); the report-only production canary; and operational
   routing among admitted reviewers on cost, latency and availability in
   Quartermaster, never on an injection score.
4. **No ranking of reviewers is published, and none is pending.**

## Why

The ranking question was not blocked by effort or budget. It was blocked by a
fact about the evidence, recorded before this decision and unchanged by it:
on the five operators with a production analog, **eight of nine bindings catch
13/13** ([operator analogs](finding-2026-09-07-operator-analogs.md)). The
ordering the board carried came from operators that plant defects production
does not produce. The same shape recurs across every valid task set CAPLAB has
built — the advisory-selection ladder did not order performance monotonically,
and two of its three prior scenarios sat at ceiling or floor. The working
hypothesis is now that **frontier reviewers do not meaningfully differ in
catch rate on realistic first-pass review**, and that a study designed to
order them is measuring a difference that is not there.

`reviewer-ranking-001` was opened on 2026-09-10, four days after the
disposition reached that conclusion, and pursued ground truth by hand-built
witness instead. One day of concentrated work produced coverage of 13 of 32
sampled changes, two admitted cases — both development-exposed, so neither can
serve as held-out evidence — and a scorer that failed its challenge twice on a
repeated pre-append/post-append citation error. Its own gate table requires a
frozen held-out set on top of that. The cost is real and the prior on the
result is a tie.

What remains true is the reverse finding: false-alarm behaviour **does**
separate subjects, and by a wide margin — 34 versus 1 across 57 shared cases
at p=2.3e-10 on the 2026-09-06 iso-v1 contrast. That axis stays descriptive
under the iso-v1 caveat and is not reopened here; it is recorded because it,
not catch rate, is where a future question should start.

## What this does not decide

- No qualification release, no D0019 work, and no disposition of the striatum
  bootstrap-qualification pin expiring **2026-09-21**. That renewal remains a
  deliberate Principal act and is not made by this record.
- No change to the advisory ledger, the Quartermaster registry, existing
  permitted review tuples (#40, #41), or Sol's provisional `review: frontier`
  placement.
- No judgment on whether striatum implements any of the seven requested items,
  which is striatum's to make.
- The criterion replay stays **parked**, not abandoned. It un-parks if and when
  the ledger holds >=5 gold-defect and >=5 gold-clear cases at the incident
  level, which requires request item 1.

## Inference flagged for correction

The owner directed items 1 and this record explicitly. Items 2 and 3 are the
primary agent's reading of the owner's framing ("whether to proceed ... or
simply to cancel it") together with the recommendation the owner acted on. If
the intent was to keep `reviewer-ranking-001` open, this record is wrong in
item 2 and should be corrected rather than worked around.
