# CAPLAB-23/P5 isolated-restore correction execution

Status: **stopped with the target preserved** on 2026-07-16. ADR 0011's
correction did not complete. Independent verification is recorded separately.

## Authority and frozen boundary

**Decision:** ADR 0011 selected campaign
`caplab-p5-isolated-restore-corrective-2026-07-16` for one isolated restore
retry only. It did not authorize dependency creation, byte deletion, purge,
tombstone creation, P6, P7, evidence admission, model calls, or acceptance.

| Surface | Frozen identity |
|---|---|
| ADR 0011 SHA-256 | `d110fd0e74285f22ecffb31e36eae256190a4eeaf50cd082cd14fc9c03cc15fb` |
| CAPLAB commit | `065c5d4a3461156a4765906f1f1a26110a26b565` |
| CAPLAB tree | `ebfe6b39bdbc9fd7f454085432e512835a1b06a3` |
| Proximal commit | `6850fba0ac3f1eefd9e12e56c3256d5949a0c13b` |
| Proximal tree | `acab8e877ccb9b06b3bde6f3915b4531e720471b` |
| Selected backup | `20260712-010203F_20260716-195901D` |
| Target | `/var/tmp/caplab-p5-pgrestore` |
| Port and socket | `55435`, `/var/tmp/caplab-p5-pgrestore/socket` |

Both repositories were clean and the Proximal commit was pushed. Fresh
verifier `/root/caplab_p5_isolated_verifier` returned PASS to the first host
effect in assignment report SHA-256
`f45bf4a9b3d338f99b73b783682040cfa3abfce561125e878ff226bc2895c260`.

## Execution observations

The executor preserved the stopped failed target's identity, live PostgreSQL
identity, selected backup, P4 and P5 controls, helper hashes, test evidence,
and verifier assignment in root
`/var/tmp/caplab-p5-execution.20260716T222255Z`. The old stopped target had no
PID, listener, mount boundary, or process reference and was removed exactly.

Committed Proximal helpers were installed with these SHA-256 values:

- common guard: `c9d16338a7c8accae5d69a1bcc911b84ad36585b20cc7a516621b530f16c31a8`;
- restore: `e6744b2c652730f27a44482a73df8521a87fb5a5120e7c50a70fceb1cc026897`;
  and
- stop: `5ed70997e2cf5c578b719f86540f3af62037f9508ff5e3ff93ef9d90b312482d`.

**Observation:** pgBackRest restored the selected backup successfully: 45.4
GB across 11,608 files. PostgreSQL used the generated target-owned config,
HBA, ident, and recovery-only auto configuration. It listened only on
`127.0.0.1:55435` and the target socket, obtained WAL through pgBackRest, and
entered recovery.

**Observation:** recovery then failed with direct status `1` because
`max_wal_senders = 0` was below the backed-up primary value `10`. PostgreSQL
reported insufficient parameter settings and shut the isolated postmaster
down. Receipt `004-restore-selected-backup-isolated` preserves the exact log.

**Inference:** the explicit recovery-time `max_wal_senders` setting is the
first observed blocker. A later restore or configuration defect remains a
credible rival because recovery did not proceed beyond this check.

## Safe stopped state

The failed target remains present with no `postmaster.pid`, target-named
PostgreSQL process, or listener on `55435`. Root state remains
`phase=starting`; its campaign, authorization, backup, target, port, socket,
live identity, and configuration hashes match the preserved target marker and
files.

The live cluster remained active at `/var/lib/postgresql/17/main`, port
`5432`, PID `2654541`, start time
`2026-07-03 06:16:25.66893+00`. Live P4 and P5 registration identities,
closure `1|1|0|0`, migration hashes, unprivileged `NOLOGIN` CAPLAB roles, P4
and P5 `/nvr` content hashes, and absent P5 credentials remained unchanged.

## Stop decision

ADR 0011 authorized one retry and requires a stop on restore mismatch. The
executor did not change the setting, retry, run the stop helper against the
non-queryable instance, remove the preserved target, or advance to purge or
P6.

Independent verification is in
[`caplab-p5-isolated-restore-verification-2026-07-16.md`](caplab-p5-isolated-restore-verification-2026-07-16.md).

