# Native credential marker policy, version 3

Select `quarantine_profile="credential-private-text/v3"` explicitly. The
default and versions 1 and 2 retain their prior behavior. This extends the
[version 2 classification](codex-external-credential-v2.md) with two scoped
protocol fields:

| Location | Recognized field and type | Omitted text markers |
| --- | --- | --- |
| Top-level JWT claims | `auth_provider`: string | Field name and the exact generic category `password` |
| `https://api.openai.com/auth` | `groups`: list | Field name only; membership values remain guarded |

These are CAPLAB marker-policy selections. Other authentication categories
remain guarded. A field at the wrong location, a malformed field, private
names or custom keys with the same spelling, and private membership strings
retain their markers. No category is globally removed from the marker set.
Complete credentials, raw tokens, JWT segments and account/subject identifiers
remain protected. Projection bytes, descriptor ownership and expiry checks do
not change. Selecting this profile grants no provider or publication authority.

The change follows reviewer-output-probe-2: version 2 rejected six of the 163
authorized task files because ordinary source contains `password` and
`groups`. A controlled local comparison now rejects zero task files with
version 3 and the same six with version 2. This checks compatibility with
those exact task inputs; it does not establish that all future output will
be retained or that a withheld transcript contained no actual credential.

Three added public-interface tests cover source preservation, group membership,
private collisions, malformed locations and split-stream token leakage.
The first category test and group-field test each failed before their
corresponding implementation changes. Private observations and hashes are in
`~/.local/share/caplab/reviewer-ranking-001/development/capture-category-verification-20260910-2.json`
(SHA-256 `7dd6e3c358f69483f70c4932427bf7f6bff9cc84aa1a9acf053f5175c092eece`).
The first intermediate check, retained separately, still rejected four files
before the group-field correction. Neither local check called a provider.
