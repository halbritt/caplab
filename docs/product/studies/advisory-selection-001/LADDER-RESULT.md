# Advisory-selection ladder result

Completed 2026-07-31. This record interprets the ladder frozen in
[`LADDER-PROTOCOL.md`](LADDER-PROTOCOL.md), including its six amendments.

## Result

No tuple showed a measurable pooled injection effect. The largest observed
contrast was `gpt-5.6-sol/high` at `+0.171`; the frozen detection threshold was
`+0.350`. The empirical minimum detectable effect (MDE) was below the frozen
threshold at every tuple, so the operative bar remained `+0.350`.

The claim is narrow:

> No injection effect was detectable at the frozen threshold under ideal
> static delivery.

This is not evidence of no effect. The protocol cannot detect effects below its
operative bar. The injected packets were hand-built and verified static
stimuli; no deployed CAPLAB path produces them.

All seven scenarios survived the ceiling gate at every tuple. The completed
surface therefore has no detectable boundary below the top of the tested
ladder.

| native subject tuple | none mean | pooled delta | empirical MDE | operative bar | measurable |
|---|---:|---:|---:|---:|---|
| `gpt-5.6-luna/low` | 0.267 | +0.086 | 0.046 | 0.350 | no |
| `gpt-5.6-luna/medium` | 0.362 | -0.029 | 0.060 | 0.350 | no |
| `gpt-5.6-luna/high` | 0.343 | +0.152 | 0.107 | 0.350 | no |
| `gpt-5.6-luna/xhigh` | 0.333 | +0.067 | 0.073 | 0.350 | no |
| `gpt-5.6-terra/low` | 0.371 | +0.029 | 0.096 | 0.350 | no |
| `gpt-5.6-terra/medium` | 0.362 | +0.019 | 0.057 | 0.350 | no |
| `gpt-5.6-terra/high` | 0.286 | +0.162 | 0.119 | 0.350 | no |
| `gpt-5.6-terra/xhigh` | 0.362 | +0.019 | 0.050 | 0.350 | no |
| `gpt-5.6-sol/low` | 0.371 | +0.019 | 0.075 | 0.350 | no |
| `gpt-5.6-sol/medium` | 0.400 | +0.086 | 0.098 | 0.350 | no |
| `gpt-5.6-sol/high` | 0.419 | +0.171 | 0.042 | 0.350 | no |
| `gpt-5.6-sol/xhigh` | 0.410 | +0.133 | 0.065 | 0.350 | no |

The end-of-study unaided ordering, from lowest to highest measured none-arm
mean, is:

1. `luna/low`
2. `terra/high`
3. `luna/xhigh`
4. `luna/high`
5. `luna/medium`
6. `terra/medium`
7. `terra/xhigh`
8. `sol/low`
9. `terra/low`
10. `sol/medium`
11. `sol/xhigh`
12. `sol/high`

This is an observed ordering, not a monotonic capability scale.

## Evidence accounting

The campaign holds 591 append-only subject episodes:

| disposition | count | analysis treatment |
|---|---:|---|
| behavioral attempt | 569 | one accepted `gpt-5.6-terra/high` judgment |
| behavioral non-attempt | 19 | mechanical primary score of zero |
| infrastructure | 3 | excluded; successful replacement retained separately |

Every episode has a successful native tuple attestation. Sixty episodes record
`codex-cli 0.145.0`; 531 record `codex-cli 0.146.0`.

Adaptive replication was recomputed from the replacement judgments. Exact
agreement between the first two complete code vectors gives `k=2`; disagreement
extends the cell to `k=5`. `C1` through `C3` form the score. `SCOPE` participates
in exact-vector agreement but not the score. Sample variance within each
realized arm supplies the pooled standard error and empirical MDE. Infrastructure
episodes do not participate in trial order; their successful replacement does.

## Replacement rater decision

The frozen 42-artifact calibration did not produce a passing high-effort
candidate:

| native rater tuple | overall primary | positive | negative | lowest scenario | frozen result |
|---|---:|---:|---:|---:|---|
| `gpt-5.6-luna/high` | 92.1% | 82.1% | 100% | 77.8% | fail |
| `gpt-5.6-sol/high` | 92.9% | 83.9% | 100% | 77.8% | fail |
| `gpt-5.6-terra/high` | 92.9% | 83.9% | 100% | 83.3% | fail |

