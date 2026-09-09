# Investigate the scripted native transport failure

Baseline `fd66de7`. Primary agent under ADR 0026 and the continuing CAPLAB goal.

## Observation and initial authorization

The current local fixture implements response POST/SSE but returns 405 for
response GET/WebSocket requests. Retained native attempts show four WebSocket
retry errors and a fallback error before a completed fixed tool exchange.
Strict final-message linkage rejects that stream. The last timed attempt spent
23.334 seconds before its first response POST and failed its 30-second native
deadline. This does not establish that transport retries caused the timeout.

The current local launch profile is closed and versioned. An added harness
setting would change effective configuration and cannot silently replace it.
The installed binary contains responses_websockets and responses_websockets_v2;
presence of strings alone does not establish supported configuration behavior.
Official configuration documentation describes provider supports_websockets,
but does not establish an applicable built-in provider override for this binary.

Authorize read-only inspection of current sources, prior retained diagnostics,
official transport documentation and the installed binary. Permit at most two
isolated `features list` metadata commands, baseline then explicit false values
for those two feature flags, using the installed binary directly. No agent
`exec`, model request, real credentials or host configuration. Use a fresh
empty HOME/CODEX_HOME on private tmpfs, unshared network and other namespaces,
readonly binary/system mounts, 512 MiB address-space and 2 MiB file limits,
no cores, ten-second deadline and 100,000-byte capture. Record binary hash,
commands, output and exit. Stop on unexplained failure without retry.

Retain this record and private `/tmp/caplab-native-transport-*` artifacts. Do not
change runtime, tests, launch profiles, fixture protocol, native limits, prior
evidence or tracker state in this initial inspection. Any material follow-up
requires its exact scope here before execution. Preserve unrelated docs/designs,
worktrees and services. No provider spend, historical research processing,
messages, push or independent acceptance. This authorization expires at the
local record commit. The broader capture and representative repair requirements
remain open.

## Metadata outcome and fixture decision

Both metadata captures exited zero with complete streams and empty stderr.
Both list responses_websockets and responses_websockets_v2 as removed/false,
with or without explicit false settings. Do not add these flags to a profile.
This observation does not test every possible provider override.

Select a fixed WebSocket fixture using the existing native launch configuration.
The official WebSocket guide describes response.create, optional generate:false
warmup, and continuation through previous_response_id. Implement only the bounded
local fixed exchange, including explicit warmup lineage and two generated
responses. Preserve the existing tool JavaScript, witness and final response
payload. A local fixture is protocol evidence, never provider inference.

Authorize acquiring exactly websockets 15.0.1 from PyPI into a fresh private
`/tmp/caplab-native-transport-deps` target, without modifying repository or host
dependencies. Retain distribution URL, PyPI hash, downloaded wheel and installed
file hashes; refuse unexpected dependencies. Use the library's synchronous
server with compression disabled, bounded message size/queue, bounded receives
and explicit shutdown. Build and exercise the fixture under this private prefix
with constructed clients only. Test the exact exchange, warmup, missing/wrong
lineage, wrong tool result, duplicate/extra messages, malformed/oversized input
and cleanup. Keep at most one admitted WebSocket, two generated responses,
one optional warmup, one MiB per message, bounded total input, and a fixed
deadline. Unsupported HTTP response transport must fail visibly.

This stage authorizes no installed-native agent attempt or repository runtime
change. A native adoption requires separate prospective authorization after
the fixture checks pass. A manually implemented WebSocket frame codec would
add avoidable protocol risk; a private pinned library keeps that responsibility
outside the fixed application exchange. No inference about its security or
native interoperability follows from choosing the library.

Before implementation, select the library's asynchronous server lifecycle
instead of the synchronous wrapper. Inspection of the pinned synchronous source
shows that its server does not track connection threads for shutdown; the async
server supplies close/wait_closed over accepted connections. Use one event loop,
compression disabled, max_size one MiB, max_queue two, two-second handshake,
one-second close timeout, no keepalive, and at most 30 seconds for the fixed
exchange. Tests may shorten that deadline to verify timeout refusal. This
changes only private fixture implementation, with the same permitted effects.

## Execution and control results

The pinned universal wheel is SHA-256
`f7a866fbc1e97b5c617ee4116daaa09b722101d4a3c170c787450ba409f9736f`.
Its downloaded bytes agree with the PyPI distribution metadata; the metadata
declares no dependencies and lists no vulnerabilities. That listing is not a
security audit. Sixty installed files are hash-verified in the private target.
Neither repository dependencies nor host installation were modified.

