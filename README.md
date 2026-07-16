# Agent Capability Lab

Agent Capability Lab (CAPLAB) is a behavioral capability measurement and
model-development laboratory. It preserves study designs, evaluation
instruments, adjudication records, checked-in aggregates, and reviewer-facing
projections without collapsing mechanical observations into scientific
inferences or owner decisions.

CAPLAB does not own the engineering-doctrine corpus or its retrieval runtime.
Those are supplied by the separately versioned
[`halbritt/pincite`](https://github.com/halbritt/pincite) repository through
the exact dependency recorded in [`pincite-dependency.json`](pincite-dependency.json).

## Repository map

| Path | Contents |
|---|---|
| [`caplab/`](caplab/) | CAPLAB runtime code, Pincite dependency verification, and the study-results dashboard |
| [`docs/product/`](docs/product/README.md) | Product specifications, plans, and capability cards |
| [`docs/agent-judgment/`](docs/agent-judgment/README.md) | Evaluation operation and extension guidance |
| [`doctrine/evaluations/`](doctrine/evaluations/README.md) | Evaluation contracts, fixtures, adjudication records, and preserved experiment reports |
| [`doctrine/tools/`](doctrine/tools/) | CAPLAB-owned evaluation, projection, replay, and adjudication tools |
| [`docs/decisions/`](docs/decisions/README.md) | Architecture decisions and their authority boundaries |
| [`docs/domain/`](docs/domain/README.md) | CAPLAB domain language and context map |
| [`tests/`](tests/) | Hermetic CAPLAB tests and pinned-Pincite integration checks |
| [`ubiquitous_language.md`](ubiquitous_language.md) | Canonical assertion, evaluation, and decision vocabulary |

The retained `doctrine/evaluations/` path is a stable historical artifact
namespace, not a claim that CAPLAB owns Pincite doctrine. Sealed Harbor records
may also retain old `books` repository paths. Those bytes are experiment
provenance and are not live repository configuration.

## Pincite dependency

The default validated release location is:

```text
~/.local/share/pincite/release
```

Override it with `PINCITE_RELEASE_HOME`. CAPLAB fails closed unless that
checkout is at the exact pinned commit and its Pincite retrieval-state gate
reports the expected corpus and doctrine identities:

```bash
make pincite-check
```

The dependency manifest pins the repository, release tag, commit, corpus ID,
and doctrine ID. Updating it is an explicit compatibility decision, not an
incidental consequence of a newer Pincite checkout.

## Checks

Install the small Python dependency set:

```bash
python3 -m pip install -r requirements.txt
```

Run the hermetic CAPLAB suite:

```bash
make test
```

Run the complete local gate against the pinned Pincite release:

```bash
make check
```

GitHub Actions runs the hermetic suite. The full integration gate is local
because the Pincite repository and release checkout are private dependencies.

## Evaluation and dashboard entrypoints

Start with [`docs/agent-judgment/README.md`](docs/agent-judgment/README.md) for
the behavioral evaluation harness and
[`caplab/dashboard/README.md`](caplab/dashboard/README.md) for the Study 001
review dashboard.

Machine screening, mechanical grading, and deterministic projections are
observations of instrument output. They are not human adjudication,
verification, acceptance, or authority to promote a broader capability claim.

## Assertion discipline

Repository analysis follows [`ubiquitous_language.md`](ubiquitous_language.md):

- observations retain inspectable evidence and provenance;
- inferences state uncertainty and credible rivals;
- recommendations remain distinct from decisions;
- decisions name an owner and authority source; and
- authorization, execution, verification, and acceptance remain separate.
