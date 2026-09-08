# Adjacent placebo selection: prospective rule

Date: 2026-09-08. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `5aa63df`.

## Authorization before execution

Investigate CAPLAB-61's four proposed adjacency mechanisms using the current
validated Pincite release at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Read the graph README, index,
views, nodes and edges metadata and the SQLite index schema. Inspect only
identifiers, categories, relationship types and routing metadata needed to
assess candidate enumeration. Do not load source books, historical campaign
artifacts, subject outputs, archived transcripts or prior scores. No model
calls or embedding generation are authorized.

Create a bounded zero-model prototype and metadata-only receipts under
`/tmp/caplab-61-*`; preserve release commit, source paths and content hashes.
The prototype may enumerate candidate concept IDs from that pinned metadata.
It must not classify actual pairings as non-bearing or import governing records
or study evidence into CAPLAB.

After this inspection, this change may add a prospective selection procedure
under `docs/product/contracts/`, link it from `docs/product/README.md`, and
complete this record. Verify that it answers every CAPLAB-61 requirement and
that its ordering is reproducible on the inspected inputs. After verification,
append its resolution to CAPLAB-61 and mark the rule-specification item Done;
append an integration pointer to CAPLAB-70 without closing or changing its
judgment requirement. Preserve original descriptions, comments and unrelated
fields. Re-read before writing; stop that update on concurrent change.

No actual pairing acceptance, owner-time commitment, arm addition, numerical
parameter change, model spend, experiment launch, historical rewrite or
admission, reviewer ranking, placement, or external message is authorized.
Preserve `docs/designs/`, runtime code, frozen study files, services and sibling
worktrees. This authorization expires at commit. Retain bounded inspection
receipts; remove only this task's temporary doctrine working files after its
advisory receipt is recorded.

## Findings and decision

Select the [prospective rule](../product/contracts/adjacent-placebo-selection-v1.md):
same-category candidate pool, decreasing exact Jaccard overlap of the original
`routing.activate_for_tasks` sets, then exact concept ID. Retain zero-overlap
candidates with that limitation visible. Select the first semantically eligible
candidate only after every predecessor is recorded ineligible. An unresolved
predecessor blocks selection. The whole actual serving artifact must match the
claimed intervention; a concept selected inside a packet cannot certify the
packet as non-bearing.

This combines a transparent category boundary with a finer deterministic
ordering, without requiring new embeddings or observing subject behavior.
No actual pairing is selected in this turn. CAPLAB-70 retains the separate
semantic judgment and its named authority.

| Candidate mechanism | Current-source observation | Disposition |
|---|---|---|
| Same category file | 227 concepts occupy 14 artifact files. Every one of 221 non-core bearings has at least one non-core peer. | Selected as the candidate pool, with semantic adjacency still required. Category alone is coarse. |
| Semantic graph distance | `views.yaml` contains entry nodes and allowed relations, not distances. `edges.yaml` / the SQLite edges table contains 163 concept-to-concept edges touching 128 of 227 concepts; relation types include prerequisites, specialization, tension and other different meanings. | Not selected as one scalar distance: coverage is incomplete and these relations do not all mean equally close alternatives. This does not discredit the graph for its stated purpose. |
| Routing-index co-activation | Compiled routes have nine broad task families; 222 concepts share `repository-assessment`. The original task metadata contains 363 distinct strings. | Use raw-task set overlap for ordering. It is declared metadata overlap, not observed co-activation or demonstrated semantic similarity. |
| Embedding adjacency | The inspected graph/index schema provides no selected frozen embedding artifact or its model/tokenizer/vector identity. None was generated. | Not selected for v1. Its comparative discrimination and operational cost are unmeasured, not assumed inferior. |

The prototype shows positive raw-task overlap for 154 of the 221 non-core
bearings. The other 67 have only category/tie-order nominations. Excluding all
zero-overlap candidates would remove those bearings before semantic review;
this rule instead exposes the weak signal and requires the same semantic
eligibility check. No candidate may pass merely because it is first in the
metadata order. If the category has no semantically suitable candidate, report
no eligible pairing; do not silently substitute a trivial random concept.

