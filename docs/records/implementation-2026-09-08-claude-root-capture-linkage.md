# Link retained Claude root session observations

Date: 2026-09-08. Baseline: `9b65e8c`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add a Claude-specific retained root-session parser and capture linkage API in
`src/caplab/claude_capture_link.py`, focused synthetic tests, a versioned contract,
this record and a link from the native collection verification contract. Read
the official Anthropic session reader and its tests at an identified source
commit; retain a bounded public source snapshot with its URL and SHA-256 under
`/tmp/caplab-claude-link-*`. It is implementation evidence, not imported governing
authority. Use existing bundle verification and retained bytes only. Exercise
new synthetic task captures, preparations and collections using a local Python
producer, including conflicting IDs, child scope, missing and malformed evidence,
budget exhaustion, tampering and incomplete processes. Run focused and full
checks; record results and make a local commit. Preserve existing native policy,
profiles, launchers, Codex behavior, historical evidence, `docs/designs/`, sibling
worktrees and services. No native inference, SDK installation or invocation,
native home or credential reads, registration, ranking, placement, tracker writes
or external messages. Retain source snapshots, probes and logs; delete only named
doctrine scratch after consolidation. Authorization expires at commit. Stop or
narrow the claim if root interpretation requires an unsupported format assumption,
if identity agreement is treated as execution binding, or if preserved files need
changes outside this scope.

## Decision and claim boundary

Require agreement between the configured Claude session UUID, captured root
stdout session observations and one exact retained root transcript candidate.
Validate transcript bytes strictly and distinguish root from child observations
using the official persisted reader's field vocabulary. Report field agreement
only. Keep process completion, native capture completeness, model/effort
attestation, executed-invocation binding and child linkage separate. The SDK
source informs a parser; the measured native harness remains Claude Code.

## Source observations and implementation

The official Anthropic Python SDK reader was inspected at commit
`f1315c69a74db1c15fed2e5974918495d90b7d57`. The retained public source
`/tmp/caplab-claude-link-official-sessions.py` is 71,480 bytes with SHA-256
`c885b89b741d190fc081a2a8e793e2c6e2affd0bc4bbf3e75facf20091e06551`.
Its `tests/test_sessions.py` snapshot is 77,117 bytes, SHA-256
`a3f5925267863f751cb71d29f158c878160438ea9113ddc7f5e07a3ef2c15fe7`,
at `/tmp/caplab-claude-link-official-tests.py`. Exact source URLs, commit and
hashes are in `/tmp/caplab-claude-link-source-provenance.json`. The field mapping,
visibility predicate, chain selection, project/session locator and fixture
builder were read. The SDK is not installed in the observed Python environment;
no SDK code or native harness was executed for this inspection.

The source supports field names and root/non-root distinctions. Its convenience
reader skips malformed lines and reconstructs one conversation branch. CAPLAB
instead rejects malformed retained JSONL and compares explicit fields across
the selected file. It does not reconstruct or certify the conversation chain.
This is an intentionally narrower and stricter contract; source inspection is
not live compatibility evidence for the installed Claude CLI.

The new module composes existing bundle verification, receipt and stable-file
readers, and existing Claude stdout session observation rules. It borrows the
already-tested `_retained_bytes` helper from `codex_capture_link`; that helper
only checks bounded file bytes and hashes and performs no Codex interpretation.
The small shared mechanism is reused without changing the established Codex API
or moving its behavior in this feature checkpoint. Native-specific selection
and result semantics remain in separate linkers. Joint metadata read sequences
remain explicit; broader extraction needs its own preservation checkpoint if
future capture consumers justify it.

Byte inputs are borrowed and never mutated. Parsed records and result dictionaries
are local to each call, with no stored/shared state. Descriptor owners are scoped
by `ExitStack`; errors propagate after cleanup. Receipt and payload bounds precede
accumulation. No concurrency is introduced. Scope flags are validated at runtime
instead of accepting Python truthiness or treating annotations as validation.
UTF-8 decoding and LF splitting preserve non-ASCII text without interpreting
message contents as identity evidence.

No change leaves Claude custody disconnected from explicit root observations.
Filename-only selection cannot detect a conflicting body. Reusing the SDK's
convenience reader would lose malformed records and introduce a branch-selection
claim this function does not need. Reopening source homes would abandon retained
custody. The selected addition consumes already-retained evidence through one
bounded public API; it changes no launcher, policy, dependency or runtime state.
The benefit claimed is an executable field-consistency check, not improved model
discrimination, a completed Binding or maintainability measured from churn.

## Verification observations

