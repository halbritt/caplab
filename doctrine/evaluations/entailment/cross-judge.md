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
