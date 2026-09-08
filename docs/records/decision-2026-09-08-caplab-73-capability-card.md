# Advisory-responsive approach selection: prospective capability card

Date: 2026-09-08. Decision mechanism: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `5a80b3b`.

## Authorization before execution

Create the capability card at the path reserved by CAPLAB-58:
`docs/product/capability-cards/caplab-advisory-selection-001-advisory-responsive-approach-selection.md`.
Update `docs/product/README.md` and the advisory-selection study README to
link the new prospective card and distinguish it from the missing
preregistration. Complete this record with source provenance, requirement
coverage, adversarial arithmetic checks, document verification and advisory
doctrine receipt. New synthetic examples may be computed locally.

Use the current repository contracts and read-only Plane descriptions and
comments for CAPLAB-46, 50, 52, 57, 58, 73 as decision provenance. Do not admit,
copy, rewrite, rescore or purge historical campaign evidence. No native call,
model spend, coder assignment, human-time commitment, runtime change, sealed
study amendment, reviewer ranking or placement is authorized. Preserve
`docs/designs/` and all campaign artifacts. This card does not qualify a
Binding or authorize a study.

After verification, append a resolution to CAPLAB-73 and mark that drafting
item Done. Preserve its original description and unrelated fields. Re-read
before updating and stop on concurrent change. No external comments or
messages are authorized. Authorization expires at commit. Remove only this
task's doctrine scratch after recording its receipt; retain the local source,
arithmetic, document and tracker verification receipts.

## Selected contract and reconciliation

Select a prospective card for the construct, independent of any single study's
primary estimand. The CAPLAB-46/58 clauses remain: fitting uptake, resistance
to misfit advice, and non-degradation of the work. CAPLAB-52's amendment makes
own-code uptake the foundational study's primary and selectivity a descriptive
secondary. Neither a positive primary nor an underpowered secondary establishes
the full construct. A future study may measure the premise while explicitly
withholding a favorable capability claim.

The old claim that three clauses require exactly three arms is replaced
prospectively by three required comparison roles: an appropriate baseline,
bearing advice, and plausibly adjacent non-bearing advice. Arm count alone
does not identify all three clauses: non-degradation requires a separately
measured work-quality outcome, and each code family needs its baseline.
Additional arms require their own justified contrasts; a bare baseline or
borrowed packet does not automatically replace the non-bearing comparison.
No existing study's arm assignment is changed here.

Non-monotonicity applies to selectivity, not to the foundational uptake
estimand. Equal increases in bearing and placebo conduct give zero selectivity
even when both increases are large. A positive difference produced only by
reducing placebo conduct is insufficient to demonstrate fitting uptake.
Keep the separate contrasts and require evidence for every constitutive
clause before a favorable full-construct claim. Uncertainty or an unmeasured
clause yields an incomplete claim, never an assumed pass.

The CAPLAB-64 procedure supplies asymmetric B/P derivation, validated
alternative witnesses, binary definitions and negative space. Its newer
pooling and missingness constraints govern adopting studies; no numerical
threshold is chosen from observed results. Coder agreement is reliability,
not an independent accuracy anchor or demonstrated blinding.

Leaving the card absent leaves the original conflicting tracker prose as the
most accessible construct contract. Copying that prose unchanged would make
exact arm count and uptake stand in for construct validation. Inventing a
composite score would conceal tradeoffs without a selection policy. The
selected card instead names separate evidence requirements and failed-claim
dispositions. It adds a specification and navigation, not an executable gate.

## Requirement coverage and challenge checks

| CAPLAB-73 requirement | Card resolution | Verification boundary |
| --- | --- | --- |
| Definition and three clauses | Construct section preserves fitting uptake, resistance to distortion and non-degradation | Checked against CAPLAB-46/58 decisions |
| Constitutive placebo | Required comparison roles retain an adjacent non-bearing comparison | Exact-three-arm inference amended explicitly; no existing assignment changed |
| Non-monotonicity | Equal positive dB/dP yields zero S; theta remains a separate premise estimand | Four examples computed with exact rational arithmetic |
| Two-source derivation | B requires rule plus reference; P follows its single-source amendment | Linked CAPLAB-64 procedure, including positive and negative witnesses |
| Alternative repair, binary codes, negative space | Required for codebook adoption | No actual codebook validated by this document |
| Blinding and freeze ordering | Protected prior witness, context separation, redaction validation, reliability before unblinding | Accuracy anchor and blinding remain unestablished |
| Inherited card versus study specifics | Final handoff separates construct invariants from population, Binding, dose, coder roster, parameters and schedule | No preregistration or frozen numeric gates invented |
| Promotion gates exposed by CAPLAB-44 | Clause-by-clause uncertainty and quality evidence, then separate accepted measurement/qualification policy | No profile promotion or reviewer ranking authorized |

