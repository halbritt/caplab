# Claim-to-source entailment screening summary

Generated deterministically from `results.jsonl` by
`doctrine/tools/entailment_eval.py --summarize`. Do not edit by hand.

Each verdict is an observation of model output supporting an inference
about entailment. It is screening evidence, not verification and not
acceptance; it does not modify doctrine.

Records: 12 unique judgment keys (12 result lines).

## Verdict counts

| verdict | count |
|---|---|
| supported | 11 |
| not_supported | 1 |

## Verdicts by source

| source | supported | partially_supported | not_supported | contradicted | resolution_failed | unparseable | transport_error | total |
|---|---|---|---|---|---|---|---|---|
| SRC-APOSD | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 4 |
| SRC-EGO | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| SRC-WELC | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |

## Flagged entries (not_supported, contradicted, unparseable)

- `not_supported` — concept `implementation-explicit-failure-policy` — `books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217/chapters/015-10-define-errors-out-of-existence.md :: 10: Define Errors Out Of Existence`

## Locator-resolution failures

None.

## Latency

Mean latency over 12 model-judged records: 10.55s.
