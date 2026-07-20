---
id: caplab-review-dissent-local-qwen-r1
artifact_type: dataset-card
title: CAPLAB local-Qwen review-dissent contrastive corpus r1
status: authorized-internal-training-export
created: 2026-07-20
decision_record: adr-0048
---

# CAPLAB local-Qwen review-dissent contrastive corpus r1

## Contents and intended use

This internal corpus contains seven mechanically valid one-shot review records
from the native Striatum tuple
`local-qwen-35b-a3b-striatum-openai-lane-v1`. It supports one bounded tuning
experiment on evidence-grounded defect detection and clean-case false-refusal
control. It is not a general coding, ranking, safety, or placement dataset.

The canonical export is [`corpus.json`](corpus.json), semantic SHA-256
`303a55e6594528ab520d9fbc92d306cd942d4d6a76c68ef314797aa0c84cf1e5`
and file SHA-256
`09ec666630189ebbe9bf180d3dd567623f8dbee753871f63ac7f66c712cb87f2`.

## Inclusion and reward semantics

The corpus includes all seven schema-valid local-Qwen development responses.
Six score `1.0` under the frozen mechanical review oracle and supply chosen
SFT-style records. One clean response scores `0.2` because it invents critical
findings; that record pairs the deterministic reference review as chosen with
the observed false-positive review as rejected.

Reward is relative only: chosen is preferred to rejected. The export does not
assert an absolute reward, human preference, or broad capability disposition.
The mechanical oracle supplies the label, so `human_disposition` is explicitly
`not-required-mechanical-oracle` rather than fabricated.

## Split policy

Splits are by task family, never trajectory:

| Split | Families | Exported rows |
|---|---|---:|
| train | `RD-D01` migration review | 3 |
| development | `RD-D02` publication review | 4 |
| test | `RD-H01`, `RD-H02` | 0; identities sealed, content unopened |

The held-out family bytes are not in this export. CAPLAB-16 must keep them
unopened until the training checkpoint and base comparison are frozen.

## Exclusions

- `r01` is excluded because the local response truncated inside a JSON string;
  it remains a subject-invalid raw observation and was not retried.
- All CAPLAB-8 Claude and OpenAI responses are excluded by ADR 0048's current
  terms boundary.
- All CAPLAB-13 proprietary responses are excluded because they failed the
  frozen schema and are independently barred from this competing-model corpus.
- Study 001 remains `no-example-eligible` under ADR 0024.
- No provider, harness, capture, verifier, or incomplete-lineage row is
  eligible.

## License, privacy, and secrets

The exact local quant's [Hugging Face model card](https://huggingface.co/mudler/Qwen3.6-35B-A3B-APEX-GGUF)
identifies Apache-2.0 and the I-Compact file used by the campaign. CAPLAB owns
the synthetic task contract and deterministic reference-review use for this
private product purpose. The corpus is internal-only; redistribution is not
authorized by this card.

The terms review also checked the current official
[Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms) and
[OpenAI Terms of Use](https://openai.com/policies/row-terms-of-use/). Those
sources assign output interests while prohibiting competing-model development,
so proprietary outputs were excluded rather than relicensed.

Inputs describe synthetic repositories and contain no real person. A literal
scan of all raw local responses and the export found no credential, token,
email address, home path, or non-synthetic personal datum. Raw custody remains
private beneath the ADR 0047 path through the CAPLAB-17 disposition.

## Known biases and limitations

The corpus has only two development families, seven valid rows, one model
tuple, one harness, and one contrastive negative. The deterministic references
are concise oracle constructions rather than human-written ideal reviews.
Several otherwise perfect model reviews include noncritical claims outside the
primary oracle; the score does not validate those claims semantically.

No training, checkpoint quality, transfer, held-out performance, general
competence, latency, cost improvement, or Striatum fitness follows from this
export. Those remain separate preregistration, execution, verification, and
decision steps.
