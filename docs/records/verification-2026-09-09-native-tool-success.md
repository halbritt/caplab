# Exercise a native tool call and completed capture with scripted responses

Baseline `b671c9f`. Primary-agent decision under the continuing CAPLAB goal and
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Decision and authorization before execution

Current native diagnostics cover startup and local 401 failures. The earlier
repair-capture integration uses a trusted Python producer of native-shaped
events. Neither establishes that the installed native harness can execute a
tool request, emit its result and finish a response while CAPLAB retains the
task change, native stream, persisted session and final message together.

Authorize a new private fixed probe derived from
`/tmp/caplab-native-quarantine-probe.py`, recording the source path and hash,
under `/tmp/caplab-native-tool-success-*`, plus this repository record. Preserve
the original probe and all prior captures. Keep all repository runtime, tests,
native policies and frozen study artifacts unchanged. Before executing, freeze
the derived script, synthetic protocol fixtures, canonical native plan, actual
diagnostic command overrides, installation manifest and source identities.

Permit exactly one installed Codex CLI execution in one fresh
`caplab-native-tool-success-<32 hex>.service` unit. Enforce the existing
`native-agent-systems.json` through the canonical `codex-terra-max` invocation
builder. The configured tuple remains native Codex / gpt-5.6-terra / max.
This diagnostic explicitly overrides only the response and refresh URLs to a
private loopback fixture and disables startup update checking. Its responses
are authored protocol stimuli, not provider/model outputs or a comparative
measurement. It selects no proxy subject or exception for an actual study.

The fixed prompt asks for a capture diagnostic. Serve one scripted
`exec_command` function call that writes and reads `capture-witness.txt` in
the initially empty `/work`, using fixed Python source and UTF-8 witness bytes.
Only if the next request carries that exact call ID and witness-bearing tool
output may the fixture serve the fixed completed assistant message. Require
the native request to declare the supported tool. Permit at most two response
POSTs, no more than 32 total requests, and at most 1 MiB per request; record
errors and fail on unsupported shapes. Ancillary requests receive errors;
no real endpoint is reachable. Local transport fallback is within this one
native launch, not a retry allowance for the diagnostic.

Use only fabricated external-token input through sealed memfd and read-only
mounts, no real account/configuration/session read. Preserve the preceding
quarantine factory and exact six-value exclusion. Keep all namespaces unshared,
loopback only, read-only host/native mounts, five private 64-MiB writable tmpfs
mounts and the two required null/random devices. Drop capabilities before
starting the fixture or native client. Keep task, selected-native and full-mount
retention guarded; no completed aggregate may be claimed after any refusal.

Bounds: 256-MiB child memory, no swap, 64 tasks; 512-MiB outer memory, no swap,
128 tasks; 30 seconds native, 45 seconds child capture, 90 seconds unit and
100 seconds outer capture. Preserve 300,000 combined child stream bytes,
1-MiB task bytes/1,000 entries, 8-MiB selected native bytes/1,000 entries,
40-MiB full-mount bytes/2,000 entries and the existing receipt limits. Require
quiescent writers before final retention. Keep outer custody outside the
namespace. Clean only the owned processes/unit/cgroup and anonymous descriptors;
retain complete and partial new custody. No retry under this authorization.

Before the native launch, validate the scripted event sequence and request
guards with synthetic local Python checks. Afterward verify original-source
and installation preservation, exact unit/cgroup removal, task/native/mount
integrity, tool call/result linkage and task/final-message bytes where available.
Native success is a criterion to test, not a promised observation. Any failure
stops the launch sequence and remains a failure record; further execution needs
a new bounded decision. No production credentials, provider access, model spend,
study measurement, historical evidence import/admission/rewrite, tracker write,
message, push, ranking or independent acceptance. Preserve `docs/designs/`,
other worktrees and services. This scope expires at the local record commit.

## Protocol evidence and limits

