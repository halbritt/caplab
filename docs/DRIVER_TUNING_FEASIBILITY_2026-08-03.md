# Can a local model be tuned to drive Striatum?

**Date:** 2026-08-03 · **Author:** Claude (Fable 5), operator session on `striatum-next`
**Corpus:** `corpus-driver/` (built by `extract_driver.py`, this repo) — every agent
transcript on this box in which an agent drives striatum, extracted from the two
Claude Code accounts (`~/.claude`, `~/.claude-harm`) and Codex (`~/.codex/sessions`).
**Method:** three repo deep-reads (striatum-tuner pipeline, striatum-next control
surface, governance layer) + three corpus analyses (quantitative profile, activity
taxonomy from primary transcripts, dataset design), followed by a two-lane adversarial
verification pass whose corrections are folded in. Ledger-derived numbers were
reproduced exactly by an independent recount; corpus-derived numbers are labeled with
the corpus version they were computed on.

---

## 1. Question and verdict

**Question.** We have ~three months of agent logs — Claude and Codex sessions issuing
`striatum request / drive / status / resolve / accept / reject` and deciding what to do
next. striatum-tuner already turned lane transcripts into a tuned local review model
that is deployed and serving (`local-qwen-ft`). Can the same machinery tune a local
model to act as **the driving agent** (the operator role)? If not readily — should the
control surface be narrowed, or the dataset improved?

**Verdict.** Not as *the whole operator* — and the whole operator is the wrong target.
The corpus shows the operator role decomposes into:

1. **A polling loop (~84% of modern-dialect striatum calls)** whose *cadence* is
   near-deterministic (v2 recompute: status→status 75.0%, ledger→ledger 80.9%
   self-transitions) and already automated by the 5-minute systemd wake timers.
   Cadence should stay *code*, not weights. The one signal worth mining in this bulk
   is the **loop-exit decision** — what the operator saw right before choosing to
   intervene — because until stalls@5-class mechanization lands, silent wedges are
   detectable only by an operator reading output.
2. **A small judgment tail (7.5% of modern calls)** — resolve/accept/reject/cancel —
   whose decision context is compact and mechanically assemblable from the ledger.
   This is where a tuned model can genuinely help, **but not in the shape the raw
   logs suggest.** The lawful, already-delivered home for model participation is the
   **adjudication-preparation dossier** (evidence-only, never a recommendation), and
   striatum-next's own accepted design routes the base dossier to "the cheapest
   capable backend" — a slot designed for exactly this local model (§6).
3. **General software engineering (>80% of operator tool calls)** — stall RCA, Go
   fixes, redeploys. Out of reach for a one-shot local model and out of scope for
   "driving" proper; it is lane-shaped work that happens to be done by the operator.

Five gaps keep a tuned model out of the operator seat itself: **interface** (no local
tool-loop harness; `striatum-openai-lane` is deliberately one-shot), **data** (the 873
authoritative judgment records are at/below the proven bar, 94%-proceed prior — and,
decisively, they are records of the *forbidden output shape*; the lawful dossier shape
has only 14 ledger examples), **authority** (no-pre-scripted-resolutions; resolver
identity is bare `$USER`, so a model resolving would forge personal authority),
**output contract** (the delivered dossier gate refuses recommendation language
before evidence admission), and **data locality** (the registered corpus predicate
pins adjudication notes on-box — off-box training needs an explicit Principal export
direction).

Both user-named remedies apply, in order: **the control surface is already being
narrowed by delivery inside striatum-next** — ride it (§7) — and **the dataset
improvement the question asks about is itself a registered target state**,
`judgments-become-a-corpus@1`, which names deterministic extraction of exactly these
pairs, with the proceed-skew declared and the corpus kept on-box (§8). The
recommended path (§9) trains a **base-role dossier model** against the delivered
sealed contract and declares it as a backend capability — no new authority, no new
ontology, and the constitution's own cost rule pulls it in: "a harness that burns
frontier credits to prepare every dossier has failed this predicate."

