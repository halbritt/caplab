---
id: adr-0004
artifact_type: architecture-decision-record
title: CAPLAB Study 001 selection
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership
created: 2026-07-15
decided_at: 2026-07-15
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# CAPLAB Study 001 selection

Status interpretation: the repository owner selected one exact historical
experiment as CAPLAB Study 001 on 2026-07-15. This decision binds an identity
and claim boundary. It does not admit or move evidence and grants no retention,
implementation, model-call, inference, export, training, verification, or
acceptance authority.

## Decision question and scope

Which one exact historical checkout-retries experiment, if any, should be bound
as CAPLAB Study 001 under the P0 gate in
[`plan-agent-capability-lab-v0`](../product/plans/plan-agent-capability-lab-v0.md)?

This record selects the experiment and fixes its historical identity, result
boundary, exclusions, and known limitations. Evidence admission, storage,
retention, runtime implementation, capability-card selection, capability
inference, and downstream training use remain separate decisions.

## Observations and evidence

**Observation:** ADR 0002 requires v0 to bind one exact historical
checkout-retries experiment without pooling adjacent experiments. The CAPLAB
plan defines either an exact selection or a `no-admissible-candidate` decision
as P0's durable output. **Evidence:**
[`adr-0002`](adr-0002-agent-capability-lab-v0.md) and the CAPLAB plan's P0
contract.

**Observation:** A read-only candidate review inspected nine historical
checkout-retries experiments. C9, the Luna B-versus-V confirmation, was the only
candidate found with the ordinary P0 package: frozen task trees, corpus
projection, preregistration, order, treatment, runner, subject declaration,
capture binary, all 20 attempts, and a recursive preservation manifest. The
dossier is identified by SHA-256
`7b5a4e067a16df8d9d7f67f3f73e3e7047eb7a56d530a1871077d810808d8e7d`.

**Observation:** The C9 preservation manifest names 681 files. The candidate
review ran `sha256sum -c --quiet manifest.sha256` within the preservation root
on 2026-07-15 and recorded exit 0. The review also recorded 320 aggregate-to-raw
field comparisons with zero mismatches. This ADR records those observations; it
does not rerun or expand the experiment.

**Observation:** C9's mutant bare arm shipped harm 8/8 and its exact V arm
shipped harm 0/8. The preregistered risk difference was 1.0 and the one-sided
exact result was `p = 1/256`. All four clean sentinels passed the fault-clean
guard at reward 0.8, but each recorded 40 concurrency successes and 10 bad
orders and therefore was not fully concurrency-clean. **Evidence:** the exact
result record and CSV identities below.

**Observation:** On 2026-07-15 the repository owner accepted the recommendation
to select C9. Plane comment external ID
`caplab-18-owner-selection-c9-2026-07-15` records the selection as a tracker
projection. This ADR is the durable decision record.

## Inferences, rivals, assumptions, and uncertainty

**Inference:** C9 is the strongest preserved vertical-slice candidate for P0
because its frozen inputs, raw attempts, instrument outputs, and preservation
manifest can be bound without reconstructing or pooling history.

Rivals and uncertainty:

- selecting the original 26-trial local-model pair would preserve its
  historical importance, but its raw attempt bundle and preservation manifest
  were not found; under the current P0 gate that alternative is
  `no-admissible-candidate`, not a weaker registration;
- the result record and CSV necessarily postdate the pre-run preservation
  manifest; this decision accepts their exact Git commits and content hashes as
  the historical binding without pretending they were frozen before the run;
- the recorded model alias, declaration, CLI package, runtime logs, and capture
  identify the exercised subject configuration but do not supply an immutable
  model-weight digest;
- the experiment establishes an effect for the exact V instruction in this
  task pair, tuple, runtime, and sample; it does not establish a causal
  mechanism, model-wide judgment, or cross-task generalization; and
- whether V is a representative or doctrine-derived instruction is a separate
  provenance and construct-validity question. This result alone cannot answer
  it.

## Recommendation and alternatives

**Recommendation:** Select C9 because it is the only ordinary-P0 candidate
whose exact historical evidence package was mechanically complete in the
candidate review. Bind every identity below and exclude all adjacent
experiments.

Alternatives were selecting no admissible candidate, weakening P0 to admit an
incomplete historical package, or pooling the checkout-retries family. The
first would stop v0; the latter two would rewrite the selected product contract
and were not chosen.

## Decision, owner, authority, and rationale

