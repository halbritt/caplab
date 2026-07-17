---
id: adr-0014
artifact_type: architecture-decision-record
title: CAPLAB P5 purge completion and P6 Study 001 admission
status: decided
decision_owner: caplab-execution-delegate
decision_authority: direct-repository-owner-delegation
created: 2026-07-17
decided_at: 2026-07-17
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-custody
  - caplab-study-001
  - caplab-runtime
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts:
  - caplab-p5-promotion-readiness-execution-2026-07-17
  - caplab-p5-promotion-readiness-verification-2026-07-17
---

# CAPLAB P5 purge completion and P6 Study 001 admission

Status interpretation: after the ADR 0013 correction passed independently, the
repository owner instructed the agent to continue the queued work in order,
delegated CAPLAB decision authority, and, after the agent stated the exact
remaining boundary, replied: `well, it's authorized now`.

The `caplab-execution-delegate` selects the ordered campaign below. Stage A
reopens only ADR 0009/0010's already frozen P5 purge sequence through its
existing `2026-07-23T23:59:59Z` expiry. Stage B authorizes CAPLAB-24/P6 through
`2026-07-24T23:59:59Z` only after a fresh independent P5 PASS. This decision
does not authorize CAPLAB-25/P7, recomputation, a model call, capability
inference, training eligibility, export, publication, acceptance, or any
change to the historical source repository.

## Decision question and scope

Should CAPLAB complete the exact frozen P5 purge after an independent
pre-effect check, then admit and register only ADR 0004's selected C9 Study 001
evidence under ADR 0005's governance, preserving every historical byte,
identity, timestamp, and outcome and stopping before P7?

This is one ordered authorization with two distinct checkpoints. A Stage A
PASS removes the predecessor blocker; it does not itself perform or verify
Stage B. A Stage B PASS verifies registration; it does not recompute the
historical result or accept a capability claim.

## Observations, evidence, and uncertainty

**Observation:** ADR 0013's isolated restore correction passed independent
verification. The isolated target and state are absent, loopback port `55435`
has no listener, the live PostgreSQL cluster is unchanged, P4 is unchanged,
and P5 remains disabled with closure `1|1|0|0`, two good byte copies, no purge
tombstone, and no active P5 credentials. **Evidence:** the linked execution
and verification records at CAPLAB commit `840cecd`.

**Observation:** the P5 identity remains the hash-bound ADR 0010 identity:

| Field | Frozen value |
|---|---|
| Campaign | `caplab-p5-recovery-2026-07-16` |
| Operation | `op-p5-recovery-0001` |
| Request SHA-256 | `4164a5d4febd4f429158d5917a15ae303392ecf1d9d6a57e84ae9a731282b229` |
| Content SHA-256 | `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d` |
| Manifest SHA-256 | `77acb678e5fa2d99374ba5a2e5841a043d904333a7718612fd3b0153a057f1b4` |
| Corrective authorization | ADR 0010 SHA-256 `0b0682acaa749f7715687e10f3c0565f0776da951375d9f3fb5ed329c94e2b9a` |
| Custody request selected here | `custody-p5-final-20260717` |

**Observation:** the selected Study 001 preservation root contains 681
manifest entries, 602 under `attempts/` and 79 under `frozen-inputs/`, totaling
approximately 12 MiB. `sha256sum -c` verified every entry on 2026-07-17. The
manifest-file SHA-256 remains
`081a14d9b4f2872a2d8058f1b0896a7d0e4fd954f164b8c46d2d768558a0d50c`.
A filename and content-pattern scan found no credential candidate. Both source
commits selected by ADR 0004 remain available. The current source checkout is
dirty and behind its remote, so execution must read the selected commits with
Git object commands and must not use or modify its worktree.

**Inference, medium confidence:** blanket restricted admission is the safest
P6 disposition. The tree contains prompts, trajectories, logs, captured
workspaces, verifier material, and a projected doctrine corpus with mixed
licensing and operational sensitivity. No credential candidate was observed,
but a bounded pattern scan cannot prove the absence of every secret. A
restricted namespace, no public projection, content-addressed identity, and a
fail-closed credential check preserve the narrowest useful admission.

Credible rivals are:

- admit only derived aggregates, which cannot satisfy P6's end-to-end attempt
  and object-locator contract;
- redact the tree, which creates new evidence identities and risks changing
  the historical record;
- defer admission, which is safer but leaves an owner-authorized, fully
  preserved 12 MiB checkpoint unfinished; and
- admit every object without restriction, which is inconsistent with ADR
  0005's privacy, licensing, and disclosure boundary.

## Decision, owner, and rationale

