# Inspect tool-pair evidence through an anchored task capture

Date: 2026-09-08. Baseline: `1477c26`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Extend `src/caplab/native_tool_pairs.py` with a capture-backed inspection API.
Add `scripts/captured_tool_pairs.py`, `tests/test_captured_tool_pairs.py`,
`docs/product/contracts/captured-tool-pairs-v1.md`, this record, and a link
from `docs/product/contracts/native-tool-pairs-v1.md`. These six files are the
only edit targets. Use the existing task-capture verifier and descriptor reader
to follow an independently retained attempt digest to its exact stdout bytes.
Keep the pure parser and existing raw-file CLI behavior unchanged.

Integrity failures must raise before any pairing report. Verified captures
whose stdout exceeds the parsing allowance or cannot satisfy the native event
contract must return an explicit unavailable observation with no pairing counts.
Retain task termination, return code and completeness even when pairing is
available. Never equate capture integrity with native execution linkage,
complete native events, successful work, blinding or study eligibility.

Run newly authored local Python fixtures through real bounded task capture;
they emit synthetic native-shaped stdout and make only bounded writes in fresh
temporary task roots. No untrusted task code or native/model call. Include
failed exits, byte truncation and timeout; at most five seconds and 64 KiB
streams per fixture. Remove only newly created task roots after sealing, and
inspect from retained custody. Retain probe custody and source/authorization
snapshots under `/tmp/caplab-captured-pairs-*`. Run focused tests and `make check`
with its existing prescribed read-only store checks. Consolidate advisory
provenance before removing only named advisory scratch. Commit locally;
authorization expires at commit. Stop on wider required effects.

Preserve existing capture and integrity owners, raw historical evidence,
unrelated `docs/designs/`, worktrees, services and timers. No historical
transcript read, copy, migration or admission; no study run, coder exposure,
score, ranking, tracker mutation, external message or push.

## Decision and preservation boundary

The current tool-pair report checks a supplied stdout hash. That is useful for
an independently identified file, but does not follow the attempt receipt chain.
This integration supplies that missing relationship while retaining the existing
verifier's failure and resource semantics. Implement it alongside the current
report owner, using the existing low-level reader rather than a second custody
parser. A native invocation proof would require different evidence and is not
inferred from this relationship.

Rejecting every incomplete process would discard useful observations and hide
missingness. Treating unparseable bytes as an empty event list would fabricate
zero activity. Instead, verify integrity first, then report pairing availability
and its reason separately from the recorded process outcome. The caller still
supplies expected native format and root ID; these values are not selected from
the same stream to make a mismatch disappear.

## Implementation and focused verification

`inspect_captured_tool_pairs` first verifies the whole task bundle, then
rereads the independently anchored attempt and process receipts. Its bounded
descriptor read checks stdout against the recorded size/hash before invoking
the unchanged pure parser. Receipt verification and I/O errors are outside
the parser's exception handler. An oversized parsing input or native-event
contract failure returns an explicit unavailable reason and null report;
an integrity failure raises. The new CLI exits zero for completed inspections,
including unavailable analysis, and exits two without JSON stdout on integrity,
argument or filesystem errors.

Twenty-seven focused tests passed in 7.802 seconds. The five new integration
tests use real local Python processes and task capture, not fabricated capture
receipts. They cover both supported layouts after task removal, failed exits,
timeout and newline-aligned truncation with pending calls, malformed and
mid-line-truncated output, parsing limits, expected-root mismatch, a genuinely
empty observed group set, wrong anchors and tampered stderr. The CLI test
distinguishes unavailable parsing from integrity failure. The log is
`/tmp/caplab-captured-pairs-focused.log`.

Three inspectable probes are retained beneath
`/tmp/caplab-captured-pairs-probe-n84uj31_/`. Both complete native-shaped
streams produce an available paired report while retaining producer exit 7.
The truncated stream retains `byte-limit` termination and unavailable pairing
with a native-event-contract reason. All three task roots were removed after
sealing. Source capture custody and reports remain; independent attempt and
report hashes are in `/tmp/caplab-captured-pairs-probe.json`. The exact probe
script is `/tmp/caplab-captured-pairs-probe.py`.

The original report functions, raw-file CLI and task/process capture/verifier
owners retain identical source bytes, recorded in
`/tmp/caplab-captured-pairs-protected.json`. Existing native session linkage
and scoring behavior are unchanged. These are synthetic integration results,
not native emission, complete capture, coding validation or reviewer capability
measurements. CAPLAB's representative capture and coding work remains open.

## Advisory closure

The Pincite retrieval-state gate passed against release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-a9f1f28edc86155a` incorporates four typed observations for authorization,
source/ownership, tests and retained probes. Selected guidance keeps this
integration in the report owner, reuses the custody verifier, preserves byte
and descriptor boundaries, and separates authority from observed outcomes.
Packet content hash, corpus/doctrine/retriever versions, source locators and
citation classifications are consolidated in
`/tmp/caplab-captured-pairs-verification.json`.

Fifteen remaining generic obligations are retained individually as nonmaterial
with rationales in that receipt. They concern optional recurring-change
history, wider toolchain/static-checker matrices, concurrent mutation,
annotation costs, a historical defect or feature-specific user instruction,
broader future/risk audits and formal procedure exports. No such claims are
made: this implementation is authorized by the recorded delegation and
verified only against the scoped contracts and synthetic integration evidence.

## Final verification and integration

`make check` exited 0: 1,199 tests in 183.398 seconds, 4 skips.
The retained log is `/tmp/caplab-captured-pairs-make-check.log`. All six
selected doctrine citations classified as valid packet citations. Ten named
advisory scratch files were consolidated into the verification receipt and
removed; baseline source, authorization, probe custody and logs remain.

The test guard pass retained real producer/capture/file boundaries and five
distinct integration scenarios. Documentation checks verified API fields,
limits, error handling, CLI behavior and local links against current source.
Local integration consumes the bounded authorization. Representative native
compatibility, independent coding validation, reviewer correctness and the
broader roadmap remain incomplete; no acceptance claim is made.
