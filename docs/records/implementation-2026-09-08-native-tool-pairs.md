# Report observed native tool request/result linkage

Date: 2026-09-08. Baseline: `4a5e94d`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Implement `src/caplab/native_tool_pairs.py`, `scripts/native_tool_pairs.py`,
`tests/test_native_tool_pairs.py`, the contract
`docs/product/contracts/native-tool-pairs-v1.md`, and this record. Parse bounded,
independently hash-identified UTF-8 JSONL bytes from Codex exec stdout or Claude
stream-json stdout. Report observed item/request/result associations by native
ID and scope, source locators, missing counterparts, duplicates, ordering
conflicts, partial requests and unclassified observations. Preserve formats'
different units; do not present their counts as comparable action counts.

Validate with newly authored synthetic streams and CLI probes only. Run focused
tests and `make check`, including its existing prescribed read-only store checks.
Retain authorization, probes, source/reference locators and logs under
`/tmp/caplab-tool-pairs-*`. Consolidate advisory provenance and remove only
named advisory scratch. Commit the five files locally; authorization expires
at commit. Stop on insufficient format evidence or a need for wider effects.

No historical transcript read/copy/admission, native/model call, new benchmark
or study execution, scoring, coder exposure, roster/threshold selection,
tracker write, external message, push or service change. Preserve all existing
capture, session linkage, identity and scoring owners, historical evidence,
unrelated `docs/designs/`, worktrees and timers. This report cannot establish
native execution linkage, capture completeness, successful verification,
correctness, blinding, eligibility or acceptance.

## Decision and source basis

CAPLAB-79 requires native-ID tool pairing and explicit missingness. Existing
root linkers establish narrower session-field relationships. Add a report
owner for this distinct observation rather than changing their meaning or
inferring completed work from final prose. Leaving the gap to ad hoc reading
makes pending and repeated events easy to confuse. A common execution proxy
would change the subject and is not selected.

The inspected official Codex documentation describes JSONL item lifecycle
events separately from turn completion and final messages. This report uses
that exposed item lifecycle, not an undocumented rollout function-call schema.
[OpenAI non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

Claude's documented tool blocks carry a request ID and a result's
`tool_use_id`. Streaming deltas precede complete assistant messages; child
messages have a separate parent-tool scope. Partial input completion is not
tool execution completion. The report uses completed message blocks for the
request/result pair and retains partial starts separately.
[Claude content blocks](https://code.claude.com/docs/en/agent-sdk/python#content-block-types),
[Claude streaming output](https://code.claude.com/docs/en/agent-sdk/streaming-output).

These sources establish a parser contract, not observed compatibility with
every installed native version. The new report remains a development reporting
surface until representative, separately authorized captures validate it.

## Implementation and observed checks

The API validates exact source bytes and initialization before grouping.
Every source line remains in an index with byte offset, length and hash.
Group references locate complete requests, results, partial starts and item
updates without copying command or result bodies. Claude groups include both
session and parent-tool scope; Codex groups describe one expected thread.
Repeated requests/results, conflicting kind/name and reversed result order
remain ambiguous. Unknown native observations remain locatable. Reported
outcome fields stay separate from work correctness and capture completeness.

Eight new tests passed in 0.132 seconds on the first implementation check.
The final focused run passed 60 tests in 4.861 seconds, including existing
Codex parsing and both root-linkage suites. Logs are
`/tmp/caplab-tool-pairs-focused-initial.log` and
`/tmp/caplab-tool-pairs-focused-final.log`. The fixtures cover partial and
pending calls, interleaving, duplicate/reordered records, scope collisions,
unknown events, non-ASCII byte locations, malformed input, independent hashes
and a real bounded CLI invocation. No native event producer is mocked into
a claimed harness measurement; all new stream contents are synthetic.

Two retained CLI probes are in `/tmp/caplab-tool-pairs-probe-l6xprsjw/`.
The Codex-shaped fixture reports one paired failed-exit item and one pending
request despite optimistic final prose. The Claude-shaped fixture leaves
a root request and same-ID child result unmatched. Both CLI processes exited
0 with empty stderr and unchanged source bytes. Exact commands, source and
report hashes, and expected group counts are in
`/tmp/caplab-tool-pairs-probe.json`. The raw fixtures and reports have mode
0600 beneath a private temporary directory.

Six existing parser, linkage, collection-verification, task-verification and
invocation owners are byte-identical to baseline, as recorded in
`/tmp/caplab-tool-pairs-protected.json`. No old capture or score interpretation
was changed. This is useful preparation for CAPLAB-63/77/79/84, but it does not
complete their native compatibility, representative legibility, coding,
blinding or resource-measurement requirements.

## Advisory closure

Pincite's retrieval-state gate passed against release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. An initial unsupported task label
`feature` was rejected before packet creation; the advertised `implementation`
route was then used. Final packet `pkt-d4a50e8e51faecbb` incorporates four
typed observations for authorization/contracts, source ownership, tests and
retained CLI probes. Selected guidance concerns repository precedence,
bounded authority, explicit byte decoding, structured file cleanup, local
ownership and runtime validation. Its full identity, source locators,
evidence and citation results are consolidated in
`/tmp/caplab-tool-pairs-verification.json`.

Twenty remaining generic obligations are retained individually with
nonmaterial classifications and rationales in that receipt. They concern
distributed synchrony/performance, wider toolchain matrices, concurrent
mutation, static-checker and annotation claims, representative native file
metadata, a feature-specific user instruction, broader future/risk audits
and formal procedure exports. This bounded implementation is selected under
the recorded delegation; it claims local synthetic behavior only. Real native
compatibility and completeness remain unverified, rather than being inferred
from those missing observations.

## Final verification and integration

`make check` exited 0: 1,194 tests in 194.892 seconds, four skips. The log is
`/tmp/caplab-tool-pairs-make-check.log`. All seven selected doctrine citations
classified as valid packet citations. Ten named advisory scratch files were
consolidated into the verification receipt and removed; authorization, probe
custody and logs remain. Test-guard review retained behavioral scenarios and
real CLI/filesystem boundaries. Documentation checks verified field names,
source pointers, commands and local links against the implemented contract.

The five new files are locally integrated. This consumes the bounded execution
authorization without claiming independent acceptance, native capture
completeness, reviewer correctness, harness selection or roadmap completion.
