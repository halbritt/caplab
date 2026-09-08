# Behavioral code authoring, version 1

Status: prospective procedure, selected by the primary agent under
[the CAPLAB-64 decision](../../records/decision-2026-09-08-caplab-64-code-authoring.md).
A study must explicitly adopt this version before using it. This document does
not amend frozen codebooks or establish that any existing instrument passed.

## Purpose and claim

Write binary codes that detect a concept's observable conduct without requiring
the reference author's exact repair. A **B-code** detects conduct specified by
the bearing concept: the concept selected as relevant to the defect. A
**P-code** detects conduct specified by the non-bearing placebo concept.
P-code satisfaction can represent distraction or harmful scope expansion.
It is not a favorable quality judgment.

Code uptake answers whether conduct exhibits the frozen definition. Report
repair correctness, scope violations, review false alarms, cost, and actual
downstream value separately where independently measured. A concept-shaped
repair need not be correct; a correct alternative need not exhibit that
concept. Neither agreement among coders nor matching a reference establishes
reviewer capability or justifies placement.

This procedure specifies instrument definition and its handoff to application.
CAPLAB-65 owns the coding roster, accuracy anchor, and single-code failure
disposition; CAPLAB-66 owns blinding validation; CAPLAB-71 owns numerical
parameters; CAPLAB-84 owns shakedown integration. None is discharged here.

## 1. Assign roles and partition context

Before authoring, record the responsible people or exact agent bindings, their
roles, input inventories, and prior exposure. Authorization to spend a model
call or a person's time must exist separately. Do not describe a second pass
by the same author as independent validation.

| Role | Permitted context | Excluded context |
|---|---|---|
| Task author | Defect report, parent environment, task constraints under the study's task-authoring contract | Retrieval keywords or routing fields when that contract requires blind task authoring; future subject outputs |
| Code author | Frozen task and acceptance contract, parent and reference repair, selected B/P concept decision rules, pairing rationale | Study subject outputs, arm results, model rankings; retrieval metadata beyond the nominated rule |
| Code validator | Same definition inputs plus proposed codes and witness artifacts | Study subject outputs or outcome summaries used to tune the instrument |
| Custodian | Raw capture, assignments, mappings, codebook identities, access records | No right to change judgments or code definitions through custody operations |
| Application coder | Opaque episode ID, frozen code text and negative space, the complete authorized and validated blinded evidence surface, arm-invariant context named at freeze | Reference repair, author labels and witness answers, B/P source map, arm assignment, model identity, prior judgments or outcomes |

Code author and application coder must have separate contexts. Merely starting
a fresh chat does not establish independent errors or cure exposure through
files, memory, shared instructions, or accessible workspaces. Record the
enforced access boundary and any unavoidable exposure. Unverified boundaries
block a blinded-coding claim. When a transcript is required, stripping packet
text alone does not establish blinding; see the
[redaction counterexamples](../../records/inspection-2026-09-08-caplab-66-redaction-feasibility.md).

## 2. Assemble one derivation record per code

The author writes each record before study subject outputs exist. For a reused
world, disclose previous exposure and follow an explicit reuse decision;
do not backdate a freeze. Use stable code IDs and include all of these fields:

| Field | Required content |
|---|---|
| Identity | Procedure version, study/world ID, B or P family, code ID/version, author identity and date |
| Construct | One observable behavioral proposition; why it follows from the nominated decision rule; claim exclusions |
| Source | Source repository/release commit, original path, content SHA-256, decision-rule section or byte/line span, and custody locator; separately identify an external source with no Git commit |
| Reference anchor | For B: parent and reference tree identities, diff hash, relevant path/hunk and behavior demonstrated. For P: explicitly `not applicable: single-source`, with the pairing validation below |
| Positive rule | Necessary and sufficient observations for a true judgment, including which artifact or event surface carries them |
| Negative space | Explicit exclusions and boundary resolutions, including misleading evidence that is insufficient |
| Satisfiability | A materially different witness from the reference repair; artifact locator/hash, explanation of the behavioral difference, and validation result |
| Scoring | Mechanical or agent/human, input boundary, implementation or coder protocol version, true/false/unavailable conditions |
| Audit | Witness matrix, observed results and failures, validator identity, unresolved disagreements and disposition |

For B-codes, the decision rule and reference anchor must independently support
the proposition. Naming a concept beside a hunk is insufficient. If the rule
requires conduct the reference lacks, flag the reference classification for
separate review. Do not alter a historical label or invent an anchor.

For P-codes, derive the proposition only from the placebo rule. Do not demand
a positive reference anchor: that contradicts the non-bearing pairing. A
positive P witness shows that the code can fire on feasible conduct in this
world. It may be an unnecessary change or an incorrect attempted repair;
record correctness and scope separately. A sketch alone is a proposed witness,
not a validated one. If permissions or the world make the behavior impossible,
reject the code or pairing before freeze.

## 3. Challenge patch matching and define negative space

