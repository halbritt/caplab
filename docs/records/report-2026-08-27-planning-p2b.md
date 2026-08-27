# Planning P2b: the qualification sweep, and the rate that rewards not planning

- Date: 2026-08-27. Phase P2b of `planning-constructs-v1.md`, Arm 1.
- Sweep seed `20260827`, contract `plan-v2`, environment `iso-v1` /
  `design-only`, oracle `striatum-plan-oracle 1`
  (`4ff9ed37c5113b203d57af69d0ae8e0a3cfef8b20d37de36d33d499abea053f2`),
  checks registry `repository.json` at `registry_version 37`.
- Run roots: `advisory/pool-runs/plan-<subject>-20260827/`, one row per task
  carrying the produced graph, the oracle verdict and the oracle hash.

## What the Principal decided before anything was spent

Four rulings, all recorded here because they are claim identity:

1. **Construct.** Keep the composite as a named synthetic contract; score
   the production work graphs as an oracle-**calibration** population, not
   as per-task controls.
2. **Registry.** Put a verified index of resolvable check-set ids in the
   prompt and keep resolvability in the metric.
3. **Base blob.** Design-only for this sweep.
4. **Terra.** Probe the two `disabled` tuples first; on finding them alive,
   include both.

## Three instrument defects, caught before spending

**The contract promised a registry it never supplied.** `plan-v1` required
every `acceptance_checks` entry to name "a check or set from the checks
registry provided in the context", and `render_task_prompt` concatenated
only the dispatch inputs. No registry ever reached a subject. Scored as
written, resolvability would have measured guessing. `plan-v2` carries the
index; the profile is bumped because the contract changed.

**Four of the registry's 46 sets do not resolve.** `cli-guards` is listed,
all five of its member checks are defined in the same file, and the oracle
rejects it — as it does `cap6-guards`, `srws-guards` and `wgi2-guards`.
Which ids are offered is therefore verified against the oracle at sweep
time rather than read off the registry. Offering a name that cannot resolve
scores the registry's drift as the planner's defect.

**The draw was not pass-disjoint.** `step_pass` treated only bare digits as
a step's attempt, but real tails carry a retry suffix (`2281-r4`), so three
tasks from one pass landed in a nominally disjoint 24-task draw. The corpus
spans 112 eligible passes and one pass carries 29 tasks; treating them as
independent inflates n.

## The calibration arm

The 121 production work-graph submissions deduplicate to **68 output
identities** — one identity alone carries 35 submissions. Against
`registry_version 37`:

| | n | share |
|---|---|---|
| parse | 67 / 68 | 0.985 |
| legality | 66 / 68 | 0.971 |
| resolvability | 48 / 68 | 0.706 |
| every mechanical check | 48 / 68 | 0.706 |

The oracle discriminates. But the gap is almost entirely resolvability,
and those failures are the **instrument's, not the planners'**: the checks those graphs name (`chk-build`, `chk-full-suite`,
`chk-cli-append`) do not exist in today's registry, because the graphs
predate it. This is scar tissue 1 doing its job — had the sweep scored
subjects without running this first, 20 registry-era artifacts would have
looked like a defect rate.

Two cautions on this population. It is 67/68 `local`, the deterministic
backend that owns packetization, so it is generated-artifact dominated. And
it cannot be a per-task control: the corpus is `implementation-planning`
(design → prose plan, D2) while the oracle mechanizes packetization's
`work-graph-legality` gate (plan → work graph, D1, documented in the pass
file as "no judgment; the judgment is at implementation-planning"). **No
production lane performed the design-to-work-graph composite `plan-v2`
asks for.**

## The draw

24 tasks, seeded `20260827`, **one task per step pass**, balanced 12
`produce` / 12 `revise`, drawn from the 274 tasks (over 112 passes) whose
design-only prompt fits the 180 KB budget. Selection never reads production
outcome. Median prompt 33 KB; roughly 276k input tokens per subject.

## Results

| subject | declared | n | finishability | 95% CI | median packets | ≤2-packet graphs | scope disjointness | identical-scope graphs |
|---|---|---|---|---|---|---|---|---|
| `codex-terra-max` | disabled | 24 | **1.00** | [0.86, 1.00] | 4.5 | 6/24 | 1.00 | 3/21 |
| `codex-harm-terra-max` | disabled | 24 | **0.96** | [0.80, 0.99] | 5 | 6/24 | 1.00 | 2/20 |
| `claude-harm-opus-5-high` | accepted | 24 | 0.88 | [0.69, 0.96] | 7 | 3/24 | 1.00 | 6/23 |
| `codex-sol-high` | accepted | 24 | 0.79 | [0.60, 0.91] | 4 | 7/23 | 1.00 | 4/18 |
| `cc-glm-5-3-max` | accepted | 24 | 0.75 | [0.55, 0.88] | 5 | 2/23 | 0.90 | 9/22 |
| `claude-opus-5-high` | accepted | 24 | 0.71 | [0.51, 0.85] | 7 | 3/23 | 0.91 | 9/22 |

