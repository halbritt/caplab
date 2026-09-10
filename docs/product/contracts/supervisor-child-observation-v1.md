# Supervisor-owned native child observation, version 1

`wait_for_native_child()` in `caplab.native_child_observation` observes the
direct child of an already authenticated native entrypoint without asking the
provider, task or child to emit a readiness message. The caller supplies the
existing `FrozenNativeChildEvidence`, an owned leaf cgroup and a wait timeout
greater than zero and at most 30 seconds. The supervisor must be outside that
cgroup. The caller owns source quiescence, the borrowed parent descriptor and
exclusion of outside process migrations, signals and namespace changes.

The readiness loop polls bounded kernel process metadata every 10 ms. A
matching parent and executable file object is only a hint. Disappearing
candidates can be retried within the wait; other errors stop observation.
After a hint, the supervisor freezes the selected cgroup and calls the existing
frozen observer. That observer requires exactly one matching direct child,
stable process/group identity and the independently expected executable hash.
Multiple matching children, changed membership or an exited image are failures.

The supervisor owns one freeze/thaw pair. Each transition has a two-second
wait; thaw is attempted even if executable verification fails. The record
contains the poll count, selected timeout, monotonic phase times and frozen
observation. `NativeChildObservationError.record` retains a fixed failure code
and completed phases; the caller must guard it before persistence and stop its
workload on failure. A missing or short-lived child is unavailable evidence.
The API does not claim continuous image residence or task success.

The wait bound excludes the two freeze transitions and bounded image reading.
The existing maximum image allowance is 1 GiB. These operations add observation
time and perturb the workload; the retained timing is not an estimate of total
capture overhead or an overhead-free model runtime. No provider message or
inference call is part of this API.

`inspect_supervisor_child_observation()` checks an anchored successful record
against the independently selected supervisor/parent and enclosing process
interval. Its caller remains responsible for record custody, executable and
cgroup identity, trace linkage and the native task result. It refuses failure
records, mismatched owners and invalid phase order rather than treating them
as zero-duration observations.

The scripted diagnostic selects this mechanism only with
`--child-observation-profile supervisor-poll/v1`, parent-routed launch version 2
and `--resource-profile cgroup-usage/v1`. The resulting preparation is version 6
and carries both selections. The fixture receives no observation socket, and
the workload receives no observation-socket mount. Inspection requires no
fixture observation-request/acknowledgment fields and verifies the supervisor
record separately from the fixed protocol exchange. Older preparations retain
their fixture-triggered behavior and inspection semantics.

This selection tests the capture mechanism with the actual native harness and
fabricated provider responses. It does not turn those responses into model
measurements or authorize real credential delivery. Real provider administration,
credential quarantine usability and representative repair execution remain
separate prerequisites.
