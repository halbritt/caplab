---
id: adr-0072
artifact_type: architecture-decision-record
title: Explicit application release for future enrolled pool launches
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-10-09
supersedes: []
---

# Pool explicit release

Under ADR0026 and the continuing shared-admission feature, select the existing
retrieval explicit-byte exec gate for future enrolled advisory pool launches.
ADR0068/0069's block-writer EOF cannot itself authorize the application after
supervisor exit. The protected outer still counts on creation; startup-gate
execution is a stage of that same outer, not a replacement native harness.

Mount the pinned gate read-only in the existing private `/dev` mount, invoke it with the pinned system interpreter,
and send exactly one release byte followed by the original stdin payload only
after permit, actual creation, namespace witness and current deadline checks.
For arg-mode applications, the original argv remains and stdin is EOF after
the gate consumes its byte. Refusal/crash before the byte cannot exec the native
command. Missing native completion or reuse-safe namespace closure still holds
accounting; gate EOF is not a manufactured death observation.

Identify this future administration as `pool-held-pid1-explicit-gate-v1` in its
enrollment and measurement environment. Pin gate/interpreter bytes in assigned
intent. Do not rewrite old enrollment, right, completion, measurement or SDK
events. Original `pool-held-pid1-v1` custody may be loaded only in recovery mode
with its exact original receipt, for reconciliation rather than new launches.
Future code refuses mixing administrations in the same custody domain. Preserve
native command/model/effort, declared account joins, budgets, assignments,
timeouts, exception causes/cleanup notes, interrupted-arm recovery and output
contracts. Unenrolled behavior and native Revbench/retrieval paths stay intact.

Authorize source/tests/docs in the existing isolated sole-author worktree,
provider-free genuine SDK and local bwrap/process controls with private homes,
and an offline wheel. Record a tested-commit selection before source integration
or installation. No production home writes, provider/model call, historical
campaign continuation, measurement registration or qualification acceptance is
selected. Stop and retain unexplained process/accounting/provenance outcomes;
repair demonstrated faults without weakening controls. Evidence archives are
not executable custody. Reopen for gate/runtime, OS topology, stdin semantics
or native subject changes. Remaining producers continue as separate work.

On startup failure, after forced group abort/held-init abort and monitor reap,
attempt bounded communicate with no release input to retain original raw
stdout/stderr and exit facts. Timeout/error annotates the primary failure;
incomplete streams are not complete scored output or namespace-closure proof.
