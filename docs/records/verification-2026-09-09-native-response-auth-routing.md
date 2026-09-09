# Native response endpoint and authentication failure routing

Baseline: `309525f`. Primary agent acting under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Decision and bounded authorization

The [preceding diagnostic](verification-2026-09-09-native-auth-401.md) did not
reach a response 401. Its `chatgpt_base_url` redirected ancillary HTTP requests,
but native stderr still named the external response WebSocket URL. The native
child timed out; the managed case never launched. Preserve that failure and
its consumed authorization without reclassifying or reusing it as a new result.

The [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
describes `openai_base_url` as the built-in OpenAI provider's base-URL override.
The installed public binary contains that field. Select one new two-case
synthetic diagnostic adding only this routing key to the prior native command
configuration. Keep the native harness, model and effort, authentication modes,
prompt, response/error fixture and resource bounds. Do not introduce a custom
provider, shared SDK, app-server, real endpoint, successful model response or
transport-disable flag. Source documentation and a binary string establish a
candidate configuration, not its effective routing; the new run must observe it.

Authorize a new record, private source/verification/advisory artifacts under
`/tmp/caplab-response-auth-*`, and one fresh owned unit with two sequential native
CLI cases: external tokens with an empty refresh field, then managed ChatGPT
with a fabricated nonempty refresh token. Both use newly constructed fabricated
fixtures from the prior script's source, including its fresh September 9
last-refresh date. Read no actual operator credentials, account configuration,
historical experiment payloads or remote model endpoint. No CAPLAB runtime,
contract, test, tracker or configuration changes. Preserve historical custody,
`docs/designs/`, other worktrees and services. No messages or push.

Before launch, freeze the new source, fixture, native installation manifest,
policy and selected runtime hashes. Enforce the native-agent policy with the
existing invocation builder before adding the declared diagnostic overrides.
The exact prompt remains `Authentication diagnostic only. Reply READY without
using tools or changing files.` Add `openai_base_url` pointing to the same
private HTTP origin as `chatgpt_base_url`; retain the local refresh override.
No custom provider or transport selection is authorized.

Retain all-unshared Bubblewrap namespaces, only private loopback, read-only
host/native mounts, two device nodes, sealed read-only synthetic auth and a
64-MiB runtime tmpfs. Trusted bootstrap may raise loopback with CAP_NET_ADMIN,
then must clear effective/permitted/inheritable capabilities and set and verify
no-new-privileges before the server and native child. Verify exact input bytes,
EROFS, no inherited memfd and local HTTP preflight. Unit bounds remain 512 MiB
memory, zero swap, 64 tasks, eighty seconds and control-group cleanup; native
child twenty seconds, case capture thirty seconds/300,000 combined bytes,
outer capture ninety seconds/100,000 bytes, no core, 2-MiB per-file limit.
The HTTP fixture retains sixteen-request, 1-MiB-body and two-second-socket
bounds. Response paths return 401; refresh returns 400 invalid_grant; unrelated
paths return 404. No successful model or refresh response is available.

Require complete native termination and complete captures before advancing
between cases. Stop on timeout, bootstrap/fixture error, integrity/containment
failure or cleanup failure; preserve partial custody and do not retry. Stop and
unload only the exact owned unit and verify its cgroup is absent. Recheck source
and installation identities. This new allowance is one fixed execution of a
changed routing configuration, not permission to retry the preceding attempt.
It expires at the local record commit, with no remaining native allowance.

Require an observed response-path 401 before any 401-path inference. Require
an actual managed refresh request before treating the refresh override as a
working control. Missing observations, timeouts, local cache acceptance and
normal process exit cannot establish no-refresh behavior. Even a completed
comparison is scoped to these synthetic inputs and this failure path; it does
not authorize real credentials, prove provider authentication, complete a
representative repair, admit native study evidence or support reviewer ranking.


## First execution: routing observed, fixture rejected

The new unit `caplab-response-auth-64e593093cdd43e2949dc8c6f0dee4c7.service`
launched only its external case. Native stderr now names
`ws://127.0.0.1:33989/responses`, and the local fixture recorded an authenticated
GET to `/responses` with status 401. It also received model-catalog and ancillary
requests. This establishes effective local routing for the tested command.

The native client rejected the response with `HTTP version must be 1.1 or
higher`. The inspected installed Python HTTP handler defaults to HTTP/1.0, and
the bootstrap did not override it. The client then retried the handshake,
eventually fell back to HTTP, and timed out at twenty seconds. Sixteen requests
were retained (one response-path 401, fifteen ancillary 404s); subsequent
requests produced 26 recorded handler AssertionErrors after the request bound.
The managed case did not start. Both launcher captures reached EOF with exit 1;
the native child was killed with return code -9. This is an invalid refresh
comparison because the response failed protocol validation and the request
budget was exhausted. No no-refresh conclusion follows.

The original scripts and `/tmp/caplab-response-auth-native/` failure custody
remain frozen. The unit's before-case observation retains its actual cgroup
path and the specified memory/swap/task limits; cleanup reports `not-found`.
The authorization for that unit is consumed. Do not amend its results or rerun
its unchanged source.

## Separate fixture-correction authorization

Under the same ADR 0026 delegation, authorize a newly identified fixed run
under `/tmp/caplab-response-auth-http11-*` with a fresh
`caplab-response-auth-http11-<32 hex>.service` unit. This grants one new pair of
sequential external and managed cases only after the preceding unit's cleanup
is verified. It does not renew the preceding run or alter its failed criteria.

Change exactly two fixture properties: declare `protocol_version = 'HTTP/1.1'`
and raise the per-case request allowance from sixteen to sixty-four. Keep
Connection: close and exact Content-Length responses, all native command and
environment settings, fabricated auth sources, twenty-second native timeout,
namespace/mount isolation and all other resource/stop/capture criteria. Keep
401 and invalid_grant responses; provide no successful model/refresh content.
These corrections address the observed protocol error and exhausted request
budget; no change to Codex transport or retry configuration is authorized.

Before launch, validate the new handler's preflight response version is HTTP/1.1
as well as status/body. Freeze new script/fixture/source/installation identities.
Require normal native termination, no fixture errors and complete capture before
advancing to managed. Verify source identities and exact-unit/cgroup cleanup
at closeout. Stop later cases and preserve failure custody on any failure; no
retry allowance. The corrected run's authorization expires at this record's
commit. Retain both runs and classify their outcomes separately. All original
preservation boundaries and interpretation limits remain in force.


## Corrected execution and bounded interpretation

The HTTP/1.1 run completed both cases under unit
`caplab-response-auth-http11-98bbde2fdeb64532b53c5813bad975e8.service`.
Both native children exited 1 normally and emitted `turn.failed`; neither
reached its timeout. Both bootstrap captures and the supervisor exited zero,
with complete streams. The fixture reported no handler errors.

| Synthetic cache mode | Response-path 401 requests | Refresh requests | Native terminal outcome |
| --- | --- | --- | --- |
| External tokens, empty refresh string | 21 GET and 18 POST | 0 | 401 Unauthorized after retries and HTTP fallback |
| Managed ChatGPT, fabricated refresh token | 4 GET | 1 POST | Access token could not be refreshed |

The external case recorded 56 total requests and took 14.200 seconds including
bootstrap/capture. Its response requests used the exact fabricated access token.
The managed case recorded 22 requests and took 0.799 seconds. Its refresh request
followed response-path 401s, used `grant_type=refresh_token`, and supplied the
exact fabricated refresh token. The fixture returned 400 invalid_grant, as
frozen. The remaining requests were ancillary 404s. These counts characterize
this run and do not establish stable retry counts or a rate-limit model.

This supplies a working managed-refresh control for the installed CLI and the
local override. External-token mode made no refresh request during its completed
synthetic 401 failure path. Its native execution was not simply a cache-parser
success. The managed observation also demonstrates that a read-only auth mount
does not prevent a refresh request from being attempted: auth bytes remained
unchanged while the fixture received the refresh token.

The comparison supports further investigation of external-token administration;
it does not establish all refresh paths, successful authentication, expired-token
handling, successful task capture, account capacity or compatibility with real
operator credentials. Neither the fixture's rejected tokens nor its error bodies
are provider evidence. Native transport retries occurred within each one-shot
CLI launch; no experiment launch was retried. Native model execution against a
provider, real credential transformation and a new administration adoption remain
outside these authorizations. The old credential guard and ADR 0063 profile are
unchanged. CAPLAB-80/84 and representative repair evidence remain incomplete.

## Verification and retained failure custody

The separate read-only verification script
`/tmp/caplab-response-auth-verify.py` compared both runs with their frozen
script, fixture selection, selected runtime/policy hashes and full selected
Codex installation manifest. All matched. It checked the five launcher receipts
against complete stream sizes/hashes/EOF, native start/summary pairs, exact
synthetic auth hashes, EROFS, no inherited memfd, zero capabilities and
no-new-privileges. Effective native argv/env matched the planned tuple plus the
three declared configuration overrides and local refresh endpoint.

The verifier checked request populations, native terminal outcomes, the managed
refresh grant and token-match observation, token absence from invocation/native
capture, and agreement between successful reports and raw streams. It verified
the first run's timeout/protocol error and absence of managed execution separately.
Both exact owned units are unloaded and both recorded cgroup paths are absent.
The observed memory/swap/task limits matched their declared bounds. The result
is `/tmp/caplab-response-auth-checked.json`; it distinguishes the invalid first
comparison from the completed corrected diagnostic.

The frozen initial probe `/tmp/caplab-response-auth-probe.py` has SHA-256
`d13f249facd0d85e4f97b9a39d4bfe7d4dc3b4dc46f3a5c62ff4aa88f7439a66`. The corrected probe
`/tmp/caplab-response-auth-http11-probe.py` has SHA-256
`51c28c1d43ea69b14004a3dea32728359d7216cbc672d5fff0ecfba84e89bd4c`.
Their embedded bootstrap bytes match their separate source files. Both capture
roots, failure outputs and exact pre-execution scope snapshots are retained.
No source or capture from the failed run was changed to make verification pass.

Private scripts passed AST parsing and Ruff's undefined-name/unused-import
checks. Repository runtime and tests were unchanged; the full suite was not
rerun. The latest runtime verification remains 1,252 tests with four skips from
`e652313`. No tracker, operator credential, service outside the two owned units,
historical experiment or study acceptance changed.

## Advisory provenance

The validated Pincite gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`
and retriever `retriever-ec995ecdd083b2c8`. The packet contains baseline/routed
concepts, not precisely nominated authentication guidance.

Initial packet `pkt-c1b06083ea6e17bb` led to a first typed-evidence pass and
packet `pkt-39fe16ec13c165b7` (SHA-256
`39fe16ec13c165b7de57eb352cfc895da39d5b6a064a84f0999f1f1d0f7744e0`). A second bounded pass
added the separately recorded correction authority and inspected HTTP fixture
source. Final packet `pkt-396ba453d1217075` has SHA-256
`396ba453d1217075af8a066b356940a6e336bc1dcd43563a30111808eedfc1c2`. Each final Markdown
packet was read before its corresponding native launch. New outcomes were not
supplied as evidence before execution.

Sixteen unmet obligations retain individual nonmaterial classifications: one
recurring-change obligation, six language/toolchain obligations, three static
checker/typing obligations, one non-ASCII obligation and five general no-change
cost/adoption obligations. This diagnostic changes no production API, dependency,
checker or credential administration. The actual protocol defect is supported
by native stderr and the installed handler source, without a typing decision.
The frozen fixture is ASCII. The missing generic obligations do not establish
any broader compatibility, security, cost or adoption conclusion.

Used concepts are `python-structured-cleanup`,
`universal-evidence-before-intervention`, `universal-repository-contract-precedence`
and `agent-conduct-authority-bounded-action`: paired cleanup, observed controls
before refresh inference, native/preservation contracts, and separately scoped
execution with retained failure. The AI failure-mode review missed the first
fixture's default HTTP version; that error is recorded and the corrected
preflight checks version as well as status/body. No mock success, hidden retry
or weakened post-execution criterion was used.

Pincite release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` was rechecked.
Both used packets closed with four valid structured citations each. Private
manifest `/tmp/caplab-response-auth-verification.json`, SHA-256
`651b2b5eca801e9d24b17c846b799d853d01f199b8a3045cb8506cd25abaa125`, retains 53 artifact
identities. Sixteen advisory scratch files were embedded byte-for-byte,
verified and removed. Both frozen probe populations, original failed outputs,
exact scope snapshots and verification artifacts remain available. Local links
and whitespace checks passed. Both native allowances are consumed.
