The highest-leverage next step is to turn the corpus from a knowledge base into a judgment system—one that produces contextual, evidence-backed engineering decisions.

```text
source spans → doctrine → guidance units → evidence packets → skills/actions
                    ↑             ↓               ↓
              contradiction map   evaluations ← outcome traces
```

### 1. Create “guidance units”

These should be smaller and more operational than chapters, but richer than extracted claims:

```yaml
id: legacy-code.characterization-test
problem: Safely change behavior that is not understood
recommendation: Establish characterization tests before restructuring
applies_when:
  - existing behavior must be preserved
counterindications:
  - behavior is intentionally being replaced
tradeoffs:
  - preserves undocumented defects
failure_modes:
  - tests capture implementation rather than observable behavior
evidence:
  - source_span_id: wewlc-ch02-span-184
derivation: extracted | synthesized
```

Keep three layers visibly separate:

- Authorial doctrine: what a source actually says.
- Extracted interpretation: structured claims derived from it.
- Cross-source synthesis: conclusions produced by comparing sources.

That separation prevents synthesis from quietly becoming “what the book said.”

### 2. Preserve disagreement instead of manufacturing consensus

The graph becomes unusually valuable when it records:

- corroboration;
- contradiction;
- different assumptions;
- advice that applies at different scales;
- older guidance superseded by changed tooling;
- the same term used with different meanings.

A useful answer should sometimes return:

> Fowler recommends X under these conditions; Feathers gives a safer sequence for legacy systems; Ousterhout would object because Y.

That is more useful than a blended paragraph representing nobody’s actual position.

### 3. Build evidence packets, not generic RAG results

Retrieval should assemble a compact packet containing:

- the strongest primary evidence;
- corroborating evidence;
- the best dissenting evidence;
- applicability and counterindication notes;
- exact chapter/span provenance;
- a confidence or coverage statement.

Use lexical, vector, and graph retrieval together. The graph should expand or constrain candidates; graph centrality should never be treated as truth.

### 4. Build evaluations before many downstream products

Create scenario-based benchmarks such as:

- “How should I introduce tests around this legacy method?”
- “Is this service boundary actually a bounded context?”
- “Which architecture characteristic is driving this decision?”
- “What would these authors disagree about?”
- “There is insufficient evidence—should the system abstain?”

Measure:

- claim-to-source entailment;
- citation correctness;
- applicability;
- contradiction handling;
- actionable specificity;
- appropriate abstention;
- preservation of code examples and qualifications.

Each guidance unit can generate positive, negative, and boundary-case scenarios.

### 5. Package thin operational skills

Avoid enormous skills containing condensed books. Make skills that retrieve guidance units at runtime:

- architecture review;
- legacy-code intervention;
- refactoring sequencing;
- domain-model critique;
- performance investigation;
- code-construction review;
- design-simplicity review.

A skill should encode the workflow and output contract. The corpus supplies the knowledge. This keeps prompts small and lets provenance survive into the final recommendation.

### 6. Add decision receipts

Every substantial recommendation should be able to emit a durable receipt:

```text
Decision
Context and assumptions
Recommended action
Rejected alternatives
Supporting doctrine
Conflicting doctrine
Source spans
Confidence and missing evidence
```

These can become ADR inputs, review comments, issue descriptions, or audit artifacts.

### 7. Learn from use without rewriting history

Capture which evidence packets were retrieved, accepted, rejected, or useful in real engineering work. Outcomes can adjust retrieval and applicability rankings, but should never modify the source doctrine.

This creates a useful feedback loop:

- doctrine remains immutable;
- synthesis remains versioned;
- operational confidence evolves with evidence.

### Recommended first slice

I would choose one task—probably architecture review or changing legacy code—and build:

1. Thirty hand-audited guidance units.
2. A contradiction/applicability map across three books.
3. Fifty scenario evaluations.
4. A minimal hybrid evidence-packet retriever.
5. One thin operational skill that emits decision receipts.

That slice will reveal whether the ontology, retrieval, and provenance model work before expanding across all 331 chapters.

The traps are building a chat interface first, fine-tuning prematurely, producing one grand “unified doctrine,” or translating every sentence into an automated rule. The corpus becomes maximally useful when it can reliably explain not only what to do, but when the advice applies, what disagrees with it, and exactly where the judgment came from.

The ADHD skill’s full protocol requires isolated parallel branches, which were unavailable under the current delegation constraint; this is the direct converged recommendation rather than a full parallel exploration.
