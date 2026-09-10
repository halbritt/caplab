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
