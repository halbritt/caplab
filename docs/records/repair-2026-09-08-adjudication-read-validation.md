# Validate control adjudications before they influence reporting

Date: 2026-09-08. Baseline: `53e3ede`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before repair

Repair `src/caplab/advisory/adjudication.py` so public construction, JSONL load
and append cannot bypass the record contract. Add focused tests in
`tests/test_advisory_adjudication.py`, replace the incomplete synthetic record
in `tests/test_review_gate.py`, document the boundary in
`docs/product/advisory/review-gate-report.md`, and update this record. These five
files are the only edit targets. Run synthetic reproductions, focused tests and
`make check`. Retain bounded scripts/logs and advisory receipts under
`/tmp/caplab-adjudication-read-*`; commit locally after verification.

Require the expected record tag, nonempty dispatch ID and recorded time,
recognized disposition and basis kind, explicit nonblank basis/authority for
sound or defective judgments, dictionary evidence entries and string notes.
Mechanical judgments require nonempty recorded evidence. Reject ambiguous JSON
keys and non-finite JSON values. Own admitted record values so later caller
mutation cannot change a loaded judgment. Validate the complete input batch
before append opens or changes a destination. Preserve existing last-record-wins
loading, alias precedence, duplicate-ID append skipping and optional missing-file
behavior. Structural validity is not proof of truth, authority or independence.

The existing 71-record historical ledger at
`advisory/control-adjudications.jsonl` has SHA-256
`3171bd4a9278134a3f43cf1f491ebcd7390e6eb6e81c18ab274e672c80ce4c30`.
It uses `principal-ruling` for four recorded Principal judgments, documented in
`adjudication-dossiers-2026-08-23-sol-clean-controls.md`. Preserve that existing
basis spelling alongside human-adjudication and mechanical-oracle; do not
silently rename it or infer new Principal authority. Verify all existing
records and effective dispositions remain readable and unchanged. Stop if the
repair would require migrating or relabeling any historical entry.

No historical evidence mutation, relabeling, admission, registration, scoring,
claim rebuild, model call, tracker write, external message, push or service
change. Preserve unrelated `docs/designs/`, source custody and worktrees.
No correctness/adjudication judgment is delegated by this validation repair.
Consolidate advisory evidence before deleting only named scratch; authorization
expires at commit. Stop on wider required effects.

## Reproduction and implementation

The initial six regression methods produced 16 failures against the original
implementation. Public construction accepted missing metadata, foreign tags,
unknown dispositions/bases, blank authority and malformed evidence. The JSONL
reader accepted duplicate disposition keys. Caller mutation changed an already
loaded/aliased judgment. Append accepted an invalid later record, and the builder
retained nested caller-owned evidence. Baseline output is
`/tmp/caplab-adjudication-read-baseline.log`; these are synthetic reproductions,
not claims that the historical ledger contains those defects.

One local validator now owns record validation and copies values at construction,
build and append ingress. JSONL parsing rejects duplicate keys before records
enter that validator. It checks the same UTF-8 JSON representation used for
append, so serialization errors in a later batch member cannot be discovered
only after earlier members have been written. The validation error propagates;
no malformed judgment becomes a default sound or unaudited control.

The existing review-gate test previously supplied only a dispatch ID and a
sound label. It now constructs a complete synthetic judgment with its stated
test authority; its gate-count assertions are unchanged. No production control
record is rewritten. The documented Principal-ruling basis is preserved as an
existing human-judgment spelling, not new authority conferred by this repair.

The code still cannot authenticate the named authority or establish that an
evidence claim is true. Empty evidence objects remain structurally valid entries;
the semantic sufficiency of a check, evidence location and environment is still
the caller's responsibility. Recorded times are nonempty strings, not validated
dates. Optional absent ledgers and duplicate/alias precedence retain their prior
behavior. Append is not a concurrent-writer transaction or protection against a
later filesystem I/O failure.

## Focused and compatibility verification

The six new methods pass in 0.022 seconds, covering both record ingress paths,
ambiguous JSON, caller ownership, whole-batch refusal before file mutation,
legacy basis and duplicate precedence, non-ASCII round trips, and nested evidence
ownership. The existing 16 review-gate tests pass in 0.013 seconds. The malformed
append cases also cover unencodable text and a nested mapping that cannot use
the writer's sorted JSON serialization. Tests use real temporary files and
public results; no mock validator or internal-call assertion was introduced.

All 71 records in the unchanged historical ledger load successfully, producing
the same 70 effective dispatch judgments under last-record-wins semantics.
Its SHA-256 remains `3171bd4a9278134a3f43cf1f491ebcd7390e6eb6e81c18ab274e672c80ce4c30`.
The read-only compatibility result is
`/tmp/caplab-adjudication-read-compatibility.json`. No scores, claims or historical
judgments were recomputed or changed. Keeping permissive reads would retain the
observed bypass; validating only the builder would leave file and direct-object
ingress unprotected. Shared validation preserves a single record owner.

## Full verification and advisory closure

`make check` exited 0: 1,205 tests in 220.200 seconds, four skips. The complete
output is `/tmp/caplab-adjudication-read-make-check.log`. This verifies the
repaired boundaries and existing suite; it does not accept judgments or certify
reviewer accuracy. No live native attempt was launched.

The validated Pincite release is `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`;
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
Final packet `pkt-374be0bd6323cd85` has content SHA-256
`374be0bd6323cd853836b8366504d43f6e53eab7caac8e764805eb3de838180f`.
The execute ceiling is advisory; ADR 0026 and the explicit scope above supply
authorization. The selected concepts are repository-contract precedence,
evidence before intervention, authority-bounded action, behavior preservation,
and configuration-reference validation. The last applies to the record tag
and defined enums; evidence locators are not resolved or authenticated.

Thirty remaining generic evidence obligations are retained individually with
nonmaterial classifications and rationales in
`/tmp/caplab-adjudication-read-verification.json`. They concern unchanged
identity policy, bulk discovery, ranking, external integration, broader gate
and monitoring audits, production incidents, quantified intervention cost and
formal procedure exports. The narrow claim is the reproduced local validation
repair, supported by synthetic regressions and unchanged-ledger compatibility.
No broader reliability, semantic authority, independent adjudication, selection
confidence measurement or roadmap acceptance is inferred.

The verification artifact consolidates both packets, typed evidence and citation
classification before removal of the ten named advisory scratch files. It also
pins the retained authorization, observations, diff, tests, compatibility result,
full-suite log and completed record. Source custody, historical ledger,
`docs/designs/` and sibling worktrees remain outside the change.
