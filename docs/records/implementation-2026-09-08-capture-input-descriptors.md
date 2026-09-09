# Pass explicitly borrowed descriptors through bounded process capture

Date: 2026-09-08. Baseline: `db78e11`. Decision mechanism: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md) and the
continuing owner request to improve CAPLAB.

## Authorization and preservation

Authorize an additive `pass_fds` argument in `src/caplab/process_capture.py`,
focused tests under `tests/`, the bounded-process-capture contract update, and
this record. Permit local model-free tests, the required full suite, private
advisory and verification artifacts under `/tmp/caplab-capture-fds-*`, and a
local commit. Preserve existing callers, receipt schema, limits, explicit
environment and input snapshots, process-group cleanup, failure propagation,
and historical custody. No unrelated refactoring, credential-guard changes,
tracker writes, pushes, messages, or other worktree/service changes. Preserve
`docs/designs/`. This implementation authorization expires at commit.

Also authorize one newly identified offline native integration probe after
focused tests pass: installed Codex invoked only as `codex login status` with
the whole-second fabricated credential fixture from the preceding private
probe source. Reuse its source construction, not its past outcomes as new
observations. Freeze the new script, fixture, source and installation hashes
before release. Supply the synthetic bytes through the new descriptor API and
Bubblewrap `--ro-bind-data`; no payload in argv or environment. No actual
operator credential/configuration read, account access, provider request,
model inference, token refresh, or new historical-evidence admission.

Use a fresh `/tmp/caplab-capture-fds-native/` root, fresh owned user unit,
all-unshared Bubblewrap namespaces, loopback-only network, read-only host and
native mounts, two required device nodes, and a private 64-MiB runtime tmpfs.
Bound the unit to 512 MiB memory, zero swap, 64 tasks and 40 seconds; native
capture to five seconds and 100,000 bytes, outer capture to 50 seconds and
100,000 bytes. Require exact input bytes, read-only write refusal, no input
memfd surviving into the final native bootstrap, complete native capture and
exit zero, unchanged source manifests, and stopped/unloaded owned unit with
absent cgroup. Preserve partial custody and stop on any failed criterion;
no native retry allowance. This is transport verification, not renewed
provider-authentication evidence or a representative repair shakedown.

## Observation and decision

The [preceding characterization](verification-2026-09-08-native-codex-auth-format.md)
found two permission-denied failures when Bubblewrap tried to bind a
supervisor's `/proc/<pid>/fd/<n>`. Direct inherited `--ro-bind-data` worked,
but its private launcher constructed the input from synthetic bytes in argv.
That workaround is unsuitable for real credential bytes. The current
`capture_process` calls `Popen` without an input-descriptor allowlist; the
older Revbench subprocess owner already uses Python's `pass_fds` facility.

Add an optional empty-by-default descriptor sequence to the existing capture
owner. Snapshot it as a tuple; require unique exact integers greater than 2
and require each to be open before capture custody is created. Pass only those
explicit descriptors through `Popen` with `close_fds=True`. Reject booleans,
standard-stream numbers, duplicate or closed descriptors, and malformed
containers. Do not read, hash, seek, close, duplicate, or change inheritable
flags on the caller's descriptors. The caller must keep the descriptors open
and their identities stable until the call returns; this is borrowing, not
protection against a caller concurrently closing/reassigning descriptors.

The launched program can use the inherited handles according to their existing
permissions. File offsets and other open-file-description state are shared;
this interface does not make writable descriptors read-only or prevent child
output from disclosing input bytes. Callers remain responsible for sealed
inputs, launcher closure of handles before the final subject exec, redaction,
and external containment. The receipt format is unchanged and contains no
input payload. Empty default preserves existing no-extra-descriptor behavior.

Leaving capture unchanged would retain the demonstrated transport gap. A new
launcher or descriptor-remapping framework would add another resource owner
without a present requirement. Borrowing numeric descriptors matches the
existing subprocess convention and lets Bubblewrap consume a sealed memfd
directly. No throughput or generalized secret-management claim is selected.

Verify actual child receipt of allowed synthetic bytes, exclusion of unrelated
inheritable descriptors, unchanged parent ownership, list snapshot behavior,
invalid/closed rejection before custody, and ownership through timeout, launch
failure and capture exceptions. Then exercise the direct Bubblewrap/native
path once under the fixed authorization above. These checks do not establish
provider authentication, refresh support, complete credential isolation from
authorized child code, or measurement-task completion.

## Implementation and bounded native observation

The existing process owner now accepts `pass_fds=()` and performs the frozen
validation before custody creation. Its `Popen` call supplies the snapshotted
allowlist with `close_fds=True`; CAPLAB neither duplicates the input descriptors
nor changes their parent flags. Existing call sites and the v1 receipt schema are unchanged.
The contract now documents shared offsets/permissions and stable borrower
lifetime. It deliberately makes no promise to protect against a caller that
closes or reassigns a borrowed handle concurrently.

