# Coder comparison with supplied reference labels

Status: implemented descriptive diagnostic. This is not an accuracy gate or a
validated human anchor. Decision and verification:
[implementation receipt](../../records/implementation-2026-09-08-code-reference-comparison.md).

The existing [two-coder agreement report](code-agreement-report-v1.md) answers
whether coders agree. The optional reference comparison answers whether each
coder agrees with a separately supplied label set. It cannot establish that
those labels are correct, independent, human-authored or representative.

## Inputs and command

The original `caplab-code-agreement-input/1` supplies the two coders, worlds,
codebooks, expected slots and judgments. No arm labels or model identities are
needed. For an accuracy-anchor diagnostic, declare the intended anchor slots
before labels are inspected; do not derive this population from surviving
reference or coder records. If a whole-study input has only a sparse reference
set, unreferenced study slots remain visibly missing. The tool does not infer
which missing references were planned or silently narrow the anchor population.

The reference file is an analyst-side `caplab-code-reference-input/1` object
with exactly `schema_version`, `reference_id`, and `judgments`. Each judgment
has exactly `slot`, `code_id`, `value`, and `evidence_locator`. For example:

```json
{
  "schema_version": "caplab-code-reference-input/1",
  "reference_id": "synthetic-reference-example",
  "judgments": [
    {"slot": "s1", "code_id": "C1", "value": true,
     "evidence_locator": "synthetic://example/s1/C1"},
    {"slot": "s2", "code_id": "C1", "value": false,
     "evidence_locator": "synthetic://example/s2/C1"}
  ]
}
```

These are constructed labels, not human judgments or admitted evidence.
`reference_id` identifies the supplied set, not a verified judge. A nonempty
`evidence_locator` is required for each record, including unresolved records;
its target is not opened or verified. Preserve exact source/custody and author
provenance separately before any accuracy claim. Never show reference answers
to a coder merely to prepare this analyst input.

`value` is Boolean or `null` for explicitly unresolved. Missing records remain
missing. Duplicate `(slot, code_id)` references are errors even when identical.
Unknown slots/codes, extra keys, absent/empty locators, numeric 0/1, string
Booleans and invalid schemas are rejected. Slot identity determines the world,
so equal code names in different worlds do not merge. Neither input is mutated.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 scripts/code_agreement.py judgments.json --reference references.json
```

Without `--reference`, the original version 1 agreement report is unchanged.
With it, the output is `caplab-code-reference-report/1`, containing the original
report under `agreement`, the supplied `reference_id`, and one
`reference_comparisons` row per world/code/coder. The CLI records SHA-256 of
both original input files as `input_sha256` and `reference_sha256`. These hashes
identify supplied bytes; they do not register or authenticate the evidence.
Explicit JSON `null` as the reference document is an error, not omission of
reference mode. Both files use the existing strict UTF-8 JSON decoder; duplicate
keys and non-JSON numeric constants are rejected. Failure exits 2 without a
report; successful diagnostic output exits 0 even when all rates are undefined.

## Counts and denominators

Each comparison row keeps `expected_labels`, `missing_reference_labels`,
`unavailable_reference_labels`, `known_reference_labels`,
`positive_reference_labels`, and `negative_reference_labels`. Known means a
supplied Boolean label; it does not mean independently established truth.

Within known references, the row counts `compared_labels`,
`missing_judgments_on_known_references`, and
`unavailable_judgments_on_known_references`. These sum to the known-reference
count. Missing coder judgments outside known references remain visible in the
embedded agreement report; they are not comparable against an unknown answer.

`reference_joint_counts` uses the declared axes `reference`, then `coder`:

| Key | Supplied reference | Coder judgment |
|---|---|---|
| `00` | false | false |
| `01` | false | true |
| `10` | true | false |
| `11` | true | true |

This follows the reference-row/prediction-column orientation of the
[standard confusion matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html).
CAPLAB deliberately calls these reference-label counts because the diagnostic
does not establish ground truth. No scikit-learn dependency is added.

Rates are descriptive and use explicit comparable-label denominators:

| Field | Calculation |
|---|---|
| `reference_coverage` | compared labels / known reference labels |
| `reference_agreement` | (`00` + `11`) / compared labels |
| `positive_reference_agreement` | `11` / (`10` + `11`) |
| `negative_reference_agreement` | `00` / (`00` + `01`) |

Any zero denominator yields JSON `null`. In particular, a known positive
reference with no coder judgment does not create a successful positive result.
Its positive-reference count remains visible even when the positive rate is
undefined. Complete-case agreement can be high despite poor coverage; inspect
both classes and the missingness counts. No rates are pooled across worlds,
codes or coders, and no uncertainty interval or acceptance threshold is supplied.

## Interpretation and next requirement

Consider reference labels `[false, true, false, true]` with both coders returning
`[true, false, true, false]`. Their κ is 1, while each coder's reference agreement
is 0. The distinction is expected: κ measures agreement between annotators,
not their agreement with independently established answers.
[Definition of Cohen's κ](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html)

The tool implements arithmetic, not the independent anchor. CAPLAB-65 still
needs its roster and qualified reference evidence; the human-time source remains
a Principal-owned choice. A reference made by coder consensus or the same
fallible model is not independent merely because it is in a separate file.
CAPLAB-71 still owns thresholds, uncertainty, sample size and missingness limits.
No frozen study, campaign, real coder qualification, reviewer ranking or
placement decision changes through this diagnostic.
