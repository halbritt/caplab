# Connect restricted routing to the scripted native diagnostic

Baseline `7596a85`. The previous goal turn committed a bounded retained-routing
reader. The native diagnostic still hosts its scripted endpoint inside the
workload's loopback namespace. Moving its provider exchange through restricted
routing requires a distinct profile and a supervisor-owned fixture, while
preserving request identity, the authenticated child-observation handshake,
prepared task inputs, native execution provenance and raw failure outcomes.

Under the continuing owner goal and ADR 0026, the primary agent selects a
`codex-scripted-routed/v1` diagnostic configuration. It uses the fixed synthetic
IPv4 address `198.18.0.1` in a newly owned disconnected outer namespace; only
the actual fixture TCP port is permitted. No host address or route changes.
The fixture runs outside the workload cgroup, retains its own bounded protocol
artifacts under trusted quarantine, and requests the existing freeze/observe/
thaw handshake as the authenticated supervisor process. The native workload
remains independently authenticated by the mount and exec handoffs. This is a
different collection path, not a claim that TCP itself authenticates a native
process. The old offline profile remains unchanged.

Authorize changes to `native_launch_configuration.py`, `scripts/scripted_native/`
and `scripts/probe_scripted_native_capture.py`, and the shared native custody
inspector as required for this explicit profile. Add focused tests and a
versioned contract; update this record and relevant existing diagnostic
documentation. Preserve old preparation formats and offline behavior. New routed
preparation must explicitly pin its profile and additional tools. Materializing
a workload as mapped root and dropping all five capability sets before handoff
are profile-specific choices, not silent changes to the old configuration.

Fresh tests may launch only synthetic Python/WebSocket producers inside owned
disconnected namespaces and exercise the real policy, routing and capture
components. Preserve new private diagnostics, failures and advisory artifacts
under `/tmp/caplab-routed-native-*`. No historical custody may be copied,
modified, replayed or admitted. No installed native harness may execute until
the final-source gates pass and a separate exact one-attempt authorization is
recorded here. No provider/model calls, real authentication, spending, tracker
writes, messages, deployment, push, scoring or study execution are authorized.
Preserve unrelated `docs/designs/`, worktrees and services. Run focused and full
checks, retain provenance and commit verified implementation locally. This
implementation authorization expires at that commit; an eventual attempt needs
its own purpose, source/configuration/input pins, resources and expiry.

Owned fixture threads, namespace processes, routing helper and cgroups must
terminate on success and failure. Stop on unexplained loss of containment,
identity disagreement, quarantine, failed cleanup or changed source pins. A
failed native attempt remains failed even if its bounded observation verifies.
The routed diagnostic remains synthetic: it cannot establish provider
compatibility, representative repair costs, model quality or qualification.

Keeping the loopback fixture would not test routed provider traffic. Replacing
the native harness with a shared HTTP client would change the subject. Select
the supervisor-owned fixture and preserve actual native execution as the later
integration gate. This feature changes a named profile, not the study design.

The routed profile must allow the policy-install/readback and routing-readiness
steps before the native body. Select a 25-second routed mount-handoff timeout,
75-second process-capture ceiling, 120-second owned-unit ceiling and 130-second
outer capture ceiling. Keep the 30-second native body, five-second native
identity/observation handshake, memory/task/file/stream limits, and 45-second
routing-helper ceiling. The new preparation freezes these profile-specific
limits. They are diagnostic stops, not guarantees of successful scheduling or
measured repair costs. The offline profile's existing ceilings remain unchanged.

## Implementation observations and preparation scope

The routed launch/profile test first failed as unsupported; it now pins the
fixed external address, distinct configuration hash and exact trace expectation.
The fixture tests first failed on the absent bind/quarantine options and absent
thread owner. Real WebSocket exchange, guarded-before-write refusal and joined
cleanup after a body error now pass. The production outer namespace test reached
the real handoff but its test callback omitted the existing quarantine argument;
that fixture adaptation was corrected, along with use of the helper's documented
tuple return. It now exercises the production outer network and supervisor
endpoint through the actual policy/routing/retained-inspection path.

The existing bootstrap-worker characterization needed `external_fixture=None`
in its extracted offline execution context after adding the new branch. Its
shutdown and late-fallback predicates were preserved. A new summary test exposed
four accepted peer/time contradictions; numeric runtime checks now refuse them.
Its initially expected ValueError was corrected to the neighboring supervisor's
existing RuntimeError convention. The explicit routed preparation test also
exposed the inherited offline capture ceiling before the distinct limits were
implemented. Red and subsequent check logs remain under `/tmp/caplab-routed-native-*`.

Source review found that calling `ExitStack.close()` on exceptional exit would
deliver a normal exit to the routing context. Exceptional and guarded-refusal
paths now pass the actual exception triple so the producer's `body_completed`
field cannot be cleared by successful cleanup. The normal path closes routing
after stopping workload writers and closes the fixture before sealing its own
summary. Existing producer deadlines remain the final bounds; no retry is added.

