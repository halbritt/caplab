# Study 001 recomputation

This package implements the deterministic, read-only CAPLAB-25/P7 tracer
authorized for development by ADR 0016. It reconstructs the frozen Study 001
normalized result from the P6 registration, checks every used Postgres locator,
verifies the Garage object and independent `/nvr` copy by content identity, and
applies the preregistered paired exact analysis without importing historical
runtime code.

The only CLI command is:

```bash
python -m caplab.recomputation recompute
```

The live command requires the exact root-custodied
`/etc/caplab/recomputation.toml`, an unexpired campaign, the temporary
`caplab_reader` identity, a clean transport environment, and the exact P6
admission manifest. It opens PostgreSQL transactions read-only and has no
object-store, independent-copy, or database write method.

Success emits a canonical `caplab-study-recomputation/1` observation that binds
the P6 manifest, all 20 outcome byte identities, the registered result CSV, the
clean implementation commit, the normalized result, the comparison, and the
failure policy. Any registration, relationship, locator, byte, frozen-design,
or historical-result discrepancy stops with a typed error and no result.

This package cannot make a capability inference, decide training eligibility,
export data, call a model, train, publish, route a subject, or accept CAPLAB v0.
ADR 0016 does not authorize the live command. A separate durable continuation
must first bind the exact clean implementation and host surface.
