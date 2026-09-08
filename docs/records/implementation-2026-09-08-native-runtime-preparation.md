# Prepare private persistent native runtime directories

Date: 2026-09-08. Baseline: `288bd9b`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `src/caplab/native_runtime.py`, `tests/test_native_runtime.py`, a versioned
runtime-preparation contract and this record; link it from the invocation
contract. Prepare only new private synthetic runtime directories in temporary
locations, retain exact synthetic prompt/plan bytes, inject filesystem failures,
and exercise the mount layout with a bounded local bubblewrap/Python probe.
Use no real native binary, credential, authentication, session or historical task
content. Permit focused/full tests and a local commit. Preserve all existing
native policy, invocation profiles, launchers, frozen manifests, capture sources,
`docs/designs/`, sibling worktrees and services. No model spend, live campaign,
historical evidence effects, tracker write, external message or placement.
Retain verification probes/logs; remove only named doctrine scratch after
recording receipts. Authorization expires at commit. Stop if plan validation
requires an unapproved profile or if the local containment probe requires access
to real credentials, unrelated host paths or a native inference process.

## Decision and boundary

The invocation builder names a persistent episode runtime but creates no host
state. The old launch path either disables native persistence or uses unsuitable
shared/transient harness storage. Select a new preparation API that revalidates
the complete invocation against the canonical builder and an independently
retained invocation digest before creating fresh host custody outside the task.
Retain the exact plan and prompt privately, create the selected harness/home
subdirectories, and publish an explicit host-to-namespace mount mapping only
after file/directory sync succeeds. Never reuse a root or copy an ambient home.

The runtime tree is the only intended writable runtime mount. The outer private
custody containing the plan, prompt and preparation receipt must remain outside
the agent's mount namespace. Configuration/credential seeding, executable
binding, filesystem/network containment, session linkage, quotas and launch
permission remain separate required adapter responsibilities. A preparation
receipt is not evidence that the namespace was mounted or a native launch was
safe. It also does not reserve a study assignment or prevent replay elsewhere.

No change leaves the new invocation API without persistent host destinations.
Retrofitting the old launcher would change frozen execution behavior; copying
shared harness homes would broaden input authority and mix episode custody.
This component instead creates only a named new empty runtime layout and sealed
input records, with partial state retained on failures and no automatic retry.
The model-free integration probe will test actual persistence and separation
under its stated mounts; it will not qualify a native harness or general sandbox.

## Execution and verification evidence

The new preparer checks the independent invocation digest and reconstructs the
complete canonical plan before any destination creation. It then publishes the
private plan, writes and syncs exact prompt bytes, creates the selected empty
runtime/home tree, syncs directories and publishes the preparation receipt.
It returns a prospective task/runtime mount mapping and translated host capture
paths. Returned state comes from the reconstructed owned plan, not the caller's
mutable map. The preparer is synchronous, holds no cache/worker and starts no
process. Existing invocation profiles and capture/launch code remain unchanged.

Seven focused tests passed in 0.655 seconds:
`/tmp/caplab-native-runtime-focused.log`. Both layouts retain exact hashes and
private modes. Invalid or independently re-hashed unsupported plans fail before
creation. Existing roots, task overlap and linked host paths fail without
replacement. Prompt write failure leaves the retained prefix, closes its
descriptor and withholds preparation; directory-sync failure likewise retains
partial state and refuses retry into that root. These are new-feature checks,
not a reproduction of a pre-existing runtime-preparation implementation.

The integration test uses actual bubblewrap 0.9.0 and local Python under
`--unshare-all`, explicit mounts and a cleared environment. It passes a synthetic
unrelated secret to the outer process and verifies its absence inside. Task and
runtime writes persist after the child exits; sealed inputs and the owner's
home are unavailable at the checked namespace paths. The bounded task capture
and integrity verifier run on that same process. No native executable, API,
authentication or model is involved. This establishes the tested mount behavior,
not general sandbox, credential-containment or network-policy conformance.

