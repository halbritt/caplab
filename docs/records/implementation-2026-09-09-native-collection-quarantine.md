# Guard prospective persisted native collection

## Decision and authorization

The primary agent acts under ADR 0026 and the continuing CAPLAB improvement
request. At baseline `bfde286`, process capture accepts a trusted exact-secret
stream gate, but native collection copies selected files, literal symlink
targets, names, preparation and invocation receipts without that policy.
CAPLAB-84 requires restricted custody across the selected capture surfaces.

Authorize an optional `quarantine_factory` input to `collect_native_outputs`,
guarded copying in its existing task inventory owner, a bounded shared helper
for synchronous stream checking, focused synthetic collection tests, the native
collection contract and this record. Preserve process capture and its existing
protocol; do not change the legacy credential parser or exact-secret matcher.
This is a prospective feature, not historical evidence sanitization.

Check file payloads before writing with a separate fresh gate per file. Charge
received bytes against the existing shared quota even while a gate withholds
overlap. Flush only at actual EOF. Check raw filenames and literal link targets
before recording them, and check both serialized receipt bytes and their string
keys/values before writing. Check caller custody paths before creating output.
Successful guarded output must remain byte-for-byte raw and usable by existing
v1/v2 collection verification. A match, incomplete file, changed bytes, invalid
gate, cleanup failure or source change must prevent final publication. Retain
safe partial custody; do not retry, purge or fabricate a failure receipt.

The factory remains trusted caller-owned policy with bounded memory and runtime;
the helper owns each returned gate until abandonment on success or exception.
No whole-file buffering, text decoding of opaque payloads, redaction, encoded
secret search, secret zeroization claim, or gate identity claim in v1/v2 receipts.
Known literal symlink encoding is checked before base64; JSON strings are checked
before serialization escaping. Arbitrarily encoded content and fragments split
across separate fields/files remain outside exact-value protection. Original
source custody and caller exception/log handling remain caller responsibilities.

Authorize fabricated fixtures, private advisory and verification files under
`/tmp/caplab-collection-quarantine-*`, and focused/full local checks. Commit the
bounded change after verification. Preserve unrelated files including
`docs/designs/`, worktrees, services, credentials, provider configuration and all
historical evidence. No native/provider execution, model spend, credential read,
tracker write, outbound message, evidence registration or independent acceptance
is authorized. Implementation authorization expires at the verified commit.

## Alternatives and verification criteria

Leaving collection unchanged preserves a known unguarded write path in the
planned authenticated adapter. Checking after copying is too late to prevent
durable exposure. Buffering whole files would defeat bounded streaming. Reusing
the existing matcher through its protocol preserves credential-policy ownership;
a synchronous helper owns checking/cleanup while the inventory owns source
stability, quotas and filesystem writes. Process capture retains its separate
concurrent-stream lifecycle; no structural refactor of that working component.

Verify a secret across a real 65,536-byte read boundary, safe binary byte-exact
round trips through independent v1/v2 verification for both harness plans,
literal names/targets and escaped receipt strings, shared quota overflow,
gate transformation/invalid-state/cleanup failures and source/storage errors.
Run existing collection/task/process tests and `make check`. Stop publication
on unexplained failures. These checks establish a capture mechanism, not
full-surface privacy acceptance, authentication, complete native emission,
representative measurement or a roadmap completion.

## Execution and focused verification

The optional factory is now wired through native collection to its existing
inventory copier. A synchronous helper owns fresh gates, counts and hashes
received/emitted bytes, and abandons each gate on every exit. File reads and
quotas remain inventory-owned; metadata checks reuse the same helper. No
runtime import of the legacy credential provider was added. Tests instantiate
its existing exact-secret matcher with fabricated values only.

Twelve new public collection tests exercise real files and the independent
collection verifier. The first test failed because the input did not exist.
Subsequent vertical tests showed that guarding payloads alone still allowed
secret-bearing filenames, encoded symlink targets and escaped prompt strings.
Each failed before its corresponding guard was added. A later generated-name
test showed that checking the final receipt was too late to protect an object
locator already created on disk; generated and pending names are now checked
before creation. Retained failing outputs use the prefix
`/tmp/caplab-collection-quarantine-`: `red.log`, `name-red.log`, `link-red.log`,
`prompt-red.log`, and `generated-name-red.log`.

The focused run passed 92 tests in 12.551 seconds. Its log is
`/tmp/caplab-collection-quarantine-focused.log`. The new tests establish:

