# Correct the private HTTPS namespace before source execution

The first brief-preview preparation, plan SHA-256
`a91df81d8fa31e319746319ae5458e518ae8b22c043d25a90526625d2c248323`,
failed its port-443 preflight before importing or executing newsroom source.
It retained the caller's namespace UID while adding the bind capability, which
did not survive execution as intended. Its allowance is closed and its source,
probe, criteria, output and completion records remain unchanged.

Under ADR 0026, authorize `development/brief-preview-witness-2` with exact
copies of the first preparation's base/change trees, witness files including
its disposable TLS material, selection and patch. Preserve source provenance
and a complete copy inventory. Keep the source, inputs and criteria identical.

Use the previously executed recovery/partial-refresh namespace configuration:
map UID/GID zero inside the isolated user namespace, drop all capabilities,
and retain only CAP_NET_BIND_SERVICE. This enables the fixture's private
port 443; it grants no host capability or external network access. Record the
executor derivation and new plan before launch.

The first authorization's 40 executions, preflight, 20-second per-execution
limit, 300-second total, 05:00Z expiry, containment, preservation, verification
and non-admission boundaries apply to this separate allowance. No source
execution occurred in the first attempt. No failed slot or historical result
is replayed or relabeled.
