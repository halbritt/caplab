# Scripted native capture diagnostic v1

`scripts/probe_scripted_native_capture.py` prepares, executes once and inspects
one fixed offline Codex tool exchange. It exercises capture infrastructure with
scripted responses. It does not measure model or reviewer capability, provide
a model-serving endpoint, select a study or create a qualification claim.

## Prepare

With `PYTHONPATH=src`, invoke:

```text
python3 -B scripts/probe_scripted_native_capture.py prepare /absolute/private/output \
  --codex-root /absolute/installed/codex \
  --websockets-root /absolute/installed/websockets
```

The output must be a fresh resolved path under trusted private ancestors. Input
trees must be resolved and must not overlap it. Preparation executes no native
agent and downloads nothing. It uses the native-agent-system contract to build
the fixed `codex-terra-max` invocation, validates the supported Codex source
profile, and requires websockets release metadata identifying 15.0.1. The
dependency is a caller-supplied installed package directory, not a service URL.
Version metadata is a compatibility check, not proof of package authenticity.

`preparation.json` seals the absolute custody path/device/inode, invocation,
Codex installation manifest, dependency manifest, selected child source files,
active Python implementation pins, resolved system-runtime pins and fixed
limits. The caller receives its SHA-256 and must retain that independent anchor.
The caller owns the authenticity/quiescence of inputs and runtime, and the
private custody lifetime. The source profile verifies four selected Codex files;
the installation manifest inventories its complete declared tree. Python pins
cover active CAPLAB `.py` files, the diagnostic modules and its two shared probe
helpers, excluding historical trees, tests and bytecode. This does not establish
every behavior-bearing runtime dependency or a complete Binding.

One-shot enforcement assumes the owner preserves this custody root and its
consumption receipt without deletion or rollback. The diagnostic does not
provide an external durable attempt ledger or authorize replay in another root.

An optional prepared task is selected with both `--task-input /absolute/private/input`
and `--task-input-sha256 <input.json hash>`. The bundle must already satisfy the
[task-input contract](task-input-v1.md); preparation neither discovers a world
nor copies its original source. The default empty task keeps preparation schema
`caplab.scripted-native-preparation/v1`. Supplying an input uses `/v2` and adds
`task_input` with its exact custody path, input hash and 300,000-byte metadata
allowance. Keep that input custody stable and available through inspection.

Input-declared allowances must not exceed 1 MiB and 1,000 entries, checked
before input payload verification. Actual input counts must leave room for
both before/after copies and the diagnostic witness within the existing task
capture quotas. Its root must permit owner write/search, and
`capture-witness.txt` and descendants are reserved. Partial option pairs,
overlapping custody and incompatible inputs refuse preparation. Input bytes
are reverified before attempt consumption and materialization.

After authenticated mount checks, the supervisor materializes the selected
input into blocked `/work`, captures its before inventory, verifies content
agreement and seals the [prepared-task link](prepared-task-capture-v1.md) in
the guarded handoff before release. Quarantine or linkage failure prevents
release and preserves partial effects. The fixed diagnostic tool still only
adds its witness file; the task is not presented as a model-generated repair.
Input instructions can affect native behavior and require their own exposure
and configuration accounting before any study use.

## Authorize and execute once

Preparation grants no execution authority. A separate authorization document
has these exact fields:

```json
{
  "schema": "caplab.scripted-native-authorization/v1",
  "preparation_sha256": "<independently retained preparation hash>",
  "custody_root": "/absolute/private/output",
  "attempt_limit": 1,
  "decision_owner": "<authorized owner or delegate>",
  "authority_source": "<scoped authorization record>",
  "permitted_effect": "one-scripted-native-diagnostic"
}
```

The caller must hold actual authority for the named effect. These fields and
their hash bind a supplied record; they do not authenticate their own authority.
Execute with the independent preparation and authorization hashes:

```text
python3 -B scripts/probe_scripted_native_capture.py execute /absolute/private/output \
  --preparation-sha256 <hash> --authorization /absolute/authorization.json \
  --authorization-sha256 <hash>
```

Before launch, the implementation rechecks source/dependency/runtime pins and
authorization scope. It exclusively creates and fsyncs `consumption.json`, then
fsyncs the custody directory. Exactly one concurrent caller can consume the
allowance. Any existing consumption file, including a truncated one, is spent.
There is no reset or automatic retry. Failures after consumption do not refund
the attempt. Source or authorization mismatch before consumption refuses
without creating the receipt.

The native subject is Codex with the fixed model/effort and
`codex-scripted-local/v1` launch configuration. The capsule receives fabricated
readonly authentication, its fixed fixture code, the explicit readonly
installation/dependency, and five bounded writable mounts. Only loopback exists
in its unshared network namespace. The six-device profile, nested procfs,
capability drop, outside ordinary tracer and trusted quarantine remain required.
There is no real token, provider connection or arbitrary prompt/tool override.

