# Scripted native routed diagnostic, version 2

`prepare ... --launch-profile codex-scripted-routed/v2` selects a non-root
workload beneath the user namespace that owns its network. It uses the
[parent-owned routing contract](capture-parent-routing-v1.md) to address the
mapped-root nested sandbox failure observed in routed attempt 2. The default
remains `codex-scripted-local/v1`; the
[original routed profile](scripted-native-routed-v1.md) remains selectable.

Without a resource profile, preparation uses
`caplab.scripted-native-preparation/v4`, with the same field inventory as v3 and
exactly `launch_profile: codex-scripted-routed/v2`. Version 3
still requires `codex-scripted-routed/v1`. Changing either field alone and
recalculating the preparation hash is refused. The launch configuration has its
own profile-bound identity, even though its native command and fixture endpoint
settings equal those of v1. Source, installed harness, dependency, optional task
input, runtime and resource pins retain the existing validation. A new helper
source is included in implementation pins. Preparation grants no execution
permission; authorization and one-shot consumption remain separate.

The optional [cgroup resource profile](cgroup-resource-observation-v1.md) selects
preparation v5 and binds `resource_profile: cgroup-usage/v1` in addition to the
routed/v2 launch profile.

The explicit [buffered trace profile](buffered-exec-trace-v1.md) additionally
requires supervisor-poll/v1 and selects preparation v7. It quarantines raw and
decoded trace strings before durable retention and links the copied trace to
the observed anonymous source.

The initial inner Bubblewrap still maps root so trusted setup can raise
loopback and establish the workload identity. For v2 only, it also requests
CAP_SETFCAP and mounts `workload_identity.py` read-only beside the other trusted
bootstrap sources. The sealed control document selects
`namespace_profile: parent-user/v1`; bootstrap refuses another explicit value
or that selection without the external fixture.

After raising loopback, trusted `enter_parent_owned_workload()` requires mapped
UID/GID zero and calls `unshare(CLONE_NEWUSER)` in the same process. It writes
`deny` to setgroups and maps child UID/GID 1000 singly to parent zero. It requires
that the resulting process IDs equal 1000. The function does not itself drop
capabilities: bootstrap then performs the existing routed all-five-set drop and
no-new-privs checks before handoff. Failure at any step stops this workload;
partial setup cannot be released, reused or repaired in place.

This preserves the process, mount and network namespace while changing its user
namespace. The policy/routing owner lease independently verifies the kernel's
immediate-parent relationship, observer-coordinate mappings and zero workload
privileges while the authenticated peer is blocked. Helpers use the network
owner's user descriptor and retain their existing mapped-root implementation,
capabilities, policy, deadlines and shutdown behavior. The workload never gains
helper authority over the ancestor network.

The runner selects `parent-user/v1` only for the v2 preparation. New routing
records use the v2 schemas and linked identity snapshot. Native inspection
derives the expected namespace profile from the anchored preparation, then
passes it through shared custody inspection together with the independent
policy and terminal anchors. Readiness and peer identity still come from the
verified mount handoff. Shared custody callers that omit the profile keep the
legacy v1 routing check; the only explicit added profile is `parent-user/v1`.

The outer namespace, joined supervisor fixture, synthetic authentication,
request identity, child observation, source-prepared native launch, trace,
quarantine, task materialization, retention and resource ceilings retain the
v1 contracts. Historical preparations and attempts are not migrated or replayed.
A successful synthetic topology control is not a completed installed-native
attempt. Installed-native execution needs fresh pinned preparation and an exact
one-attempt authorization. Neither profile performs model-generated review or
establishes repair quality, observer cost, hostile-containment acceptance or
reviewer capability.
