# Construct a development repair world with an executable truth oracle

Date: 2026-09-08. Baseline: `f160b86`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before construction

Create a new development-only world at
`docs/product/studies/advisory-selection-001/development-worlds/atomic-transfer-v1/`
and its tests at `tests/test_atomic_transfer_world.py`. Author the task and
acceptance contract before its implementations and oracle. Construct a broken
parent, two candidate repairs and explicit misleading partial repairs. Verify
state, return/error and retry observations against the acceptance contract using
new disposable SQLite databases and deterministic statement-failure injection.
Run focused/full checks and retain a new probe and source hashes under
`/tmp/caplab-atomic-transfer-*`. Make a local commit. Consolidate then remove
the exact named doctrine scratch files; retain test logs and verification.

The primary agent is the task, fixture and oracle author; its execution checks
are not independent validation or acceptance. Record its prior exposure to
CAPLAB's governance, code-authoring contracts and engineering doctrine. No
claim of blinded task authorship is authorized. No concept target, B/P code,
pairing, corpus source admission or independent human judgment is selected.
This world is development material, permanently excluded from an unobserved
study population; no later hash or rename restores that status.

No native/model call, historical-world/capture read or reuse, evidence admission,
frozen campaign change, codebook freeze, live database access, benchmark ranking,
placement, tracker write, external message or service operation is authorized.
Preserve capture owners, policy, existing worlds, `docs/designs/` and sibling
worktrees. Only new temporary databases may be executed or mutated. Stop if the
task requires real account data, non-disposable services, external side effects,
or a correctness promise its stated failure model cannot establish. Authorization
expires at the local commit.

## Selected work and limits

Build an atomic transfer task whose observable contract includes conservation,
insufficient-funds rejection, request deduplication, conflicting retry rejection
and rollback on a statement failure before that statement executes. Checking
only the final happy-path balance would miss partial debit, duplicate retry and
false-success failures. The oracle will inspect database state and exceptions,
not reference-patch similarity or concept words.

This supplies a concrete development exercise for the code-authoring contract's
correctness witnesses and negative examples. It does not complete CAPLAB-84's
world selection, independent validation, code derivation, capture integration
or representative shakedown. Selecting a corpus concept after authoring this
world would require its own decision and an exposure disclosure; no retrieval
success or spontaneous-rate measurement is claimed here.

## Constructed artifacts and observed discrimination

The world contains the task, parent, two candidate repairs, two negative
witnesses, a pure ledger model and executable oracle, and a development dossier
with exact content hashes and exposure exclusions. `TASK.md` was written before
the implementations and was not changed to fit their outcomes. This ordering
is recorded by the construction sequence; it is not an independent protected
freeze witness.

The immediate-transaction repair uses two account updates; the savepoint repair
uses one set-based update and different rollback/publication commands. Both
passed the same nine oracle checks, including the 100-call mixed retry sequence.
No patch text, concept word or reference similarity enters the oracle.

| Witness | Successful fresh transfer | Exact/conflicting retries | Before-statement failures |
|---|---|---|---|
| Broken parent | Pass | Fail | Partial state remains at two of four boundaries |
| Retry-only repair | Pass | Pass | Partial state remains at two of five boundaries |
| Rollback with false success | Pass | Pass | All seven fresh and all three replay failures are swallowed |
| Immediate-transaction repair | Pass | Pass | Pass at seven fresh and three replay boundaries |
| Savepoint/set-based repair | Pass | Pass | Pass at six fresh and three replay boundaries |

The false-success negative preserves balances under injected failure and still
fails because it does not propagate a SQLite error. This distinguishes correct
error behavior from state conservation alone. The retry-only negative passes
the ordinary sequences and still fails atomicity. A no-write success claim is
also rejected; absence of an observed statement yields unavailable fault
coverage. A cursor-based variant passes the fresh-transfer check but gets
unavailable fault coverage because that surface is not instrumented.

