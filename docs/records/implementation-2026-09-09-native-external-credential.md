# Prepare explicit external-token administration for native repairs

Baseline `215c2d3`. Restricted provider TLS has been verified, but authenticated
native repair execution remains unavailable. The old Revbench credential guard
is governed by its original execution contract and must not be weakened to
admit a different current cache or administration. Prior native diagnostics
showed that the installed CLI accepts fractional refresh timestamps and
external-token mode, with no refresh request in the bounded external-token
401 control. Those observations do not authenticate the current account.

Under the continuing owner goal and ADR 0026, authorize one metadata-only read
of `/home/halbritt/.codex/auth.json` before selecting a new administration
mechanism. Open without following a symlink; require a regular file owned by
the current UID, mode 0600, one hard link and at most 64 KiB. Require stable
descriptor/path identity and metadata around the bounded read. Parse only in
memory, with duplicate JSON keys refused. Do not retain or hash raw credential
bytes, token segments, claim values, account/subject identifiers or unknown
field names. Do not run the native CLI, refresh, deliver credentials, create
a credential memfd or contact any endpoint.

Retain only allowlisted shape and compatibility observations under
`/tmp/caplab-external-credential-*`: authentication-mode enum; exact expected
top-level/token field-shape booleans; API-key presence; token-string presence;
refresh-timestamp format class; access and ID token JWT-shape/required-field
type booleans; unsigned expiry as past/not-past/absent; and equality booleans
for subject/account claims where those named claims exist. Never retain an
arbitrary parser exception containing source data. Stop with a fixed generic
error if safe parsing or source stability cannot be established. This one
read supplies local format evidence only and expires when it returns.

No new runtime behavior, real credential delivery, native/provider request,
study, spending, historical custody change, tracker write, human judgment or
external message is authorized by this initial inspection. Preserve the old
guard, all existing profiles and attempts, `docs/designs/` and other services.
Any selected implementation must receive a prospective scope below before its
effects occur.

## Metadata observation and implementation selection

The one local read found the expected managed ChatGPT cache shape, no API key,
all four token strings, a fractional UTC refresh timestamp, an expired ID-token
claim and a not-past access-token claim. Both JWT payloads have integer issue/
expiry fields and nonempty issuer/subject fields. Their subjects agree, and
both named account claims agree with the cache account field. No claim value,
token bytes or source hash was retained. This remains unsigned local metadata,
not authentication or an account-capacity observation.

Select a separate external-token delivery API for future repair administration.
Its caller supplies independently expected source, account and subject hashes
in private administration context. A bounded owner-only source read must match
them, validate the exact managed cache and named claim relationships, and
require enough remaining access-token lifetime for the caller's deadline.
ID-token expiry remains metadata in this explicit profile; it does not establish
bearer-token validity. Require well-formed UTC refresh metadata, including the
currently observed fractional form. Preserve original token bytes and identity;
do not fabricate a JWT, refresh token or provider response.

Deliver a native `chatgptAuthTokens` document in sealed anonymous memory with
the refresh token removed. Expose only its borrowed descriptor and a fresh
exact-byte quarantine factory. Keep the original credential source untouched
and do not persist the projected document, token/claim values or source/identity
hashes in public capture records. The caller owns execution authorization,
deadline, isolated read-only native mount, account administration and cleanup.
No default API caller or historical Revbench behavior changes.

The quarantine set must include complete input/output token material, JWT
segments, source refresh token, account/subject identity and nonempty textual
claim values, including nested values. Treat standard JWT structure/issuer/
audience fields as protocol metadata rather than private identifiers; opaque
claim keys and other textual leaves remain guarded. Numeric and boolean
custom leaves are not unique secret strings. This is exact-byte credential/
identity quarantine, with possible false positives, not arbitrary PII redaction,
transformation detection, memory zeroization or exfiltration certification.
Keep this narrower claim explicit; do not weaken the older guard's contract.

Authorize one new module, focused tests, a contract and this record. Test only
new synthetic owner-mode files, identity/source mismatch, expired access,
malformed metadata, unsafe filesystem sources, sealed descriptor lifetime and
cross-process quarantine. Test real descriptor and process boundaries with
bounded local Python children. No actual credential may be read again or
delivered by this implementation scope. No provider, model or native CLI
execution is selected here. Run the required full checks, retain private
verification/advisory evidence, commit and push; authority expires at that
verified commit. Existing profiles, the Revbench guard and all historical
custody remain unchanged.

## Implementation and bounded verification

