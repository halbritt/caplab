# Inspect the native request structure before changing its tool surface

Baseline `32902f8`. Decision owner: primary agent under the continuing CAPLAB
objective and [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Observation and initial authorization

The preceding decoded diagnostic recorded an empty list from the top-level
`document.get('tools', [])`. It did not record top-level keys or distinguish
an absent field from an empty one. Therefore that observation does not establish
that the complete native request contains no tools. Changing shell/model
configuration before resolving this observer ambiguity risks changing the
subject without evidence. Select one bounded request-structure inspection.

Authorize one new private probe derived from the unchanged decoded probe,
preflight and verification artifacts under `/tmp/caplab-native-tool-shape-*`,
and this record. Preserve all predecessor source/custody. Record request shape
with a maximum depth of three and a maximum 200-node budget: object key names,
value types and list counts; inspect the first two list elements and up to
40 fields per object. Retain no string values except tool type/name in actual
`tools` arrays, each bounded to 128 characters and at most 40 tools. Retain
field-presence distinctions, wire/decoded hashes and sizes. All diagnostic
metadata continues through guarded stderr. This is a diagnostic projection;
it cannot prove absence outside its explicitly retained depth/entry bounds.

After synthetic structure and malformed-request preflight checks pass, permit
exactly one installed-native request inspection under a fresh
`caplab-native-tool-shape-<32 hex>.service`. Decode using the verified one-frame
zstd/identity path, retain bounded structure, return an intentional refusal and
stop after the first response POST. Count all native requests before decoding,
stop on first error or 32 requests, preserve 1-MiB wire/decoded body limits.
No scripted response or native tool execution is authorized by this initial
scope. Any further launch requires a prospective amendment after inspection.

Keep the exact canonical native/model/effort plan, prompt, fabricated auth,
loopback-only unshared network, read-only installation/system mounts, five
64-MiB private tmpfs mounts and null/urandom devices. Keep all predecessor
256-MiB child/512-MiB outer memory, no swap, task, stream/file/entry, deadline,
guarded retention, capability-drop and owned cleanup limits. Freeze source,
installed harness and decoder identities before launch. Verify root/stream
linkage, retained custody, unchanged source/install/library, unloaded unit and
absent cgroup. Preserve incomplete outcomes. No real credentials, provider
access, model spend, historical research effect, tracker write, message, push,
repository runtime/test change or independent acceptance. Preserve unrelated
`docs/designs/`, worktrees and services. Authorization expires at local commit.

The official [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
describes shell/unified-exec toggles and request compression. It does not
establish the cause of this observed empty top-level tool list. No toggle
change is selected.

## Structure-inspection preflight

Five synthetic shape checks passed: absent versus empty tools, a nested tool
list, omission of ordinary string values, field/tool/node budgets and depth
truncation. Three actual local HTTP cases passed: compressed nested JSON,
identity-encoded empty tools and malformed zstd. Each stopped after one request
and closed its listener. The final probe hash is
`791b2d884a6bbd81f814651c8b2cd81bde8f0bf7f52b7bea12c651d43cd5187e`.
Both diagnostic prints target stderr. The source decoder and resolved zstd
library still match their previous pins; the library version is 1.5.5.
Ruff F passed. The output projection has a further 64-KiB serialized bound and
one shared 40-tool budget. Proceed with the single authorized inspection.

## Observed request and tool-exchange amendment

The inspection ran under
`caplab-native-tool-shape-5a291281d374495ea3961f3bfe5bc907.service`.
It observed eleven top-level fields and no top-level `tools` field. Its first
input item contains a tools array with two namespace declarations named
`functions` and `collaboration`. This directly demonstrates the earlier
observer's incomplete lookup; it does not establish which functions are
inside those namespaces. The inspection intentionally stopped after its first
response POST with no timeout or handler errors. Native stdout linked to its
retained root and passed tool-pair parsing; the exact unit/cgroup are absent.
Source: `/tmp/caplab-native-tool-shape-inspection.json`.

Authorize a separate derived private probe and one installed-native tool
exchange under `/tmp/caplab-native-tool-namespaced-*` and
`caplab-native-tool-namespaced-<32 hex>.service`. Preserve the completed shape
inspection. Read only tool declarations at `input[*].tools`; require exactly
one `functions` namespace and exactly one function named `exec_command` within
its `tools`. Require an object parameter schema with string `cmd` and numeric
`yield_time_ms` and `max_output_tokens`, and no required arguments outside the
fixed supplied argument set. Record bounded declaration names/types and the
selected parameter schema; refuse missing, ambiguous or incompatible forms.
Do not add a configuration override or substitute another tool if it is absent.

The fixed response names namespace `functions`, function `exec_command` and
the preceding fixed UTF-8 witness-writing command. The second response requires
the exact call ID and actual returned witness output; accept a text string or
an array of text content blocks, and reject other forms. Then emit the same
fixed final message. The native process must exit normally within 30 seconds.
At most two response POSTs; the listener closes after the second successful
response, without treating normal completion as an error. Keep every earlier
network/credential/mount/resource/capture/source/cleanup bound. Validate request
selection, schema refusals and real HTTP response sequencing with synthetic
preflights before this one launch. Verify actual task witness bytes, native
call/result, root/final linkage and custody afterward; preserve any failure.
No third native launch is authorized by this amendment.

This authored response tests the installed harness's capture path. It is not
a provider/model response, comparative subject substitution, study result or
reviewer capability measurement. The official function-calling guide documents
namespace objects containing tool arrays; the actual input-item location here
comes from the installed-native request observation.

## Namespaced preflight

The corrected private fixture passed six schema refusals: top-level-only
lookup, missing function, duplicate function, wrong tool kind, unsupported
required arguments and wrong property types. The actual local HTTP exchange
used namespaced declarations, a compressed first request, exact call identity,
returned text blocks and a second request without repeated declarations. Both
responses and listener closure passed. The fixed command executed locally and
produced the exact UTF-8 witness file. An unused preflight import was removed;
Ruff F then passed. Final native probe hash:
`bee81ebbe3bb4b46943d7360668b5c5c3b2e63c930beb96f7bafc68404ae1b3f`.
The source decoder and installed library match their frozen hashes. Proceed
with the one namespaced native diagnostic; no tool-availability or execution
success is inferred from these synthetic checks.

## Namespaced refusal and separate code-mode authorization

The namespaced attempt ran under
`caplab-native-tool-namespaced-d9fd2d8a14a747598936dfd3c5c61fc8.service`.
The actual namespace declares custom `exec`, function `wait` and function
`request_user_input`. It does not declare a direct `exec_command` function.
The fixed schema check refused before sending a response, after one response
POST and 24 requests, with no timeout. Native return code -9 is the owned stop.
There was no tool execution, task change or final message. Root and tool-pair
parsing passed; full-mount custody reverified 3,303,087 bytes in 138 entries.
The 116 retained files contain none of the six configured raw synthetic values.
Sources, installation and decoder remained unchanged; unit/cgroup are absent.
The failure verifier is `/tmp/caplab-native-tool-namespaced-verify-failure.py`.
The prior amendment's single tool-exchange allowance is consumed.

Under ADR 0026, separately authorize one code-mode diagnostic derived from that
preserved source under `/tmp/caplab-native-tool-codemode-*`, unit
`caplab-native-tool-codemode-<32 hex>.service`. This new prospective scope follows
the observed native declaration; it does not reinterpret the failed attempt.
Require exactly one declared custom tool `functions.exec`, with a string
description no larger than 64 KiB containing the exact `tools.exec_command`
reference. Retain its content hash and declared format; refuse otherwise.
Send one custom tool call with fixed JavaScript that awaits precisely one
`tools.exec_command` using the already fixed witness-writing command, then
prints the returned value through `text`. No collaboration or dynamic tool
selection. Require its exact custom-call ID and witness-bearing actual output
before the final message. Verify actual task bytes and native call/result;
fixture text alone cannot establish execution.

Keep the native command, model, effort, flags and all previous isolation,
resource, capture and cleanup limits. This uses the harness's declared code
execution interface; it adds no SDK, proxy or replacement harness. Before the
single launch, test the custom-call response sequence, declared-tool refusal
and fixed JavaScript against a synthetic executor that actually runs the
command. Preserve the preceding two attempts unchanged. No fourth native
launch is authorized by this record. Any failure closes this diagnostic with
its exact remaining gap; it cannot be relabeled as a successful capture.

## Code-mode preflight

Five declaration refusals, wrong call/output refusals and the two-response
compressed HTTP sequence passed. Node executed the exact fixed JavaScript
against a synthetic one-call executor which ran the real shell command and
checked its exact UTF-8 file. This tests authored JavaScript, not the native
code-mode host. Ruff F passed. Final native probe hash:
`2903dac125dd4ba0c6c673a555fa80db804f9c806f3fed62bc1092f6081849fc`.
Source decoder/library pins remain unchanged. Proceed with the single newly
authorized code-mode diagnostic.

## Code-mode observation and remaining gap

The code-mode attempt ran under
`caplab-native-tool-codemode-f8ca4bc5e646418e9362b6238010f564.service`.
The actual custom tool description declared `tools.exec_command`; its complete
selected declaration had content hash
`a8e670594bc359f55ffe5fbf3e4ca79e84bf0164b5df9e0aec95a78a80035de5`.
The observed format is the native Lark grammar for plain JavaScript with an
optional exec pragma. The fixture sent one scripted custom-call response.
The retained native rollout contains that exact namespace/name/call-ID/input.
However, it contains no custom-tool output, the task is unchanged, the final
message file is absent, and no second response POST occurred. The native
process exited zero with no timeout or handler error. The wrapper correctly
failed the frozen requirement of a completed two-response tool exchange.
Exit zero and retained call text do not establish tool execution.

The private verifier `/tmp/caplab-native-tool-codemode-verify-failure.py`
rechecked actual call bytes, missing output/final/task changes, process/task/
native/full-mount custody, root and tool-pair parsing, source and library pins,
unchanged installation, unloaded unit and absent cgroup. Full-mount retention
contains 3,419,990 bytes in 138 entries; 116 retained files contain none of the
six configured raw synthetic forbidden values. The empty stdout tool groups
remain a bounded observation and do not erase the retained custom-call record.

All three launch allowances in this record are consumed; no fourth launch
occurred. The next investigation must establish how this native code-mode
harness dispatches an authored response item, including its required response
metadata and lifecycle. This record does not select a guessed metadata repair.
It supersedes the inference that the native tool surface was empty: the earlier
fixture checked the wrong location and then the wrong tool kind. Preserve both
failed probes and their original records; this new evidence supplies the correction.

## Doctrine and final claim boundary

The validated release gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-7a0678d1955aa7c7` was reassembled once with five typed
records. Final packet `pkt-0a53609338714e95`, content SHA-256
`0a53609338714e951df132be7fcf2d45115d1b78c6debf511d5b5fe3ed872a13`,
uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
The final packet was inspected, including its changed activations. Applied
bounded authority, repository precedence, evidence before intervention,
separate repair/structural changes and preservation of existing behavior.
The AI Failure Modes checks focused on guessed interfaces, plausible but wrong
field lookup, exact literal execution and false success from a zero exit code.

Thirty-two unmet obligations remain explicit. Eighteen about deduplication,
bulk-ingest population, async UI, relevance ranking and service paging are
nonmaterial because those surfaces do not change. Three general configuration
reference obligations are nonmaterial to the narrow declaration observations:
no native configuration changed, and the required runtime declarations were
checked before sending. The eight external-capability and authoritative-gate
obligations remain material to a working-integration or production-readiness
claim; those claims are withheld. Three general no-change obligations are
nonmaterial to this bounded outcome record: no product runtime change or
optimization recommendation is made. The verified correction concerns the
observer's lookup; complete native tool execution remains unverified.

No standing runtime/test source changed. Private preflight, actual native
observations and integrity/cleanup checks verify this scope; no new full suite
was required. No provider/model spend, real credential access, historical
research effect, tracker update, message, deployment or push occurred. The
continuing CAPLAB goal and CAPLAB-84 remain incomplete.

## Final custody

Private manifest `/tmp/caplab-native-tool-shape-verification.json`, SHA-256
`43d746b404408b34f6a6545e851781d1e6f334bb63125bd0f6c33fc2aa113bbc`,
covers 382 retained artifacts and 13 unchanged source records. All typed
provenance hashes matched; five doctrine citations classified as valid packet
citations. Eleven temporary packet/evidence/citation files were embedded,
verified byte-for-byte and removed by exact path. Native/preflight source,
logs, source snapshots and all three capture roots remain retained.

Commit this record only. Preserve `docs/designs/`, other worktrees and services.