No random-wrong arm is added. It would consume a separate assignment and
analysis population without testing the same hard discrimination. A future
floor check needs a separately justified design. CAPLAB-84 currently describes
four shakedown arms, including a real packet borrowed from another scenario
as sham. That packet is not automatically adjacent-wrong. This new rule does
not change its arm count, dose, contrast or expired authorization.

## Verification

The metadata-only prototype `/tmp/caplab-61-adjacency-probe.py` ran against the
read-only pinned SQLite index. It emitted only identifiers, categories-related
counts, routing overlap counts and source hashes; no subject outputs or actual
worlds were loaded. Reversing the full source record order reproduced every
ranking. Exact-ratio ties and zero overlap were checked on a new synthetic
catalog. Excluding every peer yielded empty lists for all 221 bearing IDs.
The inspected source files were hashed before and after execution and remained
unchanged. Receipt: `/tmp/caplab-61-adjacency-result.json`.

The prototype verifies nomination ordering, not the complete semantic review,
freeze, packet-construction or adjudication workflow. No source or test code
in CAPLAB changed, so the runtime suite was not rerun for this document and
throwaway-prototype work. Documentation links and the rule's worked selection
examples are checked separately before commit.

| CAPLAB-61 requirement | Procedure coverage |
|---|---|
| Reproducible selection, not a hand-picked favorable pair | Sections 1–2 pin complete input metadata and exact order; section 4 selects first eligible with no skipped unresolved predecessor. |
| Plausibly adjacent but non-bearing | Section 3 requires two distinct judgments and world-specific evidence; neither the category, overlap score nor missing reference code is sufficient. |
| Evaluate the four proposed mechanisms | Decision table above uses current schema and bounded metadata observations; unmeasured embedding performance remains unclaimed. |
| Deterministic rule stated at freeze | Sections 1, 2 and 5 pin source identities, exact arithmetic, tie-break, exclusions, order and decision receipts before outcomes. |
| Decide adjacent-wrong versus random-wrong | Version 1 selects adjacent-wrong only, adds no arm, and requires a separate design for any random-wrong floor check. |
| Restate consequences for arms/contrasts | Purpose section preserves CAPLAB-84's borrowed-packet sham and requires explicit serving/contrast adoption; no silent substitution or pooling. |
| Feed orthogonality and owner spot-check | Section 3 requires negative parent/reference and positive P witnesses before the CAPLAB-70 judgment; software checks do not impersonate it. |

Actual placebo difficulty, semantic eligibility, B/P witness validation and
independent acceptance remain unmeasured. CAPLAB-61 can close as a rule
specification after this audit; CAPLAB-70 remains open for actual pairings.

## Source receipts

Read-only planning snapshots: `/tmp/caplab-61-selection-current.json`,
`/tmp/caplab-61-selection-comments.json`, `/tmp/caplab-70-selection-context.json`,
and `/tmp/caplab-84-selection-context.json`. CAPLAB-61 has no comments in the
returned result. These are planning context, not admitted study evidence.
No governing records were imported into CAPLAB.

The current-source paths below are relative to the validated release's
`doctrine/` root; the commit is named in the authorization above.

| Source | SHA-256 |
|---|---|
| `graph/README.md` | `b51f8596b12415f2297bbe6dc6042ffbb4ab40d292edf90b7f919f07baaaa9ff` |
| `graph/edges.yaml` | `9a62c3950d29f08cab56809ec0523e10cb44eeda415300b3108a5165453c9f07` |
| `graph/index.yaml` | `2f9e75c2100e1d1561159cd1de8914dd9f920f1e3d4edf2d3636579d6db735e4` |
| `graph/nodes.yaml` | `845c0c966142cb48ca082b9472de3bdc3f24a5a16c3e89c3dd7a35c4163b1d21` |
| `graph/views.yaml` | `4dd3edbffdebcfa3f191fbfb5d647700d38a1c3a1e60ef2a616e9e77f79c7eb5` |
| `runtime/doctrine-index.sqlite3` | `29907d65f85a428eb530a426c47cac740ba8647ddfad89860670b001aff9c4eb` |

Prototype SHA-256: `71481111482ffe048479b6709084e4dadb081cbc3724cbd51ef60cc96bfe8560`.

