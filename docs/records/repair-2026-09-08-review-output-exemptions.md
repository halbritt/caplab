# Restrict review snapshot exemptions to root paths

Date: 2026-09-08. Baseline: `3fbeea9`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Investigate and repair basename-wide exclusions in the canned and native
review task snapshots. Permitted files: `src/caplab/review_dissent/instrument.py`,
`src/caplab/review_dissent/native.py`, `tests/test_review_task_preservation.py`,
`docs/product/contracts/review-task-preservation-v1.md`, and this record.
Use newly rendered synthetic development fixtures to reproduce hidden nested
additions and handling of legitimate task files with the reserved basenames.
Verify public capture/grading behavior, existing valid output parity and
symlink rejection; run the relevant suites and `make check`.

This authorization permits local source/test/docs edits and synthetic files
under temporary directories. It permits no historical capture inspection,
copying, admission, rescoring, rewriting or purge; no model call, campaign,
ranking, placement, tracker write, or external message. Preserve `docs/designs/`,
frozen instruments and manifests, other worktrees and services. Retain test and
probe receipts under `/tmp`; remove only named task doctrine scratch after its
receipt is retained. Stop on unexplained compatibility changes or a repair that
requires changing frozen instrument criteria. Authorization expires at commit.

## Observation and proposed decision

Both current snapshot functions exclude files by `path.name`, although the
review output and generated metadata are at specific task-root paths. This
also excludes nested files that have those basenames. The preference snapshot
already compares the task-relative path for its metadata exception.

Subject instructions permit the root `REVIEW.json` output and prohibit editing
other task files. Select task-relative path matching for the existing exception
sets if the synthetic reproduction confirms the mismatch. Preserve root
exceptions, existing schemas and byte-hash semantics. No change leaves the
observed gap; banning the basenames throughout task trees would reject legitimate
task filenames without establishing their preservation.

This is a semantic repair of the path exemption, not a complete implementation
of CAPLAB-79's before/after inventory. File modes, intermediate writes, special
files, atomic filesystem snapshots, native capture integration and campaign
eligibility remain separate requirements. CAPLAB-84 remains open.


## Execution and verification

The reproduction confirmed the proposed mismatch, and the selected repair was
applied to both snapshot functions. Each now compares the task-relative path
with its existing exception set. The two functions retain their own exception
sets and error types; this repair needs no shared policy abstraction or API
change. The [snapshot contract](../product/contracts/review-task-preservation-v1.md)
states the resulting behavior and the remaining inventory limits.

Before the repair, five new tests produced 16 failing subcases in 1.578 seconds:
`/tmp/caplab-review-exemptions-red.log`. Nested additions were omitted by both
paths. Native capture also reported legitimate, unchanged nested input files
as unpreserved, because the expected snapshot included them while the observed
snapshot excluded them. Canned capture missed edits to such existing files.
The canned path already included `.caplab-native-review-task.json`; its
corresponding cases passed before the repair and remain protected.

A separate public-entrypoint probe against `3fbeea9` confirms the consequence:
adding `src/REVIEW.json` yields `preserved: true` and mechanical score `1.0`
in both old captures. Current captures yield `preserved: false` and score `0.0`
for the same constructed task state. Receipts:
`/tmp/caplab-review-exemptions-counterexample.py` and
`/tmp/caplab-review-exemptions-counterexample.json`. These are synthetic
instrument tests, not observations about any actual reviewer.

The focused review suites passed 106 tests in 10.430 seconds:
`/tmp/caplab-review-exemptions-focused.log`. New tests cover nested additions
at two depths, unchanged legitimate input names, edits and deletions, binary
and non-ASCII content, and root/nested symlink rejection. Synthetic variants
extend an in-memory development fixture; they are not resealed study designs.

The parity probe compares entire old/current captures for all eight development
cells, with/without an ordinary added file and with completed, refused or
capture-failure status, through both canned and native entrypoints. All 96
captures match with no field exclusions. Receipts:
`/tmp/caplab-review-exemptions-parity.py` and
`/tmp/caplab-review-exemptions-parity.json`.

AST/direct-import checks and the source hashes taken before the full suite are
in `/tmp/caplab-review-exemptions-source-check.json`. The scan found an existing
unused `tempfile` import in `native.py`, also present at `3fbeea9`; this repair
adds no unused import and leaves that unrelated cleanup outside its scope.

## Interpretation and remaining requirements

This closes a demonstrated path-based grading error. It does not estimate its
historical frequency or establish that any model exploited it. Frozen capture
records and their scores were neither read nor changed. No new native attempt
was prepared or launched; no source-digest gate was relaxed or manifest resealed.

CAPLAB-84 still requires the complete prospective capture design, including
mode-aware task inventories, session linkage and measurements on representative
repair episodes. The root metadata exclusions remain a limit of these content
snapshots. Reopen the exemption contract if authorized output paths change;
do not infer output authority from a filename appearing elsewhere in a task.


## Doctrine receipt

The release retrieval-state gate passed at release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`.

Final packet `pkt-c9bd28261b15d198`, content SHA-256
`c9bd28261b15d19835fd82cb1b060a12d47e08eb5d9e7f6a61fe4c7a2504a710`,
was reassembled after one evidence-gathering pass with five typed records:
authority, contracts, source, tests and synthetic observations. The
implementation route supplied advisory guidance; the repository record
classifies the actual change as a semantic repair.

Applied `universal-evidence-before-intervention` to require a public grading
counterexample; `universal-repository-contract-precedence` to distinguish the
permitted root output from unauthorized nested changes;
`universal-preserve-behavior-by-default` to compare all fields of ordinary
captures; and `agent-conduct-authority-bounded-action` to preserve historical
captures and keep synthetic results separate from real reviewer claims.
Four citations classified as `valid-packet-citation`.

All 14 remaining obligations are nonmaterial to this path-exemption repair:

| Concept | Exact unmet requirements | Classification and reason |
|---|---|---|
| `implementation-placement-by-ownership` | recurring change evidence when available | Nonmaterial: both existing snapshot owners exhibit the same reproduced defect; no recurring-churn or architecture-cost claim. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI/static-tool conformance claim or tooling change. Verification uses the existing Makefile and local Python 3.12.3. |
| `python-mutable-ownership` | concurrency; lifetime and size | Nonmaterial: no concurrency, cache, input mutation or scaling change; relative-path selection changes which bytes enter an existing local result. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no formatter, linter or checker policy is changed or claimed as verified. |
| `python-runtime-static-boundary` | annotation maintenance cost; checker and trust-boundary evidence; configured checker and Python version | Nonmaterial: no annotation/checker change or static-correctness claim; executable task transitions establish the repair. |
| `python-structured-cleanup` | acquisition and release paths; exception and cancellation behavior; nesting order; owner and lifetime; resource ownership and failure policy | Nonmaterial: the same standard-library traversal and byte reads are retained, with no manual descriptor or new resource lifecycle. This does not verify atomic snapshots or broader filesystem failure handling. |


## Completion checks

`make check` passed 957 tests with four skips in 160.298 seconds:
`/tmp/caplab-review-exemptions-make-check.log`. No source or test file changed
after that check began. Final file/link checks, source hashes, citation receipt
and the exact scratch cleanup list are retained in
`/tmp/caplab-review-exemptions-verification.json`.

The eleven named doctrine scratch files were removed after retaining their
receipt. Regression logs and synthetic probes remain. No tracker field or
external message changed. Commit closes this repair; the CAPLAB improvement
goal and CAPLAB-84 remain open.
