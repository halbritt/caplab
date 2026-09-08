# Two-coder agreement report

`scripts/code_agreement.py` reads one explicitly named JSON file and prints a
descriptive report. It makes no model calls, discovers no campaign files, and
does not modify its input. Use it to inspect whether two coders apply each
world's frozen binary codes consistently, with incomplete observations visible.
The [decision record](../../records/decision-2026-09-08-code-agreement-diagnostic.md)
selects the prospective single-code failure disposition; this CLI does not
apply a threshold or decide study acceptance.

For an explicitly supplied reference label set, use the optional
[`--reference` comparison](code-reference-report-v1.md). It retains this report
and adds per-coder reference counts and coverage. Reference truth and
independence remain unverified; the original mode and schema are unchanged.

## Input

`caplab-code-agreement-input/1` has exactly five top-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Exactly `caplab-code-agreement-input/1` |
| `coder_ids` | Exactly two distinct non-empty strings, in matrix-axis order |
| `worlds` | Non-empty object mapping world IDs to non-empty lists of distinct code IDs |
| `slots` | Expected assignments, each with exactly `slot` and `world`; slot IDs are globally unique |
| `judgments` | Observed records with exactly `slot`, `coder_id`, `code_id`, and `value` |

Each judgment names a declared coder, expected slot and code belonging to that
slot's world. `value` is a JSON Boolean or `null` for explicitly unavailable.
An omitted record means missing judgment. Duplicate judgments are rejected,
even when identical. Unknown keys, unknown IDs, duplicate slots or code IDs,
numeric values such as 0/1, string Booleans, duplicate JSON object keys, and
non-JSON numeric constants are errors. A world with no assigned slots is
retained with zero expected pairs; it does not silently disappear.

Prepare the expected population from the authorized frozen assignment and
codebook records, not from whichever judgments survived. The CLI validates
internal references only. It does not verify a freeze, native identity,
custody, source evidence, coder independence, blinding, or omitted planned
assignments. Any historical extraction or evidence admission needs its own
authorization. Do not put arm labels, model labels, or reference answers into
a coder-visible input merely to construct this analyst-side report.

## Run a small example

Save this newly constructed example as `judgments.json`:

```json
{
  "schema_version": "caplab-code-agreement-input/1",
  "coder_ids": ["coder-a", "coder-b"],
  "worlds": {"world-1": ["C1"]},
  "slots": [
    {"slot": "s1", "world": "world-1"},
    {"slot": "s2", "world": "world-1"}
  ],
  "judgments": [
    {"slot": "s1", "coder_id": "coder-a", "code_id": "C1", "value": false},
    {"slot": "s1", "coder_id": "coder-b", "code_id": "C1", "value": false},
    {"slot": "s2", "coder_id": "coder-a", "code_id": "C1", "value": true},
    {"slot": "s2", "coder_id": "coder-b", "code_id": "C1", "value": null}
  ]
}
```

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 scripts/code_agreement.py judgments.json
```

The report has two expected pairs, one complete pair and one incomplete pair.
The complete pair agrees, but observed and chance agreement are both 1, so κ
is `null` with reason `chance-agreement-is-one`. Coder B has one explicitly
unavailable judgment. If its second record is omitted instead, that count
moves to `missing_judgments`; the incomplete pair remains visible.

The command exits 0 when it produces a valid diagnostic, including one with
missing judgments or undefined κ. That exit code is not a reliability pass.
Malformed input exits 2 with an error on stderr and no report on stdout.

## Read the result

The output schema is `caplab-code-agreement-report/1`. It includes coder IDs,
the expected slot count, the SHA-256 of the original input bytes, and one
`codes` row for each `(world, code_id)`. Rows contain:

- `expected_pairs`, `complete_pairs`, and `incomplete_pairs`;
- `missing_judgments` and `unavailable_judgments` separately for each coder;
- `joint_counts`: `00`, `01`, `10`, `11`, where the first digit belongs to
  the first `coder_ids` entry and 0/1 denote false/true;
- `observed_agreement`, `chance_agreement`, `kappa`, and
  `kappa_unavailable_reason`.

Only complete pairs enter the joint table. Per-coder missingness counts may
overlap on the same pair, so their sum is not the incomplete-pair count.
There is no aggregate κ across codes or worlds. Input record order does not
change the result; swapping coder order transposes the joint table and leaves
κ unchanged. The input hash attests bytes, not admission or provenance.

For N complete pairs, observed agreement is `(n00 + n11) / N`. Chance
agreement uses each coder's own marginal label frequencies; κ is
`(observed - chance) / (1 - chance)`, the unweighted definition documented by
[scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html).
CAPLAB implements the binary arithmetic directly and adds no dependency.
No complete pairs yields null statistics with reason `no-complete-pairs`;
chance agreement of one yields undefined κ. Undefined values are never
replaced with 1 or 0.

The values describe agreement on the complete pairs. Incomplete observations
can change which conduct is represented, and a high point estimate with few
pairs does not establish precise or representative reliability. This version
does not estimate uncertainty intervals. It does not establish accuracy:
two coders that always make the same wrong judgment can agree perfectly.

For a future study, freeze the roster, accuracy evidence, per-code thresholds,
missingness limits, sample plan and analysis before unblinding. Apply the
[code-authoring procedure](behavior-code-authoring-v1.md) and its separate
blinding and accuracy requirements. A required code failing its frozen gate,
or an undefined required statistic, stops interpretation; do not drop the code
after inspecting outcomes. CAPLAB-65 remains open for roster and accuracy-anchor
decisions, and CAPLAB-71 retains numerical parameter ownership.
