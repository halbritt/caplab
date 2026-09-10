# Retained routing inspection, version 1

`caplab.capture_network_verify.verify_capture_routing(root, *, plan,
expected_policy_sha256, expected_terminal_sha256, expected_ready_sha256,
expected_peer_pid)` reads one completed bundle from
[`capture_routed_network`](capture-network-transport-v1.md). It launches no
process and writes no artifact. The supplied policy is rebuilt using the
[exact destination contract](capture-network-policy-v1.md).

The caller must supply the policy hash from its selection, the readiness hash
from its verified handoff linkage, the authenticated peer PID, and a terminal
byte hash from trusted collection. Computing all expected hashes from the
untrusted bundle being inspected does not establish provenance. Hashes use
lowercase SHA-256; the PID is a positive integer, never a boolean. The reader
does not reopen that PID or compare it to a currently running process: retained
PIDs and namespace identities can outlive their original processes.

The root must be a resolved absolute path other than `/`, with stable private
ancestry owned by the caller. The root and each opened child directory must be
owned by the current UID and have no group/other permissions. Child directories
and regular files are opened relative to pinned descriptors without following
symlinks. Nonregular objects are refused without blocking on FIFOs. Each file's
identity is checked during its read; directory identity is rechecked before
return. This is not a snapshot mechanism against a concurrent writer with the
same owner or an external hard-link holder. The caller must exclude such writes.

Metadata reads share a fixed 1 MiB allowance. Each of the four process captures
has at most 128 KiB of combined stdout/stderr; streams are checked against their
retained byte counts and hashes and then reread within those bounds for content
inspection. JSON uses strict UTF-8 with duplicate-key and nonfinite-number
refusal. Binary stream hashes are calculated on original bytes, with no text
normalization. The fixed reader has no configurable traversal or payload paths.
Unreferenced extra files are not inspected or certified.

Inspection requires the closed version-1 schemas and checks:

- Agreement between terminal, readiness, routing command and installation
  links, and between preflight, installation, namespace identities and the
  independently supplied peer and policy.
- Exact helper source, argv, environment and descriptor relationships for the
  current fixed policy and routing profiles. Tool observations contain valid
  hashes; the Python observations in both profiles must agree.
- Zero recorded workload capabilities and no-new-privs; the exact policy helper
  capability report and the routing helper's first stderr capability report.
- The selected installation document, empty initial ruleset, and the complete
  captured readback against the selected destination policy. Valid handles and
  counter values are normalized only as specified by the policy contract.
- Complete, zero-exit process receipts; exact stream inventory, EOF, length and
  hash; UTC wall timestamps; monotonic process and byte-receipt intervals.
  Wall time may jump, so ordering uses monotonic time, not wall-clock subtraction.
- Initial, install and readback process order; readback completion before
  routing starts; readiness within the routing process interval; successful
  body completion, normal shutdown and the producer's unchanged-tool observation.

On success the result is `caplab.capture-routing-inspection/v1`, with
`status: verified-observation`, the three supplied hashes, peer PID and namespace
identities. `native_containment_verified` and `study_eligible` remain false.
The status means the retained records are consistent with the bounded checks.
It does not independently establish that the recorded commands ran, that tool
bytes belonged to an approved installation, or that capability reports are
kernel-authenticated. Those require trusted collection and external evidence.
Readiness is not continuous liveness. The reader does not establish network
topology, workload release, provider compatibility, native task success,
representative repair quality or qualification.

Incomplete, missing, malformed or contradictory custody raises `ValueError`
(normally `CaptureVerificationError`) or `OSError`. No success report, repair,
retry or registration follows. A body exception with normal helper shutdown
and a timeout after body completion both fail this completed-bundle interface;
their raw evidence remains available through the original capture records.
All acquired descriptors close on success and refusal.

`scripts/inspect_capture_routing.py` exposes the same read-only check. It takes
positional `root`, required `--policy` (a bounded 64 KiB policy JSON file),
`--expected-policy-sha256`, `--expected-terminal-sha256`,
`--expected-ready-sha256` and `--expected-peer-pid`. Invoke with `PYTHONPATH=src
python3 scripts/inspect_capture_routing.py --help` for argument syntax. A valid
inspection prints JSON to stdout and exits zero. A refusal writes the argparse
error to stderr, emits no success JSON and exits two. Preserve failed custody;
correct the caller's anchors only from their authoritative source.

The offline native diagnostic is unchanged. A future routed native profile
must connect this reader to authenticated handoff and terminal provenance;
this standalone interface does not enable that profile.
