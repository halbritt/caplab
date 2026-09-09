# Check filtered tracing against the evidence contract

Baseline `3208029`. Primary agent under ADR 0026 and the continuing CAPLAB goal.

## Decision and prospective authorization

The installed strace 6.8 manual describes `--seccomp-bpf` as reducing ptrace
stops to selected syscalls, with fallback if filter setup fails. CAPLAB requires
creation/exec records independent of success or failure. Workload seccomp may
take precedence over the tracer filter, so matching selected successful calls
alone would not establish preservation of failed-call evidence.

Authorize a bounded fixed C control and Python supervisor under
`/tmp/caplab-trace-filter-*`, this decision record, and a clarification of the
process/exec trace contracts if the observations warrant one. Compile a local
fixed producer: issue exactly 10,000 getpid syscalls, create one child, then have
that child install a filter returning EPERM for execve and clone. It must attempt
both denied calls and report their actual return/errno values before exit. No
native agent or provider is involved. Compare three alternating pairs of ordinary
and seccomp-filtered strace using the same executable, namespace layout and
syscall selection. Retain every attempt and both failures and successes.

Use Bubblewrap with all namespaces unshared, readonly executable/system mounts,
no network, 256 MiB address-space limit, 2 MiB file/trace bound, no cores,
10-second process deadline and 10,000-byte capture. Existing capture owns cleanup;
do not target other processes. Record exact command/source/binary/tracer identities,
raw output, traces and elapsed capture intervals. Counts and selected-call
retention are the primary comparison. Timings describe only this constructed
syscall workload and cannot estimate native agent overhead or explain its timeout.

No native rerun, model spend, real credentials, external workload endpoint,
historical research copy/admission/rewrite/purge, tracker write, message, push
or independent acceptance. Preserve unrelated docs/designs, worktrees, services
and all prior custody. Stop on unexpected return values, filter setup failure,
timeouts or cleanup failure; do not repeat a failed pair automatically. No
production tracing configuration or native deadline change is authorized.
Commit the verified record/contracts locally; authorization expires at commit.

No change preserves instrumentation uncertainty. Adopting an optimization from
its description alone risks incomplete evidence. The control tests evidence
preservation before considering any native adoption, with no completeness claim
from successful parentage or exec checks alone.

## Initial observations and additional control authorization

The first ordinary control exited zero with both denied calls. Its inspector
incorrectly expected an empty environment. Bubblewrap's installed manual says
clearenv preserves PWD; the trace contains only PWD=/. Correct that expectation
and inspect the existing completed run without rerunning it. Preserve the first
script and failed log. The remaining five planned executions completed normally.

All three pairs retained both denied records in both modes. The anticipated
omission was not observed. Before interpreting this as successful filter
compatibility, authorize two additional fixed state controls, one per mode.
Use a separate derived C source/binary that reports Seccomp_filters from its own
proc status before and after installing the child filter. Preserve the original
six runs and workload; these two are state observations, not additional timing
samples for that comparison. Keep prior bounds and cleanup. Inspect the installed
version's upstream tracer implementation if needed. No native adoption follows
without evidence that the relevant filtering was actually active.

## Discriminating child-state control

Both state controls exited zero. Ordinary tracing reported zero inherited
filters and one after installation; filtered tracing reported one and two.
Both still retained both denied calls. Filter presence alone does not establish
that the tracer uses its optimized resume path for that child.

Upstream strace v6.8 `src/strace.c` marks a newly forked process with
TCB_SECCOMP_FILTER only after its first seccomp stop. Before that transition,
the restart path uses PTRACE_SYSCALL. This supplies a concrete rival explanation
for the initial result, not proof of this installed binary's internal state.

Authorize one additional pair under `/tmp/caplab-trace-filter-primed-*` and
`/tmp/caplab-trace-filter-primed-runs`. Derive the state control by adding one
child execve of a fixed nonexistent path before installing its denial filter.
Require return -1/ENOENT and retain that call and its output. This selected
syscall can trigger the tracer's child-state transition before the two denied
calls. Keep all prior source, results, filter logic, limits and namespace
configuration. Compare ordinary and filtered modes once each, retain either
presence or absence of the denied trace records, and stop on any unexpected
producer result, incomplete capture or failed cleanup. No timing comparison
across these changed workloads, no native run and no production adoption.

## Observations and selected disposition

The additional pair completed with exit zero, complete captured streams and
empty stderr. Both children reported the preliminary exec result -1/ENOENT,
then execve and clone results -1/EPERM. The ordinary trace retained both denied
calls at lines 7 and 8. The filtered trace retained the preliminary exec at
line 6 and child exit at line 7, with neither denied call between them.
Both public selected-exec and direct-parentage inspections passed. These are
checks of retained observations, not proof that every selected syscall arrived.