The private fixture is `/tmp/caplab-native-transport-fixture.py`; its controls
are `/tmp/caplab-native-transport-tests.py`. The first test failed before the
fixture existed. Subsequent controls exposed warmup incorrectly generating a
tool call, invalid messages reaching response generation, and a second socket
being admitted. Each failure log is retained, with its subsequent passing run.

Eight final test methods pass over actual loopback WebSockets. They verify:

- The two generated event sequences equal the previous fixed SSE payloads after
  decoding the SSE envelope; tool JavaScript and final text are unchanged.
- Optional warmup returns an empty output and an ID. The first generated call
  uses that ID and the retained warmup input. Repeated or late warmup is refused.
- Wrong/missing response lineage and wrong tool call ID/output cannot receive
  the final response. A third generated response is refused.
- Wrong event type, nonboolean generate, duplicate JSON keys, nonfinite JSON,
  binary messages, malformed JSON and an oversized message emit no response.
- A second WebSocket receives 409 before message processing. The health route
  returns its exact fixture body, and an unknown path returns 404.
- Timeout and early close remain failed exchanges. Closing the fixture with an
  active client closes its socket and listener; the test's descriptor set is
  restored and a subsequent connection to that port is refused.

At most three application messages are retained by the handler; an additional
message causes refusal. This bounds accepted JSON input to three MiB, separate
from library framing, handshake buffers and any final refused message. The
HTTP request callback retains at most 32 parsed requests. It is not a claim
that malformed pre-handshake traffic is counted there or that this fixture is
suitable for untrusted network service. Native adoption still requires the
existing isolated namespaces and outer resource/deadline controls. Ancillary
HTTP POST compatibility has not been established; this stage exercises the
WebSocket exchange and GET health/refusal paths only.

`/tmp/caplab-native-transport-controls-verification.json` verifies two metadata
capture receipts, identical feature-list stdout, empty stderr, all 60 installed
dependency file hashes, eight unchanged payload AST fragments and eight current
repository source identities at `fd66de7`. Ruff F passes for fixture, payload
and controls. No repository runtime or test changed, so no full-suite rerun.

Source references are the [official WebSocket guide](https://developers.openai.com/api/docs/guides/websocket-mode),
[Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference),
and [websockets 15.0.1 async server API](https://websockets.readthedocs.io/en/15.0.1/reference/asyncio/server.html).
Direct downloading of the OpenAI Markdown page returned HTTP 403; the fetched
web-tool response is retained instead. This documentation-fetch failure caused
no experiment retry. Native interoperability, strict native final-message
linkage, native timing and capture completeness remain unverified.

## Advisory review and next evidence

The Doctrine retrieval gate verified fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`
at release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Initial
`pkt-f2f2ebb1530d3993` and final `pkt-4bb5cce0d3f0d62b` were read as Markdown.
The final content SHA-256 is
`4bb5cce0d3f0d62b551f975759a9d04a4f45c80a04c737e3c3aa8a0b4c66ba18`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`.
Five typed observations cover authority, incident, source, tests and runtime.
Five citations classified as valid: repository contract precedence, evidence
before intervention, authority-bounded action, preserving behavior, and keeping
semantic work separate from structural work.

All 28 residual obligations remain explicit. Deduplication (3), input population
discovery (4), asynchronous UI (4), declarative references (3), ranking (4)
and operational monitoring (3) are nonmaterial to this private fixture and
unchanged product surfaces. External capability (3) and readiness-gate authority
(4) remain material to native adoption and broader capture claims. Those claims
are withheld; the current result establishes only the tested local protocol.

The next execution must mount the pinned private fixture dependency readonly,
preserve the effective native command/environment, guard, ordinary tracing,
containment and limits, and retain actual WebSocket request shape and lineage.
Before any native release, reconcile ancillary HTTP handling and run the guard
controls. Freeze exact source hashes and an attempt allowance. Require normal
native completion, exact task and final bytes, strict failure-free linkage and
owned-resource cleanup; a failure consumes the allowance and remains failed.
Neither the successful local fixture nor this statement authorizes that attempt.

## Final custody

Manifest `/tmp/caplab-native-transport-verification.json`, SHA-256
`32933ed063ac4e11f651979d1d29c5abedf449a8a00ab4e7102cd4f3abd19648`,
retains 97 artifacts and 11 unchanged repository source identities. Eleven
advisory scratch files were embedded byte-for-byte, checked and removed by exact
path. Artifact, source and typed-provenance hashes agree. Private fixture,
controls, dependency wheel/installation, metadata outputs and failed/passing
logs remain retained. The local record commit closes this stage's authorization.
No native agent task, model spend, tracker write, push or independent acceptance
occurred. The broader CAPLAB goal remains active.
