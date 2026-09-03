---
design_id: planner-evaluation-v1
artifact_type: design
status: proposed
decision_owner: repository-owner
author: CAPLAB execution delegate (Claude), 2026-09-03
supersedes: none
relates_to:
  - docs/product/capability-cards/planning-constructs-v1.md
  - docs/records/research-2026-09-02-planning-ranking-instrument.md
  - docs/records/report-2026-08-27-planning-p2b.md
  - docs/records/report-2026-09-02-planning-additions.md
  - docs/records/report-2026-09-02-plan-operators.md
  - docs/records/report-2026-09-03-judge-calibration.md
---

# Planner evaluation: a design for an instrument that ranks

This document is a **recommendation**. It proposes how CAPLAB should
measure the planning capability of a binding so that the measurements
order bindings, and it states why the author believes the order would be
meaningful. It selects nothing and authorizes nothing. The constructs it
names become constructs only when the Principal specifies them on a
capability card. Assertion types follow
`docs/domain/ubiquitous-language.md` and are labelled where they matter.

## 1. Summary

The planning board of 2026-08-27 measured eight bindings on
`planning.finishability/1` and could not rank them. The reason is
structural, not accidental: the construct is a boolean validator, and in the
design-only environment one check carries all the failures, so the rate
falls with decomposition and 93 of 93 small graphs pass. A validator is a
gate. Gates do not rank.

The proposed instrument has three layers, each with its own label class,
and a ranking comes only from the middle one:

| layer | construct (proposed) | what it measures | label class | output |
|---|---|---|---|---|
| L0 | `planning.finishability/1`, `tree-mounted` | can the binding emit a legal, resolvable, tree-consistent work graph | mechanical | admissibility and yield |
| **L1** | `planning.pairwise_preference/1` | which of two admissible graphs for the same task better delivers the design, verifiably | independent-family judgment, calibrated | **Bradley-Terry order with intervals** |
| L2 | `planning.execution_yield/1` | do the packets build and pass their own declared checks under one fixed executor | mechanical, downstream | validity check on L1 |

The ranking claim is L1's. L0 says which graphs may enter it. L2 and a
production correlate say whether L1's order predicts anything mechanical.
If L2 disagrees with L1, L1 is revised, not promoted.

Why this should rank (§6): pairwise judgment recovers order where absolute
scores saturate; the judges are calibrated on this instrument before their
verdicts are read, and the calibration completed today puts the best judge
at 98.4% catch of injected planning defects, zero preference for the defect,
zero position flips, and no preference for packet count; independence by
family removes self-preference; both orders remove position; and the
anchor layer is a pre-registered falsification test rather than a claim of
validity by construction.

## 2. Context

### 2.1 What is being measured

[Observation] Striatum's `implementation-planning` pass turns an accepted
design (L2 artifact) into a prose implementation plan (L3); `packetization`
lowers the plan to a work graph (L4) deterministically and gates it on
`work-graph-legality`. The card's Arm 1 corpus asks a binding for the
composite — design to work graph in one step — under the `plan-v2`
contract, because the work graph is the shape a mechanical oracle can
score. No production lane performs the composite, so there is no per-task
production reference for it.

### 2.2 What the board showed

[Observation] Eight bindings, 24 tasks each, seed 20260827, `iso-v1`,
design-only, pinned instrument (oracle rebuilt at striatum-next `06cd940`,
registry v37): finishability 1.00 (`codex-terra-max`) down to 0.71
(`claude-opus-5-high`). Yield 192/192. Every failing check but three is
`scope_overlap`; the three are `non_topological_index` from one binding.

[Inference] The rate is close to an inverted proxy for decomposition. Every
graph with five packets or fewer passed (93/93). The two top bindings have
the smallest graphs. This is not a capability ordering, and the record of
2026-08-27 and the Principal's reading of 2026-09-02 agree on that.

### 2.3 What already exists to build on

- The eight planners' 192 stored graphs and the 24 tasks' design contexts
  (CAS-retained; `task_context` renders them byte-identically to what the
  planners read).
- 137 production work graphs recovered from the graph store, 67 of them
  accepted heads, 59 sound under the pinned oracle — the card's "real
  accepted plans".
