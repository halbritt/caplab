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
`caplab-review-admission-gate-result/2`. The output directory must be new;
reusing a directory is refused to prevent accidental natural-case replay and
replacement of a prior report. Pool rows retain `control_attempts` and
`mutant_attempts`, including parsed responses, execution outcomes, and the
manifest check for each attempt.

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
Only successfully observed attempts contribute to `refused_and_anchored` or
`conforming`. Conformance validates structure and the existing lexical
discipline rule; mentioning a clause, decision, or harm does not establish
that the rationale is correct. Likewise, naming `result_tree_hash` is not
proof that a finding demonstrates the defect. Full responses remain available
for inspection. An aborted pool leaves the natural cases unavailable and
launches no further calls.

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
one. This changes location accounting only; the gate's natural-case lexical
conformance checks remain bounded as described above.

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