The official [function-calling guide](https://developers.openai.com/api/docs/guides/function-calling)
defines call IDs, arguments and function-call outputs, including streamed
function-call events. These fields inform the synthetic fixture. The attempted
streaming-reference fetch was unavailable; no successful reference fetch is
claimed for it. The installed client's actual compatibility remains the
diagnostic question. No provider-authenticated identity or response is inferred
from accepting authored protocol events.

## Executed failure and revised next action

The fixed synthetic preflight verified six tool-call events, eight completion
events and five rejected malformed/mismatched requests. An initial preflight
stopped on a typographical error in this record before any native launch; it
was corrected. The frozen probe SHA-256 was
`fb007653cb4edfe02d459438a56bfe57ad6b6afcb32bb7a3a3bccf8f05c4b290`.

One native launch ran in
`caplab-native-tool-success-c804f11d13844662a29e8f98ce6d4f5a.service`.
It did not satisfy the success criteria. Native WebSocket attempts received
the fixture's 405 errors before HTTP fallback. The first two response POSTs
raised `UnicodeDecodeError` in the fixture's assumed UTF-8 body decode. No
request headers or body bytes were retained for these failures, so the actual
content encoding is unavailable. Compression is a possible explanation only.

The POST counter reached 29: the first two decoding errors were followed by
27 count-assertion errors. The handler retained only successfully processed
requests in its total-request list and continued serving after exceptions.
Consequently the intended two-POST bound was not enforced. This is an observed
diagnostic-guard failure, not a compliant bounded exchange or a native model
failure. The native process reached its 30-second timeout and was killed with
return code -9. The wrapper and outer diagnostic exited nonzero. No scripted
tool exchange, task edit or completed native turn was observed.

The namespace remained loopback-only, sealed fabricated auth bytes stayed
unchanged, and no refresh request appears in the retained request list.
That list omits handler failures, so it is not a complete request census.
Source and installation hashes remained unchanged. The `/work` after-inventory
contains only its root. Guarded retention recovered 3,303,087 bytes across
138 full-mount entries. Scanning all 116 retained files and their names found
none of the six configured raw sensitive values; transformed values and other
secrets are outside that exact-value check.

The independent failure verifier rechecked task, selected-native and all five
mount inventories after namespace exit. The wrapper's process/task receipts
verify retention of the failed diagnostic; they do not complete the timed-out
native attempt. A separate root-link attempt failed because bootstrap
`fixture_start`/`fixture_summary` JSON records share stdout with native events
but have no native event type. The captured tool-pair reader likewise reports
the stream unavailable. No filtered stream was substituted to make the original
capture pass. This is another fixture integration defect that precedes any
claim about tool-pair or final-message linkage.

The cleanup receipt and a fresh `systemctl --user show` both report the exact
unit as `not-found`; its named delegated cgroup is absent. No other unit was
stopped. Failed custody remains at `/tmp/caplab-native-tool-success-run/`;
the original and derived probe sources are unchanged. The independent result
is `/tmp/caplab-native-tool-success-failure-verification.json`, with verifier
`/tmp/caplab-native-tool-success-verify-failure.py`. Its first invocation stopped
at the expected root-link refusal; the corrected verifier records that refusal
as unavailable evidence and completes the remaining integrity/cleanup checks.

Before another native attempt, separate supervisor/fixture diagnostics from
native stdout, count all request attempts before decoding, stop the native
sequence on the first fixture failure, and retain bounded content-encoding
observations before choosing a decoder. Validate those paths with synthetic
error cases. Do not guess a codec, raise the request limit or strip records
from an old stream to relabel this attempt successful. A fresh exact scope is
required for any further native launch; none is granted here.

Only this record changes in the repository. No runtime or standing test code
changed, so the full suite was not rerun. The synthetic protocol checks,
actual failed native attempt and subsequent custody checks are the relevant
verification. This supplies evidence about missing capture integration and
changes the next action; it is not representative repair measurement,
CAPLAB-84 completion, provider authentication or reviewer qualification.

## Advisory disposition

The Doctrine release gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-8c61175dfba06d23` was reassembled once with four typed
records binding authority, contracts, source and observed failure. Final packet
`pkt-bf0829fa41124848`, content SHA-256
`bf0829fa411248480b20ad27db2ee6b0f167832484433c2c4dc21368735dd55a`,
uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
Activated concepts, conflicts, authority and prohibitions remained unchanged.

Applied repository precedence, evidence before intervention, bounded authority,
the explicit bytes/text boundary and the distinction between coverage and
adequacy. The passing authored-event preflight did not establish compatibility
with actual request bytes or the multiplexed process stream; the native failure
changed the next action. Preserve that disagreement rather than upgrading the
preflight to a native success criterion it did not exercise.

Five residual obligations are nonmaterial to this failure report: four concern
expanded toolchain/CI/formatter inspection, and one concerns the standing suite.
No repository runtime, supported language facility, dependency or standing test
changed. Fixed-source syntax/static checks, the actual failed native run and
retained-custody verification establish the reported narrow observations;
no new runtime compatibility or successful integration claim is made.

Final private manifest: `/tmp/caplab-native-tool-success-verification.json`,
SHA-256 `665c7b9d7f940d3de17343877afa543e1712ea3f3fa33ddac00e0f4190de5f6f`.
It covers 140 artifacts and 13 unchanged source records, including the exact
failed native custody and pre-execution scope. All typed provenance hashes
matched, and all five citations classified as valid packet citations. Ten
temporary packet/evidence/citation files were embedded byte-for-byte, verified
and removed by exact path. Probe sources, scripts, failures, preflight fixtures,
native custody and verification results remain retained. The final consolidation
again confirmed the named unit unloaded and its cgroup absent.
