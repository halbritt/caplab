# Prepare Codex child configuration from installation sources

Baseline `118b75c`. The primary agent acts under ADR 0026 and the continuing
CAPLAB goal. The previous goal turn completed reusable child execution linkage;
the intervening daily summary made no implementation change.

## Observation, decision and authority

The public child checker requires independently supplied child argv and
environment. The installed Codex 0.153.4 JavaScript launcher forwards argv,
resolves an optional platform package and rewrites package-manager variables.
Its package-manager detection depends on namespace paths and metadata as well
as environment. Matching observed trace strings cannot supply that independent
expectation. The existing startup capsule mounts the package at /opt/native and
links /toolbin/codex to its launcher, with empty capsule ancestors.

Select a closed preparation profile for these exact Linux x64 launcher and
package metadata bytes. Read those three files and the native binary using
bounded descriptor-relative, no-symlink access. Require an independent binary
hash from the caller. Rebuild the anchored launch using the existing canonical
policy. Produce the prospective native child argv/environment and source hashes
with explicit namespace assumptions. This verifies selected source bytes at
read time, not executable residence, Node identity, namespace conformance,
child PID authority, task success, full capture or a Binding.

Authorize a new codex_child_configuration module, focused tests, three exact
upstream source fixtures under tests/fixtures/codex-launcher-0.153.4, a fixture
provenance note, a product contract, and this record. The three fixture imports
are the current installed bin/codex.js, package.json and
node_modules/@openai/codex-linux-x64/package.json from
/home/halbritt/.npm-global/lib/node_modules/@openai/codex. These are test source
fixtures, not imported governing records or historical experimental evidence.
Preserve their exact bytes, package/version, original path and SHA-256. The
installed distribution supplies no source commit; record that as unavailable.

Authorize extracting existing launch validation into a shared private helper
without changing its semantics, checked before adding new preparation behavior.
Use TDD for exact configuration, source drift, unsupported installation layout,
wrong independent anchors, byte limits, descriptor cleanup and launch-profile
refusals. Execute the copied unchanged launcher with Node only in an isolated,
networkless Bubblewrap fixture whose child is a fixed Python observer. This
control is not a native agent attempt: no installed native binary, model,
credentials, provider, or task/review workload executes. Bound each control
with a ten-second deadline, output allowance, address-space and file limits;
reap only owned processes. Inspect the installed package read-only afterward.

Use /tmp/caplab-child-config-* for new private evidence, advisory packets and
verification. Run focused/full checks and commit locally. Preserve existing
public capture behavior, all historical evidence, unrelated docs/designs,
worktrees and services. No tracker write, push, deployment, message, independent
acceptance or study execution. Stop on unexplained failures or source drift;
authorization expires at the verified local commit.

Keeping a private literal transformation leaves source support unchecked.
Generalizing arbitrary launcher versions would require an unsupported semantic
interpreter. The closed profile refuses unknown source bytes; new versions need
a separately reviewed profile. The caller-selected binary hash identifies bytes
without asserting those bytes implement Codex correctly. Public startup adoption
and independent child selection remain later integration work for CAPLAB-84.


## Implementation and observed checks

The launch validator was extracted without semantic changes. All 12 existing
launch tests passed at that checkpoint. The source check expands the helper
back into its caller and verifies AST equality to baseline; prior builders,
dataclasses and child composition also have unchanged ASTs. Seven adjacent
capture/identity/trace sources remain byte-identical to 118b75c.

The first preparation test failed on the absent module, then passed. Seven new
methods cover owned output copies, exact source identities, both supported
launch profiles, altered metadata/launcher/binary, independent anchors,
rehashed launch injection, total byte limits, missing files, symlink directories
and files, FIFO refusal, package-manager metadata and descriptor restoration.
A separately selected fixture binary changes preparation identity without
claiming native execution. No internal function or filesystem operation is mocked.

