# Compare overlapping retained capture surfaces

Baseline `57a0bf5`. The previous goal turn made progress by enforcing native
request configuration. Under ADR 0026, select a bounded consistency comparison
for CAPLAB-79/84 capture integration. The existing shared `inspect_custody`
verifies task, selected native collection and retained writable mounts
separately, but does not compare their overlapping entries. Two individually
valid bundles can therefore disagree about the same final source path.

Authorize a pure comparison helper in `src/caplab/capture_overlap.py`, its
integration after existing verification in `scripts/probe_native_capture_startup.py`,
focused tests using existing real isolated synthetic capture producers, a
contract and this record. The scripted native inspector already calls that
shared custody reader; it must receive the comparison through that actual path.
Compare final task entries against the full retained task mount, and each
selected native location against its corresponding retained runtime subtree.
Require matching path sets, kinds, modes, file lengths/hashes, literal symlink
targets and recorded source metadata. Object locators differ between copies
and must not be compared. Missing selected locations must also be absent from
the corresponding retained runtime path. Preserve valid empty locations and
unselected runtime files without classifying either as missing capture.

The helper consumes already independently verified receipts, not arbitrary
untrusted inventory claims. The caller retains ownership of anchors, all
payload verification, source/mount linkage, custody quiescence and limits.
The comparison establishes only overlapping-entry agreement. It cannot prove
exhaustive emission, intermediate writes, temporal atomicity, containment,
source authenticity, provider identity, task correctness or study eligibility.

Use newly constructed fixture bytes only, including binary/non-ASCII content,
mode changes, symlinks, selected-subtree omissions/additions and false missing
locations. Exercise real task/native/mount copies after their original sources
are removed. A valid-but-conflicting payload must pass its own integrity
verifier and fail the comparison. Preserve prior failure, quota, missingness,
quarantine and execution-link semantics. Run focused and full checks and commit
only this scope. Fixed local process controls inherit existing bounded fixture
limits; no installed native agent, model call, paid call or provider access.

Authorize a separate read-only comparison of the exact prior native capture at
`/tmp/caplab-wire-identity-native`, source provenance `57a0bf5`, result SHA-256
`e119660e7c3be488184d799e0523271ce7534f5e463ab35946388a2b23d22c36` and
preparation SHA-256
`9aa8ab28f22ae3b420580a77c2782e854f848e04978fadcdf50e316b38a0bd31`.
Verify its anchored manifest before interpretation. Preserve all original
captures/results and name the new comparison's source and method; do not
replace the earlier verification, register evidence, or claim this reader ran
during capture. No historical bytes are copied into public tests or fixtures.

Private verification/advisory artifacts use `/tmp/caplab-capture-overlap-*`.
No tracker write, message, push, unrelated cleanup or old attempt reuse.
Stop on unexplained disagreement or any unclear source/custody boundary;
do not remove metadata from the criterion merely to make a capture pass.
This scope expires at the verified local commit. The wider shakedown and
reviewer-capability goal remain incomplete.

## Implementation and verification

The pure helper translates selected source paths to relative subtree paths and
compares canonical entry documents after excluding each copy's path and object
locator. It borrows inputs unchanged. The shared custody reader invokes it only
after existing task/native integrity checks, mount/source linkage and all five
retained-mount payload checks. Anchored final-task and native receipts are reread
with bounded no-follow readers. The resulting `overlap` field is part of the
existing scripted native inspection path; there is no disconnected acceptance
helper or new producer behavior.

Five focused methods pass. The first test initially failed because the helper
did not exist. Real isolated Python producers exercise Codex and Claude-format
copies after original source removal, including nonzero exit, binary bytes and
a literal non-UTF-8 symlink target. The test producer gains only an optional
explicit extra-link mapping for those constructed fixtures. A changed final
file, rehashed into its collection receipt, passes the existing independent
native integrity verifier and fails overlap comparison. This demonstrates why
valid individual copies are insufficient.

Constructed metadata cases reject changed modes, source timestamps, link
targets, task/native omissions and additional native subtree entries. Missing
locations must disappear from both copies; empty retained directories remain
retained. Namespace-prefix and object-locator cases distinguish source paths
from copy storage paths. These pure comparison cases do not independently
establish custody integrity; the separate changed-payload case and real fixture
round trips provide the retained-file checks. Existing failure, byte accounting
and native identity semantics are preserved.

