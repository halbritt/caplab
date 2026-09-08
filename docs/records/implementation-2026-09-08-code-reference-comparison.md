# Compare coder judgments with supplied reference labels

Date: 2026-09-08. Baseline: `e48284a`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Extend the existing read-only coder diagnostic with an explicit reference-file
comparison. Permitted files: `src/caplab/code_agreement.py`,
`scripts/code_agreement.py`, `tests/test_code_reference.py`,
`docs/product/contracts/code-agreement-report-v1.md`,
`docs/product/contracts/code-reference-report-v1.md`, and this record.
Factor the existing validated judgment representation only as needed to share
it between the two report builders. Preserve agreement-only version 1 output.

Use only new synthetic judgment/reference inputs. Verify reference/missingness
counts, strict validation, wrong-but-agreeing coders, CLI input preservation,
and old/new agreement parity; run `make check`. No historical labels, captures,
evidence admission, human-time commitment, model calls, scoring of real coders,
threshold adoption, ranking, placement, campaign launch, tracker write or
external message is authorized. Preserve `docs/designs/` and unrelated state.
Retain test/parity receipts under `/tmp`; remove only named doctrine scratch
after retaining its receipt. Authorization expires at commit.

## Decision and authority boundary

CAPLAB-65 requires accuracy evidence in addition to coder agreement. Its current
planning snapshot is `/tmp/caplab-roadmap-instrument-frontier.json`. Staffing
the human anchor remains a Principal-owned choice; an availability question
was sent to the user in this conversation. No answer or human-time allocation
is assumed. Independent diagnostic construction can proceed without that choice.

Select a separately identified reference input with per-label evidence locators,
complete expected-population validation, and descriptive per-world/code/coder
confusion counts. Keep missing labels, unresolved references and unavailable
coder judgments visible. Report complete-case agreement with references and
positive/negative reference-class denominators separately; no global average,
threshold, automatic coder acceptance or claim that the supplied labels are true.

No change leaves the analyst without a reproducible reference comparison.
Treating one of the two coders as truth or deriving references from their
consensus would not establish independence. Replacing the existing agreement
report would hide a different diagnostic; retain it inside the new report and
preserve the original CLI mode when no reference is supplied.


## Execution and verification

Added `build_code_reference_report` and `--reference` on the existing CLI.
Shared parsing validates the original expected-population contract once per
report. Agreement-only output keeps its version 1 schema; the new
`caplab-code-reference-report/1` embeds that agreement data and adds per-coder
reference comparisons. Reference rows require an evidence locator, but this
operation does not read or authenticate that locator. The CLI hashes both
supplied byte strings and changes neither file.

The output distinguishes missing references, explicit unresolved references,
missing coder judgments and explicit unavailable coder judgments. Class counts
remain visible when a class-specific comparison has no observations. Rates
with zero denominators are null. Reference counts use the first matrix axis
and coder labels the second; the guide cites the primary scikit-learn matrix
and kappa definitions opened on September 8. CAPLAB implements this arithmetic
directly and adds no statistical-library dependency.

Eleven new tests include the concrete failure-of-inference witness: two coders
have kappa 1 while each disagrees with all four supplied references. Other cases
verify an asymmetric hand-counted matrix (3/2/1/4), missingness and class
coverage, absent classes, empty worlds, cross-world code identity, input/order
preservation, exact reference contracts, original coder validation and both CLI
branches. The focused agreement/reference suite passed 24 tests in 0.285 seconds:
`/tmp/caplab-code-reference-focused.log`.

An initial development run failed because the extracted agreement formatter
still referenced `slots` after its tuple binding was discarded. Restoring that
binding fixed the regression before verification. This was an implementation
error during the new feature, not an existing CAPLAB agreement defect.

The retained parity probe executes the old module from `e48284a` and the current
module over 1,640 new inputs: all Boolean/null coder pairs for zero through
three slots, with/without a missing first judgment, plus unassigned world/code
rows. Entire agreement reports compare equal without field exclusions, and
input objects remain unchanged. Receipts:
`/tmp/caplab-code-reference-parity.py` and
`/tmp/caplab-code-reference-parity.json`.

