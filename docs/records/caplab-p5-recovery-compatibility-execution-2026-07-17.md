# CAPLAB-23/P5 recovery-compatibility execution

Status: **stopped with the target preserved** on 2026-07-17. ADR 0012's
correction did not complete. Independent verification is recorded separately.

## Authority and frozen boundary

**Decision:** ADR 0012 selected campaign
`caplab-p5-recovery-compatibility-corrective-2026-07-17`, the explicit
recovery-compatible value `max_wal_senders=10`, stronger replication and TCP
isolation proofs, and one isolated restore retry. It did not authorize a
second retry, dependency creation, byte deletion, purge, tombstone creation,
P6, P7, evidence admission, model calls, or acceptance.

| Surface | Frozen identity |
|---|---|
| ADR 0012 SHA-256 | `7dabe6891bc1679ccbad4a893ba864ba42a59a301cbce472de15a2b03fbd64f0` |
| CAPLAB commit | `b32ed4ea74971c526fe631c34d2d5d8903b4385a` |
| CAPLAB tree | `0592902eb23b0ae588f0489083cfa2c71c790dba` |
| Proximal commit | `06a2d292871284cd2dad7efdad0998f41ed390e5` |
| Proximal tree | `2867f1f340fd2894a4fd6d2953536f0599356673` |
| Selected backup | `20260712-010203F_20260716-195901D` |
| Target | `/var/tmp/caplab-p5-pgrestore` |
| Port and socket | `55435`, `/var/tmp/caplab-p5-pgrestore/socket` |

Both repositories were clean and the Proximal commit was pushed. Fresh
verifier `/root/caplab_p5_adr0012_preflight` returned PASS to the first host
effect in report SHA-256
`a46f930e3769a9ff3efca859941b758c3bb57657a6056e3cd1c3d98225ac6713`.
The verifier first found that the target-removal helper did not explicitly
detect a Unix-domain listener. Execution remained paused until that helper
refused both TCP and target-socket listeners and the verifier passed its new
SHA-256
`fe465984a93940733542dcd60d424d85580462ff9dd4230dd74be477a78d8b1e`.

## Source and pre-effect verification

The focused source-contract test failed before implementation because the
helper still contained `max_wal_senders=0` and lacked the explicit replication
HBA. After the bounded change, all 13 P5 host-surface tests, Bash syntax,
host-controller help, systemd verification, and `git diff --check` passed.
ShellCheck was not installed.

The installed helper checkpoint matched the committed files:

- common guard:
  `d092ff9ea5348c7f4aeb479bfe9ee6f16e2c54069881e62a37948ca6f9cf76ee`;
- restore:
  `abb2edfe247d684fc7b375de7f8d2f25a7b6616a58489ae400e5c3795c4cbd49`;
  and
- stop:
  `5ed70997e2cf5c578b719f86540f3af62037f9508ff5e3ff93ef9d90b312482d`.

The prior stopped target and old state matched their frozen hashes. They had
no PID, TCP or Unix listener, mount boundary, or process reference and were
removed exactly. The live PostgreSQL identity and P4/P5 controls remained
unchanged after removal.

## Execution observations

Evidence is preserved under root-only execution directory
`/var/tmp/caplab-p5-execution.20260717T061628Z`.

**Observation:** pgBackRest restored the selected backup successfully: 45.4
GB across 11,608 files. PostgreSQL started with the target-owned config, HBA,
ident, loopback port, and target socket. It accepted
`max_wal_senders=10`, obtained the required WAL, reached a consistent
read-only recovery state, and did not repeat ADR 0011's compatibility refusal.

**Observation:** the helper queried the target through its Unix socket. A
real TCP connection to `127.0.0.1:55435` was rejected by the target HBA for
user and database `postgres`. The server log then selected timeline 2 for
promotion.

**Observation:** the helper returned direct status `1` with
`isolated PostgreSQL identity differs from the authorized target`. Its exit
guard issued a fast stop only after verifying the isolated endpoint and PID.
The preserved target has no `postmaster.pid`, TCP listener, Unix listener, or
target-named PostgreSQL process. Its external state remains `phase=starting`.

**Observation:** stopped-target `pg_controldata` reports
`max_wal_senders setting: 10` and `Database cluster state: shut down in
recovery`.

**Inference:** the new blocker is a promotion-readiness race.
`pg_ctl --wait start` returned when PostgreSQL began accepting read-only hot
standby connections. The helper sampled `pg_is_in_recovery()` before
promotion completed, so the combined identity check saw recovery still active
and failed. The log's later timeline selection and the preserved control state
support this explanation. An unprinted second identity mismatch is a weaker
credible rival, but the fixed settings, successful queries, HBA rejection,
and control data do not support one.

## Safe stopped state

The preserved state and target configuration hashes are:

| File | SHA-256 |
|---|---|
| external state | `1d3190a64e8c075896cc075a5575e8fa2e66ddff74d26d2480725dffc404b457` |
| target marker | `e2acf41d67ca82aa45574c924bebe383badbce25c872948c148229d513d9c091` |
| PostgreSQL config | `632c8645255e011912303dd01e0defb1b043f70fabd012b52301c114581dbbbb` |
| HBA | `accbc912e975cc95301833f8c161320c462283f5ab10c08bc53e28aba26c66ef` |
| ident | `87311bfe1b17cb2b0f376c8ffebbfdaf2590b6ac675b1b6d8edecfc146461f3f` |
| auto config | `7485cdb76d33628049b0958f3fe25e05e77e1709b91feebe4a162846784eeb0b` |
| `pg_control` | `ece280302cf3fc1e7f3086f5d1e39e23573dd65cb1a259305de4a7be2992f75d` |

The live cluster remained active at `/var/lib/postgresql/17/main`, port
`5432`, PID `2654541`, start time
`2026-07-03 06:16:25.66893+00`. P4 and P5 registration identities and P5
closure `1|1|0|0` remained unchanged.

## Stop decision

ADR 0012 authorized one retry and requires a stop and preserved state on any
identity mismatch. The executor did not retry, remove the new target, create a
dependency, delete bytes, purge database state, or enter P6.

Independent verification is in
[`caplab-p5-recovery-compatibility-verification-2026-07-17.md`](caplab-p5-recovery-compatibility-verification-2026-07-17.md).
Its full preserved report SHA-256 is
`5cee24d03c0594b6c01cf5f55a370b385fa414c65a60ab915f7f8997c57d06de`.
