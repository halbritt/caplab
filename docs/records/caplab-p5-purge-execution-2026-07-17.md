# CAPLAB-23/P5 exact purge execution

Status: **completed** on 2026-07-17. ADR 0014 Stage A executed the remaining
exact P5 dependency and purge sequence. A fresh independent verifier returned
PASS. This is P5 verification, not CAPLAB acceptance.

## Authority and checkpoints

The repository owner explicitly authorized the restated P5-then-P6 boundary;
ADR 0014 records that authority. ADR 0015 corrected only the controller's
source location after the first read-only preflight safely refused the
advancing shared checkout. No mutation preceded that refusal.

| Surface | Identity |
|---|---|
| ADR 0014 commit | `0f61c3619fdfb45c9163383c24cac3a8345c8bf5` |
| ADR 0015 commit | `ffb428b3cd2438f80dc7d358720d3f6a62224409` |
| Frozen P5 executor source | `e86ed0ecd734b902be2afcd0d20d5a07225c2579` |
| Proximal correction | `2e95ecd97468af1cac4ec7a552827a45619a2970` |
| P5 operation | `op-p5-recovery-0001` |
| Custody request | `custody-p5-final-20260717` |
| Content SHA-256 | `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d` |
| Evidence root | `/var/tmp/caplab-p5-execution.20260717T220619Z` |
| Evidence manifest SHA-256 | `93931de9929b8ae4beedbd91d22a40cf39effa0b1a70486dbcb4bb7163df3e0b` |

The Proximal correction was committed and pushed before installation. Its 16
tests, Python compilation, Bash syntax, systemd verification, and diff check
passed. The installed controller matched its committed SHA-256. The dedicated
detached CAPLAB source worktree was clean at the original executor commit.

Independent pre-effect verification returned PASS in report SHA-256
`31f392bcb9a02ee3f6e280528229f457b3047f3ba26288e7340544b34f6e29b5`
before credentials, custody rows, byte deletion, or purge.

## Execution observations

Temporary P5 operating-system, PostgreSQL, and Garage access was recreated
under the original expiry. The frozen P5 registration reconciled with both
byte stores and all identity layers. Its initial orphan inventory was empty.

Custody request `custody-p5-final-20260717` was created. Retained campaign
dependency `caplab-p5-final-gate-20260717` caused the guarded PostgreSQL
procedure to refuse with SQLSTATE `P5004` and direct numeric status `1`.
Closure remained `1|1|1|0|1`: operation, registration, custody request, no
tombstone, one dependency. The matching release event cleared the current
dependency inventory.

The executor reconciled both P5 stores immediately before staging. Two
root-only rollback copies were staged and each matched the exact P5 content
SHA-256. Only the exact content-addressed P5 Garage object and `/nvr` copy were
removed. Subsequent verification returned the expected `ObjectMismatch` with
direct numeric status `2`.

The exact custody request then invoked only
`caplab_v0.purge_p5_operation`. It returned a tombstone at
`2026-07-17T22:18:40.092397Z` with the frozen operation, request, content,
manifest, and ADR 0010 authorization identities. The retained row counts are:

| Row class | Deleted |
|---|---:|
| operation requests | 1 |
| operation events | 8 |
| audit events | 1 |
| registrations | 1 |
| manifests | 1 |
| attempt artifacts | 1 |
| artifacts | 1 |
| attempts | 1 |
| trial assignments | 1 |
| trial contexts | 1 |
| administrations | 1 |
| agent configurations | 1 |
| model identities | 1 |

Post-purge state was `0|0|1|1|0`: no P5 operation or registration, one
custody request, one tombstone, and no current dependency. The bucket retained
only the 98-byte P4 object. P4's local content remained SHA-256
`87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`.

## Disablement, cleanup, and preservation

Temporary Garage keys and credential files were removed. The P5 operator,
verifier, and custodian PostgreSQL roles are `NOLOGIN` with no password. The
two P5 operating-system accounts are disabled by the host controller. The
isolated target, external state, socket, process, and port `55435` listener
remain absent.

The live PostgreSQL cluster retained its data directory, port `5432`, and
start identity. P4's exact registration, Garage object, and `/nvr` byte were
unchanged.

After independent final PASS, the root-only rollback copies were removed. The
temporary frozen CAPLAB source worktree and Proximal correction worktree were
removed and both worktree registries pruned. The pushed Proximal branch and
commits remain durable history.

The root-only execution directory contains 52 command groups, direct numeric
status receipts, the two independent reports and sidecars, and 213 files total
including `SHA256SUMS`. `sha256sum --check --quiet` passed before the manifest
hash above was recorded.

## Scope result

CAPLAB-23/P5 passed independent verification. Backup copies are not claimed to
have been physically deleted; they expire under their governing schedules.
No historical evidence was admitted, no P6 effect occurred during Stage A,
and no P7, recomputation, model call, inference, export, training, publication,
or acceptance effect occurred.
