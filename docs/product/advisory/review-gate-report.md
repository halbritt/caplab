# Read an admission-gate report

The review gate records observations for one requested binding under tree-v1.
Its floors remain proposed. A report does not admit a reviewer or establish a
ranking. Live execution remains subject to the
[confirmed disposition](../../records/report-2026-09-07-review-instrument-disposition.md).

Inspect the planned population without making model calls:

```bash
PYTHONPATH=src python3 scripts/review_gate.py --plan <binding>
```

An authorized run writes `gate-result.json` with record type
`caplab-review-admission-gate-result/3`. The output directory must be new;
reusing a directory is refused to prevent accidental natural-case replay and
replacement of a prior report. Pool rows retain `control_attempts` and
`mutant_attempts`, including parsed responses, execution outcomes, and the
manifest check for each attempt.

Tree checks compare against the digest captured at materialization. A failed
pre-check prevents the call; a failed post-check retains the response but
excludes its verdict. Either stops the remaining assignments for that case.
`integrity_failure` names the phase and replicate (and the arm for pool
cases). Pool rows retain their planned replication and report
`control_unattempted_replicates` and `mutant_unattempted_replicates`;
natural cases report `expected_replicates` and `unattempted_replicates`.
Unattempted assignments contribute to unavailable counts without fabricated
responses. See the [integrity stop contract](../../records/repair-2026-09-08-tree-integrity-stop.md).

Every planned analog cell appears in `cell_observations` with one status:

| Status | Meaning |
|---|---|
| `scorable` | The operator produced a usable pair and all specified attempts supplied valid verdicts with successful execution and integrity checks. |
| `not_applicable` | The operator reported that it could not apply before any attempt. |
| `incomplete` | A row exists, but preparation or an attempt failed, or required evidence is absent. |
| `missing` | No retained row exists for the planned cell. |

The four counts sum to `cells_planned`. Duplicate or unexpected cells and
excess attempts are errors. Observed verdicts require exit code zero, no
timeout or transport error, a valid verdict, bwrap, and a passing manifest
check. Analog observations must also name tree-v1. Old rows without the
per-attempt evidence cannot establish those observations.

The shared response validator requires a JSON object with a supported verdict
and a list of finding objects. Supplied anchor, text, and rationale fields
must be strings. A successful process must explicitly record that it did not
time out. These checks validate the envelope, not the truth of its findings.

`missed` counts complete, scorable analog cells whose mutant was not refused.
Read it alongside coverage: zero misses with no scorable cells establishes
nothing about defect detection.

`controls_by_disposition` counts individual control attempts, grouped by the
adjudication ledger's `sound`, `defective`, and `unadjudicated` labels. Each
group reports expected attempts, observed verdicts, refusals, and unavailable
verdicts. Missing cells retain their expected control attempts. Inapplicable
cells require no calls. A valid control observation remains visible when its
paired mutant fails. One refusal among three control attempts counts as one
refusal even when the majority accepted.

The ledger labels are not proof of tree-v1 revalidation. Unadjudicated
controls remain separate; their refusals are not established false alarms.
The sound-label group must not support an admission decision without checking
that its adjudications apply to the execution environment and artifact.

Natural-case records retain each response and report unavailable attempts.
Only successfully observed attempts contribute to
`refused_with_exact_anchor_mention` or `mechanical_checks_passed`.
Natural cases name `anchor_matching: normalized-anchor-exact/1` and use the
shared exact matcher: formatting wrappers and case are normalized, but
`result_tree_hash_backup` does not match `result_tree_hash`. An exact mention
still does not establish that a finding demonstrates the defect. Full
responses remain available for inspection.

`conformance_validation: review-gate-conformance/2` separates the mechanical
checks from full contract conformance. The checks require a valid response
envelope, at least one nonempty anchor on a refusal, and a nonempty `rationale`
on every finding. A legacy `text` field does not supply the contract's
`rationale`. These are necessary checks, not a complete review-ledger schema
validator. A response that fails them has `ok: false` and status
`failed-mechanical-checks`. A response that passes has `ok: null` and status
`unverified`, including an accepting response with no findings.

