---
id: caplab-p7-live-recomputation-execution-2026-07-20
artifact_type: execution-record
assertion_type: observation
campaign: caplab-study-001-p7-recompute-2026-07-18
authorization: adr-0022
executor: primary-agent
executed_at: 2026-07-20
status: complete
---

# CAPLAB P7 live recomputation execution

## Authority and boundary

ADR 0022 authorized one exact fourth P7 attempt after the regular-file runtime
custody correction. The execution used CAPLAB source
`bf6de2b24ac61e82107208cdc609c7e534c6eaaa`, Proximal desired state
`1b79aa07cc4e44e8fc828449f882c6b62008edb6`, and P6 admission manifest
`d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`.

This record reports execution and executor validation. It is not capability
inference, training eligibility, export authorization, CAPLAB-33 independent
verification, or CAPLAB-34 acceptance.

## Pre-effect observations

- The three earlier stopped-attempt archives verified unchanged. The third
  retry evidence was moved to
  `/var/tmp/caplab-p7-stopped-third-retry-2026-07-19` and sealed as a fourth
  archive. Its 59-entry `ARCHIVE_SHA256SUMS` has SHA-256
  `9f01070a14a37d7fd0e8cd04932614499bfca28146650fb2fd74a7fe28da2819`.
- CAPLAB and Proximal were clean and pushed at their bound commits. The 105
  CAPLAB tests and ten controller tests passed.
- The installed runtime interpreter was a regular, non-symlinked
  `root:caplab` mode-0750 file with SHA-256
  `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118`.
  Its 50-file CAPLAB source inventory had manifest SHA-256
  `fd32d932f2dd90ef486ec199b8fd9930eb69a11aeea86ed107a77d9cd299f322`.
- The expiry timer was active and enabled. PostgreSQL contained the one P6
  registration, 684 evidence records, 325 unique objects, 11 identity kinds,
  and exact 20/20/20 attempt-assignment-outcome links. Garage and `/nvr` each
  retained 326 objects. Reader, writer, and verifier access was disabled with
  zero sessions and no P7 credential, key, state, or reader process.

The capture procedure stopped twice before enablement while its own test-user
and SQL-column assumptions were corrected. Those capture-only stops are
retained in the evidence. They changed no product or access state. A postflight
comparison also exposed PostgreSQL 17's random `\restrict` wrapper token; both
raw dumps are retained, and only those wrapper lines were removed from the
normalized comparison.

## Execution observation

The versioned controller enabled one temporary `caplab_reader` identity and
passed `verify --phase ready`. The frozen model-free recomputation ran twice.
Both invocations returned zero and emitted the same canonical bytes. The
output file has SHA-256
`48e7e3817cb53c4a78c51442777196aafc6e5e12d535fc7ae2c06d1f7a3ba55b`;
the content-addressed observation manifest is
`68845b0ce21fe30e21b5e46f988c624bef85b6eaf3d02319f24c8e7992e7c6d1`.

The result is an observation with normalized-result SHA-256
`6c4deff865354c78835741bcbbead517828e207db16452469872dfb363dbaab8`.
It has eight defined mutant-arm blocks, harmful counts `B=8` and `V=0`, risk
difference `8/8`, one-sided exact permutation probability `1/256`, two-sided
probability `2/256`, and `confirmatory_criterion_met=true`. Its historical
comparison is byte-identical. Capability inference, cross-task capability,
preference, universal ranking, Striatum placement, and training eligibility
remain `unavailable`.

## Disablement and preservation

The installed exit trap ran aggregate disablement after validation. Both
`disable` and `verify --phase disabled` returned zero. The P7 Garage key and
credential are absent; all three PostgreSQL roles are `NOLOGIN` with no
password, zero related sessions, and zero reader processes.

Exact pre/post comparisons passed for both repository identities, installed
host and runtime files, the complete PostgreSQL data dump, cluster start
identity, P4 and P6 records, Garage bucket and key inventory, all 326 `/nvr`
hashes, symlink inventory, OS accounts, timer, and all four stopped-attempt
archives.

The fresh root-owned evidence remains at
`/var/tmp/caplab-p7-execution-2026-07-18`. Its 72-entry `SHA256SUMS` has
SHA-256
`42b57e7c7dc38786f32267e6e2f63031cc56e335e592688470d47dcee2ac94e6`
and verifies. The evidence contains the recomputation observation but no live
Garage secret.

## Result

**Execution result:** complete. CAPLAB-25/P7 produced the bound mechanical
observation, byte-identical replay, historical match, aggregate disablement,
and preservation proof required by ADR 0022. P8 and P10 may consume this
observation under ADR 0016. P9, P11, P12, P13, and P14 remain separately
gated.
