# Agent Capability Lab

CAPLAB measures software-agent capabilities that patch-completion benchmarks
do not capture directly: judgment under contradictory evidence, verification
behavior, abstention, evidence-responsive decision control, and other
study-specific constructs. After later gates, it is intended to supply governed
evidence for Striatum placement decisions and open-model training work.

This is the standalone CAPLAB repository. The initial product decisions,
Study 001 selection, capability card, and dashboard projection were imported
from `halbritt/books` at commit
`cdbb5120d1d450763fca2a8aca172f6308413440`. Historical Study 001 evidence was
not copied during that repository separation.

CAPLAB-22/P4 completed independent verification and its synthetic state remains
quarantined with access disabled. ADR 0009 authorizes the bounded
CAPLAB-23/P5 recovery campaign through `2026-07-23T23:59:59Z`. Historical
evidence admission, CAPLAB-24/P6, model calls, training, and CAPLAB acceptance
remain outside the current scope.

Run the hermetic repository gate with:

```bash
make check
```

The read-only dashboard is under `src/caplab/dashboard`. Runtime code belongs
under `src/caplab/runtime`.