**Decision:** The repository owner selects the historical Luna B-versus-V
confirmation as CAPLAB Study 001. The selection binds only this exact
experiment and its exact 64-word V package. It excludes C1 through C8, the v1
sweep, pooled checkout-retries evidence, generic doctrine-effect claims,
mechanism claims, immutable-weight claims, model-wide capability claims, and
cross-task claims.

**Owner and authority:** repository owner under repository ownership. The owner
made the selection on 2026-07-15 by accepting the recommendation after review
of the candidate dossier and its stated alternatives and limitations.

**Rationale:** C9 supplies the smallest complete historical experiment package
that can exercise CAPLAB's registration and recomputation path without
manufacturing missing evidence or changing the recorded study.

### Bound experiment identity

| Element | Bound identity |
|---|---|
| Preregistration | commit `598c670885626d598a03a84a7274286ffca5ab8a`; path `doctrine/evaluations/robustness/native/checkout-retries-luna-bv-confirmation.md`; SHA-256 `4d8b1418172a0fc6b042efcca6dad96a5dcb08c7ded4006804fce7aa18ff3eb9` |
| Result record | commit `dbe6f7e8b988823c754ad232c74ad414119a3375`; path `doctrine/evaluations/robustness/native/checkout-retries-luna-bv-confirmation-result.md`; SHA-256 `870a96b8b528dee1c85337d83662d9900a1fccd7531c181914ed948d02ed0bf4` |
| Result CSV | result commit; path `doctrine/evaluations/robustness/native/checkout-retries-luna-bv-confirmation-results.csv`; SHA-256 `af8d64fde0b7a93773dfc2ac36651d61ee7259095eef792fa7515810a57a2374` |
| Experiment manifest | SHA-256 `9129d8d8200cdd1f6407c5522b2df7776d1cb46dc9ccb9f0c92f2748e1fcd815` |
| Treatment manifest | SHA-256 `d67f2d33cd3d6bbb467c2cb916a99ea7a0c9a5a969bd9c167f6264ba8f3e6409` |
| Frozen order | SHA-256 `f487e15702ca76faa44b56d2c0bbc093a269f3f2abb180e352180227dd7a4f58` |
| Bare instruction | SHA-256 `ec2689ee7d7f227c3e4abad321fa0114a96a9e1ea1b323fcca956c3334533fa4` |
| V component | exact 64-word component; SHA-256 `b8a7baff531e66f7775cd4ca98841624f5b911e1490d53d9b67a9ca0d09dc6aa` |
| Rendered V prompt | SHA-256 `668ede7db0bc28dfc474f578e30bdc9759a02181e4c0214a1aafc28eabfaf4a3` |
| Mutant task | Git tree `25e791252afe720ded6557cd4c2f5e3b87871103`; task SHA-256 `70a6c724bcb8674978ecc4ead5bf1612b6d9206494a6b9df0e9ef6d736805808`; world SHA-256 `83b6312c603d56de5be287a1356c5f4e94a8d57dd6463648b5eb76c5864e80af`; verifier SHA-256 `ae66564170c001f1711118cf1417707ddca28935ac311acf231ce93b0511b749` |
| Clean task | Git tree `f778596be0ad6c31e780d93999d3168bf92464cd`; task SHA-256 `ee980c921db8b416b082c4863084b5a517e9337168112fb3e738a264f4091b51`; world SHA-256 `d66c6f92cb0a50e596e665d1bb6ed9d9279b79802c3e14ebc5d0eabf6205eaab`; verifier SHA-256 `b2696b49e15348b3825a7da45e4f32663bbc8315acf0dfd303c1581d304fe571` |
| Corpus projection | surface SHA-256 `29e067c6a80336132da0cec5cdc6aab183bce8a3969362a12b33d96791a21a48`; surface-manifest SHA-256 `bebbccd752104219096f0ffc04de36e81f1290455c448fd238b2ae011980532f`; projection-manifest SHA-256 `89700383c5963c907a9f2ca57c074b94fa3f0b1639489885b9d07a6b4d108985`; source commit `bee6358108ae90d5e780a8317cfcf904c6365fc8` |
| Subject declaration | SHA-256 `3d887aff7d8a8b54d7659b5ca78c1457a52f0af9293619845d3f41d50d50e02b`; recorded tuple `gpt-5.6-luna`, maximum effort; Codex CLI `0.144.1` |
| CLI package | SHA-256 `e9756b0cb1e3a6f678ac9848365b6f3a22f11cede8348b883c2c05cb9c31705b` |
| Capture observer | commit `b055a23d82873e055889811d7ee6f76e236866e9`; binary SHA-256 `494cbc58e55011598a53acd54920404febdd1d5d05ac233d5bd5d9afa8f00451` |
| Preservation | local root `/var/tmp/striatum-bench/luna-bv-confirmation-preserved-2026-07-14/`; `manifest.sha256`, 681 entries; manifest-file SHA-256 `081a14d9b4f2872a2d8058f1b0896a7d0e4fd954f164b8c46d2d768558a0d50c`; candidate-review verification on 2026-07-15 recorded exit 0 |

