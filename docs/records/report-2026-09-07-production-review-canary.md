# Production review report: first usable canary

The Principal asked: “can you help me make caplab actually useful?”
This change supplies a production report that identifies reviews to inspect.
It does not establish reviewer accuracy or accept a CAPLAB outcome.

The confirmed review-instrument disposition permits a report-only canary
([§4](report-2026-09-07-review-instrument-disposition.md)). Model spend remains
zero. Placement, admission thresholds, source records, and Striatum declarations
are unchanged. The Striatum request remains a draft for the Principal.

Observation: the existing criterion command produced retrospective strata,
but no fixed review window or complete per-run inspection report. Its case
output omitted reviews outside four strata. The new command reuses its reader
and adds a report projection. The old command retains its output format.

The report shows decisions, missing verdicts, run outcomes, elapsed time,
and downstream event links. It groups candidates by downstream event.
One request cancellation can attach to many reviews. Those links are
inspection candidates, not independent defects or adjudicated outcomes.
Reviewer labels come from the ledger. They are not verified exact Bindings.

## First observation

Source: a fresh `striatum -json ledger cat` export, completed with exit code
zero from `/home/halbritt/git/striatum-next`.

- Export: `/tmp/caplab-review-canary-20260907-ledger.jsonl`.
- SHA-256: `6d06f5dff5542b1fcd45b51c39a700c74890920b67df93c8a662a6e00c2a6c93`.
- 403,344 events, sequences 0 through 403343.
- Final event time: `2026-09-07T05:37:21.606Z`.
- Report: `/tmp/caplab-review-report-20260907/report.md`, with all selected
  run and event locators in `report.json` beside it.

The initial report is a retrospective baseline. A fixed cutoff of 403343
can select subsequent reviews for future reports.

| Observation | Runs |
|---|---:|
| Anchored change-set or repo-doc reviews | 6,321 |
| Cleared | 2,969 |
| Refused | 471 |
| No retained verdict | 2,881 |

Of the 2,881 runs without a retained verdict, 1,979 closed as
`submitted_partial`, 852 as `canceled`, 40 as `abandoned`, and 9 as `error`.
One remained open. These counts do not establish that output was lost or
that a reviewer answered incorrectly.

Recommendation: inspect the partial submissions and their capture path before
using the retained population to compare reviewers. The missingness limits
such comparisons. The production report can identify records for that work.

## Verification and limits

- The actual command read the fresh export and produced the report.
- Nine canary and gate tests passed, with five subtests. They cover missing
  and open runs, chronology, repeated cancellation links, fixed cutoffs,
  verdict precedence, source hashes, escaped text, and overwrite refusal.
- Both legacy criterion output files were byte-identical before and after
  the extraction on a mixed-outcome fixture at source commit `e6c8d3a`.
- The full suite produced 678 passes, four skips, and two failures already
  named in the handoff: missing `.github/workflows/check.yml` and a pinned
  Codex binary mismatch. The focused tests passed after the final edits.

The report needs a complete export and the local object store. It refuses
empty exports, invalid JSON, sequence gaps, and existing output directories.
A truncated export that ends on a complete event still requires the export
command's exit status to detect. The source hash identifies bytes, not
completeness or evidence admission.

No timer is installed. No review-specific re-ruling event reader is implemented.
The report computes no gold score, correctness rate, or placement decision.
Applications and conflicts join by hash. Cancellations join by request and
defect wording. These joins need individual inspection before any judgment.

The [procedure](../product/advisory/production-review-report.md) explains
refreshing the report and keeping the observation cutoff fixed.

## Engineering recommendation receipt

The recommendation was to extend the existing read path with a bounded report.
Leaving the old command alone would leave the inspection path incomplete.
Changing the leaderboard would still require this missing read path.
The implementation adds a projection and preserves the existing criterion output.
It adds no external service, model call, or source-record mutation.

Doctrine supported the recommendation only. Repository authority remained
with the Principal's request and confirmed disposition. Selected concepts:
`universal-evidence-before-intervention`,
`universal-repository-contract-precedence`, and
`agent-conduct-authority-bounded-action`.

- Packet: `pkt-26a8db951a6a989b`.
- Packet file SHA-256: `4e141ad8fee6cd6d551c2573fffaa4769436f5cf6457cc810b7bea19e9b2b0c8`.
- Doctrine: `doctrine-f6bbb5196a3f8bf9`.
- Retriever: `retriever-ec995ecdd083b2c8`.
- Release commit: `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
- Source locators: the confirmed disposition, `AGENTS.md`, the domain
  language, both report scripts, and `tests/test_review_canary.py`.

The remaining generic obligations are nonmaterial to this bounded addition:
co-change, raw commit samples, architecture pressure, coupling and test pain,
performance cost, and broad schema/caller migration analysis. No conclusion
on those subjects is made. Preservation is bounded to the legacy CLI fixture
and report tests, with the two full-suite failures disclosed above. The report
does not discharge the missing independent-outcome requirement for ranking.
