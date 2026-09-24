# Striatum still does not emit what post-hoc review quality needs

- Date: 2026-09-23. Source: a full ledger export (`striatum -json ledger cat`,
  440,911 events through seq 440910, exit 0), scanned directly. The production
  review canary was also run on the same export. The question: is
  striatum-next emitting enough to establish review quality after the fact?
  Checked against the seven items of the
  [2026-09-07 request](request-2026-09-07-striatum-review-outcome-events.md),
  which was filed on 2026-09-14 as Cairn record `4c75c6e0`. "Since filing"
  means events written on or after 2026-09-14.

## Result: no. No requested item has shipped

| # | Requested | Ledger today |
|---|---|---|
| 1 | Re-ruling event for review verdicts | **Absent.** There is no new event type. There have been 0 acceptance rulings on a change-set, ever: 695 acceptance `gate_result`s fall on proposals, designs, plans and decision records only, 108 of them since filing. Nothing records a review verdict being overruled. |
| 2 | Rendered prompt retained on review runs | **Absent.** `manifest.prompt_asset_hashes` is empty on 27,951 of 27,951 runs opened, including all 1,449 since filing. |
| 3 | Budget field on review runs | **Absent.** The only bound on a run open is `deadline_class` (`batch`). |
| 4 | Review-to-outcome linkage | **Absent.** `application_record.licensed_by.gate_results` never includes a review-class gate (80 applications since filing, 0 linked to a review). `cancellation_record` does not name a review run. |
| 5 | Verdict-retention gap | **Worse.** Since filing, 331 of 627 review-pass runs closed `submitted_partial` (53%), against 23% before. The canary counts 2,897 of 6,574 anchored review runs with no retained verdict. |
| 6 | Prospective gold accrual (blinded Principal adjudication) | **Absent.** |
| 7 | Escalation-on-dissent (striatum's option) | Not observed as a lane behaviour. The Review Ledger schema carries `dissent` arrays (commit 6f93739). |

No striatum-next commit since 2026-09-07 references the request or any of its items.

## What can be computed post hoc today

Reviewer **behaviour**: clear and refuse counts, missing-body rates and
latency per backend (the canary tables). Examples: `codex-sol-max` refuses
177 of 243; `claude-harm-fable-5-high` retains no verdict on 1,023 of 1,120.

Reviewer **quality** cannot be computed. No event says a verdict was right or
wrong. Outcomes cannot be joined to the review that cleared them, and the prompt
a reviewer saw is not retained. `claude-opus-5-5-high` and the GPT-6 tuples have no
production review runs in this snapshot.

## Consequence

The production canary cannot become a quality instrument until items 1 and 4
exist at minimum. Until then, the only review-quality evidence in hand is
off-ledger: the 2026-09-23 Artificial Analysis Acceptance_Criteria_Review
replication, where all four tested tuples tied.
