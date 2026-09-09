# Adopt isolated procfs in one native diagnostic

Baseline `455fa31`. The primary agent acts under ADR 0026 and the continuing
CAPLAB goal. The preceding native file-capacity diagnostic reached the fixed
custom call, whose command failed setting up its Bubblewrap UID map through
read-only procfs. The new opt-in handoff mode passed actual nested Bubblewrap
execution, privilege-refusal controls and the 1,337-test repository suite.
Installed-native completion remains unverified.

## Decision and prospective authorization

Select one installed-native diagnostic using the verified mode. Authorize this
record and private source, preflight, capture and verification artifacts under
`/tmp/caplab-native-nested-*`. Derive the probe from
`/tmp/caplab-native-file-capacity-probe.py`, SHA-256
`09cb8cee7c7785c5b841bd30ce5bc0237f9330be205d8cfeabf6f38e4ab1ac30`.
Change only the owned prefix, removal of the outer `/proc` read-only remount,
and `nested_userns=True` at mount handoff. Keep the outer root read-only.
Freeze current source pins; exactly two helpers legitimately differ from the
old preflight through commit `455fa31`. Preserve both generations of identities.
Require every other source pin, native installation, tracer and decoder pin to
match before launch and after capture.

Permit exactly one launch of installed Codex 0.153.4 with gpt-5.6-terra/max,
using the canonical native policy builder and the preceding fixed invocation,
prompt, scripted custom-call response and final-message response. Preserve
workspace-write sandboxing, local response/refresh overrides and tracing.
The newly fabricated authentication fixture is read-only and secret-quarantined.
There are no real credentials, external model/provider endpoints or model spend.
Unshare user, PID, mount and network namespaces; expose only loopback and the
two previously allowed devices. Drop capabilities and require NoNewPrivs before
the supervisor checks the peer and releases it. Keep five 64-MiB writable tmpfs
mounts, the 8-MiB per-file limit, zero core/swap, child/outer memory 256/512 MiB,
child/outer PID limits 128/192, and native/capture/unit/outer time limits of
30/45/90/100 seconds. Preserve 300,000-byte child streams, 1-MiB task files,
8-MiB selected native artifacts and 40-MiB/2,000-entry full-mount retention.
The local fixture retains its 1-MiB wire/decoded body limit, at most 32 requests
and exactly two permitted response POSTs. It stops on its first error.

Verify exact derivation and preflight before consuming the launch. Require the
native custom-call output to contain successful command status and the exact
UTF-8 witness, captured task bytes to agree, the fixed final message to be
retained, two successful response POSTs and natural native process completion.
A JavaScript launcher or tracer exit zero alone is insufficient. Inspect the
bounded failed-syscall/signal trace for the actual Codex process status. Keep
root/tuple linkage, stdout tool-pair availability and capture completeness
distinct; do not invent tool events absent from a native projection.

On failure, preserve partial custody and its observed cause; no retry is
authorized. Quiesce and reap only owned processes, close fixture/listener/input
descriptors, remove only the exact owned unit and verify its cgroup is absent.
Verify capture hashes, known-value quarantine, source/installation identities
and recorded namespace/resource predicates after exit. Do not weaken criteria
to obtain a success label. No repository runtime change, tracker write, message,
push, historical research evidence effect, study adoption or independent
acceptance is authorized. Preserve `docs/designs/`, all sibling worktrees and
services. Commit the resulting record locally; this allowance expires at that
commit and is consumed by its single native launch.

Leaving the old probe unchanged repeats the observed UID-map blocker. Disabling
Codex sandboxing changes the evaluation subject. A successful synthetic
Bubblewrap control cannot establish native integration. This bounded diagnostic
addresses the next missing observation while preserving the native harness.

## Preflight

Exact replacement counts and bootstrap equality passed. The derived probe is
`/tmp/caplab-native-nested-probe.py`, SHA-256
`f3b8e219cfbb5d093076dda0230d1f0445b957ae9ecc37005c8e8711bffc5705`.
The native plan and full inventoried installation match the preceding selection.
All 13 current source identities match committed `455fa31`; the only differences
from the old preflight are the two authorized helpers. Decoder and strace pins
match. Preflight: `/tmp/caplab-native-nested-preflight.json`. Ruff F passed.
Proceed with the single authorized native launch; no retry allowance remains
after it starts.

