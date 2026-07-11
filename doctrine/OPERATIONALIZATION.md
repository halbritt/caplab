# Operationalizing the doctrine corpus

Status: post-extraction design note for downstream retrieval and evaluation work.

## Conclusion

The next useful artifact is a judgment system that can turn a repository problem
into a bounded recommendation, show the evidence and disagreement behind that
recommendation, and state when the available evidence is insufficient.

The current doctrine contract already defines most of the knowledge model needed
for that system:

- the concept schema requires applicability, evidence requirements,
  preservation boundaries, failure modes, conflicts, source support, and
  routing metadata;
- validated source formulations remain separate from canonical graph nodes;
- the graph relation vocabulary distinguishes direct support, corroboration,
  refinement, inference, historical relationships, and tension;
- the authority model, procedures, rubrics, and checklists constrain how
  doctrine becomes action.

Do not create a parallel layer of generic “guidance cards.” Treat the concept
record as the canonical unit of judgment and extend the system around it.

```text
source chapter sections -> formulations -> concepts and conflicts -> evidence packet
                                                                  -> operational skill
                                                                  -> decision receipt
                                                                  -> evaluated outcome
```

Source text and source formulations remain provenance-stable. Concepts, routing,
evaluations, and operational confidence can evolve as separately versioned
derived artifacts.

## Readiness gate

Operational work should begin only after:

1. `python3 doctrine/tools/validate_doctrine.py` passes;
2. concept, formulation, edge, conflict, procedure, and source IDs are stable;
3. every derived claim and graph edge has resolvable provenance;
4. the source registry and traceability ledger record corpus identity, chapter
   counts, extraction checksums, and schema versions;
5. unresolved conflicts and known coverage gaps are explicit.

The completed library passes this gate: 331/331 chapter files are covered, all
141 Concept Records project to the provenance graph, and the doctrine validator
checks concepts, conflicts, procedures, routing, techniques, exact source
headings, graph references, and extraction checksums. Downstream retrieval still
needs its own scenario acceptance evidence before it should guide execution.

## Recommended sequence

### 1. Build evaluations before the retriever

Create a scenario corpus that tests whether the doctrine changes engineering
judgment, not whether a model can repeat a concept label. Each scenario should
contain:

- a concrete repository situation and granted authority;
- the evidence available to the agent;
- the evidence deliberately withheld or made ambiguous;
- concepts and conflicts expected to activate;
- acceptable recommendations, required caveats, and prohibited actions;
- source formulations that can support the answer;
- an abstain or escalate condition where appropriate.

Include positive cases, counterexamples, misleading keyword matches, conflicting
doctrine, insufficient evidence, and authority-boundary cases. Initial scenario
families should follow the existing role surfaces: architecture, implementation,
review, refactoring, repair, legacy change, and performance.

Evaluate at least these properties:

- claim-to-source entailment;
- citation and locator correctness;
- applicability and exclusion handling;
- conflict detection and selection-rule use;
- distinction among observation, inference, recommendation, and decision;
- appropriate abstention or escalation;
- actionable specificity without unauthorized action.

These evaluations become the acceptance tests for retrieval, skills, and future
schema changes.

### 2. Retrieve evidence packets, not chunks

The routing index is generated and validated. A future runtime retriever should
begin with it and the graph views, then assemble the smallest packet that can
support a decision. A packet should contain:

- the activated concept and its prerequisites;
- primary source formulations;
- corroborating formulations where they add confidence;
- relevant conflict records or dissenting formulations;
- applicability, exclusions, preservation boundaries, and required evidence;
- missing evidence and the action it blocks;
- exact source locators and corpus version.

Lexical, vector, and graph retrieval may all nominate candidates. Routing rules,
prerequisites, exclusions, and authority constraints decide what survives.
Graph centrality and embedding similarity are candidate signals, not measures of
truth.

The retriever should be able to explain why each record was included and why a
plausible alternative was excluded. That explanation is part of the retrieval
contract and should be covered by evaluations.

### 3. Preserve disagreement

