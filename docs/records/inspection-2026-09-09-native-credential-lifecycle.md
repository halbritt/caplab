# Distinguish managed refresh from external-token administration

Baseline: `e652313`. Decision mechanism: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Scope and authorization

Authorize this record, read-only inspection of public native package metadata
and official documentation, and private fixed synthetic probes and verification
artifacts under `/tmp/caplab-auth-lifecycle-*`. Preserve repository runtime,
native contracts, old Revbench credential guards, operator credentials/configs,
all historical evidence, `docs/designs/`, other worktrees and services. No
tracker mutation, native task/model execution, provider call, login/logout,
actual credential read/copy/refresh, source configuration change, message or
push. Commit this record locally after bounded verification; scope expires
at commit.

Authorize one fresh offline unit containing exactly two Codex `login status`
executions against newly constructed external-token cache fixtures. Both use
`auth_mode: "chatgptAuthTokens"` and the preceding synthetic whole-second
fixture's fabricated ID token, access token and account ID. One omits the
refresh-token field; the other supplies an empty refresh-token string. This
is a new format compatibility question, not a repetition of the prior managed
cache population. The original managed-cache outcomes remain prior observations.
Do not launch an app-server or substitute its interface for native CLI exec.

Use the installed Codex source root from the existing native startup probe,
freeze its complete bounded installation manifest and new script/fixture/source
hashes, and supply each synthetic payload by sealed memfd through the existing
explicit descriptor API and direct Bubblewrap `--ro-bind-data`. No payload in
argv/environment. Use all-unshared namespaces, read-only host/native mounts,
loopback only, required null/random devices, private 64-MiB runtime tmpfs,
512-MiB unit memory, no swap, 64 tasks and 40 seconds. Each native capture gets
five seconds and 100,000 bytes; outer capture gets 50 seconds and 100,000 bytes.

Require exact supplied bytes, read-only write refusal, no input memfd inherited
by the final native bootstrap, complete streams and normal process termination.
Native exit codes characterize compatibility; no success is presupposed.
Verify source/installation hashes, preserved fixture bytes, and stopped/unloaded
owned unit with absent cgroup. Stop on containment, integrity, incomplete capture
or cleanup failure; preserve partial custody and do not retry. No real account
validity, refresh behavior or authenticated task readiness can be inferred from
these offline status commands.

## Documentation observations

