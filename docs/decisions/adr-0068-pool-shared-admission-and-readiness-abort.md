---
id: adr-0068
artifact_type: architecture-decision-record
title: Prospective advisory pool shared admission and fail-closed readiness abort
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-10-08
supersedes: []
---

# Prospective advisory pool shared admission and fail-closed readiness abort

Caplab selects an additive, explicitly enrolled advisory pool administration.
Each frozen run specification and case/arm/replicate names one exclusive native
launch right. The owner-controlled nonrollback `shared-launches` custody retains
its domain, enrollment, intent, possible creation, actual creation brackets,
streams and completion. It is evidence custody, not another admission ledger.
The existing Quartermaster home alone reserves and settles shared resources.
Revbench retains its genuine capture type; both native adapters reuse the same
internal admission lifecycle, interval evidence, transport and reconciliation.

Enrollment verifies the catalog's native command/model/effort and configured
profile against the actual declaration and the canonical native-agent-systems
contract. A configured account/profile association is not authenticated account
identity. This slice neither infers accounts from tokens nor invents provider
window mappings. New containment is a new measurement environment; historical
runs, declarations, assigned native rights and qualification are not rewritten.

The prospective pool administration adds Bubblewrap's PID namespace, network
sharing, new session and block/info handshake to its existing filesystem mounts.
It holds the exact PID1 pidfd before releasing the native application. Admission,
readiness and transport latency consume the existing per-invocation timeout and
explicit UTC administration expiry. The shared permit has no execution power.
Every positive outer creation counts once, including a child-side exec failure.
A `Popen` exception is unresolved, not positive noncreation. A closed native
right that stops before calling `Popen` can truthfully return unused capacity.
Replay never invokes: it reconciles retained preimages or refuses the same slot.

## Refusal-path correction to ADR0067

Root and independent-review evidence demonstrates that SIGTERM can reap the
outer monitor while its blocked PID1 remains alive. Closing the block writer
then releases the application without `release()`. Reaping alone is therefore
insufficient abort cleanup. Before EOF on an unreleased barrier, kill and
positively observe death through the held PID1 pidfd. Native Revbench also uses
forced process-group termination on its unreleased startup error path, before
closing that descriptor. It does not change ordinary post-release grace policy.

If PID1 was not positively observed, or its descriptor is unavailable, abort
reports `ProcessProofUnavailable` and retains the block writer rather than
silently releasing it. Those descriptors remain owned by that process until
explicit disposition/process exit; finite admission limits bound additional
possible launches. No missing observation becomes quiescence or noncreation.
This is a deliberate negative-path cleanup contract change. Tests must assert
the retained-descriptor refusal, not suppress it as successful cleanup.

This barrier still is not a crash-proof single-use capability: OS exit closes
file descriptors. Abrupt supervisor/monitor crash and external signals require
separate native evidence; this decision does not claim universal crash closure.
The accounting remains held on missing facts. Do not infer physical noncreation
or provider-safe qualification from a retained shared hold.

## Scope and execution authorization

Under ADR0026 and the continuing integration feature, authorize this source
candidate, private synthetic homes and provider-free local process tests, public
configuration/documentation and wheel construction. Preserve existing active
campaigns and real credentials. No benchmark, provider call, production shared
home effect, measurement registration or qualification acceptance is selected.
Source integration/install may be selected separately from native administration;
independent review supplies evidence and is not a Quartermaster authority gate.

Preference/review-dissent preflight and trials, retrieval CommandAdapter,
artifact-rater helpers/roots, legacy advisory executor, sweep supervisors and
probe helpers remain separate producer integrations. No coverage is inferred
from this wrapper. Historical arithmetic experiments remain historical.

Reopen for ABI/kernel topology, command/credential/account, containment,
assignment/retry or stronger crash-proof claims. Stop on unexplained accounting,
cleanup or provenance results. Retain failed receipts; do not weaken the oracle.