The JSON examples in the two guides were run together through the real CLI.
Both coders have zero agreement with those constructed reference labels; their
reference coverage is 1 and 0.5 respectively. Inputs and report are retained as
`/tmp/caplab-code-reference-example-input.json`,
`/tmp/caplab-code-reference-example-reference.json`, and
`/tmp/caplab-code-reference-example-report.json`. These are synthetic values,
not an accuracy-anchor result. AST/direct-import checks and source hashes are
in `/tmp/caplab-code-reference-source-check.json`.

## Limits and next boundary

The [reference comparison contract](../product/contracts/code-reference-report-v1.md)
requires the caller to declare the anchor population before inspecting labels.
A sparse reference set over a whole-study input leaves missing references
visible; the diagnostic does not infer or select the intended anchor subset.
Agreement conditional on supplied references is not proof of their truth,
independence, human authorship, blinding or representativeness. Small samples
remain uncertain, and no uncertainty interval or numerical gate is adopted.

CAPLAB-65 still needs its roster and qualified anchor; the availability question
has not allocated human time. CAPLAB-71 retains numerical parameter ownership.
No reference source, actual coder, reviewer capability or study outcome was
accepted or qualified. Existing frozen studies and historical evidence remain
unchanged. Reopen this diagnostic contract if the adopted anchor design requires
a different analysis unit or denominator; preserve the old reports rather than
silently changing their interpretation.


## Doctrine receipt

The release retrieval-state gate passed. Release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`.

Final packet `pkt-9d1d301073e9a4e1`, SHA-256
`9d1d301073e9a4e10dd127e15bab1e03e0cac55f26f8684cd280acf82bab4dc4`.
One evidence-gathering pass supplied five typed records: authority, repository
contracts, source structure, tests and synthetic observations. Retrieval matched
no precisely nominated concept; the packet supplies baseline, routed,
prerequisite and kernel guidance.

Applied `universal-evidence-before-intervention` to the shared-wrong-label
witness; `universal-repository-contract-precedence` to keep the report distinct
from qualification; `universal-preserve-behavior-by-default` to require complete
agreement-output parity; and `agent-conduct-authority-bounded-action` to keep
synthetic diagnostic verification separate from staffing or accepting an anchor.

All 15 remaining obligations are nonmaterial to this bounded feature:

| Group | Exact unmet requirements | Classification and reason |
|---|---|---|
| `implementation-placement-by-ownership` | recurring change evidence when available | Nonmaterial: the existing diagnostic owns the same validated labels; no recurring-churn or architecture-cost claim is made. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI or static-tool conformance claim. Verification uses the existing Makefile and executable tests. |
| `python-mutable-ownership` | concurrency; lifetime and size | Nonmaterial: synchronous, local report construction introduces no worker or retained cache; input preservation is tested. No scaling claim is made. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no formatter, linter or type-checker policy changes or conformance claims. |
| `python-runtime-static-boundary` | annotation maintenance cost; checker and trust-boundary evidence; configured checker and Python version | Nonmaterial: no checker policy or static correctness claim; executable validation rejects invalid external labels. |
| `python-structured-cleanup` | acquisition and release paths; exception and cancellation behavior; nesting order; owner and lifetime; resource ownership and failure policy | Nonmaterial: the CLI uses the existing standard-library whole-file read pattern, with no retained descriptor, process or manual resource lifecycle. No cancellation guarantee is added. |
| `python-text-bytes-boundary` | representative non-ASCII data | Nonmaterial: the existing explicit strict UTF-8 decoder and JSON encoder are reused without codec or normalization changes; this feature adds label comparison, not a Unicode interoperability claim. |

## Completion checks

`make check` passed 952 tests with four skips in 131.270 seconds:
`/tmp/caplab-code-reference-make-check.log`. No source or test file changed
after that check began. Final source-hash, file/link and parity checks are
retained in `/tmp/caplab-code-reference-verification.json`.

Four doctrine citations classified as `valid-packet-citation`. The packet
identity, applied concepts and obligation table above retain the receipt.
The eleven named task doctrine scratch files were removed after recording it;
focused/full test logs, parity probes and synthetic examples remain. No tracker
field or external message was changed. Commit closes this implementation,
not CAPLAB-65 or the broader measurement goal.
