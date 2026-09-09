# Repair the native diagnostic request and stream boundaries

Baseline `43eae6f`. Primary agent under the continuing CAPLAB goal and
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Initial authorization

Preserve the failed source and custody named in
[the preceding diagnostic](verification-2026-09-09-native-tool-success.md).
Authorize a new fixed private probe, preflight tests, source snapshots and
verification records under `/tmp/caplab-native-tool-transport-*`, and this
repository record. No repository runtime or standing test change is selected.
Record exact derivation source and hashes before creating the new probe.

Move fixture diagnostic JSON to stderr, leaving native stdout unmodified.
The native stderr remains mixed with explicitly named fixture diagnostics;
this does not claim a separately authenticated supervisor channel. Verify
unambiguous diagnostic records, and never filter an old stdout to claim it
passed native linkage. Count every accepted native request before reading or
decoding its body. A single-threaded request loop stops accepting requests on
the first fixture error, at 32 native requests, or after two response POSTs.
The parent stops the native process promptly on fixture error; the fixed outer
deadline remains a separate bound. Validate these paths with synthetic HTTP
clients, including malformed requests and connection attempts after refusal.

Authorize exactly one new installed-native **request-format inspection** after
those preflight checks pass, under a fresh
`caplab-native-tool-transport-<32 hex>.service` unit. It retains the first POST's
Content-Encoding, Content-Length and Transfer-Encoding fields, wire byte count,
hash and first eight wire bytes as hex, then deliberately refuses the request
and stops. It does not decode or serve a scripted tool response. This identifies
the actual transport without guessing a codec. No additional native allowance
is granted by this initial scope.

Use the same canonical `codex-terra-max` plan, fixed diagnostic prompt,
fabricated external-token fixture, guarded memfd delivery, loopback-only
namespace, read-only installation/system mounts, five private 64-MiB tmpfs
mounts and two usable devices as the preceding probe. Preserve the explicit
local response/refresh URL overrides and disabled update check. Freeze the
derived source, installation manifest and source identities before launch.

Keep 256-MiB child memory/no swap/64 tasks, 512-MiB outer memory/no swap/128
tasks, 30-second native deadline, 45-second child capture, 90-second unit and
100-second outer capture. Preserve all earlier stream/task/native/mount byte,
entry and receipt allowances, capability drop, quarantine, quiescent retention
and exact cleanup ownership. The first POST is an intentional stopping
observation, not a successful tool/model response. Keep timeout, protocol error,
planned stop and incomplete native capture distinct.

No operator credential/configuration/session read, provider access, model spend,
study measurement, historical research import/admission/rewrite, tracker write,
message, deployment, push or independent judgment. Keep the configured native
tuple separate from authored fixture responses. Preserve unrelated files,
`docs/designs/`, worktrees and services. Stop after the one inspection, retain
all failures and verify unit/cgroup removal. Further decoding or native
execution requires a prospective amendment after this observation. Authority
expires at the local record commit.

## Request-format observation and decoding amendment

The synthetic HTTP preflight passed four cases: a binary POST retained its
format metadata and stopped; duplicate encoding and oversized length stopped
on the first request; 32 ordinary requests exhausted the budget and closed
the listener. Each check confirmed that another connection could not be
accepted. Static inspection confirmed both diagnostic prints target stderr.
An unused import in the standalone preflight helper was corrected before
native execution; the native probe source was unchanged by that correction.

The one native inspection ran under
`caplab-native-tool-transport-b1b8557e64e04d8f9fa5e75979e59c76.service`.
Its first response POST explicitly declared `Content-Encoding: zstd`,
`Content-Length: 21516`, no Transfer-Encoding, and began with wire prefix
`28b52ffd00581da0`. The 21,516 observed bytes had SHA-256
`8340e284b40edefe68dced21fe6568d7fe5c53598bead512c2e2043120618abf`.
This is now an observed encoding for this request. It does not retroactively
identify the unretained encoding of the preceding failed attempt.

The fixture stopped after that one POST, with no handler error or timeout;
the native process was intentionally killed with return code -9. Pure native
stdout now passes root linkage and tool-pair parsing. Those parsers do not
complete the intentionally stopped native attempt. Task/native/mount custody
reverified, and the exact unit is unloaded with its cgroup absent. Retained
observation and linkage: `/tmp/caplab-native-tool-transport-inspection.json`.

Authorize a second derived private probe and one new native tool diagnostic
under `/tmp/caplab-native-tool-decoded-*`, with unit name
`caplab-native-tool-decoded-<32 hex>.service`. Preserve the inspection probe
and its custody unchanged. Keep its request-counting, stop-on-error, stderr
diagnostics and all namespace, quota, timing, credential and cleanup limits.
This is a separate allowance after the completed inspection, not a retry of
that intentionally stopped attempt.

