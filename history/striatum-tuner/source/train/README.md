# Training runbook (needs the GPU rig)

Everything before step 3 is already done in this repo; steps 3+ need the
quad-3090 rig (or one rented 80 GiB card).

## 0. Prereqs

```bash
pip install llama-factory   # or: git clone LLaMA-Factory && pip install -e .
# HF weights for the tuning target at the path named in review_sft_qlora.yaml,
# e.g. /home/halbritt/models/hf/Qwen3.6-27B (must match what you will serve).
```

`dataset_info.json` here must be copied (or symlinked) into the dataset dir:

```bash
ln -s ../train/dataset_info.json sft/dataset_info.json
```

## 1. Datasets (done — regenerate any time)

```bash
python3 extract.py --ledger-jsonl <dump> --out corpus
python3 analyze.py --ledger-jsonl <dump>
python3 make_sft.py --corpus corpus/corpus.jsonl --pass review --out sft   # + other passes
python3 make_dpo.py
```

## 2. Baseline (done — see eval-runs/)

```bash
python3 eval.py --eval sft/review.eval.jsonl --out eval-runs/baseline-35b-nothink
```

## 3. SFT (GPU)

```bash
llamafactory-cli train train/review_sft_qlora.yaml
```

~1.4k examples × ~2 epochs at cutoff 40960. On 4×3090 with ZeRO-3 offload
expect hours, not days. Watch eval loss; the review set dominates by design.

## 4. Optional DPO (GPU)

```bash
llamafactory-cli train train/review_dpo.yaml
```

Only 78 pairs — treat as a nudge. Keep the result only if step 5 improves.

## 5. Eval the adapter (any box that can serve it)

Export + serve, then replay the held-out split and diff against baseline:

```bash
# merge adapter into the base model
llamafactory-cli export --model_name_or_path <base> \
    --adapter_name_or_path out/review-sft-r1 \
    --export_dir out/review-sft-r1-merged --template qwen3

# GGUF for llama.cpp (in ~/git/llama.cpp)
python3 convert_hf_to_gguf.py out/review-sft-r1-merged --outfile qwen-ft-f16.gguf
./build/bin/llama-quantize qwen-ft-f16.gguf qwen-ft-Q4_K_M.gguf Q4_K_M
# (alternative: convert_lora_to_gguf.py and serve base + --lora adapter.gguf)

# serve on a second port, then:
python3 eval.py --eval sft/review.eval.jsonl --base-url http://127.0.0.1:8082/v1 \
    --model qwen-ft --out eval-runs/ft-r1-nothink
```

Metrics that must beat `eval-runs/baseline-35b-nothink/summary.json`:
`json_valid`, `verdict_legal`, `side_match`, `fate_agreement`. The frontier
reference ceiling is in `corpus/analysis.json` (codex-sol-max ≈ 0.83
fate-agreement; incumbent local-qwen ≈ 0.40).

## 6. Deploy into Striatum

See `../deploy/local-qwen-ft/` — new backend id, own seal key, quality
baseline. Never mutate the `local-qwen` declaration in place.
