---
id: caplab-p7-live-retry-attempt-2026-07-19
artifact_type: execution-record
assertion_type: observation
campaign: caplab-study-001-p7-recompute-2026-07-18
authorization: adr-0018
status: stopped
---

# CAPLAB P7 stopped live retry

## Scope

ADR 0018 authorized one retry of the exact P7 continuation. The executor
preserved the first stopped attempt, installed the selected controller, captured
fresh pre-effect controls, enabled the bounded reader identity, and began the
ordered readiness checks. This record states execution and cleanup
observations. It is not verification, a capability inference, another retry
authorization, or acceptance.

## Observations

- The first stopped attempt was moved intact to
  `/var/tmp/caplab-p7-failed-attempts-2026-07-18`. Its 56-file archive and
  disabled state passed `ARCHIVE_SHA256SUMS`; that manifest has SHA-256
  `5ad7259eaf6f85d85b2595e559835aebe9cdb134a8d4d4989b6dcd9473da8d5e`.
- The corrected controller from pushed Proximal commit
  `8c45e62a22cf5c7e566df2d4510b49742f39b6ac` was installed with SHA-256
  `7497d3cf12fd6b6d91dbb0e14cd8fe852fd162f055d7974377871338e3c79607`.
  Its seven lifecycle tests, Ruff check, systemd unit verification, and active
  expiry timer checks passed.
- A fresh root-owned evidence root captured 25 pre-effect files. The normalized
  whole-schema dump, cluster identity, P4 and P6 controls, Garage inventory,
  independent-copy hashes, install hashes, test results, cardinalities, and
  disabled access state matched the authorized baseline. The observed counts
  remained 684 evidence records, 325 unique content identities, 20 assignments,
  20 attempts, 20 outcomes, 326 Garage objects, and 326 independent copies.
- `enable` created only the expiring read-only P7 reader identity. The installed
  controller then passed `verify --phase ready`.
- A second, unversioned shell assertion stopped before either recomputation. It
  required each role's stored password field to be `NULL`. PostgreSQL instead
  retained its unusable `*` marker for the roles. A boolean-only follow-up
  established that every role password remained unusable; no stored password
  value was retained in the record.
- No first or replay recomputation output, error file, or return-code file was
  created. The product recomputation command did not begin.
- The installed cleanup trap completed aggregate disablement with status zero.
  The retained state is `disabled`; the P7 key and credential are absent; the
  reader, writer, and verifier are `NOLOGIN`; and reader sessions and processes
  are zero.
- The normalized whole-schema dump, PostgreSQL summary and cluster identity,
  P4 and P6 controls, Garage information and key inventory, independent-copy
  hashes, and source/install identities match their pre-effect observations.

## Diagnosis

**Inference:** the first divergence was the shell wrapper's representation-level
assertion, not the controller, PostgreSQL access boundary, or recomputation
product. It conflated a missing stored password with an unusable stored
password. The credible rival was that the roles held a usable password; the
boolean-only check `(rolpassword IS NULL OR rolpassword='*')` discriminated
against that rival without emitting the stored value.

The narrow repair moves the complete PostgreSQL readiness invariant into the
versioned controller. It accepts only `NULL` or PostgreSQL's unusable `*`
marker and fails closed on a missing role, usable password, writer or verifier
login, unexpected session, effective reader write authority, or non-loopback
listener. The live read-only query executed successfully against the disabled
host state, and nine lifecycle tests cover acceptance and every widening class.

## Evidence custody

The 46-file root-owned retry evidence remains at
`/var/tmp/caplab-p7-execution-2026-07-18`. Its `SHA256SUMS` file has SHA-256
`c46bb43a6165da15e49524ddc4dd0f931eaa91af19bde7782ea3d0a3cbe515b7`
and passed verification after the stop. It contains no Garage secret or
recomputation result.

## Result and boundary

**Execution result:** stopped before P7 recomputation. CAPLAB-25 remains open.
ADR 0018 is consumed and authorizes no changed controller, recovery action, or
further live attempt.

The causal repair is prepared in clean, pushed Proximal commit
`031d20cceefa1f7f4bf5db9386d89383d763edf0`; the controller SHA-256 is
`8f5b2378a772f1c5c1fd28031e0c9ac9a96b84f90c0270d2c48d85ce3be7d076`.
Doctrine packet `pkt-e8b0978f6a99d580`, content SHA-256
`e8b0978f6a99d580010e4cb0a9d9e759c78b928988bda883f9fb1f76eec53eeb`,
supports the causal repair and preserves the owner decision boundary.
Installing the new controller or continuing live execution requires a new exact
owner decision.
