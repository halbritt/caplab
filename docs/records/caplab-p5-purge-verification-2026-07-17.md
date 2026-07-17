# CAPLAB-23/P5 exact purge verification

Result: **PASS for ADR 0014 Stage A and CAPLAB-23/P5**.

Independent verifier `/root/caplab_p5_adr0012_preflight` did not implement or
execute the purge. Its root-only final report SHA-256 is
`751a27c2900d7271c50749cfc45c5775c4f84eb9e1c44b0cc755376bf416ba50`.
The report and checksum sidecar are `root:root` mode `0600`, and the sidecar
verification passed.

## Supported observations

- Every Stage A success has a direct numeric status-0 receipt.
- The dependency-bearing purge rehearsal returned SQLSTATE `P5004` and direct
  status `1` without changing the P5 closure.
- The matching dependency release left no current dependency or shared
  identity.
- Both root-only staged copies matched the frozen P5 content identity before
  deletion.
- Only the exact P5 Garage object and `/nvr` copy were removed; byte
  verification then failed closed with `ObjectMismatch` and direct status `2`.
- The guarded transaction deleted the complete exact P5 application closure
  and retained a tombstone with the frozen custody, operation, request,
  content, manifest, and authorization identities plus complete row counts.
- P5 live application rows and bytes are absent; the custody request and
  tombstone remain; no dependency remains.
- P5 credentials and Garage keys are absent, P5 PostgreSQL roles are
  `NOLOGIN`, and the lifecycle phase is disabled.
- The isolated restore and port `55435` listener remain absent.
- The live PostgreSQL cluster identity is unchanged.
- The exact P4 registration, 98-byte Garage object, and `/nvr` SHA-256 are
  unchanged.
- The rollback staging and temporary P5 worktrees were removed only after the
  independent PASS.

## Verification judgment and residual authority

The previous P5 failures remain truthful historical records. Together with the
ADR 0013 correction and this exact purge, every mandatory ADR 0009/0010 P5
criterion is now supported. CAPLAB-23 may be projected Done.

The PASS opens only ADR 0014 Stage B/CAPLAB-24/P6. It does not accept CAPLAB or
authorize P7, recomputation, model calls, capability inference, export,
training, publication, or any change to the historical source repository.
