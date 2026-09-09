# Characterize native cached-credential parsing without provider access

Date: 2026-09-08. Baseline: `736ed55`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization and preservation boundary

Authorize a private fixed probe script and one execution under
`/tmp/caplab-codex-auth-format-*`, plus this repository record. The script may
invoke the installed Codex npm entrypoint only as `codex login status`, once
for each of five prospectively named synthetic cases: absent credential,
whole-second refresh timestamp, fractional-second refresh timestamp, expired
ID-token claim, and invalid refresh timestamp. No actual operator credential,
configuration, account identifier, message or session is read or copied.
All supplied tokens and account/subject values are newly fabricated constants;
the signature is deliberately not a valid provider signature.

Use the installed source root named in `probe_native_capture_startup.py`,
hash its full bounded manifest before and after the run, and retain exact
fixture bytes, argv/environment, script hash, process receipts and streams.
Provide present inputs through sealed anonymous memory, bind them read-only
outside the writable runtime, and place a literal auth-file symlink inside a
fresh runtime. Verify supplied bytes and refusal of write access before native
execution. Keep the source descriptor alive only for its case. No credential
is inherited as an open descriptor by the native process.

Each case uses Bubblewrap with all namespaces unshared, loopback-only network,
read-only `/usr` and native installation, usable `/dev/null` and `/dev/urandom`,
a private 64-MiB runtime tmpfs and an otherwise read-only root. Use only the
explicit native HOME, CODEX_HOME, PATH and LANG environment. Limit each capture
to five seconds and 100,000 stream bytes. Bound the single owned transient
user unit to 512 MiB, no swap, 64 tasks, 40 seconds and no core files; the
outer capture has 50 seconds and 100,000 stream bytes. Stop on containment or
byte mismatch, write access, incomplete streams, source drift, or failure of
the absent/whole-second controls. Other case outcomes are characterization,
not predetermined successes. No retry allowance.

The existing Revbench payload guard may inspect the same fabricated payloads
with fabricated expected claims for comparison. Preserve its code, contract,
tests and frozen profiles; do not loosen it to match native behavior. No model
selection, prompt, inference call, provider endpoint, login, logout, refresh,
account pool, real credential delivery, historical import/admission, tracker
write, message or push is authorized. Clean only the owned unit/processes and
anonymous descriptors; preserve partial new custody. Verify source manifests,
bounded process outcomes, synthetic input identity, read-only delivery, unit
and cgroup closure. Retain advisory provenance before removing only named
consolidated scratch. Commit only this record locally; authorization expires
at commit. Preserve `docs/designs/` and other worktrees and services.

## Decision and claim boundary

The [local metadata inspection](inspection-2026-09-08-native-serving-metadata.md)
found that the older guard refuses current credential refresh metadata. It
did not preserve that timestamp's shape and does not prove the native client
would reject the credential. The installed npm package declares `0.153.4`;
the older Revbench contract names `0.147.0`. No compatibility is assumed.

