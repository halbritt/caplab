# Preserve restarted creation calls without inventing parentage

Baseline `2495f11`. Primary agent under ADR 0026 and the continuing CAPLAB goal.

## Decision and prospective authorization

The latest native trace contains a complete clone resumption with result
`? ERESTARTNOINTR (To be restarted)`. The public creation reader rejects it;
the trace later records a separate successful clone. Select explicit recognition
of that exact internal restart result for the supported creation syscalls. It
has no returned child PID and cannot provide a birth. Continue parsing flags,
matching unfinished/resumed calls and requiring an independently selected,
unique successful creation with namespace translation. Do not infer which later
call is the restart or merge their line numbers.

Authorize `process_trace.py`, its tests, exec composition tests, the process
trace contract and this record. Run public failing regressions before repair,
existing real namespace controls, read-only compatibility inspection of the
unchanged native trace through its manifest anchors, and the full suite.
Retain source, test failures, verification and advisory provenance under
`/tmp/caplab-creation-restart-*`; commit the scoped repair locally. This is a
semantic trace-grammar repair, not a native runtime or timeout change.

No new native attempt, real credentials, provider call, model spend, historical
research copying/admission/rewrite/purge, tracker write, message or push.
Preserve unrelated docs/designs, worktrees, services and all prior evidence.
The failed native attempt remains failed; new inspection does not revise its
original disposition. Stop on unexplained tests, ambiguous restart semantics or
source drift. Authorization expires at the verified local commit. Full capture
binding, normal native shutdown, study readiness and independent acceptance
remain unestablished.

No change leaves a reproduced native-format gap. Ignoring every question-mark
result would admit unknown trace semantics. Treating the restarted call as a
birth would fabricate a PID; combining it with a later call would invent a
relationship the trace does not independently establish. The existing shared
parser owns this rule for both public readers; no new interface is needed.

## Source interpretation and execution

In [upstream Linux v6.8 fork.c](https://github.com/torvalds/linux/blob/v6.8/kernel/fork.c),
copy_process returns ERESTARTNOINTR when signals need handling before allocating
the new task. kernel_clone propagates that error before starting a child; the
supported creation syscalls use this path. This is source context for the
interpretation, not proof of identical Ubuntu kernel build bytes. The original
native trace supplies the observed runtime syntax. Source bytes and locator are
retained in `/tmp/caplab-creation-restart-kernel-source.json`.

The public regression failed with `invalid process creation result`. The repair
adds only exact restart-result recognition to the shared result check. It does
not append a creation record, skip flag validation or change resumption handling.
Three new test methods cover interleaving and later-call line numbers, restart
without any successful child, all four creation syscall shapes, unknown results,
malformed flags, duplicate births, wrong parentage flags, exact exec mismatch,
orphan resumption and exec/creation overlap. All 21 focused tests pass, including
the existing authenticated namespace kernel fixture. No new restart was induced
in the kernel; the retained real occurrence and synthetic regressions cover it.

The unchanged prior manifest
`eee968ec4dad28cb2a1be08285ade1653a1a9842b2053c675771084b0fb651f4`
and all 199 artifact hashes verify. New inspection of the complete original
trace recognizes the interrupted record at line 681 and verifies the selected
native creator 3717115 to child 3717124 at line 20. Exact binary exec at line 21
also passes. `/tmp/caplab-creation-restart-compatibility.json` records the new
inspections alongside the original refusal and failed native outcome. No source
trace, prior report, deadline or attempt disposition was changed.

## Advisory review and limits

The release gate verified fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial `pkt-2823371916d96a6b` and final Markdown packets were read. Five typed
records retain authority, incident, source, tests and runtime observations.
Final packet `pkt-dca3afa601c287ed` has SHA-256
`dca3afa601c287ed19aefe33d07834ee8d2d69360dba694450b159e2da96549b`;
versions are corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
Applied guidance is repository-contract precedence, evidence before intervention,
authority-bounded action, preserving unselected behavior and separating semantic
repair from structural work. Review checked exact-token matching, positive-PID
requirements, preserved flag/lifetime checks and unchanged original custody.

All 28 missing obligations remain explicit: deduplication (3), population
discovery (4), asynchronous UI (4), declarative references (3), ranking (4)
and monitoring (3) are nonmaterial to unchanged surfaces. External capability
(3) and full readiness-gate verification (4) remain material to broader capture
integration and study claims, which are withheld. No annotation, concurrency,
performance or complete Linux syscall-validation claim follows from this repair.

The next material investigation is native startup/retry delay and observation
overhead under the unchanged diagnostic deadline. Normal native shutdown,
strict final-message transport-error treatment and complete output binding
remain unresolved. No native rerun occurred in this repair.

## Final verification and custody

`make check` exited zero: 1,374 tests in 165.550 seconds, four skips. All three
new methods ran. Runtime and test source remained unchanged after the run.
Ruff F and diff checks passed. Manifest
`/tmp/caplab-creation-restart-verification.json`, SHA-256
`df04ba743d60cd66775da5fbcc711d1fc2469fb010c220b7c066c2e3bb3c544a`,
retains 14 artifacts, ten repository source identities and 11 advisory scratch
files embedded and removed after exact verification. Source, artifact and typed
provenance hashes agree; five citations classify as valid packet citations.
Prior artifact hashes were checked again and remain unchanged. The local commit
closes this repair authorization. The broader goal remains active; no independent
acceptance, qualification or roadmap completion is claimed.
