# Observe native launch and shutdown timing

Baseline `a3f02f1`. Primary agent under ADR 0026 and the continuing CAPLAB goal.

## Decision and prospective authorization

The preceding failed attempt completed fixed output but reached its 30-second
native deadline. Its unchanged trace now passes parentage and exact binary exec
inspection. Earlier successful native controls took about five seconds from
last stdout receipt to capture completion; the failed control left less time
than that after final output. These are observations from different attempts,
not a performance comparison or a cause of the timeout. The bootstrap polls
the native launcher directly; the outer capture completed before its own limit.

Select one fresh diagnostic with explicit monotonic timing in the bootstrap,
fixture request records and authenticated guard observation. At timeout, retain
bounded process state for the owned launcher and its direct children only:
at most eight PIDs, at most 4 KiB per proc file, status State/Tgid/PPid/Threads,
wchan and child PID list. Record unavailable proc reads explicitly; read no
environment, memory, credentials or arbitrary process tree. These are workload
observations, not trusted execution identity or a replacement for host evidence.

Authorize this record and private artifacts under `/tmp/caplab-native-shutdown-*`.
Derive the prior binary-link probe/support and controls, preserving original
hashes. Change owned paths, diagnostic timing fields and timeout state capture
only. Keep native installation, model/effort, prompt, fixed tool and response
bytes, effective native configuration, combined tracing, fabricated readonly
auth, quarantine, namespace/device/procfs controls and resource limits unchanged.
The guard program remains byte-identical. Pin all current source and installation
identities and run focused checks and five synthetic guard controls before launch.

Permit exactly one installed Codex 0.153.4 attempt, subject codex-terra-max,
gpt-5.6-terra, effort max, through the native-system policy and isolated local
two-response fixture. Retain 30/45/90/100-second native/capture/unit/outer limits;
256/512 MiB child/unit memory, zero swap, 128/192 PIDs; 300,000-byte native
streams, 1 MiB/1,000 task entries, 8 MiB/1,000 native-output entries,
40 MiB/2,000 retained-mount entries, 2 MiB trace and 8 MiB native files.
Keep five 64 MiB tmpfs mounts, six basic devices, bounded 1 MiB wire/decoded
HTTP requests, 32 requests and two response POSTs. No automatic retry.

No real credentials, external endpoint, provider inference, model spend,
historical research copying/admission/rewrite/purge, tracker write, message,
push or independent acceptance. Preserve unrelated docs/designs, worktrees,
services and all prior custody. Stop on drift, timeout, unsupported semantics,
quarantine or unexplained failure; retain partial evidence and inspect it without
retrying. Verify the owned unit/cgroup are absent. A failed run remains failed
even if it emitted final output. Do not increase limits or infer causation from
one observation. Commit the verified record locally; authorization expires there.
Full capture binding, representative repair, study eligibility and capability
claims remain unavailable.

No change cannot locate the delay. Changing timeout, logging configuration or
workload simultaneously would confound this diagnostic. Official non-interactive
documentation describes turn events but does not establish this installation's
shutdown latency; installed wrapper source waits for its native child's exit.

## Preflight and release

The derived probe is SHA-256
`f69f7f5611e7a18f356980a3ba372dc0a2f7379a41513eec4d773c94c930d155`;
support is `cfa2bf9f75424372ab4f75e9cd9c9ab8f5e3f30ee0d0df59e76d9bb2ce679ed0`.
Seventeen repository source pins match the current commit; only the explained
process-trace parser differs from the preceding diagnostic. Installation,
Node, tracer, decoder and canonical plan identities agree. Guard bytes are
unchanged, and AST checks confirm unchanged fixed response and request-decoder
functions. All 18 shared trace tests and five synthetic guard controls pass.
The bounded proc snapshot observes the current control process and explicitly
reports a nonexistent PID as unavailable. No native agent ran in these controls.

Ruff F passes for the probe/support, guard controls and prepared verifier. The
separately extracted bootstrap exposes an existing unused `parse_qs` import;
it is retained to preserve the selected scope and does not affect execution.
The diagnostic clocks have no role in release authorization or success criteria.
Proceed with the single native attempt; any outcome consumes the allowance.

## Failed attempt and timing observations

Unit `caplab-native-shutdown-96590fe2e5754bd7afaacc7e34991e97.service`
consumed the allowance and failed at the native deadline. Native return code
is -9, bootstrap return is 1, and the outer capture finished with complete
streams before its own 45-second limit. No retry occurred. Both fixed response
POSTs returned 200; the tool completed with exact witness bytes, followed by
the exact final response and turn.completed. These do not establish normal exit.

The monotonic observations, in seconds, are:

