# Claim-to-source entailment screening

Model-judged screening of whether each doctrine concept's cited source section
actually supports its claimed contribution. The concept graph, section maps,
and corpus are read from the exact Pincite release; results and human audits
remain under CAPLAB custody.

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
  and results must never modify Pincite doctrine sources, concept records, or
  the graph. When a flagged citation survives human reading, the finding is
  recorded here rather than rewriting Pincite.

## Method

`doctrine/tools/entailment_eval.py`:

1. Enumerates every `(concept, claim, source_support)` pair from
   `$PINCITE_RELEASE_HOME/doctrine/concepts/*.yaml` (deterministic file and
   record order).
2. Resolves each locator (`relative/chapter/path.md :: Exact Converted
   Heading`) to the text under that heading up to the next heading of the same
   or a higher level, using the same heading normalization as
   Pincite's locator contract. Where the Pincite section maps cover the
   chapter, headings
   classified `embedded` — conversion-flattened callouts, captions, and
   subsection children — do not terminate the section, so the full logical
   section is judged; without a current map the plain level rule applies.
   Resolution failures are recorded as
   findings (`verdict: resolution_failed`), never crashes. Repeated normalized
   headings require an explicit `@@ occurrence=N` selector.
3. Sections above 60000 characters are recorded as
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

## Frontier second opinions

`frontier-review.jsonl` records second-opinion reviews of flagged records by a
frontier model (reviewer `kind: model`, one JSON line per review, schema
`frontier-review/1`: `key`, `concept_id`, `finding` ∈ {`citation-holds`,
`citation-defective`, `needs-deeper-review`}, `confidence`, `rationale`,
`evidence_quote`, optional `proposed_fix` {`relationship`, `contribution`},
`local_verdict_assessment` ∈ {`correct`, `overstated`, `artifact`},
`reviewer`, `reviewed_at`). Like the local verdicts these are **model
observations**: the adjudication bench shows the latest per key beside the
local screening verdict, but a flag remains pending until a human records a
finding in `human-audit.jsonl`. Frontier reviews must never be copied into
human audits unread.

## Run, resume, summarize

```bash
# Screen everything not yet judged (resume is the default):
python3 doctrine/tools/entailment_eval.py \
  --pincite-root "$PINCITE_RELEASE_HOME"

# Bounded pilot filtered by source or concept:
python3 doctrine/tools/entailment_eval.py \
  --pincite-root "$PINCITE_RELEASE_HOME" \
  --source SRC-APOSD --limit 4

# Enumerate, resolve, and build prompts without model calls:
python3 doctrine/tools/entailment_eval.py --dry-run

# Force re-judging of already-recorded keys:
python3 doctrine/tools/entailment_eval.py --redo --concept universal-no-change-option

# Judge with a hosted model (bearer key read from the named env var; only the
# variable NAME enters provenance). Record keys bind the judge, so verdicts
# from different judges coexist and cross-judge disagreement is comparable:
python3 doctrine/tools/entailment_eval.py \
  --endpoint https://openrouter.ai/api/v1 --model z-ai/glm-5.2 \
  --api-key-env OPENROUTER_API_KEY --max-tokens 8192

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
  `entailment-prompt/4` changed judge semantics again without changing the
  prompt text: evidence-quote verification now normalizes conversion and
  typography artifacts (PDF line-break hyphenation, markdown emphasis, inline
  span anchors, curly quotes) and treats an ellipsis in a quote as an elision
  whose fragments are checked independently — under `/3` these produced false
  `quote_not_found` verdicts (14 of 17 observed cases). Section bounds are
  additionally map-aware (see Method), and the section identity in each
  record's key (`section_sha256`) changes wherever the maps widen a section,
  so pre-map judgments are not reused for re-bounded sections.
  `entailment-prompt/5` replaced quote normalization with lowercase
  alphanumeric squashing on both sides (robust to hyphenation gluing,
  mid-word small-caps markup, heading markers, and typography variants) and
  added `[...]`-style elision fragments with a 10-character minimum: judged
  against hosted-judge output, `/4` produced 22 of 28 (GLM 5.2) and 16 of 20
  (qwen 27B) false `quote_not_found` verdicts that `/5` verifies correctly,
  while genuine paraphrases stay flagged.
