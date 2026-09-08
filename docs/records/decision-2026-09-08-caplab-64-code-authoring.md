# Prospective code-authoring procedure

Date: 2026-09-08. Decision owner and delegate: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

The active objective authorizes continued improvement of CAPLAB's measurement
quality. This bounded change may create
`docs/product/contracts/behavior-code-authoring-v1.md`, add its navigation link
to `docs/product/README.md`, and complete this decision record. It may use the
read-only CAPLAB-50, 52, 55, 64, 65, and 71 issue/comment snapshots as planning
context, retaining their source locators and hashes. It may create and verify
new synthetic arithmetic examples without model calls.

After verification, append a resolution to CAPLAB-64 and mark that
specification item Done; append the new parameter obligations to CAPLAB-71;
append a prospective correction of the equal-refusal identification claim to
CAPLAB-55. Preserve each original description, unrelated fields, and all
comments. Re-read before updating and stop that update on concurrent change.
These are planning projections of this record. No external comments or
messages are authorized.

Preserve existing study protocols, scenario/code artifacts, campaign evidence,
runtime code, frozen thresholds, and `docs/designs/`. No historical evidence
admission, rewriting, rescoring, live launch, model spend, reviewer ranking,
placement, or human-time commitment is authorized. This authorization expires
when this bounded change is committed. Remove only this task's temporary
doctrine working files after recording receipts; retain inspection and
verification receipts under `/tmp/caplab-64-*` and related issue snapshots.

Verification must cover every CAPLAB-64 requirement, source compatibility,
local document links, concrete failure cases, and exact Plane changes. A
written procedure does not verify an actual codebook, independent coding,
blinding, or instrument fitness. Stop and narrow any claim that would require
those unavailable observations.

## Decision and alternatives

Select a prospective procedure with explicit code derivation, distinct author
and application contexts, counterexamples, fixed scoring methods, custody,
and reporting gates. It applies only when a future study explicitly adopts
its version. Existing frozen studies are unchanged.

Leaving CAPLAB-64 as a list leaves the same operational choices to each author.
Building an automatic author or classifier now would add implementation before
the judgment contract is settled. The procedure is the selected deliverable;
execution and validation of a real codebook remain separate work.

The CAPLAB-55 planning comment's inference that equal refusal rates make a
conditional contrast approximately unbiased is superseded for prospective
adopters. Equal rates do not identify which attempts survived in each arm.
The existing symmetric attempt gate and missingness reporting remain; neither
now licenses a causal interpretation of selected attempts by itself.

## Verification

The new [procedure](../product/contracts/behavior-code-authoring-v1.md) was
audited against the live CAPLAB-64 description and the CAPLAB-50/52/55 comments
it depends on. These checks establish specification coverage, not empirical
fitness or independent acceptance of this author's work.

| CAPLAB-64 requirement | Procedure evidence and audit outcome |
|---|---|
| Author and context partition | Section 1 names author, validator, custodian and coder inputs/exclusions, bindings, prior exposure and access boundaries. Separate contexts do not assert independent errors. |
| Two-source derivation | Section 2 requires a decision-rule derivation and reference behavior anchor for B, with source commit/path/hash/custody. A disagreement flags the classification for review. |
| P single-source asymmetry | Sections 2–4 explicitly omit the positive reference anchor; a feasible positive P enactment must validate satisfiability, separately from correctness. |
| Materially different repair | Section 3 requires a concrete witness on the same parent, rejects cosmetic changes, and distinguishes a sketch from validation. |
| Negative space | Section 3 requires boundary witnesses and fixed resolutions for claims, vacuous tests, incomplete actions, and correct non-concept repairs. |
| Frozen mechanical/agent split | Section 4 pins the method, inputs, environment and errors. Boolean agent output is not a mechanical predicate. |
| Predicate and pairing validation | Section 4 tests B on parent/reference as false/true; P as false/false plus a mandatory true witness. Transcript conduct cannot be inferred from a static diff. |
| Tamper-evident freeze | Section 5 requires complete byte inventories, a protected digest and prior append-only witness; hash equality alone does not prove independent freeze timing. Amendments preserve old bytes. |
| Per-arm difficulty and withholding | Section 7 specifies base-rate and contrast comparisons, paired control handling, uncertainty containment, substantive comparability, and a fail-closed pooling rule. CAPLAB-71 must supply numeric values before freeze. |
| B-only reference audit | Section 2 flags missing reference conduct only for B. P negatives do not audit truth or independently prove semantic non-bearing. |

