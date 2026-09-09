# Inspect native serving configuration before repair execution

Date: 2026-09-08. Baseline: `3c9e57a`. Primary agent under ADR 0026.

## Authorization before inspection

The continuing CAPLAB goal requires representative repair measurements.
Existing offline native launches establish no authenticated serving path.
Authorize one metadata-only inspection of the current owner's native
configuration at `/home/halbritt/.codex/config.toml`,
`/home/halbritt/.claude/settings.json` and `/home/halbritt/.claude.json`.
Report only file presence/type/permissions, configured model/provider identifiers,
native authentication-method flags, and endpoint scheme/hostname/port.
Do not print URL userinfo, path/query/fragment, credentials, tokens, account
identifiers, project histories, messages or unrelated tool configuration.
For `/home/halbritt/.codex/auth.json` and
`/home/halbritt/.claude/.credentials.json`, inspect only file stat metadata;
do not open their contents. Report relevant ambient environment variable names
as booleans of presence, without values. Do not follow configuration symlinks.

This allows local parsing of the three named configuration files solely to
produce the selected non-secret metadata. Retain only that metadata and the
inspection method under `/tmp/caplab-serving-metadata-*`; do not copy raw
configuration or credentials or hash secret-bearing source bytes into evidence.
No login/status command, native CLI, network endpoint, model call, credential
copy, account pooling, historical import, tracker write, message, service
change or push is authorized. Stop on unsupported source types or a schema
that cannot be inspected without exposing excluded data. Preserve all source
files and unrelated workspace state. This inspection allowance ends after
the one read; further effects require a prospective amendment here.

## Initial observations and follow-up scope

Both named credential files exist as regular owner-mode `0600` files; neither
was opened. The inspected Codex configuration names default model
`gpt-6-astra` and no named provider override. Claude settings name
`claude-fable-5-1[1m]`, with no configured base URL or credential environment
variables in that settings file. Claude's user configuration contains OAuth
account metadata. None of the inspected ambient authentication/base-URL/proxy
variable names is present. These observations do not prove authentication,
available capacity, an actual route or the absence of uninspected overrides.
Explicit study profiles continue to govern selected model IDs.

The existing Revbench Codex credential guard supports a named ChatGPT credential
shape and read-only anonymous delivery, but is part of an older exact live
instrument. Inspect compatibility before deciding whether to reuse its
mechanism. Authorize one bounded read of `/home/halbritt/.codex/auth.json`
through a non-following descriptor, after checking regular type, owner `0600`,
single link and at most 64 KiB. Parse it only in memory. Report the allowlisted
authentication-mode name, required-field presence, numeric expiry observations
as expired/not-expired/absent, and the existing local credential guard's named
success/refusal status. Derive the guard's expected claim hashes only in memory;
do not retain or print those hashes, claims, tokens, audiences, account IDs,
raw file bytes or exception text containing data. This is local unsigned-claim
compatibility, not a provider authentication check. No credential memfd is
created and no credential is delivered to another process or service.

Also authorize one further metadata-only read of Codex configuration to check
the documented top-level `openai_base_url` and credential-store/authentication
settings omitted from the initial projection. Preserve all earlier exclusions
and bounds. No native or network call, login, refresh, repair execution or
model spend is permitted by this follow-up. Its allowance ends after these
reads; later use needs a new exact authorization.

## Credential compatibility observations

The local Codex document declares `chatgpt`, has no nonempty API key, and
contains the four required token fields. Unsigned local expiry metadata marks
the ID token expired and the access token not expired at inspection. The
existing Revbench payload guard returns `credential_last_refresh_invalid`.
It stops at that check; this result is not a complete inventory of every
possible incompatibility. No raw timestamp format or credential value was
retained. In particular, the inspection does not diagnose a malformed token,
prove that the account is usable, or justify loosening the old guard.

The follow-up configuration read found no top-level `openai_base_url`, explicit
credential-store setting or forced-login setting. These are bounded local
configuration observations; they are not a provider-observed route or an
account capacity check. No credential was copied, mounted, refreshed or
delivered to a native process. Credential values, claim hashes and account
identifiers were not written to evidence or tool output.