- A full fabricated secret spanning the 65,536-byte read boundary never reaches
  retained files; the source remains unchanged and collection is unpublished.
- Safe binary/Unicode payloads, an incomplete secret prefix at EOF, literal
  non-UTF-8 link targets and exact copied receipts survive both native harness
  layouts and both source modes. Independent v1/v2 verification succeeds even
  when descriptor collection uses a runtime moved away from its prepared path.
- Names, JSON keys, escaped prompt values, raw serialized receipt bytes, final
  metadata, generated names and caller output paths are checked at their write
  boundaries. A raw non-UTF-8 filename is checked before JSON escaping.
- Shared quota exhaustion charges received bytes and discards withheld overlap;
  prior safe artifacts remain and no final receipt is published.
- Invalid factories, invalid gate results, transformation, truncation, expansion,
  late quarantine, cancellation and cleanup failures prevent completion. Source
  mutation and storage-open failure also close descriptors and abandon gates.
- Explicitly disabling the option preserves raw unguarded copying, including
  the synthetic value that guarded collection would reject.

The native/source metadata claim ceilings and existing receipt formats remain
unchanged. This does not prove that an arbitrary supplied factory enforces the
intended secret policy. Its exact identity and configuration must be frozen by
the adopting adapter. A transforming gate can emit a changed prefix before EOF
exposes the hash mismatch; such partial custody has no completed collection.
No memory zeroization, arbitrary encoding detection or independent privacy
acceptance follows from these tests.

The live roadmap read at `bfde286` again found twelve open items, including
CAPLAB-84 In Progress and CAPLAB-80/85 Ready. The read-only snapshots are
`/tmp/caplab-roadmap-20260909-bfde286.json` and
`/tmp/caplab-roadmap-states-20260909-bfde286.json`. No tracker state changed.
The next integration still needs task-surface protection, policy provenance,
and the separately authorized authenticated native adapter before representative
repair measurement. This component change does not complete those items.

## Advisory provenance and review limits

The validated release gate verified source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Initial packet
`pkt-16e42ac30c478d6a` supplied obligations. Two typed-evidence passes covered
the authority/contracts, actual source ownership and executed regression tests.
Final packet `pkt-1607c27c331676a1`, retriever
`retriever-ec995ecdd083b2c8`, has content SHA-256
`1607c27c331676a1b26cd5a46c306d99684ec09d8e5b2824a8e83b9f6bb19e0f`.

Five obligations remain nonmaterial to this additive, local mechanism claim:
CI/build matrix, formatter/static-tool configuration, Python/dependency version
matrix, formatter/linter/type-checker configuration, and full repository
toolchain inspection. No toolchain or dependency change or cross-platform
qualification is claimed; the declared Python floor, neighboring implementation,
local static check and executed repository suite provide the bounded evidence.

Seven used concepts have valid packet citations: repository-contract precedence,
structured cleanup, text/bytes boundaries, mutable ownership, preservation by
default, evidence before intervention, and local reasoning. The helper isolates
trusted gate lifecycle from filesystem/source ownership while avoiding a second
secret matcher. Its synchronous lifetime differs from concurrent process capture;
the latter was left unchanged. Revisit the helper if the selected adapter requires
a different policy contract, rather than extending it into a general transform
framework. The decision remains CAPLAB-owned; advisory guidance creates no
execution authority or acceptance.

The review checked for silent fallbacks, unchecked callback results, lost raw
bytes, quota extension through buffering, leaked resources, and unsupported
completion claims. All errors propagate; tests do not substitute a successful
native run or accept the component as a complete measurement instrument.

## Final local verification

`make check` passed: 1,276 tests in 183.234 seconds, with four skips. Its log is
`/tmp/caplab-collection-quarantine-make-check.log`. Ruff's undefined-name and
unused-import check passed for all changed runtime files and the new test file;
changed documentation links resolve and `git diff --check` is clean. Runtime
and test sources remained unchanged throughout the full run.

The local verification script
`/tmp/caplab-collection-quarantine-verify.py` checked terminal focused/full logs,
the source identities retained by typed evidence and all seven citation
classifications. Private manifest
`/tmp/caplab-collection-quarantine-verification.json` has SHA-256
`18851a77d7c775d311a81ff3b4401a3d4019fe2e6704ae1008a8408533495574`.
It retains hashes for 23 artifacts and the final runtime/test/contract sources.
Twelve advisory scratch files were embedded byte-for-byte, rechecked, then
removed by exact filename; the red/focused/full logs and initial scope snapshot
remain separately addressable. No historical evidence was altered or purged.