Construct a materially different witness on the same parent. For B it must
satisfy the code through a different implementation approach while meeting the
task's acceptance contract. Renaming symbols, moving the same patch, changing
formatting, or copying the reference into a wrapper is not an alternative.
For P, construct an explicit enactment of the irrelevant concept and document
why it still fits the attempt and permission boundaries. The reference repair
is already a P-negative, so the positive witness must change its conduct.

The validator checks the witness against the written rule without using
reference similarity as the criterion. Record exact inputs, observations,
commands where applicable, and failures. Agent judgments remain judgments;
task tests support only the behaviors they exercise. An independent accuracy
anchor is a separate requirement.

Include at least one boundary witness for each material ambiguity. Examples
include documentation claiming an action without the action, a test that
asserts a constant, a tool invocation with no successful completion, a renamed
but unchanged mechanism, and a correct repair that lacks this particular
concept's conduct. Resolve each in the code text before freeze. A coder must
not infer "verified" merely from reading a file or running a linter when the
rule requires checking behavior.

Prefer artifacts when they expose the construct. Use a transcript only when
the required conduct cannot be inferred from the artifact, and name exactly
which event evidence suffices. An unavailable event stream does not prove the
conduct was absent. Do not make a portability problem disappear by treating
different harness event types as interchangeable.

## 4. Validate the scoring method and B/P pairing together

Freeze the method for every code before any study output is scored. Mechanical
predicates require a pinned implementation, environment, inputs, exit/error
semantics, and retained execution evidence. A parser failure, timeout, missing
file, or unsupported event is **unavailable**, never false. Agent/human codes
require the same witness matrix, recorded judgments, and the separate
CAPLAB-65 reliability/accuracy gates. Calling a judgment mechanical because
its output is Boolean is prohibited.

| Witness | B-code expectation | P-code expectation |
|---|---|---|
| Parent, represented as a no-change candidate | False | False |
| Reference repair | True | False |
| Materially different B repair | True for the code it witnesses | Observe all P-codes; a positive requires pairing review |
| Explicit P enactment | Observe; no automatic B expectation | True for the code it witnesses |
| Mere claim, imitation, or vacuous evidence that the rule excludes | False for the challenged code | False for the challenged code |
| Missing required observation or predicate failure | Unavailable | Unavailable |

The parent row is a **definition check**, not a scored study attempt; the
no-write-set gate in section 6 remains in force during application. For an
artifact predicate, provide the same input representation for parent,
reference, and alternatives. For action-sequence codes, a static reference diff
cannot establish that a process occurred. Require independently authorized
reference action evidence or leave that code unvalidated; never manufacture
a reference transcript.

Run every P-code on the parent and reference. A positive fails the proposed
pairing. Inspect whether the concept actually bears or the detector is broad;
revise the code/pairing and rerun the entire matrix before freeze. All-negative
results establish only those negative witnesses. The explicit positive
witness is mandatory to rule out an always-false detector. Broader semantic
non-bearing judgment remains distinct from this mechanical check.

Example definition audit (illustrative, not an admitted scenario): B detects
that failure is returned to the caller. The parent logs and returns success;
the reference returns a wrapped error; an alternative returns a typed failure
result while preserving the task contract. A comment saying "propagate error"
without changing the success return is a negative. P detects an irrelevant
cache addition: parent and reference are negative, a concrete cache addition
is positive, and merely adding a cache-themed comment is negative. Judge each
repair's correctness separately. A text search for "error" or "cache" would
fail this matrix even if it matched the reference or the concept title.

## 5. Witness the freeze

The custodian seals a manifest that enumerates every code and its method,
source/pairing map, parent/reference/alternative identities, witness results,
task and acceptance contract, scorer configuration, coder-visible schema,
redaction version, missingness rules, code aggregation and weights, and the
applicable parameter table. Include byte lengths and SHA-256 hashes for every
file, a manifest version, author/validator identities, date, and decision
locator. No required value may be blank. State the code count in each family
explicitly; do not silently double the study's intended 2–4-code scope by
assuming that limit applies independently to both families.

Store the sealed manifest and validation receipts outside the subject and
application coder's writable surfaces. Record its digest in an owner-controlled
append-only record before the first study subject output. A local timestamp
or a hash kept beside editable files is not an independent timing witness.
If independent freeze order cannot be established, report that limitation and
withhold the prospective-freeze claim.

Before each launch and scoring batch, verify all referenced bytes against that
manifest. Stop on mismatch or missing entries. Amendments create new versions
with reasons, authority, and affected slots named; retain previous bytes and
results. No silent code removal, altered predicate, method switch, or relabeling
of a failed validation. A changed instrument requires a new analysis boundary;
do not blend versions to rescue an estimate.

This is a required custody procedure, not a claim that the current runtime
implements a codebook seal. CAPLAB-84 must verify implementation and recovery
before an adopting campaign launches.

## 6. Preserve attempt denominators and interpretation limits

Apply the same attempt rule in every arm: any non-empty write-set is an
attempt, including an entirely out-of-scope edit or an unsuccessful repair.
Score observable codes for those attempts; retain correctness and scope as
separate observations. No write-set consumes the assigned slot with all conduct
codes unavailable. Do not replace it until a compliant attempt appears.
Infrastructure disposition and its bounded replacement policy remain distinct.

