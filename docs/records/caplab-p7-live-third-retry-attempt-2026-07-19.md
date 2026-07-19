---
id: caplab-p7-live-third-retry-attempt-2026-07-19
artifact_type: execution-record
assertion_type: observation
campaign: caplab-study-001-p7-recompute-2026-07-18
authorization: adr-0021
status: stopped
---

# CAPLAB P7 stopped third live retry

## Scope

ADR 0021 authorized one execution of the exact third P7 retry. The executor
preserved all earlier stopped evidence, installed the repaired CAPLAB source
and source-pinned Proximal files, captured fresh pre-effect controls, and called
the versioned controller's `enable` command. This record states execution and
cleanup observations. It is not independent verification, a capability
inference, another retry authorization, or acceptance.

## Observations

- The second-retry evidence and disabled state were moved intact to
  `/var/tmp/caplab-p7-stopped-second-retry-2026-07-19`. Its 53-file archive
  passes `ARCHIVE_SHA256SUMS`; that manifest has SHA-256
  `cc9fc15a80ab9ff59f8192cbf90d859a3ee510ab24d03b2ced7c0dae2f6f9153`.
  Both earlier stopped-attempt archives remain unchanged and verify.
- Repaired CAPLAB commit
  `bf6de2b24ac61e82107208cdc609c7e534c6eaaa` was installed under its distinct
  runtime path. The dependency lock, package import, frozen 105-test gate, and
  current repository gate passed. The earlier frozen runtime was retained.
- The five canonical host files from clean, pushed Proximal commit
  `c5bb1efa1402010a57ccc7034f3555b14830bc1c` were installed with their bound
  hashes. The expiry timer remained active and enabled.
- A fresh root-owned evidence root captured 31 pre-effect files. The normalized
  whole-schema dump, cluster identity, P4 and P6 controls, Garage inventory,
  independent-copy hashes, install identities, cardinalities, and disabled
  access state matched the authorized baseline: 684 evidence records, 325
  unique content identities, exact 20/20/20 assignment-attempt-outcome links,
  326 Garage objects, and 326 independent copies.
- `enable` stopped in installation verification before creating campaign state,
  a Garage key, a credential, PostgreSQL login, or any reader process. The new
  venv's `bin/python` was a symbolic link; the controller requires the runtime
  interpreter path itself to be a regular, non-symlinked file and reported
  `installed runtime interpreter is absent or ambiguous`.
- Because enablement stopped before creating campaign state, both the installed
  cleanup trap and an immediate repeated `disable` reported `state_read`.
  They still ran the independent PostgreSQL, process, Garage-inventory,
  credential, and OS-account cleanup operations.
- Independent post-stop checks found no P7 Garage key or credential, zero role
  logins, zero reader/writer/verifier sessions, zero reader processes, and no
  campaign state. The PostgreSQL summary and normalized whole-schema dump,
  cluster start identity, P4 and P6 controls, Garage information and key list,
  independent-copy hashes and symlinks, and OS accounts match their pre-effect
  observations exactly.
- Neither recomputation ran and no product result was emitted.

## Diagnosis

**Inference:** the first divergence is the runtime construction command, not
the repaired recomputation, registered evidence, or access boundary. Python's
default `venv` construction created `bin/python` as a symlink, while the
versioned controller deliberately rejects a symlink at the frozen interpreter
custody boundary. The earlier P7 runtime used a regular interpreter file.

The narrow candidate correction is to construct the venv with `--copies` and
verify the installed interpreter with `lstat` before installation is considered
complete. It must not weaken the controller's symlink refusal, alter the
recomputation repair, or reuse ADR 0021.

## Evidence custody

The 59-file root-owned evidence set remains at
`/var/tmp/caplab-p7-execution-2026-07-18`. Its 58-entry `SHA256SUMS` file has
SHA-256
`56b49199a9df5ddc5cfa8f307e7b2bfe81747a52de6a6af4c633adcd191d7eb6`
and passed verification after the stop. It contains no Garage secret,
credential, recomputation result, or replay output.

## Result and boundary

**Execution result:** stopped before access enablement and P7 recomputation.
CAPLAB-25 remains open. ADR 0021 is consumed and authorizes no runtime
replacement or further live attempt.

After this stop was reported, the repository owner instructed the executor to
`retry again`. That records owner intent to continue, but the correction must
first bind an exact regular-file runtime construction, clean desired-state
commit, installed identities, preserved stopped evidence, and mandatory
cleanup before another live effect begins.
