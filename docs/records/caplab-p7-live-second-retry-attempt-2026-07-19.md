---
id: caplab-p7-live-second-retry-attempt-2026-07-19
artifact_type: execution-record
assertion_type: observation
campaign: caplab-study-001-p7-recompute-2026-07-18
authorization: adr-0020
status: stopped
---

# CAPLAB P7 stopped second live retry

## Scope

ADR 0020 authorized one execution of the exact second P7 retry. The executor
preserved both earlier stopped attempts, installed the selected versioned
controller, captured fresh pre-effect controls, enabled the bounded reader
identity, and started the first frozen recomputation. This record states
execution and cleanup observations. It is not independent verification, a
capability inference, another retry authorization, or acceptance.

## Observations

- The previous active evidence and disabled state were moved intact to
  `/var/tmp/caplab-p7-stopped-retry-2026-07-19`. Its 48-file archive passes
  `ARCHIVE_SHA256SUMS`; that manifest has SHA-256
  `cc0807b93ed9217ad9718b6ace19c2ee485d6a3e5ed40fdb3b041a40804bafca`.
  The first stopped-attempt archive remains unchanged and verifies with
  manifest SHA-256
  `5ad7259eaf6f85b2595e559835aebe9cdb134a8d4d4989b6dcd9473da8d5e`.
- The controller from pushed Proximal commit
  `031d20cceefa1f7f4bf5db9386d89383d763edf0` was installed with SHA-256
  `8f5b2378a772f1c5c1fd28031e0c9ac9a96b84f90c0270d2c48d85ce3be7d076`.
  Its nine lifecycle tests, isolated Ruff check, command help, systemd unit and
  calendar verification, diff check, and live read-only disabled-state query
  passed. The isolated Ruff invocation avoided an unrelated `/tmp/ruff.toml`
  inherited by the temporary exact-commit worktree; it did not alter source.
- A fresh root-owned `0700` evidence root captured 28 pre-effect files. The
  normalized whole-schema dump, cluster identity, P4 and P6 controls, Garage
  inventory, independent-copy hashes, install identities, frozen/current test
  gates, cardinalities, expiry timer, and disabled access state matched the
  authorized baseline. Counts remained 684 evidence records, 325 unique
  content identities, exact 20/20/20 assignment-attempt-outcome links, 326
  Garage objects, and 326 independent copies.
- Aggregate disablement was installed as the exit trap before `enable`.
  `enable` succeeded, and the installed controller passed
  `verify --phase ready`.
- The first frozen recomputation exited with status 2 and emitted the typed
  `CanonicalizationError` message `floating-point values are not identity-safe`.
  It emitted no result. The required byte-identical replay did not run.
- The exit trap completed aggregate disablement with status zero. The retained
  state is `disabled`; the P7 key and credential are absent; reader, writer,
  and verifier are `NOLOGIN`; and reader sessions and processes are zero.
- The normalized whole-schema dump, PostgreSQL summary and cluster identity,
  P4 and P6 controls, Garage information and key inventory, independent-copy
  hashes and symlinks, OS accounts, and source/install identities match their
  pre-effect observations.

## Diagnosis

**Inference:** the first divergence is a JSON-decimal parser asymmetry at the
recomputation identity boundary. Admission parses immutable JSON with
`parse_float=str` before it forms the registered historical observation.
Recomputation parses the same immutable bytes with default `json.loads`, which
creates a Python `float`; the subsequent identity-safe canonicalizer refuses
that value before it can compare the bytes with the registered observation.

The credible rival is corrupt or mismatched registered evidence. That rival is
weakened by the exact P6 manifest, pre-effect byte and cardinality controls, and
the fact that the refusal occurs during local canonicalization rather than
locator, digest, or historical-observation mismatch handling. A public
recomputation regression test must reproduce the parser divergence before this
inference can support a repair.

The smallest candidate repair is to apply admission's existing
`parse_float=str` policy at the recomputation immutable-byte boundary. It must
not catch or coerce arbitrary Python floats, weaken canonicalization, rewrite
historical evidence, or broaden live access.

## Evidence custody

The 51-file root-owned evidence set remains at
`/var/tmp/caplab-p7-execution-2026-07-18`. Its 50-entry `SHA256SUMS` file has
SHA-256
`b0d1b0269ea9b167e3e2ccdbe19dfca6e43e2707c2970a2c9880d0565a497cd6`
and passed verification after cleanup. It contains no Garage secret,
credential, recomputation result, or replay output.

## Result and boundary

**Execution result:** stopped during the first P7 recomputation. CAPLAB-25
remains open. ADR 0020 is consumed and authorizes no repair deployment,
changed frozen source, or further live attempt.

Doctrine packet `pkt-7f0f29d6d5486b26`, content SHA-256
`dc8c419ca1d8de7db545dc0735991c57cbb174ff9d8563cc1dd9262d6095cff8`,
supports a test-first repair of the first divergent parser boundary and
preserves the owner gate. ADR 0016 Stage A separately permits model-free
implementation and test work in the recomputation package through the existing
expiry; it does not permit another live run.
