# How to build a planning instrument that ranks

- Date: 2026-09-02. Research memo, Principal-directed: "do some research
  and figure out how to build an instrument that does actually yield a
  ranking on planning."
- Inputs: the P2b record and today's additions (eight subjects,
  `plan-*-20260827`), the capability card `planning-constructs-v1.md`, the
  Tier B harvest (`planning.independent_acceptance/1`), the review
  instrument that does rank (matched-pair defect injection), striatum's
  pass catalog and ledger record schemas, and the external literature cited
  at the end.
- This is a proposal. Nothing here is a construct until the Principal
  specifies it on the card.

## 1. Why the current instrument cannot rank, in one paragraph

`planning.finishability/1` scores a work graph by whether it clears a set of
boolean legality checks. In the design-only environment only one check ever
fails (`scope_overlap`), its odds rise with the number of packet pairs, and
93 of 93 graphs with five or fewer packets pass. A boolean validator over a
domain with one live constraint saturates: it is a gate, and a gate ranks
nothing above the bar. This is not a defect in the oracle. It is what
validators do — PlanBench, the formal-planning benchmark, uses the VAL plan
validator for exactly the same yes/no verdict, and its authors report the
same consequence: models cluster at the ceiling or the floor, and the
benchmark separates them only by widening the domain, never by reading the
validator's bit as a score.

Two properties a ranking instrument for planning must have follow from
this:

1. **A graded criterion that is invariant to decomposition size.** Any
   metric that a one-packet plan can max out, or that a twenty-packet plan
   can max out, is not measuring planning.
2. **Ground truth that lives downstream.** A plan is good if the packets it
   declares can be built and verified as declared. That is observable, and
   striatum records it (`gate_result` v2 pins `gate_id`, `outcome`,
   `request_ref`, and the producing run per packet gate; `build_corpus.
   harvest_gate` already joins those to producers).

## 2. What the literature offers

Four ideas transfer; one warning attaches to each.

**Execution-grounded evaluation.** The serious agent benchmarks of 2025–26
have converged on running the plan and scoring the outcome rather than
scoring the plan text (the agent-evaluation surveys, the Agent Planning
Benchmark's "intrinsic plus extrinsic" split, execution-based tool-use
evaluation). Warning: plan quality and execution success are only partly
coupled. One study found that of 717 tasks given a plan rated 5/5, 32.8%
still produced wrong results, almost all from executor-side parameter and
action errors. So execution outcome measures the *planner × executor*
pair; to attribute it to the planner, the executor must be fixed and named
in the claim, exactly as the harness is today.

**Pairwise comparison with a Bradley-Terry fit.** Where absolute scores
saturate, pairwise verdicts still order: Arena-Lite (EMNLP 2025) runs
per-prompt tournaments and fits Bradley-Terry ratings; round-robin BT
raises correlation with the human-vote arena to 0.96 Spearman. Pairwise
verdicts agree with human preference more reliably than absolute scores on
MT-Bench. Warning: judges are non-transitive at measurable rates, and BT
assumes a total order; the fit must report its inconsistency, and the
judge-aware BT-σ extension (a per-judge discriminator parameter estimated
jointly with item strengths) is the right model when judges of unequal
reliability are pooled.

**Judge bias is measurable and partly fixable.** Verbosity bias is 15–30
points of inflated preference for the longer answer on some judges, and it
is model-specific — Gemini-family and Llama judges prefer longer, Claude
judges prefer shorter, GPT-4o is near neutral. Position bias flips 10–15% of
frontier-judge verdicts on order alone. The standard mitigations are to run
each pair in both orders and score an order-dependent verdict as a tie, to
randomize position, and to state in the rubric how length is to be treated.
Warning from the same literature: position-swap helps on natural pairs and
*hurts* on adversarial ones, so the mitigation has to be validated on this
corpus, not assumed.

**Validators as gates, not scores.** PlanBench's lesson, stated above.

## 3. The design: three layers, one of which ranks

The instrument is a stack. Each layer has a different label class, and the
claims say which.

### Layer 0 — eligibility gate (mechanical; exists)

`planning.finishability/1`, moved to the `tree-mounted` environment the P2b
record already calls for. With the base materialized, the oracle scores
write-scope reality and atomicity (the two checks that never ran), and the
planner can name file-grain scopes, which lifts the directory-collision
confound. **This layer does not rank.** It decides which graphs are
admissible to the layers above, and its output on a claim is a yield: how
often the tuple produces an admissible graph. That is the honest use of a
validator.