All three candidates had 100% `SCOPE` agreement. Terra/high passed the overall,
negative, and per-scenario gates but missed the positive gate by one decision:
47 of 56 agreements rather than the required 48.

The repository owner authorized a judgment call if Terra/high reproduced the
same narrow result, then authorized rerating the stack. Terra/high was therefore
accepted as a post-data instrument decision and rated every eligible artifact.
It is not represented as a successful frozen calibration. The unrun xhigh
candidates were not needed for that owner-authorized decision.

This decision has two material limitations:

- the accepted rater missed a frozen continuity gate; and
- the replacement rater belongs to the same model family as the subjects.

## Custody

Raw custody is under
`~/.local/share/caplab/campaigns/advisory-selection-001-ladder-2026-07-29/`.
The governing evidence hashes are:

| artifact, relative to `rater-recovery/` | SHA-256 |
|---|---|
| `calibration-manifest.json` | `d0567b2a8ff98a7ccfc3a5ff0594a56855fe1826c8d27b65a12012dbe15dee4b` |
| `candidates/luna-high/calibration-result.json` | `7bee897275f61454b34ef22b959d214da8c6f96d724f11ab8bdec0d5858e29ea` |
| `candidates/sol-high/calibration-result.json` | `4950b84aca04cceb65069ddcad3289fca95842fb282f45496065f5bfa82b9234` |
| `candidates/terra-high/calibration-result.json` | `d417cf001750c13dee7b3483c73bcfb5a5b402ad9c1c6807a965e22540665b16` |
| `full-scoring-manifest.json` | `75007bea7c92bd63e32b2b4dbdd86e294f997ea9c3cb515a2f1bd94191fbed68` |
| `continuation-round-1-plan.json` | `7796dce42e83d9ca1ba712a030a7ecbfbd0324b0e75ebdd0a5f804b93506a8d6` |
| `continuation-round-1-scoring-manifest.json` | `8da82bf6bdcc75cba927515f2087cebccc31a999447ad1f30e4e5273e76704ee` |
| `continuation-round-2-plan.json` | `5c6dd7a89ef9dcda025d0a6cd6e6bfe05041a512e80b44ea455723458894bea1` |
| `continuation-round-2-scoring-manifest.json` | `c27dc4e5f0bf8184c21c371902bbe577723452fa6b40fc066f0d78f0b5685b00` |
| `final-analysis.json` | `7cf28400cd19e5e4c918494eb8b1b26e26c87230679bcc4eeba4372f0adf18c2` |

Recompute the result without replacing existing evidence:

```bash
campaign_root=/home/halbritt/.local/share/caplab/campaigns/advisory-selection-001-ladder-2026-07-29
scripts/caplab-ladder-analyze.py \
  --campaign-root "$campaign_root" \
  --score-root "$campaign_root/rater-recovery/full-terra-high/scores" \
  --score-root "$campaign_root/rater-recovery/continuation-round-1-terra-high/scores" \
  --score-root "$campaign_root/rater-recovery/continuation-round-2-terra-high/scores" \
  --output "$campaign_root/rater-recovery/final-analysis.json"
```

The analyzer refuses incomplete custody, unattested subject episodes, duplicate
or missing judgments, a rater tuple other than Terra/high, or an attempt to
replace different analysis bytes.

## Authority and doctrine receipt

The doctrine packet was
`pkt-739af28cc6df99ef` with content SHA-256
`739af28cc6df99efd27771895361132f7fe85613587dbbc740d799c7abff57bf`,
corpus `corpus-2026-07-12-a11702cc9217`, and doctrine
`doctrine-f6bbb5196a3f8bf9`. The citation classifier recorded these five used
concepts as valid packet citations:

- `agent-conduct-authority-bounded-action`
- `universal-repository-contract-precedence`
- `universal-evidence-before-intervention`
- `architecture-decision-record`
- `refactoring-stop-backtrack-escalate`

Doctrine supported evidence-first execution and the separation of authority
stages. It did not authorize the rater exception. The repository owner's
messages supplied that authority.

This record contains observations, the protocol-defined inference, and the
owner-authorized rater decision. It does not infer repository-owner acceptance
of the final study claim.
