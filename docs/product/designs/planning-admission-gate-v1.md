---
design_id: planning-admission-gate-v1
artifact_type: design
status: proposed
decision_owner: repository-owner
author: CAPLAB execution delegate (Claude), 2026-09-04
supersedes: planner-evaluation-v1 (parked) as the planning measurement of record
relates_to:
  - docs/product/capability-cards/planning-constructs-v1.md
  - docs/product/designs/planner-evaluation-v1.md
  - docs/records/report-2026-09-04-planner-ranking-disposition.md
---

# Planning admission gate: pass/fail per binding, then route on cost

A **recommendation**, drafted to the Council disposition of 2026-09-04
(§3.1–3.3, §5.2–5.4). It specifies what CAPLAB would measure, once, when a
new binding or harness version appears, so that striatum can admit it for
planning or refuse it; and what striatum-side telemetry then keeps admitted
bindings honest. It does not order bindings. Ordering among admitted
bindings is operational — cost, latency, quota, context window — and lives
in Quartermaster, not in a capability claim.

## 1. The question the gate answers

*Is this binding defective or regressed for planning?* Not *is it the best.*
The framing follows the Council's restatement of the goal: striatum absorbs
weekly model churn, any frontier planner is probably adequate, and the only
failure worth paying to detect is one that would put bad plans into the
build pipeline. A gate that says yes/no with stated error bounds, in under
an hour of lane time, on a fixed task set, is the instrument for that
question.

## 2. Three probes, one verdict

Each probe is mechanical or reuses machinery that exists and is audited.
Thresholds below are **proposed** and are the Principal's to set; every
number is a Wilson interval, never a point.

### 2.1 Probe A — lowering legality, tree-mounted (`planning.finishability/1`)

- **Task set.** A fixed, named draw of **12 tasks** from the
  implementation-planning corpus (pass-disjoint, 6 produce / 6 revise,
  seeded; the set is versioned and the same for every binding). Prompts
  under the 100 KB transport, so no task is dropped.
- **Environment.** `iso-v1`, **`tree-mounted`**: the pinned base is
  materialized in the case workspace, so the oracle scores write-scope
  reality and atomicity and the planner can name file-grain scopes.
  Instrument pinned (oracle hash, registry version) on every row.
- **Contract.** `plan-v2`. Registry index of resolvable check sets in the
  prompt.
- **Verdict.** Yield: graphs that parse, index, resolve, and are
  tree-consistent, out of 12. **Proposed floor: ≥ 10/12** (Wilson lower
  bound above 0.55). Below the floor the binding is not admitted for
  planning; between 10 and 12 the failures are listed on the claim.
- **What it does not do.** It does not rank (P2b, 2026-08-27). Two bindings
  at 12/12 are equal here.

### 2.2 Probe B — plan-defect discrimination as a reviewer (`planning.defect_discrimination/1`, Arm 2)

The binding reviews work graphs. It is shown a sound control graph and, in a
separate call, the same graph with one audited defect injected, under a
plan-review contract, and returns a verdict with findings. This is the
review instrument's shape (matched pairs, mechanical ground truth), and it
is the probe that catches the oracle-silent failure modes — dropped
deliverable, purpose/scope contradiction, overclaimed verification, the
atomicity split — that Probe A cannot see.

- **Material.** The nine audited operators over the 59 sound
  production-accepted controls (real accepted plans) and, where a class is
  thin, the 164 sound sweep controls, labelled as synthetic. **Proposed:
  4 pairs per class, 36 pairs, 72 calls**, planner-balanced, seeded.
- **Contract.** `plan-review-v1` (to be written): REVIEW ONLY preamble,
  the task's design and context, the registry index, one graph, verdict
  `accept | needs_revision` with anchored findings. The contract version
  is claim identity.
- **Verdict.** Catch (needs_revision on the mutant) and false alarm
  (needs_revision on the control), both with Wilson intervals; anchored
  share (finding names the injected packet). **Proposed floor: catch lower
  bound ≥ 0.5 and false alarm upper bound ≤ 0.4** on the 36 pairs; the
  size probes (`atomicity_split`, `merge_independent_packets`) are reported
  but not counted in the floor.
- **Control audit first** (scar tissue 1): every control is sound under the
  pinned oracle before any pair is shown; a control refused by two
  admitted bindings is queued for adjudication, as the review corpus does.

