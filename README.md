# CAPLAB — Agent Capability Lab

CAPLAB measures software-agent capabilities that patch-completion benchmarks
do not capture directly: judgment under contradictory evidence, verification
behavior, abstention, evidence-responsive decision control, and other
study-specific constructs. After later gates, it is intended to supply governed
evidence for Striatum placement decisions and open-model training work.

This is the canonical CAPLAB repository: `halbritt/caplab` on GitHub and
`/home/halbritt/git/caplab` on the primary host. The active product, package,
tests, decisions, and operational records live at the repository root.

The repository also retains the complete tracked tree and Git ancestry of the
former Ethogram repository under `history/ethogram/`. That subtree is
historical source and evaluation custody, not an alternate package root or
runtime authority. Its prior branches remain available for provenance and
recovery. See [ADR 0019](docs/decisions/adr-0019-canonical-caplab-repository.md)
for the consolidation boundary and rollback path.

CAPLAB also absorbed the useful measurement boundary from `striatum-tuner`
under [ADR 0062](docs/decisions/adr-0062-binding-qualification-boundary.md).
The active known-defect methodology is `caplab.revbench`; exact-Binding
Measurement validation, versioned policy evaluation, append-only Claims, and
the deterministic Quartermaster-facing export are under
`caplab.qualification`. Historical tuner runs and fate-derived conclusions
remain non-qualifying source custody under
[`history/striatum-tuner/`](history/striatum-tuner/README.md). CAPLAB does not
implement Quartermaster's runtime registry or Dispatch selection.

The initial product decisions, Study 001 selection, capability card, and
dashboard projection were imported from `halbritt/books` at commit
`cdbb5120d1d450763fca2a8aca172f6308413440`. Historical Study 001 evidence was
not copied during that initial repository separation; its later restricted
admission is recorded by CAPLAB-24/P6.

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
under `src/caplab/runtime`. The qualification architecture, status semantics,
and operator boundary are documented in
[`docs/product/qualification/`](docs/product/qualification/README.md).