`rationale_cues_present` reports the old word-pattern observation separately.
It supplies neither a pass nor a failure: “no harm exists” contains a cue,
while a concrete description of data loss can contain none. The gate has no
independent check that a clause was falsified, an in-force decision violated,
or harm demonstrated. The natural-case `conforming` count is therefore
`null`, not zero or a count of lexical matches. `conformance_unverified` and
`conformance_failed_mechanical` count the two statuses among observed
attempts. Together with `unavailable`, they account for the specified
replicates. An aborted pool leaves the natural cases unavailable and launches
no further calls.

The plan output also declares this assessment limit. The proposed conformance
floor cannot be established by this report. Version 2 reports retain their
historical lexical semantics; this change does not rewrite them or the frozen
gate specification.

Pool runs now record `response_validation: review-response/1`. A pair requires
all specified attempts to be valid before a majority score is emitted.
Individual valid observations remain in the attempt records when the pair is
incomplete. The summary distinguishes planned, missing, inapplicable, and
incomplete pairs; an incomplete prospective run is refused by the claim
export path even when it has some successful pairs. Resuming older rows under
the new validation contract is refused before any invocation. Historical
summaries retain their recorded semantics and are not rewritten by this
change.

New pool rows and summaries also name
`anchor_matching: normalized-anchor-exact/1`. Their `anchor_hit` requires
exact normalized location equality, and `anchors_emitted` retains the whole
representative list. Older matching contracts cannot be resumed into this
one. This changes location accounting only; neither the pool nor the natural
case establishes finding correctness from location mentions.

Prospective preparation now declares `pair_validation: paired-presence/1`.
The injection must declare itself checkable, its presence checker must return
exactly `True` on the mutant, and exactly `False` on the control. An unknown
result cannot launch a reviewer. The `unearned_verification_claim` heuristic
is also insufficient: a test can call a validating helper without containing
any schema-related words itself. Applicable cells in that class now remain
`incomplete` with an `oracle unverified` reason, rather than counting as
operator inapplicability or reviewer misses. This does not quarantine or
readjudicate a historical case. Resuming rows from older pair-validation
contracts is refused before invocation.

The gate specification is unchanged and still includes four candidate cells
for that operator. A future authorized gate run must disclose this preparation
gap; it cannot treat unavailable cells as passed. The existing abort policy
can stop a run after consecutive preparation failures. Mechanical contrast
on other operators is necessary, but is not a blanket guarantee of sound
controls or semantic finding correctness.

The pool's `run-spec.json` binds future results to the declared experiment and
the Python sources used to prepare it. The conclusion operator now preserves
the full selected heading and its element anchor; it no longer introduces a
missing-anchor defect alongside the intended conclusion. The corrected
generator must use a fresh run directory. A run specification is not native
Binding verification or evidence that a finding's rationale is correct.

These observations do not resolve the production-outcome gap. The
[production report](production-review-report.md) remains the report-only
surface for finding reviews and missing evidence to inspect.

## Adjudication input validation

Control records are validated when built, loaded from JSONL, supplied directly
to `Adjudications`, or appended. The expected v1 tag, nonempty dispatch ID and
recorded time, recognized disposition/basis kind, evidence-object list and
string-note list are required. Sound/defective records also require nonblank
basis and authority strings; mechanical-oracle records require nonempty
evidence. The historical `principal-ruling` spelling remains supported.
Recorded times must be nonempty strings; this boundary does not verify dates.
Unknown fields are retained if their JSON representation is valid.

Ambiguous duplicate JSON keys, non-finite values and unserializable records
are rejected. Loaded values are owned, so mutating the caller's original record
cannot change eligibility. A malformed record is an error, not an unaudited
or sound control. Optional absent ledgers still yield no adjudications.

Append validates the whole proposed batch before opening or creating its
destination. It retains the existing duplicate-ID skip behavior; loading an
existing history retains the last record for each dispatch ID. This is not a
concurrent-writer transaction or an atomic guarantee against later I/O failure.
An alias cannot overwrite an existing canonical control judgment.

These checks validate record structure, not truth. They do not authenticate a
named adjudicator, execute an evidence locator, prove authority or independence,
check environment applicability, or turn a control judgment into a production
gold outcome. The caller must still establish those facts before using it for
an authorized decision. No historical record is migrated by these checks.
