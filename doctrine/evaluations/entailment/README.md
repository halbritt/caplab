# Claim-to-source entailment screening

Model-judged screening of whether each doctrine concept's cited source section
actually supports its claimed contribution. This covers the first property
listed under "Build evaluations before the retriever" in
[`../../OPERATIONALIZATION.md`](../../OPERATIONALIZATION.md) — claim-to-source
entailment — which the deterministic fixtures in the parent directory
explicitly do not evaluate.

## Epistemic framing

Per [`ubiquitous_language.md`](../../../ubiquitous_language.md):

- Each record's `verdict` is an **observation** of model output: the fact that
  a specific model, given a specific section and contribution, emitted a
  specific judgment. The evidence is the record itself (locator, chapter
  checksum, prompt parameters, model identity, raw fields).
- That observation supports an **inference** about entailment: the citation
  probably does (or does not) support the contribution. Rival explanations
  always include model error, truncation of the section, and the section-scope
  assumption below.
- A verdict is **screening, never verification and never acceptance**. It
  ranks citations for human audit. It creates no authority to change anything,
  and results must never modify doctrine sources, concept records, or the
  graph. When a flagged citation survives human reading, the finding is
  recorded here (or as a versioned local finding), not by rewriting doctrine —
  see "Learn from outcomes without rewriting doctrine" in
  `OPERATIONALIZATION.md`.

## Method

`doctrine/tools/entailment_eval.py`:

1. Enumerates every `(concept, claim, source_support)` pair from
   `doctrine/concepts/*.yaml` (deterministic file and record order).
2. Resolves each locator (`relative/chapter/path.md :: Exact Converted
   Heading`) to the text under that heading up to the next heading of the same
   or a higher level, using the same heading normalization as
   `doctrine/tools/validate_doctrine.py`. Resolution failures are recorded as
   findings (`verdict: resolution_failed`), never crashes.
3. Sends one prompt per pair — section text (truncated at 24000 characters,
   with truncation recorded), concept claim, contribution sentence, and
   relationship type with its meaning — to the local OpenAI-compatible
   endpoint (`http://localhost:8081/v1`, alias `qwen3.6-35b-a3b`,
   server-default sampler, `max_tokens` 4096, requests strictly sequential).
4. Parses a strict JSON verdict (`supported`, `partially_supported`,
   `not_supported`, `contradicted`) from `message.content` only (the model's
   `reasoning_content` is ignored). One retry on parse failure, then
   `unparseable` with the raw content; one retry on transport failure, then
   `transport_error`.
5. Appends one JSON line per judgment to `results.jsonl` with full provenance:
   concept, source, locator, chapter sha256, truncation, contribution,
   relationship, verdict, evidence quote, rationale, model id, request
   parameters, endpoint, latency, schema version `entailment-eval/1`, and a
   deterministic key = sha256 over (concept_id, locator, contribution,
   chapter_sha256). The key changes when a chapter file changes, so edited
   chapters are automatically re-screened.

## Run, resume, summarize

```bash
# Screen everything not yet judged (resume is the default):
python3 doctrine/tools/entailment_eval.py

# Bounded pilot filtered by source or concept:
python3 doctrine/tools/entailment_eval.py --source SRC-APOSD --limit 4

# Enumerate, resolve, and build prompts without model calls:
python3 doctrine/tools/entailment_eval.py --dry-run

# Force re-judging of already-recorded keys:
python3 doctrine/tools/entailment_eval.py --redo --concept universal-no-change-option

# Rebuild summary.md and print verdict counts (no judging):
python3 doctrine/tools/entailment_eval.py --summarize
```

Results append to `results.jsonl`; re-judged keys append new lines and the
summary keeps the last record per key. `summary.md` is generated
deterministically from `results.jsonl` — do not edit it by hand.

## Known limits

- **Single-model judgment.** One local model, one prompt, one sample. Verdicts
  carry that model's failure modes; disagreement with a human reading is
  expected and is why this is screening only.
- **Truncation.** Sections longer than 24000 characters are truncated (the
  record says so); support appearing late in a long section can be missed.
- **Section-scope assumption.** Only the text under the cited heading is
  judged. The citation contract says locators support audit and retrieval,
  "not claims that every sentence in a chapter endorses the derived rule";
  support supplied by surrounding chapter context can yield a false
  `not_supported`.
- **Paraphrase gap.** Claims and contributions are deliberately paraphrased
  doctrine, not quotes; a literal-minded judge may under-credit legitimate
  paraphrase or over-credit keyword overlap.
- **Relationship semantics.** `tension` and `historical_precursor` citations
  ask the model to confirm a characterization, not endorsement; misreading the
  relationship's meaning is a rival explanation for any flagged verdict.
