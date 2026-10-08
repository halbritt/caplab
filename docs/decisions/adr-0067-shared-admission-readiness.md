---
id: adr-0067
artifact_type: architecture-decision-record
title: Prospective shared-admission readiness and held PID1 proof
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-10-08
decided_at: 2026-10-08
supersedes: []
superseded_by: null
---

# Prospective shared-admission readiness and held PID1 proof

Caplab selects an additive Codex external-token administration for future
shared-admission runs: `codex-terra-max-revbench-live-external-token-readiness-v1`.
The exact registered policy adds invocation-owned Bubblewrap `--block-fd` and
`--info-fd` pipes. The two previous policy files stay byte-identical. Selection
requires whole registered policy equality. This behavior change requires a new
prospective Binding/apparatus/authorization, and never modifies an active run.
This decision authorizes construction and provider-free local-process tests;
it does not authorize a benchmark administration or qualification acceptance.

The existing supervisor retains its original launch intent, shared permit and
native authority. After creating the outer monitor it retains actual creation
before observer/control-plane work. The bounded info frame supplies a candidate
host PID; the supervisor validates the actual parent, boot, namespace depth and
PID1 identity around `pidfd_open`. It retains that exact descriptor before
writing the block-release byte. Observing and retaining readiness consumes the
original execution budgets. Expired authority never releases the application.
There is no new launch right, persistent observer, helper or admission ledger.

A malformed/lost frame, unavailable pidfd or expired barrier aborts startup
through the existing infrastructure-error cleanup: kill/reap the owned monitor
before releasing pipe resources. The positively created outer still counts one;
no terminal native completion or noncreation proof is invented. Recovery holds
uncertainty. Block-writer EOF also releases Bubblewrap, so the pipe is not a
crash-proof launch capability. A parent crash preserves the durable possible-
creation/permit state, uses existing death-on-parent containment, and cannot
produce a positive quiescence fact or authorize replay.

Settlement continues to require monitor completion and observed death of the
held namespace-init pidfd. Existing closure/2 sidecars and their lower-bound
rules remain. This administration allows at most 1000 ms of post-monitor pidfd
observation after execution has stopped. It grants no execution extension. Old
administrations retain their 50 ms observer capped by their native deadline.
Missing death evidence retains capacity. Actual UTC/monotonic brackets require
one boot and ordered readings; no event instant is fabricated.

## Source basis and rejected alternative

Bubblewrap v0.9.0 emits `child-pid` through `--info-fd` in the monitor after clone,
and reads `--block-fd` before application fork/exec. Its monitor can exit before
PID1 finishes. The pinned direct adapter and existing observed host kernel are
TCB dependencies, not independently authenticated hardware.
[Bubblewrap source](https://github.com/containers/bubblewrap/blob/v0.9.0/bubblewrap.c).

A pipe-only `--sync-fd` proposal was investigated but never committed or
installed. EOF is insufficient: Linux v6.8 calls `exit_files` before
`exit_notify`; namespace-init descendant teardown is inside that later path.
Thus EOF can precede complete namespace extinction. Passing simple-child tests
cannot establish the stronger tree claim. Root wait and numeric PID absence
are also insufficient. The selected readiness mechanism retains the existing
positive pidfd proof instead of broadening its meaning.
[Linux exit source](https://github.com/torvalds/linux/blob/v6.8/kernel/exit.c).
The host reports 6.8.0-146-generic; this source analysis does not attest Ubuntu's
entire built kernel to the upstream tag.

## Verification and preservation

Use genuine fast children, child-side exec failure, background descendants,
original-deadline timeout, malformed actual info bytes, OS pidfd refusal,
post-observation clock expiry, replay, descriptor cleanup, exact new-policy
selection and old-policy/native custody controls. No provider/model call or
operator credential is needed. Preserve assignment, one-shot custody, trial
bounds, native harness/model/effort, credential quarantine, active pins,
qualification and provenance. Other producers remain separate integrations;
this decision does not claim all Caplab paths are enrolled.

Reopen on adapter ABI/topology, subject, credential/authority or stronger proof
changes. Stop on contradictory source/runtime behavior or an unexplained
accounting result. Reversal selects a prior policy only for a new administration;
no historical accounting or custody evidence is erased.

## Doctrine receipt

Bounded construction review used `pkt-adf69929f1a2babe` (SHA256
`adf69929f1a2babef7d2c11d9a104bc9061821207bec734f733385c7175d63b2`), corpus
`corpus-2026-07-12-a11702cc9217` and doctrine `doctrine-f6bbb5196a3f8bf9`.
Typed repository, authority, source and real-process test evidence discharged
the selected material custody/authority/preservation obligations. The seven
actually used concept IDs were classified as valid packet citations. Generic
unused obligations do not establish all-producer integration or qualification.
