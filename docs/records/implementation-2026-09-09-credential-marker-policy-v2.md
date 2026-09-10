# Separate protocol categories from private credential text

Baseline `238666b`. The previous goal turn made progress: provider-independent
child observation is integrated and verified. It also found that the selected
real cache's exact-text quarantine blocks four of six public normal-output
samples. Real credential adoption remains withheld. A capture gate that treats
every short metadata category as an identifying secret can prevent meaningful
repair measurements, but simply dropping short strings would lose protection
for short private names and unknown claims.

Under the continuing owner goal and ADR 0026, investigate a separately selected
marker policy. Preserve version 1 and the historical Revbench guard. A possible
version 2 may recognize only explicitly declared protocol-category fields and
closed vocabularies; it must continue guarding all token bytes, identifiers,
private names, unknown fields/values and overlapping private occurrences. It
must not remove a string globally merely because a public field also uses it.

The installed pinned native binary contains the declared literals
`chatgpt_plan_type`, `chatgpt_account_id` and `chatgpt_user_id`. Current official
[Codex app-server documentation](https://learn.chatgpt.com/docs/app-server)
separates plan metadata from account identity and describes external-token
administration. This supports investigating field-aware classification; it
does not classify the owner's actual plan as public or authorize disclosure.

## Prospective private diagnosis

Authorize one bounded local read of `/home/halbritt/.codex/auth.json`, requiring
a current-owner regular file, mode 0600, one link, at most 64 KiB and stable
descriptor/path metadata. Open without following a symlink and without blocking;
disable core dumps. Parse only in memory. No raw credential, token, claim,
identifier, unknown field name or hash of those values may be retained.

Compare the prior six frozen public samples with markers grouped by origin:
complete credential/token material, header text, ordinary claim text and the
specific auth-claim field `chatgpt_plan_type`. Retain only per-sample booleans
and whether that field is a string in the prospectively selected vocabulary
`free`, `go`, `plus`, `pro`, `team`, `business`, `enterprise`, `edu`, `unknown`.
Do not report which value is present. Derive identity hashes only in memory
for local parser compatibility; they are not independent identity anchors.

Test a candidate marker set that omits only a recognized category occurrence
at that exact field in either token. Rebuild all other markers, so any same
text at another private location still quarantines output. Preserve raw token
and projected document markers. Do not create a credential descriptor or
deliver credentials, refresh, launch a native client or contact a provider.
Retain script, public corpus and boolean results under
`/tmp/caplab-quarantine-v2-*`. This one read expires when the inspector returns.
No runtime change is authorized until a prospective implementation scope below
selects the actual policy from the findings. Historical custody, tracker state,
other services and `docs/designs/` remain unchanged.

## Diagnosis and implementation selection

The one private read completed. Reconstructed marker groups exactly matched
version 1. Every false positive among the six frozen samples originated solely
from a recognized category at the selected field. Rebuilding the candidate
markers with only those field occurrences omitted allowed all six samples.
No token, header or other private-claim marker matched the four affected
samples. The actual category value was not retained or reported.

Select the explicit profile `credential-private-text/v2` as an optional argument
to the existing delivery API. Its default remains `credential-private-text/v1`.
Version 2 excludes only recognized string values at
`claims["https://api.openai.com/auth"]["chatgpt_plan_type"]` using the frozen
vocabulary above. Retain the field-name marker, unknown values and wrong-type
content. Rebuild markers by occurrence so the same string in any other private
claim remains protected. Preserve token bytes and all source, identity, lifetime,
sealed-descriptor and cleanup rules. Expose the selected profile on the lease
so callers can record it in administration context without secret values.

This is a deliberate privacy-contract distinction: a plan-category word is
not an identifying secret when it occurs at that field. The policy does not
hide subscription-category metadata in restricted raw custody. It does not
make that custody public or authorize disclosure of the owner's actual plan;
account/administration blinding remains a separate obligation before coder
exposure. Private names, account/subject identities and unknown claims are not
declassified, regardless of their length or resemblance to a category.

Authorize the implementation, focused synthetic tests, version 2 contract,
this record, required full checks and private advisory/verification artifacts.
Test unchanged default behavior, all selected enum categories, short private
text with the same spelling, wrong-path/unknown values, non-ASCII private text,
split-token/claim quarantine, sealed projection identity and child-process
retention. No existing native profile adopts version 2 automatically. No real
credential delivery, native/provider execution, study, tracker write, historical
rewrite or outbound message is authorized. Commit and push verified work;
implementation authority expires at the verified commit.

After focused synthetic tests pass, authorize one further metadata-only local
read under the same filesystem/privacy bounds to compare the actual implemented
profiles on the same source in memory. Compare the six frozen samples and the
already retained native diagnostic at `/tmp/caplab-native-adoption-attempt-1`.
Verify its manifest before scanning; limit the selected capture to 500 regular
files, 4 MiB per file and 32 MiB total. Retain only selected artifact paths/
hashes, aggregate/per-surface quarantine counts and pass/fail of in-memory
positive secret controls. Do not retain source/identity hashes, token/claim
values or which exact private marker matched. Do not rewrite the diagnostic.
No anonymous credential FD or child process may receive the real credential.
This read expires after the comparison returns; passing it is bounded local
compatibility evidence, not provider authentication or complete privacy proof.

## Broader comparison and further diagnosis

The implemented candidate passed six focused tests, including real Python
descriptor handoff and decoded-claim quarantine under both profiles. In the
second authorized local read, both profiles passed 13 positive token/identity
controls and produced identical credential projections. Version 1 quarantined
112 of 170 retained diagnostic files; the category-only candidate quarantined
86. All six small samples passed under the candidate. The 2,771,007-byte native
capture remained unchanged. This broader counterexample prevents calling the
candidate usable; the candidate implementation is not yet the final policy.

Authorize one additional local diagnostic read under the same privacy and
filesystem bounds. Partition remaining matches into header field names,
header text values, claim field names, claim text values and complete token/
identity material, using only the already frozen public sample and native
capture corpus. Do not retain any matched string, arbitrary claim name, source
hash or private value. For field names, report only membership in a closed,
prospectively named protocol-key set: `jti`, `nbf`, `nonce`, `auth_time`, `acr`,
`amr`, `azp`, `at_hash`, `sid`, `kid`, `typ`, `alg`, `scope`, `scp`,
`chatgpt_account_id`, `chatgpt_user_id`, `chatgpt_plan_type`, `organizations`,
`organization_id`, `is_default`, `role`, `roles`, `groups`, `email_verified`.
For text values, report only whether a match occurs at a key in that same set,
without identifying the value. Counts/booleans and selected artifact paths
are sufficient to choose the next investigation. Do not broaden any exclusion
or deliver credentials under this read. Its allowance expires on return.

That read identified field-name matches in 80 files and text-value matches in
39; token/identity material and header markers matched none. The declared
`role`, `scp` and `sid` fields accounted for some matches, with other field
names still unresolved. This contradicts a category-only explanation of full
capture usability. No broader exclusion follows from these counts alone.

Authorize one final structural diagnosis on the same bounded source/corpus.
Permit a restricted metadata record naming a matched claim key only when it
contains 1–64 ASCII lowercase letters/underscores, occurs verbatim in the
already frozen diagnostic corpus, and also occurs in the pinned installed
native binary. Retain both public-source locators and the binary offset as
provenance; matching source text does not itself declassify a field. Retain
no claim value. For value matches, report only aggregate counts by the fixed
keys `scp`, `scope`, `role`, `roles` and whether all such values belong to a
candidate closed vocabulary of standard scopes (`openid`, `profile`, `email`,
`offline_access`) or roles (`owner`, `admin`, `member`, `user`, `reader`).
Keep unsupported values under an unnamed aggregate. This narrowly extends
private structural-metadata retention, without publishing an actual account
category, identifier, credential or arbitrary value. All other read bounds
and no-delivery conditions apply; the read allowance expires on return.

The structural diagnosis identified six matching field names already present
in both public sources: `rat`, `role`, `session_id`, `sid`, `sl`, and `title`.
Matched role and scope values were all within the proposed closed vocabularies;
six files still had a value match outside those classified fields. Binary
substring presence alone does not establish field meaning, so no key or value
has yet been added to the exclusion policy from that observation.

Authorize one follow-up metadata read to establish the locations and type
classes of those six names, retaining paths only through already named
protocol fields and replacing other ancestors with an unnamed placeholder.
For the six remaining value-matched files, retain only whether the matches
come from an `organizations[*].title` field with `is_default` exactly true
and a label in the prospective generic-label set `Personal`, `personal`,
`Default`, `default`. Do not retain which label is present. No other value
may be disclosed or excluded. Use the same pinned source/corpus, limits,
core-dump refusal and no-delivery rules. This read expires on return and
can justify only a later explicit field/type-scoped policy selection.

## Final version 2 scope

The follow-up found `rat` as a top-level integer, `sl` as a top-level boolean,
and `sid`/`session_id` as top-level strings. The other matched keys occurred
at `auth.organizations[*].role` and `.title`. All six remaining value-matched
files were explained by a selected generic title on a default organization.
No actual title, role, scope value or identity was retained. The final policy
can therefore address the full observed marker classes without dropping short
private strings by length or discarding unknown claims.

Extend the selected version 2 policy with exact field/type rules. Treat
top-level `rat` (nonnegative integer), `sl` (boolean), `sid`/`session_id`
(nonempty strings), and `scope`/`scp` (string or string list) as structural
field names. Keep session identifiers and unknown scope values guarded.
Recognize only the four named OAuth scopes, individually in a list or in a
canonical single-space-separated string. Treat the known auth account/user
ID and plan fields as structural only with string values, and organizations
as structural only with a list value. Keep account/user IDs guarded.

Within `auth.organizations[*]`, treat `role`/`title` as structural when strings
and `is_default` when boolean. Exclude only the five named role categories,
and only the four named generic titles when `is_default` is exactly true.
All other titles, unknown values, wrong-location/type content and private
occurrences of equal text remain guarded. These rules classify named structure
and generic administration categories, not arbitrary free-form identity text.
The version 1 behavior and historical observations remain unchanged.

Authorize extending the implementation/tests/contract to these final rules.
After focused tests pass, authorize one final bounded in-memory comparison on
the same real source and frozen 170-file corpus, under the existing no-value-
retention and no-delivery bounds. Verify all 13 positive controls, projection
equality and unchanged historical files again. This final comparison is not
permission for another diagnostic read, credential delivery or native run.

## Final local comparison and synthetic verification

The final implementation passed eight focused tests in 0.202 seconds. They
exercise both policies through real sealed-descriptor/Python-child handoff,
split decoded-claim quarantine, unchanged projections and source bytes, all
declared plan categories, non-ASCII private names, and token/identity markers.
The new protocol-metadata test failed before the full field/type rules existed
and then passed. Wrong locations and types, mixed scope lists, unknown roles/
scopes, custom titles, nondefault titles, a numeric default flag and private
occurrences equal to public categories all retain quarantine. A dictionary
key `*` does not acquire the list-element exemption.

The final authorized local read compared both implemented profiles against
the same source in memory. Version 1 quarantined 112 of 170 files; the final
version 2 quarantined zero. The selected files total 2,771,007 bytes and remain
byte-identical to the frozen diagnostic. All six small samples passed under
version 2, while version 1 retained its four earlier refusals. Both policies
caught all 13 split positive controls for complete credential material,
tokens, JWT segments and account/subject identity. Projection bytes were
identical. The five pinned source/test/tool files matched after comparison.

The result is `/tmp/caplab-quarantine-v2-final-comparison.json`; the complete
selected-file identities are in
`/tmp/caplab-quarantine-v2-final-comparison-selection.json`. This establishes
bounded compatibility for those retained file bytes and the declared samples,
not universal capture usability, arbitrary privacy protection or independent
identity selection. No real credential descriptor, native execution, provider
request or authentication occurred. Six separately scoped local reads were
consumed across diagnosis and comparison; none is a continuing allowance.

The earlier category-only candidate and its 86 refusals remain recorded. The
current profile does not retrospectively change any native attempt, captured
bytes, eligibility or failed transport result. Explicit administration
selection, complete-surface preflight and exact execution authority still
precede any real credential delivery. Account blinding and representative
repair/reviewer measurement remain unfinished.

The final full check exited zero: 1,499 tests in 288.172 seconds, with four
skips, using
`CAPLAB_TEST_WEBSOCKETS_ROOT=/tmp/caplab-native-transport-deps/websockets make check`.
Its log is `/tmp/caplab-quarantine-v2-full-suite.log`. Scoped Ruff formatting/F
checks and `git diff --check` passed. Source and tests remained at the pinned
versions used for the final local comparison and full check.

## Advisory and final custody verification

Final advisory packet `pkt-736249043fe1abf8` has content SHA-256
`736249043fe1abf8dcfcc597d67c7188ece0f7b85324dfd52f2dd589d97def1d`. Its corpus is
`corpus-2026-07-12-a11702cc9217`; retriever is
`retriever-ec995ecdd083b2c8`. The decision receipt is
`/tmp/caplab-quarantine-v2-decision-receipt.json`. Four typed evidence records
and the receipt passed schema validation; both packets have citation
classifications. Twelve missing obligations remain nonmaterial: five concern
unselected deep domain-model investment, four concern wider CI/toolchain
qualification not claimed here, and three concern expert identity judgments
not made here. Exact rationales are retained in
`/tmp/caplab-quarantine-v2-obligations.json`.

Final read-only verification matched all five source/test/tool pins and all
170 historical file hashes and sizes, including the original result anchor.
It rechecked the retained comparison predicates without reading the credential
source or executing another diagnostic. The verification result is
`/tmp/caplab-quarantine-v2-verification.json`.

Private verification manifest:
`/tmp/caplab-quarantine-v2-verification-manifest.json`, SHA-256
`3d1d0daac874e3b529abb3bd95704d3528ab7ce3418ba1590e941226863afa22`. It retains 49 artifact identities, the source pins and
historical selection locator; the historical capture itself is unchanged.