The real control executes the exact imported JavaScript launcher with Node,
using a fixed Python observer as its child in a networkless Bubblewrap namespace.
The initial control exposed Bubblewrap's added PWD; a fixed same-PID Python
handoff now resets the exact launch environment before Node exec, matching the
public capture's environment ownership. Both canonical and scripted-local
profiles then produced exactly the prepared child argv and environment. The
control has a ten-second timeout, 64-KiB output/file limit, 16-GiB virtual address
space limit for Node's reservation, 64-MiB V8 old-space setting, no cores, all
namespaces unshared and all capabilities dropped. This is launcher semantics
verification, not an installed native binary or agent/model attempt.

The new read-only application verifies the original close diagnostic's manifest
and all artifact hashes before using its pre-release selected binary hash.
Current installed launcher, both package files and the 258,659,424-byte binary
agree with their original selected identities. Independently prepared child
argv/environment match the original guarded expectation. Only after preparation
does the script read the old trace and candidate PID and invoke the existing
child linker, which verifies the recorded zero exit. The new preparation hash is
084ef5f35d7abf49b1119bf579885895a4bc29a43b12dbb36a16ecea47f39533.
This post-run read is not retroactive prospective preparation, independent PID
authentication, executed-byte verification or namespace verification. Original
error dispositions and source evidence remain unchanged.

Test Guard and Docs Guard checks found no mock-based success substitution or
claims of complete capture. Source fixtures have exact original path/hash and
package/license provenance; the upstream source commit is explicitly unavailable.
Contract links resolve, Ruff F and diff checks pass. Plane still contains 86
items, 12 open; CAPLAB-84 remains In Progress. No tracker write occurred.

The full make check passes 1,406 tests with four skips in 168.890 seconds.
No runtime or test source changed after that run began. The test process
completed with exit zero; Python is 3.12.3, Node is v24.19.0 and Ruff is 0.15.17.
No broader runtime or CI matrix was tested.


## Advisory review and conclusion limits

The validated Doctrine release gate passes at release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Corpus is `corpus-2026-07-12-a11702cc9217`, Doctrine is
`doctrine-f6bbb5196a3f8bf9`, retriever is `retriever-ec995ecdd083b2c8`.
Initial packet `pkt-6250531edbd24748` and final packet
`pkt-8b1947586a96ef85` were read. Final content SHA-256 is
`8b1947586a96ef8536a29d9f90d3962723cbaf0d249c54709eddf3891e1e5243`.
Five typed records retain authority, source, incident, test and runtime evidence.

Applied concepts are repository-contract precedence, evidence before
intervention, authority-bounded action, preservation by default and separation
of semantic from structural change. Static launcher inspection and the real
launcher control justify the closed source profile; a matched execution trace
cannot justify its own expectation. The separate AST-equivalent extraction
checkpoint protects existing callers while the new reader adds source checks.

The final packet leaves 29 obligations unmet. Eighteen concerning deduplication,
bulk discovery, async UI, symbolic configuration references and top-N ranking
are nonmaterial: this module reads four fixed paths and changes none of those
mechanisms. Three monitoring obligations are nonmaterial because no service,
monitor or paging policy changes. Four external-capability obligations and four
authoritative-gate obligations remain material to full native execution/capture
and serving-parity claims, which are withheld. The source preparation is
explicitly conditional and provisional for those broader claims. No new
provider call, native binary execution or native namespace observation occurred.

The closed preparation profile and its bounded source verification are complete
for this scope. Independently observed runtime/namespace conformance, child PID
selection, public startup adoption, complete capture and representative repair
measurement remain open under the continuing goal. No roadmap completion,
reviewer qualification or independent acceptance is claimed.

Private manifest `/tmp/caplab-child-config-verification.json`, SHA-256
`b1d4f6123680ce7800aeb594fc0d4c3c43a909ebccb4b195f39f66f3a07d3cf0`,
seals 19 private artifacts, eight baseline/current source records and
8 implementation/test/contract/fixture files. Eleven advisory scratch files
were embedded, hash-verified and removed. All five used concepts classify as
valid packet citations. A first citation-envelope schema error was corrected
using the inspected schema; the refusal is retained.

This local commit expires the scoped implementation authorization. No push,
tracker write, historical evidence mutation or independent acceptance occurred.