144 invocations, **100% yield** — every subject returned a parseable work
graph on every task. 141 of 144 parsed against the schema. Median prompt
33 KB, median 70 s per task, roughly 1.7M input tokens across the sweep.
`cc-glm-5-3-max` is measured outside its `supported_pass_types`, which the
card's placement nuance permits for information.

## What the numbers say

**Read the first two columns together or not at all.** The two tuples with
the best mechanical scores produced the smallest graphs. `codex-terra-max`
cleared every check on all 24 tasks with a median of 4.5 packets, 6 of its
graphs carrying two packets or fewer. `claude-harm-opus-5-high` scored 0.88
with a median of 7. The ranking and the amount of planning run in opposite
directions.

That is not a quirk of one subject. Pooled over all 141 parsed graphs:

| graph size | n | pass rate | 95% CI |
|---|---|---|---|
| 1–2 packets | 27 | **1.00** | [0.88, 1.00] |
| 3–5 packets | 53 | **1.00** | [0.93, 1.00] |
| 6–9 packets | 56 | 0.70 | [0.57, 0.80] |
| 10+ packets | 5 | 0.60 | [0.23, 0.88] |

**All 86 graphs with six packets or fewer passed every mechanical check.**
The smallest failing graph has seven packets; the largest passing one has
fourteen, so this is a probability that climbs with size, not a threshold.

The mechanism is arithmetic. Every one of the 73 legality failures in the
sweep is `scope_overlap`, and a k-packet graph offers k(k−1)/2 packet pairs
that can collide. Decomposing the work into more packets buys more chances
to fail the only check that ever fires. On this corpus, in this
environment, `planning.finishability/1` is close to an inverted proxy for
how much the planner decomposed the step.

Two consequences follow, and the sweep's main deliverable is really these:

1. **This rate must not be used to rank tuples for placement.** Ranked
   bare, it puts `codex-terra-max` first partly for planning least. No
   quartermaster objective was installed over it; see Housekeeping.
2. **A size-normalized successor exists and behaves.** The share of packet
   pairs whose write scopes collide does not fall merely because a graph is
   bigger — median 1.00 for 2–5-packet graphs against 0.92 for 6+, where
   the binary rate falls 1.00 → 0.70. Beside it, whether any two packets
   declared the *identical* write scope is a defect no tree access would
   excuse, and it separates the subjects: `cc-glm-5-3-max` 9 of 22 graphs
   and `claude-opus-5-high` 9 of 22, against 2–3 of ~20 for the terra pair.
   Neither is claimed here — inventing a metric mid-sweep and scoring on it
   is how an instrument talks itself into a result — but both are computed
   in `scripts/planning_sweep_report.py` and are the natural basis for a
   `planning.finishability/2`.

Resolvability did not fail once across all 141 parsed graphs. Once the
registry was actually in the prompt, that half of the construct stopped
carrying information, and the finishability rate is in practice the
legality rate.

On the placement question that motivated the sweep: both `disabled` terra
tuples probed alive, so their status is a placement decision and not an
exhausted account, and both scored at the top of a metric that this record
argues should not be used for ranking. That is an argument for measuring
them properly under a tree-mounted environment, not for re-enabling them on
this evidence.

## What this sweep does not establish

1. **It does not measure the implementation-planning pass.** It measures a
   composite no production lane performed, scored by the downstream pass's
   gate. Treat it as a mechanical probe of packetization competence, not as
   the planning gate's verdict.
2. **It is not comparable to `planning.independent_acceptance/1`** despite
   both carrying the word *finishability*. That construct's
   `finishability_pass_rate` is striatum's `implementation-plan-finishability`
   gate applied by independent-family model review to a prose plan; this one
   is mechanical work-graph legality. A subject can sit high on one and low
   on the other with neither number wrong, and this sweep does nothing to
   refute the Tier B numbers that motivated it.
3. **Write-scope reality and atomicity went unscored.** Design-only means
   the oracle runs without `-tree`, so both verdicts are
   `tree-not-provided`. Two of the card's five Arm 1 checks did not run.
