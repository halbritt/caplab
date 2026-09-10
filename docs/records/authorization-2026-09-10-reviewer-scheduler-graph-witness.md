# Private graph witness for scheduler review evidence

Under ADR 0026 and the active ranking goal, authorize new private custody
`reviewer-ranking-001/development/scheduler-graph-witness-1`. Use only the
hash-checked base `0a7aa730f164e98a705dfe27c5db2ec8f20cc8a5` and repair
`b9325d547fa8fc4f8df38ddef274ca9eae6a95f4` source snapshots already preserved
in `scheduler-witness-2`. Preserve that custody unchanged.

Compile a newly authored Go test witness in the original `internal/driver`
package using Go's overlay mechanism to add one virtual test file. Do not
replace any original source or test. Historical test helpers may construct
the private graph, catalog, request, planned run, declaration objects and
synthetic failed-submission bundle. Their setup checks establish fixture
readiness only; historical test functions must not run, and their assertions
must not supply a reviewer verdict. Freeze the new witness and expected
behavior before execution. The expected provenance requirement remains
predating D0008.C1/C11.

Execute original graph initialization, object storage, run opening,
submission drain/classification, scheduling-decision creation, lane-binding
creation, graph reopening and folding. All graph identities, objects,
records, repository identity files and spool bundles are newly created test
data inside the isolated process. A fixed synthetic terminal message stands
for account exhaustion; no provider or real credential is used. No actual
execution backend may dispatch work. The original capture adapter records
calls only; the witness must verify zero dispatch calls.

Authorize one compilation per source revision, with a 180-second limit, and
two executions per revision, each with a 90-second outer limit. Each execution
covers five frozen conditions: ordinary placement, exhaustion with local
fallback, exhaustion with supervised fallback, an unrecognized terminal
message, and an expired observation. Total compilation/execution limit is
900 seconds. Use the existing pinned Go 1.23.4 toolchain and complete cached
module closure; disable network, downloads, automatic toolchain changes and
CGO. Source and dependency mounts remain read-only. Only private caches,
outputs and disposable graph directories may be written.

Retain complete newly created graph data and repository identity files before
test cleanup, plus raw observations and process records. Capture every setup
failure and stop its condition; do not treat setup failure as source failure
or repair success. Reopening and re-requesting an existing decision/binding
must be distinguished from first creation. Do not bypass the Driver's
manifest, policy, declaration, observation or graph checks to reach a desired
result. Killing on timeout is limited to owned process groups; test temporary
directories disappear after capture.

This authorization permits no write to a real Striatum repository, graph,
ledger, service or timer; no historical rewrite; no live reviewer call; no
corpus admission or ranking acceptance. Expiry: consumption or
2026-09-11T00:00:00Z. Stop on source/runtime drift, missing authorization,
unexpected external effect, fixture failure or the stated limits.
