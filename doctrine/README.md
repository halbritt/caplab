# Evidence-Governed Software-Engineering Doctrine

This directory is a selectively retrievable doctrinal library for autonomous
software-engineering agents. It is derived from the complete corpus listed in
[`sources.yaml`](sources.yaml), but it is organized by engineering decision,
role, context, evidence, and authority rather than by book.

## Governing precedence

Apply guidance in this order:

1. explicit human authorization and stop conditions;
2. accepted repository contracts, tests, architectural decisions, and current
   runtime facts;
3. task-specific evidence from the repository and its history;
4. context- and language-specific doctrine from this library;
5. universal doctrine from this library;
6. generic source advice.

A lower-precedence rule cannot override a higher-precedence fact. A doctrine
record can justify a question, investigation, proposal, or bounded action; it
cannot create authority the agent was not granted.

## Assertion discipline

Every assessment and execution record should distinguish:

- **observation**: directly supported by inspected evidence;
- **inference**: an explanation that fits observations but may have rivals;
- **recommendation**: a preferred response with costs and alternatives;
- **decision**: a selected response within an identified authority boundary;
- **verification**: evidence that the selected response had its intended effect;
- **acceptance**: an authorized party's judgment that the outcome is sufficient.

Do not turn inference into observation, recommendation into authorization, or
verification into acceptance.

## Library map

| Artifact | Purpose | Primary retrieval key |
|---|---|---|
| `corpus-map.yaml` | Source contributions, assumptions, limitations, and tensions | source ID |
| `bibliography.json` | Canonical titles, editions, creator roles, and field-level evidence | source ID |
| `chapter-coverage.yaml` | Exact chapter inventory, disposition, and content hashes | chapter/source ID |
| `universal-doctrine.md` | Compact cross-role foundation | every engineering task |
| `role-doctrine.md` | Role-specific defaults, permissions, and stop rules | agent role |
| `concepts/*.yaml` | Canonical operational concept records | concept ID, task, signal |
| `techniques/*.yaml` | Costed architecture/domain techniques with activation and reversal rules | demonstrated force/technique ID |
| `graph/index.yaml` | Provenance-bearing semantic doctrine graph and relation vocabulary | node/edge/source formulation |
| `routing-graph/links.yaml` | Generated non-semantic co-retrieval adjacency | concept ID |
| `procedures.yaml` | Deterministic decision procedures | task/procedure ID |
| `negative-doctrine.yaml` | High-confidence prohibitions with trigger thresholds | risk/failure signal |
| `conflicts.yaml` | Preserved disagreements and selection rules | conflict ID/context |
| `change-types.yaml` | Semantic and authority boundaries among change types | intended change |
| `evidence-taxonomy.yaml` | What evidence classes can and cannot establish | available evidence |
| `authority-model.yaml` | Allowed transitions from observation through acceptance | authority level |
| `routing-index.yaml` | Compact selective-retrieval index | role/task/repository signal |
| `context-lenses.yaml` | Conditional refinements for lifecycle, archetype, risk, and language | repository context |
| `rubrics.md` | Scored evaluation rubrics | artifact under review |
| `checklists.md` | Readiness, preservation, evidence, and escalation gates | execution phase |
| `traceability.yaml` | Coverage and source-support audit | concept/source/procedure ID |
| `runtime/*.schema.json` | Portable evidence-record, packet, assertion, receipt, and dependency contracts | runtime artifact type |
| `evaluations/` | Authority/routing canaries, entailment screening, and a pending-human calibration queue | scenario/evaluation axis |
| `CONVERGED_RECOMMENDATION.md` | Current synthesis and next accepted implementation target | downstream product decision |
| `OPERATIONALIZATION.md` | Retrieval, evaluation, receipt, and outcome-learning design constraints | downstream runtime work |

The files under `_work/extractions/` are audit notes from the full-corpus
reading pass; `_work/canonicalization/` records every merge, distinction, and
source-formulation decision. They are evidence scaffolding, not runtime doctrine
or default retrieval inputs for agents.

