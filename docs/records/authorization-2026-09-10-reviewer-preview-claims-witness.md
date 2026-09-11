# Investigate the natural scheduler review's preview claims

Under ADR 0026, authorize a bounded original-code investigation of the two
additional findings in `scheduler-natural-review-1`, final SHA-256
`4fa7a73703f5cd88ea9bce10b6746cb3a06bc575d8afd98a8bdfcde9b0187fe5`.
Create private `development/preview-claims-witness-1` under
`~/.local/share/caplab/reviewer-ranking-001`. Read the preserved original base
`0a7aa730f164e98a705dfe27c5db2ec8f20cc8a5` and change
`b9325d547fa8fc4f8df38ddef274ca9eae6a95f4`, their requirements and exact
source/tool inventories. Retain copied provenance, report and scoped source
excerpts outside the execution task. Preserve all original custody.

Compile the original packages with separately authored Go test overlays.
The overlays may use original fixture builders to establish valid inputs;
their expectations come from original source requirements and separately
observed behavior. Do not substitute a toy scheduler or a mocked preview.
Do not modify production functions or reuse the reviewer's test as the oracle.

For the new preview, exercise an ordinary supervised v3 outcome, an active
exhaustion v5 outcome, and a valid unsupervised v2 control. Record the original
preview result/error, complete input, scheduler schema and original graph
state. Supply a valid sample from the original session clock to the same
returned input and evaluate it using the original scheduler; compare with
the original recovery decision where applicable. Check graph observations
before and after the preview separately from recovery's authorized append.
No backend dispatch is permitted. Keep input validity and fixture failures
separate from a preview defect.

For the storage advisory, call original `buildSession` on freshly initialized
isolated fixture graphs in both revisions. Record filesystem membership,
content hashes and directory changes before/after first construction and
repeat construction; record original ledger contents separately. This
distinguishes inherited constructor effects from the newly added caller.
The new original environment-gated diagnostic may also run against a fresh
isolated graph with an explicitly absent run as an input-error control.
Report that scope exactly; do not portray it as a successful opened-run
diagnosis. No production store, host registry, provider or timer is mounted.
Synthetic local seal-key creation by original session construction is allowed
inside the fixture only; retain key hashes/metadata rather than key contents.

The read-only promise's scope is a separate requirement question. Source
inspection presently locates it on the preview method, not an explicit
blanket promise covering session initialization. Preserve that uncertainty;
constructor writes alone cannot establish an incorrect advisory or a broader
contract violation. Similarly, a test process that logs a diagnostic error
and exits zero has not necessarily violated a declared exit-status contract.

Use the original pinned Go 1.23.4 toolchain and offline cached dependencies,
read-only source mounts and fresh private build/capture directories. Freeze
probe bytes, source/tool bindings, conditions, predictions and comparison
rules before execution. At most three builds of 180 seconds each, six test
executions of 60 seconds each, and 1,200 seconds total. Expiry is consumption
or `2026-09-11T10:00:00Z`. No model calls, network, automatic retry, repairs,
source-repository writes or source-store mutation are authorized.

Preserve setup/compiler/runtime failures and every safe observation. Verify
inputs before and after execution, actual outcomes and control validity,
then record bounded interpretations with their original requirement basis.
Land results and update planning. New case-root admission, historical
rescoring, scorer acceptance and comparative ranking remain separate effects.