- Nine plan-defect operators with mechanical checkers, audited on 272 sound
  controls across three populations: 2,056 admissible mutants, zero
  operator-induced oracle trips.
- A pairwise judge module (rubric `plan-judge-v1`, adapters, independence
  rule, both-orders resolution) and a completed calibration of three
  judges (§6.2).
- The review instrument's precedent: matched-pair defect injection has
  separated bindings on catch and false alarm with p<0.001 on this fleet,
  and the pattern is reused here for judge calibration.

## 3. What "a meaningful ranking" must mean

A ranking is meaningful for placement when it has all of the following.
Each is a property the design must supply and a test the design must pass.

1. **Construct validity.** The order reflects planning quality as striatum
   needs it — packets a builder can execute and verify, covering what the
   design promised — and not a nuisance variable such as packet count,
   prose length, or output format.
2. **Discriminating power.** Adjacent bindings separate by more than their
   intervals at the sample size the budget allows, at least at the ends of
   the order.
3. **Reliability.** The order repeats under a fresh task draw, a second
   judge family, and the reverse presentation order, within stated bounds.
4. **Independence.** No binding is judged by its own family, and no judge's
   verdicts are read before the judge's reliability is measured on this
   instrument.
5. **Predictive validity.** The order predicts a downstream, mechanical
   outcome — packets that build and pass their checks — on at least a
   subset, and does not contradict the production record where one exists.
6. **Bounded scope.** The claim names the environment, contract, corpus,
   rubric version, jury and instrument pin, and is a capability profile for
   one construct, not a global model ranking (ubiquitous language:
   *capability profile*, *projection*).

`planning.finishability/1` fails (1), (2) and (5) by construction. Any
replacement is judged against this list, including the one proposed here.

## 4. Design

### 4.1 Corpus and task identity

[Decision recorded 2026-08-27, carried] The corpus is the
`implementation-planning` harvest: 348 tasks over 112 step passes, drawn
seeded and pass-disjoint, balanced produce/revise, design-only inputs
retained in the CAS. The environment is `iso-v1` bubblewrap. Task identity
is claim identity; a task's design context is the same bytes for every
planner and every judge.

Proposed change: raise the draw from 24 to **48 tasks** for the first
ranking run (274 tasks fit the budget), for the power reasons in §6.4.

### 4.2 Layer 0 — the gate

`planning.finishability/1` in the **`tree-mounted`** environment: the base
tree is materialized in the case workspace, so the oracle scores
write-scope reality and atomicity (the two Arm 1 checks that never ran),
and the planner can name file-grain scopes, which lifts the
directory-collision confound the P2b record identified.

Output per binding: **yield** — the share of tasks on which the binding
produced a graph that parses, indexes, resolves, and is tree-consistent.
Inadmissible graphs do not enter L1; the yield is reported beside the L1
strength so a binding cannot improve its rank by failing to answer. No
ordering is derived from L0.

Instrument pin: oracle binary hash and registry version on every row (the
2026-09-02 drift flipped 19 of 148 stored verdicts; the pin is not
optional).

### 4.3 Layer 1 — the ranking

**Unit.** One task, one ordered pair of admissible graphs from two
different planners, one judge. The judge reads the task's design and
context, then graphs A and B, and answers `{"preferred": "A"|"B"|"tie",
"confidence", "reasons"}` under the versioned rubric.

**Schedule.** Round-robin over planners per task: with *k* planners,
k(k−1)/2 pairs per task. Each pair is presented in both orders, to two
judges from families independent of both planners, chosen in jury order.
Assignment of A/B is random per presentation, not fixed per planner.

**Blinding.** Graphs are shown under neutral labels with no planner
identity. Planner-identifying content inside a graph (a model naming
itself in a purpose string) is a known leak; the pre-registration includes
a scan for family names in graph text, and any graph that names a model
family is excluded and the exclusion counted.

**Resolution.** Per (task, pair, judge): the two orderings resolve to
`first`, `second`, or `tie`; a verdict that changes with presentation
order is a tie, never a preference. Per (task, pair): two judges' resolved
verdicts pool as two observations, weighted by judge reliability (§6.2)
under a judge-aware Bradley-Terry fit (BT-σ) or, if the jury is uniform in
reliability, as plain observations.

