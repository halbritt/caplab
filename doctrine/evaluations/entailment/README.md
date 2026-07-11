# Claim-to-source entailment screening

Model-judged screening of whether each doctrine concept's cited source section
actually supports its claimed contribution. This covers the first property
listed under "Complete human evaluations before accepting the retriever" in
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
  always include model error, incomplete context, and the section-scope
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
   findings (`verdict: resolution_failed`), never crashes. Repeated normalized
   headings require an explicit `@@ occurrence=N` selector.
3. Sections above 24000 characters are recorded as
   `insufficient_context` and are not sent to a model. Complete shorter
   sections, the concept claim, contribution sentence, and relationship type
   with its meaning are sent to the local OpenAI-compatible
   endpoint (`http://localhost:8081/v1`, alias `qwen3.6-35b-a3b`,
   server-default sampler, `max_tokens` 4096, requests strictly sequential).
4. Parses a strict JSON verdict (`supported`, `partially_supported`,
   `not_supported`, `contradicted`) from `message.content` only (the model's
   `reasoning_content` is ignored). One retry on parse failure, then
   `unparseable` with the raw content; one retry on transport failure, then
   `transport_error`. A non-empty evidence quote that is not present in the
   complete cited section becomes `quote_not_found` rather than support.
5. Appends one JSON line per judgment to `results.jsonl` with full provenance:
   concept, source, locator, chapter and section sha256, contribution,
   relationship, verdict, evidence quote, rationale, model id, request
   parameters, endpoint, prompt version, latency, schema version
   `entailment-eval/2`, and a deterministic key over the complete judgment
   target and judge configuration. The key binds claim, relationship,
   contribution, chapter and section identity, prompt version, requested
   model, served model identifier, endpoint, token limit, and sampler
   overrides. Changing any of those
   creates a distinct judgment instead of silently reusing a stale result.

## Human audits

`human-audit.jsonl` records human review of screening results (one JSON line
per audit, schema `entailment-human-audit/1`: `key`, `concept_id`, `locator`,
`finding` ∈ {`citation-holds`, `citation-defective`, `needs-deeper-review`},
`note`, `reviewed_by`, `reviewed_at`). Multiple audits per key are allowed;
the latest wins for display. Audits are appended by the web adjudication UI
(`doctrine/tools/adjudication_server.py`, see
[`../gold/README.md`](../gold/README.md)) and are findings about citations —
they do not modify doctrine, results, or the graph.

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
- **Context budget.** Sections longer than 24000 characters are not judged;
  they remain `insufficient_context` until evaluated with a complete-section
  or audited chunking strategy.
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
  `corroboration` means an additional supporting formulation and does not by
  itself claim an independent source ID; cross-source support is evaluated
  separately. This clarification is encoded in `entailment-prompt/3`, so older
  judgments are not reused under the changed prompt semantics.
