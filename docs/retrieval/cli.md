# Run a retrieval experiment

CAPLAB measures whether each configured retrieval command ranks frozen labelled
notes for the supplied queries. Read the corpus, labels and control strata
before interpreting a score. Retrieval quality, observed body exposure and
verified task completion are separate measures. A retrieval report is an
observational experiment artifact; it is not a qualification or acceptance
record.

Start with the [provider-free example](../../examples/retrieval/README.md).
The package requires Python 3.12 or later. From the repository root, use
`PYTHONPATH=src python3 -m caplab retrieval ...`; the equivalent module entry
point is `PYTHONPATH=src python3 -m caplab.retrieval ...`. Installed packages
also provide `caplab retrieval ...`.

## Commands

| Command | Arguments | Behavior |
|---|---|---|
| validate | `--spec FILE` | Parse strict UTF-8 JSON and emit the validated normalized spec; no retrieval or output directory creation |
| run | `--spec FILE --output NEW_DIRECTORY` | Seal the full assignment roster and execute actual configured adapters; retain evidence and emit the report |
| report | `--run DIRECTORY [--format json\|markdown]` | Verify retained artifacts before emitting a report; JSON is the default |
| compare | `--left DIRECTORY --right DIRECTORY [--left-arm ID --right-arm ID]` | Verify both bundles and align compatible cases/seeds; select arms explicitly for within-run comparisons |
| import-task | `--report FILE --plan FILE --corpus FILE --cairn-checkout DIRECTORY --output NEW_DIRECTORY` | Retain original native task evidence and apply the selected checkout's real evidence parser; no regrading or replay |
| report-task | `--run DIRECTORY [--trusted-parser-checkout DIRECTORY]` | Verify retained task sources and ledger objects; optionally replay delivery parsing with explicitly trusted, matching parser source |

Specs reject unknown schema versions, duplicate identities, overlapping labels
and unsupported configurations. CLI JSON parsing also rejects duplicate object
keys and nonfinite numeric literals. Invalid input emits a
`caplab-retrieval-cli-error/1` JSON object on stderr, with a code, error type,
message and contract path when available. Unexpected exceptions use
`internal_error` with their exception type and return 2; they never masquerade
as an incomplete report. Reports and validation JSON go to
stdout, so they can be redirected without mixing diagnostics.

Use absolute paths for file arguments in command specs; the example preparation
helper supplies them. Each command runs in an empty temporary directory, so a
relative data or script path from the invoking directory will not resolve there.
The executable is selected once and pinned before execution. Other arguments
remain literal values; the runner does not rewrite them as paths.

Exit statuses:

- **0**: validation/comparison succeeded, or a run/report is finished with every
  assignment successful. This is execution status, not a quality threshold.
- **1**: a report exists but the run has failed, timed-out, interrupted,
  not-started or missing assignments, or has not been finished. Inspect its
  coverage and errors; they remain part of the plan.
- **2**: command arguments, input, filesystem access, artifact integrity or
  comparison compatibility failed, or resource cleanup failed. No fabricated
  successful result is emitted.
- **130**: an interruption escaped the runner. Inspect retained evidence before
  deciding how to continue; the CLI does not automatically rerun work.

A successful `compare` returns 0 even when its source runs contain failures;
inspect its pairing/coverage counts. Comparison validity is separate from run
completeness and quality. `report-task` emits the verified registered document;
verification is conveyed by successful exit status, without adding fields to
the retained evidence schema.

A resource cleanup failure returns `cleanup_failed`, the retained `output`
directory and per-arm `failures` on stderr. The run stays unfinished, without
a final manifest. Its recorded attempts and cleanup diagnostics remain
available through `report --run DIRECTORY`, which returns 1 for that unfinished
run. Do not infer successful cleanup from successful query measurements.

Never reuse an output directory. The runner and artifact store preserve a plan
and attempt evidence across classified failures. `plan.json`, `attempts.jsonl`,
`report.json` and `manifest.json` are conventional inspection paths; raw exact
request/response/stdout/stderr objects and their references belong to the
retained evidence bundle. Use `report` and `compare` to verify a bundle before
reading it as trustworthy. Integrity detects inconsistent byte edits; it does
not authenticate the writer or detect wholesale replacement without an
independently pinned manifest identity.

## Read the result

The report starts with the experiment's configured arms, corpus/query counts,
label provenance and run coverage. It then presents limitations and metrics.
Precision@k uses k as its denominator even for short ranked lists. Answerable
queries receive precision, recall, reciprocal rank and nDCG; empty-gold controls
receive separate false-positive/forbidden-hit rates. Every rate retains its
numerator and denominator. Failed attempts do not become correct abstentions.

Conditional metrics cover scorable attempts. All-assignment bounds describe
uncertainty from unscored assignments; neither zero-imputed nor one-imputed
bounds are observed retrieval quality. Body exposure is measured only when the
adapter actually observed delivery. Seeds repeat queries; paired comparisons
use case/seed identities and case-level uncertainty instead of treating seeds
as independent cases. Changed labels/corpus/query pins fail comparison rather
than being silently aligned.

## A real Cairn run

