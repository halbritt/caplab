# Preserve outcome kind and schema in the transfer oracle

Date: 2026-09-08. Baseline: `8cf9f25`. Primary-agent decision and bounded
execution authority: [CAPLAB ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Reproduce returned-exception and schema-mutation counterexamples using the new
development world's existing candidate repair and disposable SQLite databases.
Retain before/after reports under `/tmp/caplab-transfer-observations-*`. Repair
`development-worlds/atomic-transfer-v1/oracle.py` within
`docs/product/studies/advisory-selection-001/`, update its README and
`tests/test_atomic_transfer_world.py`, add focused regression tests, this record
and a new `development-v2.json` dossier. Version the audit result to v2 because
its observation semantics change. Keep `TASK.md`, all five witness source files,
the original `development.json`, construction record and prior probe/logs
unchanged. The original dossier describes the tree at `8cf9f25`; preserve that
commit/path/hash provenance and do not present it as describing revised bytes.

Distinguish returned values from raised exceptions. Compare the task's schema
alongside row state and transaction ownership. Keep unsupported fault surfaces
unavailable. Use only existing trusted authored witnesses and new wrappers, never
native/model calls or external databases. Run focused/full checks, consolidate
advisory evidence, delete exact named scratch, and make a local commit. Retain
probe and logs. No study admission, frozen criterion change, historical result
rewrite, ranking, placement, tracker write, external message, push, service or
credential operation. Preserve runtime/capture owners, existing unrelated worlds,
`docs/designs/` and sibling worktrees. Authorization expires at commit.

Stop if a fix requires weakening the task, relabeling old results, claiming
independent validation, or executing untrusted candidate code outside a separate
authorized containment boundary. Primary-agent checks remain self-verification.

## Reproductions and selected repair

A wrapper around the existing transaction repair returned every caught exception
as an ordinary value. All nine original oracle checks passed. A second wrapper
added an unrequested table inside the repair's transaction; it also passed all
nine checks. Both violate unchanged `TASK.md`. These are oracle false acceptances,
not observations of a native reviewer or production incident.

The earlier exploratory schema wrapper added its table after commit. The old
oracle detected that wrapper's interrupted fresh path because transfer state
remained committed when the later statement failed. Its other checks missed the
schema change. That exploratory result is retained separately; it does not
replace the stronger transaction-contained counterexample.

V2 records each candidate outcome as `Observation(kind, value)`, distinguishing
`returned` from `raised`. Success requires a returned string; expected errors
require a raised instance of the specified exception class. A returned exception
or equality-imitation object cannot supply either fact. Exception object identity
is not required. Actual unsupported fault operations remain unavailable.

Main and temporary schema definitions are compared with their initial snapshots.
The snapshot includes object type, name, table name and SQL, excluding physical
root-page placement. Persistent schema changes fail the task contract. If schema
differs, the dependent row check is null rather than attempting to query tables
that may have been removed. This is final-observation coverage; reversed
intermediate DDL, attached databases, settings and filesystem effects are not
fully assessed. It adds no sandbox guarantee.

No change would leave known task violations undetected. Changing expected task
behavior to admit them would invalidate the exercise. The selected repair
preserves the task, witness implementations and missing-observation policy while
versioning the audit's changed semantics.

## Verification

The returned-exception wrapper now fails invalid/conflicting/funds outcomes and
both statement-failure checks. Its valid fresh/retry paths remain successful.
The transactional-schema wrapper fails the fresh state/schema check and both
fault baselines. Its invalid-input-only path remains unchanged because it never
opens the transaction or creates the table. No failed result is relabeled as a
different subject or erased.

The focused suite adds returned-error, main/temp table, index, trigger,
removed-table, unsupported-marker and non-string equality counterexamples.
Both existing repair strategies still pass the same nine audit checks, and the
parent and two original negatives retain their discrimination. The concurrency
test now consumes the outcome kind instead of discarding it.

The first focused run caught an ordering regression: checking baseline state
before checking for observed statements changed the no-statement fault result
from unavailable to failed. The implementation order was corrected to preserve
that existing requirement; its test was not weakened. The initial failed log is
retained as `/tmp/caplab-transfer-observations-focused-initial.log`.

The task, original dossier, five witness files and construction record remain
byte-identical to `8cf9f25`. The three original oracle definitions `database`,
`snapshot` and `expected_step` also retain their ASTs. The
original dossier's content hashes were verified against that Git commit, rather
than incorrectly comparing them with revised current files. The new v2 dossier
links the full source commit, original path/hash, current content and prior
exposure. Both dossiers remain development-only and unsealed.

Retained artifacts under `/tmp/caplab-transfer-observations-` include `before.json`
(returned errors and exploratory post-commit schema),
`before-transactional-schema.json`, `after.json`, `source-check.json`, focused/full
logs and `verification.json`. Previous construction evidence remains unchanged.
No independent acceptance, study admission or reviewer capability claim is made.

After the first full pass, review identified that a candidate could catch the
probe's unsupported-operation exception. The probe now records that operation
separately, preserving unavailable fault coverage even when the candidate returns
the caught exception. A regression case covers this path; a returned marker
without an actual unsupported operation remains an invalid return. The first
full pass (1,160 tests, four skips, 148.655 seconds) is retained separately.

Final focused checks passed **15 tests in 0.408 seconds**. Final `make check`
completed with exit 0: **1,161 tests, four skipped, 147.394 seconds**. The final
probe records the current oracle hash and the new unavailable-coverage case;
the earlier after-report remains at `after-first-pass.json` under the same prefix.

## Advisory disposition and closure

The retrieval-state gate passed against
`/home/halbritt/.local/share/pincite/release`, release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`. Five typed records supplied authority,
contracts, source, tests and synthetic observations. Final packet:
`pkt-cbcd7cf2c42f6c38`, content SHA-256
`cbcd7cf2c42f6c387a358a0144516529c2bf3e11e452f27091d883f23edea664`.

Applied `universal-repository-contract-precedence` to the unchanged task and
version boundary, `universal-explicit-invariants` to schema/state observations,
`implementation-explicit-failure-policy` to raised versus returned outcomes and
unavailable instrumentation, and `implementation-risk-driven-tests` to the
reproductions and preservation cases. All four citations classified as valid.

Four missing obligations remain nonmaterial: `CI and build matrix` and `Python
and dependency version matrix` are not expanded by this local oracle repair;
`formatter and static-tool configuration` and `formatter linter and type-checker
configuration` are unchanged. Existing local checks passed; no broader platform
or static-tool guarantee is asserted.

The consolidated verification manifest preserves artifact hashes, both full runs,
the initial regression, final checks, old/new source provenance and advisory
identities. Eleven exact doctrine scratch files are removed; probes and logs
remain. No roadmap item is closed by this repair and the development world's
independent-validation and study-exclusion limits remain. Authorization expires
at the local commit containing this record.