The [authentication guide](https://learn.chatgpt.com/docs/auth) describes shared
local login caches and automatic refresh for managed ChatGPT sessions. Its
enterprise access-token login is a distinct automation option; the guide does
not establish that an OAuth access token extracted from a managed cache is an
enterprise access token.

The [managed-auth automation guide](https://learn.chatgpt.com/docs/auth/ci-cd-auth)
describes refresh before normal execution when the cache becomes stale, a
refresh-and-retry path after a 401, and persistence of the refreshed bundle.
It requires one serialized workflow stream per cache and warns that another
consumer's token rotation can make a restored copy stale. These are documented
current-client behaviors, not measurements of this installed binary's precise
refresh threshold or the operator's current session.

The [app-server guide](https://learn.chatgpt.com/docs/app-server) describes
experimental `chatgptAuthTokens` authentication, where a host supplies access
and account information and responds to refresh requests. It does not establish
that native CLI exec can load that mode from `auth.json`, or that the installed
version implements a no-refresh CLI path. App-server behavior must not be
silently attributed to CLI exec.

## Inference and compatibility question

A read-only managed-auth mount constrains local writes; it does not prevent a
client from attempting remote refresh before encountering a write failure.
Therefore the preceding successful read-only status probes are insufficient
to authorize using the operator's shared managed cache in a native task run.
The existing ADR 0063 refresh prohibition remains in force for its old profile.

The next bounded question is whether the installed CLI recognizes an external
cache representation without a refresh credential. Recognition would justify
further execution-path investigation, not authentication, no-refresh proof or
adoption. Rejection would rule out that tested representation for this version.
Do not change the managed cache's mode, truncate real credentials, borrow an
API-key identity, or select app-server as the measurement subject to make a
probe pass. A dedicated serialized managed session and an explicitly selected
external-token administration are different future options with different
custody and identity obligations.

## Native observations and disposition

Both authorized status commands completed with full streams in the fixed
read-only offline namespace. The npm package declares Codex `0.153.4`, and
its complete selected installation manifest matched before and after the
probe and on final read-only verification.

| Synthetic external-cache representation | Native observation |
| --- | --- |
| `refresh_token` omitted | Exit 1; parser reports missing `refresh_token` field |
| `refresh_token` present as empty string | Exit 0; `Logged in using ChatGPT` |

The observed distinction is cache-document acceptance. The success message
does not distinguish managed versus externally managed execution semantics;
it is not proof that CLI exec uses the app-server's external refresh protocol.
No full bundle or operator token was transformed for this probe. The old
Revbench guard still refuses the synthetic external mode; it was not changed.

The omission representation is incompatible with the tested local parser.
The empty-string representation is a candidate for a further, separately
scoped native execution-path characterization. Do not adopt it for real
credentials based on this status result. The next meaningful check must
establish the actual request/401 behavior of native CLI exec with this mode,
preserve the distinction between a missing refresh credential and a proven
no-refresh policy, and stop rather than renew authorization when credentials
expire. The current result does not authorize that execution check.

The private probe is `/tmp/caplab-auth-lifecycle-probe.py`, SHA-256
`7574ca20b2af6980bb817d06d5fdbb9f8e53d71950cd81992d210752a0605118`.
Custody is `/tmp/caplab-auth-lifecycle-native/`. The omitted-refresh input
SHA-256 is `5a568bff850d4c06aea77a14468687b42781047bcb09484b7c02d8766c29e7d0`;
the empty-refresh input SHA-256 is
`7647dd0d9eb92cc962081f6189c83d494a4bb04aa27b638ea7a8b01c1838caaa`.
Each bootstrap observed the expected input hash, `EROFS` on write, loopback
only, and no inherited input memfd before native exec. Parent descriptor
flags and sealed bytes remained unchanged. The unit reported the frozen
memory, swap and task bounds.

Unit `caplab-auth-lifecycle-b699f460695b4f23ab3053155697fba1.service`
unloaded and its observed cgroup disappeared. The read-only verification at
`/tmp/caplab-auth-lifecycle-verify.py` checked all three process receipts and
stream sizes/hashes/EOF, source/script/fixture/installation identities,
report-to-capture agreement, exact synthetic transport, absence of nonempty
synthetic token values in invocation/native capture, expected native outcomes,
and current unit/cgroup closure. Its result is
`/tmp/caplab-auth-lifecycle-checked.json`. No native retry occurred.

## Advisory provenance and final verification

Pincite's validated release gate recorded source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, and retriever `retriever-ec995ecdd083b2c8`.
Release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` was rechecked.
Initial packet `pkt-cdbb1fda08aa077d` preceded one typed-evidence pass covering
authority, contracts, source and existing test/verification evidence. Final
packet `pkt-f9601fc319a6ba08` has content SHA-256
`f9601fc319a6ba08889df5f5f1288914b58f04bc9466b2de9ce8f4aff7ce8c96`.

All 31 remaining obligations are individually retained as nonmaterial for
this format-only investigation: six concern architecture decisions without
an administration adoption; six concern duplication without a production-rule
merger; four concern abstraction without a new public interface; five concern
special methods not introduced; ten concern language/toolchain conformance
without a runtime, interpreter, dependency or style migration. Their omission
does not support a production administration change. Four used concepts
classified as valid citations: `python-structured-cleanup`,
`universal-evidence-before-intervention`, `universal-repository-contract-precedence`,
and `agent-conduct-authority-bounded-action`. They support paired cleanup,
observation before adoption, old-contract preservation and the two-case scope.

The private probe passed AST parsing and Ruff's undefined-name/unused-import
check; its read-only verifier passed the same Ruff check. No repository runtime
or tests changed, so the full suite was not rerun. The two native cases and
custody checks supply the new evidence. CAPLAB-80/84 and the broader roadmap
remain incomplete; no reviewer score, account capacity, independent judgment
or study acceptance is established.

Private manifest `/tmp/caplab-auth-lifecycle-verification.json`, SHA-256
`895de6ede79557acb25ebe623bdaeafb9b05c03ad03b016bc47602a816c64df3`,
retains 32 artifact identities. Eleven advisory scratch files were embedded
byte-for-byte, verified, then removed. The frozen probe, both native capture
roots within the owned unit's custody, supervisor capture, logs, read-only
verifier and its output remain available. Local record links and whitespace
checks passed; the only repository change is this inspection record.
