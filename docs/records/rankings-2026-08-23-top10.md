# Fleet capability rankings — top 10 reviewers and builders (2026-08-23)

Derived from the CAPLAB raw-data snapshot of 2026-08-23 (`advisory/claims.jsonl`,
`build.packet_delivery/1` harvest, adjudication ledger through the Principal's
rulings of this date). Rankings are evidence-ordered, not preference-ordered;
the standing column shows where each binding sits after `policy_version 35`.

**Comparability caveats.** Review numbers compare only within one instrument,
custody class, and case seed; each row cites its best large-n cohort.
Discrimination = catch − false-alarm rate. Build numbers are
production-harvested (tree-moved cascade rows excluded) and carry era
confounds. The delivery column measures mounting, not skill.

## Reviewers — `review.defect_discrimination/1`

| # | binding | disc | catch | FA | n (seed) | standing after v35 |
|---|---|---|---|---|---|---|
| 1 | agy-gemini-3-7-flash-high | **+0.68** (+0.73…+0.76 @0817; **+0.50 on the v2 clean contract — the only positive clean-contract number**) | 84% | 16% | 57 (20260819) | pool #1, `frontier` |
| 2 | codex-sol-high | +0.77 ⚠ v1-changeset rows; clean-contract twin: +0.30 | **96%** | 20% (clean contract: **60%**, adjudicated 6/10) | 57 (20260819) | pool #5, `strong` — best catch, miscast as a binding gate |
| 3 | claude-harm-fable-5-high | +0.66 | 76% | 9% | 54 (20260817) | not in pool — review delivery 9.1% @ n=1115 (mounting broken) |
| 4 | agy-gemini-3-7-flash-medium | +0.58–0.60 | 72% | 14% | 57×2 | pool #2 |
| 5 | cc-glm-5-3-max | +0.54 | 72% | 18% | 57 (20260819) | **pool #3 (promoted, v35)** — the independence slot behind the gemini pair |
| 6 | or-gemini-3-7-flash-high | +0.52 | 55% | 4% (silence-flagged — read `anchored` first) | 56 | withdrawn pending CAPLAB sweep (bare lane) |
| 7 | oc-glm-5-3 | +0.42 | 72% | 30% | 57 | mounting hold |
| 8 | agy-gemini-3-7-flash-low | +0.41 | 41% | 0% | 22 (dispatch instrument) | eligible, unranked for review |
| 9 | oc-deepseek-v4-flash | +0.38 | 67% | 29% | 57 | mounting hold |
| 10 | glm-5-3-max | +0.37 | 57% | 20% | 56 | disabled (bare lane) |

The Claude 5 and Opus 4.8 effort ladders cluster at +0.2–0.6 on the historical
dispatch instrument at n≤37 — too thin and not instrument-comparable to rank.
The notable row is #3: the third-best judge measured cannot serve because its
harness path delivers 9% of the time.

## Builders — `build.packet_delivery/1` (checks-pass, tuples with n≥15)

| # | binding | checks-pass | n | delivery | standing after v35 |
|---|---|---|---|---|---|
| 1 | agy-gemini-3-7-flash-high | **0.875** | **535** | 0.996 | build #3 (conserved for review) |
| 2 | claude-opus-5-high | 0.872 | 39 | 0.750 | build #2 |
| 3 | codex-sol-high | 0.820 | 172 | 0.974 | build #1 |
| 4 | claude-opus-5-medium | 0.796 | 113 | 0.647 | unlisted (rank fallback) |
| 5 | codex-sol-xhigh | 0.789 | 242 | 0.987 | unlisted (rank fallback) |
| 6 | agy-gemini-3-7-flash-medium | 0.785 | 195 | 0.994 | build #4 |
| 7 | codex-sol-max | 0.770 | 579 | 0.923 | disabled (effort cap) |
| 8 | claude-harm-opus-5-medium | 0.750 | 68 | 0.544 | build #6 |
| 9 | codex-sol-medium | 0.727 | 44 | 1.000 | unlisted (rank fallback) |
| 10 | codex-terra-medium | 0.688 | 16 | 0.333 | build #7 |

Anchor at the bottom: **claude-harm-sonnet-5-high, 0.335 over n=400** — the
worst large-n builder harvested, moved to the build tail in v35.

## The v35 changes these rankings carried

1. **Review:** `cc-glm-5-3-max` takes third preference — the slot that reviews
   gemini-built packets once independence excludes the google-gemini class.
   `codex-sol-high` drops to fifth: its headline +0.77 stands on
   v1-changeset-quarantined rows, and on the clean v2 change-set contract its
   false-alarm rate is 60% (adjudicated) — each false refusal burns a bounded
   revision attempt no accounting predicate refunds. `deepseek-v4-flash`
   dropped as inert.
2. **Build:** both `claude-harm-sonnet-5` tuples to the tail; eligibility
   untouched, first candidates unchanged on both passes.

Records: `striatum-next` commit `e93407f` (policy v35);
`docs/records/adjudication-dossiers-2026-08-23-sol-clean-controls.md`;
`docs/records/raw-data-2026-08-23.md`; `docs/leaderboard/index.html`.