A retained standalone probe also applies the full planned environment before
running its synthetic Python child. It verifies `HOME=/episode/home` and
`CODEX_HOME=/episode/codex`, retains synthetic session/diagnostic bytes and a task
result, and inspects the process/task bundle. Probe and receipt:
`/tmp/caplab-native-runtime-probe.py`, `/tmp/caplab-native-runtime-probe.json`.
Retained root: `/tmp/caplab-native-runtime-probe-q6y_w5xk`. Attempt SHA-256:
`8f6d7c1bd801c98da55501c672f46a759584aeeb072e4b56095ca6638751ad11`.
The inspection checks 5,221 receipt bytes, nine task bytes, three task entries
and 111 stream bytes, with one added `result` path and exit code zero. The
synthetic session file explicitly identifies itself as mechanics data, not
native evidence. Its presence proves persistence only.

Source hashes, direct-import checks and unchanged protected-source checks are
retained in `/tmp/caplab-native-runtime-source-check.json`. No unused direct
imports were found. The tested interpreter is Python 3.12.3. No dependency,
formatter, checker or CI setting changes. The explicit paths and failure policy
keep filesystem ownership in this preparation module while delegating plan
semantics and publication to their existing owners. Reopen for a new layout,
profile or consumer requiring recovery/adoption; none is inferred from a hash.

The full `make check` completed successfully: 1,021 tests in 177.371 seconds,
four skips, exit zero. Log: `/tmp/caplab-native-runtime-make-check.log`.
Source/test hashes still match the focused-check receipt, and all seven named
protected sources remain byte-identical to baseline `288bd9b`.

## Advisory doctrine and completion

Final packet `pkt-6f269658d198da19`, content SHA-256
`6f269658d198da19d918a84913f3514b66b0bc3441b64e2f0fca55c1de34628e`,
uses `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9` and
`retriever-ec995ecdd083b2c8`. The question nominated no precise concept;
baseline, routed, prerequisite and kernel guidance is advisory only.
One evidence-gathering pass supplied five typed records. Four citations classify
as valid: `python-structured-cleanup` (paired descriptor closure),
`python-text-bytes-boundary` (exact UTF-8 prompt preservation),
`universal-preserve-behavior-by-default` (protected existing sources), and
`agent-conduct-authority-bounded-action` (prospective preparation versus launch).

Six obligations remain nonmaterial to this bounded feature:

- `implementation-placement-by-ownership`: `recurring change evidence when available`;
  this implements an accepted missing runtime contract, with no churn claim.
- `implementation-repository-language-conformance`: `CI and build matrix` and
  `formatter and static-tool configuration`; no such configuration changes or
  cross-platform/tooling qualification are claimed.
- `python-repository-shaped-idiom`: `formatter linter and type-checker configuration`;
  the change follows adjacent source and makes no formatter/checker claim.
- `python-runtime-static-boundary`: `annotation maintenance cost` and
  `configured checker and Python version`; no annotation-cost or static-proof
  claim is made, and the actual tested Python version is recorded above.

The first citation invocation used the wrong schema key and then treated
`--receipt` as an output flag. Both failed without altering repository evidence;
using `schema_version` and stdout redirection produced the checked classification.
Verification is consolidated in `/tmp/caplab-native-runtime-verification.json`,
including packet identity, obligations, citations, source/probe checks and hashes
of exactly eleven removed doctrine scratch files. All execution logs, probes,
source checks and retained synthetic custody remain available.

This implementation is verified for its stated preparation contract and tested
mount layout. It does not complete CAPLAB-84 or CAPLAB-85, authorize inference,
prove containment for a native harness, establish session completeness, or admit
reviewer capability evidence. Next integration work is bounded collection of
this episode's native session and diagnostic files, followed by a separately
specified adapter. No independent acceptance judgment is recorded here.
