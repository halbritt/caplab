# striatum-tuner

Fine-tuning corpus extraction for the local Striatum lane model (Qwen on
`localhost:8081`). Mines the striatum-next graph's provenance ledger and
retained exchange spool into prompt→output SFT datasets, so the local model
can be trained to serve as an execution-lane backend (the `local-qwen`
declaration in `striatum-next/backends/`).

Workstation tooling — deliberately **outside** the product repo (same standing
as `~/git/agent-artifact-miner`): it reads the graph store and spool, produces
no compiler artifacts, and gates nothing.

## What it does

Every historical pass run left three things behind:

1. **Sealed dispatch bundle** — `~/.local/share/striatum/exchange/<graph>/dispatch/<dispatch_id>/`
   (manifest + environment + inputs): exactly what the lane received.
2. **Submission bundle** — `…/spool/submissions/<dispatch_id>/`
   (outputs + exhaust): exactly what the lane produced.
3. **Ledger labels** — admission decisions, gate verdicts, refusal codes, run
   closures.

`render.py` is a byte-faithful Python port of the lane prompt renderer
(`striatum-next/internal/backend/llm/prompt.go` @ HEAD), including the
argv-mode inline-selection/spill algorithm. Each re-rendered prompt is
verified against the `rendered_prompt_hash` its attempt closure recorded:
**records from 2026-07-25 onward verify byte-exact** (the port-correctness
canary); older records mismatch only because the Go renderer itself evolved
(26 revisions), and re-rendering them at HEAD is deliberate — training should
match the prompt distribution the lane will see at inference.

## Usage

```bash
# 1. Extract the full corpus (one JSONL record per submission, with prompt,
#    outputs, and ledger labels). ~2k records / ~215 MB for the main graph.
python3 extract.py --repo ~/git/striatum-next \
    --graph 019f22ef-0cb4-780f-9b82-b210bab24325 --out corpus
# (--ledger-jsonl <dump> skips the `striatum ledger cat` invocation)

# 2. Build SFT train/eval splits (OpenAI messages format, time-ordered split —
#    eval is strictly newer than train).
python3 make_sft.py --corpus corpus/corpus.jsonl --pass review --out sft
python3 make_sft.py --corpus corpus/corpus.jsonl --pass implementation-planning --out sft
```

Extracted passes (the one-shot lanes; `build` is excluded until the local
harness grows a tool loop — a one-shot model cannot compute
`result_tree_hash`):

| pass | train/eval | notes |
|---|---|---|
| review | 882 / 98 | median ~9k tok, p90 ~24k, max ~37k (3.5 bytes/token measured); verdicts 212 accept / 254 accept_with_findings / 509 needs_revision / 5 reject |
| implementation-planning | 155 / 24 | fenced `striatum-work-graph` JSON grammar |
| design-convergence | 141 / 16 | |
| proposal-generation | 90 / 9 | |

The split is candidate-aware: dual-signal review puts the same candidate in
front of two lanes, so whole candidate groups land on one side of the
time-ordered split (zero train/eval candidate overlap, verified), and DPO
pairs exclude eval candidates.

Filters (see `make_sft.py`): admitted + `status: complete` only; baseline
lanes excluded (`local-qwen`, `glm`, `kimi`, deterministic `local`) so targets
come from frontier/strong backends; legacy `revise` verdicts normalized to the
current gate vocabulary (`needs_revision`); prompts capped at 128 KiB (the
argv transport bound; ≈37k tokens, inside the 40960 training cutoff).

A production-mirror baseline with thinking left on is unnecessary: the
incumbent's historical ledger performance (40.2% fate agreement over 246 real
reviews, thinking on) already *is* that number.

## Pipeline

| step | tool | status |
|---|---|---|
| corpus extraction | `extract.py` | done — 2,051 records |
| fate labels + backend ranking | `analyze.py` | done — `corpus/analysis.json` |
| SFT splits | `make_sft.py` | done — `sft/` |
| DPO pairs (dual-signal disagreements) | `make_dpo.py` | done — 78 pairs |
| baseline eval of served model | `eval.py` | done — `eval-runs/baseline-35b-nothink/` |
| QLoRA SFT | `train/*.yaml` | done — `out/review-sft-r1/` |
| tuned generation eval | `eval.py` | done — `eval-runs/ft-r1-nothink/` |
| deploy as new backend | `deploy/local-qwen-ft/` | after eval acceptance |