## Observed result

The one run used unit
`caplab-native-nested-7fd652da130e42aea77b459798202661.service`.
The live handoff passed its new procfs, namespace and privilege predicates.
Codex emitted a command-execution start and result in stdout and a matching
custom-call output in the retained rollout. Both report exit 1:

```
bwrap: Can't bind mount /oldroot/dev/zero on /newroot/dev/zero: Unable to mount source on destination: No such file or directory
```

This is a later sandbox setup failure than the preceding UID-map error. It
does not establish successful command execution. The captured task remains
empty and no final message exists. The second response POST reached the local
fixture; its missing-witness assertion refused a final success response and
triggered owned cleanup. The wrapped tracer status is -9 after that cleanup;
natural native completion is unavailable. No native timeout was reported.

The first verifier inherited an empty stdout tool-pair expectation from the
preceding run and failed on the newly available pair. Its source is retained as
`/tmp/caplab-native-nested-verifier-before-pair-correction.py`. Direct inspection
of stdout lines 8 and 9 and the parsed pair established one matching native ID,
unchanged command text, failed status and exit 1. The corrected verifier requires
those observations and agreement with the rollout command output. The task
success criteria remain unchanged and unmet.

Verification: `/tmp/caplab-native-nested-failure-verification.json` and
`/tmp/caplab-native-nested-verify-failure.py`. Task, selected-native and full-mount
custody checks passed, including the new recorded procfs predicates. Retained
mounts contain 3,692,752 bytes and 141 entries; 118 retained files were scanned
for the configured raw forbidden values with none found. The 92,771-byte filtered
trace has no EFBIG or delivered SIGXFSZ. Child PID-limit and memory max/OOM/kill
event counters are zero before and after. No forced post-capture group kill or
quarantine refusal occurred; fixture-triggered process cleanup is separate.
All 13 source pins, the installed harness, decoder and tracer still match.
The exact unit now reports not-found and its observed cgroup path is absent.

The next implementation question is whether an explicit diagnostic device
profile can supply the native sandbox's required `/dev/zero` while checking the
exact character-device identity and preserving existing callers. This record
authorizes neither that extension nor a second launch. Any subsequent profile
must be separately selected, tested and authorized before native adoption.

## Advisory closeout

The Doctrine retrieval gate passed at release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
The authoritative gate log retains the exact printed fingerprint. Initial
packet `pkt-6f76160e0ca7e7b0` and five typed evidence records led through two
passes to `pkt-eae7afae33aac191`, SHA-256
`eae7afae33aac191093c2158a6b865b43d463c17670f5ee98778ca3d1744b5c3`.
Versions: corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`,
schema `evidence-packet/3`. The initial and first reassembled Markdown were
read; the final diff changes packet identity and four discharged obligations.

The 25 remaining obligations are classified by their effect on this result:
18 on deduplication (3), population ingestion (4), async UI (4), declarative
references (3) and ranking (4) are nonmaterial to this fixed diagnostic; none
of those product paths changed or is certified here. Three external-capability
obligations and one evaluation/serving-parity obligation remain material to a
working native/provider integration or study-readiness claim, which is withheld.
Three monitoring obligations are nonmaterial because no service or paging
policy changed. The explicit provisional-verification record and direct source
inventory of gate signals satisfy the four newly discharged obligations.

Applied concepts are repository-contract precedence, evidence before
intervention, separation of semantic and structural changes, preservation of
default behavior, and authority-bounded action. The claim is a verified native
failure observation and containment-compatibility diagnosis. It is not a
completed repair shakedown, successful native task or reviewer qualification.

## Final custody

`/tmp/caplab-native-nested-verification.json`, SHA-256
`8e62b5173a4d9964cc9769102a623da6ecc7f304fa2f19becf675e417df33846`,
retains 132 artifact hashes, 13 source identities and 13 embedded advisory
scratch files removed after archival. All artifact, source and embedded hashes
were checked before removal. A fresh unit read and cgroup-path check confirmed
cleanup again. Five citation observations classified as valid packet citations.
Ruff F and diff checks pass. No runtime or test source changed after the
previous 1,337-test suite; this diagnostic adds only its repository record.
One native allowance was consumed, with no second launch. No real credentials,
model/provider spend, tracker writes, messages, push or historical research
evidence effects occurred. The continuing CAPLAB goal remains incomplete.
