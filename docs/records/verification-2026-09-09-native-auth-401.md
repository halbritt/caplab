# Observe native authentication handling of a local 401

Baseline: `d7b2467`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization and subject boundary

Authorize a private fixed diagnostic under `/tmp/caplab-auth-401-*` and this
record. The subject is the installed Codex CLI's authentication failure path
against a synthetic local HTTP fixture, not model capability or a provider
Binding. Keep native CLI exec, the contract's `codex-terra-max` model/effort
arguments, and explicit diagnostic endpoint changes; do not use app-server,
a generic SDK, a real provider, or any other model. Enforce the native-agent
contract before constructing the derived diagnostic argv. No score, native
study evidence admission, reviewer ranking or representative repair claim.

Authorize one new owned unit with two sequential cases: external-token mode
with empty refresh string, then managed ChatGPT mode with a fabricated refresh
token. Use only newly constructed synthetic fields from the preceding probe
source; read no actual credentials, account metadata, operator configuration
or historical experiment payloads. Prompt: `Authentication diagnostic only.
Reply READY without using tools or changing files.` No actual inference
response is served. No native retry allowance.

Each case creates a private Bubblewrap network/user/PID/mount namespace with
only loopback, read-only `/usr` and native installation, required null/random
devices, a read-only sealed synthetic auth input and a 64-MiB writable runtime.
A trusted bootstrap may temporarily use CAP_NET_ADMIN solely to raise its
private loopback interface. Before starting the fixture server or native
child, clear effective/permitted/inheritable capabilities, set no-new-privileges,
and verify those observations. Verify no inherited input memfd and read-only
auth write refusal. No host network namespace, external network interface,
operator home or credential path is mounted.

The local server binds only 127.0.0.1 on an ephemeral port inside that namespace.
It serves 401 for response requests, 400 `invalid_grant` for `/oauth/token`,
404 for unrelated paths and a separate preflight route. It provides no model
answer or successful refresh. Requests are limited to 1 MiB each and sixteen
observations per case, with two-second socket timeouts. Retain method/path,
response status, body hash and synthetic credential-match booleans, not new
provider evidence. A local preflight must verify HTTP reachability before
launch. Fixture endpoint and refresh override are explicit in native argv/env.

Use a unit with 512 MiB memory, zero swap, 64 tasks and 80 seconds total.
Each native child has twenty seconds, its outer capture thirty seconds and
300,000 combined bytes; the unit capture has ninety seconds and 100,000 bytes.
Core files are forbidden and runtime file size is limited to 2 MiB per file.
Freeze script, fixture, installation manifest, native policy and selected
runtime source hashes before release. Preserve bounded process streams and
final fixture/native observations. Any native timeout, incomplete capture,
fixture error, containment/integrity failure or cleanup failure stops later
cases; preserve custody without retry. A complete native nonzero exit is the
expected error-path outcome. Require an observed response 401 before drawing
a 401-path inference. Lack of a managed refresh observation prevents treating
the override as a working positive control.

Stop and unload only the owned unit; verify its cgroup disappears and sources
remain unchanged. Preserve repository runtime, native policy, old credential
guards, historical custody, `docs/designs/`, other worktrees and services.
No tracker write, provider request, real token refresh, message, push or
configuration change. Retain verification/advisory provenance and commit this
record locally; authorization expires at commit.

## Source observations and hypothesis