### Layer 1 — the ranking: `planning.pairwise_preference/1`

Round-robin pairwise judgment over the work graphs already produced.

- **Material.** The 192 stored graphs from `plan-*-20260827` are the first
  corpus: eight planners, 24 shared tasks, same contract, same seed. No new
  planner spend is needed to compute a first ranking; the graphs are on
  disk with the design they answer.
- **Unit.** For one task, one pair of planners, one judge: both graphs
  shown blinded under neutral labels, the accepted design and the packet
  context beside them, in a random order; the same pair run again in the
  other order; an order-dependent verdict scores as a tie.
- **Rubric.** Stated in the prompt, versioned, and pinned on every claim
  (scar tissue 2). The judge is asked which graph, if built packet by
  packet as written, is more likely to deliver the design's stated
  deliverables with each packet independently verifiable. The rubric names
  the two failure directions explicitly — a graph that hands the step back
  whole is not a plan, and a graph that splits one check unit across
  dependent packets makes its intermediates unverifiable — and says that
  packet count is evidence of neither.
- **Jury.** At least two judges from families independent of both planners
  in the pair, by aliasing class, on the striatum rule that a Gemini-built
  artifact is never judged by Gemini. With four families on the fleet
  (anthropic, openai, google, zhipu) every pair has at least two eligible
  judge families.
- **Fit.** Bradley-Terry over the win/loss/tie matrix, per task then
  pooled; strengths reported with bootstrap intervals over tasks (the unit
  of independence is the task, not the comparison). Report the pairwise
  win matrix beside the fitted order, the tie rate, the position-flip rate
  per judge, and the transitivity violation count. If BT-σ is used, report
  each judge's fitted discriminator; a judge near zero is a coin and its
  verdicts are down-weighted by the model rather than by hand.
- **Judge calibration, built in.** This is where Arm 2 of the card earns
  its place inside Arm 1. Each judge is also shown control/mutant pairs
  — an accepted production plan against the same plan with one of the
  card's eight defect classes injected (dangling dependency, circular
  `depends_on`, unresolvable check, scope outside tree, atomicity split,
  dropped deliverable, purpose/scope contradiction, overclaimed level).
  The judge must prefer the control. Its catch rate and false-alarm rate
  on those pairs are its reliability, measured on the same instrument and
  the same day; a judge below a floor is excluded before its verdicts on
  the real pairs are read. Controls are audited by the oracle first (scar
  tissue 1). Two operators deserve adding for planning specifically:
  *merge two independent packets* and *split one packet across a check
  unit* — size-changing mutations that let the sweep measure whether a
  judge is rewarding decomposition size rather than plan quality.
- **Label class.** Acceptance by independent-family judgment, model-
  relative, never gold — the Tier B framing, stated on every claim. It is
  the same class as `planning.independent_acceptance/1`, so a consumer
  already knows how to weight it, and it must never be summed with the
  mechanical layer (the category error the P2b record names).

### Layer 2 — the anchor: `planning.execution_yield/1`

The check on Layer 1's validity, and the only layer whose label is not
model-relative.

- **Unit.** One planner's graph for one task, built packet by packet by a
  **fixed executor** in the `tree-mounted` environment, each packet's
  declared `acceptance_checks` run by the checks registry after its build.
- **Metrics.** Share of packets whose declared checks pass on first build;
  share of graphs that close without a replan; rework (revised packets ÷
  packets). The executor tuple is claim identity and is held constant
  across planners — the literature's 32.8% executor-side failure share is
  the reason.
- **Scale.** Expensive: a matched subset of four to six tasks across the
  eight planners is 150–300 packet builds. Its job is not to rank on its
  own but to answer one question with a number: does Layer 1's order
  predict Layer 2's yield (Spearman over planners, with its interval)? If
  it does not, Layer 1 is measuring judge taste and the record says so.
- **Production correlate, free.** The 348-task corpus carries seven
  production planners with downstream packet gates in the ledger.
  `harvest_gate` over `packetization` → `build` → `verification` gives, per
  planner, packet first-pass rate and revision count on plans it actually
  authored. Scheduler-routed and confounded by task mix, but it exists
  today at zero spend, and Layer 1 run over the production graphs should
  agree with it in direction before anyone believes Layer 1 on synthetic
  ones.