**Decision:** execute Stage A and Stage B in order, with a hard independent
verification gate between them.

**Owner and authority:** the repository owner delegated CAPLAB decision
authority to the primary agent. The delegate exercises that authority in this
record after restating the exact boundary and receiving the owner's explicit
authorization. The primary agent is executor. Independent verifier
`/root/caplab_p5_adr0012_preflight`, or a named human who did not implement or
execute the stage, is assigned to P5 purge and P6 verification. The verifier
may return PASS or FAIL but cannot accept CAPLAB or widen this authorization.

**Rationale:** the work is already decomposed into ordered checkpoints. The P5
purge has a tested exact-identity procedure, preserved rollback bytes, and an
unexpired frozen authority. P6 has a small verified source set and explicit
governance. Finishing those checkpoints separately is lower risk than leaving
synthetic custodian state indefinitely or combining admission with
recomputation.

### Stage A — exact P5 purge completion

Before any P5 mutation, the executor must preserve a new root-only execution
directory and require an independent read-only PASS for:

- clean installed CAPLAB and Proximal source identities;
- unexpired ADR 0009/0010 authority and the exact P5 identity above;
- disabled lifecycle state, absent credentials, and absent isolated restore;
- unchanged P4 registration and bytes;
- exact P5 closure `1|1|0|0` and both good P5 byte copies;
- no retained P5 custody dependency or pre-existing tombstone; and
- proof that every effect command is limited to the P5 object key, local-copy
  key, operation, and custody request and cannot name the live cluster.

After PASS, the executor may recreate the existing temporary P5 identities,
verify the frozen registration, and:

1. create pending custody request `custody-p5-final-20260717`;
2. record retained campaign dependency
   `caplab-p5-final-gate-20260717`, require guarded purge refusal and preserve
   its direct numeric status receipt, then record the matching release event;
3. recalculate inventory and stop if any dependency or shared identity remains;
4. stage the exact P5 Garage and `/nvr` bytes in a root-only recovery directory
   and verify each staged SHA-256;
5. delete only the exact P5 Garage object and `/nvr` copy and verify both are
   absent while P4 remains byte-identical;
6. invoke only `caplab_v0.purge_p5_operation` through the exact pending custody
   request and preserve its returned tombstone and row counts;
7. on database refusal or incomplete tombstone, restore both staged P5 byte
   copies, verify the registration, disable access, and stop;
8. on success, disable and remove all temporary P5 access and verify the
   isolated restore remains absent, P5 live rows and bytes are absent, the
   tombstone remains, and P4 is unchanged; and
9. preserve a verified evidence manifest and obtain a fresh independent final
   PASS before updating CAPLAB-23 or entering Stage B.

The purge affects live CAPLAB rows and exact P5 bytes only. It does not claim
immediate physical deletion from pgBackRest, restic, or other backup copies;
those age out under their own schedules. The non-sensitive tombstone,
authorization identity, content hashes, execution record, and verification
record remain in Git and PostgreSQL.

### Stage B — P6 restricted Study 001 admission

Stage B may begin only after the Stage A verification record says PASS and
CAPLAB-23 is projected Done. Its source boundary is exactly:

- preservation root
  `/var/tmp/striatum-bench/luna-bv-confirmation-preserved-2026-07-14`;
- the 681 entries in `manifest.sha256`, whose manifest-file SHA-256 is
  `081a14d9b4f2872a2d8058f1b0896a7d0e4fd954f164b8c46d2d768558a0d50c`;
- that manifest file itself;
- preregistration commit
  `598c670885626d598a03a84a7274286ffca5ab8a`, path
  `doctrine/evaluations/robustness/native/checkout-retries-luna-bv-confirmation.md`,
  SHA-256
  `4d8b1418172a0fc6b042efcca6dad96a5dcb08c7ded4006804fce7aa18ff3eb9`
  (already one of the 681 preserved entries); and
- result commit `dbe6f7e8b988823c754ad232c74ad414119a3375`, result-record
  SHA-256
  `870a96b8b528dee1c85337d83662d9900a1fccd7531c181914ed948d02ed0bf4`,
  and result-CSV SHA-256
  `af8d64fde0b7a93773dfc2ac36651d61ee7259095eef792fa7515810a57a2374`.

The effective admission set is 684 content records before content-hash
deduplication: 681 manifest members, the governing manifest, and the two later
result records. Each receives an explicit inventory entry. All are selected as
`restricted-admission`; none is selected as a redacted derivative, quarantine,
or exclusion. If a stronger credential scan or manual inspection finds a
credential-bearing object, that object changes to quarantine, its credential
must be rotated, and P6 stops until a new complete registration manifest can
be frozen without silently changing the original object.