**Fit and report.** Bradley-Terry strengths per planner with bootstrap
intervals over **tasks** (the unit of independence is the task; the
comparisons within a task share a design). Reported beside the strengths,
always: the k×k win matrix, the tie rate, the position-flip rate per judge,
the count of transitivity violations in the majority graph, per-judge
agreement (Cohen's κ between the two judges on shared pairs), and the L0
yield. A strength is never shown without its interval and its yield.

**Rubric.** `plan-judge-v1` names coverage, verifiability, dependency
honesty, scope discipline, and granularity, and states in words that packet
count is evidence of neither quality nor defect. Two revisions are already
owed from the calibration (§6.2): the registry index of resolvable check
sets must be in the judge prompt exactly as it was in the planner's, and
the transport must carry prompts above 100 KB. Any rubric change is a new
profile (`plan-judge-v2`) and a new cohort.

**Label class.** Acceptance by independent-family judgment, model-relative,
never gold — the Tier B framing, stated on every claim. It is never summed
with L0 or L2.

### 4.4 Layer 2 — the anchor

`planning.execution_yield/1`: one fixed executor builds a planner's graph
packet by packet in the `tree-mounted` workspace; after each packet its
declared `acceptance_checks` run through the checks registry. Metrics per
graph: first-pass packet check rate, closure without replan, rework ratio.
The executor tuple is claim identity and is held constant across planners.

Scale: 4–6 tasks × all planners on the first run (150–300 packet builds).
Its purpose is one pre-registered number: Spearman ρ between L1 strength
and L2 first-pass rate across planners, with its interval.

### 4.5 The production correlate

Zero-spend validity evidence: the ledger holds `gate_result`,
`head_movement`, `packet_quarantine`, and `escalation` records for the
packets of production plans authored by seven bindings. `harvest_gate` over
`build` and `verification` gates gives each producer a first-pass packet
rate and revision count on its own plans. Scheduler-routed and
task-mix-confounded, but it exists. L1 run over the 59 sound production
graphs (all but three from `local`) is not informative about model
planners; the correlate is instead read against the Tier B
`planning.independent_acceptance/1` producer rates for the same bindings,
and against L2. Direction agreement is the test; magnitude is not claimed.

### 4.6 Arm 2 — plan-review discrimination

Unchanged from the card. The same operators and audited controls score
plan **reviewers** (who holds the `implementation-plan-review` gate) on
catch and false alarm. Not part of the planner ranking; named here because
building the operators once served both, and because the reviewer that
holds the gate should be at least as good a judge as the L1 jury.

### 4.7 Claim shape and identity

Every L1 claim names: construct and rubric version; corpus draw (seed,
n tasks, pass-disjointness); environment; L0 instrument pin; jury (judge
ids, aliasing classes, command hashes, calibration run and reliability);
schedule (round-robin, both orders, two judges); fit (BT variant,
bootstrap n); and the exclusions with counts (transport, leaks,
inadmissible). A consumer can reproduce the ranking from the stored calls
without any model in the loop.

## 5. Why not the alternatives

[Recommendation, alternatives named]

- **Keep finishability/1 and add size normalization only.** A
  size-normalized legality rate (scope disjointness, identical-scope
  duplicates) is honest and cheap, and the P2b record proposed it. It still
  measures legality, and 100% of graphs at ≤5 packets are legal. It is the
  right L0 refinement and the wrong ranking.
- **Rank on Tier B `planning.independent_acceptance/1`.** Production
  plan-review pass rates exist for seven producers. They are
  scheduler-routed (different tasks per producer), judged by whichever
  family placement chose, and era-mixed. They are a correlate, not an
  instrument.
- **Execution outcome as the primary ranking (L2 alone).** The most valid
  label and the most expensive by two orders of magnitude; and the
  literature's 32.8% executor-side failure share means it ranks the
  planner×executor pair. It is the anchor, not the instrument.
- **Absolute rubric scores (1–5) instead of pairwise.** Absolute LLM scores
  compress toward the top and drift across judges and days; pairwise
  verdicts agree with human preference more reliably on the same material
  (MT-Bench, Chatbot Arena). Pairwise also gives the calibration a
  ground-truth form (control vs mutant) that absolute scoring lacks.
- **No change.** Leaves striatum's implementation-planning preference list
  ordered on priors, with a measured 0.207 finishability holder at the top
  and its best alternative disabled. The pressure is demonstrated.

## 6. Justification: why this should yield a meaningful ranking

### 6.1 The mechanism

Absolute validators saturate because most graphs clear every constraint the
validator can express; the residual variation is dominated by one
environment-induced failure. Pairwise judgment does not ask whether a graph
is legal. It asks which of two legal graphs better delivers the design,
which is a graded question with room above the bar. Bradley-Terry turns
many such comparisons into latent strengths whose precision grows with the
number of opponents each planner meets, not only with the number of tasks.
Arena-Lite (EMNLP 2025) and the round-robin BT results (Spearman 0.96
against the human-vote arena) show the recovery works on model outputs
where absolute scores did not separate.

### 6.2 The judges can see the differences that matter — measured today

[Observation] Calibration run `plan-judge-calibration-20260903`: 180
control/mutant pairs (20 per operator class, planner-balanced, drawn from
sweep and production-accepted controls), each to two independent judges in
both orders, 714 calls. Rubric `plan-judge-v1`, environment `iso-v1`.

| judge | defect pairs | catch | prefers defect | ties | position flips | size pairs | prefers control on size pairs |
|---|---|---|---|---|---|---|---|
| `agy-gemini-3-7-flash-high` | 122 | **0.984** [0.94, 1.00] | 0.000 | 2 | 0 / 155 | 35 | 35 / 35 |
| `cc-glm-5-3-max` | 93 | 0.892 [0.81, 0.94] | 0.032 | 7 | 3 / 115 | 26 | 26 / 26 |
| `claude-harm-opus-5-high` | 30 | 0.933 [0.79, 0.98] | 0.000 | 2 | 1 / 36 | 7 | 7 / 7 |

Per class, every judge caught 100% of `circular_depends_on`,
`dangling_dependency`, `write_scope_outside_tree` and
`purpose_scope_contradiction`, and 92–100% of `dropped_deliverable` and
`overclaimed_verification`. The one weak class is
`unresolvable_acceptance_check`: Gemini 14/16, GLM 5/13 (3 preferred the
defect), harm 2/4.

[Inference] Three things follow.

- The oracle-silent classes — dropped deliverable, swapped purpose,
  overclaimed verification, the atomicity split — are exactly the defects
  the mechanical gate cannot see, and the judges see them at or near the
  ceiling. That is the capability the ranking needs and the validator
  lacked.
- **The size probes came back clean.** On `atomicity_split` the mutant is
  the larger graph; on `merge_independent_packets` the smaller. Every
  judge preferred the control on every size pair, in both directions
  (Gemini 19/19 and 16/16). A judge scoring packet count would have split.
  The instrument's central risk — that L1 inherits L0's size artifact
  through the judge — has a measured answer of no, on 68 pairs.
- The weak class is the instrument's fault, not the judges'. A judge cannot
  know that `withholding-guards-full-suite` is unregistered unless it sees
  the registry index the planner saw; the planner prompt carries that index
  and the judge prompt did not. `plan-judge-v2` carries it. Until then the
  class is excluded from judge reliability or scored as oracle-only.

Position flips were 0/155, 3/115 and 1/36 against the literature's 10–15%
for frontier judges on open-ended material; graphs are structured enough
that order barely moves the verdict.

### 6.3 Independence and blinding remove the two self-preference paths

A judge never shares the planner's aliasing class (`google-gemini`,
`openai-gpt`, `anthropic-claude`, `zhipu-glm`), so no binding is ranked by
its own family. Graphs are blinded and orders randomized. The remaining
path — a family's stylistic preference for another family's output — is
measurable: two judge families see every pair, and their agreement (κ) and
any systematic split by planner family are reported. If the two judges
disagree systematically on one planner, that planner's strength carries a
flag, not a number.

