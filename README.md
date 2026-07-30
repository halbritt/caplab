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
| review | 882 / 98 | median ~9k tok, p90 ~24k, max ~32k; verdicts 212 accept / 254 accept_with_findings / 509 needs_revision / 5 reject |
| implementation-planning | 162 / 17 | fenced `striatum-work-graph` JSON grammar |
| design-convergence | 142 / 15 | |
| proposal-generation | 90 / 9 | |

Filters (see `make_sft.py`): admitted + `status: complete` only; baseline
lanes excluded (`local-qwen`, `glm`, `kimi`, deterministic `local`) so targets
come from frontier/strong backends; legacy `revise` verdicts normalized to the
current gate vocabulary (`needs_revision`); prompts capped at 192 KiB.

## Pipeline

| step | tool | status |
|---|---|---|
| corpus extraction | `extract.py` | done — 2,051 records |
| fate labels + backend ranking | `analyze.py` | done — `corpus/analysis.json` |
| SFT splits | `make_sft.py` | done — `sft/` |
| DPO pairs (dual-signal disagreements) | `make_dpo.py` | done — 78 pairs |
| baseline eval of served model | `eval.py` | done — `eval-runs/baseline-35b-nothink/` |
| QLoRA SFT (+optional DPO) | `train/*.yaml` | **needs GPU rig** — see `train/README.md` |
| deploy as new backend | `deploy/local-qwen-ft/` | after training |

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

## Training notes (for the next step)

- Target model should be whatever `llama-27b.service` will serve; train
  no-think and serve with `chat_template_kwargs={"enable_thinking": false}`.
- 27B QLoRA at 32k sequence length does not fit a single 3090 — use the
  quad-3090 rig or a rented GPU for the training run itself.
- Serve as GGUF LoRA adapter (`--lora`) or merged+requantized; either way the
  tuned model enters Striatum as a **new backend declaration** (own id, own
  seal key, `quality: baseline`) — never by mutating `local-qwen` in place.
- Pre-deployment eval: replay held-out sealed dispatch bundles through
  `striatum-openai-lane` against the tuned endpoint; score JSON validity and
  verdict agreement with the adjudicated ledger outcome.

`corpus/` and `sft/` are generated data and stay out of git — regenerate from
the graph store, which is the system of record.
