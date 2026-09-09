# Preserve expected slots in capture accounting

Date: 2026-09-08. Baseline: `e245b3a`. Primary-agent authority:
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before implementation

Extend `src/caplab/capture_accounting.py` with a population reporting entry
point. Add `scripts/capture_population.py`, `tests/test_capture_population.py`
and `docs/product/contracts/capture-population-report-v1.md`. Link that contract
from `docs/product/contracts/capture-byte-report-v1.md` and update this record.
These six files are the only edit targets. Run focused checks and `make check`;
retain synthetic inputs, inspection reports, logs, scripts and advisory receipts
under `/tmp/caplab-capture-population-*`. Commit locally after verification.

The population input names expected cells and slots, with independently retained
task/native receipt anchors or explicit nulls. Preserve empty cells and every
expected slot. Bound input bytes and slot count, reject duplicate cell/slot IDs
and reused custody paths or receipt anchors, and require unique-key finite JSON.
Verify every supplied bundle, including a supplied counterpart whose other
anchor is unavailable. Require the collection's configured tuple to match the
cell's declared tuple. Corruption or inaccessible supplied evidence fails the
report; it cannot be silently converted into missingness.

Report available complete bundle pairs and unavailable pairs separately, retain
partial component inspections, and keep total pair bytes null if any expected
pair is unavailable. Available-pair totals are explicitly conditional on that
subset. Keep failed processes, incomplete streams and missing native locations
visible without treating them as eligible or as reviewer errors. Do not infer
launch count or failure cause from absent anchors. An independent input hash
pins this supplied population record; it does not authenticate a preregistration
or prove that no assignments were omitted.

Use only new synthetic captures made by the existing local Python fixture,
including failed and byte-limited producers; no native harness or model calls.
Do not inspect or process historical captures, labels, worlds or scores. No
resource units, service changes, native execution, budget/parameter freeze,
campaign admission, scoring, ranking, placement, tracker writes, external
messages or push. Preserve existing single-bundle behavior and verifiers,
`docs/designs/`, sibling worktrees and all historical custody. No independent
acceptance or study eligibility is delegated by this accounting addition.

Stop on a required change to existing capture evidence semantics or a wider
scope. Consolidate advisory evidence before deleting only named scratch;
retain synthetic probe evidence and completed-record provenance. Authorization
expires at commit. This implements an existing accounting requirement, not a
claim that representative costs or the broader CAPLAB goal are established.

## Implementation and verification observations

The existing byte reporter requires both final receipts. Its contract already
forbids treating failed captures without those receipts as zero-cost attempts,
but callers previously had to preserve the expected population themselves.
The added entry point keeps that population in the same accounting owner and
reuses existing bundle verification. It introduces no separate storage service,
assignment system or resource gate. Leaving the API unchanged or averaging
available reports would leave the denominator obligation outside the report.

The input is immutable bounded JSON bytes with an independent expected hash.
Its exact shape, cell/slot identities and anchor uniqueness are validated
before reads. Parsed input is owned, so later changes to a caller's source
mapping cannot alter the returned result. A supplied but inaccessible or
corrupt bundle fails inspection even when its counterpart is absent. Only an
explicit null denotes an anchor not supplied. A verified native collection
must match its cell's configured tuple; that is configured identity, not an
observed served model or complete Binding.

Seven focused tests passed in 2.068 seconds. They exercise missing and partial
pairs, empty cells, failed processes, byte-limited captures, missing native
surfaces, corruption with a missing counterpart, configuration mismatch,
reused paths/anchors, duplicate cells/slots, strict input and resource limits,
CLI/API agreement and no JSON output on an invalid anchor. Real synthetic
Python processes and filesystem receipts are used. There are no mocked
verifiers, native calls or historical observations. Existing single-bundle
tests and their fixture were reused without modification.

The separately retained probe has five declared slots across three cells:
one full failed-process capture, task-only and native-only partial pairs, one
slot with neither anchor, one full byte-limited capture, and an empty cell.
It reports two available pairs and three unavailable pairs. Available pairs
retain 42 logical payload bytes and 25,808 receipt bytes; both all-slot totals
are null. The empty cell remains with zero declared slots. Partial component
counts stay in their inspections and do not enter pair totals. These small
synthetic values are not representative costs or an episode-cost average.

