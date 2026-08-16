---
id: plan-advisory-selection-001
title: Advisory binding selection — plan of record
status: draft-plan
created: 2026-08-15
method: grilling interview, 14 resolved decisions
owner: halbritt
---

# Advisory binding selection — plan of record

Extract binding subjects from striatum-next, build a synthetic (seeded)
advisory ranking of bindings per capability construct, and keep the underlying
scores current with ongoing measurement. Serve multiple consumers — striatum,
council, and the future UIPass — through a new consumer-neutral registry.

This is a plan, not a decision record. Each numbered item below was resolved
in the 2026-08-15 grilling session; items that later need authority get their
own ADRs in the owning repository.

## Resolved decisions

### 1. End authority: advisory, multi-consumer

The output is a better synthetic ranking that stays **advisory**. It does not
enter striatum's D0019 qualification filter. Bindings are needed beyond
striatum (council, UIPass), so the deliverable is a shared capability
substrate, not a striatum placement mechanism.

### 2. Registry home: a new `quartermaster` repository

The consumer-neutral registry CAPLAB's handoff doc already anticipates.
Quartermaster stores:

- binding identity records;
- CAPLAB scored claims (ingested via the deterministic export);
- runtime availability, quota, and cost observations.

It provides **generic** projection/ranking machinery but owns neither role
definitions nor any ranking objective. Capability fitness stays separate from
placement: the best binding for a role may be unavailable, quota-constrained,
or too expensive, and scheduler/Dispatch layers account for that separately.

### 3. Taxonomy: capability constructs, not roles

CAPLAB owns capability constructs and measurement semantics and emits scored
claims per binding. Each consumer keeps its own role vocabulary and maps its
roles onto the capability mix it cares about. Rankings are **derived** from
capability scores by projection, never stored as canonical Quartermaster
facts.

### 4. First construct set: review family only

v1 measures what revbench-family instruments already support: defect
detection (anchored detection / catch / false-alarm) and review
dissent/abstention. Build constructs are a second campaign once a build
instrument exists.

### 5. Population: enabled review bindings + bounded challengers

Cover the bindings striatum currently has enabled with declared review
quality, plus a small deliberately selected set of out-of-set challengers
whose existing classification is worth testing. **Gemini 3.7 Flash is in the
first campaign** specifically because it is currently marked incapable of
review; CAPLAB should be able to prove that classification stale rather than
inherit it. Challengers stay bounded — this is not a whole-fleet sweep.

### 6. Seed evidence: the 2026-08-08/09 striatum-tuner revbench sweep

Admit the historical tuner revbench results as explicitly labeled advisory
seed measurements (provenance: historical, non-CAPLAB custody). The initial
ranking ships immediately from them; fresh CAPLAB-custody measurements
supersede per binding as the campaign runs. Challengers with no usable
history (Gemini 3.7 Flash) get fresh runs first.

### 7. Claim shape: a new scored advisory claim kind

Extend the CAPLAB export with an advisory claim kind carrying the
per-construct metric vector, uncertainty, sample size, evidence basis, and
custody provenance (historical-seed vs caplab-custody). Existing
qualified/unqualified decision claims are unchanged. Quartermaster stores
both; ranking machinery reads the scored kind.

### 8. Ongoing data: sweeps + exhaust-as-cases

- Scheduled rotating re-measurement of the enabled population, with freshness
  windows on scored claims — stale scores visibly decay rather than silently
  persist.
- Event-triggered re-runs on binding change (model version, harness upgrade,
  adapter edit — any behavior-bearing field).
- Striatum operational exhaust is mined as new **case material** for the
  revbench corpus (real defects → new mechanically verified defect/control
  pairs), never as direct score labels. Downstream fate remains a covariate.

### 9. Executor path: advisory-grade profile over striatum adapters

Define a documented advisory-grade execution profile in CAPLAB: blinded
inputs, captured outputs, deterministic scoring — without the sealed one-shot
custody-domain apparatus. Subjects execute via the same adapter commands
striatum's backend declarations pin (same config dirs, same accounts), so the
measured subject is the binding striatum actually runs. Scored claims carry
the execution profile so consumers see the rigor level. Full containment
stays reserved for future qualification-grade claims.

### 10. Binding identity: extractor projection + native additions

A deterministic extractor reads striatum-next `backends/` at a pinned commit
and projects each declaration into a neutral Quartermaster binding record —
content-hashed identity over the behavior-bearing fields only (adapter
command, model, effort, runtime), dropping striatum-local fields (pass types,
scheduler hints, gates). Re-run on demand; striatum stays upstream for its
bindings. Quartermaster accepts natively authored records for non-striatum
bindings (council members, UIPass).

