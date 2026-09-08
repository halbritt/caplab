# Compare retained Codex final-message and event bytes

Date: 2026-09-08. Baseline: `7a539e2`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add a final-message comparison API to `src/caplab/codex_capture_link.py`, new
focused synthetic tests, a versioned contract, this record and a link from the
existing Codex root-link contract. Preserve existing root-link behavior and all
current capture/parsing owners. Read the official OpenAI Codex `rust-v0.153.4`
final-file writer and JSON event processor at an identified commit; retain bounded
public source snapshots and hashes under `/tmp/caplab-codex-final-*` as advisory
implementation evidence, not imported governing authority. Use only new synthetic
task/runtime/collection bundles and local Python producers for verification.
Exercise exact bytes, empty/non-ASCII text, mismatches, missing and malformed
evidence, changed retained payloads, bounds and unsuccessful process outcomes.
Run focused/full checks and make a local commit. No native model or version
execution, credential/home reads, historical evidence changes, registration,
ranking, placement, tracker writes or external messages. Preserve `docs/designs/`,
worktrees, services, existing policies, profiles and launchers. Remove only named
doctrine scratch after consolidation; retain sources, probes and logs.
Authorization expires at commit. Stop if writer semantics require an unsupported
normalization or root field agreement is promoted to successful execution.

## Decision

CAPLAB-79's accepted capture decision requires the final artifact convenience
copy to agree with the native stream. The current root linker checks root and
tuple fields but does not inspect this selected artifact. Compose it with the
existing completed-turn final-message selector, then reread anchored retained
stdout and final-file bytes. Compare exactly, with no trimming or newline repair.
Keep process outcome, native completeness and execution binding separate.

## Source and implementation observations

The official tag resolves to commit `3d2ee51ca2d5db578f328aa75e20aa22c0197c9a`.
The writer in `codex-rs/exec/src/event_processor.rs` uses `std::fs::write` on
the supplied string. The JSONL processor records completed agent messages and
selects a final message on completed-turn notification. Its plan-only fallback
does not establish an agent-message event. This new API requires that event and
withholds agreement when it is unavailable; it does not reinterpret a plan as
an agent response. See the pinned links in the contract. Exact URLs, source paths,
byte counts and SHA-256 values are retained in
`/tmp/caplab-codex-final-source-provenance.json`, alongside bounded snapshots
of the writer and adjacent processor/test files. No native inference or Rust
source execution supplied this observation.

The new function composes existing root verification and final-event selection,
then rereads three anchored receipts, stdout and the final object. Descriptor
lifetimes use `ExitStack` and the existing stable, bounded byte reader. The same
independent anchors apply throughout; source task/runtime paths are not opened.
Caller-owned custody must remain quiescent because this is not an atomic snapshot.
Unique stdout, rollout and final bytes share the identity allowance. The repeated
stdout read and separate receipt passes are documented rather than hidden inside
a total-I/O claim. Parsed records and encoded text remain proportional to bounded
input; no concurrency, shared state or performance optimization is introduced.

The comparator preserves exact UTF-8 bytes, item ID and zero-based event index
while omitting answer text from its report. Earlier agent messages, tool output,
unrecognized plan-only output and a missing message cannot supply an alternative
answer. Whitespace and normalization differences remain differences. A matching
empty file requires an explicitly completed empty agent message. Process timeout
and nonzero exit remain in the embedded root report and cannot be cleared by a
matching convenience copy.

No change would leave an explicit capture-contract requirement unchecked.
Filename-only comparison lacks content evidence. Trimming or adding a newline
would hide discrepancies the inspected writer does not require. Reimplementing
the event selector or reopening source paths would duplicate settled behavior
or abandon retained custody. The selected integration makes one byte-consistency
claim; it supplies no quality, provider identity or complete-capture conclusion.

## Verification observations

The first focused run passed 29 tests in 11.216 seconds: it unintentionally
rediscovered the imported fixture's 17 existing test methods in addition to the
12 new tests. Importing the fixture module instead of its TestCase class removed
that duplicate discovery. The final focused run passed the 12 intended tests in
5.397 seconds. Logs: `/tmp/caplab-codex-final-focused.log` and
`/tmp/caplab-codex-final-focused-final.log`. No production behavior changed during
that fixture correction.

Tests exercise exact non-ASCII bytes after source removal, no read-side mutation,
empty and absent messages, added-newline disagreement, earlier-answer rejection,
missing final artifacts, incomplete/failed native events, aggregate identity-byte
boundaries, changed final payloads after root verification, and nonzero/timed-out
outer processes. The existing root API still succeeds on a valid root without a
final file; only the new comparison requires it.

