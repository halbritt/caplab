# Recognize the observed legacy clone flag

Baseline `88f6ee7`. Decision owner: primary agent under ADR 0026 and the
continuing CAPLAB improvement goal.

## Decision and prospective authorization

The preceding native diagnostic failed its 30-second deadline. Separately,
both public binary exec and parentage inspection rejected unabbreviated native
thread-creation records containing `0x400000`. The Linux header identifies
that bit as `CLONE_DETACHED`. Select a semantic parser repair, not a change to
native execution or to the failed attempt's disposition.

Authorize changes to `process_trace.py`, its public-interface tests, the exec
tests, the process-trace contract and this record. Recognize the named flag
and hexadecimal encodings of exactly that bit. Preserve refusal of unknown
bits, abbreviated flags, ambiguous lifetimes and selected thread/parent-sharing
edges. Successful detached creation must use legacy clone without CLONE_PIDFD;
clone3 and the PIDFD combination are invalid according to the Linux contract.
Failed calls may retain those known flags without supplying child evidence.

Run failing regressions before each repair, bounded local kernel controls and
the full repository suite. A fixed C control may be compiled in a fresh private
directory and run under Bubblewrap/strace with no network, a 10-second process
limit, 2 MiB trace/file limit, bounded capture and owned cleanup. Read the prior
private diagnostic through its unchanged manifest anchors to check compatibility;
write only a new inspection result. No native rerun, credential access, provider
call, model spend, study promotion, historical research mutation, tracker write,
message or push. Preserve prior artifacts, unrelated `docs/designs/`, worktrees
and services. Retain source hashes, failures, verification and advisory provenance
under `/tmp/caplab-clone-detached-*`. Stop on unexplained failures or unsupported
syscall semantics; do not broaden numeric acceptance to make a trace pass.
Authorization expires at the verified local commit. Independent acceptance,
normal native shutdown and full capture binding remain unestablished.

No change leaves a reproduced compatibility defect. Ignoring all creation calls
or all numeric flags would weaken the parentage contract. The existing shared
parser is the owner of this rule for both public readers; no new interface or
configuration is needed.

## Additional observed tracer syntax

The fixed C control exited zero and the kernel refused detached PIDFD and
clone3 calls with EINVAL. The private inspector first failed because it counted
Bubblewrap's own clone as the selected C child. The trace also contains the
numeric flag as `0x400000 /* CLONE_??? */`. Authorize that exact strace annotation
on the known numeric bit, with a public regression. Do not strip arbitrary
comments or accept annotations on unknown masks. Select the control's call by
its declared detached flag and namespace return PID; this is a synthetic kernel
format control, not independent authentication of the C parent. Preserve the
first inspector and failed log, and inspect the existing completed control
without rerunning it.

## Execution and verification

The shared parser now recognizes only the known detached bit, its named form
and the observed numeric annotation. Unknown numeric masks, decimal encodings,
wrong annotations and empty flag tokens still fail. A successful detached
creation is checked for the syscall/PIDFD restrictions before entering the
creation list. Failed calls retain known flags but supply no child. Selected
`CLONE_THREAD` and `CLONE_PARENT` edges remain refused.

Three new public test methods cover legacy forms and thread distinction,
failed versus impossible successful combinations, and exact exec composition
with unknown-token rejection. The retained red logs demonstrate failure before
the flag, combination and annotation repairs. All 18 focused process/exec
tests pass, including the existing authenticated namespace kernel control.
No exec payload comparison or receipt schema changed.

The separate C control's parent 3685521 created child 3685522 (namespace PID 3)
at trace line 5. Its child reported namespace parent 2, agreeing with the
creator's own output. Legacy detached clone succeeded; detached PIDFD and
clone3 each returned EINVAL. The process exited zero. The source, compiled
binary, trace, bounded process receipt, first inspector failure and corrected
inspection are retained under `/tmp/caplab-clone-detached-*`. This verifies
observed kernel/trace behavior, not an independently authenticated C parent.
The existing Python fixture supplies the separate authenticated control.

The Linux header `/usr/include/linux/sched.h` defines the bit; the installed
clone manual and [upstream Linux manual](https://man7.org/linux/man-pages/man2/clone.2.html)
document its legacy behavior and the invalid combinations. This repair does
not claim to validate every Linux flag combination.

Read-only compatibility verification checked the preceding manifest hash
`59235207f65690b7fb2701e3258d38c22d311f13415aeab547d9ca37f3b426a3`
and all 194 artifact hashes. With the repaired parser, new inspection of that
unchanged trace verifies creator 3643245 to child 3643254 at line 20 and exact
selected binary exec at line 21. The new result is
`/tmp/caplab-clone-detached-compatibility.json`. Original parser refusals and
the native timeout remain preserved; this is no retroactive successful attempt.
No native process was launched in this repair.

## Advisory review and remaining limits

The release gate verified source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`
and release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
Initial packet `pkt-6f59a6e8be8cb692` and final Markdown were read. Five typed
records preserve authority, incidents, source, tests and runtime evidence.
Final packet `pkt-5ec36aa7f45fe2e0` has SHA-256
`5ec36aa7f45fe2e0ab77f17aabea4f2414f7dd115dd96bd864fef28b0cf49860`;
versions are corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
Applied guidance is repository-contract precedence, evidence before
intervention, authority-bounded action, preserving unselected behavior and
separating semantic repair from structural work. The review checked that
numeric support cannot mask parent/thread semantics or alter original custody.

All 28 unmet obligations remain explicit: deduplication (3), population
discovery (4), asynchronous UI (4), declarative references (3), ranking (4)
and monitoring (3) are nonmaterial because those surfaces are unchanged.
External capability (3) and full readiness-gate verification (4) remain material
to broader integration/readiness claims, which are withheld. The bounded parser
checks inspect the raw trace; they do not establish serving parity or complete
execution/output attribution. No performance claim is made from either control.

Normal native shutdown, strict final-message transport-error handling, complete
capture binding and representative repair measurements remain open. The broader
goal remains active; this repair supplies no reviewer qualification or independent
acceptance.

## Final repository verification and custody

`make check` exited zero: 1,371 tests in 184.579 seconds, four skips. All three
new test methods ran. No runtime or test source changed after that run. Ruff F
and diff checks passed. Both fixed C peers are absent; prior diagnostic artifact
hashes were checked again and remain unchanged.

Manifest `/tmp/caplab-clone-detached-verification.json`, SHA-256
`0639c71a6cb6c97a7a54c4da45e353341e82d845a6f71973fd0784f0755b2f30`,
retains 25 artifacts, 14 source identities and 11 advisory scratch files embedded
and removed after exact-byte checks. Five citation observations are valid packet
citations. The authorization snapshot preserves the record bytes observed by the
typed evidence before this execution/closeout text was added. Source, artifact
and embedded hashes verified. The local commit closes this repair authorization;
the native timeout and broader roadmap remain open.
