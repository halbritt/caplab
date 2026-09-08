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
New reports use `caplab-review-canary/3` with
`downstream_ordering: ledger-sequence-after-review-closure/1`.
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
Versions 1, 2, and 3 can supply a verified baseline. The
reference records that version. Moving from version 1 to version 2 can expose
links previously omitted by timestamp filtering or missing verdicts; ledger
continuity does not mean the report calculations stayed the same. Version 3
also corrects stale verdict provenance and exposes source discrepancies.
Historical reports are not rewritten.

Read the report in this order:

1. Inspect missing verdicts and their run outcomes. A cancellation or partial
   submission can explain missing output. Missing output is not a wrong answer.
2. Use the downstream event list to locate work for inspection. It includes
   cleared, refused, and unknown-verdict reviews, with separate counts. One
   event can link to many reviews. The JSON retains the review run, subject version,
   content hash, reviewer label, and downstream event sequences.
3. Read the source event and artifact before judging a review. Cancellations
   join by request and defect wording. They can describe a process failure.
4. Compare a later report with the same cutoff to observe new outcomes.

The population contains review runs with a materialized-base pin and a
change-set or repo-doc subject. Prose reviews are excluded. Open runs and
missing verdicts remain in the denominator. A recognized verdict from the
latest admitted review body takes precedence over the latest review gate
result. Gate-only verdicts are counted separately
in JSON. Reviewer names are backend labels from the ledger, not independently
verified exact CAPLAB Bindings. Wall time covers all closed outcomes and
includes failures. It is not successful-review latency or a speed ranking.

`verdict_selection: latest-admitted-body-then-latest-review-gate/1` names
that selection rule. If the latest body is unavailable or supplies no
recognized verdict, an older body's verdict cannot be attached to its hash.
The report falls back to the latest gate or leaves the decision unknown.
This rule describes the report's observation; it does not decide which
source is correct or whether a later admission validly supersedes an earlier
one.

`review_body_observations` retains every matching admission's event sequence,
artifact identity, body hash, raw verdict field, read status, and response
envelope error. Status distinguishes a missing or invalid reference,
`unavailable-or-unverified` bytes, invalid JSON, a non-object JSON value, and
a parsed object. The object-store reader verifies hashes but groups missing,
undecodable, and hash-mismatched objects together as unavailable. A parsed
object can still have an unsupported verdict or malformed findings. The
recognized verdict remains an observation; envelope validity and semantic
conformance are separate questions. The hash locates the full body without
copying it into the report.

`review_gate_observations` retains each linked gate event and its raw outcome.
Repeated evidence references within one gate event do not duplicate that
event. `multiple_body_verdicts`, `multiple_gate_outcomes`, and
`body_gate_disagreement` expose source differences without adjudicating them.
Reviewer summaries count these flags and latest-body statuses. The Markdown
groups issues and provides the first three run locators in ledger order;
JSON retains all observations. Runs without an admitted body remain visible
as `not-admitted`, including when a gate supplies the only verdict.

`lifecycle_observations` retains linked `pass_run_closed`,
`submission_received`, `admission_decision`, `submission_refused`, and
`dispatch_lapse` events in ledger order. Each entry names the event sequence,
schema version, timestamp, and relevant recorded detail. Submission entries
include diagnostic and submission-object references, without reading those
bodies. This field is an additive extension of version 3 reports.

`unknown_verdict_lifecycle` (`caplab-review-lifecycle/1`) summarizes only
reviews whose reported verdict is unknown. Closure-source counts use the
selected closure event; open runs and missing closure-source labels stay
explicit. Scheduling deferral reasons remain separate from submission and
admission outcomes. Admission refusal codes are paired with their recorded
`submitted_state` and report both event counts and distinct runs. A run can
have several admission decisions, including decisions about other outputs;
these rows can overlap and are not counts of incorrect reviews.

Read `schema_invalid` alongside its detail and submitted state. A record
with state `absent` and detail `required output missing` does not establish
that the reviewer emitted malformed JSON. Likewise, a cancellation sourced
from `scheduling_deferral` is a scheduling observation, not evidence of a
reviewer refusing or failing its task. Diagnostic references can support
further inspection; their presence alone does not explain the root cause.

Applications and conflicts join by content hash. Request cancellations join
more broadly. A missing content hash or request reference supplies no join;
two absent identifiers do not establish a relationship. Only events with a
ledger sequence greater than `closed_seq` count as later outcomes. Tied or
reversed timestamps do not remove those events, and a future timestamp on an
earlier event does not make it a later outcome. Original timestamps remain in
the report. Open reviews have no post-closure events.

Closed reviews with unknown verdicts retain the same downstream links and
later-version observations as reviews with verdicts. The links cannot supply
their missing verdicts. Reviewer summary columns still count clearances and
refusals separately; adding an unknown review to the inspection list does not
count it as either. A newer artifact version after refusal is reported without
a judgment of correctness.
Short follow-up can hide later problems. The script does not infer gold
outcomes from downstream acceptance events.

To support reviewer accuracy comparisons, Striatum still needs the
[review-specific outcome records](../../records/request-2026-09-07-striatum-review-outcome-events.md)
requested in the draft for the Principal. That request remains unfiled by CAPLAB.