### 6.4 Power: what separates at what n

[Inference, arithmetic] For one planner pair on t tasks with a true win
probability p, the Wilson interval at t=24 and p=0.65 is [0.45, 0.81] —
one pair alone does not separate at 24 tasks unless p ≥ 0.75. Bradley-Terry
pools: each planner meets 7 opponents on every task, so its strength rests
on 7t comparisons (168 at t=24, 336 at t=48). Under a uniform-strength null
the standard error of a BT log-strength falls roughly as 1/√(7t); at t=48
two planners whose true head-to-head rate is 0.62 separate at the 95%
level, at t=24 they need about 0.67. The eight planners on the board show
head-to-head structure well above that on the mechanical proxy alone
(fable 5.1 collided once in 24 tasks where opus-5 collided 25 times), so
the design expects the ends of the order to separate at t=48 and the middle
to overlap — which is the honest shape of a ranking with intervals. The
first run is therefore proposed at 48 tasks, and separation of adjacent
middle bindings is not promised.

### 6.5 The validity test is pre-registered and can fail

L1 will be believed only if:

- **H1 (anchor).** Spearman ρ(L1 strength, L2 first-pass packet rate) ≥ 0.6
  across ≥ 6 planners on ≥ 4 shared tasks, interval excluding 0.
- **H2 (production correlate).** L1 order agrees in direction with the Tier B
  producer rates for the bindings present in both (no reversal between a
  top-third and a bottom-third binding).