For every world and arm, report assigned slots, launches, attempts, no-attempts,
capture failures, unavailable codes, and scored code denominators. Do not
renormalize a partial code set into a complete episode score or convert an
unavailable code to zero. Freeze aggregation and missingness handling before
data exist; an undefined or failed reliability statistic is not a pass.

Use the [usable-sample accounting contract](usable-sample-budget-v1.md) when
translating those denominators into a sample-size or capacity plan. Required
usable observations, scheduled slots, and observed usable counts are distinct;
loss compensation does not create statistical information. CAPLAB-71 must
freeze the loss-rate interpretation, per-cell targets, and shortfall disposition.

Attempt-conditioned code differences describe the observed attempts. Equal
attempt rates do not establish equal composition or an unbiased treatment
effect. A simple counterexample uses two equally common latent types. In
control only type L attempts; under treatment only type H attempts. Both arms
have attempt rate 1/2. Among attempts L always exhibits code 0 and H code 1,
with no within-type change in conduct when attempting. The observed difference
is 1 solely because the types selected into observation differ. This example
does not assign an observed conduct value to a refusal.

Thus the refusal imbalance threshold is a stop diagnostic, not proof of
identification when it passes. A causal claim requires a separately frozen
estimand and justified assumptions or sensitivity analysis for selection.
Balanced rates alone cannot supply them. This prospective correction is also
consistent with the equal-dropout counterexamples in
[Bell et al. (2013)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4688419/);
the CAPLAB example and application are our inference, not a validation study
reported by those authors.

## 7. Check difficulty before pooling

Let T denote bearing-concept treatment, P placebo-concept treatment, and C
the matched control specified by the adopting study. Define B and P episode
fractions over their respective frozen code sets. The served-code contrasts
are `dB = mean(B_T) - mean(B_C)` and
`dP = mean(P_P) - mean(P_C)`. The proposed served-content summary is
`theta = (dB + dP) / 2`; it measures uptake, not benefit. For designs with
retrieval, injection, sham, and none arms, the study must explicitly map each
comparison and its control before applying these definitions. No arms are
silently combined by this procedure.

The analyst follows these steps only after the frozen coding and blinding
gates, without changing codes in response to the arm labels:

1. Report per-code and per-world control base rates, each arm's code fractions,
   and their unavailable denominators. State floor/ceiling limitations. Show
   `g = mean(B_C) - mean(P_C)` as the within-control difficulty diagnostic;
   reference validation alone supplies no empirical difficulty estimate.
2. Estimate dB, dP, and `h = dB - dP` by world with the frozen uncertainty
   method. Preserve pairing of the two scores on each control episode and
   cluster multiple codes from an episode; code count is not sample size.
   Use the study's explicit world sampling/weighting model. A fraction in
   [0,1] does not by itself make different code sets exchangeable.
3. Compare uncertainty intervals for g and h against prospectively justified
   tolerances `delta_base` and `delta_contrast`. Pooling requires the entire
   intervals to lie inside their respective closed tolerance bands around
   zero for every world included in the proposed pooled claim. The interval
   method, confidence level, treatment of multiplicity, and tolerances must be
   selected in CAPLAB-71 before outputs exist. Failure to reject a difference
   is insufficient; wide or unavailable intervals withhold pooling.
4. Also require a substantive common interpretation for both code families
   and the frozen per-world effect-homogeneity check for any cross-world
   summary. Similar base rates alone do not establish a common construct.
   A materially divergent world, missing gate, unresolved selection claim, or
   insufficient precision keeps theta withheld. Report dB and dP separately,
   with their conditional scope and intervals, and identify the failed gate.

Always retain the separate contrasts even when pooling is eligible. Do not
drop difficult worlds, choose tolerances from observed differences, subtract
placebo uptake from correctness, or change weights to obtain a pooled number.
The gates constrain interpretation; they do not license tuning an instrument
against study outcomes. Shakedown validation episodes stay outside the study's
analysis population, and they do not authorize an unplanned variance pilot.

Worked arithmetic check: control B = 1/2 and P = 0, treatment B = 3/4,
placebo P = 3/4 gives dB = 1/4, dP = 3/4, theta = 1/2, g = 1/2,
and h = -1/2. The headline 1/2 conceals quite different contrasts. With no
frozen tolerances or uncertainty method, this input must produce separate
contrasts and `pooling withheld`, regardless of the attractive theta.

## 8. Release the codebook only after its audit

The release record maps each code to its derivation, witnesses, validation,
method, and frozen bytes. It names the application coder context, records the
freeze witness and outstanding accuracy/blinding requirements, and includes
the parameter table. An unresolved requirement yields **not ready**, with its
reason. Codebook readiness is not study execution, study acceptance, or a
reviewer recommendation.

CAPLAB-64 owns the specification deliverable. An actual adopting codebook is
complete only after its own records and
observations meet these requirements. Do not use the planning item's Done
state as evidence that a codebook or campaign is ready.
