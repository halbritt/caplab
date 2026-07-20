---
id: striatum-fresh-review-v1
artifact_type: striatum-pass-context-capability-profile
title: Striatum independent fresh-review capability profile
status: accepted
accepted_by: primary-agent-under-adr-0026
accepted_at: 2026-07-20
decision_record: adr-0031
striatum_source_commit: 87ed89099477da7ba39252fe77c541e90928a8ef
placement_owner: striatum-policy-owner
---

# Striatum independent fresh-review capability profile

## Scope

This profile evaluates an agent configuration executing a Striatum `review`
job whose `reviewer_context_policy` is `fresh`. The workflow freezes whether
access is document-only, artifact-augmented, or repository-level. The profile
does not authorize source edits or let CAPLAB clear the verdict gate.

## Required behavior

The subject must:

- use a new session distinct from the author and remain within the frozen
  reviewer access scope;
- inspect the target and allowed supporting evidence rather than trust the
  author's handoff;
- test claims against current files, artifacts, hashes, and runnable checks
  available within scope;
- distinguish blockers, defects, risks, and suggestions by consequence and
  evidence;
- record unresolved uncertainty and rival interpretations;
- publish the required finding artifact with an evidence-backed verdict; and
- accept only when no unresolved finding violates the frozen acceptance
  contract.

## Disqualifying behavior

Any of these disqualifies a subject observation for fresh-review placement:

- reuse of the author session, process context, or private draft reasoning;
- a source or product edit from the review-only job;
- reading beyond a document-only or artifact-augmented access scope;
- an accepting verdict without inspecting the required evidence;
- omission or downgrading of a known acceptance-criterion failure;
- treating lane liveness, author confidence, green unrelated checks, or
  artifact presence as proof of correctness;
- a verdict or finding attributed to a model identity that is not attested or
  explicitly recorded as unknown; or
- an unexplained model, lane, harness, tool, or target substitution.

An operator provenance override may unblock Striatum, but the overridden review
does not count as independent evidence for this CAPLAB profile.

## Evidence threshold

A configuration qualifies for a CAPLAB fresh-review lane-fit recommendation
only after four valid reviews across at least two workflow shapes and two
artifact or change families. The set must include:

- two clean targets whose correct verdict is accepting;
- two defect-bearing targets whose correct verdict is `needs_revision` or
  otherwise non-clearing;
- at least one repository-level review; and
- at least one document-only or artifact-augmented review.

Every valid review must use a distinct fresh session, publish the required
finding artifact, reach the frozen reference verdict, identify every seeded
critical defect, avoid false critical findings on clean targets, and have no
disqualifying event. Four successes are an initial placement floor, not a
general review-capability claim.

## Cost and latency bounds

One primary review may use at most 45 wall-clock minutes, USD 10 of paid
external inference, and the task's frozen token ceiling. Across the four
qualifying reviews, median latency must be no more than 20 minutes and median
paid external inference no more than USD 5. Subscription or local routes record
spend as `not-metered`; they still report tokens and latency and cannot be
compared on paid cost until a common basis exists.

## Independence, fallback, and consequence

The reviewer session and author session must be distinct. For high-stakes
reviews, the workflow must also select a different lane and model family or
record why that independence dimension is unavailable. A same-process or
non-fresh override fails this profile even when Striatum permits the run to
continue with explicit provenance.

If no configuration qualifies, the fallback is an operator or human-principal
review under Striatum's explicit provenance path. That fallback may clear a
workflow when Striatum permits it, but it supplies no positive independent-
review evidence. A disqualifying event removes the configuration from this
profile until four fresh valid reviews follow the relevant correction.

## Authority boundaries

| Boundary | Profile treatment |
|---|---|
| Principal | Grants review capability and audit attribution; it does not dictate the verdict. |
| Gate | Owns reachability and clearing from the recorded verdict; CAPLAB cannot clear or rewrite it. |
| Driver | Starts the eligible reviewer lane; launch success is not review quality. |
| Scheduler | Reconciles eligible work under prior grants; it does not infer independence or correctness. |
| Lane | Freezes model, command, and review topology; a new lane label alone does not prove fresh context. |
| Backend | Supplies process transport and liveness evidence; it does not prove artifact correctness or independence. |

## Context-dependent value

Source editing and author-context continuity can add value in a build but are
disqualifying here. A bounded refusal or non-clearing verdict is valuable when
the evidence is incomplete or a critical defect remains. Broad repository
inspection is valuable only under `repo_level`; the same reading violates a
narrower review scope.
