# Retraction — claim `qc-5c3d57292faa3f1b` (aborted-run admission)

- Date: 2026-08-16
- Subject: `claude-fable-5-high`, construct `review.defect_discrimination/1`
- Custody: `caplab-advisory`
- Disposition: **void** — admitted in violation of the admission rule, not
  superseded by a better measurement

## What happened

The supervised run `advisory/runs/adv-claude-fable-5-high-20260816` was cut
off by the vendor account's session limit ("You've hit your session limit ·
resets 1:20am (UTC)"). The instrument detected it correctly and aborted
after 9 consecutive empty lanes, leaving 7 usable pairs of a 21-pair target.

CAPLAB nonetheless derived and admitted a claim from it, because
`caplab.advisory.scoring.completed()` treated the presence of `summary.json`
as proof of completion — and the instrument writes its summary *before*
raising its abort. A killed run therefore left a complete-looking directory
holding a truncated sample.

The claim recorded catch 0.571 / false-alarm 0.429 on n=7. Those numbers
describe an outage as much as a subject: the sample is a seven-case prefix
of a matched set, selected by when the vendor cut the account off.

## Why void rather than superseded

Advisory claims are append-only and are normally retired by a superseding
claim. This one is different in kind: it was never admissible. Its own
governing rule — a run that aborted is excluded whole — was in force and
was not applied because of a defect in the check. Leaving it in the ledger
with a superseding sibling would imply two lawful readings of one subject.
The row is removed from `advisory/claims.jsonl`; the git history of that
file preserves the fact that it existed, and this record states why.

## Corrective

`completed()` now requires both that `summary.json` exists and that it
carries no `aborted` value, and the execution receipt additionally records
the abort text and the instrument exit code. Two regression tests cover it
(`test_aborted_run_is_not_complete`, `test_aborted_run_yields_no_claims`).

The 55 `historical-seed` claims were re-derived under the fixed rule and are
byte-identical: no tuner run contributed rows through this defect.

The companion run `advisory/runs/adv-claude-fable-5-medium-20260816` hit the
same limit with 0 usable pairs and produced no claim.

## Lineage

This is the fifth instance of one shape in this program's history, after the
four the striatum-tuner rescore commit named (agy's print-timeout discarding
completed work, `TimeoutStartSec` killing a drive before it wrote its
session record, revbench exiting 0 over 152 empty attempts, and scoring
reading `results.jsonl` without checking for a summary). The question that
catches all five is not "did it report failure?" but **"what record does the
abort path fail to write — and do we require it?"** Here the abort path did
write a record; what it failed to do was withhold one.
