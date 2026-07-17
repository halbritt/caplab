# CAPLAB-23/P5 promotion-readiness correction execution

Status: **completed** on 2026-07-17. ADR 0013's bounded correction passed its
runtime criteria, and the verified isolated target and state were removed.
Independent verification is recorded separately. This is not P5 acceptance.

## Authority and frozen boundary

**Decision:** ADR 0013 selected campaign
`caplab-p5-promotion-readiness-corrective-2026-07-17`, a fixed 30-second
promotion wait, and one isolated restore retry. It retained every ADR 0012
target, HBA, replication, TCP, PID, configuration-hash, and live-cluster
guard. It did not authorize a second retry, dependency creation, byte
deletion, database purge, tombstone creation, P6, P7, model calls, evidence
admission, or acceptance.

| Surface | Frozen identity |
|---|---|
| ADR 0013 SHA-256 | `2e2660cebd6d2b35704b9ffe3b586997ff639eebe1df08fbf7348f3950baa075` |
| CAPLAB commit | `54535bb92b8a79590ecfdc3cde713c655ccf35b5` |
| CAPLAB tree | `f9e0e807a7aaece914a472611a38d04b792d4d1d` |
| Proximal commit | `430eb40178a2f447d361a7fed666480d1f2f7c39` |
| Proximal tree | `dc86e4dd8abee561d57ba923b7af26328b749a5c` |
| Selected backup | `20260712-010203F_20260716-195901D` |
| Target | `/var/tmp/caplab-p5-pgrestore` |
| Port and socket | `55435`, `/var/tmp/caplab-p5-pgrestore/socket` |

Both repositories were clean and the Proximal commit was pushed before the
first host effect. Independent preflight verifier
`/root/caplab_p5_adr0012_preflight` returned PASS in report SHA-256
`6747d5a415e43dbd153829a52ef273ecdb026c063ec99b5b94e8aba71745a7a9`.
Its independent timeout harness observed status `1`, 30 elapsed seconds, 31
polls, and 30 live-identity checks.

## Source and pre-effect verification

The focused test first failed because `wait_for_isolated_promotion` did not
exist. After the bounded change, it reproduced a `t` then `f` recovery-state
sequence and proved two polls with one intervening live check. It also proved
that unexpected recovery values and query errors remain failures.

All 14 P5 host-surface tests, Bash syntax, host-controller help, systemd
verification, and `git diff --check` passed. ShellCheck was not installed.
The installed helper checkpoint matched the committed files:

- common guard:
  `4f190717f519cde40f40b4e3eac4aa77dda16ade368026f30ee80e4e34971d90`;
- restore:
  `ae2c679b4016f438db60a04809340c034f10aa6f8c8ee646b76bd77ce48f2041`;
  and
- stop:
  `5ed70997e2cf5c578b719f86540f3af62037f9508ff5e3ff93ef9d90b312482d`.

The prior stopped target matched all seven hashes frozen in ADR 0013. It had
no PID, TCP or Unix listener, mount boundary, or process reference. Exact
guarded removal returned status `0`; the live PostgreSQL identity and P4/P5
controls remained unchanged.

One inline post-install receipt, `002-post-install-precleanup-check`, returned
status `1` after its read-only checks because shell quoting split a local
expected-output literal. It performed no target or database mutation. The
executor preserved that failure, replaced the inline literal with an
inspectable checkpoint script, and receipt
`002b-post-install-precleanup-check` passed the complete hashes, backup,
listener, live-identity, and P4/P5 control gates before cleanup or restore.

## Execution observations

Evidence is preserved under root-only execution directory
`/var/tmp/caplab-p5-execution.20260717T193535Z`.

**Observation:** pgBackRest restored the exact backup successfully: 45.4 GB
across 11,608 files. PostgreSQL started with the target-owned config, HBA,
ident, socket, and loopback port. It obtained the required WAL, reached
consistent read-only recovery, selected timeline 2, completed promotion, and
became ready for read-write connections.

**Observation:** the helper sampled `pg_is_in_recovery()` twice. The first
result was `t`; after one live-identity proof and one-second sleep, the second
was `f`. The helper then proved `max_wal_senders=10`, zero active replication
senders, and HBA rejection of a real TCP connection to `127.0.0.1:55435`.
The isolated PID was `1027021`, distinct from live PID `2654541`.

**Observation:** read-only restored-database queries returned:

- migrations `0001_runtime_core.sql` and
  `0002_p5_recovery_custody.sql` with their recorded file hashes and runtime
  commits;
- the exact P4 content and manifest identities;
- the exact P5 request, content, manifest, object key, local-copy key, seven
  registration identity hashes, and analysis hash;
- one matching row for the manifest and each of the six referenced identity
  tables; and
- P5 closure `1|1|0|0`.

Fresh interim verification returned PASS and opened only the guarded
stop/removal gate. Its report SHA-256 is
`d620cd81df665e774c8d7359ecbbc8208f2c5af8f15d5325cf4d0582abc70557`.

## Guarded shutdown and removal

The committed stop helper rechecked phase, campaign, authorization, state,
marker, configuration hashes, target endpoint and PID, and the live identity.
It stopped only isolated PID `1027021`, changed the external state to
`phase=stopped`, and returned status `0`.

The stopped state, marker, and `pg_control` SHA-256 values were respectively
`d499f27bd4418bbde0a6c8443c4e90eb546867169e45a9d2c2484d7c479f424e`,
`29de3fde34d877aefbd6a953094cfb1a641f16d8483909301c132bb0520b1ed8`,
and `aab91c81de055b2645436acac4a412763552bb6c39f852180281e303b6799384`.
An independent removal precheck returned PASS in report SHA-256
`ee4a16ad24afd77efc45c907c525b8683534034a06c15484ec9e76f8d377a0fb`.

The exact guarded removal returned status `0`. The target and external state
are absent, and port `55435` has no listener. The live cluster remains active
at `/var/lib/postgresql/17/main`, port `5432`, PID `2654541`, start time
`2026-07-03 06:16:25.66893+00`. P4 and P5 registration identities and P5
closure `1|1|0|0` remain unchanged.

## Scope result

ADR 0013's isolated promotion-readiness blocker is removed. The one retry is
consumed. No dependency was created, no P5 bytes or database rows were
deleted, no tombstone was created, and P6 was not entered. Passing this
correction does not pass P5, accept CAPLAB, or authorize the remaining purge
sequence.
