# Cross-judge screening comparison — qwen3.6:27b × GLM 5.2

Generated 2026-07-12 from the two complete `entailment-prompt/5` judge streams
in `results.jsonl` (357 citation targets each; latest record per key). Both
verdict sets are model observations; agreement strengthens the screening
inference, it does not verify anything.

## Agreement

283 of 357 targets (79%) received the identical verdict from both judges:

| verdict | both judges agree |
|---|---:|
| supported | 270 |
| partially_supported | 8 |
| not_supported | 1 |
| quote_not_found | 3 |
| insufficient_context | 1 |

The 270 double-supported citations are the corpus's hardened core: two
architecturally unrelated judges (a local dense Qwen and Zhipu's GLM), each
reading the full map-bounded section, independently found the doctrine's
characterization supported.

## Priority audit queue

1. **Both judges hard-flag (1):**
   - `go-explicit-contextual-errors` :: Efficient Go "How to Wrap Errors?" —
     the only citation in the corpus both judges reject.

2. **One judge hard-flags, the other supports (6):**
   - `domain-anticorruption-layer` :: DDD "FACADES" — GLM contradicted
   - `implementation-duplication-as-evidence` :: CC "7.1 Valid Reasons to
     Create a Routine" — GLM contradicted
   - `agent-conduct-authority-bounded-action` :: CC "Boss-Readiness Test" —
     GLM not_supported
   - `architecture-metrics-as-signals` :: FSA "They aren't physics" — GLM
     not_supported
   - `architecture-distribution-readiness` :: CA "THE DECOUPLING FALLACY" —
     qwen not_supported
   - `legacy-unprotected-enabling-edit` :: WELC "Hyperaware Editing" — qwen
     not_supported (this citation carries a human-audited 2026-07-12
     rewording; the split verdict suggests a borderline paraphrase, not a
     regression)

3. **Both judges quote_not_found (3):** paraphrase suspects where neither
   judge produced a verifiable quote.

4. **Gradation disagreements (68):** supported ↔ partially_supported splits.
   Low priority; they mark citations whose support is real but arguable in
   strength, and are candidates for eventual confidence annotations rather
   than bench sessions.

## Reading

Screening precision after the section-map and quote-verification fixes is
high enough that the entire two-judge hard-flag surface for 357 citations is
seven items. The remaining risk the gold queue must carry is recall: neither
judge audits what the doctrine failed to cite.


## Addendum — SRC-RI and SRC-UT campaign citations (2026-07-13)

Both judges screened the 123 citations added by the Release It! / Unit
Testing extraction campaign under `entailment-prompt/5`:

| | qwen3.6:27b | GLM 5.2 |
|---|---:|---:|
| supported | 108 | 109 |
| partially_supported | 1 | 5 |
| quote_not_found | 14 | 9 |
| not_supported / contradicted | **0** | **0** |

100/123 exact agreement (97 double-supported); **no citation received a
hard flag from either judge** — against 14 hard flags in the original
corpus's first screening. The campaign enforced section-scoped
contributions and map-verified locators at extraction time, which is
where that difference comes from. The 21 distinct quote_not_found
targets are paraphrase suspects for light bench audit; the remaining
disagreements are gradations.

## Addendum — six-book campaign citations (2026-07-12)

Both judges screened the 94 citations added from SRC-100GO, SRC-CIG,
SRC-DDIA2, SRC-SEAG, SRC-APWP, and SRC-ADPCH3 under
`entailment-prompt/5`:

| verdict | qwen3.6:27b | GLM 5.2 |
|---|---:|---:|
| supported | 83 | 86 |
| partially_supported | 1 | 2 |
| not_supported | 0 | 1 |
| insufficient_context | 1 | 1 |
| quote_not_found | 9 | 4 |

83/94 targets received the same verdict, including 80 double-supported
citations, two double-`quote_not_found` citations, and one shared
`insufficient_context` result. Neither stream had a contradiction, parse
failure, transport failure, or locator-resolution failure.

GLM issued the campaign's only hard flag on
`architecture-distribution-readiness` in DDIA2, while qwen graded the same
citation `partially_supported`. The frontier pre-pass found a real scoping
defect: the cited section supplies the drivers for distribution, but the
registered contribution also attributes failure, latency, consistency, and
operational costs that occur after the section boundary. That model
recommendation remains queued for human adjudication.

The judges produced 13 quote failures across 11 distinct targets, with two
targets flagged by both. Section-level frontier review classified those
quote failures as mechanical artifacts caused by stitched spans, omitted
list items, Markdown normalization, or OCR/conversion spelling. The shared
batch-processing `insufficient_context` result was the deterministic
60,000-character context gate on a resolvable 86,539-character chapter
section; its cited support occurs near the start. The only remaining
disagreement was a supported-versus-partially-supported gradation.
