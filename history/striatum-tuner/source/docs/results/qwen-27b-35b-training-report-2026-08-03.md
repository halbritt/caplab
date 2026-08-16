# Qwen3.6 27B and 35B training report

- Date: 2026-08-03
- Project: Striatum reviewer fine-tuning
- Status: Both production training campaigns completed; the 35B artifact is also deployed locally

## Executive summary

Two Qwen3.6 reviewer models were fine-tuned with QLoRA on the same 1,268-example Striatum supervised corpus:

- `Qwen/Qwen3.6-27B` completed 318 optimizer steps on an H100. Its final adapter and converted LoRA GGUF are stored locally. A separate 98-example generation evaluation completed without inference errors.
- `Qwen/Qwen3.6-35B-A3B` completed 318 optimizer steps on an H200 after a three-gate smoke-test ladder exposed and repaired dense-path, Hopper-kernel, and MoE-specific defects. Its final adapter, converted GGUF, checkpoint, evaluation evidence, and recovery manifest are retained. The adapter is deployed behind the local `qwen3.6-ft` Striatum alias.

The campaigns were successful, but neither was a clean first attempt. The 27B campaign spent substantial time discovering dependency and memory constraints directly on paid hardware. The 35B campaign began the same way, then introduced a local-to-Hopper-to-real-MoE smoke ladder and staged checkpoints. That change reduced the cost of finding ordinary pipeline failures and made the final recovery reproducible.

The 27B training pod settled at **$35.3405**. Including the observed generation-evaluation balance delta gives **$35.7727** of known campaign spend. The conservative all-in estimate for the 35B campaign is **at most $43.47**, within the $100 campaign budget. These totals are not a normalized cost comparison: the 35B figure includes more preflight, smoke-test, recovery, and acceptance work.

## Outcome matrix

| Property | Qwen3.6-27B | Qwen3.6-35B-A3B |
|---|---:|---:|
| Base revision | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | `995ad96eacd98c81ed38be0c5b274b04031597b0` |
| Architecture | Dense | MoE, about 3B active parameters |
| Training GPU | H100 80 GB | H200 |
| Training examples | 1,268 | 1,268 |
| Epochs / optimizer steps | 2 / 318 | 2 / 318 |
| QLoRA trainable parameters | 233,455,616 | 42,332,160 |
| Final reported loss | Aggregate `1.1415964373` | Step 318 `0.963399`; mean logged step loss `1.3705` |
| Final adapter | Present, hash verified | Present, hash verified |
| Checkpoint recovery | Frequent checkpoints used to harden the successful run | Checkpoint 318 validated and reused in a dedicated recovery run |
| Generation evaluation | 98/98 rows, no errors | 98/98 rows, no errors |
| Local deployment | Artifact retained | Active as Striatum backend `local-qwen-ft`, alias `qwen3.6-ft` |

The loss values in this table are not directly comparable. The 27B trainer emitted an aggregate `train_loss`; the 35B evidence retained per-step losses and their mean.

## Shared training objective and data

Both runs trained a structured reviewer rather than a general chat assistant. The model consumes review context and emits a machine-readable review decision. The training corpus contained 1,268 conversations:

| Slice | Examples |
|---|---:|
| Review | 882 |
| Implementation planning | 155 |
| Design convergence | 141 |
| Proposal generation | 90 |
| **Total** | **1,268** |

The full production corpus was text-only: each local JSONL row had an empty `images` list. The 35B smoke ladder nevertheless exercised the repository's shared multimodal processor, image preprocessing, chat-template, label-masking, collation, save/resume, adapter-reload, and inference paths using a small representative image set. It did not introduce a separate trainer.

Common production settings were:

- two epochs, micro-batch size 1, gradient accumulation 8;
- learning rate `1e-4`, cosine schedule, warmup ratio `0.03`;
- maximum sequence length 40,960, packing disabled, thinking disabled;
- BF16 compute, NF4 4-bit base quantization, double quantization;
- LoRA rank 32, alpha 64, dropout 0.05;
- gradient checkpointing and fused loss.

Only the SFT corpus required by the remote workload was uploaded. The source corpus, broader analysis material, and local fate-scoring work remained on owner-controlled systems.

