# Study 001 capability-profile proposal

This package implements CAPLAB-26/P8's deterministic proposal boundary. It
accepts three content-addressed inputs:

- a `caplab-study-recomputation/1` observation from P7;
- the exact selected capability-card bytes, SHA-256
  `8c910c50923340d3586e82ac29fee4614eb72bfefd2347180803e1792b08fad5`;
  and
- the exact ADR 0006 selection bytes, SHA-256
  `7d14f4e4c9efffd297512be6b1a00cccb16f309119667ee6663afb316e5ff713`.

The file boundary is:

```bash
python -m caplab.profile \
  --recomputation /path/to/recomputation.json \
  --card docs/product/capability-cards/caplab-study-001-explicit-verification-elicited-harm-avoidance.md \
  --selection docs/decisions/adr-0006-caplab-study-001-capability-card-selection.md
```

Success writes one canonical `caplab-capability-profile-proposal/1` document
to standard output. The proposal binds the registered input, selected card,
Study 001 result, population, missingness, failures, and credible rivals. Its
status is `pending-human-inference`. Task-family and cross-task capability,
model-wide capability, preference, Striatum placement, training eligibility,
mechanism, safety, verification, and acceptance remain unavailable.

Changed card or ADR bytes, a broken content identity, a non-Study-001 input,
a non-observational recomputation, a historical mismatch, or any promoted
upstream claim stops with a typed error. The package has no persistence,
provider, inference-recording, placement, export, or acceptance interface.

ADR 0016 authorizes this model-free boundary. P7 produced its content-addressed
observation on 2026-07-20, and the first actual P8 execution emitted profile
manifest `641965dc30fd0dbfca81d56bb05282b01e8e079285ab605c12672e92f3971ef0`.
The profile remains pending the CAPLAB-27 human inference decision.