- **H3 (reliability).** Kendall τ ≥ 0.7 between L1 orders from two disjoint
  task draws of 24, and between the two judge families' orders.
- **H4 (nuisance).** No planner's strength moves by more than one interval
  width when graphs are re-judged with packet count masked (a variant that
  shows purposes and dependencies only) — a robustness check on 8 tasks.

If H1 or H3 fails, the record says the rubric measures judge taste on this
corpus and the ranking is not promoted; the operators and calibration
remain valid for Arm 2. If H4 fails, the size probes were too easy and
harder size mutations are added before any re-run.

### 6.6 Doctrine check

Doctrine retrieval (Pincite packet `pkt-8f1f42f4f904f7bb`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
release `d3e0c0d`; role `architecture-agent`, task
`architecture-assessment`; authority ceiling *recommend*) activated
concepts this design is checked against:

- `universal-evidence-before-intervention` — the intervention is earned by
  the P2b observation (validator saturation, 93/93) and today's calibration,
  and the no-change option is named in §5.
- `universal-measure-claimed-improvement` — the claimed improvement
  ("ranks") has a preserved baseline (the board) and is tested on the same
  dimension (H1–H4), not asserted.
- `universal-minimize-simultaneous-uncertainty` — one layer changes at a
  time: the gate is unchanged in semantics, the ranking is a separate
  construct, the anchor is a separate construct; rubric changes open new
  cohorts.
- `architecture-metrics-as-signals` (demoted stub, applied by analogy) — a
  narrow proxy identifies a question and cannot decide placement; the
  design forbids a quartermaster objective over L0 and gates one over L1
  on H1–H3.
- `data-system-of-record-derived-state` — the ranking is derived state:
  regenerable from stored calls, never a system of record; consumers
  project it (ubiquitous language: *projection*).
- `agent-conduct-authority-bounded-action` — this document recommends; the
  Principal decides; execution of any run is a separate authorization.

Unmet material obligation from the packet: `evidence-runtime-observation`
for L2 (no execution-yield run exists yet). That is why L2 is proposed as a
pilot and H1 is a test rather than a result.

## 7. Threats to validity and their treatment