Manual adversarial review also checked: an always-false P detector fails its
positive witness; a repeated concept phrase without conduct fails code
validation; absent capture is unavailable; perfect coder agreement is not an
accuracy anchor; positive S from negative dB cannot establish fitting uptake;
quality harm cannot be offset by code uptake; and a wide harm interval is not
non-degradation. A ceiling leaves uptake unmeasurable rather than proving low
capability. A borrowed sham or a bare arm does not silently satisfy adjacent
non-bearing control. These are contract dispositions, not executed study cases.

The local verification receipt `/tmp/caplab-73-card-verification.json` records
30 resolved document links, all four exact arithmetic examples, the card hash
and the absent preregistration. `git diff --check` passed. No runtime or test
source changed, so the full runtime suite was not rerun for this prose change.
The previous commit's 883-test run is not evidence that this card is an
implemented gate. Independent scientific acceptance remains unclaimed.

## Decision provenance

The Plane snapshots below were read as planning/decision provenance, not
admitted empirical evidence. Their original descriptions and comments are
preserved. The file hash identifies the exact local JSON envelope inspected;
comment IDs identify the source records inside it.

| Local source | Issue/comment identity | SHA256 |
| --- | --- | --- |
| `/tmp/caplab-card-46.json` | CAPLAB-46: ef3c1e88-45f7-4541-a6d5-e9c091e8a14e | `ea4e3ce1bf6a33ed791fcb49a5dafeecb57ece34dc971abdaabf07b374877fd6` |
| `/tmp/caplab-card-46-comments.json` | CAPLAB-46: 3478e9e1-7f4a-4e46-8f34-57459ccd54bd, e9ec320c-05fd-4996-964a-5461b7ad9806 | `3a3dd5a5543fc46e731d39e3a339b63d390b86be91888819c183ec22815959d6` |
| `/tmp/caplab-card-50.json` | CAPLAB-50: 4fb8fc59-4a21-4085-89c8-b5b64a421eb0 | `e744f3f025a06b1acb8b1d550756d9aea4e2a25c414d97e2ff2513299acfc3d0` |
| `/tmp/caplab-card-50-comments.json` | CAPLAB-50: d3c1dee3-85e7-4873-8ced-bdb57fc67324, 5792aea1-1ce2-467c-9445-ee3d56cee7fd | `8b8e6747495538b18bc3857d766e2ffbfb436eb9dc5c13f0e6aa2091878a4839` |
| `/tmp/caplab-card-52.json` | CAPLAB-52: eb258eb2-9d5c-45be-95d0-0d452eadb47c | `db61c92ee6fc82a9489d59f55876f5dff791491b8e20479674560ac6d5c15a7d` |
| `/tmp/caplab-card-52-comments.json` | CAPLAB-52: 9b5f903f-df2a-4f9d-9f83-aa7e28a68d2c, 82d73c4a-760b-4d66-8eef-1f689b77866a, 88fe8935-76c4-4ab8-a571-52e547789bd6 | `2b54b13c5c8d7e2723c04ad8e9be4a4acd946b7ba69296adf68ea2679334f986` |
| `/tmp/caplab-card-57.json` | CAPLAB-57: 5606aa20-9f0d-4b8e-adda-2e6c63fb5323 | `5282e8f81c7035b6630ff6ff11eff49f67c5a3473df4524ecda3bcad9a3eed0c` |
| `/tmp/caplab-card-57-comments.json` | CAPLAB-57: 7b366c16-a160-4e52-9867-3e44c109c311 | `793619418efb82b567055b396438e7de695d6e47a0945bcffd172da4a24f95ac` |
| `/tmp/caplab-card-58.json` | CAPLAB-58: 60d6d3de-7f9a-4620-8311-547552feb936 | `6aa7c432e8c29632502f9eb531cae032dc99e2f02b03b4ba3b6eeb9f955fff53` |
| `/tmp/caplab-card-58-comments.json` | CAPLAB-58: 72ac02a6-6fce-4774-ba23-3d7a10452f22 | `1a537eb346fc097247af5bf9c27291dd866fa0b7c708080b7a08f8313e96c4e7` |
| `/tmp/caplab-card-73.json` | CAPLAB-73: d58ba21e-955d-437f-92ea-429a479dcfb0 | `69bc06580f3ddcca144dab940f6d3672fb01f3659fc8d7b6d9cf24d61d0a9be9` |

