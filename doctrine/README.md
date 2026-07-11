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
| `universal-doctrine.md` | Compact cross-role foundation | every engineering task |
| `role-doctrine.md` | Role-specific defaults, permissions, and stop rules | agent role |
| `concepts/*.yaml` | Canonical operational concept records | concept ID, task, signal |
| `techniques/*.yaml` | Costed architecture/domain techniques with activation and reversal rules | demonstrated force/technique ID |
| `graph/index.yaml` | Canonical doctrine graph entry point and relation vocabulary | node/edge/source formulation |
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
| `runtime/*.schema.json` | Portable evidence-packet, assertion, receipt, and dependency contracts | runtime artifact type |
| `evaluations/` | Deterministic authority and dependency-impact canaries | scenario/expected assertion boundary |
| `CONVERGED_RECOMMENDATION.md` | Current synthesis and next accepted implementation target | downstream product decision |
| `OPERATIONALIZATION.md` | Retrieval, evaluation, receipt, and outcome-learning design constraints | downstream runtime work |

The files under `_work/extractions/` are audit notes from the full-corpus
reading pass; `_work/canonicalization/` records every merge, distinction, and
source-formulation decision. They are evidence scaffolding, not runtime doctrine
or default retrieval inputs for agents.

The graph under `graph/` is a semantic projection of the same doctrine. It does
not replace concept records or chapter evidence. Canonical nodes converge shared
ideas; source formulations retain each source's conditions and vocabulary; typed
edges make prerequisites, refinements, conflicts, protections, and tradeoffs
explicit.

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
- Confidence means: `universal` for a highly portable rule with broad support;
  `strong` for reliable support within stated constraints; `contextual` for a
  rule that depends materially on repository conditions; `weak` for a useful
  hypothesis requiring local confirmation; and `contested` for an unresolved
  disagreement.

## Retrieval contract

Retrievers should begin with `routing-index.yaml`, load the universal concepts
marked `core`, and add only records activated by the current role, task,
repository signals, language, and risk class. Exclusion conditions and
prerequisites are hard filters. A specialist record must not be loaded merely
because it shares a keyword with the task.

When the repository does not supply the evidence required by a record, the
agent should gather evidence, narrow the claim, propose an experiment, or stop.
It should not substitute confidence or source prestige for missing evidence.

### Assembling an evidence packet

`tools/assemble_packet.py` implements this retrieval contract as a
deterministic CLI. It applies the routing index `selection_order` for a role,
task, question, and optional repository signals, languages, and risk class,
then emits a packet conforming to `runtime/evidence-packet.schema.json`:

```bash
python3 doctrine/tools/assemble_packet.py \
  --role legacy-code-agent --task legacy-change \
  --question "Can we safely extract the billing calculation?" \
  --signal "no tests around target" --risk regression \
  --out packet.json --render markdown
```

Interpretation notes (the assembler cannot inspect a target repository):

- A route prerequisite naming another concept record is pulled into the
  activated set; every other prerequisite and each `required_evidence` item is
  reported in `missing_evidence` as `<item> — required by <concept-id>` unless
  a provided `--signal` matches it. Missing evidence never drops always-load
  or role/task-baseline concepts; `exclude_when` matches always do, and every
  dropped candidate is recorded in `excluded_candidates` with its reason.
- `corpus_version` is derived from repository data only:
  the traceability `generated_at_utc` date plus a sha256 digest over the
  sorted `source_sha256` values in `sources.yaml`. Identical invocations
  produce byte-identical packets; the packet is retrieved guidance and does
  not create authority to act.
