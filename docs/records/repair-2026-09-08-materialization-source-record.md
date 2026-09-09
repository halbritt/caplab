# Bind reused review materializations to their requested source record

Date: 2026-09-08. Baseline: `01a2a81`. Primary-agent decision and bounded
execution authority under [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Reproduce source-record mismatch on an existing case using synthetic store
objects and evidence only. Repair `src/caplab/advisory/materialize.py`, add
regressions in `tests/test_advisory_materialize.py`, and update this record.
New manifests must bind the complete JSON source record by a deterministic
SHA-256. Reuse and rebuilding of an existing manifest require that identity
to match the requested record. Refuse missing, mismatched or unreadable
identity before removing any existing bytes. Legacy manifests remain readable
by the integrity verifier; they cannot be silently adopted or overwritten by
materialization. A separately authorized fresh case is the recovery path.

Preserve same-record valid cache reuse without requiring the live source,
dictionary-order independence, and existing same-record damaged-payload
rebuild behavior. Keep canonical product bytes, overlay semantics, source
selection, view filtering and historical evidence unchanged. This is a cache
identity defect repair, not a performance change or complete source-provenance
proof. Inputs and case parents must remain stable during the operation; no
concurrent-writer synchronization is added.

Run focused tests, an inspectable synthetic probe, and `make check` with its
existing prescribed read-only store checks. Keep source/authorization snapshots,
logs and probe custody under `/tmp/caplab-source-record-*`. Consolidate advisory
provenance before deleting only named advisory scratch. Commit these three
files locally; authorization expires at commit. Stop if reproduction fails or
the repair needs broader effects. No historical evidence copying, migration,
admission, rewrite, purge or replay; no model/native invocation, study run,
score, ranking, tracker write, external message, push or service change.
Preserve unrelated `docs/designs/`, worktrees and timers.

## Observed path and selected response

`pool_runner.measure_case` names its workspace using substrate, operator and
seed. `materialize_case` currently accepts a verifying cache without comparing
its source record. The requested object, evidence payloads, artifact-removal
path or other source metadata may therefore change while the old tree is
reused. Byte integrity is necessary but cannot establish requested-input
identity. This is an observable local failure path; no historical occurrence
has been established.

Bind the entire JSON record, including evidence and view-removal inputs,
instead of maintaining a second list of selected identity fields that can
omit a future input. Dictionary key order is immaterial; array order and
all values remain significant. Even a provenance-only metadata change
requires a fresh case. This conservative rule prevents ambiguous adoption.
Leaving the behavior unchanged retains stale-input risk. Automatic rebuilding
on a mismatch would destroy existing custody and is rejected. A new manifest
field under the existing record type allows retained old manifests to remain
verifiable without claiming that their requested record is known.

## Execution and verification evidence

The baseline produced eight failed expected-refusal subcases: five changed
source-record inputs and three unsafe legacy/damaged/unreadable-manifest
rebuilds. One additional assertion errored because the new identity field did
not yet exist; that error is not counted as a defect reproduction. The log is
`/tmp/caplab-source-record-red.log`.

`source_record_sha256` now hashes UTF-8 JSON with sorted keys,
`ensure_ascii=False`, `allow_nan=False`, and Python's default separators. It is
included in the manifest's existing digest. Existing manifests are read and
compared before payload verification or any cleanup. A missing or mismatched
binding raises `ValueError`; malformed JSON raises its normal `ValueError`
subclass, and read errors propagate. No mismatch path rewrites the old case.
The existing runner catches these materialization failures and returns an
unusable observation before any reviewer invocation.

All 42 focused tests passed in 0.322 seconds, covering materialization,
tree-v1 and invocation integrity stops. The log is
`/tmp/caplab-source-record-focused.log`. Four new test methods cover changed
objects, evidence, base class, substrate identity and artifact-removal paths;
dictionary-order-independent reuse; legacy/unreadable/mismatched manifests;
and same-record damaged-payload rebuilding. The earlier contradictory-cache
test now accepts either rejection reason: source-record mismatch occurs before
the anchored-product check. Its rejection and byte-preservation assertions
remain, and the separate fresh-source anchor tests are unchanged.

The inspectable probe in `/tmp/caplab-source-record-probe-zbn2jgjg/` requested
a changed synthetic requirement under the same substrate. Baseline returned
the original manifest and original requirement. Fixed materialization refused
the request and retained both existing file hashes. The script, exact input
records, observed outcomes and source hashes are retained in
`/tmp/caplab-source-record-probe.py` and
`/tmp/caplab-source-record-probe.json`. Every materializer function except
`materialize_case` has unchanged source bytes, recorded in
`/tmp/caplab-source-record-protected.json`.

## Boundaries and advisory use

This binds requested-record identity; it does not authenticate the record,
establish external Git-tree completeness, version the materializer's policy,
or synchronize concurrent writers. A copied or hostile self-consistent
manifest still requires the independent digest checks already used by the
execution caller. No historical cache was inspected or migrated. The fresh
Plane snapshot `/tmp/caplab-roadmap-current-01a2a81.json` still lists the open
capture, coding, blinding and study-design tasks; this repair closes none of
their representative-measurement or independent-judgment requirements.

Pincite retrieval-state verification passed against release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-e58c5e9c8d98f74b` uses four typed observations for authority/contracts,
source, tests and the retained probe. Repository precedence, reproduction,
semantic-change classification, preservation and bounded authority are the
selected guidance. Packet content hash, corpus/doctrine/retriever identities,
evidence and citation classifications are consolidated in
`/tmp/caplab-source-record-verification.json`.

The receipt retains all 33 remaining generic obligations with individual
nonmaterial classifications and reasons: no database deduplication, bulk
ingest, reference registry, ranking, monitoring or external service is changed;
no historical incident, duplication refactor, broad future-risk audit or formal
procedure export is claimed. The local preservation matrix and observed
failure, rather than these broader claims, support the bounded repair.

## Final verification and integration

`make check` exited 0: 1,186 tests in 161.288 seconds, 4 skips.
The retained log is `/tmp/caplab-source-record-make-check.log`. All five
selected doctrine citations classified as valid packet citations. Ten named
advisory scratch files were consolidated into the verification receipt before
removal; authorization, source snapshots, probe custody and test logs remain.

The test guard pass retained four distinct behavioral scenarios and real
filesystem/store operations. The documentation guard pass checked the new
field, failure behavior, runner error handling and local links against current
source. No additional changed-surface defect was found. Local integration
consumes this authorization; it does not accept a study or establish reviewer
correctness. The broader goal remains active and incomplete.