The supervisor seals the effective launch and source-prepared child expectation
before releasing the authenticated launcher, retaining its proc descriptor. At
the first validated response request, an authenticated bootstrap handshake
requests one frozen kernel child observation. The supervisor thaws before
sealing and acknowledging. The fixture sends no scripted response before that
acknowledgement and still enforces its original deadline afterward.

Every request, including warmup and continuation, must explicitly name the
selected model, reasoning effort and `detailed` reasoning summary. The endpoint
retains raw request bytes before validation and refuses missing, malformed or
conflicting fields before requesting a child observation or constructing any
response for that request. Earlier completed responses remain retained. The
expected fields are copied from the caller's selected configuration at fixture
construction. Other reasoning metadata remains in raw custody; matching the
three selected fields does not establish complete configuration or provider
authentication. Inspection independently compares the raw fields with the
prepared subject and checks the recorded request observation.
Earlier captures that lack that observation retain their original pinned
inspector and original claims. The stricter current inspector does not certify
that this gate ran in an older capture; a later raw-field consistency check is
a separate observation with its own provenance.

Fixed limits are native/capture/unit/outer 30/45/90/100 seconds; workload/unit
memory 256/512 MiB, zero swap, 128/192 tasks; stream 300,000 bytes; task
1 MiB/1,000 entries; native collection 8 MiB/1,000; retained mounts
40 MiB/2,000; trace 2 MiB; native file 8 MiB. Each writable mount is 64 MiB.
Handshake wait is five seconds and each freeze/thaw transition two seconds.
Kernel/file operations do not have an independent wall-time guarantee; the
owned unit/outer lifetime still bounds the execution. The freeze interval is
part of this instrumented configuration and is reported separately.

## Outcomes and inspection

Execution retains available evidence beneath `run/`. Once capture and owned
cleanup end, `result.json` anchors the consumption, available outcomes and a
manifest of retained run files. If execution or manifest construction fails,
the result records the failure and does not claim success. If even result
publication fails, the consumption and retained prefixes remain; no completion
receipt is invented. The caller receives the result SHA-256 when it is sealed.

The capture worker can finish retaining evidence while the native bootstrap
reports failure. Native, bootstrap, capture-worker and transport outcomes stay
distinct. The known missing WebSocket close-frame error remains an error even
when both scripted responses, tool output, final file and native exit zero are
present. `execute` exits 1 for a failed diagnostic attempt, including that case.
No unexpected error is suppressed or treated as a successful exchange.

```text
python3 -B scripts/probe_scripted_native_capture.py inspect /absolute/private/output \
  --preparation-sha256 <hash> --result-sha256 <hash>
```

Inspection checks the anchored manifest before interpreting capture, then
composes the existing custody, tracer, child-creation/exec/termination, tool-pair
and final-message readers. The child PID comes from the sealed kernel
observation; command/environment come from the prospectively sealed source
preparation. The original installation must remain available and unchanged for
source revalidation. It checks exact task/final bytes, raw request/response
lineage and timing, resource counters, quarantine and owned-unit removal.
The shared custody reader also checks [overlapping retained copies](capture-overlap-v1.md):
the final task inventory against retained `/work`, and selected native locations
against retained `/episode`. Individually valid copies that disagree are refused.
For prepared tasks, inspection also requires the preparation's exact input
selection, the handoff's materialization/before linkage, and an observed task
change list containing only the added `capture-witness.txt`. Other task content
or mode changes refuse inspection. A successful check does not validate the
task's oracle or establish that a model repaired it.

Missing prerequisite artifacts return `status=unavailable` and exit 1. Changed
or malformed anchored evidence refuses with an exception; it never becomes a
verified observation. A complete qualifying diagnostic observation returns
`status=verified-observation` and exits 0 even when its preserved transport error
makes `native_attempt_succeeded=false`. Inspection success is distinct from
attempt success. All reports leave Binding completeness and study eligibility
false, and native-capture completeness unestablished. Historical private
captures are not converted into this format by these operations.

## Verification environment

Linux cgroup v2, delegated systemd user units, Bubblewrap, Node, Python 3.12+ and
strace are required for execution. Real cgroup controls use fixed local process
producers; standing tests do not invoke an installed native agent. Protocol
tests require the supported websockets package, either importable normally or
selected with `CAPLAB_TEST_WEBSOCKETS_ROOT`. They report an explicit skip if the
package is absent. Run the full suite with that dependency present before
authorizing a native integration attempt. A separate scoped authorization is
required for each actual native attempt; passing component tests does not grant
it or complete the representative repair shakedown.
