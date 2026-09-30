# Retrieval evaluation: contracts and metrics

Owner: agent-235, 2026-09-30, for plan `docs/plans/cairn-retrieval-evaluation.md`
(3da9f33). Code: `src/caplab/retrieval/contracts.py` and `metrics.py`. Both are
pure: no filesystem, network or clock access. This document is an interface
contract for the runner, artifacts and CLI owners. It makes no retrieval-quality
claim, sets no threshold and grants no qualification.

## Errors

Every rejection raises `ContractError(code, path, message)`. `path` is
JSON-pointer-like (`/queries/3/relevant_ids/0`; attempts in `summarize` are
prefixed `/attempts/N`). Codes:

| Code | Meaning |
|---|---|
| `TYPE` | Wrong type |
| `MISSING_FIELD` / `UNKNOWN_FIELD` | A required field is absent / a field is not in the contract |
| `EMPTY` | An empty list where one is required |
| `TOO_LARGE` | A size bound is exceeded |
| `TOO_DEEP` | Nesting is too deep |
| `OUT_OF_RANGE` | A number is outside its bounds |
| `NOT_FINITE` | NaN or Infinity |
| `INVALID_ID` | Not a slug |
| `DUPLICATE_ID` | An identity repeats |
| `UNKNOWN_ID` | An ID is not in the spec or corpus |
| `INVALID_VALUE` | Not an allowed enum value |
| `UNKNOWN_SCHEMA` | Unsupported `schema_version` |
| `INCONSISTENT_LABELS` | Relevant and forbidden overlap, or answerable without relevant |
| `INCONSISTENT_ASSIGNMENT` | `assignment_id` does not match arm, query and seed |
| `INCONSISTENT_STATUS` | A failed attempt carries results, or an ok attempt carries an error |
| `INVALID_TEXT` | Unpaired surrogates |

## `validate_spec(document) -> dict`

Input: `caplab-retrieval-spec/1` as in the plan. The normalized output has
exactly these keys:

```text
schema_version  "caplab-retrieval-spec/1"
experiment_id   slug
corpus          [{id, body, kind="note", shareable=true, repo?, supersede_with?}]
queries         [{id, text, relevant_ids, forbidden_ids=[], stratum="answerable"}]
arms            [{id, adapter: "command"|"cairn", configuration}]
                  command: {argv: [nonempty str, ...]}
                  cairn:   {binary, checkout, semantic_worker?, semantic_mode: "off"|"on"}
                           (semantic_mode "on" requires semantic_worker)
cutoffs         sorted distinct ints in 1..1000 (at most 16)
seeds           sorted distinct ints in 0..2^31-1 (at most 100)
timeout_seconds int in 1..86400
```

Rules:
- **Identifiers.** Experiment, note, query and arm IDs are slugs: 1–128 of
  `[A-Za-z0-9._-]`, starting alphanumeric. `:` is reserved as the assignment
  separator.
- **Types.** Booleans and floats are never accepted as integers. Unknown fields
  are rejected at every level.
- **Labels.** Labels must resolve to corpus notes. `relevant_ids` and
  `forbidden_ids` are each unique and disjoint. `supersede_with` names a
  different existing note.
- **Answerability.** A query is answerable if and only if `relevant_ids` is
  nonempty. Stratum `answerable` with empty gold is rejected. An empty-gold
  control must name its stratum (for example `no_answer`, `forbidden_control`,
  `superseded`, `wrong_project`).
- **Bounds.** Corpus ≤ 100,000 notes, bodies ≤ 1 MiB, query text ≤ 64 KiB,
  queries ≤ 10,000, arms ≤ 32.
- **Normalization.** It only fills defaults and sorts cutoffs and seeds. It is
  idempotent and does not mutate its input.

Helpers:
- `assignments(spec)` returns the full roster, in arm, query, seed order:
  `{assignment_id, arm, query_id, seed}`.
- `assignment_id(arm, q, seed)` is `"{arm}:{q}:{seed}"`.
- `canonical_json(value)` gives sorted-key, compact UTF-8 bytes with no NaN.
- `spec_digest(spec)` is `"sha256:" + hex(sha256(canonical_json(spec)))`. Seal
  the normalized spec with it before launching retrieval.

## `validate_attempt(attempt, spec) -> dict`

Fields:
- **Required:** `assignment_id`, `arm`, `query_id`, `seed`, `status`,
  `ranked_ids`, `latency_ns`.
- **Optional:** `delivered_ids` (default None), `error` (default None),
  `observation` (default `{}`). Nothing else is accepted.

Rules:
- **Identity.** Arm, query and seed must be in the spec, and `assignment_id`
  must equal `assignment_id(arm, query_id, seed)`.
- **Status.** One of `ok`, `error`, `timeout`, `interrupted`, `not_started`.
- **Ranked IDs.** Unique corpus IDs in rank order, at most 10,000. An empty
  list is a legal ok result: a successful abstention.
