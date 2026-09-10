# Verify the native reviewer's new topic-creation finding

Under ADR 0026, the primary agent authorizes a local behavioral investigation
of the sole final finding from output-probe-3. Use the exact Council original
change `9c66a76836245fbc8d203812a4a36f475341ce0e` already copied in that probe's
task custody. Mount it read-only with its original provenance; do not rewrite
the reviewed source or supply a candidate fix.

Copy the original protocol's configuration example into new private witness
custody, retaining its source/hash. Configure one DeepSeek member, no credential
seeds and one empty root. Compare the accepted `root_view_entries` limits 1
and 100000, three isolated processes per limit, at most 20 seconds each and
150 seconds total. Freeze inputs, probe and predicted observations before
execution. Exercise the public configuration parser, service initialization,
topic creation and credential-root validator; retain actual errors and success.

Use installed, hashed Node/tsx dependencies, a disabled network, synthetic
environment credentials, private temporary homes and read-only source. No
provider, reviewer or production service is called. Retain all observations,
source/runtime hashes, process outcomes and fixture-construction provenance
under `reviewer-ranking-001/development/topic-credential-witness-1`. Stop on
input drift, deadline or unexpected setup failure; no consumed slot is replayed.

Expiry: six slot consumptions or 2026-09-11T00:00:00Z. This authorizes behavior
verification, not independent acceptance of the delegate's own execution,
evidence admission or ranking. The expected-error interpretation must name
its basis separately from observed behavior and from reviewer attribution.
