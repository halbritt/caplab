# Production review follow-up with verified baseline ancestry

Date: 2026-09-08. Report-only observation and software verification under the
repository owner's active CAPLAB improvement goal and the confirmed review
disposition. No model call, reviewer ranking, placement change, historical
evidence admission, or external request was made.

## Source and population

A fresh `striatum -json ledger cat` export completed with exit code zero from
`/home/halbritt/git/striatum-next`:

- Export: `/tmp/caplab-production-20260908-9e8Est/ledger.jsonl`.
- SHA-256: `ba8754dd853fc51442904fb2b7502fa253b164cff31c8205d3f4e4c37d18d3bf`.
- 406,971 events, sequences 0 through 406970; final timestamp
  `2026-09-08T09:53:36.328Z`.
- Graph: `019f22ef-0cb4-780f-9b82-b210bab24325`, from the genesis record.
- Fixed run-opening cutoff: 403343, from the
  [September 7 baseline](report-2026-09-07-production-review-canary.md).

The verified report is
`/tmp/caplab-production-20260908-9e8Est/verified-follow-up/report.md` with its
JSON companion. Its baseline reference records report SHA-256
`9f34182f130eb47baf632b5825711717390ff269b15ba0ec4a66e302283fe52c`
and ledger SHA-256
`6d06f5dff5542b1fcd45b51c39a700c74890920b67df93c8a662a6e00c2a6c93`.
The baseline's 2,534,867,842 bytes matched the new export's prefix exactly.

The window contains 27 anchored change-set or repo-doc reviews: 26 clearances
and one refusal, all with retained verdict bodies. Backend labels are
`agy-gemini-3-8-flash-high` on 26 runs and
`agy-gemini-3-8-flash-medium` on one. This is a routed production population,
not a matched comparison or an independently verified set of CAPLAB Bindings.
The complete retention in this window does not repair earlier missingness.

## Inspection candidate and outcome gap

Seven clearances and one refusal link to cancellation event 404284. The event
cancels request 388570 and activates replacement 404281 after resolution
404283. Its reason discusses planning livelock, compiler propagation of a
rejection reason, and a request reissue. It does not adjudicate the linked
review verdicts. The seven clearances are not seven independent defects.

Across the entire export, all 433 Principal acceptance gates name one of:
101 proposals, 104 designs, 201 implementation plans, or 27 decision records.
None names a change set. This inspection used `subject.identity`, including
the 142 older records without an applicability materialization. The aggregate
and cancellation links are retained in
`/tmp/caplab-production-20260908-9e8Est/source-inspection.json`.

Striatum commit `a6b1ae71d95cdf99200c10d8c6ce855d9da70a69` adds
`catalog/target-states/review-conclusions-are-evidence-bound.yaml`. It proposes
criterion-bound primary conclusions, independent typed challenges, and
separate measurement of reviewer roles. Its `status: proposed` and
`evaluator.mode: progress_only` explicitly deny current request or satisfaction
force and say the schemas and measurement implementation do not yet exist.
It is a prospective downstream requirement, not CAPLAB product authority or
proof that reference outcomes are available. The current ledger schema has
no new review-outcome event type.

The independent-outcome requirement remains unmet. A request cancellation,
critic challenge, agreement, or downstream acceptance alone cannot fill it.

## Implemented continuity check

`review_canary.py --baseline-report <report.json>` now verifies the prior
report's retained export against its hash and event-count metadata. The
reader checks that export as a byte prefix during the same scan that produces
the new snapshot. A different graph, altered prefix, truncated export, lost
baseline source, or inconsistent metadata prevents report emission.

An initial baseline supplies its final sequence as the cutoff. A follow-up
supplies its original cutoff, including zero, so later observations do not
silently change the selected population. The existing numeric `--after-run`
path remains available and does not claim baseline verification. Neither path
proves the export command completed or freezes object-store availability.
The [procedure](../product/advisory/production-review-report.md) documents
these limits and the new command.

## Verification and remaining work

The canary suite passed 12 tests, including CLI integration, source mutation
and truncation, missing baseline files, contradictory metadata, and fixed
cutoffs across follow-ups. Full `make check` passed 710 tests with four
existing skips and no failures or errors in 151.464 seconds. A final focused
rerun passed after tightening malformed baseline metadata handling. Logs:
`/tmp/caplab-followup-make-check.log` and
`/tmp/caplab-followup-focused-final.log`.

The actual verified follow-up was compared with the manual-cutoff report;
every observation and summary field was identical after removing the new
baseline reference. The historical criterion algorithm and prior reports
were preserved. The preceding goal turn is verified progress at `acaea50`.
The untracked system-design directory was left untouched. The overall goal
remains active; semantic finding validation and independently grounded
production comparisons remain material work.

Pincite guidance came from validated packet `pkt-3e3bd2739e798445`, content
SHA-256 `3e3bd2739e798445079217e3f5101a1f62dee4dcce3a5cf74d3181d6a5e3e203`,
doctrine `doctrine-f6bbb5196a3f8bf9`, retriever
`retriever-ec995ecdd083b2c8`. Applied concepts were
`implementation-risk-driven-tests`, `operations-gate-authoritative-signal`,
and `universal-repository-contract-precedence`. Checking the source prefix
enforces the existing same-graph procedure; a numeric range check alone cannot
establish continuity. Source inspection, regression tests, and the real-data
comparison supply the material evidence. Generic packet obligations about
rank truncation, ingestion traversal, architecture alternatives, and deployment
parity are nonmaterial to this local report input. No claim about reviewer
accuracy or live readiness follows from the guidance or passing tests.
