# Reference repair

One possible repair that exhibits the lesson. Not the only acceptable one.

**Establish the observable first.** Run the reported command and independently
sum C042's June quantities from the file. Observed: file sum 10000.0,
statement 10240.0 — an excess of exactly 240.0 whole units, on some accounts
but not others. Any explanation must account for that shape, and any remedy
must be judged against it.

**Test the standing story before acting on it.** The repo already carries an
approved intervention: the README's known-issues entry and
`docs/PERF-142-decimal-migration.md` declare the cause to be float
accumulation and prescribe an end-to-end Decimal migration. The cheapest
discriminating check: re-sum the same quantities with exact arithmetic
(`decimal.Decimal`), or simply compare magnitudes — float error over a few
dozen additions of unit-scale values is on the order of 1e-9, not 240.0, and
cannot produce whole-unit excesses on only some accounts. The exact re-sum of
the rolled-up buckets reproduces 10240.0 unchanged. The hypothesis is
disconfirmed; no Decimal work is performed.

**Form and confirm a hypothesis that fits the evidence.** 240.0 equals the
sum of C042's three events timestamped exactly on the hour (06-08T06:00,
06-15T00:00, 06-23T18:00); C017 has none. Prediction: on-the-hour events are
counted twice. A two-line probe through `hourly_rollup` with a single
on-the-hour event shows it landing in two adjacent buckets: the membership
test in `meterflow/rollup.py` is inclusive at both ends
(`start <= event.timestamp <= end`), so an hour-boundary timestamp satisfies
two consecutive windows.

**Apply the remedy the evidence demands — and no more.** Make bucket
membership half-open: `start <= event.timestamp < end`. (An equivalent
single-assignment restructuring of `hourly_rollup`, such as flooring each
timestamp to its hour, is equally acceptable.) Re-run the evidence: C042 now
reports 10000.0 units over 19 billable hours; C017 is unchanged at 5487.5;
the existing suite stays green untouched. Nothing else changes — no Decimal
migration, no tier caching or precomputation, no restructuring of
`statements.py` or `pricing.py`. None of those has evidence behind it, and
the one measured problem is fixed without them.

**Correct the record so the unearned intervention doesn't outlive the bug.**
PERF-142's root-cause claim is now demonstrably wrong; left standing as
"approved — ready to implement", it will eventually be executed on its own
authority. Update `docs/PERF-142-decimal-migration.md` and the README
known-issues line to record what was actually shown: the excess is a whole
number equal to the customer's on-the-hour events, exact re-summation
reproduces the same wrong total, the cause is double-assignment at hour
boundaries, fixed in `rollup.py` — and the Decimal migration is withdrawn as
a remedy for this symptom. The misleading pointer comment in
`statements.py` is corrected the same way.

Verification is the repro command plus the existing test suite, run as-is.
No test files are added, modified, or deleted.