Additional challenge cases checked in the prose audit: always-false P
detector; reference-text matching; unavailable observations misread as false;
out-of-scope work dropped as refusal; partial code denominators inflated into
complete scores; pooled means hiding divergent contrasts; equal attempt rates
misread as causal identification. Each has an explicit rejection, retained
denominator, or interpretation boundary in the procedure.

Exact `fractions.Fraction` arithmetic verified the pooling example
`dB=1/4, dP=3/4, theta=1/2, g=1/2, h=-1/2` and the selection counterexample
(both attempt rates 1/2, observed code rates 0 and 1). Local document links
were checked for existence. Receipt: `/tmp/caplab-64-code-verification.json`.
No runtime code or tests changed; the runtime suite was not rerun for this
documentation-only change.

The selection counterexample is newly constructed, not historical evidence.
The direction of the correction is corroborated by the primary study
[Bell et al., BMJ 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC4688419/), whose
indexed text explicitly rejects equal dropout as a guarantee against bias.
Direct article opens encountered access challenges, so this record relies
only on that indexed claim and the separately checked local counterexample,
not on uninspected details of their simulations.

## Consequences and limits

The primary delegate selects this version as the CAPLAB-64 specification
deliverable and projects that item Done after these checks. CAPLAB-65, 66, 71,
and 84 remain responsible for their separate judgments, parameters, empirical
evidence, and integration. No real codebook has been created or validated in
this change. No classifier, freeze enforcement, or statistical interval
implementation is claimed.

The new procedure adds CAPLAB-71 obligations for the base-rate and contrast
tolerances, interval method and coverage/multiplicity choices, world pooling
gate, explicit code counts/weights, and arm/control mapping. A blank value
blocks adoption at freeze; it does not become a permissive default. Reopen
this procedure if a concrete witness reveals patch matching, an impossible
P-code, unverifiable author separation, an unsupported evidence surface, or a
reporting rule that permits a stronger claim than the observations support.

## Source receipts

Plane execution: CAPLAB-64 is Done with the specification resolution appended;
CAPLAB-71 retains its state with parameter obligations appended; CAPLAB-55
retains its Done state and original description/comment content with the
prospective correction appended. Exact submitted/returned descriptions and
unrelated product fields were checked against fresh reads. Receipts are
`/tmp/caplab-{64,71,55}-{before-code-update,after-code-update}.json` and their
`code-update.ndjson` / `code-update-result.json` siblings. No comments or
messages were sent. Doctrine citation consumption classified all five used
concepts as valid packet citations.

Plane changed CAPLAB-55's `completed_at` from
`2026-07-25T17:35:24.317706Z` during the description update. One bounded API
attempt to restore that exact field was ignored and again produced an update
time (`2026-09-08T15:09:34.579973Z`). No further retries or database mutation
were attempted. The original completion timestamp is preserved here and in
the before snapshot; the UI timestamp is an API side effect, not a new
completion or acceptance event. Restoration receipts:
`/tmp/caplab-55-completion-restore.ndjson`,
`/tmp/caplab-55-completion-restore-result.json`, and
`/tmp/caplab-55-after-completion-restore.json`. This is the sole observed
unrelated metadata preservation limitation.

Fresh roadmap list `/tmp/caplab-roadmap-after-64.json` contains 17 items in
open state groups after the update. The broader goal remains incomplete.

Baseline checkout: `7261bcf`. Root instructions and ADR 0026 govern the
change. The following read-only Plane snapshots retain complete source issue
and comment IDs, timestamps and original HTML. Their API records have no Git
source commit; these are planning-context receipts, not imported or admitted
study evidence.

| Read-only receipt | SHA-256 |
|---|---|
| `/tmp/caplab-64-code-current.json` | `84e497b7e45fbe02c521009a629a60a4e4a80eb518ff364031ecd5fe3789fc27` |
| `/tmp/caplab-50-code-comments.json` | `8b8e6747495538b18bc3857d766e2ffbfb436eb9dc5c13f0e6aa2091878a4839` |
| `/tmp/caplab-52-code-comments.json` | `2b54b13c5c8d7e2723c04ad8e9be4a4acd946b7ba69296adf68ea2679334f986` |
| `/tmp/caplab-55-code-comments.json` | `5fcb54d49b44ab6351d29182b4d77cadbed18dd2b17cd7dbad848ca0e9361877` |
| `/tmp/caplab-65-code-context.json` | `dfeeaa9c91b3fadc32f165edbb2843348125bdc20b21ac3de0370429ddee9106` |
| `/tmp/caplab-71-code-context.json` | `ea41479d0d746f559e3b41ea00151139c0dd86cdcb00b791e7172a899000e717` |

