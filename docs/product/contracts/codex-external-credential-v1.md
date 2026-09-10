# Native external-token credential delivery, version 1

`caplab.codex_external_credential.open_codex_external_credential()` is a
context manager for separately authorized native repair administration. It
accepts a credential source path, independently expected source/account/subject
SHA-256 values and `minimum_access_lifetime_seconds` from 1 through 86,400.
These hashes belong in private administration context. The API writes no
receipt, registers no account and authorizes no execution.

The source must be a resolved absolute path to a regular file owned by the
current UID, mode 0600, with one hard link and 1–65,536 bytes. The read uses
non-following/nonblocking flags, verifies stable descriptor/path metadata and
matches the source hash. Source bytes remain unchanged. Unsupported input
raises `ExternalCredentialError` with a fixed code and no source/claim details.

The accepted source has exactly `auth_mode`, `OPENAI_API_KEY`, `tokens` and
`last_refresh`; mode is `chatgpt` and the API-key value is null. The token object
has exactly nonempty ID/access/refresh/account strings, each at least 12
characters. Refresh metadata is a valid UTC calendar timestamp ending in Z,
with an optional 1–9-digit fractional part. It is preserved as supplied.

Both token payloads must be bounded, strict UTF-8 JSON objects with unique keys,
canonical unpadded base64url header/claim segments, RS256/ES256 algorithm
metadata, issuer
`https://auth.openai.com`, a nonempty audience, an expected subject and the
matching `claims["https://api.openai.com/auth"]["chatgpt_account_id"]` field. Issue
times must be nonnegative and not future; expiry must follow issue time. The
access expiry must cover the requested remaining lifetime. ID expiry may be
past in this explicit external-token profile.

These are unsigned local mismatch checks. They neither verify token signatures
nor prove provider authentication, selected-account authority or capacity.
The caller must obtain the expected identities independently and use an
execution deadline within the selected lifetime. Successful parsing alone
does not establish a complete Binding or usable capture configuration.

The context yields `ExternalCodexCredential` with a borrowed `descriptor` and
`quarantine_factory()`. Its sealed anonymous document changes only
`auth_mode` to `chatgptAuthTokens` and removes the refresh-token value. Other
token strings and identity remain unchanged. Seals prevent writes, growth,
shrinkage and seal removal; the descriptor closes on context exit. The caller
must not retain its numeric descriptor for later reuse. No source refresh or
native credential-store mutation occurs.

Every factory call creates independent exact-byte stream state. Markers include
complete source/projected documents, tokens, JWT segments, source refresh,
account/subject identity and nested nonempty textual claim values. Standard
JWT issuer/audience/timestamp structure is excluded; declared public structure
keys are `id`, `label`, `email`, `name`, `organization`, `delegations` and
`https://api.openai.com/auth`. Other nonempty claim keys are guarded. Numeric,
boolean and null custom leaves are not unique secret byte strings. Claim
traversal is limited to 4,096 visited values and 32 levels per structured input.

The caller must apply a fresh guard to every durable stream/metadata/mount
surface, including failures, and provide an isolated read-only native mount.
Short strings and generic claim keys can quarantine ordinary output; those
false positives must be measured before calling a real cache usable. Missing
or quarantined capture is unavailable, never an empty successful result. This
is not general PII redaction, transformed-secret detection, memory zeroization
or hostile-exfiltration certification.

The historical Revbench credential profile and guard are unchanged. This API
has synthetic file/descriptor/process verification; it has not delivered the
owner's real credential or executed an authenticated native repair. A new
prospective native profile, private identity selection and exact execution
authorization remain necessary before that use.

An explicitly selected [version 2 marker policy](codex-external-credential-v2.md)
recognizes declared protocol fields and generic categories. This version 1
policy remains the default and retains its original marker behavior.