Nine focused tests passed in 0.297 seconds. They additionally check the ledger
model against a hand-calculated conservation/retry example, positive integer
subclass handling, and four two-connection schedules: competing withdrawals and
duplicate IDs for each candidate repair. Each observed schedule applied one
transfer, preserved the unrelated account, and retained one request record.
These are selected schedules, not an exhaustive concurrency proof.

`make check` completed with exit 0: **1,155 tests, four skipped, 160.759 seconds**.

Each database is new and disposable. Statement injection occurs once, before a
direct `execute` call, on fresh or exact-retry paths; recovery uses the same
connection and request. SQL reached through other APIs, post-commit failures,
power loss and real storage faults are not covered. Setup and oracle errors
propagate; candidate exceptions are recorded observations. This development
oracle is not an adversarial execution sandbox or a complete assessor for
arbitrary connection usage.

The task's argument contract accepts positive integers excluding booleans.
During implementation review the candidate type checks were corrected to admit
integer subclasses, and the oracle avoids requiring the identical exception
object where the task requires a propagated SQLite error. The written task was
preserved. Neither correction weakened the written contract to rescue a result.

Seven selected governing/capture files remain byte-identical to `f160b86`;
the change adds development files and tests without modifying runtime or existing
worlds. All new Python imports are used. Source preservation and the five-witness
probe are retained at `/tmp/caplab-atomic-transfer-source-check.json` and
`/tmp/caplab-atomic-transfer-probe.json`. Focused/full logs and the consolidated
verification manifest use the same `/tmp/caplab-atomic-transfer-` prefix.

## Exposure and remaining work

The primary agent authored the fixtures and oracle in the same ongoing session.
Its exact author Binding and complete prior-context inventory are not attested;
known governance and doctrine exposure is recorded in `development.json`.
The mechanical observations above are not an independent validator's verdict.
No human judgment, target concept, B/P pairing, behavior code, native episode,
spontaneous rate, legibility result or quality effect was manufactured.

This is a development exercise for testing correctness witnesses and failure
discrimination. Independent oracle review, validated observation coverage,
concept/code derivation where applicable, representative capture, coder accuracy
and blinding still precede study use. No previously exposed derivative can be
called an unobserved world. There is no reviewer ranking, qualification decision
or claim that this synthetic mechanism represents the production defect
population. CAPLAB-84 and the overall roadmap remain incomplete.

## Advisory disposition

The retrieval-state gate passed against
`/home/halbritt/.local/share/pincite/release`, release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`. Five typed evidence records supplied
authority, contracts, source structure, tests and the synthetic probe. Final
packet: `pkt-c7e3516d6c256cbe`, content SHA-256
`c7e3516d6c256cbe0f875e87f38267b523f5cae300922aad8ca497ceac7d0331`.

Applied `universal-repository-contract-precedence` to the development-only
authority, `implementation-risk-driven-tests` to interruption/retry witnesses,
`testing-coverage-is-not-adequacy` to independent state assertions and explicit
unavailable coverage, and `python-structured-cleanup` to disposable connections
and transaction ownership. All four citations classified as valid. This advisory
input is disclosed author exposure; it is not a served treatment or evidence of
concept recall.

Four missing obligations remain nonmaterial: `CI and build matrix` and `Python
and dependency version matrix` are unexpanded because this local SQLite exercise
claims no cross-platform compatibility; `formatter and static-tool configuration`
and `formatter linter and type-checker configuration` are unchanged and no new
static-tool guarantee is claimed. Existing repository checks and whitespace
verification supply the bounded local integration evidence.

The consolidated `/tmp/caplab-atomic-transfer-verification.json` records input,
probe, log and advisory hashes and deletion of eleven exact scratch files.
Probe and logs remain; temporary databases were removed by their owners. No
independent acceptance is recorded. Construction authorization expires at the
local commit containing this record.
