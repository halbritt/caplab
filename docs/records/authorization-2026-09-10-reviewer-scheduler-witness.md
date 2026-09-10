# Scheduler decision and replay witness

Under ADR 0026 and the active reviewer-ranking goal, the primary agent
authorizes a local reproduction for sampled Striatum-next repair
`b9325d547fa8fc4f8df38ddef274ca9eae6a95f4`. Preserve the selected sample and
its denominator. This extends the read-only feasibility inspection with the
following exact effects.

Copy tracked regular-file trees from `/home/halbritt/git/striatum-next` for:

- precursor `58ff7ce58e58b0cd5ea7719c5826fa3716bfbb68`;
- first partial repair `147775a0047a1219e241ae4798813a50b35f32fc`;
- sampled base `0a7aa730f164e98a705dfe27c5db2ec8f20cc8a5`;
- sampled repair `b9325d547fa8fc4f8df38ddef274ca9eae6a95f4`.

Use new private custody
`reviewer-ranking-001/development/scheduler-witness-1`. Retain commit, tree,
path, original blob, mode, byte length and SHA-256. Record the `CLAUDE.md`
symlink's target and blob without materializing it; it is not a compiler
input. Do not rewrite source files. Mount the independently authored Go
witness under a new, separately identified directory in the module solely to
permit Go's internal-package imports.

Compile each revision once using the existing Go 1.23.4 toolchain and the
exact cached dependencies named by its go.mod/go.sum. Pin toolchain and
dependency bytes; disable module downloads, automatic toolchain selection,
CGO and network access. Builds may write only private build caches and
outputs. Each build has a 180-second limit. Missing dependencies or compile
failure remain preparation failures, not source defects.

Freeze input conditions, expectations and verifier criteria before running
the witness. Authorize two executions per revision, each returning the same
seven conditions: ordinary local placement, unrelated active observation,
exhausted supervised candidate falling back to local, supervised failover,
all supervised candidates exhausted, expired observation and malformed
observation. Each execution has a 30-second limit. Total build/execution
budget is 900 seconds. Kill only owned process groups on timeout.

Exercise original `DecisionSchemaVersion`, `Evaluate`, record canonical
serialization and record decoding. Preserve version selection, bindings,
refusals/deferrals, input/output preimages and every error. Check the effect
of removing an observation absent from the durable preimage; distinguish
this counterfactual from a complete record-to-input replay implementation.
No target tests may supply empirical verdicts, and no production graph or
driver is invoked. The independent expected behavior comes from predating
D0008.C1/C11, the original record schema and recovery consumer contract.

Keep inherited encoding failures, newly mismatched versions, repaired
serialization and potentially incomplete recorded inputs distinct. The
patch title and its operator diagnostic are leads, not independent truth.
Neither a working serialization path nor these checks accept a whole-patch
clean label. This authorization creates no admitted corpus, reviewer score,
historical acceptance, external provider call or operational change.

Preserve all attempts and their criteria. Stop on source/tool/dependency
drift, missing scope, or the stated limits. Expiry: consumption or
2026-09-11T00:00:00Z. No target repository, live ledger, service or timer is
modified. Private build artifacts may remain as evidence; ephemeral process
workspaces are deleted after guarded/local capture.