| Control | Ordinary denied records | Filtered denied records |
| --- | ---: | ---: |
| Original fixed producer, three pairs | 2 in each run | 2 in each run |
| Filter-count observation, one pair | 2 | 2 |
| Preliminary selected child exec, one pair | 2 | 0 |

The last pair uses `/tmp/caplab-trace-filter-primed.c`, compiled with
`cc -Wall -Wextra -Werror -O2`. Its aggregate is
`/tmp/caplab-trace-filter-primed-comparison.json`; source, executable, tracer,
command, raw trace, captured stdout/stderr and inspection hashes are retained.
All ten fixed controls completed; no native agent ran in this investigation.

The [Linux v6.8 seccomp documentation](https://www.kernel.org/doc/html/v6.8/userspace-api/seccomp_filter.html#return-values)
places ERRNO above TRACE in filter precedence. In
[upstream strace v6.8](https://github.com/strace/strace/blob/v6.8/src/strace.c#L3932),
a child's first seccomp stop sets its filter state; the subsequent resume path
uses PTRACE_CONT between selected calls. The
[filter implementation](https://github.com/strace/strace/blob/v6.8/src/filter_seccomp.c)
supplies TRACE for selected calls. Together these support the explanation that
the original child stayed on syscall stepping until exit, whereas the added
selected call enabled filtered stepping before the denials. This is a source-
supported inference, not a direct observation of the installed tracer's flags.
The upstream tag is not exact Ubuntu package-build provenance. The observed
omission itself is established by the fixed producer and retained streams.

Select ordinary tracing for the existing evidence producer contract and
explicitly exclude `--seccomp-bpf`. This clarifies the existing requirement
to retain selected calls regardless of outcome. The public text readers cannot
detect pre-write omissions, so actual producer configuration remains a caller
obligation. No parser, API, startup command, timeout or native configuration
changes. Reopen this restriction only with separately scoped evidence that a
replacement observation mechanism preserves the required failed-call coverage.

The original alternating capture intervals were 0.164656/0.081295,
0.231370/0.132204 and 0.265162/0.155368 seconds (ordinary/filtered). They include
setup and cleanup for a synthetic 10,000-getpid workload; cache state was not
controlled. No native overhead estimate, performance target attainment or timeout
cause follows. A faster capture that omits required calls cannot meet this
evidence contract. Native startup/retry delay, normal shutdown, strict output
linkage and representative repair remain open.

## Advisory review and verification

The retrieval gate verified fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`
at Pincite release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
Initial packet `pkt-d4b8ba03ae7a751c` and final packet
`pkt-c4a90b9e85a15e1b` were read as Markdown. The final content SHA-256 is
`c4a90b9e85a15e1b56610a9f516b8b9ba97a57dc3d068ad0c12deef03772cf0f`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`.
Five typed records cover authority, incident, source, tests and runtime. Five
citations classified as valid: repository contract precedence, evidence before
intervention, authority-bounded action, preservation of behavior, and separation
of semantic and structural work. This is a producer-contract clarification
backed by a failed compatibility control; runtime behavior is unchanged.

All 29 residual obligations are explicit. Deduplication (3), population
discovery (4), asynchronous UI (4), declarative references (3), ranking (4)
and operational monitoring (3) are nonmaterial to this bounded control and
unchanged product surfaces. External capability verification (4) and readiness
gate authority (4) remain material to broader native integration, performance
or study claims, which are withheld. A demonstrated counterexample suffices
to exclude this proposed configuration; it does not qualify the replacement
or prove ordinary tracing complete.

The retained audit `/tmp/caplab-trace-filter-audit.json` checks all ten capture
receipts and stream hashes, exact producer results, raw denial counts and
selected-call reports. Every PID present in each trace has an exit-zero record
and was absent in procfs at audit. Both new C builds used warnings as errors;
Ruff F passes for the final comparison, auditor and closeout scripts. All 21
existing trace tests pass. Eight runtime/test/toolchain files match baseline
`3208029`; the prior full-suite result remains 1,374 tests with four skips.
No full suite was repeated for these documentation-only edits. Local contract
links and diff whitespace checks pass. No production tracing option changed.

## Final custody

Manifest `/tmp/caplab-trace-filter-verification.json`, SHA-256
`ff96d6a8b9281204709a932d10f06aa83e8a663c693bd76f285f3d673a6502d8`,
retains 80 artifacts and 13 repository source identities. Eleven advisory
scratch files were embedded byte-for-byte and removed after hash verification.
All artifact, source and typed-provenance hashes agree. The initial failed
environment expectation, all ten original captures and the control that
contradicted the initial compatibility observation remain retained. The local
commit closes this authorization. No native rerun, model spend, tracker write,
push or independent acceptance occurred; the broader CAPLAB goal remains active.
