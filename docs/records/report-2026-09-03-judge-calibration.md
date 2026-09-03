# Judge calibration: three judges on 180 audited plan-defect pairs

- Date: 2026-09-03. Ranking memo layer 1, first half; authorized by the
  Principal ("2 and 3 are authorized").
- Run root: `advisory/pool-runs/plan-judge-calibration-20260903/`
  (`calls.jsonl` per ordered call, `resolved.jsonl` per pair and judge,
  `summary.json`). Rubric `plan-judge-v1`, environment `iso-v1`, pinned
  P2b oracle and registry v37 for control soundness.
- Jury: `agy-gemini-3-7-flash-high` (google-gemini), `cc-glm-5-3-max`
  (zhipu-glm), `claude-harm-opus-5-high` (anthropic-claude).
  `codex-sol-high` was in the smoke jury and answered `404 Not Found` from
  `chatgpt.com/backend-api/codex/responses` on every call, in and out of
  the sandbox, on a bare probe as well — the account or the service, not the
  instrument. Dropped for the run.

## Design

180 pairs: 20 per operator class, planner-balanced, drawn seeded from the
audited admissible mutants over sweep controls and recovered
production-accepted controls. Each pair to the first two eligible judges
(a judge never shares the planner's aliasing class; `local` has no model
family) in both orders; an order-dependent verdict is a tie. 714 calls,
one lane per judge, ~90 minutes.

## Results

| judge | pairs | usable | defect pairs | catch | 95% CI | prefers defect | ties | position flips | size pairs, prefers control |
|---|---|---|---|---|---|---|---|---|---|
| `agy-gemini-3-7-flash-high` | 181 | 157 | 122 | **0.984** | [0.94, 1.00] | 0 | 2 | 0/155 | 35/35 |
| `cc-glm-5-3-max` | 140 | 119 | 93 | 0.892 | [0.81, 0.94] | 3 | 7 | 3/115 | 26/26 |
| `claude-harm-opus-5-high` | 40 | 37 | 30 | 0.933 | [0.79, 0.98] | 0 | 2 | 1/36 | 7/7 |

Per class (control preferred / pairs):

| class | gemini-3.7-flash-high | glm-5-3-max | harm-opus-5-high |
|---|---|---|---|
| `circular_depends_on` | 15/15 | 11/11 | 4/4 |
| `dangling_dependency` | 19/19 | 15/15 | 4/4 |
| `dropped_deliverable` | 19/19 | 12/13 | 6/6 |
| `overclaimed_verification` | 18/18 | 13/14 | 4/4 |
| `purpose_scope_contradiction` | 18/18 | 14/14 | 3/3 |
| `write_scope_outside_tree` | 17/17 | 13/13 | 5/5 |
| `unresolvable_acceptance_check` | **14/16** | **5/13** (3 preferred the defect) | **2/4** |
| `atomicity_split` (mutant larger) | 19/19 | 15/15 | 3/3 |
| `merge_independent_packets` (mutant smaller) | 16/16 | 11/11 | 4/4 |

By population: Gemini 111/113 on sweep controls and 9/9 on
production-accepted; GLM 76/84 and 7/9; harm 28/30 on sweep (no
production pairs fell to it).

## Reading

**The judges see what the oracle cannot.** Six of the nine classes are
oracle-silent by construction. On five of them every judge is at or near
the ceiling. This is the capability the ranking needs.

**No judge scores packet count.** On the split probe the mutant is the
larger graph; on the merge probe the smaller. All three judges preferred
the control on every size pair, both directions, 68 of 68. The instrument's
central risk — that a judge inherits the validator's size artifact — has a
measured answer of no on this material.

**Position barely moves a verdict.** Flip rates 0%, 2.6%, 2.8% against the
literature's 10–15% for frontier judges on open-ended text. Structured
graphs are harder to be swayed on by order.

**One class is the instrument's defect.** `unresolvable_acceptance_check`
replaces a registered check-set id with a plausible unregistered one. The
planner prompt carries the index of resolvable sets; the judge prompt did
not. A judge that has not seen the registry can only guess whether
`withholding-guards-full-suite` exists, and GLM guessed against the
control three times. `plan-judge-v2` must carry the index. Until it does,
this class is excluded from judge reliability. Without it: Gemini 106/106,
GLM 78/80, harm 26/26 — control preferred over defect pairs of the
other six classes.

**The calibration was too easy to weight judges by.** Ceilings on seven
classes mean the three judges cannot be ordered by reliability from this
run; BT-σ weights would be flat. Subtler classes (a plausible but wrong
dependency direction; a scope that exists but is the wrong one) are owed
before judge weights are trusted. For a first ranking the jury is treated
as uniform, and the design says so.

## What did not run

- **Transport.** 21 pairs (84 calls) were refused because the judge prompt
  exceeded the 100 KB argv transport: the design context plus two graphs
  reaches 247 KB on the largest tasks. 36 of the 84 refused calls were
  production-accepted pairs, which are the larger graphs. The judge path
  needs the file-spill transport the review runner has, or the task draw
  must cap context size and say so. Until then the ranking under-samples
  large tasks.
- **Codex.** See above; 4 smoke calls, no verdicts.

## Findings for striatum

- The codex endpoint returned 404 all day on the striatum codex config
  dir. Any live codex lane is failing the same way.
- The `striatum-next` working tree carried 129 modified-modified and 23
  added-deleted entries at 15:xxZ from activity that is not CAPLAB's; the
  review-sweep tree guard stopped two sweeps on it. The guard did its job;
  the churn is upstream's to explain.
