# Converged Recommendation

The corpus should be used as an evidence-governed judgment library, not as a
global style guide and not as one prompt containing every book.

The completed library supplies the required layers:

- 141 canonical Concept Records with applicability, evidence, preservation,
  failure, routing, and exact chapter-heading provenance;
- 25 preserved conflicts with evidence-based selection rules;
- 20 deterministic decision procedures, 40 operational prohibitions, 38
  costed specialist techniques, role doctrine, context lenses, rubrics, and
  authority/change/evidence models;
- a repository-native semantic graph connecting 170 nodes through 467 source
  formulations and 237 typed, provenance-bearing edges, plus 363 explicitly
  non-semantic routing links;
- selective role, task, language, risk, and repository-signal routing.

The operational unit is the Concept Record plus its graph neighborhood and any
activated conflict—not a chapter summary or a newly invented guidance-card
layer. A retriever should begin with `routing-index.yaml`, apply exclusions and
prerequisites, load proof obligations and conflicts before transformations, and
retain formulation IDs, source-attributed contributions, and exact locators in
the returned evidence packet.

The graph-backed evidence-packet assembler is now implemented as an
experimental runtime boundary. Its compact `evidence-packet/2` output uses
controlled role and task vocabularies, typed evidence, explicit obligations,
prerequisite closure, a selection budget, content identities, and exact
claim-level provenance. It:

1. selects doctrine activated by the question, role, task, repository signals,
   language, risk, and explicit lenses, then uses typed evidence only to update
   obligation status;
2. surfaces activated conflict IDs and their registry rather than silently
   selecting a position;
3. carries the role's authority ceiling and constraints without promoting a
   packet into authorization;
4. exposes missing evidence obligations and budget exclusions so a consuming
   agent can gather evidence, abstain, or escalate;
5. returns exact claim-level source contributions and chapter provenance.

The assembler does not itself diagnose a repository, choose a conflict
position, recommend work, or execute a change. Those are downstream agent
behaviors constrained by the packet, procedures, assertion contract, and
authority model.

The runtime schemas, packet contract, and deterministic authority and routing
canaries establish structural behavior. They do not prove natural-language
entailment or retrieval quality. Human-adjudicated calibration remains the next
acceptance gate; pending candidates must not be represented as accepted gold
results.

Repository contracts and current runtime facts remain higher-precedence than
every result produced from this library. Retrieval selects potentially relevant
doctrine; it never creates authority to act.
