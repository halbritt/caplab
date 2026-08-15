# Advisory scored claims

The advisory track created by
[`plan-advisory-selection-001`](../plans/plan-advisory-selection-001.md).
It measures review-family constructs and emits **scored advisory claims**
for the quartermaster registry (`halbritt/quartermaster`). Code:
`src/caplab/advisory/`; ledger: `advisory/claims.jsonl`; export:
`advisory/caplab-advisory-export.json` (`caplab-advisory-export/1`).

## Boundary

Everything in this track is advisory. It deliberately does not touch
`caplab.qualification`: no Measurement, no qualification Claim, no
qualified/unqualified decision, a separate export document kind. Custody
provenance is explicit per claim and closed:

- `historical-seed` — the striatum-tuner 2026-08-07..09 fleet sweep,
  admitted so the initial ranking is not empty. Executed before CAPLAB
  directed runs; consumers weight it down or out via their objectives.
- `caplab-advisory` — CAPLAB-directed advisory-grade executions.

## Construct

`review.defect_discrimination/1` — matched-pair defect injection. A
mechanically verified defect is planted in a known-sound control at a known
element; both arms run blinded through the subject's declared adapter
command. Metrics: `catch_rate`, `false_alarm_rate`, `discrimination`
(catch − false-alarm; zero for any constant reviewer), `anchored_detection`
(rescored from retained arms on the corrected anchor path, with the
rescoreable-arm denominator recorded), `n_pairs`, `n_distinct_cases`,
`findings_per_mutant`, `json_valid_mutant`. Wilson 95% intervals accompany
the rates.

## Advisory-grade execution profile v0

`python3 -m caplab.advisory run` executes the pinned striatum-tuner
instrument (`revbench.py`) as a subprocess under CAPLAB direction: CAPLAB
chooses subject, pair target, seed, and output root; records the instrument
commit and argv in `caplab-receipt.json`; requires the completed-run marker
(`summary.json`) before any claim derives; and scores captures with
`caplab.advisory.scoring` — the same scorer the seed path uses, so custody
never silently changes semantics.

Stated limits: no sealed custody domain or one-shot launch guarantee, no
provider-authenticated identity, no credential quarantine. The `--max-pairs`
bound is a hard refusal encoding the authorized budget for the campaign.
This profile can never feed the qualification ledger; upgrading evidence to
qualification grade requires the sealed path and its own authorization.

## Known limits of the current corpus

The shared case pool is small (34 distinct injections across the historical
sweep; per-class n of 1–4 per binding) and document-review-only. Treat fine
rank distinctions as noise; the Tier 3 corpus-expansion work
(substrate harvest, new operators, sealed/open governance, per-sweep
sampling) addresses this. New cases are validated against reference
bindings before they may score anyone: a case that known-strong bindings
systematically miss questions the case, not the binding.