| threat | how it would bias the order | treatment | status |
|---|---|---|---|
| Judge scores packet count | larger or smaller graphs win regardless of quality | size probes in calibration; rubric clause; H4 masked re-judge | probes clean (68/68) |
| Judge favours its own family | self-preference | aliasing-class exclusion; two families per pair; κ reported | enforced in code |
| Position bias | first-shown wins | both orders; order-dependent = tie; flip rate reported | 0–3% measured |
| Verbosity / prose style | wordier purposes win | rubric clause; H4 masks prose; per-family κ | untested; H4 |
| Judge saturation on calibration | calibration too easy to discriminate judges | ceiling on 7 classes is expected for structural defects; add subtle classes (wrong-order dependency, plausible-but-wrong scope) before BT-σ weights are trusted | open |
| Transport cap drops large tasks | order biased toward tasks with small designs | 21 of 180 calibration pairs dropped at >100 KB; add file-spill transport for judges or cap task size in the draw and say so | open, fix owed |
| Synthetic composite construct | measures a task no lane performs | stated on every claim; L2 and the correlate test transfer | inherent |
| Corpus is one repository | order specific to striatum-next planning | stated; a second corpus is future work | inherent |
| Non-transitivity | BT total order over cyclic preferences | violation count reported; BT fit diagnostics | reported |
| Rubric drift | orders across dates not comparable | rubric version is claim identity; new version, new cohort | enforced |
| Leakage of planner identity in graph text | judge infers the family | pre-run scan; exclusion counted | planned |
| Instrument drift (oracle, registry) | L0 admissibility shifts between runs | pin on every row; PROVENANCE.md | enforced |
| Judge account contention | slow judge stalls the run, or a window trips mid-run | one executor per judge; resumable on (pair, judge, order); probe-gated | built |

## 8. Cost

First L1 run, 8 planners, 48 tasks: 28 pairs × 48 × 2 orders × 2 judges =
5,376 calls; at the calibration's medians (Gemini 12 s, GLM 31 s, harm 8 s)
and one lane per judge, roughly 18 lane-hours spread across three
accounts; ~45 KB per prompt → ~60M input tokens, mostly the design context,
which prompt caching on agy and claude-code amortizes per task. No planner
spend: the 24-task graphs exist, and the second 24 tasks cost 8 × 24
planner calls (~9 minutes for fable, ~45 for GLM-flash).

L2 pilot: 4 tasks × 8 planners × ~5 packets = ~160 packet builds on one
cheap builder, 15–50 lane-hours.

Calibration to date: 714 judge calls, ~90 minutes wall clock.

## 9. Sequence

1. `plan-judge-v2`: registry index in the judge prompt; file-spill
   transport for prompts over 100 KB; leakage scan. Re-run calibration on
   the two affected classes only.
2. Second 24-task planner draw (seed 20260903) on the eight board bindings,
   pinned instrument, `design-only` — so L1 has 48 shared tasks.
3. L1 run. Report strengths, intervals, win matrix, tie/flip/violation
   rates, κ, yields. No quartermaster objective yet.
4. L2 pilot on 4 tasks; production correlate from `harvest_gate`. Test
   H1–H3.
5. Principal decision on promotion, card v2, and whether a quartermaster
   objective over L1 is installed.
6. `tree-mounted` L0 as the admissibility gate for all later runs; H4
   masked re-judge.

## 10. Decisions requested

1. Specify `planning.pairwise_preference/1` and `planning.execution_yield/1`
   on the capability card (or decline).
2. Authorize step 1 (rubric v2 and re-calibration of two classes) and step 2
   (a 24-task planner draw on the eight bindings; the fable and GLM-flash
   spend is the same order as today's).
3. Authorize step 3 (the L1 run) on the budget in §8.
4. Decide whether `codex-sol-high` rejoins the jury when its endpoint
   returns (it answered 404 on every call today) — a third family widens
   independence for GLM-planner graphs.

## 11. Evidence to date

- Board: `docs/records/report-2026-08-27-planning-p2b.md`,
  `report-2026-09-02-planning-additions.md`.
- Operators and audit: `report-2026-09-02-plan-operators.md`;
  `advisory/pool-runs/plan-operators-audit-20260902/`.
- Recovery: `advisory/pool-runs/production-work-graphs-20260903/`.
- Calibration: `report-2026-09-03-judge-calibration.md`;
  `advisory/pool-runs/plan-judge-calibration-20260903/`.
- Memo and literature: `research-2026-09-02-planning-ranking-instrument.md`
  (Arena-Lite; round-robin BT; BT-σ; non-transitivity; position and
  verbosity bias; PlanBench/VAL; execution-grounded evaluation; the
  717-task plan-quality-vs-execution study).
