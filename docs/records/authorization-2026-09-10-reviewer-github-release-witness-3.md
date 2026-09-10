# GitHub HTTPS capability activation

Under ADR 0026, authorize new custody
`reviewer-ranking-001/development/github-release-witness-3` with the same
source-copy scope, probe, slots, limits and preservation requirements as the
first two release-witness authorizations. Preserve both failed preflights;
neither custody executed historical source. The second attempt also received
EACCES because adding a capability did not activate it for the nonzero
namespace user.

Run the fixture process as uid/gid zero inside the new user namespace and keep
only `CAP_NET_BIND_SERVICE`. The mapped host identity remains the invoking
unprivileged user. All source mounts remain read-only, and external networking
remains disabled. This enables the private HTTPS endpoint without modifying
the adapter's URL, HTTP client or response parser. Freeze the resulting runner
and plan before a new 12-second preflight; stop on preflight failure. The
36 source slots remain new and one-shot. Expiry: consumption or
2026-09-11T00:00:00Z. No ranking or historical admission is authorized.