Private custody is `/tmp/caplab-capture-population-probe-hv3naq8j/`. Input SHA-256:
`1ba9000d5d9b73b4f30c38b140bc13e8dc4e3d2456ac8adc2da8024da8227ae6`.
Report SHA-256:
`0bdc9972eb74ce403f67b74bab1f27c8a563585209f1b87aef0a65dbaf703501`.
The CLI exited zero and its parsed output equaled the API report. Input and
bundle hashes stayed unchanged. The probe script and receipt are
`/tmp/caplab-capture-population-probe.py` and
`/tmp/caplab-capture-population-probe.json`.

## Claim and authority limits

The population is caller-declared and its hash alone does not prove that it
matches an authorized frozen assignment. No-anchor entries cannot establish
whether launches occurred, which resource limit was reached, or why receipts
are absent. The resource probe's kernel observations are not linked by this
report; that still requires native runner integration and its separate policy.
No failed or truncated process is removed from its available-pair observation,
and pair availability is never labeled usable measurement or study eligibility.

Even all-slot retained-byte totals would not establish runtime peaks, allocated
disk use, capture overhead, blinding feasibility, representative costs, statistical
precision or reviewer capability. CAPLAB-84 still requires native integration
and representative measurement; CAPLAB-71 still owns parameters and budgets.
No existing study is frozen, amended, admitted or accepted here. All twelve
open roadmap items remain open, and no tracker write occurred.

## Advisory disposition

The Pincite retrieval-state gate passed for release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`. Final packet:
`pkt-af0c75bce79753ce`; content SHA-256:
`af0c75bce79753ce68ec57bb71d083b9548b33ddb2b32ff1f8dff3fd298d012a`.
The execute ceiling is advisory; ADR 0026 and the exact authorization above
supply authority. Applied repository-contract precedence, evidence before
intervention, placement by ownership, mutable ownership and authority-bounded
action. The report keeps accounting in its existing owner and validates runtime
values rather than relying on type annotations or a caller's success label.

Seventeen unmet generic obligations remain nonmaterial: recurring change
history, broader CI/version/tooling matrices, static-checker and annotation
cost evidence, a production-defect classification, representative architecture
change, quantified intervention cost/future-change estimates, a comprehensive
latent-risk audit, formal leave-code-alone/preservation exports and an exhaustive
repository-contract audit. This is a bounded implementation of a stated
accounting requirement; it claims neither a measured architecture improvement
nor production incidence or representative native measurement. Each obligation
and its specific rationale remain in
`/tmp/caplab-capture-population-verification.json`.

The documented JSON example was executed directly: one expected unavailable
slot stays visible, available-pair bytes sum to zero over an empty subset,
and both all-slot totals are null. Receipt:
`/tmp/caplab-capture-population-doc-example.json`. Symbols, arguments, paths,
error behavior and local links were checked against current source. The
standalone Python signature example uses caller-supplied paths, anchors and
allowances; its values are not frozen campaign parameters.

## Closure

`make check` exited 0: 1,212 tests, four skips, 153.316 seconds. The seven new
population tests and the existing single-bundle accounting tests passed in that
run. Full log: `/tmp/caplab-capture-population-make-check.log`. Test review kept
real filesystem/process boundaries and explicit missingness assertions, with no
mock fallback or existing-test weakening. No source changes followed that run.

`/tmp/caplab-capture-population-verification.json` consolidates both advisory
packets, five typed evidence records and the five valid citation classifications.
It retains individual unmet-obligation rationales, source and synthetic-custody
hashes, the exact input/report anchors, focused/full logs, documented example,
authorization and completed record. Eleven named advisory scratch files are
removed only after consolidation; synthetic custody and scripts remain.

Only the six authorized files enter the local commit. Historical custody,
existing verifiers, the resource probe, unrelated designs and sibling worktrees
remain unchanged. No tracker write, model call, service change, push, independent
acceptance or roadmap completion is claimed. The authorization expires at this
commit; the full CAPLAB goal remains active.