Do not collapse compatible-sounding advice into a single consensus paragraph.
A useful packet may need to say that one source favors a transformation under
one set of assumptions while another source warns against it under different
conditions.

For each conflict, preserve:

- the competing claims;
- whether the difference is contextual, terminological, historical,
  methodological, or substantive;
- the evidence conditions that select a side;
- the cases where the corpus does not resolve the disagreement.

Counterfactual retrieval should be a first-class operation: “What doctrine
argues against this recommendation, and under what conditions would it win?”

### 4. Package thin operational skills

Skills should encode a workflow and output contract, then retrieve doctrine at
runtime. They should not embed condensed copies of the books or load the entire
doctrine library into every prompt.

Initial skill candidates are:

- architecture assessment;
- legacy-code intervention;
- refactoring campaign selection;
- repair diagnosis and planning;
- performance investigation;
- implementation or code-review guidance.

Each skill should identify its authority ceiling, gather repository evidence,
request an evidence packet, apply the relevant procedure and rubric, and emit a
decision receipt. Repository contracts and current runtime facts retain
precedence over corpus doctrine.

### 5. Emit decision receipts

Every material recommendation should produce a durable receipt containing:

- the decision question and authority boundary;
- observations and unresolved uncertainty;
- activated concepts, procedures, and conflicts;
- the recommendation and its applicability conditions;
- alternatives considered, including no change where relevant;
- rejected alternatives and the evidence used to reject them;
- preservation boundaries, verification gates, and stop conditions;
- exact formulation and source locators;
- corpus, schema, and retriever versions.

A receipt can feed an ADR, issue, review comment, plan, or handoff. It also gives
the evaluation system something inspectable to score.

### 6. Learn from outcomes without rewriting doctrine

Record which packets were retrieved, which recommendations were accepted or
rejected, what evidence changed the decision, and what happened after execution.
Use those traces to improve routing and evaluation coverage.

Outcome data must not silently alter source formulations or canonical claims.
When experience challenges doctrine, add a versioned local finding, conflict, or
applicability refinement with its own evidence. Preserve the historical source
claim.

## First pilot

Choose one task with observable outcomes. Architecture assessment or safe
legacy-code change are good candidates because the current doctrine already has
explicit evidence, authority, conflict, and verification requirements for both.

Build the pilot around:

1. a hand-audited subset of concept and conflict records;
2. a scenario suite containing ordinary, negative, and ambiguous cases;
3. one hybrid evidence-packet assembler;
4. one thin operational skill;
5. decision receipts retained as evaluation artifacts.

The pilot succeeds when it can distinguish action from no action, surface the
relevant disagreement, cite the correct source formulations, and stop when the
repository lacks the evidence or authority required by the doctrine. Expand to
other roles only after those properties hold.

## Present foundation and deferred runtime state

The repository already contains the portable evaluation and runtime contracts:

```text
doctrine/
  evaluations/
    fixtures/
    scenario.schema.json
    result.schema.json
  runtime/
    assertion-artifact.schema.json
    evidence-packet.schema.json
    decision-receipt.schema.json
    dependency-manifest.schema.json
```

Outcome traces remain deferred until a retention and redaction policy is
accepted:

```text
doctrine/
  traces/
    README.md
```

Evaluation fixtures should be tracked. Runtime traces may contain repository
content or operational data and need an explicit retention and redaction policy
before they are tracked or shared.

## Traps to avoid

- A chat interface before retrieval and citation behavior pass evaluations.
- One grand synthesis that erases source conditions and disagreement.
- Fine-tuning before the evidence-packet and decision-receipt contracts are
  stable; model weights are a poor provenance surface.
- Automated lint rules derived from contextual doctrine without false-positive
  tests and repository-specific activation conditions.
- Skills that carry the whole corpus in their prompt instead of retrieving a
  bounded packet.
- Treating graph connectivity, source prestige, or repeated advice as authority.
- Feeding accepted recommendations back into canonical doctrine without a
  separate evidence and review path.

Keep source-derived text and near-verbatim spans within the repository's access
boundary. Share independently authored synthesis, metadata, and provenance only
under the applicable rights and distribution policy.