Authorize preparation-only creation of new synthetic input at
`/tmp/caplab-routed-native-task-source`: `README.txt` identifying the diagnostic,
directory `input`, binary file `input/payload.bin`, and symlink `link` targeting
`input/payload.bin`. Retain it under `/tmp/caplab-routed-native-task-input` with
65,536-byte/100-entry limits and record exact source definitions and hashes.
The newly constructed source may be removed after verified retention. No
historical input is copied. Prepare fresh native custody at
`/tmp/caplab-routed-native-attempt-1`, using the declared installed Codex root
`/home/halbritt/.npm-global/lib/node_modules/@openai/codex` and retained WebSocket
dependency `/tmp/caplab-native-transport-deps/websockets`. Select only the new
routed profile and that exact new input. Preparation may read source/tool bytes
and native policy; it may not execute the native harness or spend an allowance.
Stop on unsupported/changed inputs or an existing destination. A later execution
authorization must name the resulting hashes and final-source test result.

## One installed-native execution authorization

The final-source full suite returned exit zero: 1,470 tests, four skips,
256.284 seconds. Log: `/tmp/caplab-routed-native-make-check-final.log`. The
59-test focused pass is retained separately; final full-suite source includes
the exceptional-context cleanup correction. All fifteen changed Python source
hashes in `/tmp/caplab-routed-native-final-source.json` still match. Preparation
and source checks passed without consuming an attempt. All 166 implementation
inputs were copied into `/tmp/caplab-routed-native-source-snapshot` with their
prepared hashes and original repository paths; unchanged governing inputs retain
baseline commit `7596a85` provenance. This is authorized current-source custody,
not historical research admission.

Under ADR 0026, authorize exactly one installed-native diagnostic at
`/tmp/caplab-routed-native-attempt-1`, preparation SHA-256
`e43cc0758e3d418dd13d4b1c8c0b103a7cb909678f8e7f3b1ee6400fe6d3888d`.
The input is `/tmp/caplab-routed-native-task-input`, receipt SHA-256
`626a261b34f11df899c7228baecf6de6559e92fb15b6d671db29e1940172a529`,
content SHA-256 `15d2298900c21ec590027e140a7d524b61d7938448928c545badbaa54618cb33`:
95 bytes across five entries. The exact constructed bytes and link target are
in `/tmp/caplab-routed-native-preparation-result.json`. No historical task is used.

The configuration is Codex 0.153.4 Linux x64, configured `gpt-5.6-terra`, effort
`max`, summary `detailed`, with `codex-scripted-routed/v1` and native binary
SHA-256 `56ef98ab4032d317ab26e9b5e5a175650717351edb16ed9cde0cb6d1734d62da`.
Use the fixed prompt, supplied tool call/responses, fabricated authentication,
prepared routing/capture profile and frozen resource ceilings above. The outer
network has no external route; zero provider/model calls and zero spend are
permitted. This is not a served-model Binding, study trial, blinded observation
or representative repair. The primary agent knows all synthetic inputs/output.

Create a new exact `caplab.scripted-native-authorization/v1` file under the
private prefix, retain its hash and this authorization snapshot, recheck inputs
immediately before consumption, then execute once through the repository CLI.
Verify consumed/result/manifest linkage, prepared-before and witness-only change,
native source/argv/request/child identity, outer network and routing custody,
separate native/fixture outcomes, byte preservation and owned-unit/cgroup removal.
Preserve every failure and unavailable field. The known possible missing
WebSocket close frame remains an attempt failure even if inspection verifies.
Do not change criteria inside verification or grant a retry from this allowance.

Only the newly named diagnostic's owned unit/cgroups/namespaces may be created
or stopped. Stop on source/input drift, an unexplained containment or identity
failure, quarantine, resource termination or incomplete cleanup. No second
attempt, provider access, score, study freeze, coder exposure, historical effect
or roadmap closure follows. This authorization expires at this one consumption
and its verified cleanup; a failure preserves the spent allowance.

## First attempt: missing input mount

Attempt 1 consumed its allowance and exited one before mount handoff or native
launch. The isolated outer worker could not open the selected input custody:
`FileNotFoundError: /tmp/caplab-routed-native-task-input`. The new namespace
mounted the native installation and fixture dependency but omitted the prepared
task bundle needed by `read_preparation` and later materialization. The earlier
synthetic outer test used an empty task and did not cover this dependency.
This is an integration defect, not native behavior or a representative outcome.

The result SHA-256 is
`115c0eb790404713b8025359efa6be94ba336cef8d78d7cfc95932070a8997a5`.
The service capture is complete with exit one, and the inspector reports the
missing native artifacts as unavailable. The owned unit
`caplab-scripted-native-7f46d2e7e12b487397aa4e9c77b0efeb.service` is not found
after cleanup. Raw execution, inspection and preparation evidence stays intact;
no native executable or model ran and this allowance remains spent.

