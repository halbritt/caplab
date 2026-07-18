# Study 001 training-candidate manifest

This package implements CAPLAB-28/P10's deterministic candidate derivation. It
accepts the exact P6 admission manifest and the P7 recomputation bound to that
manifest:

```bash
python -m caplab.training_candidates \
  --recomputation /path/to/recomputation.json \
  --registration /path/to/registration.json
```

Success writes one canonical `caplab-training-candidate-manifest/1` document
to standard output. Each included candidate binds its assignment, first
attempt, mechanical outcome, outcome record, and all eleven P6 identity kinds.
The mechanical label is normalized from the sealed CSV lineage and checked
against the sealed observation. All Study 001 examples share the
`checkout-retries-study-001` split group, so a later decision cannot separate
this task family and scenario template across dataset splits.

Invalid or replaced attempts, provider or infrastructure failures, verifier
or observer failures, and incomplete or ambiguous human-disposition lineage
are excluded. An altered global identity, broken relationship, substituted
result row, or verifier identity that omits an outcome stops the manifest.
Known leakage and compromised instruments are exclusion rules; neither has a
negative assertion in P6. Every candidate therefore records leakage review as
`unavailable-pending-human-eligibility` and remains
`derived-not-eligible`.

The output is a candidate manifest. It is not an eligibility decision, export,
dataset, model call, training action, verification verdict, or acceptance
record. CAPLAB-29/P11 remains human-owned and must decide exact eligibility
before any later export can be authorized.

ADR 0016 authorizes this implementation. Actual P10 derivation remains pending
the separate P7 live continuation and its content-addressed observation.
