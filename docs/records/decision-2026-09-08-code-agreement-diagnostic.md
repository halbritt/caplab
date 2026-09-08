# Per-code agreement diagnostic and failure disposition

Date: 2026-09-08. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `bd4c228`.

## Authorization before execution

The active goal authorizes a read-only local diagnostic in
`src/caplab/code_agreement.py`, a CLI in `scripts/code_agreement.py`, new
synthetic tests in `tests/test_code_agreement.py`, a usage guide under
`docs/product/contracts/`, its product navigation link, and this record.
It may report two-coder agreement for an explicitly supplied expected world,
code and slot population. Test only newly constructed inputs this turn.
Run focused tests, the documented CLI example, and `make check` before commit.

After verification, append progress and the failure disposition below to
CAPLAB-65's description, retaining its open state and original content. Re-read
the item before writing and stop on concurrent change. No comments or messages
are authorized. No roster selection, human-time commitment, model call, archived
transcript read, evidence admission, campaign launch, historic rescoring,
numerical threshold change, reviewer ranking or placement is authorized.
Preserve `docs/designs/`, other worktrees, existing calibration gates and
historical study files. Authorization expires at commit. Remove only this
task's temporary doctrine inputs after receipts are recorded; retain test and
CLI verification logs.

## Decision

For prospective adopters, any required code failing its frozen agreement gate
stops interpretation before unblinding. An undefined required statistic is
not a pass. Do not drop that code after viewing outcomes. A revised codebook
requires an explicit amendment, a new frozen version and a new analysis
boundary; it cannot repair the same study's failed gate retroactively.
CAPLAB-71 still owns numerical thresholds and missingness limits.

Implement a descriptive diagnostic with no pass/fail threshold or execution
authority. It reports binary Cohen agreement statistics separately for every
world/code on complete paired judgments and retains all expected denominators.
Missing and explicitly unavailable judgments remain distinct. Duplicate,
out-of-population or non-Boolean judgments fail validation. No aggregate kappa
may conceal a failing code. Rater calibration's historical continuity gates
are a different contract and remain unchanged.

Leaving agreement to a spreadsheet or ad hoc script would leave population
joins, missingness and undefined statistics implicit. Reusing historical
continuity percentages would conflate agreement with prior judgments and
two-coder reliability. A new scoring or authorization gate would prematurely
select unresolved parameters. The read-only diagnostic is the selected scope.

CAPLAB-65 remains open: no actual coding roster or independently grounded
accuracy anchor has been supplied or validated. Different model labels do not
prove independent errors, and no owner time is presumed available. A successful
diagnostic run does not close those requirements.

## Implementation and verification

The new module validates an explicit schema, two coder IDs, declared worlds
and code sets, expected slot assignments and Boolean/null judgment records.
The judgment key is `(slot, coder_id, code_id)`; a globally unique slot fixes
its world. Extra or duplicate observations fail before aggregation. Every
world/code remains in the report, even when it has no complete pair or no
assigned slot. Missing records and explicit nulls have separate per-coder
counts; incomplete pairs are counted once regardless of which coder is absent.

Cohen's unweighted binary kappa uses each coder's marginal frequencies, as
specified in the [scikit-learn primary documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html).
Joint/marginal counts are integers; the implementation evaluates the rational
formula directly before converting to a float. It emits null for no complete
pairs or chance agreement equal to one. This is a point-estimate diagnostic:
no uncertainty interval, threshold, accuracy estimate or acceptance gate is
implemented. No external statistics package was added.

The pre-implementation test invocation failed to import the not-yet-created
module (`/tmp/caplab-code-agreement-red.log`); this was a feature-development
checkpoint, not a reproduced production defect. After implementation, all
13 focused tests passed in 0.128 seconds
(`/tmp/caplab-code-agreement-focused.log`). They cover:

| Check | Observed result |
|---|---|
| Joint table 00=3, 01=1, 10=0, 11=2 | Observed agreement 5/6, chance agreement 1/2, kappa 2/3 |
| Two opposite balanced coders | Kappa -1 |
| Identical constant judgments | Raw agreement 1, kappa undefined |
| Identical alternating wrong judgments against newly constructed truth | Kappa 1, with no accuracy or pass claim |
| Repeated C1 ID in different worlds | Separate report rows; no pooled statistic |
| Missing record versus explicit null | Distinct counts; both stay in expected denominators |
| Duplicate slot/judgment, unknown references, non-Boolean values | Validation error |
| Reordered records and swapped coder axes | Stable report under record order; transposed table and unchanged kappa under coder swap |
| Real CLI on new local JSON | Original-byte hash reported; input unchanged |
| Duplicate JSON keys and NaN | CLI error, no report, input unchanged |