---

## 2. The corpus (the reusable artifact)

`extract_driver.py` scans all three log stores, selects every transcript that invokes
the striatum CLI, and normalizes both harness formats (Claude Code session JSONLs
including subagent/workflow transcripts; Codex rollouts including the cells-runtime
`exec` encoding) into three JSONL files with `(file, line_no)` pointers back to the
raw logs, so capped fields are recoverable losslessly.

| file | grain | size (v2) |
|---|---|---|
| `sessions.jsonl` | one record per transcript file mentioning striatum (~6.1k), classified `driver` / `lane` / `mention` | 6.9 MB |
| `events.jsonl` | normalized event stream (user/assistant/thinking/tool_call/tool_result) for driver sessions only | ~860 MB, ~530k events |
| `striatum_calls.jsonl` | one record per striatum CLI invocation: verb, disposition, `--note`, command, output, preceding assistant reasoning | ~18.1k records |

Headline contents (corpus v2):

- **675 driver sessions** — 40 claude, 42 claude-harm, 593 codex; 314 main sessions +
  340 named subagents (à la "Harvey"/"Curie" spawned under operator sessions) + 21
  workflow agents. 433 sessions speak the modern striatum-next dialect; 242 are
  legacy-only. Lane transcripts (~1.5k) and mention-only files (~4k) are indexed but
  not event-extracted (lane data is the *other* corpus, `extract.py`'s).
- **18,063 striatum call records** (sessions from 2026-05-06; earliest call
  2026-05-07; through 2026-08-03): **10,484 modern-dialect** (the current verb
  surface) + **7,579 legacy-dialect** (`run`, `supervise`, `workflow`, `recovery`,
  `daemon`, `escalation`, `lease`… — the bootstrap striatumd CLI, labeled with their
  own verbs in v2). Two eras: May–June is 100% codex driving the **legacy bootstrap
  striatum** (near-useless for tuning the current verb surface); July onward is
  striatum-next, with claude/claude-harm joining in W27 and codex dominating the
  final days (07-31→08-03: ~724 codex calls, ~0 claude).

**Rebuild:** `python3 extract_driver.py --out corpus-driver` (~7 min).

**Known caveats** (quantified by an independent flag-aware reparse + manual audit):
v1 mislabeled ~14.8% of records (legacy `striatum supervise status` → "status");
fixed in v2 by matching legacy verbs first — which also correctly promoted ~240
legacy-only sessions from "mention" to "driver". The reparse leaves ~8% of records
unconfirmed as literal CLI invocations; a manual audit of a sample found most of
those are real invocations in quoted-binary/shell-variable style, with an
*extrapolated* ~2% true textual false positives (commit messages, patch bodies) —
treat that residue as unverified and re-filter at dataset-build time.
`(session_id, seq)` is not unique across resumed session files (~18% duplication risk
on naive joins — dedupe by `(file, line_no)`). `output` is capped at 8,000 chars
(~25% of `ledger` outputs truncated; pointers recover the rest). Bare
`striatum resolve <seq>` defaults to `proceed`, so a missing disposition flag is not
an unknown disposition. The corpus is a snapshot of live log stores — re-extraction
shifts counts slightly, and the analysis sessions themselves qualify as drivers (this
study's own agents ran `striatum ledger cat`), so exclude the extracting session's
transcripts when re-mining. Quantitative claims below are labeled v1 or v2 where the
distinction matters; ledger-derived numbers are era-independent.

---

## 3. What "driving striatum" actually is (empirics)

### 3.1 The loop is nearly deterministic

Verb-class mix of the 10,484 modern-dialect calls (v2): **83.7% read-only** (ledger
5,607 + status 3,140 dominate), **8.7% state-advancing** (drive 557, request 252,
init, reconcile), **7.5% judgment** (resolve 331, accept 258, reject 114, cancel 84,
revoke 3). The transition matrix is a two-state read loop with rare exits (v2:
status→status 75.0%, ledger→ledger 80.9%, drive→{ledger,status} 69.0%); judgment
verbs return to reads, and ~72% of modern-era sessions open with a read (v1 subset:
status 219 + ledger 43 of 364 first verbs). The *cadence* is already delivered as
code: `striatum drive` plus the per-repo 5-minute `striatum-wake-*` systemd timers
run it with zero judgment (`internal/cli/waketimer.go`; quiescence reasons enumerate
exactly what waits and why). What the polling bulk still carries that code does not:
the **intervention trigger** — the operator noticing that a read looks wrong. The
stalls@5 totality gap (zero-step recovery dead-ends that "consume the frontier
silently", per the repo's own standing-debt register) is currently detected only that
way.

### 3.2 The judgment tail is small, late, and compact

- Parse-confirmed modern-CLI judgment calls: **~676–697** (parser-definition
  tolerance), from **36–39 sessions**, ~88–89% in July 2026. ~250 carry `--note`
  (median 216 chars, p90 ~750).
- The **authoritative** record is the graph ledger, not the transcripts: across the 9
  registered graphs — **382 resolution_events** (main graph: 297, 294 with substantive
  notes), **351 acceptance-class gate_results** (245 accept / 106 reject), **140
  cancellation_records**. Reproduced exactly by two independent recounts.
- Decision context is bimodal in the transcripts: *cumulative* session context before a
  judgment call is prohibitive (median 1,622 prior events; codex median 2.9 MB of
  prior tool-result text) but the **local window is compact** — median 6 events /
  ~5 KB of tool results since the previous striatum call, and every confirmed
  judgment call has an immediately-preceding reasoning block (median ~245 chars). A
  model needs a curated state snapshot, not a transcript — which is precisely what the
  delivered dossier posture's sealed inputs already are (§6).
- Disposition prior is degenerate: effective **proceed ≈ 91–94%** (ledger: 278/297
  proceed, 15 cancel_request, 4 reissue), against escalation reasons 309
  bounds_exhausted / 31 ambiguous_goal / 1 independence_unsatisfiable. Two
  consequences: disposition-classification is nearly information-free (a
  constant-proceed model scores ~94%), and any eval gated on disposition agreement
  certifies nothing (§8). The learnable signal is the **diagnosis**.

### 3.3 What the notes actually contain

From the taxonomy pass over ~40 adjudications (file:line pointers preserved in the
session's workflow artifacts; representative quotes):

> "Read individually (delegated operator, RQ-1849 mandate). bounds_exhausted on
> redispatch budget for verify/… — but the packet itself is green: … both passed at
> 05:11:29, one minute BEFORE this escalation fired. The exhaustion is verify-receipt
> redispatch churn … not a quality signal and not an adjudication matter. Proceed."

> "Refused for target drift, not quality: this proposal designs a NEW generic RFC
> well-formedness checker; the registered predicate (read it verbatim) is far
> narrower: the lint-rfcs tool ALREADY EXISTS."

Roughly **52% of noted resolves are pattern-shaped** (stale-signal churn, transient
capacity bursts, environmental exonerations) with context that fits one prompt;
**~26% cite a root-cause code fix** the operator made — those are meaningless without
the repair and are out of scope for any narrow policy. Acceptance/rejection consults a
bounded artifact set (candidate body from the object store, review ledger, target-state
predicate YAML, freshness state). Rejections fall into three classes (staleness-only
mechanical; tool-checkable mechanical defect; target-drift judgment). A caution the
verification pass added: 204/297 resolution scopes re-escalated later — usable as an
outcome signal, but it also means the recorded dispositions are imperfect SFT targets
and imperfect eval ground truth.

### 3.4 Most operator effort is not driving

Striatum calls are **7.9%** of the 227,821 tool calls in v2 driver sessions (claude
~16.6%, codex ~7.1%; the earlier v1 figure was 5.7% of 210,783). The dominant
activity by effort is **stall diagnosis and repository repair** (~25–30%): RCA → Go
fix in a worktree → full test suite → staged redeploy → only then resolve the parked
escalations "against the fixed runtime." The flagship 8,311-event codex session
(2026-07-30) spent its volume on `sed`/`rg`/`go test`/`git`, not striatum verbs.
Judgment moments that no narrow policy could make are well documented: the
mutual-invalidation-livelock diagnosis, the refusal to `proceed` because it "would
merely license another nine attempts while the same premature Decision Record path
may still exist," the authority-fork recognition ("The immediate fork is Principal
adjudication, not remediation"). Any tuned-model plan must route these to escalation,
not attempt them.

---

## 4. What striatum-tuner has already proven

The review-lane campaign establishes the whole downstream pipeline:

- **Recipe:** QLoRA (NF4, rank 32 / α 64, cutoff 40,960, no-think, Liger fused loss),
  882/98 candidate-aware time-ordered split; 35B-A3B MoE trained on a single H200 with
  routed experts frozen (42.3M trainable params), **~$23 for the full run, ≤ $43.47
  campaign all-in** under the hash-pinned runpod-jobrunner contract with the 3-gate
  smoke ladder.
- **Result:** tuned 35B fate agreement **53.1%** (0.5306 on all 98 held-out rows) vs
  the untuned 35B baseline's **18.8%** (on its 85 scoreable rows), 100% JSON-valid /
  legal verdicts, passing all strict gates
  (`docs/results/qwen-27b-35b-training-report-2026-08-03.md`; the
  `eval-runs/ft-r1-nothink/` artifact is the tuned **27B** at 39.8% — a different,
  weaker model). Frontier reference ceiling: codex-sol-max 83.2%.
- **Deployment discipline:** served as base + LoRA adapter on the existing llama.cpp
  slot (port 8081, alias `qwen3.6-ft`), thinking suppressed per-request, **new backend
  identity** `local-qwen-ft` (review-only, own seal key, old `local-qwen` retained
  disabled so attribution never mixes), pytest guard pinning alias/adapter/base/port.
- **Boundary:** everything is single-turn `[user, assistant]`. No tool-role messages,
  no multi-turn examples, no agentic harness. `build` is excluded from extraction for
  exactly this reason ("until the local harness grows a tool loop"). DPO was built
  (77 pairs on disk; README says 78) but never trained; the deployed adapter is pure
  SFT.

The training contract, serving slot, and deployment discipline transfer to a
driver-adjacent tune unchanged. What does **not** transfer — established by the
verification pass — is the dataset shape: the historical adjudication records are not
in the lawful output format (§6), so the dataset builder is a genuinely new
transformation, not a `make_sft.py` variant.

---

## 5. Why "the driver" is not readily tunable (five gaps)

**Terminology note.** In striatum, *the Driver* is the deterministic program — making
it intelligent is a named forbidden failure mode. What we would tune is the
**operating-agent / agent-principal role**: the loop above the Driver that issues
verbs. The ontological home for a non-human holder of that role already exists — RFC
0006's **Agent Principal**, "an agent runtime exercising a recorded, bounded
delegation of Principal-issuable acts … Its every act carries its identity and
delegation reference."

1. **Interface.** The operator loop is multi-turn tool use; nothing local can host
   it. `striatum-openai-lane` self-describes as "no agent loop, no tool use, no
   session state." Median codex driver session is 521 events, p90 1,148 tool calls,
   and raw actions are compound host-specific bash under three different harness APIs
   — whole-session imitation learns wrapper trivia. (This is an engineering gap, not
   a constitutional one: the Agent Principal slot exists; what's missing is a harness
   and the grant/identity of gap 3.)
2. **Data.** The unified adjudication pool (382 + 351 + 140 = **873** authoritative
   records) only marginally clears the 882-example bar that worked for review — and
   only as a multi-task union; resolve-only (382) is 43% of the bar. The disposition
   prior is 94% proceed. 60% of notes cite ledger seqs/RQ ids (citation-grounding
   risk). The deep investigations behind ~26% of resolutions are not in the record.
   And — the decisive point from verification — **these 873 are examples of the
   forbidden output shape** (selected dispositions and verdicts); the lawful dossier
   shape has exactly **14** ledger examples. Schema drift compounds it: the
   repo-pinned `bin/striatum` can no longer read the live ledger
   (`schema_newer_than_reader`) — context must be re-rendered at HEAD vocabulary.
3. **Authority.** The standing Principal rule: **"no pre-scripted resolutions, ever …
   Each escalation is read and adjudicated individually by whoever actually holds the
   authority. Babysitter/drive loops may poll and report escalations; they may not
   resolve them."** A fine-tune that maps escalation shapes to dispositions is
   pattern-matching *in weights*. The lawful slot for delegated resolution exists
   (RFC 0006 "named escalation-resolution classes" in `policy/gates.yaml` — the
   expired-2026-08-03 `harvest-issuance` entry is the delivered template for the
   grant shape), but no resolution class is instantiated, and mechanically the
   resolver identity is bare `$USER` with `authority_proof: nil` — a model acting
   through the raw CLI would forge personal authority. Never delegable to anyone:
   RFC-grain acceptance, decision-record acceptance, rejection-as-authority, gate
   override (structurally refused in the shipped binary anyway), naming.
4. **Output contract.** The delivered adjudication machinery *forbids* the obvious
   training target. `catalog/review-postures/adjudication-preparation.yaml`: the
   posture "never selects, recommends, records, or implies a disposition";
   `forbidden_outputs: [resolution_event, gate_result, selected_disposition,
   recommendation]`. `catalog/gates/dossier-content-review.yaml` refuses evaluative /
   preference / recommendation language **before evidence admission**. A
   `{disposition, note}` drafter — the shape the historical data suggests — is
   precisely the walled-off artifact; its outputs would refuse at the gate.
5. **Data locality.** `catalog/target-states/judgments-become-a-corpus.yaml`
   (accepted; no request issued yet) pins the adjudication corpus **on-box**: "it
   carries Principal adjudication notes; local-first, no export without explicit
   direction." Training on a rented H200 is an export; QLoRA of the 35B on the local
   24 GiB 3090 is not feasible. Off-box training therefore has an explicit
   prerequisite: a Principal export direction (or an on-box-capable smaller base).

---

## 6. The lawful target — and it is already built

The verification pass inverted the naive recommendation into a better one. What I
initially drafted — a `{disposition, note}` adjudication drafter — is forbidden by
the delivered contract (gap 4). What the constitution *wants* is already **delivered
and Verified**: `escalations-arrive-dossiered@1` is `[satisfied: Verified]` since
2026-07-10 (RQ-42611; work-graph integration RQ-46878; planner dual-dossier machinery
live with tests, `internal/planner/dossier_test.go`), with:

- **Sealed inputs, no exploration:** the driver pre-assembles everything
  deterministic — trigger, predicate text, evidence pins, condition-check results,
  the closed disposition set, freshness — into the sealed bundle. Live ledger reads
  and ambient repo reads are *forbidden inputs*. The lane's job narrows to "diagnosis
  prose, evidence-to-disposition mapping, and inconsistency flagging against a fixed
  output schema."
- **Evidence-only output:** `striatum://schema/adjudication-preparation-dossier` v1 —
  diagnosis, facts, unknowns, per-disposition evidence *for every lawful
  disposition*, never a preference. Dossiers admit as Evidence and "cannot close any
  gate." The target state's own words: **"dossiers inform, humans dispose."**
- **A named risk and its mitigation:** "laundered judgment — a persuasive-but-wrong
  dossier anchors rubber-stamping while the ledger looks lawful" — answered by
  dual-dossier cardinality (`exactly_two`: base + cross-family adversarial, identical
  sealed inputs) with disagreement as triage, plus the independent
  dossier-content-review gate before admission.
- **A cost rule that demands a cheap base model** (Principal constraint, 2026-07-09):
  "The base dossier routes to the cheapest capable backend; frontier spend is
  reserved for the adversarial second-dossier … A harness that burns frontier credits
  to prepare every dossier has failed this predicate."

So the question "can we tune a local model to act as the driver?" has a precise,
constitutional answer: **tune the local model to hold the base-role
dossier slot.** It is one-shot (fits `striatum-openai-lane` and the QLoRA recipe), it
requires zero new authority (Evidence plane), zero new ontology (a posture capability
declaration on a backend, like `local-qwen-ft`'s `review` today), and the aliasing
class already implies the tuned Qwen can *only* ever hold the base role
(`alibaba-qwen`; tuning creates no independence supply — the adversarial second
dossier must stay cross-family).

What stays out of any model's action space: RFC-grain and decision-record acceptance,
rejection-as-authority, override, naming — and the D0016 mechanical-acceptance seam,
which is reserved for the **deterministic Driver** ("an LLM judge at that seam was an
explicitly rejected alternative"). On acceptance surfaces, the model's lawful
contribution is the same dossier-prep, for the personal gate.

---

## 7. Remedy A — the control surface is already narrowing; ride it

1. **Deliver D0016 graduated acceptance (W1–W6)** before its activation entry lapses
   (**2026-08-21**). The three IR acceptance gates then close mechanically under the
   C4 condition set — deterministically, by the Driver, never a model. This removes
   the largest mechanical share of the judgment surface with no model at all. (Side
   effect worth naming: it also shrinks the future supply of human acceptance
   exemplars — the two remedies partially cannibalize each other, which argues for
   capturing corpus now.)
2. **Finish the stalls@N mechanization** (clauses 1–2 live wiring; the stalls@5
   plan-grain totality gap). Every stall class made mechanical is a decision no model
   ever sees — and it is the honest fix for the silent-wedge classes that today make
   operator polling load-bearing.
3. **Declare the tuned backend capable of the `adjudication-preparation` posture**
   (base role) once it passes the eval of §8. This is a backend.yaml capability
   declaration + scheduler routing, exactly like the `local-qwen-ft` review rollout —
   not a new pass, not a delivery.
4. **Add a proof-pinned issuer identity for any future model-issued verb** (the
   `authority_proof` / `delegation_ref` shape that planner-issuance and the
   harvest-issuance grant template already use), so nothing a model does is ever
   attributed as bare `$USER`.
5. **If/when the Principal wants autonomous resolution of a class:** name it
   explicitly in `policy/gates.yaml` (e.g. `bounds_exhausted` with a
   deterministic-failure signature and green gate evidence), with expiry and the
   retrospective queue, and rule explicitly on the weights-vs-"read individually"
   question. Until then: dossiers inform, humans dispose.

## 8. Remedy B — the dataset improvement is a registered target state

`judgments-become-a-corpus@1` already names the work (accepted, unrequested): a
**deterministic extractor over the ledger and object store** emitting instruct pairs —
escalations paired with resolution notes *with the input context reassembled exactly
as a dossier lane would receive it*; review ledgers labeled by downstream outcome
("the supervision signal no scraped corpus has"); acceptance adjudications with
condition-check reasoning — produced by a pass (P1, no hand authoring), byte-
reproducible, shipping a **class-distribution manifest** that declares the proceed
skew ("the laundered-judgment risk in training-data form, named at the source"), and
**staying on-box**. Advancing that target state *is* the dataset improvement, in the
compiler's own vocabulary. Concretely, layered on it:

1. **Train on what the lane will see** (the render.py house rule): prompts must be
   the posture's sealed `deterministic_inputs`, not transcript context and not live
   ledger reads (forbidden inputs). The corpus-driver transcripts remain useful as
   *auxiliary* evidence (what investigations preceded decisions) and for the
   intervention-trigger analysis (§3.1), not as prompt material.
2. **Synthesize lawful targets from the 297+ noted resolutions**: strip the
   recommendation, keep the diagnosis, expand to per-disposition evidence over the
   closed set — then hold every synthesized dossier to the dossier-content-review
   gate's own refusal classes (mechanically checkable: no preference language, no
   unauthorized disposition). The 14 existing lawful dossiers are the golden style
   references. This is the genuinely new dataset engineering; ~873 records feed it,
   but it is a transformation, not a relabeling.
3. **Eval like the machinery, not like fate-agreement.** Disposition-match is
   information-free at a 94% proceed prior. Gate instead on: (a) content-gate pass
   rate (no forbidden language, schema-valid); (b) mechanical citation verification
   (every cited seq/gate present in the sealed inputs and factually consistent);
   (c) retrospective adjudication match — re-dossier parked historical escalations
   and compare against the operator's recorded diagnosis (the target state's own
   existence-proof fixture); (d) disagreement rate vs the cross-family adversarial
   dossier in live dual-dossier runs.
4. **Split design:** time-ordered, eval strictly newer; grouped by escalation
   lineage / blocking scope (204/297 resolutions are on recurring scopes); a
   held-out-graph transfer eval (praxis: 39 resolutions + 30 acceptances) to catch
   striatum-next-vocabulary memorization.
5. **Locality:** obtain the Principal's explicit export direction before any RunPod
   run, or keep training on-box (which caps base-model size well below 35B on the
   3090) — the predicate leaves "what models train on it, and where" as backend-side
   facts, but the export itself needs the direction.
6. **Capture counterfactuals going forward** (when a disposition was nontrivial,
   record the rejected alternative and why) — otherwise DPO stays at review-DPO
   scale (~77 pairs). July produced ~300 authoritative judgment records; the pool
   grows fastest *before* D0016 delivery (see §7.1).

## 9. Recommended sequence

| step | what | cost/risk |
|---|---|---|
| 0 | Deliver D0016 loader before 2026-08-21; continue stalls@5 mechanization | in-repo work already accepted |
| 1 | Obtain the Principal's ruling on corpus export (or commit to on-box training); request `judgments-become-a-corpus@1` so the extractor is pass-produced and byte-reproducible | a compilation request + a ruling |
| 2 | Build the dossier-target synthesis (§8.2) + eval harness (§8.3) in striatum-tuner, against the delivered sealed schema | tooling work, no authority |
| 3 | QLoRA the 35B (or an on-box-feasible base if export is refused) on the proven recipe; gate on §8.3 | ~$25–45 on the existing RunPod contract if exported |
| 4 | Declare the tuned backend capable of `adjudication-preparation` (base role only — aliasing class bars the adversarial slot); route per the Principal's cheapest-capable rule; monitor via content-gate refusals + disagreement triage | backend.yaml + scheduler policy, like the local-qwen-ft rollout |
| 5 | Only after a Principal ruling + a named gates.yaml resolution class + proof-pinned issuer identity: consider autonomous resolution of that class. Separately: mine the corpus's loop-exit moments for an intervention-trigger signal as stalls@5 input | constitutional step, Principal's call |

The end-state this converges on is the one striatum-next's own trajectory implies:
the Driver stays deterministic, the mechanical judgment surface keeps shrinking by
delivery, a cheap local model drafts the evidence for every adjudication under a
contract that structurally cannot recommend, and the authority that remains is
exactly the part that was never automatable — deciding.

---

## Appendix A — key numbers

| quantity | value | source |
|---|---|---|
| driver sessions (modern-dialect / legacy-only) | 675 (433 / 242) | corpus-driver v2 |
| striatum calls (modern / legacy dialect) | 18,063 (10,484 / 7,579) | corpus-driver v2 |
| driver events / tool calls / striatum share | ~530k / 227,821 / 7.9% | corpus-driver v2 |
| modern read / advance / judgment call mix | 83.7 / 8.7 / 7.5 % | striatum_calls.jsonl v2 |
| ledger resolutions (all graphs / main) | 382 / 297 (294 noted) | ledger, recounted twice |
| main-graph dispositions | 278 proceed / 15 cancel_request / 4 reissue | ledger (verified) |
| escalation reasons (main) | 309 bounds_exhausted / 31 ambiguous_goal / 1 other | ledger (verified) |
| acceptance gate_results (all graphs) | 351 (245 accept / 106 reject) | ledger (verified) |
| unified adjudication pool vs review bar | 873 vs 882 train — but wrong output shape | ledger vs README.md |
| lawful-shape dossier records on ledger | 14 | `ledger cat` grep |
| resolution outcome labels | 204/297 re-escalated, 93 never | ledger join (verified) |
| acceptance fate labels | 41/183 later revised, 142 stood | analyze.py-style join |
| tuned 35B review model (deployed) | fate 0.5306 (98 rows) vs 0.1882 untuned (85 rows); 100% JSON | docs/results/qwen-27b-35b-training-report-2026-08-03.md |
| tuned 27B (not deployed) | fate 0.398 | eval-runs/ft-r1-nothink/summary.json |
| training cost envelope | ~$23 run, ≤$43.47 campaign (H200 QLoRA) | docs/results/… |
| local decision window before judgment | median 6 events / ~5 KB | events.jsonl join (v1) |

## Appendix B — pointers

- Corpus: `corpus-driver/{sessions,events,striatum_calls}.jsonl` + `stats.json`;
  extractor `extract_driver.py` (v2); rebuild ~7 min.
- Lane pipeline: `extract.py`, `make_sft.py`, `render.py`, `analyze.py`, `eval.py`;
  training `train/`, `jobs/qwen35b_moe/`; deployment `deploy/local-qwen-ft/`.
- striatum-next authorities: `catalog/review-postures/adjudication-preparation.yaml`
  and `catalog/gates/dossier-content-review.yaml` (the delivered, binding output
  contract), `catalog/target-states/escalations-arrive-dossiered.yaml` (incl. the
  2026-07-09 cheapest-capable-backend constraint and the laundered-judgment risk),
  `catalog/target-states/judgments-become-a-corpus.yaml` (the registered corpus
  predicate, on-box), `rfcs/0006` §Delegation (Agent Principal, named
  escalation-resolution classes), `rfcs/0016` + `decisions/D0016` (graduated
  acceptance; gates.yaml entry inert, expires 2026-08-21), `policy/gates.yaml`
  (harvest-issuance grant template, expired 2026-08-03), CLAUDE.md "No pre-scripted
  resolutions, ever", `docs/explanation/driver.md`, `internal/planner/dossier_test.go`
  (delivery proof).
- Exemplar adjudications with file:line pointers: archived in this session's workflow
  artifacts; representative pointers —
  `~/.claude-harm/projects/-home-halbritt-git-striatum-next/d4ccf78f-….jsonl:3225`
  (code-fix-coupled resolve), `…/4696ea0c-….jsonl:1939` (target-drift reject),
  `~/.claude/projects/-home-halbritt-git-striatum-next/e96fecbd-….jsonl:309`
  (delegated proxy accept with conditions enumerated).
- Operational note: the repo-pinned `bin/striatum` cannot read the live ledger
  (`schema_newer_than_reader`); use the PATH binary `~/.local/bin/striatum` for any
  extraction.
