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

Current execution scope is CAPLAB-22/P4: a model-free synthetic round trip
through the selected PostgreSQL, Garage, and independent local-copy contracts.
P5 recovery testing, historical evidence admission, model calls, training,
and CAPLAB acceptance remain outside that scope.

Run the hermetic repository gate with:

```bash
make check
```

The read-only dashboard is under `src/caplab/dashboard`. Runtime code belongs
under `src/caplab/runtime`.
