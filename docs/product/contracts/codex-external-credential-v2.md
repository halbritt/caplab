# Native credential marker policy, version 2

Select `quarantine_profile="credential-private-text/v2"` when calling
`open_codex_external_credential()`. The default remains
`credential-private-text/v1`, described in the
[version 1 contract](codex-external-credential-v1.md).
The returned lease exposes its selected `quarantine_profile`. Unsupported
profiles are refused before opening the credential source.

Version 2 changes marker classification only. Source/identity anchors, bounded
file reading, token/expiry checks, projected credential bytes, sealed descriptor
ownership and cleanup retain their existing behavior. The API still authorizes
no native execution, writes no receipt and performs no refresh or authentication.

The policy recognizes these structural field names only at the stated
locations and with the stated types. `auth` below means the exact JWT claim
`https://api.openai.com/auth`; an organization record must be a direct element
of its `organizations` list.

| Location | Structural fields and types | Text values omitted from markers |
| --- | --- | --- |
| Top-level claims | `rat`: nonnegative integer; `sl`: boolean | None added; numeric/boolean leaves already supplied no text marker |
| Top-level claims | `sid`, `session_id`: nonempty strings | None; session identifiers remain guarded |
| Top-level claims | `scope`, `scp`: string or list of strings | Only `openid`, `profile`, `email`, `offline_access` |
| `auth` | `chatgpt_account_id`, `chatgpt_user_id`, `chatgpt_plan_type`: strings | Only known plan values at `chatgpt_plan_type`; account/user IDs remain guarded |
| `auth` | `organizations`: list | None |
| Organization record | `role`, `title`: strings; `is_default`: boolean | Known roles; generic titles only when `is_default` is exactly `true` |

Known plan categories are `free`, `go`, `plus`, `pro`, `team`, `business`,
`enterprise`, `edu`, and `unknown`. Known roles are `owner`, `admin`, `member`,
`user`, and `reader`. Generic titles are `Personal`, `personal`, `Default`,
and `default`. These closed sets are CAPLAB marker-policy selections, not an
exhaustive assertion about provider account products, privileges or entitlements.

For scope lists, only recognized string elements are omitted. A scope string
is omitted only when every element of its canonical single-space-separated
form is recognized. Unknown scope strings remain guarded as complete values.
Malformed lists do not gain category exemptions. Case and bytes are preserved;
there is no lowercasing, whitespace normalization or fuzzy matching.

Every occurrence is classified separately. A generic title on a nondefault
organization, a custom title on any organization, a private name equal to a
known category, a declared key at the wrong location, and unknown fields or
values remain guarded under the existing exact-text rules. A dictionary key
spelled `*` cannot masquerade as an organization-list element. All visited
nodes, including exempt categories, count toward the existing traversal bounds.

Complete credential documents, token strings and JWT segments, source refresh
tokens and account/subject identity always remain markers. The selected policy
does not globally subtract a category string from the marker set; another
private occurrence of equal bytes still triggers quarantine. Header handling
and version 1 classification are unchanged.

This policy protects credential and identifying text while allowing declared
protocol structure and generic administration categories in restricted raw
capture. It does not hide every fact about a subscription or organization,
provide arbitrary PII redaction, detect transformed secrets, erase process
memory, or authorize public release. Account/administration blinding and
complete-surface review remain required before coder exposure or publication.
Missing/quarantined capture remains unavailable. A bounded local comparison
does not establish provider authentication or readiness for a repair study.