## 27B campaign

### Configuration and environment

The 27B model was trained from `Qwen/Qwen3.6-27B` revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` on Secure Cloud pod `akbiwknw27725g`, a single H100 80 GB GPU with an encrypted 150 GB volume. The successful environment used:

- base image `runpod/pytorch:1.0.3-cu1281-torch291-ubuntu2404`;
- LLaMA Factory 0.9.5 at commit `7af909522a951e3ad9f022ea6f88b6755257eaa5`;
- PyTorch `2.8.0+cu128` and Transformers `5.6.0` with the required `s_aux` compatibility guard;
- FlashAttention `2.8.3.post1`, FLA `0.5.0`, TileLang `0.1.8`, `tvm-ffi` `0.1.13`;
- Liger Kernel `0.8.1` with the campaign's evaluation repair.

LoRA targeted all linear modules. The run reported 233,455,616 trainable parameters out of 27,590,184,176 total parameters, or 0.8462%.

The canonical configuration and operating notes are in [the training README](../../train/README.md) and `train/review_sft_qlora.yaml`.

### Attempt history and concrete failures

The H100 pod existed for 11 hours, 42 minutes, and 36 seconds. The productive training window was only part of that lifecycle:

1. Approximately 2 hours, 17 minutes, and 32 seconds were idle provisioning and setup time.
2. Seven launches failed while resolving dependency and model compatibility issues.
3. Attempt 8 reached step 100, then inline evaluation exhausted memory before a checkpoint was saved.
4. Attempt 9 was stopped at step 6 while the run strategy was being hardened.
5. The successful attempt disabled inline evaluation and saved every 25 steps.
6. The first post-training loss-evaluation attempt also exhausted memory because the normal logits path was active. Forcing the Liger fused evaluation path corrected it.

These were pipeline and operational failures, not evidence that the dataset was unreadable or that the model could not learn. The main robustness lesson was to checkpoint before evaluation and to test the exact evaluation memory path independently.

The complete billing and failure reconstruction is in the [27B billable-time postmortem](../audits/RUNPOD_SFT_BILLABLE_TIME_POSTMORTEM_2026-07-31.md).

### Successful run

The hardened run executed from 2026-07-31 00:04:34 to 05:38:39 UTC:

- optimizer steps: 318, or 159 per epoch;
- trainer runtime: 20,040.5629 seconds (5:34:00.56);
- aggregate training loss: `1.1415964372502934`;
- throughput: 0.127 samples/second and 0.016 steps/second;
- reported compute: `6.887872275152366e18` FLOPs.

A separate 98-example loss-only evaluation completed in 204.2102 seconds with loss `1.482760429` and throughput 0.48 examples/second.

### Artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `out/review-sft-r1/adapter_model.safetensors` | 933,974,032 | `9b467d625f8583e5cbf0a678f4268857af1f02397dac154b2766d7ac55b706bd` |
| `out/review-sft-r1-gguf/review-sft-r1-lora-f16.gguf` | 466,980,096 | `5ceec887104e4ee2de0e734932b50b73a7a34a7713584675b234c37b78ed5f15` |

The [local PEFT adapter directory](../../out/review-sft-r1/) also contains its tokenizer, template, and training metadata. The converted LoRA GGUF was produced for llama.cpp-based generation tests.

### Generation evaluation

Generation evaluation used a separate encrypted Secure Cloud A40 pod and the same 98-example review set used for the 35B comparisons. The first A40 attempt, pod `8ephtpsdiw6h2h`, failed because the controller treated input-path existence as proof that upload had finished. It was deleted within three minutes and produced no rows. The corrected attempt, pod `gb1ve73bf1x5d6`, produced all 98 rows without an inference error.

The evaluation used no-thinking decoding, temperature 0.6, top-p 0.95, top-k 20, minimum-p 0, a 40,960-token context, and Q8_0 KV cache. The serving base was the quantized `Qwen3.6-27B-IQ4_XS.gguf`, whose SHA-256 was `89f2c7e4f9f91d17ba9df6f0eef67cb909bc67d91cd035291be35cd88f1848ba`; the source adapter hash was the full value in the artifact table. Inference used llama.cpp commit `000547513f1530346ecd163db8b3e13962949961`. Adapter conversion temporarily applied upstream patch commit `f839835a3401f0bf000d362dc10ba6b1c50d3a3f` from llama.cpp pull request 24627. The result file SHA-256 was `d94570c7c83e0a13a614df16f1cb06b173e15c1e7bec9fc4990dd14c6ddc4f07`, and the summary SHA-256 was `90dca4296859b5aff82968b392e396af9e8cd3e3271f44aac4f473c6ff8b19de`.

| Metric | 27B baseline | Tuned 27B |
|---|---:|---:|
| Rows / inference errors | 98 / 0 | 98 / 0 |
| JSON-valid rate | 0.1429 | 1.0000 |
| Legal-output rate | 0.1429 | 1.0000 |
| Exact-verdict accuracy | 0.0510 | 0.4082 |
| Side accuracy | 0.0714 | 0.5510 |
| Fate accuracy | 0.2143 on 14 scored rows | 0.3980 on 98 scored rows |
| Mean generation time | 11.1 s | 26.7 s |

The tuned verdict distribution was 57 `accept`, 12 `accept_with_findings`, and 29 `needs_revision`. The baseline fate rate is especially weak evidence because only 14 baseline rows were scoreable. See the [27B baseline summary](../../eval-runs/baseline-27b-iq4xs-nothink/summary.json), [tuned-run notes](../../eval-runs/ft-r1-nothink/README.md), and [tuned summary](../../eval-runs/ft-r1-nothink/summary.json).

### Cost and cleanup

| 27B cost component | Amount |
|---|---:|
| Settled H100 training pod | $35.3405 |
| Of that, GPU | $35.0129 |
| Of that, storage | $0.3275 |
| Estimated successful training interval | $16.80 |
| Observed A40 evaluation balance delta | $0.4322 |
| **Known training plus evaluation spend** | **$35.7727** |

The H100 pod was deleted and subsequently returned HTTP 404, leaving zero current compute spend. The A40 evaluation pods were also deleted. The evaluation charge is reported as an observed balance delta because only the failed A40 attempt had settled into the per-run manifest at capture time.

## 35B MoE campaign

### Why the smoke ladder was added

The initial 35B effort found basic compatibility errors only after provisioning H200 nodes and moving large artifacts. Seven paid preflights failed in succession:

1. the first run used an unsuitable H100 path;
2. an H200 image never reached the workload before the provider exposure cap;
3. a later run reached the workload but failed during setup;
4. another stopped before a real training step;
5. the first forward pass failed in the Liger fused MoE path because FP32 activations met frozen BF16 experts;
6. after that repair, backward failed in the FLA TileLang compiler path;
7. TileLang `0.1.9` fixed the first compiler defect but exposed a deeper layout-inference conflict.

The workflow was then changed to validate the same production entry point in three increasingly expensive environments:

- **Gate 1, local pipeline:** `Qwen/Qwen3.5-0.8B` on the local 24 GB RTX 3090, four deterministic multimodal examples, four optimizer steps, checkpoint save at step 2, resume to step 4, adapter reload, and post-training inference.
- **Gate 2, Hopper environment:** the same tiny model and configuration in the exact production H200 container and dependency stack.
- **Gate 3, real-model MoE:** `Qwen/Qwen3.6-35B-A3B` on the H200 for four optimizer steps, including exact MoE LoRA discovery, gradients, checkpoint save/resume, and inference.

Gate 1 used `Qwen/Qwen3.5-0.8B` revision `2fc06364715b967f1860aea9cf38778875588b17`. It matched 186 adapter modules, reported 5,411,328 trainable parameters, produced finite loss `2.365198493`, and found nonzero gradients in 372 adapter parameters. Its evidence is retained at `/home/halbritt/.local/state/striatum-tuner/gate1-hopper-binding-20260802`. Gate 3's accepted run was `run-20260802T040419-24f8d88d7909`; it matched 310 modules, reported 42,332,160 trainable parameters, and passed finite-loss, gradient, optimizer, save, resume, and inference checks. Gate 2 validated the Hopper/SM90, BF16, FlashQLA, cache, mount, and checkpoint paths. FP8 was not enabled for the correctness gates.

The design and exact gate commands are retained in the [35B smoke-ladder guide](../../jobs/qwen35b_moe/SMOKE-LADDER.md). The model-specific operating record is in the [35B job README](../../jobs/qwen35b_moe/README.md).

### Production configuration

The production model was `Qwen/Qwen3.6-35B-A3B`, revision `995ad96eacd98c81ed38be0c5b274b04031597b0`, model type `qwen3_5_moe`. The measured base contained 34,224,090,480 parameters. A single H200 ran the final workload using the FlashQLA-backed Hopper path.

QLoRA was deliberately limited to linear modules whose representation and kernels supported training:

| Module group | Matched modules |
|---|---:|
| DeltaNet | 150 |
| Full attention | 40 |
| Shared expert | 120 |
| **Total** | **310** |

The fused routed experts remained frozen in BF16; no LoRA adapters were inserted into them. This produced 42,332,160 trainable parameters and 169,328,640 bytes of FP32 adapter weights. Target discovery failed closed if a requested group matched zero modules. The complete production values are recorded in [the checked-in training configuration](../../jobs/qwen35b_moe/training-config.json).

Before training, the tokenizer census found:

- 108 of 1,268 raw rows exceeded the 40,960-token cutoff;
- four prompts overflowed the cutoff and were handled by prompt-tail salvage;
- 59 assistant responses exceeded the cutoff;
- zero rows lost all supervised labels;
- the longest row shrank from 352,062 raw tokens to 40,960 effective tokens, retaining 14,903 prompt tokens and 26,057 supervised assistant tokens.

### Staged source run

The full source run was `run-20260802T043418-2e928c2a9cb5`. Training was staged so that compatibility, early quality, and epoch boundaries could be checked before paying for the rest of the run:

| Stage | Work | Runtime |
|---|---|---:|
| Initial training | Step 0 to 5 | 461.519 s |
| Resume | Step 5 to 25 | 787.683 s |
| Mini evaluation | 16 examples | 635.086 s |
| Resume | Step 25 to 159 | 4,265.912 s |
| Epoch-one evaluation | 98 examples | 3,154.490 s |
| Resume | Step 159 to 318 | 4,882.676 s |
| **Training child stages** | **318 steps** | **10,397.789 s** |
| **In-training evaluation gates** | **114 generations** | **3,789.575 s** |

The 16-example gate was fully JSON-valid and legal, with side accuracy 0.5. The epoch-one gate was fully JSON-valid and legal, with side accuracy 0.4184. Both satisfied their predefined strict gates.

Selected training losses were:

| Step | Loss |
|---|---:|
| 1 | 1.6046 |
| 25 | 1.5929 |
| 159 | 1.4331 |
| 318 | 0.963399 |

The mean retained per-step loss was 1.3705. Training reached step 318 and wrote its final checkpoint. The source controller later marked the run failed in the `evaluate` phase with `phase_nonzero_exit`. That status describes incomplete terminal orchestration after training, not failed optimization.

### Recovery without retraining

The recovery run, `run-20260802T122647-fd862d28930d`, reused the existing checkpoint and final adapter. It did not repeat training or the full 98-row evaluation. It:

1. validated the eight-file checkpoint-318 manifest;
2. loaded the trained adapter and performed post-training inference;
3. converted the adapter to GGUF;
4. checked Hugging Face and llama.cpp exports against a shared semantic contract;
5. wrote a recovered 27-file artifact manifest.

Recovery took 487.325915 seconds and cost $0.60915739375. The Hugging Face and llama.cpp outputs were not byte-identical. Both produced valid review JSON with posture `adversarial` and verdict `accept`; that semantic agreement was the accepted export contract, and both raw outputs were preserved.

The final recovery image was `ghcr.io/halbritt/striatum-tuner-qwen35b-moe@sha256:72301afcc29fbf5cdf3ef33b5e428901a590a5f008a166e73c606b8701d270db`, version `0.1.31`. It was bound to tuner commit `c4f9635a4e3e3a85824cf9299b2058131d51934e` and runpod-jobrunner `0.1.12` commit `144537205e3fd2e3b09b16179ef3872b13f14d8e`.

### Artifacts and integrity

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| PEFT `adapter_model.safetensors` | 169,425,720 | `c729f8aea80a0eb0af74bfdccb1fe4b900196ea800cef97dd1c3a3d107987464` |
| LoRA `adapter-f32.gguf` | 169,373,216 | `807a2a59544fd9e78c8527cfb272778d9ecc7312c25e18bfa1fa7f41d1326715` |
| Checkpoint-318 manifest, 8 files / 258,025,128 bytes | — | `0929124a0a547490a737ea4060799b0c95e303f5338ee93be73a1dcaee256e9c` |
| Recovery artifact manifest | — | `3909de1dd64b0808f123580f781c88f885f6b48d0ff00e92b81be92589901d35` |
| Export receipt | — | `b9adecf135e528a784887f0617d0089a7943a8e2e1111d982799e26d97192cf1` |
| Fate-gate receipt | — | `d6926a613a74ab45c6f491e66bf2ba66e2e6dab8a65c0845d02ec1d3ab508f14` |

The authoritative recovery artifact root is:

```text
/home/halbritt/.local/state/runpod-jobrunner/runs/run-20260802T122647-fd862d28930d/receipts/artifacts
```

The RunPod network volume `7lno735a6g` remains retained for recoverability and cache reuse. All compute pods were deleted; current compute spend was zero at campaign closeout. Retained volume storage can continue to incur storage charges.

### Evaluation and acceptance

The final 98-example evaluation produced 98 rows without inference errors:

| Metric | Historical 35B baseline | Tuned 35B |
|---|---:|---:|
| JSON-valid rate | 0.8878 | 1.0000 |
| Legal-output rate | 0.8673 | 1.0000 |
| Exact-verdict accuracy | 0.1939 | 0.5510 |
| Side accuracy | 0.3367 | 0.6020 |
| Fate accuracy | 0.1882 on 85 scored rows | 0.5306 on 98 scored rows |
| Mean generation time | 11.3 s | 35.839 s |

The tuned verdict distribution was 37 `accept`, 3 `accept_with_findings`, and 58 `needs_revision`. All four strict acceptance checks passed. The local fate gate also passed: 0.5306 on all 98 rows versus the baseline's 0.1882 on 85 scoreable rows.

This comparison is useful behavioral evidence, not an exact same-weights ablation. The historical baseline came from a third-party GGUF whose source bits were not pinned to the official Hugging Face snapshot used for training. See the [historical 35B baseline summary](../../eval-runs/baseline-35b-nothink/summary.json).

### Cost and cleanup

| 35B cost component | Amount |
|---|---:|
| Terminal controller receipts | $37.0793 |
| Three operator-stopped runs reconstructed from runtime | $6.0563 |
| Manual L40S diagnostic cap | $0.33 |
| **Conservative all-in campaign estimate** | **at most $43.47** |

The estimate includes failed preflights, smoke tests, the full source run, evaluations, and recovery. It is below the authorized $100 ceiling with at least $56.53 of headroom. Zero RunPod pods remained at closeout.

The full source run's controller receipt was $22.83121344625 over 18,264.970757 seconds. The recovery receipt was $0.60915739375. Both are already included in the all-in estimate and must not be added to it again.

## Cross-model result

| Metric | 27B baseline | Tuned 27B | Historical 35B baseline | Tuned 35B |
|---|---:|---:|---:|---:|
| JSON-valid | 0.1429 | 1.0000 | 0.8878 | 1.0000 |
| Legal output | 0.1429 | 1.0000 | 0.8673 | 1.0000 |
| Exact verdict | 0.0510 | 0.4082 | 0.1939 | 0.5510 |
| Side accuracy | 0.0714 | 0.5510 | 0.3367 | 0.6020 |
| Fate accuracy | 0.2143* | 0.3980 | 0.1882** | 0.5306 |

`*` Fourteen scoreable rows. `**` Eighty-five scoreable rows. Tuned rates use all 98 rows.

Both tuned models fixed the most important format failure: every evaluated output was valid JSON and belonged to the legal verdict set. The tuned 35B model had the stronger exact-verdict, side, and fate results on this evaluation. It was also slower per generation. The comparison does not isolate architecture alone because the baselines used different quantized artifacts and did not provide identical same-source checkpoints.

## Current deployment state

The recovered 35B LoRA is installed at:

```text
/home/halbritt/models/Qwen3.6-35B-A3B-Striatum-FT/adapter-f32.gguf
```

It is served with the local compact base:

```text
/home/halbritt/models/Qwen3.6-35B-A3B-APEX-I-Compact.gguf
```

Striatum selects it through backend `local-qwen-ft` and model alias `qwen3.6-ft`. The backend is review-only and passed the deployed request/response contract. The [deployment receipt](../../deploy/local-qwen-ft/deployment-receipt-2026-08-03.md) records exact service configuration and validation.

The training export was validated against the campaign's BF16 base, while current serving uses the compact APEX base. Deployment conformance proves that the local service loads and answers through Striatum; it is not a substitute for a new quality evaluation of that exact compact-base-plus-adapter combination.

The 27B adapter and GGUF are retained locally but are not the active Striatum backend.

## Failures each validation layer can and cannot detect

| Layer | Detects | Does not establish |
|---|---|---|
| Local dense smoke test | Configuration, processor and image path, templates, tokenization, masking, collation, dense LoRA discovery, forward/backward, optimizer, save/resume, adapter inference | Hopper kernels, H200 mounts, MoE routing, full-model memory |
| Hopper dense smoke test | Exact container and CUDA stack, SM90 kernels, BF16, FlashQLA/SDPA selection, caches, mounts, checkpoint writes | Real 35B module discovery, expert dispatch, real-model memory |
| Real-model MoE smoke test | MoE targets, router/expert behavior, trainable counts, gradient flow, checkpoint compatibility, 35B memory | Multi-hour stability, full-corpus quality, final export acceptance |
| Production training | Full optimizer trajectory and checkpoint creation | Correct terminal export, quality acceptance, deployment behavior |
| Recovery and artifact validation | Checkpoint reuse, adapter load, conversion, semantic export parity, hashes | New training, independent quality improvement |
| Evaluation and fate gate | Structured-output validity and held-out task behavior | General capabilities outside the 98-row set |
| Deployment check | Installed paths, service startup, Striatum protocol behavior | Same-base equivalence with the BF16 training export |

## What this report does not claim

- It does not claim that a model merely loading constituted a successful run. Both campaigns performed backward passes, optimizer steps, checkpoint writes, and generated evaluation output.
- It does not claim that the 27B and 35B losses are directly comparable.
- It does not claim byte-for-byte parity between Hugging Face and llama.cpp inference for the 35B export.
- It does not claim that the historical GGUF baselines are exact same-source ablations of the Hugging Face checkpoints.
- It does not claim that the compact base now used for local 35B serving is behaviorally identical to the BF16 base used to validate the training export.
- It does not claim that zero compute pods means zero ongoing provider cost; the retained network volume may still accrue storage charges.

## Evidence index

- [27B training configuration and commands](../../train/README.md)
- [27B billable-time postmortem](../audits/RUNPOD_SFT_BILLABLE_TIME_POSTMORTEM_2026-07-31.md)
- [27B baseline evaluation](../../eval-runs/baseline-27b-iq4xs-nothink/summary.json)
- [27B tuned evaluation](../../eval-runs/ft-r1-nothink/summary.json)
- [27B local adapter](../../out/review-sft-r1/)
- [35B production configuration](../../jobs/qwen35b_moe/training-config.json)
- [35B smoke-test ladder](../../jobs/qwen35b_moe/SMOKE-LADDER.md)
- [35B job and artifact guide](../../jobs/qwen35b_moe/README.md)
- [35B historical baseline evaluation](../../eval-runs/baseline-35b-nothink/summary.json)
- [35B local deployment receipt](../../deploy/local-qwen-ft/deployment-receipt-2026-08-03.md)

This report is a synthesis of the repository records, local model artifacts, run-controller receipts, provider cleanup evidence, and evaluation summaries available on 2026-08-03. The underlying receipts remain authoritative if a shortened hash or rounded metric here conflicts with its source.
