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
quarantined with access disabled. CAPLAB-23/P5 completed its recovery campaign,
and CAPLAB-24/P6 independently verified the restricted admission of the frozen
Study 001 evidence. ADR 0016 authorizes implementation and hermetic testing for
the read-only CAPLAB-25/P7 recomputation, CAPLAB-26/P8 capability-profile
proposal, and CAPLAB-28/P10 training-candidate manifest. It does not authorize
live recomputation, a capability inference, a training-eligibility decision,
an export, model calls, training, or CAPLAB acceptance.

Run the hermetic repository gate with:

```bash
make check
```

The read-only dashboard is under `src/caplab/dashboard`, the bounded Study 001
recomputation is under `src/caplab/recomputation`, and evidence runtime code is
under `src/caplab/runtime`.
