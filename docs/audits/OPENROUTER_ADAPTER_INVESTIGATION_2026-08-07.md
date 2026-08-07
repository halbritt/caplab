# Why the OpenRouter adapter path "failed" — investigation and correction plan (2026-08-07)

Question investigated: Kimi K3 and DeepSeek V4 Flash *should* be usable as
review backends through `striatum-openai-lane` → OpenRouter, but the 2026-08-07
measurements said otherwise (DSv4F fate-agreement 27%, K3 0% json-valid /
empty content), while tuples with native coding harnesses looked fine. Why?

Answer: **three independent defects stacked**, and the largest one is in the
benchmark, not the backends. DeepSeek V4 Flash is almost certainly a usable
review backend today; K3 needs one declaration flag that GLM's declaration
already carries.

## Finding 1 — the eval split starves endpoint models of the review subject (benchmark validity)

`sft/review.eval.jsonl` prompts are byte-faithful re-renders of the *original*
production dispatches (hash-verified against `rendered_prompt_hash` — that was
the design goal for training fidelity). But 79/98 examples originated on
`codex-sol-max` and 12 more on agy — **argv-mode lanes**, where large input
bodies are spilled out of the prompt as *"— N bytes, not inlined; materialized
at `<path>` (relative to your working directory): read it from there"*.

**87 of 98 eval examples carry spilled input bodies.** Replayed against a chat
endpoint, the model is told to read files that do not exist and cannot see the
artifact it is reviewing. All 98 also carry another lane's absolute
`Your working directory is /home/…/exchange/…/work` sentence.

Re-scoring the 2026-08-07 DeepSeek V4 Flash run (`or-deepseek-deepseek-v4-flash-20260807`)
split by subject visibility:

| subset | n | json_valid | side_match | fate_agreement |
|---|---|---|---|---|
| fully-inline (fair) | 11 | 0.91 | 0.73 | **8/10 (80%)** |
| spilled (subject invisible) | 87 | 0.72 | 0.18 | 11/60 (18%) |

80% fate-agreement on the fair subset is codex-class (codex-sol-max production
number: 83.2%). The headline 27% was an artifact of asking the model to review
an invisible artifact — the observed rubber-stamp `accept`s and the DSML
pseudo-tool-call emissions (`<｜｜DSML｜｜tool_calls>… pwd && ls -la`) are exactly
what a model does with that prompt.

**Blast radius:** every endpoint-path number measured on this split inherits the
invalidity — the 35B baseline (fate 18.8%, "rubber-stamp accepts"), the 27B
IQ4_XS baseline (84/98 parroting `outputs/review-ledger` — parroting the path
the prompt told it to write), the `ft-r1` post-tune evals, and both 2026-08-07
OpenRouter probes that set `kimi-k3`'s declared quality note. The **SFT/DPO
training corpus itself** uses the same original-transport prompts: a tuned
stdin-serving lane is being trained mostly on prompts referencing files it will
never see. Conclusions and rankings built on these numbers are unsafe until
re-measured on transport-correct prompts.

## Finding 2 — K3's empty content: it tries to *act* on the file-writing instructions

Reproduced live (raw bodies preserved in `eval-runs/probe-k3-content-channel-20260807/`):
a fully-inline review prompt to `moonshotai/kimi-k3` (provider Together) returns
`finish_reason: stop`, **empty `content`**, 9,787 reasoning tokens. The
reasoning tail shows the mechanism verbatim: the model finishes the review in
its thinking channel, then — *"Now write the files. … Let me write the files
now."* — attempts tool-style file writes the request cannot express, and stops.

The rendered prompt (`prompt.go`: `oneShotPreamble`, `outputRules`, the
`workDir` sentence, `- outputs/review-ledger (required)`) instructs file
workspace behavior even on stdin/stdout-only lanes; the supervisor bridges
stdout→file afterward. Harness lanes really can write files; one-shot chat
models can't, and each fails its own way: K3 stalls into empty content,
DeepSeek emits DSML pseudo-tool-calls, small local models parrot the output
path. This is why K3's failure was "specific to the review prompt shape" while
a trivial control prompt worked — the control prompt asked for no files.

So `backends/kimi-k3/backend.yaml`'s recorded conclusions are wrong on both
counts: the "measured review-task incompatibility" is a prompt-shape interaction
(not a K3 defect), and the adapter comment "the budget is the fix" is refuted —
both probe configs stopped naturally (`stop`, not `length`) with budget to spare.

## Finding 3 — the fix is already in the fleet: GLM's declaration shape

Same prompt, same model, same provider, plus
`response_format: {json_schema: review_ledger, strict}` and
`provider: {require_parameters: true}` → **valid ledger in `content`**
(verdict + findings + summary, schema-conformant), $0.124, 68s. The schema
constraint forces decoding into the content channel; the file-writing stall
disappears.

This is exactly `-response-format review-ledger`, which
`backends/glm/backend.yaml` passes and the new `kimi-k3` /
`deepseek-v4-flash` declarations omit.

## Finding 4 — secondary defects worth fixing while we're here

