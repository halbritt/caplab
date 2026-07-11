# Books

This repository converts PDF and EPUB books from `sources/` into a semantically structured Markdown corpus. It also contains provenance-aware doctrine contracts and evaluation fixtures for turning the corpus into bounded engineering guidance.

The source books remain unchanged under [`sources/`](sources/). Generated books live under [`books/`](books/README.md), one directory per source.

## Repository map

| Path | Contents |
|---|---|
| [`sources/`](sources/) | Original PDF and EPUB inputs, preserved unchanged |
| [`books/`](books/README.md) | Generated chapter Markdown, assets, source metadata, provenance, and validation records |
| [`doctrine/OPERATIONALIZATION.md`](doctrine/OPERATIONALIZATION.md) | Sequence for building evaluation, retrieval, skills, and decision receipts around the corpus |
| [`doctrine/CONVERGED_RECOMMENDATION.md`](doctrine/CONVERGED_RECOMMENDATION.md) | Converged recommendation that preceded the operational design |
| [`doctrine/runtime/`](doctrine/runtime/README.md) | JSON Schema contracts and structural assertion validation |
| [`doctrine/evaluations/`](doctrine/evaluations/README.md) | Replayable authority canaries and dependency-impact fixtures |
| [`ubiquitous_language.md`](ubiquitous_language.md) | Canonical meanings of observation, inference, recommendation, decision, and adjacent authority terms |
| [`AGENTS.md`](AGENTS.md) | Repository instructions for coding agents |
| [`scripts/convert-books`](scripts/convert-books) | `sources/` book discovery and conversion command |
| [`tests/`](tests/) | Conversion-pipeline and doctrine-scaffolding tests |
| [`CHANGELOG.md`](CHANGELOG.md) | Notable repository changes |

## Source books

Only supported files located directly under `sources/` are ingested. Files in the repository root and nested source directories are not searched.

| Book | Source file |
|---|---|
| A Philosophy of Software Design, 2nd Edition | `sources/dokumen.pub_a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217.epub` |
| Clean Architecture: A Craftsman's Guide to Software Structure and Design | `sources/Clean Architecture A Craftsman Guide to Software Structure and Design.pdf` |
| Code Complete, 2nd Edition | `sources/code-complete-2nd-edition-v413hav.pdf` |
| Domain-Driven Design: Tackling Complexity in the Heart of Software | `sources/Domain Driven Design Tackling Complexity in the Heart of Software - Eric Evans.pdf` |
| Efficient Go: Data-Driven Performance Optimization | `sources/Efficient Go Data-Driven Performance Optimization (Bartlomiej Plotka) (Z-Library).pdf` |
| Fluent Python, 2nd Edition | `sources/Fluent.Python.2nd.Edition.(z-lib.org).pdf` |
| Fundamentals of Software Architecture | `sources/OReilly.Fundamentals.of.Software.Architecture.2020.1.pdf` |
| Refactoring: Improving the Design of Existing Code | `sources/Refactoring  Improving the Design of Existing Code.pdf` |
| Software Design X-Rays: Fix Technical Debt with Behavioral Code Analysis | `sources/dokumen.pub_software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725.pdf` |
| The Pragmatic Programmer | `sources/the-pragmatic-programmer.pdf` |
| Working Effectively with Legacy Code | `sources/[PROGRAMMING][Working Effectively. with Legacy Code].pdf` |

The generated [book index](books/README.md) records title, authors, converter, execution target, chapter count, status, output path, and validation warnings for each source.

## Convert and validate books

Convert every supported source:

```bash
make books
```

PDFs use Marker on the `peecee` GPU worker, with the defined local Marker path available only as an infrastructure fallback. EPUBs use Pandoc. The pipeline extracts assets, identifies logical chapter boundaries, and writes normalized Markdown plus metadata and validation records.

Convert one exact source without rebuilding the repository index:

```bash
./scripts/convert-books --book 'Refactoring  Improving the Design of Existing Code.pdf'
```

Run tests and validate generated books without invoking converters or writing output:

```bash
make check
```

Each generated book has this shape:

```text
books/<book-slug>/
  README.md
  metadata.json
  source.json
  validation.json
  chapters/
  assets/
```

`source.json` includes the repository-relative source path, content identity, and conversion provenance. Generated file manifests protect existing output: conversion refuses to overwrite unexpected edits unless `--force` is supplied explicitly.

## Assertion discipline

Repository analysis must follow [`ubiquitous_language.md`](ubiquitous_language.md). In particular:

- observations require inspectable evidence;
- inferences retain uncertainty and credible rivals;
- recommendations include alternatives and tradeoffs;
- decisions identify an owner and authority boundary;
- authorization, execution, verification, and acceptance remain separate states.

The structural validator checks these fields and predecessor relationships:

```bash
python3 doctrine/tools/validate_assertions.py \
  doctrine/evaluations/fixtures/authority-withdrawn/result.json
```

Structural validity does not prove that a natural-language assertion is true or honestly labeled. Source entailment remains an evaluation concern.

## Doctrine evaluations

The authority canaries hold evidence constant while changing authorization. The authorized fixture may reach decision and authorization; the withdrawn fixture must stop at recommendation.

Replay the withdrawn-authority case:

```bash
python3 doctrine/tools/run_scenario.py \
  doctrine/evaluations/fixtures/authority-withdrawn/scenario.json \
  doctrine/evaluations/fixtures/authority-withdrawn/result.json
```

Calculate the rebuild and reverification impact of a changed manifest node:

```bash
python3 doctrine/tools/dependency_impact.py \
  doctrine/evaluations/fixtures/dependency-impact/manifest.json \
  --changed source-a
```

These fixtures are synthetic contract tests. They do not yet measure natural-language entailment, graph retrieval quality, or source-locator correctness.

## Integrity boundaries

- Source PDFs and EPUBs under `sources/` are inputs and are not rewritten by conversion.
- Generated corpus files retain source hashes, converter provenance, and validation results.
- Unexpected manual changes to generated output stop regeneration unless replacement is explicitly forced.
- Corpus doctrine may support an observation, inference, or recommendation; it cannot create authorization.
- Evaluation outcomes and usage traces must not rewrite source doctrine silently.

The tracked `out/Refactoring/` directory is a legacy raw Marker conversion. The corpus pipeline does not use it as an intermediate.