| Interval | Observed |
| --- | ---: |
| Popen call | 0.019 |
| Guard accept to before observation sealing | 0.012 |
| After spawn to first fixture request | 6.513 |
| After spawn to first response POST | 23.334 |
| After spawn to final response write | 25.952 |
| Last stdout receipt to deadline observation | 3.421 |
| Native polling lifetime | 30.030 |
| Timeout snapshot plus kill/wait | 0.033 |
| Longest observed fixture request handling | 0.029 |

At timeout, namespace launcher PID 4 had seven threads and waited in ep_poll;
its direct native child PID 11 had 22 threads and waited in futex_wait_queue.
Both reported sleeping state. The snapshot omitted no direct children. These
wait sites are instantaneous observations, not evidence of a deadlock or its
cause. They do not describe every thread's activity.

The guard checks and observed fixture request handling were brief. Most elapsed
time preceded the first successful response POST, and final output left less
than the roughly five-second post-output interval observed in earlier successful
controls. This distinguishes the native deadline from an outer capture timeout
and narrows investigation toward startup/retry time and observation overhead.
It does not attribute the delay to tracing, native cleanup, telemetry, provider
behavior or machine load. No limit change or performance conclusion follows.
Prior intervals are source-anchored receipt observations, not exact native exit
times or a controlled comparison; capture completion includes supervisor cleanup.

## Additional trace evidence and custody

Authenticated launcher/Node exec, exact native binary exec and tracer consistency
checks pass. Raw parent creation is line 20 and native exec is line 21. The full
public parentage reader refuses a different record at line 681:
`= ? ERESTARTNOINTR (To be restarted)`. The interrupted clone began at line 678;
SIGCHLD follows at line 683, and a later clone completes at lines 684–686. The
first auditor's refusal is retained, and the final failure auditor records it
without skipping the line or changing the parser. Public parentage remains
unverified in this run. This provides a concrete subsequent parser investigation.

Trace SHA-256 is
`93cd81cebb8300ce1347470dea04aa058cd38a5fc3608ea630c36647f5be78de`,
1,797,024 bytes. Retained mounts contain 1,000,825 bytes across 130 entries.
The failure audit verifies component custody with explicitly post-failure
anchors, checks 112 files and 6,327 decoded hex strings against configured
forbidden synthetic values, and finds no matches. No auth change, fixture
error, quarantine, memory max/OOM or PID max event was observed. Final child
PID count is zero. The unit is not found and its cgroup is absent.

Original success reports were withheld. Strict final-message linkage still
refuses retained transport errors, despite exact final-byte agreement. The
timing audit is `/tmp/caplab-native-shutdown-timing-audit.json`; its source and
failure audit retain the full fields and independent anchors. No repository
runtime/test source changed. Eighteen focused tests, five guard controls and
the snapshot controls passed; the last full suite remains 1,371 tests with four
skips at `a3f02f1`. Those checks do not override the failed native result.

## Advisory review and disposition

The release gate verified fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial `pkt-dbf607954cacf411` and final Markdown packets were read. Five typed
records retain authority, incident, source, controls and runtime observations.
Final packet `pkt-acc881405df950ba` has SHA-256
`acc881405df950bac7eb0b458794685f886d9a0f6c24c6b458e0bbfbc60de106`;
versions remain corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
Five applied concepts are repository-contract precedence, evidence before
intervention, authority-bounded action, preservation outside scope, and
separating diagnostic work from semantic repair. Citation classifications are
valid. Ruff F passes for live probe/support, controls and both final auditors.

All 28 missing obligations remain explicit. Deduplication (3), population
discovery (4), asynchronous UI (4), declarative references (3), ranking (4)
and monitoring (3) are nonmaterial to unchanged surfaces. External capability
(3) and full readiness-gate verification (4) remain material to broader native
integration, performance and study-readiness claims, which are withheld.

Next, reconcile the observed restarted-clone record with explicit semantics and
regression evidence. Further native investigation must distinguish startup/retry
time and observation overhead from shutdown behavior; this run does not justify
changing the deadline. This attempt's allowance is consumed. The broader CAPLAB
goal remains active, with representative repair and full capture linkage open.

## Final custody

Manifest `/tmp/caplab-native-shutdown-verification.json`, SHA-256
`eee968ec4dad28cb2a1be08285ade1653a1a9842b2053c675771084b0fb651f4`,
retains 199 artifacts, 17 repository source identities and 11 advisory scratch
files embedded and removed after exact verification. Artifact, source and typed
provenance hashes agree. The owned unit and cgroup were checked absent again.
The local record commit closes this diagnostic authorization. No native retry,
repository runtime change, model spend, tracker write or independent acceptance
occurred.