The exact JSON block from the
[usage guide](../product/contracts/code-agreement-report-v1.md) was extracted
and run through the CLI. The two expected pairs yield one complete and one
incomplete pair, one unavailable coder-B judgment and undefined kappa.
Receipts: `/tmp/caplab-code-agreement-example.json` and
`/tmp/caplab-code-agreement-example-report.json`. The input hash is a byte
receipt, not independent custody or proof that the expected population was
frozen. No archived transcripts or actual coder judgments were used.

`make check` passed: 881 tests in 157.589 seconds, four skips, exit 0
(`/tmp/caplab-code-agreement-make-check.log`). No source or test edits followed
that run. Local guide/record links and `git diff --check` passed. All four
used doctrine citations were classified as valid and consumption recorded.
Passing tests do not supply independent acceptance, coder qualification,
blinding validation, or an accuracy anchor.

The CAPLAB-65 description append was verified against a fresh pre-write read.
The original description, open state, completion timestamp and unrelated
fields remain unchanged. Exact receipts:
`/tmp/caplab-65-before-agreement-update.json`,
`/tmp/caplab-65-agreement-update.ndjson`,
`/tmp/caplab-65-agreement-update-result.json`, and
`/tmp/caplab-65-after-agreement-update.json`. No comments or messages were sent.
The broader goal remains incomplete.

## Planning source

Read-only CAPLAB-65 snapshot: `/tmp/caplab-65-roster-current.json`.
Issue `cb83e7c1-e1ce-4c37-893d-817909593070`, last updated
`2026-07-25T22:02:57.102894Z` at the start of this task. The comments read
returned an empty result (`/tmp/caplab-65-roster-comments.json`). These are
planning context, not admitted study evidence. The original description and
open state are to be preserved in the authorized append.
Snapshot SHA-256: `dfeeaa9c91b3fadc32f165edbb2843348125bdc20b21ac3de0370429ddee9106`.

## Advisory receipt

The release retrieval gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-cad6f8ff2748cb23`, content SHA-256
`cad6f8ff2748cb235859b4e3981194c1c633eb906354a575877fc9015f0060f8`, uses corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts:
`agent-conduct-authority-bounded-action`, `data-ingest-population-scoping`,
`data-dedup-key-identity-completeness`, and
`implementation-config-reference-validation`. They support the explicit
population and identity checks, without turning this diagnostic into a gate.

Two evidence-gathering passes covered the material scope, source, tests,
reference validation and identity obligations. Remaining obligations are
nonmaterial to this bounded implementation for the reasons below.

| Concept | Missing requirements | Scope reason |
|---|---|---|
| domain-authorization-embodied-in-action | attribution recorded at discharge; the decision each gate protects and its authorized principal; the decision the gate protects and its authorized principal; the surface's declared purpose | The CLI emits a descriptive report only and discharges no execution, qualification or acceptance authorization. |
| implementation-async-ui-state-design | an enumeration of lifecycle phases with a designed state for each; content lifecycle phases enumerated; explicit handlers where platform defaults were overridden; geometry reserved independent of the async payload | There is no asynchronous UI or layout in this command. |
| implementation-attention-budget-presentation | a prioritization key tied to the consumer's decision; proof canonical data is unchanged by presentation; the bound stated and enforced; the consumer and budget named; the consumer and their budget named | The output retains every world/code without ranking or truncation; no bounded presentation or review-cost improvement is claimed. |
| implementation-rank-before-truncate | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No ranked retrieval or top-N selection is performed. |
| operations-gate-authoritative-signal | eval-versus-serving configuration parity; inventory of gates and the signals they observe; proof the check reads that signal rather than a derived view; the authoritative signal named for each gate | Native evidence and experiment comparability are explicitly unverified; this function neither admits evidence nor gates a live operation. |
| universal-no-change-option | actual current cost/risk or absence within a stated interval; intervention cost and uncertainty; latent security, safety, data, durability, and compatibility check; proc-decide-leave-code-alone | The explicit unresolved per-code measurement requirement justifies the diagnostic; no system-wide cost, security or latent-risk audit is claimed. |
| universal-repository-contract-precedence | accepted ADR, RFC, API, compatibility, generation, build, and test contracts | Relevant local instructions, authority, code-authoring contract and test command were checked; unrelated API and generation contracts are outside this new report. |