A new retained Python-producer fixture lives at
`/tmp/caplab-codex-final-probe-fko7r3j2`; report
`/tmp/caplab-codex-final-probe.json`. It is reproducible through the new test
fixture's `build` and `link` methods and uses synthetic native-format metadata.
Attempt anchor: `ba48d6208c3668848054165cb28da67a27842c57981a3f65f95bdd9a5d15cc92`.
Collection anchor: `94c60d4c9dae8094251a2581940024b6d1238b1da8916b8639b1460d4e8c4a2d`.
It matches 15 final-file bytes at event index 3, item `final`, with 678 unique
identity bytes and 4,480 comparison receipt bytes. The root report still has
unverified child linkage, execution binding and native completeness. This is
mechanics evidence, not a native response or reviewer measurement.

`/tmp/caplab-codex-final-source-check.json` records source/test hashes, Python
3.12.3 and direct-import checks with none unused. Both pre-existing functions
in the modified module have identical ASTs to baseline; thirteen protected files
are byte-identical. Existing event, rollout, collection, task, version and Claude
behavior, policy, profiles, launcher and toolchain settings remain unchanged.

Full `make check` passed 1,121 tests in 187.531 seconds, four skips, exit zero:
`/tmp/caplab-codex-final-make-check.log`. Source/test hashes still match the
recorded check and all thirteen protected sources were compared again to baseline.
No source or tests changed during the full run. Documentation links resolve;
the contract's comparison, missingness, budget and claim rules were checked
against the implementation and tests.

## Advisory doctrine

Release retrieval state passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-fae7862a41689ffb`, SHA-256
`fae7862a41689ffb97225a5ac661cffea58a8f70a08ebde6cfd5ca588edd98a1`,
uses `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9` and
`retriever-ec995ecdd083b2c8`. One evidence-gathering pass supplied five typed
records. Four citations classify as valid: `python-text-bytes-boundary` for
exact encoding and comparison, `python-structured-cleanup` for descriptor
ownership, `universal-preserve-behavior-by-default` for the existing root API,
and `agent-conduct-authority-bounded-action` for agreement without eligibility.

The packet also activated concurrency and performance guidance. No optimization
or concurrency change was selected. Its 23 unmet obligations are all nonmaterial
to this correctness feature, classified by group below; the consolidated
verification JSON retains every exact requirement and classification.

| Concept | Unmet count | Classification and rationale for every requirement in the group |
| --- | --- | --- |
| `implementation-repository-language-conformance` | 2 | Nonmaterial: CI/build matrix and formatter/static-tool configuration are unchanged; no new platform or tool qualification is claimed. |
| `python-repository-shaped-idiom` | 1 | Nonmaterial: formatter/linter/checker configuration is unchanged; current neighboring capture interfaces are reused. |
| `python-concurrency-model-selection` | 6 | Nonmaterial: no concurrency model, deployment or performance target is selected. Existing synchronous readers remain synchronous; local interpreter and failure tests are recorded without claiming a workload profile. |
| `performance-measurable-objective` | 5 | Nonmaterial: no performance intervention, target, representative workload or resource tradeoff is selected. Byte allowances enforce caller-specified correctness bounds. |
| `performance-metric-semantics` | 5 | Nonmaterial: no benchmark or profiling inference is made. Reported byte counts have the contract's direct retained-byte semantics; they do not estimate overhead or population performance. |
| `performance-representative-baseline` | 4 | Nonmaterial: no before/after speed, capacity, variance or efficiency claim is made. The preserved baseline concerns source behavior and the absent comparison only. |

## Completion of this implementation scope

`/tmp/caplab-codex-final-verification.json` consolidates source provenance,
synthetic probe, AST/source checks, focused/full results, doctrine identity,
citations and all unmet obligations. It records the exact paths and hashes of
eleven doctrine scratch files removed after consolidation. Source snapshots,
synthetic custody and execution logs remain retained.

This implements final-file agreement where a completed native agent-message
event is available. It does not complete the capture instrument or broader goal.
Plan-only output remains unverifiable by this comparator. Full invocation and
child linkage, native capture compatibility/completeness, runtime storage bounds,
and representative legibility, blinding and reviewer-quality evidence remain
required. No native execution, evidence admission, reviewer selection, or
independent acceptance is recorded.
