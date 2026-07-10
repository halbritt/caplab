# Books

This repository keeps source PDF and EPUB books in the repository root and builds
a semantically structured Markdown corpus under [`books/`](books/README.md).

## Source books

The repository currently contains these root-level source books:

| Book | Source file |
| --- | --- |
| A Philosophy of Software Design, 2nd Edition | `dokumen.pub_a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217.epub` |
| Clean Architecture: A Craftsman's Guide to Software Structure and Design | `Clean Architecture A Craftsman Guide to Software Structure and Design.pdf` |
| Code Complete, 2nd Edition | `code-complete-2nd-edition-v413hav.pdf` |
| Domain-Driven Design: Tackling Complexity in the Heart of Software | `Domain Driven Design Tackling Complexity in the Heart of Software - Eric Evans.pdf` |
| Efficient Go: Data-Driven Performance Optimization | `Efficient Go Data-Driven Performance Optimization (Bartlomiej Plotka) (Z-Library).pdf` |
| Fluent Python, 2nd Edition | `Fluent.Python.2nd.Edition.(z-lib.org).pdf` |
| Fundamentals of Software Architecture | `OReilly.Fundamentals.of.Software.Architecture.2020.1.pdf` |
| Refactoring: Improving the Design of Existing Code | `Refactoring  Improving the Design of Existing Code.pdf` |
| Software Design X-Rays: Fix Technical Debt with Behavioral Code Analysis | `dokumen.pub_software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725.pdf` |
| The Pragmatic Programmer | `the-pragmatic-programmer.pdf` |
| Working Effectively with Legacy Code | `[PROGRAMMING][Working Effectively. with Legacy Code].pdf` |

Run the complete root-level ingestion pipeline with:

```bash
make books
```

The command uses Marker on `peecee` for PDFs and Pandoc for EPUBs. It discovers
only root-level source files, preserves the originals, extracts assets, splits on
logical chapter boundaries, and writes metadata, provenance, and validation
records for every book.

Run the tests and validate existing generated output without invoking converters:

```bash
make check
```

Generated books carry file manifests and integrity checks. The pipeline refuses
to overwrite unexpected edits unless `scripts/convert-books --force` is invoked
explicitly. The tracked `out/Refactoring/` directory is the legacy raw Marker
conversion and is not used as an intermediate by the corpus pipeline.