Repository authority remains CAPLAB-owned. The following governing source
bytes were read at baseline `5a80b3b`; no empirical campaign files were read
or admitted for this drafting task.

| Source path | SHA256 |
| --- | --- |
| `docs/domain/ubiquitous-language.md` | `a89fcdeafbfd7f4ebc0ea0f3ab6afd531c6894d5e7c517bc8fb436e316ab2375` |
| `docs/product/contracts/behavior-code-authoring-v1.md` | `06dcf61621ca7c4cacad6c75db758a13a89c8b5488cc7341503d9e47b5e16f5c` |
| `docs/product/contracts/adjacent-placebo-selection-v1.md` | `391f31c5f663e1fadead7aa35fcbd15df36775e42ac8909828c6270e95df0076` |
| `docs/product/contracts/code-agreement-report-v1.md` | `00bb7de1c83a9821ead222ce1a50801bc824c0e0c17d279fa3be38d52b846db7` |
| `docs/records/report-2026-09-07-review-instrument-disposition.md` | `f879ecb5b34767052e649fd5b3b8cd5744473c670a2b05cf45d7051f7cf4bd67` |

## Advisory doctrine receipt

Release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` passed the retrieval-state
gate. Corpus `corpus-2026-07-12-a11702cc9217`; doctrine
`doctrine-f6bbb5196a3f8bf9`; retriever
`retriever-ec995ecdd083b2c8`. Final packet `pkt-cf3e0679203381f6`;
content SHA256 `cf3e0679203381f6e07679bda22120f7bc675b4ca42ed16d56f604e944b0539b`.
One typed-evidence gathering pass; execute ceiling bounded by ADR 0026 and
this record, not by retrieval.

Applied `universal-explicit-invariants` for clause-specific failed-claim
dispositions; `universal-repository-contract-precedence` for the amended
outcome contract; `data-system-of-record-derived-state` for Plane as a planning
projection; and `agent-conduct-authority-bounded-action` for separating the
prospective card from execution and acceptance.

All remaining obligations are nonmaterial to this document-only decision:

| Concept | Remaining requirements | Rationale |
| --- | --- | --- |
| `data-consistency-model-selection` | application scenario and forbidden observations; datastore consistency and isolation guarantees; datastore guarantee; forbidden observation or invariant; latency and availability consequences under partition or failure | No datastore or consistency policy is selected; no transactional guarantees claimed. |
| `data-end-to-end-request-idempotence` | atomic deduplication or uniqueness enforcement; atomic durable effect boundary; external-effect and retry behavior; identity generation and propagation path; retention period and collision semantics; stable intent identity | One description/state projection update is re-read and verified; no automatic retry after unknown outcome and no new request or deduplication protocol. |
| `data-system-of-record-derived-state` | complete mutation-path and data-authority inventory; derivation, rebuild, reconciliation, and consumer behavior during lag; measured read benefit plus write, storage, freshness, and consistency costs | Scope is the named card, record, navigation and one planning projection. No derived data implementation or performance benefit claimed. |
| `data-transaction-guarantee-verification` | application invariants and anomaly analysis; concurrency and fault tests at the relied-upon boundary; datastore guarantee and configuration; explicit application invariants; vendor or protocol guarantee for the exact configuration | No database transaction or ACID guarantee is relied on for the card; concurrent tracker changes stop the update, with no atomic-compare guarantee claimed. |


All four cited concepts classified as `valid-packet-citation`. Temporary
packet, typed-evidence and citation files were removed after recording this
receipt; source snapshots and verification receipts remain.

## Planning projection execution

CAPLAB-73 was re-read immediately before updating and matched the complete
pre-update snapshot. The read-back verified the exact appended description,
Done state and newly set completion time; the only changed fields were
`updated_at`, `description_html`, `completed_at` and `state`. The original
text, comments and unrelated fields were preserved. No comments or messages
were sent. This closes the drafting item, not the parent study or its
measurement gates.

Tracker receipts: `/tmp/caplab-73-before-card-update.json`,
`/tmp/caplab-73-immediate-card-update.json`,
`/tmp/caplab-73-card-update.ndjson`,
`/tmp/caplab-73-card-update-result.json`, and
`/tmp/caplab-73-after-card-update.json`.
