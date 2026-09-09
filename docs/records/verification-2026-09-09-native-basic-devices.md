# Adopt the verified device profile in a native tool diagnostic

Baseline `bb62d6a`. Primary agent under ADR 0026 and the continuing CAPLAB goal.
The preceding native run passed the procfs handoff but its command failed on
missing `/dev/zero`. The new closed device profile passed real nested `--dev`
execution, the installed bundled Bubblewrap control, device/terminal refusal
tests and the 1,343-test suite. Native task completion remains unverified.

## Decision and prospective authorization

Authorize this record and private artifacts under
`/tmp/caplab-native-basic-devices-*`. Derive one probe from
`/tmp/caplab-native-nested-probe.py`, SHA-256
`f3b8e219cfbb5d093076dda0230d1f0445b957ae9ecc37005c8e8711bffc5705`.
Change only the owned prefix, four additional explicit device binds (zero,
full, random and tty), and selection of `usable_devices='bwrap-basic-v1'`.
Preserve `nested_userns=True`, root read-only, bootstrap bytes and all native
invocation, prompt, scripted-response, capture, decoder, tracer and resource
configuration. Pin current sources before launch; exactly the two device-profile
helpers may differ from the preceding preflight, as committed in `bb62d6a`.
Require the installed harness and all other pins to remain unchanged.

Permit exactly one installed Codex 0.153.4 diagnostic, native subject
codex-terra-max, model gpt-5.6-terra, effort max, through the repository policy
builder. Keep workspace-write sandboxing and the fixed local command/final
exchange. Authentication remains newly fabricated and read-only. There are no
real credentials, external model/provider endpoints or model spend. Keep private
loopback, unshared user/PID/mount/network namespaces, zero peer capabilities,
NoNewPrivs, no controlling terminal and the six exact checked character devices.

Preserve five 64-MiB tmpfs mounts, 8-MiB per-file limit, no core or swap,
256/512-MiB child/outer memory, 128/192 child/outer PID limits, and
30/45/90/100-second native/capture/unit/outer limits. Keep 300,000 child stream
bytes, 1-MiB task files, 8-MiB selected native artifacts, 40-MiB/2,000-entry
full-mount retention, and the fixture's 1-MiB wire/decoded bodies, 32-request
ceiling and two-response-POST ceiling. Stop on the first fixture error.

Before launch verify exact derivation, source hashes, installation and the
unchanged native plan. After launch require successful native command output,
the exact UTF-8 witness in captured task bytes, the fixed final message, two
successful response POSTs and natural native completion. Inspect actual Codex
status in the filtered trace; launcher or tracer zero alone is insufficient.
Keep exact-invocation linkage, native projection completeness, work correctness
and study eligibility separate. Preserve failures without replacing criteria.

Quiesce/reap only owned processes, close fixture/listener/input descriptors,
verify all capture hashes and recorded procfs/device/resource predicates, then
remove and verify absence of the exact owned unit and its cgroup. Recheck source
and installation identities. No automatic retry. No repository runtime change,
tracker write, message, push, historical research evidence effect, study adoption
or independent acceptance. Preserve `docs/designs/`, other worktrees and services.
Commit the resulting record locally; the one-attempt allowance expires there.

The successful component control earns this native test; it cannot replace it.
Leaving the old two-device probe unchanged preserves the observed missing-device
failure. Neither disabling the native sandbox nor binding the whole host /dev
is selected.

## Preflight and launch

Exact derivation, bootstrap equality, native-plan equality and the full
installation manifest passed. The 13 source pins match committed `bb62d6a`;
only the two authorized helpers differ from the preceding preflight. Tracer
and decoder pins match. The device implementation's four source hashes and
full-suite log still match its sealed verification. Derived probe:
`/tmp/caplab-native-basic-devices-probe.py`, SHA-256
`13cc44a70b64cb2046865f57f9e7dd0d20cecfe58535ec2199aba8fb93b7e0b1`.
Preflight: `/tmp/caplab-native-basic-devices-preflight.json`. Ruff F passed.
Proceed with the single authorized native launch. It consumes this allowance;
any failure permits inspection and custody closeout, not a retry.

## Verified scripted exchange

The one run used unit
`caplab-native-basic-devices-e0bbd07f253b401892e7483cf5bf4492.service`.
Both response POSTs returned 200 after bounded zstd decoding. The retained
custom call matches the fixed JavaScript and call ID. Its returned command
status is zero, and the stdout command lifecycle has one matching start/result
pair with status completed. The shell command agrees with the supplied fixed
command. Both outputs contain exactly `CAPLAB café tool witness` plus a newline.
The captured task contains `capture-witness.txt` with the same 26 UTF-8 bytes.