Support only absent/identity encoding and an explicitly declared single zstd
frame. Bound both wire and decoded bodies to 1 MiB, reject concatenated/trailing
frames and malformed input, then decode UTF-8 and parse JSON. Use the installed
`libzstd.so.1` through its stable simple API, with exact ctypes signatures and
a fixed 1-MiB destination buffer. Freeze the resolved library file hash and
reported version before launch. No package installation or decoder fallback.
The [Zstandard manual](https://facebook.github.io/zstd/zstd_manual.html) specifies
destination capacity, error results and first-frame compressed-size inspection;
local synthetic checks must establish actual behavior for this installed library.

After synthetic codec/HTTP/error-path checks pass, serve the preceding fixed
scripted `exec_command` and final-message sequence. Require the declared native
tool, exact call ID and witness-bearing tool output before sending completion.
Accept at most two POSTs; stop the listener after the second, and do not treat
that normal listener completion as a fixture error. The native process must
finish normally within the unchanged deadline. Preserve failed/missing tool
results; do not manufacture task writes or tool responses in the fixture.

Verify retained task witness bytes, native call/result and final message,
root/final-file linkage, full guarded custody and exact cleanup. It remains
scripted capture plumbing, not a provider response, model repair measurement,
complete Binding, representative resource estimate or study qualification.
No third native launch is authorized by this amendment.

## Decoded-probe prelaunch verification

The decoded preflight actually executed the fixed shell command and checked
its stdout and file against `CAPLAB café tool witness` plus a final newline.
That exposed two inherited literal defects before any decoded native launch:
a literal backslash-n witness and shell quoting that would produce invalid
Python. The derived probe now uses an actual newline and `shlex.join` to
construct the command. The old fixture source remains unchanged; the final
literal correction and source hashes are retained in the derivation record.

The installed zstd library reports 1.5.5. Its resolved file, the final probe,
handler and preflight result are frozen in
`/tmp/caplab-native-tool-decoded-prelaunch.json`. The final probe hash is
`a181648bb69231956d10e83e7f1e73bad01095ae33e54f3182b3711fd25772ec`.
Synthetic checks passed exact 1-MiB wire/decoded boundaries and seven codec
refusals. Five actual local HTTP cases covered the two-response success path,
malformed compression, unsupported encoding, invalid UTF-8 and decompression
beyond the bound; each listener closed. Ruff F passed on all three files.
These checks verify the private fixture, not installed-native tool execution.
The earlier inspection unit and cgroup are absent. Proceed with the one
separately authorized decoded native diagnostic.

## Decoded native observation

The one decoded diagnostic ran under
`caplab-native-tool-decoded-6898c45bc3d648b7adeca643dcc31ded.service`.
It failed its tool-exchange criterion. The first response POST explicitly
used zstd; 21,536 wire bytes decoded into 61,110 UTF-8 JSON bytes. The fixture
recorded an empty declared-tool list, then its required `exec_command` check
raised AssertionError. No scripted response was sent. The fixture stopped
on that first error after 24 total accepted native requests and one response
POST. Native return code was -9 from the owned cleanup, with no timeout.
This establishes successful bounded decoding and fail-stop behavior for this
request, not why the native tool list was empty.

The native stdout linked to its retained rollout and passed tool-pair parsing,
with no tool groups and no completed turn. Task capture recorded no changes;
the final message file is missing. Complete wrapper streams and task retention
do not establish a complete native attempt. No tool witness or model response
was produced. All five mount inventories reverified: 3,303,085 retained bytes
in 138 entries. A scan of 116 retained files found none of the six configured
raw synthetic forbidden values; this is not a transformed-secret guarantee.

The private verifier `/tmp/caplab-native-tool-decoded-verify-failure.py` checked
process/task/native/full-mount integrity, root linkage, tool parsing, source
hashes, the unchanged native installation and the pinned zstd library. The
exact unit is unloaded and its delegated cgroup is absent. Verification is
retained in `/tmp/caplab-native-tool-decoded-failure-verification.json`.
Both recorded native allowances are consumed. No third launch occurred.
The next investigation is the selected native tool surface; changing it must
be recorded as a diagnostic configuration change and must not silently redefine
a comparative subject.

## Doctrine and bounded conclusion

The release retrieval gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-9ed6bc9ab64bff47` was reassembled once with five typed
evidence records. Final packet `pkt-de2f074cc659f15a`, content SHA-256
`de2f074cc659f15a166fb58c187c5cf08050ebc74e73598f68412c9d4309981b`,
uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
Reassembly changed activated concepts; its complete packet was inspected.
Repository precedence, bounded authority, evidence before intervention,
separation of repairs from refactoring and preservation of existing behavior
remain the applied guidance. The AI Failure Modes pass checked failure
propagation, actual API availability, literal correctness, resource ownership
and the risk of treating an authored fixture as a real model response.

The final packet retains 32 unmet obligations. Eighteen concerning deduplication,
bulk-ingest discovery, async UI states, relevance ranking and operational paging
are nonmaterial: none of those surfaces changes here. Three concerning general
configuration-reference validation are nonmaterial to the recorded transport
observations; a declaration-compatible native tool configuration remains an
explicit next investigation, not a verified integration. Four external-system
verification obligations and four authoritative-gate obligations would be
material to claiming working provider integration, production parity or full
capture readiness. Those claims are withheld. The actual installed-native
request, retained stdout and custody verifiers support only the named local
observations. The remaining three no-change obligations are nonmaterial to
this retrospective diagnostic conclusion: leaving the failed fixture unchanged
would preserve its observed quota/decoding defects; the private experiment
changes no product API and makes no cost-benefit or roadmap-completion claim.

No standing runtime or test source changed, so a new full repository suite was
not required. Private preflight, source/installation/library checks and actual
native failure/custody verification cover the selected effect. No provider
request, model spend, historical research processing, tracker update, outbound
message or push occurred. The continuing CAPLAB objective remains incomplete.

## Final custody and local commit

The final private manifest is
`/tmp/caplab-native-tool-transport-verification.json`, SHA-256
`b61a6280dcfa927df61e2960ada5292c1f1d49f1e52f6ea3e2c4dc49409d9682`.
It covers 257 retained artifacts and 13 unchanged source records. All typed
evidence provenance hashes matched, and five doctrine citations classified
as valid packet citations. Eleven temporary packet/evidence/citation files
were embedded byte-for-byte, verified, then removed by exact path. Probe
sources, source snapshots, preflight results and both native capture roots
remain retained. No diagnostic source changed after its native execution.

Commit this record only. Preserve unrelated `docs/designs/`, sibling worktrees
and services. The request-transport diagnostic is closed with a verified
remaining tool-surface failure; it does not complete CAPLAB-84 or the roadmap.
