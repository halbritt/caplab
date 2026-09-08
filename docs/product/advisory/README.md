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

Prospective pool runs marked `anchor_matching: normalized-anchor-exact/1`
report `exact_anchor_mention` instead of `anchored_detection`. The new metric
requires whole-anchor equality after the existing normalization of wrappers
and letter case. It does not credit substrings, ancestors, or longer element
names. The runner retains every emitted anchor from the representative
mutant response, so scoring can reproduce the same comparison. Runs with
different anchor contracts cannot resume into one another, and the scorer
refuses unknown or inconsistent contract markers.

Historical runs retain their frozen substring rule and separate denominator.
When a backend has both kinds of run, both metrics appear independently;
their numerators and denominators are never pooled. A location mention can
occur with any verdict and says nothing about the correctness of the
finding's explanation. Listing every real anchor can still satisfy this
metric. It must not serve as a semantic finding-quality score.

The prospective pair gate, `paired-presence/1`, requires explicit opposing
mechanical checker results before any pool or calibration attempt. It refuses
unknown results and the unsupported schema-word inference in
`unearned_verification_claim`. This can reduce executable coverage; affected
pool cells remain incomplete rather than becoming reviewer misses. See the
[gate report guide](review-gate-report.md) for the consequences and the
[oracle counterexample](../../records/repair-2026-09-08-pair-oracle.md).

New pool runs write `run-spec.json` before any attempt. It freezes the ordered
plan, declared backend configuration hash, measurement parameters, environment,
base-registry hash, Python version, and advisory-package source hashes. Rows
and summaries name its SHA-256. Resumption requires the same specification;
changed code, inputs, or parameters require a new output directory. The scorer
checks the retained specification and row/summary references before using new
results. Historical runs without this record retain their existing scoring
path but cannot be resumed by the new runner.

This specification records configuration and source provenance. It does not
verify a native Binding, pin external executable or account-state changes,
provide one-shot attempt custody, or establish comparability between two
runs. Those require the corresponding evidence and policy separately.

Prospective paired comparisons now verify the common fields of both frozen
run specifications before producing a contrast. They allow backend labels,
declaration hashes, and declared lane limits to differ as subject properties;
all other recorded conditions must match. Every planned result must be
present exactly once, summaries must reconcile with retained rows, and both
runs must have the same measurable population. Different case metadata,
preparation failures, missing rows, or a mixture of frozen and historical
runs refuse comparison.

The resulting `comparison_basis` names common-condition and source-result
hashes, subject declarations, and planned, paired, inapplicable, and anchor
counts. Targeted reproduction and admission-gate contrasts retain descriptive
counts but expose no discovery p-values or significance flags. These checks
establish agreement of the recorded conditions, not native Binding identity,
semantic finding validity, statistical independence, or reviewer ranking.
Historical unversioned comparisons retain their numerical calculations but
are explicitly labeled `unverified-historical`; a case-ID intersection does
not establish common experiment conditions.

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
