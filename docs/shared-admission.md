# Opt-in shared admission for live Revbench

This feature adds Quartermaster admission around Caplab's existing one-shot live
Revbench process custody. It does not replace a native harness, construct a
Binding, authorize an experiment, or qualify a measurement. Unenrolled execution
keeps its existing behavior. Only future explicitly enrolled live Codex Revbench
runs participate in this version: both assigned version probes and native reviews
are guarded. Local fixtures, advisory pool_runner, retrieval, preference and
review-dissent runners are unenrolled; this feature does not claim universal
Caplab coverage or prevent their independent use.

The source-only `execute` command accepts `--shared-admission CONFIG.json`.
Python callers may pass a `SharedAdmissionEnrollment` as `shared_admission` to
`execute`. The configuration is pinned in the native execution's existing custody
root before any process claim. Resumed executions must retain that exact enrollment;
an old unenrolled intent cannot be enrolled after it starts. Omitting enrollment
cannot disable a retained enrollment. Existing authorizations and apparatus pins
still apply: new source needs its own prospective apparatus/authority, not reuse
of an active run's pins.

Each assigned process reserves one slot and at most one outer creation under its
native authorization-independent effect identity, in the same designated shared
home used by other consumers. The native custody claim remains one-shot. Only a
fresh durable Quartermaster `prepared` result may cross the native Popen boundary.
Replayed/lost responses never permit another launch. Provider observations are
refreshed from the configured local observation file at acquisition and prepare;
unknown/stale/exhausted evidence defers or refuses, not a percentage-to-count
conversion. No provider collection is performed.

Admission receipts and evidence are additive immutable sidecars in existing
custody, separate from measurement/qualification documents. A pre-Popen refusal
can retire the closed native right truthfully. Popen OSError means unresolved
possible creation, not zero; successful Popen means a created child even if the
contained exec fails. A crash between a permit and a receipt retains uncertainty.
Recovery reconciles existing sidecars and native completions without launching.
Only a positively reaped, completely captured pinned PID-namespace-contained
process supports tree closure. Exceptions or missing custody never release a hold.

Native clock receipts have one-second UTC resolution. Only a creation bracket
whose before/after readings lie in the same UTC second can establish that exact
quantized creation timestamp (under the existing trusted-host-clock assumption).
A crossing bracket records positive creation with unknown time and retains its
budget/slots. No midpoint or post-Popen time is relabeled as exact creation. The
current Quartermaster API needs interval-valued evidence support, or independently
validated actual creation facts, to settle such boundary cases; this consumer does
not invent that API or silently select a representative point.

Configuration is explicit operator enrollment, not authenticated account evidence.
The selected catalog native tuple/profile is checked against the complete existing
Binding/native-system contract. The shared catalog account and policy join must be
reviewed against the actual credential/account custody by Caplab's owner. CLI
control-plane processes are not measured harness invocations; their executable
and explicit input hashes are pinned, and their outputs retained. This version
uses the external Quartermaster CLI so the isolated -I -S Caplab apparatus does
not import a second project's Python runtime. Quartermaster controls its own
installation and policy/storage versions. Do not run independent admission homes
for the same governed resource. This feature is a candidate, not deployment or
installed enrollment.
