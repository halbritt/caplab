# Corrected configuration-effort fixture

Under ADR 0026, the primary agent authorizes two new local diagnostic slots in
`reviewer-ranking-001/development/effort-control-2`, with the same two exact
Council commits, copy/provenance scope, isolation, dependency pins, 45-second
per-process and 120-second total limits as the first effort-control
authorization. Expiry: slot consumption or 2026-09-11T00:00:00Z.

The first batch is preserved: its native/session fixtures used a relative
`launch_argv[0]`, so valid effort inputs were rejected by an unrelated path
invariant. Full result equality alone therefore did not establish the intended
positive controls. Correct that fixture field to `/usr/bin/true`, freeze the
new cases before either process, and retain all outcomes. The earlier compiler
observations remain valid only for their exact recorded scope.

No provider call, reviewer score, historical overwrite or clean-label acceptance
is authorized. The first batch remains consumed and is not replaced.