Added `caplab.codex_external_credential` and its
[versioned contract](../product/contracts/codex-external-credential-v1.md).
The implementation uses the existing sealed-memfd owner and exact-byte stream
quarantine without changing them. Expected source/account/subject hashes are
required arguments; file/source validation and JWT relationship/lifetime checks
run before anonymous credential creation. Both token byte strings remain
unchanged in the projection; the managed refresh token is omitted from the
native document but retained among private quarantine markers.

The first public-API test failed because the module did not exist. It then
passed sealed delivery with an expired synthetic ID token, a valid access
window and a nanosecond fractional refresh timestamp. A later refusal test
found that JSON exponent notation `1e999` could decode to a non-finite custom
number even when explicit `Infinity` was refused. A finite-float parser now
rejects both. The test initially also had a secondary assertion-context error
after its failed subtest; that test bookkeeping was corrected without changing
the credential criterion.

Four focused tests passed in 0.124 seconds. They cover descriptor seals and
closure, unchanged source bytes, source/account/subject mismatch, account-claim
disagreement, insufficient access lifetime, malformed/duplicate/non-finite JSON,
invalid calendar metadata, unsafe mode, hard links, symlinks and consumer-error
cleanup. Real Python children read the projected input through an explicitly
passed descriptor; a split decoded-claim echo triggers the shared quarantine.
Retained capture files contain none of the checked synthetic private markers.

A separate retained control at `/tmp/caplab-external-credential-control` pins
six source/tool files and repeats successful descriptor handoff and quarantined
claim echo with newly fabricated credentials. Its safe child exited zero with
complete streams. The original synthetic source was unchanged, the descriptor
closed and the descriptor population was preserved. Source pins still matched
after the control. No actual cache was loaded through the new API, no credential
was supplied to a native CLI, and no provider request was made.

## Preservation and remaining work

This is a separate administration component, not a repair of the old Revbench
guard. Existing execution contracts, native profiles, persisted custody and
default callers retain their behavior. New native preparations will pin the
added source in their normal prospective implementation inventory; historical
preparations keep their original source versions. Reverting the new component
and its contract is the rollback route before adoption.

The descriptor carries the selected external-token cache only while its owner
context is open. It is not an account registry, authorization token, verified
provider identity or evidence-admission receipt. It makes no memory-erasure
claim, and ordinary code can still hold Python references after context exit.
There is no new background process, persistent file or dependency.

Actual source compatibility and quarantine false positives remain unmeasured.
Short textual claims or generic claim keys can stop otherwise ordinary capture;
the interface does not silently discard those markers. A future native profile
must verify the selected real administration, native parsing/serving behavior,
capture usability and deadline before a representative repair. The route's
exact IP/port policy is also not hostname enforcement; TLS connectivity alone
must not be promoted into provider-only hostile-containment acceptance.
CAPLAB-80/84/85 and representative reviewer/repair measurement remain incomplete.

The full check exited zero: 1,493 tests ran in 294.653 seconds with four skips,
using `CAPLAB_TEST_WEBSOCKETS_ROOT=/tmp/caplab-native-transport-deps/websockets make check`.
The output is `/tmp/caplab-external-credential-full-suite.log`. Scoped Ruff F
checks and `git diff --check` passed. The source was formatted before the full
suite and the retained process control; later changes only document results.

## Advisory and retained verification

The final advisory packet is `pkt-c6e880ba77578102`, content SHA-256
`c6e880ba7757810280311a29bd04cef9a2424938fad512622a7ac09c261de1f8`.
It uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
Four typed evidence records and the decision receipt were schema-validated;
both initial and final packets have concept and source citation classifications.
The receipt is `/tmp/caplab-external-credential-decision-receipt.json`.

Eighteen missing obligations remain classified as nonmaterial in
`/tmp/caplab-external-credential-obligations.json`: five concern an unselected
deep domain-modeling investment, six concern dynamic mechanism escalation not
introduced here, four concern broader CI/toolchain qualification not claimed,
and three concern expert-owned identity judgments not made by this component.
There is no material missing obligation for the bounded synthetic verification
claim. The advisory does not authorize native adoption or establish acceptance.

Readback verified all six control source pins, the safe child's retained stream
lengths and hashes, and every typed evidence provenance hash. The quarantined
child remains an unavailable capture, not a complete successful stream.
The private manifest `/tmp/caplab-external-credential-verification-manifest.json`
pins 39 artifacts and the six source/tool files; its SHA-256 is
`1bba19d4e1abef8a3a9163d5af789fd795cbaf043a800b533fc1c1fec8e75e7a`.
It excludes this final record to avoid a self-referential hash. These retained
controls contain fabricated credentials only; no real credential projection
has been retained or delivered.