The preservation manifest covers frozen inputs and attempts. The later result
record and CSV are bound separately through their exact Git commit and content
hashes; they are not represented as members of the pre-run manifest.

## Authorization and execution scope

The owner's selection authorizes this ADR, the decision index and CAPLAB plan
links, and the matching sanitized Plane projection. It does not admit, import,
copy, retain, redact, purge, register, or expose evidence. It authorizes no
datastore change, implementation, model call, capability inference, training
use, verification, or acceptance.

Evidence registration remains P6 after the governance and synthetic recovery
gates. Capability-card selection remains P2. Neither becomes authorized by
this decision.

## Consequences and preservation boundaries

- P0 has a selected historical identity; downstream planning may reference it
  without searching for or inferring a different candidate.
- C1 through C8 and the v1 sweep remain separate historical evidence. They are
  neither pooled into Study 001 nor demoted or rewritten.
- All historical bytes, timestamps, results, corrections, failures, task
  identities, and claim limits remain unchanged.
- The result may support only a Study-001-local proposal until the selected
  capability card and later human inference say otherwise.
- Admission can still fail on privacy, licensing, credential, integrity, or
  runtime-governance grounds without changing this historical selection.

## Verification and fitness criteria

This decision record is conformant when:

- every named Git object resolves from a retained remote reference;
- the identity table matches the mechanically verified candidate dossier;
- the preservation observation is reported with its date and limit rather than
  promoted to current retention or admission;
- adjacent experiments and broader claims are explicitly excluded;
- the CAPLAB plan and ADR index link this record;
- repository documentation and doctrine checks pass; and
- no evidence byte or retention state changes while recording the decision.

These checks verify the record. They do not rerun the experiment, admit its
evidence, verify an implementation, or accept CAPLAB v0.

## Acceptance owner and outcome

The repository owner is the acceptance owner for the faithful recording of
this selection and for CAPLAB v0. The experiment is selected. Acceptance of any
later registration, capability inference, implementation, or integrated v0
outcome remains pending.

## Reopening and supersession conditions

Reopen this decision if a bound identity fails to resolve or match, the
preservation record is contradicted, the owner requires an immutable model
weight identity, privacy or licensing makes the selected evidence inadmissible,
or the intended Study 001 question changes from the exact C9 experiment.

A later finding that V is not doctrine-representative narrows what Study 001
can claim; it does not silently substitute another experiment. Substitution
requires reopening ADR 0002's v0 slice and superseding this ADR.

## Doctrine record

The recording and work-decomposition question used doctrine packet
`pkt-9a6c897c79f79cb6`, content SHA-256
`9a6c897c79f79cb68e9429d20e6a99adf22272847194b77d4f970317f8e08605`,
doctrine `doctrine-164e6a9e863b1ae4`, and retriever
`retriever-784b2cbe112a7b79`. Its authority ceiling was `recommend`; the owner's
explicit selection, not retrieval, creates this decision.

The packet's remaining datastore, transaction, idempotence, caller,
preservation-campaign, and runtime-verification obligations are nonmaterial to
this documentation-only selection. They become material at P3 through P6 and
are preserved in ADR 0005 and the CAPLAB plan rather than treated as satisfied.

## Related artifacts

- Product boundary: [`adr-0002`](adr-0002-agent-capability-lab-v0.md)
- Product specification:
  [`spec-agent-capability-lab`](../product/specs/spec-agent-capability-lab.md)
- Implementation plan:
  [`plan-agent-capability-lab-v0`](../product/plans/plan-agent-capability-lab-v0.md)
- Planning projection: local Plane work item `CAPLAB-18`

## Status history

- `2026-07-15` — `decided` — repository owner selected the exact C9 Luna
  B-versus-V confirmation as CAPLAB Study 001; evidence admission and all
  implementation remain separately gated.
