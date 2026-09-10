# Permit local HTTPS binding inside the disposable namespace

Under ADR 0026, authorize separate private `reddit-recovery-witness-2` custody
with the same source, feed, criteria, real-duration limits and expiry as the
[first authorization](authorization-2026-09-10-reviewer-reddit-recovery-witness.md).
Preserve the first custody, plan, runner and failure outputs unchanged. Its
ordinary condition stopped with `PermissionError: [Errno 13] Permission denied`
while binding port 443, before constructing the adapter or issuing a harvest.

Use UID/GID 0 only inside the new user namespace, drop all capabilities, then
add only `CAP_NET_BIND_SERVICE` inside that namespace. This is the same local
HTTPS binding mechanism used by the prior GitHub witness. It grants no host
root identity or host-network access. Keep all sources/runtime mounts
read-only and only the new private captures writable.

Freeze the revised runner before execution. Keep the Go/Python source,
original clocks/timeouts, feed, probe and criteria unchanged; a fresh local
test certificate is allowed. Two executions of each frozen condition remain
authorized, 215 seconds each and 500 seconds total. Expiry remains
2026-09-11T00:00:00Z or consumption. The same setup/failure preservation and
no external-service, target-write, corpus-admission or ranking boundaries apply.