The executor may add a CAPLAB-native `admission` package, a forward-only
`0003` migration, manifest schema and fixtures, hermetic and local integration
tests, a bounded CLI, execution and verification records, and a separate
Proximal P6 least-privileged host surface. The implementation must:

- parse but never rewrite source bytes;
- verify all source commit, path, manifest, content, and size identities before
  the first write and again before registration freezes;
- give every admitted byte record a content-addressed Garage object and
  byte-identical `/nvr` copy, refusing non-identical replacement;
- preserve source commit, path, historical timestamp fields, assignment,
  attempt, condition, block, outcome, verifier, and lineage identities while
  recording CAPLAB admission time as a separate audit fact;
- link exactly 20 first attempts to their frozen assignments and mechanical
  outcome records, with no invented replacement, missingness, or human
  disposition;
- record the preservation manifest, experiment, treatment, order, task,
  subject, runtime, corpus, verifier, result-record, and result-CSV identities;
- freeze one content-addressed Study 001 registration manifest only after
  PostgreSQL locators, Garage bytes, `/nvr` bytes, source Git identities, and
  all layered links reconcile;
- make replay idempotent and stop on an absent, extra, mismatched, shared,
  credential-bearing, or historically inconsistent object;
- keep all admitted objects restricted to the named writer, recomputation
  reader, and independent verifier roles; and
- disable temporary writer credentials after execution and obtain independent
  PASS before projecting CAPLAB-24 Done.

No P6 command may invoke a provider, model, verifier that computes a new
outcome, or historical analysis. Existing result bytes are registered as
historical records only. The P7 recomputation interface remains unavailable.

## Preservation, rollback, and verification

| Surface | Preserved behavior or state | Proof |
|---|---|---|
| P4 control | registration, Garage byte, `/nvr` byte, roles, and manifests unchanged | before/after independent inventory and byte hashes |
| Live PostgreSQL service | data directory, port 5432, PID/start identity, and availability unchanged except named CAPLAB transactions | pre-effect and post-effect identity receipts |
| P5 | exact live closure removed only after byte staging and dependency absence; tombstone retained | guarded function receipt, row counts, inventories, independent PASS |
| Study 001 source | source Git objects and preservation root remain read-only and byte-identical | Git-object hashes and full manifest verification before/after |
| Historical semantics | content, timestamps, assignments, attempts, outcomes, missingness, and result bytes unchanged | typed manifest reconciliation and 20-attempt link audit |
| P7 and later | unavailable | command/help tests and absence of model/provider calls |

P5 rollback restores the two staged bytes if the database transaction does not
produce the complete tombstone. A successful exact purge is intentionally not
reversed: the tombstone is its durable result. P6 stops before registration on
source drift; after partial byte copies it removes only unregistered P6 copies
listed in a non-applying cleanup plan or leaves them quarantined if deletion
authority is uncertain. A frozen P6 registration is append-only and can be
withdrawn or purged only under a later exact owner authorization.

## Doctrine provenance

The decision-guiding retrieval used evidenced packet
`pkt-2ef8ec66cc51515b`, content SHA-256
`5469ab588c476cb2e233df0e448b14af2749b145930bedfd816f71e373b1bc79`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, and doctrine
`doctrine-a90ee3f1cf7b6f26`. Retrieval state was clean. The standalone CAPLAB
repository has no `make doctrine-check` target, so the validated release gate
was used and that missing target is not represented as a doctrine failure.

Material guidance applied is local-contract precedence, explicit invariants,
evidence before intervention, authority-bounded action, separate change
checkpoints, behavior preservation, and a durable decision record. The no
change alternative avoids immediate operational risk but retains an
unnecessary live synthetic closure and leaves the authorized P6 outcome
undelivered. The selected intervention costs a new migration, restricted
object copies, credentials, integration proof, and ongoing retention review;
uncertainty remains around latent credentials and mixed licensing, so blanket
restriction and fail-closed quarantine are mandatory.

## Stop and reopening conditions

Stop on any authority, source, expiry, repository, identity, dependency,
credential, privacy, licensing, content, timestamp, P4, live-cluster,
tombstone, reconciliation, role, backup, verifier, or manifest mismatch. Stop
if an effect requires a dirty source worktree, general delete privilege,
rewriting history, stopping the live cluster, changing another Garage object,
publishing restricted evidence, entering P7, or making a model call.

Reopen this decision if P5 cannot finish before its frozen expiry, the P5
identity or P4 control changes, the 681-entry preservation manifest changes, a
credential or license requires a different disposition, P6 needs an object or
effect outside the exact source set, or recomputation/P7 authority is needed.
