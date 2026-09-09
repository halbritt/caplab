# Link a native binary to its launcher through process creation

Baseline `748e81a`. Primary agent under ADR 0026 and the continuing CAPLAB goal.

## Observation and decision

The last diagnostic authenticates PID 3586000, which execs `/toolbin/codex`
then `/usr/bin/node`. The actual native binary execs under PID 3586007. The
retained trace omits clone/fork calls, so adjacent exec records cannot prove
parentage. The root linker correctly withholds executed-invocation binding.
Installed strace 6.8 supports `--decode-pids=pidns`, which can distinguish a
child PID returned inside the workload namespace from its host trace PID.

Select a read-only direct process-creation verifier and bounded synthetic
kernel controls before native adoption. The caller supplies the authenticated
parent and independently selected child host PIDs, protected trace hash and
byte allowance. Require one completed successful creation with explicit PID
namespace translation, reject ambiguous process lifetimes and unsupported
parent/thread semantics, and preserve exact exec inspection in combined traces.
This supplies a missing relationship; it does not independently authenticate
trace origin, binary bytes, provider identity, output origin or a full Binding.

## Prospective authorization

Authorize `src/caplab/process_trace.py`, its tests and contract, and a narrow
extension of `exec_trace.py` to recognize validated process-creation records
alongside existing exec records. Preserve existing exec parsing and refusal
behavior for unsupported records. Use TDD for direct parentage, namespace PID
translation, failed/unfinished calls, interleaved vfork completion, wrong peers,
duplicate/reused PIDs, clone parent/thread semantics, bounds and symlinks.
Run fixed synthetic Python producers in isolated Bubblewrap under host strace,
with exact UTF-8 output, no network or installed native execution, bounded
time/streams/files, and owned process-group cleanup. Retain synthetic sources,
failures, traces, advisory packets and verification under
`/tmp/caplab-process-ancestry-*`.

No installed native attempt, credentials, provider call, model spend, study
promotion, historical research copy/admission/rewrite/purge, tracker write,
message or push is authorized. Preserve unrelated `docs/designs/`, worktrees,
services and prior diagnostic custody. Run focused tests and the full required
suite, inspect failures, and commit locally. Stop for an unexplained failure
or unsupported trace semantics; do not turn missing evidence into parentage.
This authorization expires at the verified local commit.

No change leaves the missing relationship unresolved. Inferring ancestry from
event order or a wrapper's source code is insufficient. A new live native
attempt before understanding the actual kernel trace format would mix capture
instrumentation uncertainty with native behavior; fixed kernel controls can
establish that format first.

## Observed trace format and additional repair scope

The fixed kernel probe observes a translated local/host PID and interleaved
`vfork` completion. Its retained trace also shows valid strace alignment:
`<... execve resumed>)           = 0`. The first live regression reaches both
peer observations and creation verification, then the existing exec reader
refuses that padded completion. Authorize accepting horizontal result padding
in the existing exec grammar, with an isolated regression that still refuses
changed argv. This corrects observed syntax; it does not relax payload equality
or infer ancestry. Preserve the first failing logs and exact format trace.

## Implementation and bounded verification

`process_trace.py` now verifies one direct creation using a closed caller
request, independent trace hash and explicit local-to-host PID translation.
It joins unfinished/resumed calls by host PID, preserves original line numbers,
requires exactly one birth of the selected child, and rejects visible lifetime
contradictions. Clone flags are parsed by name; parent/thread-sharing semantics
cannot supply ordinary parentage. A caller must authenticate the parent process
leader and its lifetime. The shared creation parser also lets the exec reader
handle combined traces without ignoring malformed creation records or changing
exact argv/environment checks.

Seven new process tests and two added exec tests protect the exercised
relationships. The first implementation lacked the module, then accepted
unsupported clone semantics and lifetime contradictions; retained red/green
logs show those failures and repairs. The real namespace fixture authenticated
both peers with SO_PEERCRED and observed their kernel tracer before release.
It initially exposed the resumed-exec padding defect; the separate regression
then failed before the grammar repair. All 15 focused trace tests now pass.

A separately retained execution of that same fixed test control is under
`/tmp/caplab-process-ancestry-runtime`. Its 9,674-byte trace has SHA-256
`51c33ea3c6a57e15b83ce1b5dc9566eec9f72b69db6e168b35c2eddea1d22344`.
Authenticated parent 3622377 creates authenticated child 3622379, returned as
local PID 3. The vfork starts at line 5 and completes at line 7. Both tracer
consistency checks pass, the child's exact argv/environment matches, the fixed
UTF-8 stdout is correct, exit is zero and the supervisor descriptor set is
restored. This is synthetic Python execution, not an installed native agent.

The read-only compatibility check independently verifies the preceding native
diagnostic's manifest, guard, configuration and trace anchors. Its effective
launch still matches the updated exec reader. The creation checker refuses
parent 3586000 / child 3586007 with `expected exactly one child creation`.
No original trace or record was changed. The installed launcher's inspected
`spawn(binaryPath, process.argv.slice(2), ...)` explains why another PID is
expected, but source code does not replace the missing runtime relationship.

Current Plane reads still show 86 items, 12 open. CAPLAB-84 and full capture
linkage remain incomplete. A subsequent native diagnostic needs a prospectively
authorized combined trace and must verify the actual binary's invocation and
installation identity as well as this relationship. This component alone does
not change root-link or study-eligibility flags.

## Advisory review and claim limits

The validated release packet was retrieved for the specific missing parentage
relationship. Initial `pkt-5488f22838e31c70` and final Markdown were read. Five
typed records retain authority, incident, source, tests and runtime observations.
Final packet is `pkt-a1f261a30c438655`, SHA-256
`a1f261a30c43865557248dc7e6a86b719a2051e7b04a27231da7f7085e221b18`.
Versions remain corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`, schema
`evidence-packet/3`.

All 25 missing obligations remain visible: unchanged deduplication (3), ingest
populations (4), asynchronous UI (4), declarative references (3) and ranking (4)
are nonmaterial to this trace parser. Three external capability obligations
and one evaluation/serving-parity obligation remain material to the broader
native integration and study claims, which are withheld. Three monitoring
obligations are nonmaterial because no service or paging behavior changed.
Applied guidance is repository-contract precedence, evidence before
intervention, separating semantic and structural work, preserving behavior
outside the selected grammar repair, and authority-bounded action.

## Final repository verification

`make check` completed successfully: 1,368 tests in 171.966 seconds, four skips.
All seven new process-creation tests and both added exec regressions ran. No
runtime or test source changed after that run. Ruff F and diff checks pass.
The full-suite log is `/tmp/caplab-process-ancestry-make-check.log`.
No installed native execution occurred in this scope, and the preceding native
trace still cannot establish parentage. This is verification of the component
and observed syntax repair, not independent acceptance or roadmap completion.

## Final custody

Manifest `/tmp/caplab-process-ancestry-verification.json`, SHA-256
`d9c275d1734cc7d04fb2e6e2206b4efcacee73ca83738d277950e86d1d44e81a`,
retains 13 source identities, 36 artifacts and 11 embedded advisory scratch
files removed after exact-byte checks. Source, artifact, typed-evidence
provenance and embedded hashes pass. The retained synthetic peers are absent,
and the preceding native manifest and trace anchors remain unchanged. Five
citation observations classify as valid packet citations.

The local commit closes this implementation authorization. No native attempt,
model spend, tracker write, push, historical research effect or independent
acceptance occurred. The broader CAPLAB goal remains active.