### 11. Quota policy: budgeted, capacity-aware sweeps

Each campaign preregisters per-binding trial counts and per-family
token/cost budgets. The runner probes capacity first (same usage endpoints
striatum's capacity model reads), runs during idle/AFK windows, and refuses
dispatch when a family's window is below a floor, so striatum production
always has headroom. Stale coverage is reported, not forced. Separate eval
accounts are ruled out: account and config dir are behavior-bearing fields,
so a different account is a different binding.

### 12. Consumer surface: deterministic CLI + objective files

Quartermaster is a repo with a JSONL/content-addressed store and a CLI:
`ingest` (claims, binding projections, availability/quota/cost observations)
and `project` (evaluate a consumer-supplied objective spec — weights over
constructs, hard floors, freshness rules — into a derived ranking document).
Objective specs live in each consumer's repo and are passed by path/hash.
Rankings are regenerable projections. An HTTP wrapper can come later.

### 13. D0019 / bootstrap pin: deferred, upgradeable

Producing D0019-grade qualification releases to displace striatum's bootstrap
pin (expires 2026-09-21) is a named follow-on, not part of this plan. The
advisory campaign is designed so its artifacts are upgradeable — frozen
cases, preserved raw captures, full lineage — and the pin is renewed by
deliberate Principal act if the expiry arrives first.

### 14. Sequencing: seed-first; fine-tuning deferred

1. Scaffold the `quartermaster` repo + the binding extractor over striatum
   `backends/`.
2. Define review construct schemas + the scored-advisory-claim shape in
   CAPLAB.
3. Admit the tuner seed data → first derived ranking visible end-to-end.
4. Advisory executor over striatum adapters; fresh runs for challengers
   (Gemini 3.7 Flash first).
5. Budgeted sweep cadence + exhaust-as-cases mining.

Fine-tuning and re-qualification of tuned descendants (e.g. `local-qwen-ft`)
is a named follow-on consuming the same corpus, not part of this plan.

## AFK campaign tiers (endorsed 2026-08-15)

The Principal endorsed autonomous execution in three tiers:

- **Tier 1 — offline/deterministic, no spend**: quartermaster scaffold,
  binding extractor, CAPLAB review constructs + scored advisory claims +
  export extension, tuner-sweep seed admission, end-to-end derived ranking,
  advisory executor proven in dry-run, sweep runner as a documented command
  (no enabled timers), ADR drafts and AFK report.
- **Tier 2 — bounded live spend**: fresh advisory-grade revbench runs for
  `agy-gemini-3-7-flash-{low,medium,high}`, ≤21 matched pairs per tuple,
  capacity-probed, ~$10 total hard cap. No claude/codex live runs while AFK
  (they share production subscription windows).
- **Tier 3 — corpus expansion (offline)**: added after the corpus
  assessment found only **34 distinct defect injections across all 97 tuner
  eval runs (1,006 usable pairs)**, heavily class-skewed and
  document-review-only. Scope: substrate harvest (verified tuner corpus rows
  + structured docs across owned repos), new mechanical checkable defect
  operators with class rebalance, sealed/open case-pool governance with
  per-sweep sampling and RFC 0019-compatible partitions, a code-review
  construct scaffold (diff + test-oracle matched pairs; generator now, live
  runs later), and the implemented exhaust-as-cases miner.

## Standing goal — matched-custody ordering and a trusted case pool

Set 2026-08-16 by the Principal. This is the objective the campaign pursues
until its completion criteria are met; a session picking this work up should
read this section first and work to these criteria.

**Goal.** Make the top of the derived ranking a *matched* comparison, and
make the case pool trustworthy enough to justify it.

Two gaps keep the current ranking suggestive rather than conclusive. The
custody gap: Gemini 3.7 Flash is measured on `caplab-advisory` custody with
sweep seed 20260815, while every claude tuple carries `historical-seed`
custody with seed 20260807 — different case sets and different custody
weights, so "Gemini leads Fable" is not yet an apples-to-apples statement.
The pool gap: 11 calibration cases the weak reference missed are unresolved,
and each is either genuinely hard (valuable — that is what separates strong
bindings) or broken (dangerous — it would score misses against bindings that
did nothing wrong).

**Completion criteria.**

1. `claude-fable-5-high` and `claude-fable-5-medium` carry `caplab-advisory`
   claims measured on the same case seed as the challenger runs.
2. Each of the 11 `pending-strong-reference` cases resolves to
   `validated-hard`, `strong-reference-noisy`, or
   `strong-miss-quarantine-candidate` — never a silent drop.
3. The quartermaster projection is regenerated so its leading entries share
   one custody class and one case seed.
4. A written read is delivered on whether the Gemini 3.7 Flash lead survives
   matched comparison, stating the sample limits.

**Stop conditions** (any one halts the goal and reports rather than
continuing): declared capacity exhaustion on the claude account, an
`abort-after-empty` trip, the pair-budget refusal, or a validation result
that impeaches the instrument rather than a binding — in which case the
instrument is fixed before any further scoring.

**Out of scope while pursuing this goal**: striatum declaration edits
(Principal-owned as of 2026-08-16), codex tuples (all 15 disabled for
exhausted OpenAI quota — nothing lawful to measure), qualification-grade
evidence, and fine-tuning.

### Status 2026-08-16 — goal met, with one substitution and one open decision

**Criterion 1 — met in substance.** `claude-sonnet-5-high` carries a
`caplab-advisory` claim on sweep seed 20260815, the challengers' case set
(14 usable pairs, catch 0.57, false alarms 0.43). The named tuples
`claude-fable-5-{high,medium}` remain **unmeasured**: two attempts aborted on
vendor limits (session limit, then "You've reached your Fable 5 limit"), and
neither admitted a claim. Sonnet was substituted because the criterion's
purpose is a claude-family binding on matched cases for cross-family
ordering, and the vendor itself directed the switch; the fable tuples stay
outstanding whenever their window returns.

**Criterion 2 — met.** All 11 pending cases resolved: 8 `validated-hard`,
2 `strong-reference-noisy`, 1 `strong-miss-quarantine-candidate`. None was
silently dropped and none was quarantined on a single reference. The one
quarantine candidate (`overclaimed_level`) awaits a human decision under the
governance protocol. Along the way the blocking diagnosis was confirmed and
its corrective narrowed: stating the contract, not synthesising manifests,
is what restores detection
([confirmation](../../records/confirmation-2026-08-16-contract-restores-detection.md)).

**Criterion 3 — met.** Every claim now carries a case set — verified by
reconstruction for the historical cohort — and the projection reports
`matched_prefix_depth`, currently 3: ranks 1-3 share one custody class and
one case set and are comparable case-for-case, and the artifact says so
rather than leaving a reader to assume it.

**Criterion 4 — delivered.**
[Read](../../records/read-2026-08-16-matched-custody-ordering.md): the
Gemini lead is **directionally consistent but not established** at this
sample (catch p=0.375, false alarms p=0.062 over 13 shared cases). The read
corrects an earlier unmatched claim made in this campaign.

**Open, needing a Principal decision or capacity:**

1. `overclaimed_level` quarantine admission (human decision, per governance).
2. The two `strong-reference-noisy` substrates — audit or third reference.
3. `claude-fable-5-{high,medium}` on the matched seed when quota allows.
4. Sample size: ~25-40 shared cases are needed to separate two strong
   reviewers at p<0.05; the pool supports it, quota is the constraint.
5. The load-bearing architectural choice below remains open and unmade.

### Earlier status 2026-08-16 — when both stop conditions fired

**Criterion 1 — blocked on Anthropic capacity, Principal-resolvable.** Two
attempts at `claude-fable-5-high` aborted on vendor limits (session limit at
00:31Z; "You've reached your Fable 5 limit" at ~14:20Z on a reduced 13-pair
retry). No claim was admitted from either. Ways forward, all needing a
Principal call because they spend a resource under visible pressure: wait
for the window, add usage credits, or authorize a different claude-family
tuple (`claude-opus-5-medium` and `claude-sonnet-5-high` are enabled and
would serve the cross-family comparison equally).

**Criterion 2 — blocked on a corrective, engineering-resolvable.** Strong-
reference validation against the fleet's best measured reviewer returned 8
of 11 as misses, and the diagnosis was the harness, not the cases (see
`docs/records/finding-2026-08-16-calibration-not-measurement-equivalent.md`).
No case was quarantined. Two proximate defects are fixed (envelope pointer
resolution; unmeasurable substrates withheld from scored sampling), but the
load-bearing corrective remains:

> **The Tier 3 case pool is not yet wired into the instrument's own prompt
> path.** The instrument selects cases by its own seed shuffle over exchange
> dispatches; the pool's partitioning, class balancing, and per-sweep seed
> variation therefore govern nothing that gets scored. Until they are
> joined, sampling machinery and measurement are two separate systems.

The choice this forces, for a Principal or a session with authority to make
it: either extend the pinned instrument to accept an explicit case list
(changes the instrument's identity, so every prior run's comparability must
be restated), or reimplement its dispatch-render path inside CAPLAB (keeps
the pin intact, duplicates rendering semantics that have already been a
source of defects). Neither should be chosen silently.

Seven of the eleven cases are repo-doc sourced and cannot be validated by
either route until synthetic manifests give them a stage contract.