## Advisory receipt

Validated release gate passed at the source commit named above. Final packet
`pkt-878f4a2e78ff9d41`, content SHA-256
`878f4a2e78ff9d416e90752ba208d91022c8be780e1739e2c2dc54f16803f6c2`, uses corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts:
`universal-repository-contract-precedence`,
`universal-evidence-before-intervention`, `universal-explicit-invariants`, and
`agent-conduct-authority-bounded-action`. They support the distinction between
metadata nomination, semantic judgment and authorized study adoption.

One typed evidence-gathering pass established the material specification,
source and authority requirements. Remaining advisory obligations are
nonmaterial to this rule-specification deliverable for the reasons below;
actual semantic pairing validation remains unclaimed.

| Concept | Missing requirements | Scope reason |
|---|---|---|
| domain-explicit-concept | expert validation; expert-recognized language or contradiction; recurring decision or behavior; scenario or prototype validating the concept; simplification of clients or invariants | No new expert-validated domain concept or actual pairing is claimed; this rule uses existing CAPLAB terms and leaves semantic judgment open. |
| domain-language-model-loop | authoritative examples; authoritative expert examples; feedback from implementation and usage; model expressed in executable behavior; terms whose meanings affect decisions | Prototype ordering is checked, but no world-specific semantic validation or longitudinal expert feedback is claimed. |
| domain-modeling-investment-gate | business differentiation and product lifespan; business-value and expert-access evidence; expert access and feedback cadence; recurring ambiguity, contradiction, or rule defect; team capacity to sustain the model | No deep domain-modeling campaign, staffing or lifespan investment decision is proposed. |
| task:repository-assessment | evidence-co-change; evidence-generated-artifacts; evidence-static-source-structure; evidence-tests; evidence-version-history | This is a bounded current-metadata/procedure assessment, not a co-change, historical, generated-runtime or whole-codebase assessment. |
| testing-deterministic-async-observation | bounded deadline and failure diagnostics; observable completion criterion; observable completion or progress contract; repeated or adversarial scheduling results | The prototype is synchronous and observed to terminate; no asynchronous system or scheduling claim is made. |
| universal-information-hiding | actual caller needs; caller needs and decision owner; decision owner and volatility; leaked knowledge or coordinated change; material cost/failure semantics callers require | Role input partitions are specified without claiming an implemented module boundary or caller-cost improvement. |
| universal-local-reasoning | knowledge and navigation required by callers/maintainers; representative change or use scenario; representative change scenario; state, invariant, and dependency ownership | The rule makes selection records inspectable; no measured maintenance-cost or change-locality improvement is claimed. |
| universal-no-change-option | actual current cost/risk or absence within a stated interval; intervention cost and uncertainty; latent security, safety, data, durability, and compatibility check; proc-decide-leave-code-alone | The explicit uncompleted rule requirement motivates the change; no system-wide latent-risk or intervention-cost audit is claimed. |
| universal-repository-contract-precedence | accepted ADR, RFC, API, compatibility, generation, build, and test contracts | Relevant authority, source metadata and code-authoring contracts were inspected; unrelated API, generation and runtime build contracts are outside this document change. |

## Execution closure

CAPLAB-61 is Done with the rule-specification resolution appended. CAPLAB-70
retains its open state with the review-procedure pointer appended. Fresh
pre-write reads matched the inspected snapshots; exact returned descriptions,
state and unrelated fields were verified. CAPLAB-70's completion timestamp
remains unchanged. No comments or messages were sent. Receipts:
`/tmp/caplab-{61,70}-{before-selection-update,after-selection-update}.json`
and their `selection-update.ndjson` / `selection-update-result.json` siblings.

The fresh issue/state lists (`/tmp/caplab-roadmap-after-61.json` and
`/tmp/caplab-61-selection-states.json`) show 16 open roadmap items. Source
hashes were rechecked at closure and remain identical to the prototype receipt.
Document links, both worked selection examples, and `git diff --check` passed.
All four applied doctrine citations were classified valid and consumption
recorded locally. No actual pairings or campaign readiness were accepted;
the broader measurement goal remains incomplete.