### Arm 2 proper — `planning.defect_discrimination/1`

Unchanged from the card: matched-pair defect injection scores plan
*reviewers* (who holds the plan-review gate), not planners. The same
operators and audited controls serve both; building them once is the
enabling work for Layer 1's calibration and for Arm 2.

## 4. Cost, honestly

Layer 1 on the existing material: 28 planner pairs × 24 tasks = 672
comparisons, × 2 orders × 2 judges = 2,688 judge calls, each carrying the
design (median 33 KB) and two graphs (5–15 KB) — roughly 30M input tokens
on flash-class judges. Prompt caching on the per-task design context cuts
most of it. A Swiss or single-elimination schedule (Arena-Lite) reduces the
pair count to O(n log n) at some loss of matrix completeness. Judge
calibration adds 8 operators × ~20 controls × 2 orders × 2 judges ≈ 640
calls on short plan artifacts. Layer 2 at four tasks is 150–200 packet
builds at 5–20 minutes each: 15–60 lane-hours, on a cheap builder, so its
first run is a direction check, not a claim.

## 5. What this would and would not establish

It would give an ordering with intervals, computed from graphs produced
under one contract and one seed, judged by calibrated independent-family
juries whose reliability is on the record, and checked against a
mechanical downstream yield on a subset. Each layer's label class is
stated; none is summed with another.

It would not make the ordering gold. Layer 1 is what independent models
prefer, disciplined by defect-injection calibration — the vindication
method applies, as it does to Tier B. It would not measure the
implementation-planning pass as striatum runs it (the composite synthetic
contract remains). And it would not survive a rubric change: rubric version
is claim identity, and a `pairwise_preference/2` starts a new cohort.

## 6. Order of work

1. **Operators and audited controls** for plan artifacts (card P3, first
   half) — the enabling piece for everything else. Add the two
   size-changing operators.
2. **Judge calibration** on control/mutant pairs; fix the jury and the
   reliability floor on evidence.
3. **Layer 1 over the 192 stored graphs.** First ranking, no planner
   spend. Report the win matrix, tie rate, flip rate, transitivity
   violations, and BT strengths with task-bootstrap intervals.
4. **Production correlate:** Layer 1 over the production graphs against
   `harvest_gate` downstream rates for the same producers.
5. **Layer 2 on four tasks** with one fixed executor. Spearman against
   Layer 1. Then decide whether Layer 1 earns a quartermaster objective.
6. Only then `tree-mounted` re-runs of new planners: the gate at Layer 0,
   the ranking at Layer 1.

## Sources

Agent Planning Benchmark (intrinsic/extrinsic split):
https://arxiv.org/html/2606.04874v1 · Evaluation and Benchmarking of LLM
Agents: A Survey: https://arxiv.org/html/2507.21504v1 · A Survey on
Evaluation of LLM-based Agents: https://arxiv.org/html/2503.16416v2 ·
PlanBench and VAL: https://www.emergentmind.com/topics/planbench,
https://github.com/harshakokel/PlanBench · Plan quality vs execution
success (717-task study, 32.8%): reported via
https://arxiv.org/html/2606.04874v1 · Arena-Lite (tournaments + BT):
https://aclanthology.org/2025.emnlp-main.360.pdf · Ranking Unraveled
(round-robin BT, 0.96 Spearman): https://arxiv.org/pdf/2411.14483 ·
Non-transitivity in LLM-as-a-judge:
https://openreview.net/forum?id=clJIQ4TKR0 · BT-σ judge-aware Bradley-Terry
(argument quality): https://arxiv.org/pdf/2605.28313 · LLM-as-a-jury:
https://arxiv.org/html/2602.16610 · Judging the Judges (bias mitigation,
position swap results): https://arxiv.org/pdf/2604.23178 · Reliability
without Validity (judge agreement/consistency/bias):
https://arxiv.org/pdf/2606.19544 · A Survey on LLM-as-a-Judge:
https://arxiv.org/pdf/2411.15594 · Planning representations for web agents
(planner ablation): https://arxiv.org/pdf/2605.29927 · MCP-Bench
(execution-based tool-use evaluation): https://arxiv.org/pdf/2508.20453