The completed agent message and retained final file both contain exactly
`CAPLAB SCRIPTED TOOL DIAGNOSTIC COMPLETE`, 40 bytes without a trailing newline.
The stream ends with one turn.completed. The filtered trace records both
Codex-named process terminal events as exit zero, including PID 14 before the
JavaScript launcher exits. The fixture reports native return zero, no timeout,
no fixture error, no auth refresh and unchanged fabricated authentication input.
These observations verify completion of this fixed scripted local exchange;
they supply no model inference or representative repair measurement.

Task, native collection and all five retained-mount custody checks pass. The
recorded procfs and six-device predicates pass, including no controlling
terminal. Child PID-limit and memory max/OOM/kill counters are zero before and
after; afterward the child PID count is zero. No forced post-capture group kill
or quarantine refusal occurred. The 102,713-byte trace has no EFBIG or delivered
SIGXFSZ. The retained mounts contain 1,437,207 bytes and 127 entries; 113 retained
files were checked with the configured raw forbidden values absent.

Verification: `/tmp/caplab-native-basic-devices-verify.py` and
`/tmp/caplab-native-basic-devices-result-verification.json`. All 13 source pins,
the source/derived probes, fixed handler, decoder, tracer and full installed
harness manifest match. The exact unit now reports not-found and its recorded
cgroup path is absent. The single native allowance is consumed.

## Remaining linkage limits

The retained stream includes four WebSocket retry error events and one
transport-fallback error item before command execution. They remain visible.
`link_codex_final_message` deliberately requires a failure-free stream and
refuses this capture: `retained stdout lacks an unambiguous completed agent
message`, caused by `native event stream reports error`. The verifier requires
that refusal and separately compares the single completed message to the final
file's exact bytes. No error was removed, text normalized, criterion relaxed or
strict-link success fabricated. Recovery followed by native completion does not
make this a failure-free native turn.

Root ID and reported model/effort agree, but `executed_invocation_bound` remains
false, child ancestry is unverified and native capture completeness is unknown.
The filtered diagnostic trace omits successful exec calls and cannot supply the
missing exact invocation linkage. The next integration step is to bind the
actual native invocation to the prepared configuration using the existing
execution-provenance contract. A separate decision is needed on whether final
file/message identity should be inspectable independently of the existing
failure-free-turn gate. Neither gap authorizes a provider run or study promotion.

## Advisory and verification closeout

The Doctrine gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`
at release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
Initial packet `pkt-d13a563836b757fc` and five typed evidence records produced
`pkt-e5353246d099f9cc`, SHA-256
`e5353246d099f9cc46fdd328a6e82642f3137114c87ea2c813841d58547c4fa4`.
The initial Markdown was read. The final Markdown was compared in full against
the preceding device-profile packet already read; only question and packet ID
differ. The archived prior packet bytes were hash-verified before comparison.
Versions remain corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`,
schema `evidence-packet/3`.

The final 25 unmet obligations remain visible. Eighteen on deduplication (3),
ingest populations (4), async UI (4), declarative references (3) and ranking (4)
are nonmaterial to this fixed diagnostic; those product paths are unchanged and
uncertified here. Three external-capability obligations and one evaluation/
serving-parity obligation remain material to provider integration or study
readiness, which is withheld. Three monitoring obligations are nonmaterial
because no service or paging policy changed. The typed evidence names the live
and retained signals used by each gate and states the remaining provisional
claims. A local scripted endpoint is not a provider-capability observation.

Applied guidance: repository-contract precedence, evidence before intervention,
separation of semantic and structural changes, default-behavior preservation,
and authority-bounded action. The result distinguishes native command execution
from a model measurement and exact final bytes from failure-free-turn linkage.
The private verifier passed on the first run and Ruff F passed. No repository
runtime or test source changed, so the preceding 1,343-test/four-skip full-suite
result remains applicable; its source and log hashes were rechecked before
launch. No full-suite rerun was needed for this record-only repository change.

## Final custody

`/tmp/caplab-native-basic-devices-verification.json`, SHA-256
`adecb7877c80ec48a6c41a5aa8804fa9ed7bfb041b7870c6bb66f5c0978b59bb`,
retains 125 artifact hashes, 13 preflight source identities, two additional
inspected-source identities and 11 embedded advisory scratch files removed
after archival. All source, artifact and embedded hashes passed verification.
Five citation observations classified as valid packet citations. A fresh unit
read and cgroup-path check confirmed cleanup again before sealing.
One installed-native allowance was consumed. No real credential, model/provider
spend, tracker write, message, push or historical research evidence effect
occurred. This is completed scripted diagnostic work with the stated linkage
limits; the continuing CAPLAB goal and representative repair shakedown remain
incomplete.