The corrected inference occurs in CAPLAB-55 comment
`d10d285b-7339-423a-9323-e86c4e704650` (2026-07-25). The B/P asymmetry and
pooling requirement occur in CAPLAB-52 amendment
`82d73c4a-760b-4d66-8eef-1f689b77866a`; its later comment
`9b5f903f-df2a-4f9d-9f83-aa7e28a68d2c` leaves world generalization subject to
remeasurement and a homogeneity check. This procedure does not silently
choose a random-world model or revive the old campaign.

## Advisory receipt

Release retrieval gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-2ecde60231ba25c2`, content SHA-256
`2ecde60231ba25c2894814ac4dc12fd8af1e2f762158eed7dd807efb74d75115`, uses corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts:
`universal-repository-contract-precedence`,
`universal-evidence-before-intervention`, `universal-explicit-invariants`,
`performance-metric-semantics`, and `agent-conduct-authority-bounded-action`.
They support explicit evidence and reporting boundaries; they do not supply
CAPLAB authority or statistical validation.

Two evidence-gathering passes covered the material specification and authority
obligations. Remaining advisory requirements are nonmaterial to this bounded
deliverable for the reasons below; several remain material to a future live
study, for which no readiness claim is made.

| Concept | Missing requirements | Nonmaterial-to-this-deliverable reason |
|---|---|---|
| performance-measurable-objective | accepted workload and operation boundary; authority to inspect the target and identify the objective owner; environment, input distribution and scale, concurrency, and success/failure population; latency percentile, throughput, CPU, memory, I/O, network, cost, or other metric with a target; owner for the objective and any quality tradeoff | No performance optimization or accepted workload/target is proposed. |
| performance-memory-lifecycle | allocation and in-use/retention evidence; owner/reference/lifetime path; precise memory metric and interval; representative macro memory behavior | No memory or resource-use claim is made. |
| performance-metric-semantics | access to instrumentation definition or benchmark harness; instrumentation overhead and data-loss limits; sanity check against actual runtime behavior | The instrument interface is specified; actual harness behavior, overhead and loss remain unverified and block campaign readiness, not this specification deliverable. |
| performance-profile-causal-bottleneck | direct versus cumulative contribution and concurrency boundary analysis; profile type and sampling/granularity semantics; representative workload, version, and profile interval; reproducibility or independent corroboration | No resource bottleneck or profile-derived intervention is proposed. |
| task:repository-assessment | evidence-co-change; evidence-generated-artifacts; evidence-static-source-structure; evidence-tests; evidence-version-history | This is a prospective contract assessment, not a code, history, generated-artifact or empirical performance assessment. |
| universal-information-hiding | actual caller needs; caller needs and decision owner; decision owner and volatility; leaked knowledge or coordinated change; material cost/failure semantics callers require | Role access boundaries are specified without asserting an implemented module boundary or caller-cost improvement. |
| universal-local-reasoning | knowledge and navigation required by callers/maintainers; representative change or use scenario; representative change scenario; state, invariant, and dependency ownership | The procedure gathers required authoring decisions; no maintenance-cost or change-locality improvement was measured. |
| universal-no-change-option | actual current cost/risk or absence within a stated interval; intervention cost and uncertainty; latent security, safety, data, durability, and compatibility check; proc-decide-leave-code-alone | The explicit uncompleted specification requirement motivates this document; no system-wide latent-risk or intervention-cost audit is claimed. |
| universal-preserve-behavior-by-default | proc-establish-preservation-boundaries | Named documentation and projection changes preserve runtime and study bytes; no runtime preservation procedure is needed for code that did not change. |
| universal-repository-contract-precedence | accepted ADR, RFC, API, compatibility, generation, build, and test contracts; current source, configuration, and relevant runtime state | Authority and relevant planning sources were read; the broader API, generation, build and runtime corpus is outside this documentation change. |