Use the `cairn` arm to run actual retrieval in newly created disposable stores.
It must use the adapter owner's isolation path, not a hosted-agent profile or
an existing database. PostgreSQL executables and a reviewed Cairn source
checkout are prerequisites. Configure explicit Cairn binary and checkout paths;
record their source/build identities in the resulting evidence. Do not point a
fixture at a production database or copy credentials into a spec.

The adapter requires the executable's embedded VCS revision to match the clean
checkout HEAD, with `vcs_modified: false`. It observes binary/source identities
before provisioning anything. PostgreSQL requires `initdb`, `pg_ctl` and
`createdb`, run as a normal user. `pg_config --bindir` locates them; alternatively
set `CAPLAB_RETRIEVAL_PG_BIN` (or `CAIRN_PG_BIN`) explicitly. The adapter calls
the selected checkout's existing `scripts/trial-task-eval.sh -- COMMAND` mode.
Cairn owns the private `/tmp/cairn-task-eval-pg.*` cluster, Unix socket and
cleanup, with TCP disabled. CAPLAB uses a separate `/tmp/caplab-rtv-*` directory
for its temporary identity, API and logs, seeds only the supplied corpus, and
removes its scratch directory after the arm. Retrieval commands receive no
database credentials or production profile. A checkout predating the wrapper's
`-- COMMAND` mode needs `CAPLAB_RETRIEVAL_LIFECYCLE_WRAPPER` set to a reviewed
wrapper that supports it; its exact bytes and override status are recorded.

Build a reviewed Cairn revision with the supplied helper, which creates a fresh
clone and verifies the executable's embedded revision. Replace the source path
and commit below; use new output paths. This also avoids unstamped binaries
from builds in worktrees with unsupported VCS discovery:

```sh
python3 scripts/retrieval_pin_cairn.py --checkout /absolute/cairn --revision REVIEWED_COMMIT --output /tmp/cairn-retrieval-pin
python3 examples/retrieval/prepare.py --output /tmp/cairn-lexical-spec.json --cairn-binary /tmp/cairn-retrieval-pin/cairn --cairn-checkout /tmp/cairn-retrieval-pin/src
PYTHONPATH=src python3 -m caplab retrieval validate --spec /tmp/cairn-lexical-spec.json
CAPLAB_RETRIEVAL_PG_BIN="$(pg_config --bindir)" PYTHONPATH=src python3 -m caplab retrieval run --spec /tmp/cairn-lexical-spec.json --output /tmp/cairn-lexical-run
PYTHONPATH=src python3 -m caplab retrieval report --run /tmp/cairn-lexical-run --format markdown
```

This executes real Cairn searches over the fresh toy corpus; it does not promise
that Cairn matches the toy fixture's ideal ranking. Notes without `repo` are
seeded into the experiment collection; the `surveyor` sentinel remains foreign.
The adapter records actual search availability/fallback, ranking, latency and
response bytes. Its searches deliver bounded index previews; it performs no
body pull, so full-body exposure stays unobserved.
No model/selector service or live hook deployment is required for lexical
retrieval. A requested semantic mode without a worker may yield labelled
lexical fallback; preserve that observed discovery state rather than calling
it successful semantic retrieval.

## Retain native task evidence

`import-task` is an offline bridge to Cairn's own pinned
`scripts/trial_task_evidence.py` parser. Supply the original report, its matching
plan, frozen corpus and explicit parser checkout. It registers exact source
bytes, original grades and available native streams in a new filesystem ledger.
It does not launch an agent, call a model, rerun an episode or grade a task.
`report-task` resolves verified registered bytes; it does not blindly read a
mutable `evidence.json` copy.
By default it checks retained source consistency and delivery hash bindings;
it does not re-execute the delivery parser. Pass `--trusted-parser-checkout`
to recompute deliveries. Only byte-matching parser code from that explicitly
trusted checkout executes; code stored inside the evidence bundle never does.
Import-environment paths and revision metadata remain reported observations,
and coherent replacement requires an externally pinned evidence digest.
See [the bridge contract](native-task-bridge.md) for the exact detection limits.

For a newly constructed fixture or a currently authorized completed run:

```sh
PYTHONPATH=src python3 -m caplab retrieval import-task --report /absolute/new-run/agent.json --plan /absolute/new-run/plan.json --corpus /absolute/new-run/corpus.json --cairn-checkout /absolute/clean/cairn --output /tmp/native-task-evidence
PYTHONPATH=src python3 -m caplab retrieval report-task --run /tmp/native-task-evidence
PYTHONPATH=src python3 -m caplab retrieval report-task --run /tmp/native-task-evidence --trusted-parser-checkout /absolute/clean/cairn
```

Both task commands return 0 when import or verification succeeds. This is
retention status, regardless of the original task grades. Failures, not-started
assignments, unknown strata and missing streams remain visible in the document.
Missing stream evidence stays unknown; neither a completed import nor a good
retrieval rank implies task completion. Source float values remain unchanged;
no Binding, basis, Measurement or acceptance record is fabricated. Corpus or
plan identity mismatches and evidence tampering return 2. Historical evidence
requires separate authorization; the development tests use only fresh synthetic
inputs and never replay closed cohorts.

The full [retrieval evaluation plan](../plans/cairn-retrieval-evaluation.md)
still requires independent integration, real Cairn evidence and acceptance of
the complete instrument. This CLI slice supplies entry points, not that judgment.