- `striatum-openai-lane` only sends a `provider` block when
  `-openrouter-provider` pins an exact endpoint. `-response-format` without a
  pin can route to a provider that silently ignores `json_schema`. When a
  response format is set, the lane should also send
  `provider: {require_parameters: true}` (needs omitempty serialization — an
  explicit empty `only: []` would exclude every provider).
- The lane's empty-content error doesn't report the reasoning channel. One line
  ("content empty; N reasoning tokens present") turns this whole investigation
  into a glance.
- `-disable-thinking` maps to llama.cpp's `chat_template_kwargs` only;
  OpenRouter ignores it. Reasoning control there is the unified `reasoning`
  parameter (`effort` / `max_tokens` / `enabled`) — currently unreachable from
  a declaration.
- `eval_harness.py` scores the **newest-mtime file** in `outputs/` — codex
  writes `ASSUMPTIONS.md` after `review-ledger`, so most 2026-08-07 harness
  rows scored the assumptions note (verdict null). It must read the declared
  required output by name.
- `eval_harness.py` runs harness lanes in **empty workspaces** while the prompt
  names the real exchange paths — codex rows on this host record wandering to
  the production exchange and reading the original sealed bundles
  (`"inspected the matching sealed review input bundle available under the
  exchange workspace"`). Un-materialized inputs + reachable production spool =
  measurement contamination (including potential answer leakage from original
  outputs). Today's `harness-*` rows are invalid as measurement too.

## Cost/latency reality (from the probes)

K3 review ≈ $0.12–0.17 and ~70s per example on Together (~7–10k reasoning
tokens each; ≈$15/M completion). A full 98-example K3 run ≈ **$12–17**.
DSv4F is flash-priced and averaged 81s across 98 examples.

## Correction plan

### striatum-next (product repo — open a compilation-request bracket per D0011.C4)

1. **Declarations** (`backends/kimi-k3`, `backends/deepseek-v4-flash`): add
   `-response-format, review-ledger` to `adapter.command`; replace the
   incorrect incompatibility/budget notes with the confirmed mechanism
   (reference this audit + probe dir); keep quality `baseline` until the fair
   benchmark places them, then raise with `basis: measured` +
   `benchmark_ref` (tuples earn their rank).
2. **Lane** (`cmd/striatum-openai-lane`): send
   `provider: {require_parameters: true}` whenever a response format is set
   (unless a pin already provides it), with correct omitempty JSON; extend the
   empty-content error with reasoning-token presence from
   `completion_tokens_details`; optionally add `-reasoning-effort` /
   `-reasoning-max-tokens` flags mapping to OpenRouter's unified `reasoning`
   parameter so declarations can bound think-spend.
3. **Optional, its own pass**: a stdout-native instruction variant of the
   prompt projection for `stdout_output: single-required-output` lanes ("your
   entire response is the required output document; you have no filesystem") —
   removes the file-writing confusion at the source. Touches `prompt.go` +
   `render.py` parity; not needed for correctness once response_format is in.

### striatum-tuner (the real benchmark tooling)

1. **Fair split**: re-render all eval prompts stdin-mode (all-inline, no
   foreign workDir) via `render.py` — it already implements the mode switch.
   Keep the original-transport renders for harness-lane measurement. Tag every
   result row `subject_visible`.
2. **One runner, production parity** (`bench.py`, unifying `eval.py` +
   `eval_harness.py`): measure every tuple **through its declared
   `adapter.command`** the way the supervisor invokes it. Endpoint lanes:
   prompt on stdin, content from stdout (exactly the production bridge).
   Harness lanes: materialize `inputs/` into an isolated per-example workspace,
   re-render the prompt with *that* workDir (no production exchange paths
   reachable or referenced), then read the **declared required output**
   (`outputs/review-ledger`) — never newest-mtime. Record per row: usage,
   cost, provider, `native_finish_reason`, reasoning tokens, wall-clock.
3. **Leaderboard**: per-tuple summary (json_valid, verdict_legal, side_match,
   fate_agreement, exact-match, mean latency, $/review) written to
   `docs/results/review-benchmark-<date>.md`; declaration `quality.classes`
   updates cite it as `benchmark_ref`.
4. **Re-measure**: DSv4F full fair split (cheap); K3 fair split with
   response_format (~$15); GLM (replace its `benchmark-stated` frontier row
   with a measured one); local 35B baseline (the FT project's baseline is
   invalid as measured); harness tuples through the fixed harness path.
5. **Corpus follow-up**: before the next fine-tune round, re-render the SFT/DPO
   train prompts stdin-mode too — the serving lane is stdin; training on
   argv-mode spill prompts teaches path-parroting.

## Evidence

- `eval-runs/probe-k3-content-channel-20260807/` — raw K3 responses, both configs.
- `eval-runs/or-deepseek-deepseek-v4-flash-20260807/` — 98-row DSv4F run
  (headline numbers invalid per Finding 1; fair-subset re-score above).
- `eval-runs/or-moonshotai-kimi-k3-20260807/results.jsonl` — empty (run
  produced no rows); the `probe-k3-*` dirs the kimi-k3 declaration cites never
  landed in this repo — this audit and the probe dir above replace them.
- `eval-runs/harness-*-20260807/` — kept as evidence of the harness-runner
  defects (Finding 4); not measurements.
