# Link an exact exec observation to its process termination

Baseline `2411ca0`. Primary agent under ADR 0026 and the continuing CAPLAB goal.

## Observation and scoped decision

The live work-instance Plane read contains 86 items, 12 open; CAPLAB-84 remains
In Progress. Its contract requires integrated native identity/capture evidence
and representative repair measurements. Existing fixture success cannot close
it. The latest fixed diagnostic has native launcher/binary exit zero while its
wrapper exits one because it preserves a transport error. Earlier diagnostics
have selected native SIGKILL termination. Private auditors currently parse those
terminal lines themselves; the public exec checker proves exact exec only and
intentionally does not interpret termination.

Select `caplab.exec_trace.inspect_exec_termination` with the same independently
supplied trace hash, PID, executable, argv, environment and byte allowance as
inspect_exec_trace. It composes the existing exact-exec check with a stable,
same-hash reread for one subsequent terminal event. Keep the existing inspector
and its accepted behavior unchanged. Do not infer native outcome from a wrapper
receipt or convert an exit code such as 137 into an inferred signal.

Require exactly one supported terminal record after the matching exec's
completion and no later selected-PID record. Reject missing, malformed,
ambiguous, out-of-order and visibly reused PID evidence. Decode canonical exit
codes 0 through 255 and named conventional Linux signals; retain a reported
core-dump marker as a trace observation, not proof that a core file exists.
Realtime/unknown signal encodings remain unsupported in this version.
The result distinguishes normal/nonzero exit from signal termination. It does
not prove task success, trace origin, executable-byte identity, complete native
capture or qualification. Later execs on the same PID do not create a new PID;
callers select the exact native binary independently when that is their subject.

## Prospective authorization

Authorize edits to src/caplab/exec_trace.py, new tests/test_exec_termination.py,
docs/product/contracts/exec-termination-trace-v1.md, a composition link in
exec-trace-v1.md and this record. Retain private `/tmp/caplab-native-exit-*`
source/control/verification and Plane-read artifacts. Use vertical red/green
checks, real local child processes with ordinary strace, and read-only inspection
of the sealed prior shutdown, WebSocket and close-observation diagnostic traces.
Preserve each original trace, source commit/path/hash and failed disposition;
new inspection results are distinct from original verification. No native agent
attempt, provider execution, real credentials, historical research admission,
tracker write, push, message, runtime deployment or independent acceptance.

Test exact exec binding, selected PID and ordering, missing/duplicate/malformed
terminal records, normal versus signal exits, later selected-PID records,
abbreviated/non-ASCII/incomplete traces, byte/hash limits and file custody.
Use real zero/nonzero/137/SIGKILL child outcomes behind a wrapper that exits one;
authenticate the child PID through a local socket and verify tracer provenance.
Run focused checks and the repository full suite. Preserve unrelated docs/designs,
worktrees and services. Stop on unexplained failures or source drift; do not
weaken existing exec/creation semantics. This scope expires at its local commit.

## Implementation and verification

The first public regression failed because inspect_exec_termination was absent.
The initial normal-exit implementation passed that regression; the next signal
cases failed until explicit signal termination parsing was added. Both failure
logs are retained. The final function composes the existing exact-exec checker
and a same-hash bounded reread, rejects selected-PID activity after termination,
and returns the terminal kind, exit code or signal, core marker and source line.
All existing exec function ASTs and prior constants are unchanged. The new
function does not replace exec-only behavior or mutate existing reports.

Seven new test methods cover the witnessed wrapper/native mismatch, exit-code
versus signal outcomes, core-marker syntax, missing/malformed/other-PID evidence,
lifetime contradictions, resumed execs, later execs on the same PID, exact
invocation requirements, file limits/identity, non-ASCII/unfinished input and
real authenticated children. The real controls use an outside ordinary tracer,
Bubblewrap isolation and SO_PEERCRED to identify each paused child, then verify
the retained tracer observation. Children exit 0, 7, 137 or by SIGKILL while every
wrapper exits one. All outcomes remain distinct, and descriptors/processes are
cleaned up. No provider or native model harness is used in those controls.