Seven focused tests were added. Before implementation, their first run failed
on the absent `pass_fds` argument; that baseline is retained in
`/tmp/caplab-capture-fds-red.log`. After implementation, all 26 process-capture
tests passed in 1.794 seconds. They exercise binary input receipt without
payload output, unchanged parent flags and handles, shared offsets, exclusion
of an unrelated inheritable handle with both empty and nonempty allowlists,
mutation of the caller's list during setup, invalid/closed input rejection
before custody, timeout, missing executable, storage error and cancellation.
The actual child is used for delivery and cleanup assertions; injected capture
failures verify exceptional paths rather than substituting successful launches.

The single authorized offline native probe completed at
`/tmp/caplab-capture-fds-native/`. Its frozen script is
`/tmp/caplab-capture-fds-native-probe.py`, SHA-256
`d1d7dfb3d35b39952b0fd519e5909b86cbef7efda4d7f68b0e5ab788d9f9665e`.
The probe directly invokes Bubblewrap with the borrowed sealed input descriptor;
it no longer reconstructs payloads from argv. Its synthetic input SHA-256 is
`3d966dafd4212437c6087301eeeee89ab76132ef5e30e604dc1548f9f041152a`.
Codex's installation manifest remained unchanged, and its selected npm package
version remains `0.153.4`. Native status exited zero with complete streams and
`Logged in using ChatGPT`. This is expected local recognition of fabricated
credentials, not provider authentication.

The bootstrap verified the exact input hash, read-only write refusal (`EROFS`),
loopback as the only network interface, and no inherited memfd before native
exec. The parent descriptor remained non-inheritable and retained the original
sealed bytes after capture. The observed unit limits matched 512 MiB memory,
zero swap and 64 tasks. Unit
`caplab-capture-fds-8d8c46541d294409b20522d38fa6626f.service` unloaded and its
observed cgroup disappeared. No retry was needed or permitted.

A separate read-only verification script,
`/tmp/caplab-capture-fds-verify.py`, checked both process receipts and complete
stream hashes/counts, report-to-receipt agreement, fixture/script/installation
and runtime source identities, the direct Bubblewrap invocation, absence of
synthetic payloads from invocation/capture, read-only delivery and live
unit/cgroup closure. Its output is `/tmp/caplab-capture-fds-checked.json`.
The fixture selection document intentionally retains fabricated source bytes;
its custody is distinct from invocation and native output. No actual operator
credential was inspected or supplied.

## Advisory provenance and review limits

The validated release gate recorded source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, and retriever `retriever-ec995ecdd083b2c8`.
Initial packet `pkt-86bf8dfa7af9f41e` preceded two bounded evidence passes
covering authority, contracts, source and test assertions. Final packet
`pkt-5989d570ccf2ef75` has content SHA-256
`5989d570ccf2ef753e5269692a99244cfdeb1c6df0a7c1b8a84a8c79176a2eee`.

Eight unmet obligations remain individually classified as nonmaterial: six
architectural-boundary obligations do not require a new boundary to be built
or evaluated for this additive existing-owner change; two language/tooling
matrix obligations do not alter a change using the installed, already-used
Python subprocess facility with no interpreter, dependency or style migration.
Existing API/tests, adjacent source and Makefile were directly inspected.
No missing material evidence is treated as satisfied by a test plan.

Citation closure records six used concepts: `python-structured-cleanup`,
`python-mutable-ownership`, `implementation-placement-by-ownership`,
`universal-explicit-invariants`, `universal-repository-contract-precedence`,
and `universal-evidence-before-intervention`. Their effects are borrowed
lifetime/cleanup, container snapshots, placement in the existing launcher,
pre-custody checks, compatibility preservation, and the observed transport
counterexample justifying the addition. No generic configuration object or
new launcher framework was introduced solely to reorganize the existing API.

The AI failure-mode pass checked installed API support, real subprocess
execution, exception propagation, absence of fallback successes and unused
imports, and preservation of the current owner. Ruff's undefined-name/unused
import checks passed for the changed runtime, new tests and private probe and
verifier. This is local implementation verification, not an independent verdict
or acceptance of CAPLAB-80/84. Actual authentication, refresh policy, credential
quarantine and representative repair execution remain separate requirements.

## Final verification and custody

Closeout: 2026-09-09 (Pacific); work began on September 8. The required
`make check` passed all 1,247 tests in 162.407 seconds, with four skips;
`/tmp/caplab-capture-fds-make-check.log` retains the output. Local links in
both changed documents and whitespace checks passed. The review made no
further runtime changes after the native probe and full-suite run.

Release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` was rechecked.
The private manifest `/tmp/caplab-capture-fds-verification.json`, SHA-256
`a70d87f1fb5d280bb818a10712f2124b940eb623395737ed40757c5175c0efbb`,
retains 30 artifact identities plus final runtime/test/contract hashes.
Eleven advisory scratch files were embedded byte-for-byte, rechecked and
removed. The native root, frozen probe, verification script, observations and
all test/probe logs remain available. This closes the bounded implementation
and synthetic transport check without completing the broader roadmap.