### Verdict-vs-fate ranking (from `analyze.py`)

Fate of each reviewed candidate — later admission with different content
("revised") vs last admitted content ("final") — adjudicates every review
verdict identically across backends:

| backend | reviews | fate agreement |
|---|---|---|
| codex-sol-max | 440 | 83.2% |
| codex | 249 | 82.3% |
| claude-code | 26 | 69.2% |
| claude-harm-opus-4-8-high | 86 | 67.4% |
| agy | 109 | 57.8% |
| **local-qwen (incumbent)** | **246** | **40.2%** |
| agy-gemini-3-6-flash-medium | 26 | 15.4% |

Caveat: primary reviewers partially *cause* the fate they are scored against
(the gate aggregates their verdict), so top-line numbers are flattered; the
gap between the incumbent and the frontier lanes is the signal, and closing
it is the point of the fine-tune.

### Held-out generation evaluation

Replay of the same 98-example held-out review split with
`enable_thinking: false`. The tuned run loaded the final SFT adapter over the
same Qwen3.6-27B IQ4_XS base used for the 27B baseline.

| metric | untuned 27B¹ | untuned 35B | tuned 27B² | frontier reference |
|---|---:|---:|---:|---:|
| JSON valid | 14.3% | 88.8% | **100.0%** | ~100% |
| verdict legal | 14.3% | 86.7% | **100.0%** | 100% |
| exact verdict match | 5.1% | 19.4% | **40.8%** | — |
| verdict side match | 7.1% | 33.7% | **55.1%** | — |
| fate agreement | 21.4% (14 scored) | 18.8% (85 scored) | **39.8% (98 scored)** | 83.2% (codex-sol-max) |

¹ `eval-runs/baseline-27b-iq4xs-nothink/`: Qwen3.6-27B IQ4_XS served with
llama.cpp b10186 on peecee's 3090 Ti (ctx 40960, q8_0 KV, same sampler,
no-think), run under a gpu-fleet `marker`-slot lease. Its dominant failure is
total: 84/98 responses are the 6-token literal `outputs/review-ledger` — the
base model parrots the output path instead of reviewing. The 35B fails
differently (rubber-stamp accepts + ~11% broken JSON). SFT attacks both:
output format is learned directly, and the verdict distribution is balanced.

² `eval-runs/ft-r1-nothink/`: final SFT LoRA converted to F16 GGUF and served
over the 27B IQ4_XS base with llama.cpp version 10210
(`000547513f1530346ecd163db8b3e13962949961`), ctx 40960, q8_0 KV, and the
same sampler. The run completed all 98 requests without an endpoint error.
Against the 35B baseline on the same examples, the tuned model gained 32 and
lost 11 exact-verdict matches; it gained 26 and lost 5 side matches. Fate
agreement has a different denominator because it is scored only when a model
returns a legal verdict; on the 85 examples scored for both tuned and 35B,
the rates are 40.0% and 18.8%, respectively. Latency is not compared because
the tuned and baseline runs used different GPUs.

## Corpus record shape

One JSON object per submission: `dispatch_id`, `run_ref`, `pass`,
`backend_id`, `written_at`, `prompt` (re-rendered), `prompt_hash_verified`,
`outputs{output_id: {kind, body}}`, `diagnostics`, and `labels`
(`admitted`, `admission_decisions`, `submission_refused`, `run_closures`,
`gate_verdicts`).

`labels.gate_verdicts` + the dual-signal duplicate reviews in the ledger
(`redundant_candidate` records) are the raw material for a DPO stage: two
backends reviewed the same subject; prefer the one that agreed with the
adjudicated outcome. Not built yet.

## Training and deployment notes

- The completed 27B QLoRA run trained no-think. Serve it with
  `chat_template_kwargs={"enable_thinking": false}`.
- 27B QLoRA at 32k sequence length does not fit a single 3090; the completed
  run used a rented H100.
- Serve as GGUF LoRA adapter (`--lora`) or merged+requantized; either way the
  tuned model enters Striatum as a **new backend declaration** (own id, own
  seal key, `quality: baseline`) — never by mutating `local-qwen` in place.
- Before deployment acceptance, replay held-out sealed dispatch bundles through
  `striatum-openai-lane` against the tuned endpoint; score JSON validity and
  verdict agreement with the adjudicated ledger outcome.

`corpus/` and `sft/` are generated data and stay out of git — regenerate from
the graph store, which is the system of record.