All 28 focused exec, termination and creation tests pass. Read-only application
of the public interface to three sealed prior diagnostic traces supplies six
new observations: entrypoint and binary each exit zero in the close-observation
trace, and each terminates by SIGKILL in the WebSocket and shutdown-timeout
traces. Every wrapper receipt reports exit one. Exact invocation and same-trace
checks precede each terminal report. The original trace bytes, manifests and
attempt dispositions remain unchanged; these are new versioned inspections,
not replacement original verifications. The earlier incomplete clone belongs
to a different PID and still prevents the separate whole-trace parentage claim;
it does not supply the selected binary's terminal outcome.

Retained application evidence is `/tmp/caplab-native-exit-application.json`;
its source script is inspect.py under the same prefix. Source-check.json records
the baseline/current hashes, unchanged prior function ASTs, toolchain and live
Plane counts. The public contract states the two bounded reads, unsupported
signal spellings, PID-chain interpretation and independent trace/lifetime
obligations. Test Guard found no mocked state or internal-call assertions;
codebase-design review keeps parsing/ordering in the trace module and exact-exec
knowledge in its existing function. No generic event bus or new execution
adapter is introduced.

The public capture launcher has not yet adopted this stronger report. That
integration must preserve frozen historical selections and distinguish wrapper,
entrypoint and native-binary outcomes without changing capture eligibility.
This implementation and its native-trace application provide the reusable check;
CAPLAB-84's complete integration and representative measurements remain open.

## Advisory and final checks

The validated Doctrine release is commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`. The retrieval-state gate passes with
source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-c61398cdc640bd88` and final packet
`pkt-6e3deaa7617f8f9a` were read. Final packet content SHA-256 is
`6e3deaa7617f8f9a6852ea3b61b51490f9e904244d610e119e42326223954dca`.
Five typed evidence records retain authority, incident, source, test and runtime
observations with source locators and hashes.

The selected guidance is repository-contract precedence, evidence before
intervention, authority-bounded action, preservation of existing behavior and
separation of semantic from structural changes. Leaving private terminal
parsers as the only implementation would retain demonstrated duplication at
the wrapper/native outcome boundary. Replacing the exec-only interface would
unnecessarily change existing callers. The selected additive composition
preserves those callers while providing one reusable outcome interpretation.
No adjacent refactor or generic trace-event framework is selected.

The final packet retains 28 unmet obligations. The 18 concerning deduplication,
bulk-input discovery, asynchronous UI states, declarative references and
top-N ranking are nonmaterial: this change has no such mechanism. The three
monitoring obligations are nonmaterial because the change creates no service
monitor or paging policy. The three external-capability and four authoritative-
gate obligations are material to complete native-capture integration and
serving parity; those broader claims are withheld. The current claim is
limited to the public parser contract, authenticated local process controls,
and new read-only applications to three original sealed native traces.

The full `make check` run passes: 1,381 tests in 168.112 seconds, four skips.
The focused suite passes 28 tests, including the four actual child outcomes.
Ruff F and diff checks pass. No runtime or test edits followed the full run.
AI-failure-modes review found no swallowed-error or fabricated-success path;
the explicit argument signature follows the existing exec contract rather
than introducing a new configuration abstraction. No new native attempt,
provider execution, tracker change, deployment, push or independent acceptance
occurred. The implementation remains separate from its public-launcher adoption.

Private manifest `/tmp/caplab-native-exit-verification.json`, SHA-256
`6f61046a67a084234bc07956453df40886fbbfbbc42a950cad339bc71a907f95`,
seals 18 retained artifacts, 11 baseline/current source records, four current
implementation/contract/test files and the Python/strace/Bubblewrap toolchain.
Eleven advisory scratch files were embedded with their hashes, verified and
removed. All five cited concepts classified as valid packet citations. The
sealer rechecked the original three diagnostic manifests and every artifact
listed by them without changing their contents or dispositions.

The final live Plane refresh still reports 86 items, 12 open, with CAPLAB-84
In Progress. The startup caller and native-launch configuration checker still
use exec-only inspection; stronger outcome composition is the next integration
gap. This commit completes the scoped reusable-inspector work and expires its
authorization. It does not close the broader roadmap or confer acceptance.
