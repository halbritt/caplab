# Original Driver accepts a decision with missing placement evidence

The original Striatum-next Driver at sampled repair
`b9325d547fa8fc4f8df38ddef274ca9eae6a95f4` creates a local-fallback scheduling
decision, binds its lane and reopens the graph successfully. The decision
omits the active exhaustion observation that caused fallback. Removing that
observation from the original scheduler input selects the preferred backend.
This extends the [record-level witness](verification-2026-09-10-reviewer-scheduler-outcome.md)
through the actual graph decision and binding path.

The missing input matters under the predating D0008.C1/C11 requirement for
deterministic placement and complete decision preimages. A successful graph
append or restart does not establish that requirement. This is development
evidence for the sampled repair's review case; no reviewer is measured here.

## Observations

Each revision was compiled once and executed twice. Each execution covered
the same five conditions. All 20 diagnostic observations agree across
repetitions on the assessed properties. They belong to one failure family.

| Condition | Base `0a7aa730f164` | Repair `b9325d547fa8` | Observation evidence |
| --- | --- | --- | --- |
| Ordinary placement | Preferred backend; v3 | Same | No exhaustion observation |
| Recognized exhaustion, local fallback | Driver refuses v5/v2 mismatch before append | Local fallback; v2; binds and reopens | Active observation absent from decision |
| Recognized exhaustion, supervised fallback | Supervised fallback; v5 | Same | Exact active observation retained in decision |
| Unrecognized terminal message | Preferred backend; v3 | Same | Classifier creates no exhaustion observation |
| Expired observation | Preferred backend; v3 | Same | Observation remains in graph but is inactive |

All 18 completed decision/binding paths survive reopening and a fresh Session
fold. Repeating their decision and binding requests creates no records. The
two base local-fallback observations stop with the original Driver error:
`scheduling decision version moved from v5 to v2`; neither appends a decision.
Every condition records zero adapter dispatches.

The repaired local-fallback path contains one valid, active, graph-backed
observation in its scheduler input and none in its v2 decision preimage. The
counterfactual input with that observation removed selects `capture` instead
of `fallback`. The supervised-fallback control has the same selection effect
and retains the exact observation in its v5 preimage. These checks distinguish
the missing causal input from an unused field or an invalid source fixture.

The omission itself predates the sampled repair. The repair changes the
predicted schema so the existing incomplete v2 preimage passes through the
production append path. The graph still contains the source observation;
this witness establishes neither irrecoverable data loss nor incorrect
backend execution after restart.

## Method and boundaries

The witness adds one virtual test file to the original `internal/driver`
package through Go's overlay mechanism. Original source and tests are
read-only and unchanged. Historical helpers construct a disposable graph,
catalog, request, planned run and content-addressed declarations. Their setup
checks establish readiness; no historical test function runs and no
historical test assertion supplies the defect label.

A synthetic failed submission contains a fixed monthly-spend-limit terminal
message. The original submission drain, exhaustion classifier and policy
create its observation. The production Driver validates manifest, policy,
declaration and classifier pins before decision append. The witness calls
the original decision and lane-binding methods, reopens the original graph
store and repeats the requests through a fresh Session. It does not run the
outer recovery loop or dispatch a backend. Provider exhaustion is simulated;
no provider, credential or real Striatum graph is used.

The governing source requirement and commit provenance are pinned in the
prior record-level receipt. New witness criteria were frozen before execution.
The checker was written after capture to apply those criteria. It requires
graph-backed observation provenance, exact stored decision content, consistent
reopened binding and zero dispatches. Setup/capture failures are unmeasured.
Observation removal remains a counterfactual, not a general decoder for
reconstructing scheduler inputs from a decision record alone.

The counterfactual also supplies the fixture's host-clock sample, which the
supervised result requires for execution bounds. In the original
`internal/scheduler/evaluation.go`, `Evaluate` selects bindings before reading
that clock; the clock does not enter `bind`. The prior record-level witness
already supplies the clock in both observation-present and observation-absent
inputs. The new witness extends graph reachability of that established
placement effect and records this administration difference explicitly.

## Execution and custody

The [first authorization](authorization-2026-09-10-reviewer-scheduler-graph-witness.md)
attempt failed in Go vet because vet could not open the virtual overlay file.
No witness ran. The [second authorization](authorization-2026-09-10-reviewer-scheduler-graph-witness-2.md)
permits a separate build with `-vet=off`; all Go witness, overlay and criteria
bytes remain identical. Its inaccurate statement about a first-attempt
binary is corrected in a [separate observation record](correction-2026-09-10-reviewer-scheduler-graph-build.md).
Both private attempts remain preserved.

The corrected compilation/execution campaign took 15.94 seconds. Go 1.23.4
and the cached module closure were hash-checked before and after execution.
The namespace disables networking, dependency downloads, toolchain selection
and CGO. Source and dependencies remain read-only. Graph data, spool bundles
and repository identity files were copied before temporary-directory cleanup.
The four execution captures retain 396 files with checked inventories.

Private custody is under
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/scheduler-graph-witness-2`;
the failed preparation is its `scheduler-graph-witness-1` sibling. The
[receipt](../product/studies/reviewer-ranking-001/scheduler-graph-development-receipt.json)
pins both attempts, the existing source custody, process outputs, capture
inventories and verification. Corrected plan SHA-256:
`692a839050253defb17ffc7fd597b24c8b31a34bd5664fb49aba753e50dc82a0`.
Verification SHA-256:
`554256ea2e73ee15fc29850a6c703421a3232a6454eeb504f78ec040fd25c265`.

Five new checker tests challenge missing provenance, altered reopened state,
invalid folds, setup/effect failures, absent counterfactual effects and
refusals that write records. All nine focused scheduler checks pass.
`make check` passes: 1,521 tests in 209.07 seconds, with seven skips. All 70
receipt file hashes were rechecked before landing.

## Ranking implications

The case now has an original Driver/graph witness for its incomplete decision
preimage. It must still receive an explicit case-admission and attribution
decision before scoring first-pass review. General scorer validity, remaining
fixed-sample coverage, held-out incident separation, uncertainty and ranking
rules remain open. There is no accepted reviewer ranking.
