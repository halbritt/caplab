# Native review report contract

Status: development administration. This contract preserves what a reviewer
reports. It does not establish whether the review is correct or whether the
ranking instrument is valid.

The [v1 JSON schema](../../contracts/native-code-review-report-v1.json) keeps
each finding's title, claim, trigger, expected behavior, observed or predicted
behavior, change attribution, evidence and locations together. Free-text
fields retain qualifications. Locations refer to the reviewed tree using
relative paths and one-based inclusive line numbers; an unsupported location
may remain absent. Review limitations remain explicit.

Two judgments are reported separately:

| Field | Values and meaning |
| --- | --- |
| `claim_status` | `asserted`, `uncertain`, or `withdrawn`: the reviewer's current position on the claim. |
| `acceptance_effect` | `block`: recommends withholding acceptance pending resolution; `advise`: does not require that; `undetermined`: has not decided. |

A suspected problem may cause the reviewer to recommend blocking, but that
effect must be stated. Severity words, confident prose, a location or a list
headed “findings” do not supply a missing acceptance judgment. The report
format requests no minimum finding count or preferred disposition.

`caplab.native_review_report.inspect_report` checks representation, binds each
complete finding to its raw report and inspects only that finding's locations.
It retains wrong, missing and unsafe locations as unresolved locator states
without opening paths outside the supplied source tree. A valid line range
establishes a locator, not causal support. Exact duplicate findings remain
in the report with equal content hashes and separate occurrence identities;
their row count is not a defect count.

The inspector rejects duplicate JSON keys, including keys that could erase
findings or overwrite an acceptance effect. Missing required judgments and
malformed reports do not become a clearance. Empty findings also establish
no clean-control outcome. Raw native capture remains authoritative when
inspection fails; capture failures and report failures are separate.

## Connection to outcome assessment

An outcome assessment must identify the exact finding occurrence and content,
its claimed scenario and location, the independently justified requirement,
observed behavior and change attribution. Evidence for one finding cannot
be assigned to another merely because both occur in the same review. A
reproduced trigger does not settle a disputed normative scope.

The old closed-hypothesis prototype aggregates locations at document level.
It now withholds causal credit when several claims or unmapped findings make
that association ambiguous. Its six authored single-scenario calibration
cases remain development evidence. The correction does not accept that
prototype for natural multi-finding reviews.

A future incorrect-blocker measure requires both an explicit reported blocking
effect and an independently refuted claim within the relevant scope. Reported
uncertainty, withdrawal and conflicting positions must be retained; scoring
policy must define their treatment before comparing results. Unknown truth,
an unspecified acceptance effect or a failed attempt is not a correct
clearance or a false blocker.

## Administration experiment

The [bounded authorization](../../../records/authorization-2026-09-10-reviewer-finding-units.md)
permits one native review of the same full newsroom task with this final-report
format and the native CLI's output-schema option. Original source, task access,
dependencies, budgets and isolation remain fixed. Prior reviews and known
outcome witnesses remain outside the subject mount.

Repeating an exposed development case with changed reporting instructions
does not create an independent case or a paired performance comparison.
Verification must inspect the actual final claims and reported effects,
separately from JSON and capture validity. Broader case coverage, prospective
scoring challenges, frozen comparisons and held-out evidence remain required.
