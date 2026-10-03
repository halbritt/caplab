---
artifact_type: decision-record
status: selected-for-construction
decision_owner: root252-primary-agent
decision_authority: adr-0026-and-owner-shared-backend-implementation-goal
implementer: agent-253
created: 2026-10-03
supplements: decision-2026-10-03-revbench-external-token-administration.md
source_record: quartermaster docs/evidence/caplab-namespace-selection-2026-10-03/selected-construction-decision.md
source_record_sha256: 29f845bb2f2a55297db99385fae74835122f97aa228dea5505594b21b6d3203f
independent_review: quartermaster docs/evidence/caplab-namespace-selection-2026-10-03/independent-review-sol262.md
independent_review_sha256: 95dc4a997336078b414bb07005ccd6a9b5345c51c156a86494679e9b688e1709
---

<!-- The text below this line is the selected record, byte for byte (SHA-256 above). -->

# Prospective direct Bubblewrap bundle selection

Decision owner: root252 primary agent. Authority: Caplab ADR0026 and the owner's
shared-backend implementation/deployment mandate. Selected 2026-10-03 for
construction and independent review, not live administration.

## Decision and relationship to the earlier selection

For the new external-token Revbench profile only, select a new bundle that
executes the root-controlled `/usr/bin/bwrap` directly under its existing
application-specific host permission. Pin that exact executable, its ELF
interpreter, complete dynamic library resolution and relevant loader inputs,
and the changed normalized outer argv/environment. Do not add an AppArmor
grant, launch through a generally usable privileged loader, disable a sysctl,
install host packages, or silently use whichever host version is present.

This named decision reopens the preserved-adapter-member restriction of the
2026-10-03 external-token construction decision (Caplab9a23275). It changes only
the new bundle's outer adapter/interpreter/library execution path and its exact
identity checks. Its original fixed Codex0.147 executable, Terra/max subject,
external credential API/v2 marker policy, private anchors, deadline, one-shot
custody, read-only mount, subject tools and declared live network boundary
remain selected. V1 policy and all historical member/Binding/manifest/apparatus
bytes stay unchanged and addressable. New bundle, runtime, command, Binding and
clean-source apparatus identities must be prepared. No qualification transfers.

Exact observed adapter SHA256:
`e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71`.
The implementation must retain fresh exact byte counts, paths, hashes and
resolved link/ancestor metadata for the interpreter and full library closure
using bounded public static inspection. It must identify loader cache,
preload, search-path and hardware-capability selection inputs that can alter
resolution; pin and validate them or explicitly close those resolution paths.
Do not assert complete closure from the adapter hash alone. If this cannot be
made concrete without changing this decision, report that precise remaining
choice and continue the independent credential seam.

## Trust and lifecycle

Root-owned executable/library files, resolution inputs and their effective
ancestors must not be writable by the runner or unrelated non-root principals.
Expected distribution symlinks may be used only with explicit pinned resolution
and protected ancestors; a blanket no-symlink rule would reject legitimate
system paths. Validate exact identity and relevant metadata immediately before
each launch and refuse missing, changed, writable or ambiguous dependencies.
An observed host package update requires a separately prepared/reviewed bundle,
not automatic re-pinning or fallback.

Direct normal ELF loading cannot provide an atomic descriptor snapshot of all
host dependencies against a concurrent privileged package update. Root selects
the explicit host-owner trust assumption: privileged host maintainers do not
change this closure during an authorized administration. Retain evidence of the
prelaunch checks and detected drift, and document this assumption in apparatus
and the contract. Do not claim resistance to a malicious root or atomic proof
of unobserved privileged changes. This selection authorizes no update to global
package services or their configuration.

Runtime consumers read/check protected host closure; they never write, publish,
overwrite or delete it. Invocation-owned temporary files/descriptors keep
per-call cleanup. No reusable mutable staging directory or new stage installer
is required. Existing owner-only temporary staging is not world-writable merely
because its parent is `/tmp`.

## Evidence, limitations and review

Sonnet253's two original non-Codex controls used identical launcher bytes and
contained argv: direct system path succeeded with an empty root and loopback
only; its copied path failed at RTM_NEWADDR. Sol262 verified all13 original
manifest entries and stream receipts. This supports path-attached AppArmor as
the leading explanation, not an observed failed-process label or a census of
all exemptions. The predicted nonzero post-Bubblewrap capabilities did not
occur; successful control actually had zero effective capabilities.

Sol's R1 broad loader-grant and R2 shared-staging concerns are resolved by
selecting neither proposed mechanism. R3/R4/R5 factual, identity and inference
corrections are incorporated above. Independent review remains necessary for
the actual new bundle, protected resolution, drift failures and runtime code.
The controls prove neither this new implementation nor Codex external-mode
parsing/provider access. Native verification is a later declared bounded task;
no previous failed case is retried by this decision.

## Authorized construction and verification

Sonnet253 may add this record to its existing isolated Caplab branch and
implement the new bundle/validator/launcher path with fabricated synthetic tests.
It owns routine closed schema names and static member inventory within these
constraints. Compare old v1 bytes/replay, new fixed-path and closure mismatch
refusals, tampered/writable dependencies, changed loader resolution inputs,
per-call resource cleanup, full new launch-plan/evidence revalidation and
unchanged credential/custody semantics. Independent Sol reviews the exact commit
before root integration. No real credential read, auth refresh, native Codex or
Bubblewrap execution, registration, provider action or host policy mutation is
granted here. Cleanup touches only task-owned synthetic fixtures; preserve all
frozen diagnostic/review evidence. Reopen any semantic departure separately.
