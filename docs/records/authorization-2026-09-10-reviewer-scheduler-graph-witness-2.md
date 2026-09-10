# Correct graph-witness compilation administration

Under ADR 0026 and the active reviewer-ranking goal, authorize a separate
`reviewer-ranking-001/development/scheduler-graph-witness-2` attempt with all
source, isolation, capture, condition and execution limits of the
[first authorization](authorization-2026-09-10-reviewer-scheduler-graph-witness.md).
Preserve the first custody unchanged, including frozen runner and plan
`42179cc2721ada6343d89ee8b44a8f927f981452540791747e0a27a310f0ce63`.

Its sole compilation returned code 1 because Go vet could not open the added
virtual file: `vet: open internal/driver/caplab_graph_witness_test.go: no such
file or directory`. No witness execution occurred. The compiler produced an
output binary before vet failed, but that binary is not admitted for reuse.

Add `-vet=off` to the new isolated `go test -c` invocation. Vet is static
analysis outside the measured Driver path. Do not alter the Go witness,
conditions, expected properties, original source, graph validation or
classification to obtain a passing result. Pin the revised runner and reuse
the same witness and criteria hashes. Compile each revision afresh in the new
custody; the new limits are one compilation per revision, 180 seconds each,
two executions per revision, 90 seconds each, total 900 seconds. Stop on
fixture failure or unexpected effects. Expiry remains 2026-09-11T00:00:00Z.
No ranking, corpus admission, real backend execution or target-system write
is authorized.
