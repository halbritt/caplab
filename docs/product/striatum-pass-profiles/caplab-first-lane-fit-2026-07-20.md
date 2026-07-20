---
id: caplab-first-lane-fit-2026-07-20
artifact_type: striatum-lane-fit-report
title: First CAPLAB Striatum lane-fit report
status: insufficient-evidence
created: 2026-07-20
decision_record: adr-0046
placement_owner: striatum-policy-owner
---

# First CAPLAB Striatum lane-fit report

## Recommendation

**Insufficient evidence. Recommend no CAPLAB-driven placement change for any
observed subject tuple in either the authorized-build or independent
fresh-review context.** The qualifying set and Pareto set are empty.

This is a recommendation to preserve current Striatum policy, not an automatic
routing decision. CAPLAB does not mutate a lane, scheduler, gate, workflow,
backend declaration, or dispatch configuration.

## Frozen profile inputs

The accepted comparison contracts are:

| Context | Profile | File SHA-256 | Initial qualification floor |
|---|---|---|---|
| Authorized build | `striatum-build-v1` | `f4a835e667a55027cb782867d1fcc77fb0876ee4c2444295dae4846381de87c5` | Four valid jobs, at least two workflow shapes and two task families, required task types and accepting review, no disqualifier |
| Independent fresh review | `striatum-fresh-review-v1` | `ed0c2c8a4fe7cf6aa45d76dc84b778f1f990c1feac38cb41c78a50ec3814e92c` | Four valid fresh reviews across at least two workflow shapes and two artifact families, including clean/defect and repository/narrow access, no disqualifier |

ADR 0031 accepted both profiles from Striatum source commit
`87ed89099477da7ba39252fe77c541e90928a8ef`. Striatum retains placement and
policy authority.

## Evidence comparison

### `gpt-5.6-luna` at maximum effort through Codex CLI `0.144.1`

Study 001 is registered and independently verified. Its accepted mechanical
observation is narrow: for one checkout-retries task family, appending the
exact V treatment changed harmful shipment from 8/8 to 0/8 while clean controls
passed. The immutable capability-profile proposal is
`641965dc30fd0dbfca81d56bb05282b01e8e079285ab605c12672e92f3971ef0`
and remains `pending-human-inference`.

The repository owner explicitly refused the capability inference in ADR 0023,
file SHA-256
`5c072c4e003c0ceb5ed4ec17334cb2a6f91b16f97945225c1a1daec3c26c252a`.
The record supplies no four-job build campaign, second task family, second
workflow shape, required accepting-review set, or fresh-review campaign.
Therefore this tuple satisfies neither lane-fit floor.

Measured execution context is descriptive only. Across ten B and ten V trials,
median wall time was 157.356300 seconds for B and 193.689044 seconds for V.
B recorded 2,178,860 input and 72,774 output tokens; V recorded 2,154,622 input
and 88,899 output tokens. All 20 trial statuses were valid. No common paid-cost
basis is available, and these task-local measurements cannot substitute for
the four-job or four-review profile thresholds.

### `claude-fable-5-max` and `codex-terra-max`

CAPLAB-8 exercised both native systems on six synthetic complex-work tasks.
All 12 primary attempts completed. Fable was blindly preferred in five of six
pairs, but neither system had a strict mechanical advantage in any pair; the
preregistered explanation was disconfirmed. The result file SHA-256 is
`ae686af6b252cf55aef41b737231d78ea302d403d4d7bb12bc5c1e2f663c0d35`.

Those tasks are not qualifying Striatum build jobs, do not span the accepted
profile's workflow and task-family floor, and have no required accepting
review. Preference is not lane fitness. Median native trial time was 75.680047
seconds for Fable and 77.466355 seconds for GPT. Fable reported 36,909 output
tokens plus harness-specific cache accounting; GPT reported 1,329,314 input,
1,209,600 cached input, 37,624 output, and 22,948 reasoning-output tokens.
The token schemas are harness-specific and not directly comparable. Both used
unmetered subscription capacity, so paid cost is unknown on a common basis.

CAPLAB-13 then exercised the same native tuples across eight development
fresh-review cells per subject. All 16 reviews failed the frozen output schema,
so zero were score-eligible and model comparison was not estimable. The result
file SHA-256 is
`f3810f55f8b68c032f473e4433581a97451c8bbe2cb4eecd91ffa8bad64adb5e`.
This is instrument calibration failure, not fresh-review evidence. Median
trial time was 77.393671 seconds for Fable and 91.155804 seconds for GPT.
Again, token accounting is harness-specific and subscription cost is
not-metered. Neither tuple satisfies either lane-fit floor.

## Criteria matrix

| Profile criterion | Luna/Codex Study 001 | Fable native evidence | Terra native evidence |
|---|---|---|---|
| Accepted capability inference | Refused by owner | Unavailable | Unavailable |
| Four qualifying observations | No | No | No |
| Two workflow shapes | No | No | No |
| Two task or artifact families | No | No | No |
| Mandatory task constraints all pass | Not established for profile | CAPLAB-8 pairs were partial | CAPLAB-8 pairs were partial |
| Required accepting review | No qualifying set | No qualifying set | No qualifying set |
| Fresh independent review validity | Not studied | 0/8 schema-valid | 0/8 schema-valid |
| Disqualifying event absent | Not enough profile evidence to decide | Not enough profile evidence to decide | Not enough profile evidence to decide |
| Latency floor | Task-local values available; wrong population | Task-local values available; wrong population | Task-local values available; wrong population |
| Token and paid-cost comparability | Tokens available; cost basis unavailable | Harness-specific tokens; not-metered | Harness-specific tokens; not-metered |

## Uncertainty, failures, and human-only criteria

The evidence is strong for the recorded task-local observations and strong for
the conclusion that the accepted lane-fit thresholds are unmet. It is not
evidence that any tuple is incapable of either context. The dominant
uncertainties are task-family coverage, workflow diversity, accepting-review
lineage, native output-contract elicitation, cross-harness token accounting,
and subscription cost comparability.

CAPLAB-8 had one stopped r1 Codex authentication-containment attempt before a
clean r2 restart; it is preserved outside the r2 denominator. CAPLAB-13 had no
infrastructure failure but had 16 subject-invalid schema outcomes. Provider,
harness, capture, and task-image failures remain separate from subject
behavior throughout.

Human-only criteria do not become satisfied by this report. Study 001 has a
named owner refusal rather than a positive capability inference. CAPLAB-8 has
delegated blind preferences but no capability disposition. CAPLAB-13 has no
qualitative dispositions because no review crossed the mechanical schema gate.

## Fallback and reopening

Continue current Striatum placement and use an already authorized human or
existing lane path when these profiles require a fallback. No fallback output
becomes positive evidence for a candidate tuple.

Reopen this recommendation only after a content-addressed campaign satisfies
one accepted profile's exact observation count, diversity, validity,
accepting-review, latency, token, and cost requirements. A corrected CAPLAB-13
prompt alone is not enough; the fresh-review profile still requires two
workflow shapes and two artifact or change families. Reopening requires a new
CAPLAB decision and does not mutate this historical report.