Authorize correcting the outer profile's read-only input-custody mount and
testing actual input validation from inside that namespace, including refusal
to write it. Extend the exact outer-command reconstruction with the same selected
input path. This is a semantic repair within the selected profile, not a change
to the task or to attempt 1. New source requires fresh preparation and final
checks; this repair grants no execution of the old preparation or new attempt.

The regression reproduced the same missing-directory failure with a task bundle
outside the outer custody mount. The repaired command mounts that exact bundle
read-only. The test now validates it inside the outer namespace, observes EROFS
on a write attempt, materializes it through the real authenticated handoff and
reads its actual bytes from `/work` before contacting the routed fixture. The
existing handoff test helper gained only an optional task-input argument to
exercise that path. Original empty-task controls keep their defaults.

Authorize fresh preparation only at `/tmp/caplab-routed-native-attempt-2`, with
the same declared installed sources, routed profile and exact new synthetic
input receipt `626a261b34f11df899c7228baecf6de6559e92fb15b6d671db29e1940172a529`.
This reads that named input in place and imports no historical research. Preserve
attempt 1, its consumed allowance and all source/custody snapshots unchanged.
The corrected implementation must pass fresh final-source gates before any
separate attempt-2 execution authorization. No execution is granted here.

## Corrected-source verification and integration boundary

The corrected full suite completed with exit zero: 1,470 tests, four skips,
198.756 seconds, retained at
`/tmp/caplab-routed-native-make-check-corrected.log`. The owned process handle
also returned exit zero. All sixteen changed Python hashes in
`/tmp/caplab-routed-native-corrected-source.json` match the current files.
The seven-test input-materialization pass is retained at
`/tmp/caplab-routed-native-task-materialization-green.log`. The regression uses
real namespaces, a read-only task bundle, authenticated materialization and
restricted routing to the supervisor endpoint; it does not launch Codex.

Fresh attempt-2 preparation has SHA-256
`a5ec2eb55675d6813617083205b6335cb522b0948c04437b3905bcafb3dade1c`.
Preparation and all current inputs were rechecked after the full suite; its
allowance remains unconsumed. Attempt 1 is still unavailable and failed.
Commit this implementation with that integration gap explicit. Actual routed
native execution remains the next material gate; passing component and
regression checks does not discharge it.

Source review checked the fixture's started/finished futures, stop/join owner,
workload-before-routing-before-fixture shutdown, exceptional routing-context
exit, closed profile validation and separate raw native/fixture outcomes.
The new profile and its input-mount repair are semantic changes. The offline
profile, old preparation formats and their characterization tests remain the
preservation boundary. No new interface hierarchy or configurable destination
is introduced. The supervisor thread shares one summary only after joining;
the summary join creates a new mapping and leaves raw observations intact.
Binary task bytes remain opaque, and the existing UTF-8 witness remains exact.
The contract now explicitly lists the selected task custody's read-only mount.

The owner's subsequent instruction, "maybe push to main", authorized publishing
the committed main history. That push completed and the remote was verified at
`7596a85`, matching local HEAD. It supersedes the earlier no-push boundary for
that requested publication; it does not turn uncommitted work into a release
or grant independent acceptance of this diagnostic.

## Advisory and retained verification

The validated Pincite release gate passed again at release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-160133577bb43a45` and five inspected typed evidence records
produced final packet `pkt-a3f0b8df3d966da3`, content SHA-256
`a3f0b8df3d966da34fb5c17668bcd952d0f0d7d90c2bf79e939acbf1f62af60e`.
Versions: `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9`,
`retriever-ec995ecdd083b2c8`. Repository authority takes precedence.

The selected guidance concerns structured cleanup, mutable ownership, runtime
validation, preservation, authority and evidence before intervention. It supports
committing the explicit diagnostic implementation and running the next bounded
experiment; it does not verify the missing native integration. The receipt is
`/tmp/caplab-routed-native-decision-receipt.json` with status `executed`.
All seven remaining advisory obligations are individually classified in
`/tmp/caplab-routed-native-obligations.json`: CI/cross-version matrices, formatter
and checker configuration, annotation cost and static-checker evidence are
nonmaterial to this local diagnostic claim. No cross-platform, type-checker or
performance claim is made. The material native execution gate remains open.

Evidence and receipt schemas validated. Both served packets have retained
citation classifications; local record locators are distinguished from doctrine
concept citations. Changed Python files passed Ruff F checks, `git diff --check`
passed, the CLI exposes the documented profile selector, and relative contract
links resolve. Source review found no further material defect within the inspected
paths. This is the primary agent's review, not independent acceptance.

Private verification manifest `/tmp/caplab-routed-native-verification.json`
retains 241 artifact identities and sixteen changed Python hashes, SHA-256
`e911516c2cd4d3fbb6978df098eae8927c35a230d7dfe031b4d640e646cb90d4`.
It preserves the first failure, both preparations, source snapshot, corrected
checks, typed evidence, advisory packets and receipt. Later execution must add
new custody and provenance without rewriting these observations.