- **Delivered IDs.** `None` means delivery was not observed; the harness never
  fills it from rank. A list means observed delivered IDs: unique corpus IDs,
  not necessarily a subset of `ranked_ids`.
- **Latency.** An integer in 0..10^15 ns; `None` is allowed only for
  `not_started`.
- **Ok attempts.** `error` must be None.
- **Other statuses.** `ranked_ids` must be empty and `delivered_ids` None or
  empty. `error`, `timeout` and `interrupted` require `error` to be an object
  with a nonempty `code`. For `not_started`, `error` is optional.
- **Free-form fields.** `error` and `observation` must be JSON objects with
  finite numbers and nesting of at most 32 levels. Observation content (adapter
  provenance, availability or fallback, context bytes) belongs to the adapter
  owner.
- **Gold labels never appear in attempts.** An extra field such as `gold` is
  rejected.

## `score_attempt(query, attempt, cutoffs) -> dict`

Takes normalized objects. A non-ok attempt returns `scorable: false`, an empty
`cutoffs` and `failure` (its error code, or None for `not_started`).

For an ok attempt, each cutoff k (as a string key) is scored over
`top = ranked_ids[:k]`:

| Field | Definition |
|---|---|
| `returned` | len(top) |
| `forbidden_hits`, `forbidden_hit` | count / any of top in forbidden_ids |
| `precision` | Rate(hits, **k**): k is the denominator even if fewer than k were returned |
| `recall` | Rate(hits, len(relevant_ids)) |
| `success` | hits > 0 |
| `reciprocal_rank` | Rate(1, rank of first relevant) if within k, else Rate(0, 1) |
| `ndcg` | Binary gains. DCG = Σ 1/log2(i+2) over relevant positions in top; IDCG uses min(len(relevant), k) ideal positions. Float. |
| `false_positive` | Empty-gold controls only, **instead of** precision and recall: len(top) > 0 |

`exposure` is None unless `delivered_ids` was observed. When observed:
- `delivered` and `forbidden_delivered` are counts.
- `recall` is Rate(|delivered ∩ relevant|, |relevant|), for answerable queries.
- `false_positive` means anything was delivered, for controls.

Exposure is not cut off at k: it is what was actually delivered.

## `summarize(spec, attempts) -> dict`

Every attempt is validated. A duplicate `assignment_id` raises `DUPLICATE_ID`.
Arms are never pooled. The output is `caplab-retrieval-summary/1`:

```text
{schema_version, experiment_id, cutoffs, seeds, seeds_are_repetitions,
 arms: {ARM: {
   coverage: {planned, attempted, scorable, failures, not_started, missing,
              by_status{ok,error,timeout,interrupted,not_started,missing}, scorable_rate},
   planned_by_kind: {answerable, controls, with_forbidden},
   strata: {STRATUM: {planned, scorable}},
   cutoffs: {"k": {
     answerable: {
       conditional:     {precision, recall, mrr (Mean), ndcg (FloatMean), success (Rate over ok)},
       all_assignments: {recall (Mean, non-ok counted as 0), success (Rate over planned)},
       case_level:      {recall (Mean of per-query seed means), queries_scored (Rate)}},
     controls:  {false_positive_rate (Rate over ok controls),
                 clean_all_assignments (Rate: ok and not FP, over planned controls)},
     forbidden: {hit_rate (Rate over ok attempts with forbidden labels),
                 clean_all_assignments (Rate: ok and no hit, over planned with forbidden)}}},
   exposure: {observed (Rate over ok), recall (Mean), forbidden_delivered (Rate),
              control_false_positive (Rate)},
   latency_ok: {count, median_ns, p95_ns, max_ns}   (nearest rank, ok attempts only),
   attempts: [score_attempt output for every roster entry that has an attempt]}}}
```

Value shapes:
- **Rate** is `{numerator, denominator, value}`. **Mean** is
  `{numerator, denominator, value, count}`, an exact reduced Fraction of the
  mean. **FloatMean** is `{value, count}`.
- `value` is a display float and is None when the denominator or count is 0,
  meaning undefined, never 0.
- Identity and comparisons must use the exact integer fields, never `value`.
  nDCG is irrational, so it is float only and not for identity.

## Guarantees

- A failed, timed-out, interrupted, not-started or missing assignment is never
  a successful abstention. It is excluded from conditional metrics, and it
  lowers every all-assignment measure: success, recall, clean controls and
  clean forbidden controls.
- Empty-gold controls cannot raise answerable quality. They have their own
  rates, and an empty retriever scores 0 all-assignment success.
- Conditional metrics must be reported alongside `coverage` and the
  all-assignment measures, never alone.
- Seeds are repetitions of one case (`seeds_are_repetitions`). `case_level`
  averages seeds within a query first.

Not provided: paired comparison, confidence intervals and discordant pairs
belong to `compare.py`. Stratum-level metric breakdowns beyond counts, and the
task-evaluator bridge, are later slices.
