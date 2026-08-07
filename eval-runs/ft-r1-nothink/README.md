# Tuned 27B no-think generation evaluation

This directory contains the 98-example held-out generation replay for the
final `review-sft-r1` adapter. `eval.py` used the same no-think request shape,
sampler, 40960-token context, q8_0 KV cache, and held-out split as the
untuned-27B baseline.

The generation ran on an encrypted Runpod Secure Cloud A40. Only the public
base GGUF, derived LoRA GGUF, `sft/review.eval.jsonl`, chat template, evaluator,
and llama.cpp server binary were uploaded. `corpus/analysis.json` stayed on
Proximal; it was applied after the 98 generated rows were copied back and the
pod was deleted.

The Qwen3.6 LoRA conversion required the still-open llama.cpp
[PR 24627](https://github.com/ggml-org/llama.cpp/pull/24627) at commit
`f839835a3401f0bf000d362dc10ba6b1c50d3a3f`. The patch was applied in a
temporary worktree only; the served binary came from unmodified upstream
commit `000547513f1530346ecd163db8b3e13962949961`.

`summary.json` is the final locally rescored summary. `results.jsonl` contains
98 unique dispatch IDs and no endpoint errors. The remote pre-rescore hashes
remain in `logs/results-sha256.log`; the final local hashes are recorded in
`run-manifest.json`.

The first launch attempt is retained separately in
`../ft-r1-nothink-attempt1-failed/`. Its runner tried to hash files after their
destination paths appeared but before transfer completion. The watchdog
deleted that pod within three minutes. The successful runner required an
explicit `.uploads-complete` marker before checking any input or loading the
GPU.