### 2.3 Probe C — execution canary (`planning.execution_yield/1`), optional

- **Material.** 5 of the 12 Probe A tasks, chosen once and fixed. The
  binding's graphs from Probe A are built packet by packet by **one fixed
  executor** (proposed: `cc-glm-5-3-max`, the cheapest admitted builder
  with a measured review class), each packet's declared `acceptance_checks`
  run through the checks registry after its build.
- **Verdict.** First-pass check rate over ~25 packets; closure without
  replan. **Proposed floor: first-pass ≥ 0.6** with the interval reported.
  Because the executor is fixed and named, the number is the pair's, and
  it is read as a canary — a large shortfall is a finding to investigate,
  not a rank.
- **Cost.** ~25 packet builds, under an hour on the fixed executor.

### 2.4 Probe D — single-judge sanity pass, optional

One independent-family judge (calibrated 2026-09-03: Gemini 3.7 Flash
caught 106/106 oracle-silent defects) reads each of the binding's 12 Probe A
graphs beside its design and answers one question per graph: *does this
graph omit a deliverable the design names, or claim verification it does
not check?* Yes/no with a named packet. ~12 calls. Not pairwise, not a
score: a flag list for the human reading the admission record.

### 2.5 The verdict

A binding is **admitted for planning** when Probe A clears its floor and
Probe B clears both floors. Probes C and D are advisory findings on the
record. Admission is a Principal decision on the claims; the gate produces
the claims. All admitted bindings are equivalent for planning; nothing in
this design orders them.

## 3. Routing among admitted bindings

Operational, in Quartermaster: cost per planning call, p50/p95 latency,
window headroom, context window. A preference list ordered by cost among
admitted bindings, revisited only when production telemetry (§4) diverges.
CAPLAB supplies the admission claims and nothing else here.

## 4. Production telemetry and the regression alarm

Striatum records every packet gate. `scripts/planning_production_fate.py`
attributes packets to the producer of the pass's accepted plan and reports,
per producer, plan-gate outcomes, packet first-pass rate, rework ratio,
packet-review failure rate, and quarantines (see the disposition record for
the first table). This is a **covariate** — scheduler-routed, different
tasks per producer, different builders per packet — and the fate firewall
keeps it out of qualification claims. The Council's three uses:

1. **Shadow slice.** A new binding plans 10–20 sampled production tasks
   alongside the incumbent, without affecting execution; compare legality,
   reviewer rejection, replan, build yield; promote on non-inferiority within
   a deliberately wide margin.
2. **Exploration share.** 5–10% of planning tasks routed at random to the
   challenger; same gate outcomes over a fixed window; promote or demote on
   the comparison. Randomization removes the routing confound the fate table
   carries.
3. **Acceptance floor.** Per-producer packet first-pass rate below a floor
   over a window raises an alert and a replacement; this is the regression
   alarm, and it is striatum's to install.

Items 1–3 are striatum decisions; CAPLAB's part is the fate harvest and,
if asked, the non-inferiority comparison as a matched read.

## 5. What is kept from the parked design

- The nine operators and their audit (Probe B's material).
- The judge rubric, adapters and calibration (Probe D; Arm 2 gate-holder
  measurement).
- The pinned instrument and the `tree-mounted` environment (Probe A).
- The L2 executor design (Probe C).
- The clean-pair diagnostic (~450 calls) remains optional and unauthorized;
  its result would decide whether L1 is ever un-parked.

## 6. Cost per new binding

Probe A: 12 planner calls (minutes). Probe B: 72 reviewer calls (under an
hour at two lanes). Probe C: ~25 builds on the fixed executor (under an
hour). Probe D: 12 judge calls. Total well under a day of lane time and a
fraction of one review sweep — the scale weekly churn allows.

## 7. Decisions requested

1. Specify `planning.finishability/1 (tree-mounted, admission draw)` and
   `planning.defect_discrimination/1` on the card as the admission gate,
   with the floors in §2 or others.
2. Authorize the `plan-review-v1` contract and one Probe B run on the
   eight board bindings to set the floors on evidence rather than on the
   author's guess.
3. Decide whether Probe C's fixed executor is `cc-glm-5-3-max` or another
   admitted builder; the choice is claim identity.
4. Hand §4 items 1–3 to striatum as a request; CAPLAB will supply the fate
   harvest on demand.
