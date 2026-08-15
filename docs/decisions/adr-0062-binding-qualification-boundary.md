---
id: adr-0062
artifact_type: architecture-decision-record
title: Binding-specific qualification boundary and tuner absorption
status: decided
decision_owner: primary-agent
decision_authority: adr-0026-and-repository-owner-build-task-2026-08-14
created: 2026-08-14
decided_at: 2026-08-14
supersedes:
  - striatum-tuner-independent-capability-authority
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-qualification
  - caplab-revbench
  - historical-striatum-tuner-custody
related_specs:
  - caplab-qualification-contract-v1
related_plans:
  - caplab-tuner-merge-build-task
---

# Binding-specific qualification boundary and tuner absorption

## Context and authority

The repository owner directed CAPLAB to absorb the useful parts of
`striatum-tuner`, retain CAPLAB as the product authority, establish an artifact
boundary for a future Quartermaster, and complete the build. ADR 0026 delegates
routine CAPLAB product decisions to the primary agent. The exact task is
preserved at [`caplab-tuner-merge-build-task.md`](../../caplab-tuner-merge-build-task.md).

Archaeology found reusable mutation, runner, result-materialization, and
analysis mechanics in `striatum-tuner`. It also found that the existing
revbench controls were selected by downstream `fate == final`, several defect
checks established only textual shape rather than their claimed semantic
invariant, and run identity omitted behavior-bearing subject dimensions.
Those runs remain potentially useful observations, but their current labels do
not independently authorize qualification.

No executable Striatum or `striatum-next` dependency on `striatum-tuner` was
found. Existing references are provenance strings and proposed policy
configuration, so a compatibility daemon or parallel runtime authority would
solve no observed dependency.

## Decision

CAPLAB is the sole product authority for the migrated capability evidence,
measurements, policies, and claims. `striatum-tuner` becomes historical custody
and provenance; it does not remain an independent qualification authority.

CAPLAB will implement two neighboring deep modules:

1. `caplab.qualification` owns exact Binding validation, immutable Measurement
   validation, versioned policy evaluation, append-only claim history, and
   deterministic export.
2. `caplab.revbench` owns deterministic preparation, the authorization boundary
   for benchmark execution, and mechanical offline scoring for the
   review-benchmark method. The initial executor supports sealed static local
   fixtures. It fails closed for real native providers until a provider bundle
   and durable streaming-custody adapter are specified and implemented.

The generic qualification module does not execute experiments, and revbench
does not own generic policy or claim history. This avoids both a premature
experiment framework and a revbench-shaped public qualification API while
keeping benchmark execution in CAPLAB as required by the product boundary.
Every supported execution effect requires a registered, exact, time-bounded
delegation. The reserved `live-native-provider` authorization class is not an
implemented execution path and cannot turn the fixture executor into one.
Version 1 preparation also refuses live-provider Bindings after first requiring
the canonical repository native-system contract. Its only accepted local
profile uses a repository-owned synthetic model, harness, provider, and version
namespace, plus registered executable bytes and pinned version-stream digests.
It cannot be relabeled as a canonical Codex or Claude subject.

ADR 0063 supersedes only the initial live-provider-refusal clause above. It
adds one exact Codex profile, apparatus receipt, and durable custody seam while
preserving this ADR's module, authority, fate-firewall, qualification, and
Quartermaster boundaries. The local-fixture behavior remains unchanged.

A Binding identifies the exact behavior-bearing native agent system and its
administration. A protocol and corpus identify the measurement context. A
change to either side prevents claim reuse: behavior-bearing changes create a
new Binding, while protocol, corpus, experiment, or policy changes create a new
Measurement or Claim.

The only initially qualifying evidence-basis kinds are a mechanically verified
oracle and a human-authorized judgment with an explicit authority reference.
Model judgments are recorded as their own evidence kind and may support an
advisory claim only under version 1. Downstream fate is stored only as a
covariate. The policy evaluator has no predicate that reads covariates. Every
decision metric also names its truth, case-selection, and derivation lineage;
fate-conditioned selection is advisory-only unless the capability distribution
is explicitly narrowed to that selected population.

Measurements and policies are immutable and separately content-identified.
Policy evaluation uses a small closed predicate vocabulary over exact integer
and rational metrics. A threshold miss is a valid negative result, not an
execution failure. `qualified` and `unqualified` are decisions and require an
exact, time-bounded `caplab-qualification-authorization/1` record that delegates
those statuses for the Binding, capability, and policy; otherwise the result is
`advisory` or `unmeasured`. Version 1 decision claims also require immutable,
registered model, route, harness, and configuration preimages. Mutable or
unknown-byte subjects remain advisory.

Claims use `caplab-qualification-claim/1`, apply to one exact Binding and
capability distribution, and form an append-only supersession graph. No claim
has a mutable `current` flag. Multiple unsuperseded heads remain visible;
CAPLAB does not choose a runtime-active claim.

The future Quartermaster boundary is the deterministic
`caplab-qualification-export/1` artifact plus public JSON Schemas. CAPLAB does
not call a Quartermaster database or implement binding inventory, enabled
state, reachability, health, quota, cost, preference, placement, or Dispatch.

## Considered alternatives

A single revbench application would keep its implementation cohesive but would
make the first experiment family own generic policy and claim semantics. A
four-module experiment framework would support hypothetical future families at
the cost of a registry and extension surface that current repository evidence
does not justify. A compatibility service would preserve two authorities
despite there being no live caller to serve. The selected two-module boundary
has the smallest stable public surface while keeping the experiment replaceable.

## Preservation, verification, and rollback

The pinned tracked tuner source tree and ancestry are retained under
`history/striatum-tuner/source/` as historical custody so Class B and C material
is not lost. This does not admit or register those bytes as CAPLAB evidence and
does not make the historical package an active runtime or CI root. Untracked
and ignored source-working-copy data remain untouched in their original
custody. Fate-derived summaries are classified as legacy nonqualifying
observations unless an authorized audit later establishes an independent truth
basis, exact Binding, complete provenance, and independent case-selection
lineage.

Verification requires deterministic known-defect scoring, fate-firewall,
binding-change, protocol-change, policy-threshold, supersession, schema/export,
and CAPLAB-independent consumer tests. Passing these checks is implementation
verification, not owner acceptance.

Rollback removes the new active modules and CLI while retaining this decision,
the migration manifest, source hashes, and untouched tuner custody. Reopen
before allowing another truth-basis kind to issue decisions, weakening exact
Binding identity, making claims mutable, adding runtime-registry state, or
changing the Quartermaster artifact boundary.

## Doctrine receipt

Design used advisory Pincite packet `pkt-ee7d99200d16c625` from validated
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, and release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Repository-owner direction and
ADR 0026, not doctrine, supply decision authority. Final implementation
observations and citation classification are recorded after integration.