The separately authorized read-only native inspection verified the original
result/manifest, all existing predicates and the new comparison. Its output
SHA-256 is
`6356abd293ea4daff5c671b19818df0b857d19fafcfcf190963a39014b8ba088`.
The task's two entries agree. Native locations contain one diagnostic-directory
entry, one final-message entry and five session-tree entries, all agreeing with
retained `/episode`. The original inspection retains SHA-256
`c898a107e6a3427c1c52330bd977b4f5976d5aee6c970c98e82ce187b58ae9ce`.
Removing only the added `custody_checks.overlap` field from the new result gives
the original JSON exactly. Formatting the new helper and rerunning read-only
inspection produced byte-identical output. No native agent was executed, and
the prior failed attempt/socket-close classification remains unchanged.

Leaving separate verification unchanged permits contradictory copies to pass
aggregate inspection. Comparing only byte totals misses equal-length changes;
comparing only shared paths misses omissions. Select full overlapping path-set
and entry comparison while preserving unselected files and unavailable
locations. This is a prospective inspection-semantic repair under the stated
authority, not a change to old capture bytes or a completeness declaration.

## Advisory review and limits

The Doctrine release gate verified commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-e875de124826a9cb` was reassembled in two evidence passes.
Final packet `pkt-05eebdefe6020946`, content SHA-256
`05eebdefe6020946570b28b968492e1973a9c6f7bbf27d533c33e083db38d62e`,
uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
All 34 typed-evidence provenance references matched the inspected bytes.
The record at advisory time is preserved separately before these additions.

Applied explicit invariants and failure policy, literal text/byte boundaries,
borrowed-input ownership and local reasoning from the initial packet. The final
packet supports exact population scoping, checks against authoritative receipt
entries, repository-contract precedence, evidence before intervention,
separation of semantic and structural changes, and bounded authority. Eleven
concept citations classified as valid packet citations. The two retrieved
conflicts favor the demonstrated consistency repair while leaving adjacent
structure and unresolved study architecture unchanged.

The final packet retains 23 unmet obligations, classified as follows:

- Fourteen concern database deduplication keys (three), asynchronous UI phases
  (four), symbolic configuration references (three), and ranking/truncation
  (four). All are nonmaterial: this change adds none of those operations and
  compares the complete overlapping entry sets without selecting top results.
- Four concern verification against an actual external device or endpoint.
  They are nonmaterial to this reader-only repair: it changes no native
  producer, protocol or external capability. Actual retained native inputs
  passed the integrated reader. No new live execution or provider capability
  is established by that read-only observation.
- Three concern operational paging and monitoring. They are nonmaterial to
  the bounded offline comparison; no monitoring service or alert changes.
- One requests a general latent security, safety, data, durability and
  compatibility check. It is nonmaterial to this narrow comparison claim.
  The tests cover conflicting bytes, metadata, paths and missingness, and the
  caller retains existing custody checks; no exhaustive risk audit is claimed.
- Evaluation-versus-serving configuration parity remains material to the
  broader measurement goal and is not established here. Abstain from study
  eligibility, representative serving behavior or reviewer-capability claims.

## Final verification

The full suite ran 1,444 tests in 173.274 seconds, with four skips and no
failures; `make check` exited zero. The retained log is
`/tmp/caplab-capture-overlap-make-check.log`. Five focused methods passed,
and Ruff F and diff checks passed. The reviewed runtime and test bytes match
their evidence hashes. Only documentation and private verification records
changed after that full run.

The regression uses an actual conflicting file whose independent collection
verification succeeds. The other mutation cases explicitly test the pure
comparison contract, without pretending their altered metadata independently
passed every custody predicate. The fixture extension supplies literal
symlinks through the existing isolated producer. No internal helper is mocked.
The documented caller, limits, error and result fields match the source.

The previous status-summary turn added no implementation progress. This turn
completes review and custody for the pending repair. The representative
shakedown and the full reviewer-capability goal remain incomplete; no roadmap
item, acceptance judgment or study readiness is inferred from these checks.

The private verification manifest is
`/tmp/caplab-capture-overlap-verification.json`, SHA-256
`e14632fd3253471006bf847a5dfec41217bc1ce2c9431a0cccc33630cef184de`.
It anchors 29 artifacts and 166 current source/configuration/test/contract
files. Seventeen advisory packet, evidence and citation files were embedded
byte-for-byte, verified, then removed by exact path. The pre-manifest record
and advisory-time snapshot remain recoverable. Original native capture bytes
were neither copied into this manifest nor changed; their existing result
anchor and the separate read-only comparison identify that evidence boundary.