Characterize the installed client with synthetic inputs before selecting a
new administration contract. [Official Codex documentation](https://learn.chatgpt.com/docs/auth)
describes `login status` as reporting the active authentication method. A
local status result must not be promoted to provider authentication or account
headroom, especially with fabricated tokens and no network. The controls test
input discovery and parsing; the variants distinguish timestamp and expiry
handling. No change would leave the compatibility issue unresolved; modifying
the old guard before observing native behavior would conflate separate
instrument contracts.

## Probe repair and remaining-case authorization

The absent native control exited 1 with complete streams and `Not logged in`.
Its bootstrap emitted the expected JSON and newline. The private supervisor
then failed because it searched for literal backslash-n instead of a newline.
The same escaping mistake affected the unused present-input serialization.
No present-input case launched. Preserve that script and custody unchanged
under `/tmp/caplab-codex-auth-format-probe.py` and
`/tmp/caplab-codex-auth-format-run/`; the owned unit is unloaded.

Authorize a corrected private `probe-v2.py`, repairing those three newline
literals and checking its serialization/parsing before execution. Read the
already retained absent-control bytes with the corrected parser; do not run
the absent native control again. Authorize one new bounded unit containing
only the four still-unexecuted cases, under the same per-case/unit limits and
stop conditions, at `/tmp/caplab-codex-auth-format-remaining/`. Freeze its
corrected script and input identities before release. Join results only by
their explicit source roots/hashes; retain the initial observer failure.
This completes the original five-case population without replacing an
observed native attempt. No real credentials or provider access are added.

### Correction before the remaining-case run

The newline explanation above was an initial inference and is withdrawn.
AST inspection shows that the frozen script's separator is byte 10, and the
retained stdout ends in byte 10. The script hash still matches its launch
intent. Parsing those same retained bytes with the unchanged helper succeeds.
The proposed three-literal replacement failed its own precondition before
creating v2 or launching anything; the apparent escaping in displayed output
was not evidence of the source bug claimed above. The original supervisor
failure remains unexplained and is not relabeled as a successful run.

Authorize v2 to preserve the existing literal semantics, skip the already
observed absent case, and seal immediate readback byte count/hash and separator
presence before its existing delivery check. Keep that check unchanged. Verify
the existing source's fixture serialization and the retained absent output
before launching the four remaining cases. If the readback failure recurs,
stop with the new diagnostic receipt; no retry of a native case is allowed.

### Anonymous-input handoff correction

The second unit stopped before any present-input native command: Bubblewrap
refused `/proc/<supervisor>/fd/<n>` with `Permission denied`. Its readback
receipt records zero stdout bytes, explaining this missing-delivery failure.
This is a counterexample to the proposed cross-process `/proc` mount route.
Preserve v2 and `/tmp/caplab-codex-auth-format-remaining/`; its unit is unloaded.

Authorize v3 and one final bounded unit for the four still-unexecuted native
cases. A trusted captured launcher creates/seals its own memfd from the fixed
synthetic payload and passes it directly to Bubblewrap `--ro-bind-data` across
exec. Synthetic payload bytes may appear in this private probe's launch argv;
this permission applies only to the fabricated constants and is expressly
not a real-credential delivery design. Keep the bootstrap's exact payload hash,
read-only-write refusal and no-inherited-memfd checks. Require its entire stdout
to parse as the one expected JSON observation, retaining byte/hash readback
before parsing. This preserves the complete-bootstrap requirement without
depending on the unexplained first run's separator check. Do not rerun the
absent native case. Stop and preserve custody on any further infrastructure
failure. No production runtime API or credential guard changes are authorized.

## Final custody correction

Inspecting every retained capture resolves the first failure. In the first
root, `absent/capture.json` records a completed native control, while
`whole-seconds/capture.json` records a subsequent failed Bubblewrap launch.
That launch has empty stdout and stderr reporting `Permission denied` for
`/proc/1277164/fd/3`. The supervisor's separator check therefore failed on the
whole-second launch's empty output, not on the absent control's JSON. Parsing
the absent bytes did not reproduce the failing case. The earlier claim of an
unexplained absent-case readback failure is withdrawn.

The second root records the same mount failure at `/proc/1290197/fd/3`.
Both failed launches remain failed infrastructure observations. Neither reached
the native status command. The final root records the four completed native
status commands using direct inherited `--ro-bind-data` delivery. Across the
three roots there are five native status executions and two failed
present-input infrastructure launches; the absent native control was not
repeated. No further native command was needed for final verification.

## Observations

The selected installation manifest remained unchanged across all three roots
and final verification; its npm package declares Codex `0.153.4`. The fixed
fixtures and the scripts' launch hashes also matched. All five native captures
exited within their five-second bounds and retained complete stdout/stderr.
The following results describe fabricated inputs in isolated offline runtimes:

| Synthetic case | Native status | Existing Revbench guard |
| --- | --- | --- |
| Absent credential | Exit 1; `Not logged in` | Not invoked |
| Whole-second refresh timestamp | Exit 0; `Logged in using ChatGPT` | Accepts synthetic shape |
| Fractional-second refresh timestamp | Exit 0; `Logged in using ChatGPT` | `credential_last_refresh_invalid` |
| Expired ID-token claim | Exit 0; `Logged in using ChatGPT` | `credential_identity_token_expiry_invalid` |
| Invalid refresh timestamp | Exit 1; input-character parsing error | `credential_last_refresh_invalid` |

Every present-case bootstrap observed the exact synthetic input hash, a
read-only write refusal (`EROFS`), loopback as its only network interface,
and no inherited memfd. The final unit observed 512 MiB memory, zero swap,
and 64 tasks as its cgroup limits. Final read-only checks found all three
owned units `not-found` and their cgroup paths absent. No real operator
credential was supplied and no provider authentication or model execution
was performed.

## Inferences and next administration requirement

Native cached-auth recognition and the older Revbench guard have different
acceptance rules for these selected fixtures. A successful native status
result cannot establish provider acceptance: the success cases used deliberately
invalid signatures and fabricated access and refresh tokens, and one carried
an expired ID-token claim. This is a concrete negative control against treating
local status as an authentication gate.

The fractional-timestamp result does not establish the shape of the operator's
actual refresh timestamp; that shape was not retained by the preceding
metadata inspection. These cases also do not establish every format the native
client accepts. No native token refresh, writable auth storage, account capacity,
or authenticated task completion was tested.

A future administration contract must distinguish local parsing, operator
account identity, provider authentication, token refresh effects, and observed
model identity. It must name its current harness version and credential
method before reopening ADR 0063's older contract. Retain the existing guard
unchanged until that decision is made. Passing `login status` alone is
insufficient to release an authenticated study attempt.

Direct inherited descriptor delivery is a demonstrated mechanism for these
synthetic read-only inputs. Its private launcher places fabricated payloads
in argv, so this script is not suitable for real credentials. A production
handoff must keep credential bytes out of argv and retained launch receipts,
preserve descriptor ownership and cleanup, and separately define how native
refresh attempts are handled. The cross-process `/proc` binding mechanism
has two retained counterexamples and must not be assumed to work.

## Advisory provenance and verification

The existing final packet `pkt-b33c7cfd8d9c2c5b`, content SHA-256
`b33c7cfd8d9c2c5b02a47c3ab001917b8e14a46d4029c6fa51c63cac152978a4`,
supported the fixed diagnostic. Its release gate recorded corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, and source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` was rechecked
at closeout. Initial packet `pkt-d3cfda359a9a8ac3` preceded one typed-evidence
pass covering authority, contracts, source, and tests.

All 21 remaining obligations were individually retained as nonmaterial for
this private diagnostic: six concern abstraction/duplication choices that
were not made; ten concern runtime/API/toolchain changes that were not made;
five concern Python special methods or protocol laws that were not introduced.
No material omission is used to justify a production change. Citation closure
classified all four used concepts as valid: `python-structured-cleanup`,
`implementation-risk-driven-tests`, `universal-evidence-before-intervention`,
and `universal-repository-contract-precedence`. Their application was paired
cleanup, discriminating fixed controls, observation before changing the guard,
and preservation of the older contract's authority respectively.

The read-only verifier at `/tmp/caplab-codex-auth-format-verify.py` checked all
ten retained process receipts and their stream sizes, hashes and EOF status;
script, input-selection, source and installation hashes; final report-to-receipt
agreement; synthetic input and isolation observations; original absent control;
both infrastructure failures; and live unit/cgroup closure. Its result is
`/tmp/caplab-codex-auth-format-checked.json`. AST parsing passed for all three
probe scripts; Ruff's undefined-name checks passed for v3 and the verifier.
No repository runtime or tests changed, so the full suite was not rerun.

Private custody manifest `/tmp/caplab-codex-auth-format-verification.json`,
SHA-256 `0867204df5252c90471f5b946a788c0b3f95f7377495e2f2299b28c0dfdc41ad`,
retains 71 artifact identities. Eleven advisory scratch files were embedded
byte-for-byte, verified, then removed. The three original probe scripts,
three execution roots, logs, verifier and verification output remain in place.
Earlier incorrect interpretations and failed launch evidence remain visible.
This record supplies compatibility evidence for CAPLAB-80/84; neither item
is completed, and no reviewer score, ranking, independent judgment, or study
acceptance follows from these probes.