[Official Codex authentication documentation](https://learn.chatgpt.com/docs/auth)
distinguishes ChatGPT and API-key authentication and documents cached
credentials and automatic refresh. It does not establish this account's
validity or the compatibility of a read-only copy with a future run. The
[configuration documentation](https://learn.chatgpt.com/docs/config-file/config-advanced)
also documents the top-level base-URL override, which motivated the explicit
follow-up check. The current native profiles still require their own exact
administration and execution authorization.

## Projection reconciliation authorization

Under ADR 0026, authorize changing only `description_html` on work-instance
CAPLAB-80, item `eddb8273-85ab-4242-9c32-b4c465de3635`, project
`45ba7d41-e21d-4eb4-b977-7f53edc59154`. Preserve its title, Ready state and all
other writable fields. Preserve the entire current description HTML exactly
once beneath a historical-planning heading; this explicitly authorizes that
planning-text copy and local before/update/readback custody. It permits no
experimental evidence import or rewriting.

The active description must use ADR 0065's current study question and
CAPLAB-84's representative-measurement requirement, make the old three-world,
708-episode, five-times multiplier and twenty-account wall-clock figures
historical assumptions rather than current capacity estimates, and retain
account/serving-path identity, within-batch allocation, service isolation,
usage-headroom and owner-held pooling-term requirements. Add only the bounded
local metadata findings above, with no authentication or readiness inference.

This reconciles existing decisions and new observations; it selects no new
substrate, account pool, model, proxy, credential mechanism, campaign size,
parallelism or execution budget. The Doctrine skill's settled-procedure
exclusion applies to the projection reconciliation; no new doctrine-backed
engineering recommendation is made.

Re-read immediately before writing and stop on concurrent change. Verify exact
stored description and preservation of every other returned field except
server update metadata. Retain source commit/path/hash provenance and private
update/readback receipts under `/tmp/caplab-serving-metadata-*`. No other
tracker change, outbound message, native process, account operation, model
call, source configuration edit or push is authorized. Commit this one record
locally after verification; authorization expires at commit. Preserve
`docs/designs/` and sibling worktrees.

## Exact-readback representation correction

The update executed, and only `description_html` and server `updated_at`
changed. The original HTML was retained exactly once. The strict
payload-equality check failed: Plane added a single outer `<div>...</div>` to
the submitted multi-root fragment. The failure remains recorded; it is not
reclassified as a passing byte-equality check.

Authorize one representation-only correction on the same item: submit the
already stored, explicitly wrapped HTML as the exact intended payload. This
changes no content, requirements, state or authority. Re-read and compare the
entire item before submitting, and retain separate correction input/result and
readback receipts. The verification criterion remains exact equality between
submitted and stored HTML, plus exact single retention of the original HTML
and preservation of other fields. Stop if the server changes that explicit
representation again; no further update is authorized here.

## Execution and verification

Both authorized local inspections completed without source mutation or
credential delivery. Their nonsecret outputs are
`/tmp/caplab-serving-metadata-observations.json` and
`/tmp/caplab-serving-metadata-codex-compatibility.json`. The methods checked
regular-file type and descriptor/source identity, bounded reads, and stable
metadata around configuration/credential parsing. The credential follow-up
also required owner mode and a single link. Claims were parsed locally and
never signature-verified or submitted to a provider.

The tracker correction passed exact payload/readback equality. The original
description survives byte-for-byte, exactly once, with SHA-256
`f49a84c67d6f703d71e833ae9b755a35a42493c3eb9ac614081b1408a302ec96`.
The final stored description has SHA-256
`e694c45ae4e9823d34d4d8e5adf3e656484a0c6f0e2953418960f27bf073a91d`.
Only `description_html` and server `updated_at` changed. Title, Ready state
and all other returned fields were preserved. The first strict-readback
failure and its explicitly authorized representation correction remain in
separate receipts. An initial bare-number lookup returned not found; the
subsequent reads/writes used the exact item UUID and project.

The private verification manifest,
`/tmp/caplab-serving-metadata-verification.json`, has SHA-256
`59fa717ddda02faeede12ec11027d15f22bea56c7498b1611912b92abab1929a`.
It hashes 14 artifacts containing the metadata observations, initial
and corrected tracker payloads/results/readbacks, and source provenance.
It contains no raw configuration or credential bytes. No runtime source
changed, so the full suite was not rerun; verification checked metadata
invariants, source/receipt hashes, exact tracker readback and preservation.

The current credential document cannot be passed through the existing
Revbench guard as-is. [ADR 0063](../decisions/adr-0063-bounded-codex-live-revbench-execution.md)
requires reopening before a new harness version or credential method is
adopted; its older validation contract remains unchanged. This inspection
supplies a concrete compatibility constraint for that future decision, not an
authorization to copy or refresh the operator credential. CAPLAB-80 and
CAPLAB-84 remain incomplete. No native model execution, capacity estimate,
reviewer ranking, independent acceptance or human-owned judgment is claimed.
