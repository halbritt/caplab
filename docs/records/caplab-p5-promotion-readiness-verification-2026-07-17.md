# CAPLAB-23/P5 promotion-readiness correction verification

Result: **PASS for the ADR 0013 correction; PASS for the live-cluster safety
boundary**.

Fresh verifier `/root/caplab_p5_adr0012_preflight` completed the read-only
final assessment on 2026-07-17. The verifier did not implement or execute the
correction. The full preserved report SHA-256 is
`7a8d8e6f8688f69fd35ce9d3720dac4b7aa6d942c5c65c5f4ff0c849eb93c2ad`.

## Supported observations

- Exact backup `20260712-010203F_20260716-195901D` restored 45.4 GB across
  11,608 files into the fixed isolated target.
- The target used its own configuration, HBA, ident, socket, and loopback port
  `55435`. Isolated PID `1027021` never aliased live PID `2654541`.
- Recovery accepted `max_wal_senders=10`, obtained WAL, reached consistency,
  selected timeline 2, and completed automatic promotion.
- The new wait observed the real `t` then `f` recovery-state transition in two
  polls, with a live-identity proof before its one-second sleep.
- Effective recovery state was `false`; active replication senders were zero;
  and the real TCP probe was rejected by the target HBA.
- Restored read-only queries matched both migration records; exact P4 and P5
  request, content, manifest, artifact, and registration identity hashes; one
  row for every linked identity; and closure `1|1|0|0`.
- The independent interim PASS was preserved before the exact guarded stop.
  The stop helper stopped only the isolated PID and changed the external state
  to `phase=stopped`.
- Exact queryable and stopped snapshots were preserved. A separately reviewed
  removal helper removed only `/var/tmp/caplab-p5-pgrestore` and
  `/var/lib/caplab-p5-isolated-restore.state`.
- The target, external state, PID, port listener, Unix socket, process, and
  process references are absent.
- The live cluster retains the exact data directory, port, PID, start time,
  active state, P4/P5 controls, registered local bytes, and credential absence.

Receipt `002-post-install-precleanup-check` returned status `1` because shell
quoting broke its local expected-output literal after matching read-only
hash, live, and backup checks. It made no target or database change. Corrected
standalone receipt `002b-post-install-precleanup-check` passed the complete
hash, listener, backup, live, P4, P5, and closure gates before the old target
was removed or the retry began.

## Verification judgment

**PASS for ADR 0013's correction:** the fixed promotion wait removed the
observed readiness race, all restored identity and content checks passed, the
required interim evidence was preserved, and guarded shutdown and exact
removal completed.

**PASS for the safety boundary:** the isolated restore addressed only its
fixed target, socket, and loopback port. HBA rules rejected TCP and
replication paths. Stop and removal could not name or traverse the live data
directory, and every final live identity and CAPLAB control matches the
pre-effect freeze.

## Residual authority

These PASS verdicts verify the ADR 0013 isolated-restore correction only. The
one retry is consumed. They do not pass or accept P5, authorize dependency
creation or P5 byte deletion, authorize database purge or a tombstone,
authorize P6 or P7, admit historical evidence, authorize another retry, or
authorize a live PostgreSQL change. Those effects require a new explicit
decision and authorization.