Initial focused tests passed: 27 tests in 4.458 seconds, exit zero, log
`/tmp/caplab-claude-link-focused.log`. The suite exercises root/child scope,
missing and conflicting IDs, init placement, strict JSONL, non-ASCII content,
filename ambiguity, symlink and nested candidates, independent anchors, changed
payloads after initial verification, exact byte budgets and source removal.
It also preserves process timeout/nonzero outcomes separately from ID agreement.
Missing parent links remain unverified rather than being repaired or reconstructed.

The local Python producer at `/tmp/caplab-claude-link-probe.py` retained a new
synthetic capture under `/tmp/caplab-claude-link-probe-uepmasx8`. Its report is
`/tmp/caplab-claude-link-probe.json`; independently retained anchors are also
stored in that new probe root. Attempt SHA-256:
`d1a5b6cd074c273277df79f72656a77c3f00e1ec2e4ec9a1fbb9c9090eb797a9`.
Collection SHA-256:
`624507f0139502a7fae18dee4181fd3db60d09f502f1e7bdecbd2d6b2b16e07a`.
It compares 269 identity bytes, verifies 9,438 initial receipt bytes and rereads
8,560 metadata bytes. The exited process returns zero and has complete streams;
tuple attestation and native completeness remain null, and execution binding,
conversation-chain verification and child linkage remain false. The producer is
Python, and the metadata is synthetic; this supplies no native emission or
reviewer-capability evidence.

The final focused run after helper reuse passed all 27 tests in 4.215 seconds:
`/tmp/caplab-claude-link-focused-final.log`. Reinspection of the same retained
probe yielded an identical whole report; see
`/tmp/caplab-claude-link-probe-final-check.json`. Source/test hashes, direct-import
checks and thirteen protected-source comparisons are recorded in
`/tmp/caplab-claude-link-source-check.json`. No unused direct imports were found.
Python is 3.12.3; project minimum remains 3.12. No dependency, interpreter,
formatter, checker or CI settings changed. Local documentation links resolve,
and the contract was checked against the implemented field and failure rules.

An initial full `make check` passed 1,096 tests in 181.630 seconds with four skips,
exit zero: `/tmp/caplab-claude-link-make-check.log`. The small byte-reader reuse
occurred during that run, so it is not treated as final-source suite verification.

## Advisory doctrine

Release retrieval state passed for commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-0a5516c0e7566036`, SHA-256
`0a5516c0e75660365b3fc78da0d512b65af0789cdee8b4db4634bac7e0822532`,
uses `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9` and
`retriever-ec995ecdd083b2c8`. The question nominated no precise concept;
baseline, routed, prerequisite and kernel guidance remains advisory. One
evidence-gathering pass supplied five typed records. Four citations classify as
valid: `python-text-bytes-boundary` for strict UTF-8/LF interpretation,
`python-structured-cleanup` for descriptor ownership, `python-mutable-ownership`
for borrowed immutable bytes and locally owned parsed records, and
`agent-conduct-authority-bounded-action` for the explicit field-agreement ceiling.

Six unmet obligations are nonmaterial:

- `implementation-placement-by-ownership`: `recurring change evidence when available`;
  this adds a consumer required by the capture work, without a churn or measured
  maintainability claim.
- `implementation-repository-language-conformance`: `CI and build matrix` and
  `formatter and static-tool configuration`; these are unchanged and no new
  platform or tool qualification is claimed.
- `python-repository-shaped-idiom`: `formatter linter and type-checker configuration`;
  existing capture interfaces and tools are retained, without checker proof.
- `python-runtime-static-boundary`: `annotation maintenance cost` and
  `configured checker and Python version`; no annotation-cost or static-proof
  claim is made. Local Python execution is recorded separately.

## Completion of this implementation scope

Final-source `make check` passed: 1,096 tests in 160.686 seconds, four skips,
exit zero, log `/tmp/caplab-claude-link-make-check-final.log`. Source/test hashes
still match the final source inspection, and all thirteen protected files were
compared again with `9b65e8c`. The final run had no source or test edits.

`/tmp/caplab-claude-link-verification.json` consolidates source provenance,
probe reports, source checks, both focused and full runs, doctrine identity,
citations, unmet obligations and the exact hashes/paths of eleven doctrine
scratch files removed after consolidation. Public source snapshots, synthetic
custody, probes and logs remain retained.

This completes the bounded Claude root session field-comparison implementation.
The larger goal remains incomplete. Live compatibility, model/effort/version
attestation, child and conversation lineage, actual invocation binding,
containment and study readiness remain unresolved. These checks do not authorize
a native attempt, qualify a reviewer, record human judgments or supply independent
acceptance of this implementation.
