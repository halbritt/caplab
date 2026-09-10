# GitHub HTTPS namespace correction

Under ADR 0026, authorize new development custody
`reviewer-ranking-001/development/github-release-witness-2`, with the same
three source revisions, governing-record copy effects, probe, four conditions,
36 source slots, one preflight and time limits as the first release-witness
authorization. Preserve the first custody unchanged. Its only execution was
a preflight that failed with EACCES when binding loopback port 443; none of
the historical source executions started.

Add `CAP_NET_BIND_SERVICE` inside the isolated user/network namespace so the
local TLS server can bind the original adapter URL's port. This grants no
host capability or external networking. Keep the original URL, certificate
verification, unmodified public adapter call and empty credential environment.
Freeze a new plan and runner before the new preflight. No consumed slot is
replayed. Stop if the correction does not establish local TLS or if inputs
drift. Expiry: consumption or 2026-09-11T00:00:00Z. All prior interpretation,
preservation and no-ranking boundaries remain in force.