4. **Plan-promise coverage went unscored.** The oracle has no such check,
   which is exactly why a near-empty graph clears every gate.
5. **Resolvability stopped discriminating.** Once the registry was in the
   prompt, nearly every subject resolved nearly every check, so the
   finishability rate is in practice the legality rate.
6. **The dominant failure class is partly induced by the environment** —
   see below.
7. **No agy tuple was measured.** Its declared adapter pins
   `review-ledger.schema.json` and a `stdout_json_pointer` of
   `/structured_output` that its runtime never emits; under that
   declaration one call errored outright and another produced a correct
   work graph that nothing could extract. Production routed 20 of the 348
   corpus tasks to agy tuples, so striatum is doing something the
   declaration does not describe. That is a finding for striatum, not
   something CAPLAB should patch around — patching it would measure a tuple
   striatum does not dispatch.
8. **n = 24 per subject.** The Wilson intervals are wide and adjacent
   subjects overlap throughout. Only the extremes separate —
   `codex-terra-max` [0.86, 1.00] against `claude-opus-5-high`
   [0.51, 0.85] — and that separation is the artifact this record spends
   its length explaining, not a capability difference.

## The schema cannot express a verification-only packet

Every parse failure in the sweep is the same shape, produced independently
by three subjects from three model families (`claude-opus-5-high`,
`codex-sol-high`, `cc-glm-5-3-max`) on the same task
(`revise/striatum-next/cli/cancel-verb/implementation-plan/2281`): a final
packet that verifies the assembled change-set and *mutates nothing*, so the
planner left `outputs` and `write_scope` empty. Work-graph v2 requires every
packet to carry both, and the parser rejects the graph —

    workgraph: v2 packet "p6" requires outputs, write_scope, and acceptance_checks

The planners were not being sloppy; one wrote the intent into the packet's
own purpose ("mutates nothing"). A plan whose last step is a whole-surface
verification cannot be expressed in the schema without giving that packet
outputs it does not produce. Three families converging on the same rejected
shape, on the same step, is the corpus saying the schema is missing a case
rather than three subjects making the same mistake. This is a finding for
striatum alongside the registry drift and the agy declaration, and a reason
to read the parse-failure count as a schema signal before a planner one.

## The confound that limits every number above

`scope_overlap` — parallel packets declaring overlapping write scopes — is
the dominant legality failure across every subject. It is also concentrated
entirely in graphs that use directory-grain write scopes: among the 47
parsed graphs from the two Anthropic subjects, failing graphs used
directory-shaped scopes **100%** of the time against **61%** for passing
graphs, and failures frequently show two packets claiming the identical
directory.

A planner that cannot see the base tree cannot name file-level scopes, so
it defaults to directories, and directories collide. The sweep therefore
does **not** cleanly separate *this planner declares overlapping scopes*
from *this planner cannot name files it cannot see*. This is the strongest
argument for running §3.1's option 2 — the base materialized into the case
workspace — as a second environment version, and for treating the current
legality numbers as a floor rather than an estimate.

## Containment

Every lane ran under `iso-v1` bubblewrap with `~/git` masked and a neutral
workspace cwd. Across all subjects and every task, **zero files were
written** to any workspace, though the prompts name live repository paths
throughout. Scar tissue 5 holds.

## Housekeeping

- Claims: `planning.finishability/1`, custody `caplab-advisory`, appended to
  `advisory/claims.jsonl` with Wilson intervals, `n_pairs`, and the
  structure metrics beside every rate.
- **No quartermaster objective was installed.** One was drafted and then
  withdrawn: a ranking over a rate that falls with graph size would launder
  the artifact above into placement advice. The leaderboard instead renders
  median packets beside the rate, under a note saying why the rate cannot be
  read alone. When a size-normalized metric exists, it gets an objective —
  and it must never be merged into `striatum-planning-draft/1`, since summing
  a mechanical construct with a model-judged one is the category error this
  record exists to prevent.
- **Striatum's preference list is untouched.** CAPLAB measures; placement is
  striatum's, and the card says so.

## Next

- The base-materialized environment, on a matched subset, as `plan-v2` /
  `tree-mounted`. It lifts the scope-overlap confound and scores the two checks that did
  not run here.
- Report the agy declaration mismatch to striatum.
- Arm 2 (`planning.defect_discrimination/1`) remains unstarted; its controls
  must be audited before anyone is scored, and the calibration arm here is
  the pattern to copy.
