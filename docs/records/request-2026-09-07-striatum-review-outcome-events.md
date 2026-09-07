# Request to striatum: review-outcome events, for the Principal's signature

- Date: 2026-09-07. Drafted by CAPLAB per
  `instruction-2026-09-07-review-instrument-disposition.md` §4. **Not filed**;
  the Principal files it.
- Attachments: `criterion-2026-09-07-review-ledger-pass.md`,
  `report-2026-09-07-review-instrument-disposition.md`,
  `finding-2026-09-07-operator-analogs.md`.

## Why

CAPLAB tried to validate its review instrument against production outcomes
and could not: over 6,042 anchored change-set reviews the ledger holds no
event that says a review verdict was wrong. Without such events no review
instrument — CAPLAB's or anyone's — can be checked against the Principal's
judgment, and reviewer placement rests on synthetic defects that production
does not produce. The seven items below are what the ledger would need to
carry for that check to become possible. Items 1–6 are requests; item 7 is
a lane-design option for striatum's own decision.

## Requests

1. **A re-ruling event for review verdicts, both directions.** A
   `gate_result` of class `acceptance` (or a new class) whose applicability
   names the **change-set version** (identity, `version_seq`,
   `content_hash`) and whose detail names the **review run overruled**, with
   the direction: wrongly cleared, or wrongly refused. Today the Principal's
   acceptance rulings (404 in the ledger) fall on proposals, designs,
   implementation plans and decision records only; the 174 Principal
   resolutions on change-set escalations are budget dispositions on
   `bounds_exhausted` and do not judge a verdict.
2. **Retention of the rendered dispatch prompt on every review run**, or its
   hash with the object stored. `prompt_asset_hashes` is empty on all 6,042
   anchored runs, and no dispatch directory survives for any of them (the
   exchange retains 469, none a review). The pass-contract object is
   retained (four hash variants, all `contract_version: 2`); the words the
   reviewer actually saw are not.
3. **A budget field on review runs**, time or tokens. No review run carries
   one; the only deadline field is `deadline_class: batch`. Observed medians
   range from 104 s (`claude-harm-fable-5-high`) to 1,952 s (`cc-glm-5-3-max`)
   per review with no stated ceiling.
4. **A review-to-outcome linkage**: `application_record`,
   `integration_conflict`, `cancellation_record` and acceptance rulings
   keyed back to the review run that cleared the version. Today the join is
   by change-set `content_hash` and request, which spreads one cancellation
   over every packet's change set (cancellation 320479 covers 25 versions in
   6 identities) and cannot say which review, if any, was wrong.
5. **The verdict-retention gap.** 2,880 of 6,042 anchored review runs closed
   with no retained verdict body (`canceled` 852, `submitted_partial`
   without a ledger 1,979, `abandoned` 40, `error` 9). Lane design or loss?
   It bounds any future criterion work either way: if those runs produced
   verdicts that were discarded, the retained population is not the
   reviewed population.
6. **Prospective gold accrual.** A fixed small fraction of clearances and
   refusals routed to the Principal for blinded adjudication (the reviewer
   identity withheld), and randomized routing among admitted reviewers on
   comparable cases, both counted at the incident level (one artifact
   family, one ruling), so that a criterion set can grow without a
   retrospective ledger pass.
7. **For striatum's decision, not CAPLAB's: escalation-on-dissent for the
   overclaim class.** A second admitted reviewer on artifacts that carry
   receipts or verification claims, since the one defect class that
   recurs in the adjudicated record is a claim the artifact does not earn
   (receipts asserting executions that never ran; "proves" guards that grep
   comments; documented behaviour the code returns before reaching). A
   lane-design option, not an instrument.

## What CAPLAB does meanwhile

Per-binding admission gate on request (`advisory/gate/review-gate-20260819.json`),
regression sentinel, report-only production canary from the ledger as it
stands. No ranking.
