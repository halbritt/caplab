# Inspect production reviews

Use the production review report to find work that needs inspection.
It shows review decisions, missing verdicts, elapsed time, and later events.
It does not measure reviewer accuracy or change placement.

The [confirmed disposition](../../records/report-2026-09-07-review-instrument-disposition.md)
permits this report-only canary. It freezes placement and model spend on
injection sweeps. A gate run still needs a named binding from the Principal.

Create a fresh ledger export from the Striatum repository. This reads the
ledger. It does not run a review or change a declaration.

```bash
cd /home/halbritt/git/striatum-next
striatum -json ledger cat > /tmp/caplab-review-ledger.jsonl
```

Wait for exit code zero before using the export. A partial export can contain
valid JSON and still omit recent events. Keep the export while inspecting
the report. The report records its path, SHA-256, event count, and final sequence.

Create a report in a new directory:

```bash
cd /home/halbritt/git/caplab
PYTHONPATH=src python3 scripts/review_canary.py \
  --ledger /tmp/caplab-review-ledger.jsonl \
  --out /tmp/caplab-review-baseline
```

Open `/tmp/caplab-review-baseline/report.md`. Its JSON companion retains each
selected run and the event locators. Existing report directories are refused.
The reader uses the same local Striatum object store as the criterion ledger
pass. A snapshot without its object store can have missing review bodies.

For a prospective observation window, record the baseline's
`snapshot.last_seq` before collecting further reviews. After production runs,
export a fresh ledger and pass that sequence as `--after-run`:

```bash
PYTHONPATH=src python3 scripts/review_canary.py \
  --ledger /tmp/caplab-review-ledger-next.jsonl \
  --after-run 403343 \
  --out /tmp/caplab-review-follow-up
```

`403343` is the initial report's cutoff, not a moving default. Keep the cutoff
fixed across follow-up reports so later outcomes remain attached to the same
review population. Reuse exports from the same graph. No timer is installed.

To verify that a new export extends your baseline, pass its report instead
of typing the cutoff:

```bash
PYTHONPATH=src python3 scripts/review_canary.py \
  --ledger /tmp/caplab-review-ledger-next.jsonl \
  --baseline-report /tmp/caplab-review-baseline/report.json \
  --out /tmp/caplab-review-follow-up-verified
```

Keep the baseline's source export at the absolute path recorded in its
`snapshot.path`. The command checks that file's SHA-256 and event-count
metadata, then verifies its bytes as an unchanged prefix while reading the
new export. A different graph, rewritten history, truncated export, or missing
baseline source is refused before a report is written. Baseline report and
ledger hashes are retained in the new report's `baseline` field.

An initial retrospective report supplies its last sequence as the cutoff.
When a follow-up report is used as the baseline, its original `after_run`
cutoff is preserved. This keeps the population fixed while extending its
observation period. `--baseline-report` and `--after-run` cannot be combined.
The numeric form remains available for manual windows; it does not verify
baseline ancestry. Prefix verification establishes continuity, not completion
of the new export command, availability of object-store bodies, or accuracy
of a review. Continue to require exit code zero from the export command.

Read the report in this order:

1. Inspect missing verdicts and their run outcomes. A cancellation or partial
   submission can explain missing output. Missing output is not a wrong answer.
2. Use the downstream event list to locate work for inspection. One event can
   link to many reviews. The JSON retains the review run, subject version,
   content hash, reviewer label, and downstream event sequences.
3. Read the source event and artifact before judging a review. Cancellations
   join by request and defect wording. They can describe a process failure.
4. Compare a later report with the same cutoff to observe new outcomes.

The population contains review runs with a materialized-base pin and a
change-set or repo-doc subject. Prose reviews are excluded. Open runs and
missing verdicts remain in the denominator. A retained verdict body takes
precedence over a review gate result. Gate-only verdicts are counted separately
in JSON. Reviewer names are backend labels from the ledger, not independently
verified exact CAPLAB Bindings. Wall time covers all closed outcomes and
includes failures. It is not successful-review latency or a speed ranking.

Applications and conflicts join by content hash. Request cancellations join
more broadly. Only events after run closure count as later outcomes. A newer
artifact version after refusal is reported without a judgment of correctness.
Short follow-up can hide later problems. The script does not infer gold
outcomes from downstream acceptance events.

To support reviewer accuracy comparisons, Striatum still needs the
[review-specific outcome records](../../records/request-2026-09-07-striatum-review-outcome-events.md)
requested in the draft for the Principal. That request remains unfiled by CAPLAB.
