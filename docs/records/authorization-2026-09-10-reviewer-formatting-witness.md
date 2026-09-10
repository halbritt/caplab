# Check the selected formatting-only change against original execution

Under ADR 0026 and the active reviewer-ranking goal, authorize investigation
of selected Striatum change `98759de9d5f1bfa855cc8d7ff43456be243db7db`
and parent `03f0cc39b02c7882674ca2706398560e986b1032` in private custody
`reviewer-ranking-001/development/formatting-witness-1`.

Import original tracked `internal/`, `backends/`, `policy/`, `go.mod`,
`go.sum` and `Makefile` from these exact revisions, retaining commit, tree, path, Git blob,
mode and content hash. These subtrees supply source, compilation fixtures,
backend declarations and policy read by the affected original tests. Any
historical policy or declaration imported remains reference material for
this historical execution, not current authorization, qualification or
reviewer truth. No previous runs, graph stores, credentials or historical
sweep outcomes may be imported. Preserve source bytes without repair.

Freeze a comparison of complete changed-path membership and original
`internal/scheduler/glm_activation_test.go` bytes. Run the pinned Go 1.23.4
formatter against both files without editing either source. Check whether
the normalized bytes agree and whether the change is already formatted.
Compile the original scheduler test binary for each revision with locked,
cached dependencies, then run exactly the two original tests in the edited
file twice against their respective original repository inputs. No added
test, proxy implementation or model response supplies the outcomes.

Use network-free namespaces, read-only source/toolchain/dependency mounts,
and private writable build caches and execution captures. No actual backend,
model, provider, live graph, service or original repository may be mutated
or executed. The tests inspect historical declarations; their assertions
and passing results must not be promoted into current model-capability
claims. Build the whole original package but execute only the named tests.

Limit each build to 240 seconds, each test execution to 60 seconds, formatter
to ten seconds and the sequence to 900 seconds. Expiry is consumption or
2026-09-11T00:00:00Z. Stop on source/runtime mismatch, unsupported import,
compile failure, test failure or timeout. Preserve failure and do not change
the original tests or inputs to obtain a pass. Preserve all comparison
results even if they disprove the formatting-only interpretation.

The bounded question is whether the edit changes Go program tokens or the
affected original test outcomes while restoring formatter conformance.
Record other limitations explicitly. Update fixed-sample coverage only when
the named original behavior is established. No case admission, reviewer
measurement, historical rescoring, accepted ranking or operational placement
is authorized by this investigation.