The preceding [cache-format inspection](inspection-2026-09-09-native-credential-lifecycle.md)
found that `chatgptAuthTokens` with an empty refresh field is accepted by local
status. It did not establish native exec behavior. The installed public binary
contains `CODEX_REFRESH_TOKEN_URL_OVERRIDE`; this is a candidate fixture hook,
not yet verified behavior. The [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
describes `chatgpt_base_url`. Both overrides will be exercised only against
loopback within the private namespace.

Compare actual local requests and terminal native diagnostics for external
versus managed cache fixtures. The managed case tests whether a refresh attempt
can be observed through the fixture; the external case tests whether that same
401 path attempts refresh without a refresh credential. No observation here
can establish every refresh path, real credential validity, service capacity,
or safety of a concurrent operator cache. The alternative of relying on login
status leaves those questions unanswered. A real-provider experiment would
add credential and remote effects before this local uncertainty is resolved.


## Execution observations and failed criterion

The single owned unit started on September 9 at 00:30:11 Pacific. Only the
external-token case launched. Its native child exceeded the fixed twenty-second
limit and was killed with SIGKILL (return code -9). The bootstrap and supervisor
both exited 1, and the managed-token case did not start. No retry occurred.
The successful final observations document was not written. The failure is
retained at `/tmp/caplab-auth-401-native/`, including both complete launcher
stdout/stderr captures; complete launcher streams do not establish native
completion.

The bootstrap observed loopback as the only interface, exact sealed input
SHA-256 `eb81107db3ccf0fc13ed06f41ab036e548a7d89b3a7b1b7425bea2fecbf4b25b`,
read-only write refusal, no inherited input memfd, zero effective/permitted/
inheritable capabilities and no-new-privileges. The local HTTP preflight passed.
Its final summary recorded unchanged auth bytes and no fixture-handler errors.

The fixture recorded fifteen requests, all returning 404. Their paths concerned
plugins, MCP, analytics and user settings. Twelve had the exact fabricated
access-token Authorization header; the three MCP requests did not. No local
response-path request or `/oauth/token` request occurred, so no response 401 was
observed. No request body contents or credential values appear in the retained
native output; only body hashes/counts and fixture-match booleans were recorded.

Native stderr recorded two WebSocket connection failures naming
`wss://chatgpt.com/backend-api/codex/responses`, each reporting name-resolution
failure. The native argv had the selected local `chatgpt_base_url` and the
environment had the local refresh override. Thus this configuration directed
ancillary HTTP traffic to the fixture but did not redirect the observed
WebSocket response path. The namespace had no external network interface or
host resolver mount. No provider response or model output was obtained.

This is a failed diagnostic setup, not an observed authentication rejection or
no-refresh policy. The twenty-second bound expired before the intended 401
condition was reached. Because the managed case was correctly stopped, the
refresh override also lacks a working positive control. The observations do
not distinguish later HTTP fallback, another configuration key, or a separate
WebSocket route as the necessary correction.

## Disposition and verification

Do not adopt the external cache representation for real credentials. The next
useful investigation is the native response endpoint and transport configuration
for this installed version, followed by a newly frozen diagnostic only if its
request path can be directed to the local fixture. Do not remove network
isolation, infer safety from absent refresh requests, silently switch to an
app-server or proxy subject, or extend this consumed attempt's timeout.
The current authorization permits no further native launch.

Unit `caplab-auth-401-3b496e5aed254d2eb995cd424d858c31.service` was collected;
the subsequent exact-unit stop returned 5 because it was already absent.
The recorded and fresh load-state reads both returned `not-found`, and a fresh
read of the owner's user cgroup tree found no matching unit. No other unit was
stopped. The frozen probe is `/tmp/caplab-auth-401-probe.py`, SHA-256
`700e30fa467446320d304aaf37198b583951866c5797b456d1a6dd48c3ad36fe`; its embedded bootstrap matches
`/tmp/caplab-auth-401-bootstrap.py` exactly.

The separate read-only `/tmp/caplab-auth-401-verify.py` checked the frozen
script, fixture selection, selected runtime/policy hashes and full selected
native installation manifest; all matched. It checked both launcher receipts
against stream sizes/hashes/EOF, the one start/summary pair, input identity,
capability and read-only observations, timeout evidence, fifteen-request
population, absent managed-case launch, absence of synthetic token values in
invocation/capture, and current unit/cgroup closure. Its result is
`/tmp/caplab-auth-401-checked.json`. This verifies retained failure evidence and
cleanup; it does not convert the failed diagnostic into a successful probe.

Private scripts passed AST parsing and Ruff's undefined-name/unused-import
checks. Repository runtime and tests were unchanged, so the full suite was not
rerun. The latest runtime baseline remains the preceding 1,252-test run with
four skips. CAPLAB-80/84 remain incomplete; this result supplies no reviewer
measurement, account capacity, model ranking, independent judgment or study
acceptance. No tracker change, real credential access or provider execution
occurred.

## Advisory provenance

Pincite's validated release gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
Initial packet `pkt-ea6240c3b033923f` preceded one typed-evidence pass covering
authority, contracts, inspected private/native invocation source, and existing
descriptor tests and cache-format observations. Final packet
`pkt-8d80886c1415a0ba` has content SHA-256
`8d80886c1415a0ba17c3b7b47fce3b51738be6b8e09b883e339c7d29416708f6`. Its full Markdown was read before launch.
It contains baseline/routed guidance, not a precisely nominated authentication
concept. Planned native outcomes were not supplied as observed evidence.

Sixteen remaining obligations are individually retained as nonmaterial in the
private provenance: one recurring-change obligation for no production
placement change; six language/toolchain obligations for no toolchain or API
migration; three static-checker/defect obligations for no annotation change or
defect-repair claim; one non-ASCII obligation outside the frozen ASCII fixture;
and five no-change cost/adoption obligations for unchanged production code and
credential administration. None supports an authentication adoption claim.

The used concepts are `python-structured-cleanup`,
`universal-evidence-before-intervention`, `universal-repository-contract-precedence`
and `agent-conduct-authority-bounded-action`: paired process/server cleanup,
401 evidence before refresh inference, native/preservation contracts, and
stopping the second case after the first failed. The AI failure-mode pass found
and tightened the private supervisor's bootstrap-exit check before launch.
No failure was replaced with a successful fallback, and frozen criteria were
not weakened after the timeout.

Release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` was rechecked.
All four structured citations classified as valid packet citations. Private
manifest `/tmp/caplab-auth-401-verification.json`, SHA-256
`87df027e577bed4eb346fe4d1d6320171691ea00fe5c967f74ec49b47e4ecb28`, retains 27 artifact
identities. Eleven advisory scratch files were embedded byte-for-byte,
rechecked and removed. The exact pre-execution scope record, frozen scripts,
partial native custody, failure logs and read-only verification remain.