The graph under `graph/` is a semantic projection of the same doctrine. It does
not replace concept records or chapter evidence. Canonical nodes converge shared
ideas; formulations preserve the source-attributed contribution, exact locator,
and relationship to one or more canonical nodes. Curated formulations may carry
source-specific conditions and caveats. Generated source-support formulations
instead label canonical mapping applicability and policy explicitly in
`context_basis`, so canonical conditions are not attributed to an author.
Typed edges make prerequisites, refinements, conflicts, protections, and
tradeoffs explicit. Generated keyword and routing adjacency lives under
`routing-graph/` and declares `semantic: false`; it must not be cited as source
support.

## Record and citation contract

- Concept IDs are stable, lowercase, hyphenated identifiers whose namespace
  identifies the operational family (for example,
  `universal-evidence-before-intervention` or `python-protocol-conformance`).
- Procedure IDs use the `proc-` prefix; conflicts use `conflict-`; prohibitions
  use `prohibit-`; evidence classes use `evidence-`.
- `source_support` entries cite a source ID from `sources.yaml`, a relative
  chapter path, and an exact converted heading. Locators support
  audit and retrieval; they are not claims that every sentence in a chapter
  endorses the derived rule.
- Claims are paraphrased. The doctrinal library does not reproduce the source
  corpus or depend on source wording.
- Confidence means: `universal` for a highly portable rule supported by at
  least two distinct source IDs (an enforced release-gate threshold);
  `strong` for reliable support within stated constraints; `contextual` for a
  rule that depends materially on repository conditions; `weak` for a useful
  hypothesis requiring local confirmation; and `contested` for an unresolved
  disagreement.

## Retrieval contract

Retrievers should begin with `routing-index.yaml`, load its explicit six-concept
always-load safety kernel, and add records activated by the question, current
role, task, repository signals, language, risk class, or explicit lens.
Exclusions and language applicability are hard filters. Concept prerequisites
close the selected set; evidence-shaped prerequisites become obligations rather
than silently filtering out guidance. A specialist record must not be loaded
merely because it shares a keyword with the task.

When the repository does not supply the evidence required by a record, the
agent should gather evidence, narrow the claim, propose an experiment, or stop.
It should not substitute confidence or source prestige for missing evidence.

### Assembling an evidence packet

`tools/assemble_packet.py` implements this retrieval contract as a
deterministic CLI. It resolves canonical role and task vocabularies, applies a
question-sensitive and prerequisite-closed selection budget, and emits a
content-addressed `evidence-packet/2`:

```bash
python3 doctrine/tools/assemble_packet.py \
  --role legacy-code-agent --task legacy-change \
  --question "Can we safely extract the billing calculation?" \
  --signal "no tests around target" --risk regression \
  --out packet.json --render markdown
```

Interpretation notes (the assembler cannot inspect a target repository):

- A route prerequisite naming another concept record is pulled into the
  activated set. Other prerequisites and required evidence become explicit
  obligations. Signals can activate records but cannot satisfy obligations;
  only typed `evidence-record/1` inputs can do that.
- The default compact packet retains the six-concept safety kernel and all
  activated operational layers without repeating derived audit views. Use
  `--detail full` for formulations, flattened missing-evidence text, and source
  locator inventories.
- The default 5,000-unit budget is a relative concept-selection cost, not a
  byte, word, or tokenizer-token limit. Identical inputs produce byte-identical
  packets; changes to doctrine or retrieval logic change their content IDs.
- A packet is retrieved guidance. It never creates authority to act.

## Release validation

Run `make doctrine-check` to verify source binaries and generated provenance,
the exact 331-chapter coverage manifest, unambiguous source locators, canonical
bibliography, routing freshness, semantic graph projection, graph fragments,
conflict reachability, pending-human calibration-queue freshness, and doctrinal
cross-references. `make check` combines that gate with the converter integrity
check and the test suite. Queue coverage is scaffolding, not evidence that any
candidate has been adjudicated or accepted.
