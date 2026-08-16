# Reference repair

One possible good repair, not the only one. What matters is its shape: it
treats the shared exporter pipeline as the mechanism of the defect, not as
fixed infrastructure to patch around.

## Diagnosis

`worklog/export/base.py` defines a template pipeline — `render()` driving
`begin` / `format_cell` / `format_row` / `end` hooks over rows of text cells —
whose real shape is "delimiter-joined text lines". That shape fits CSV. JSON
Lines was forced through it anyway: `JsonlExporter.format_cell` can only
return a string, so every value is laundered through the shared `text()`
helper and re-wrapped in quotes by hand. Numbers become strings by
construction, and a project name containing `"` yields an unparsable line
because hand-assembled JSON never escapes anything. The two formats never
shared a mechanism; they shared a superficial resemblance ("both write
lines"). The base class also carries machinery nothing uses: an `**options`
slot no backend reads, a `@register` decorator whose registry holds exactly
two entries, and hook seams reserved for TSV/XML/fixed-width backends that do
not exist. The defect is not a typo in the JSONL backend; it is the price of
an abstraction that was never earned.

## The repair

1. **Write JSONL directly.** A `render_jsonl(columns, rows)` function builds
   one dict per row and emits `json.dumps(record)` per line. Numbers stay
   numbers and escaping becomes the library's problem — both reported
   symptoms disappear as a consequence, not as special cases.

2. **Let CSV be CSV.** With JSONL out of the pipeline, the base class serves
   exactly one format and earns nothing. `render_csv(columns, rows)` uses the
   stdlib `csv` module (`csv.writer` over an in-memory buffer,
   `lineterminator="\n"`), formatting float cells as `f"{value:.2f}"` at the
   call site — two-decimal display is a CSV-report presentation choice, not a
   universal truth about the data, so the shared `text()` coercion and the
   homegrown `_escape` go away with the base.

3. **Delete the framework.** `base.py` — the ABC, the hooks, `_REGISTRY`,
   `register`, the `**options` plumbing — is removed, along with the
   `csv_exporter.py` / `jsonl_exporter.py` class modules. The public surface
   of `worklog/export/__init__.py` is preserved: `render(name, columns,
   rows)` still raises `ValueError` on unknown names and
   `available_formats()` still answers the CLI, but dispatch is now a literal
   dict, e.g. `_FORMATS = {"csv": render_csv, "jsonl": render_jsonl}`.
   Callers and tests never notice.

4. **Add nothing speculative.** No replacement base class, no serializer
   interface, no `preserve_types` flag, no TSV stub. Two formats are two
   short functions. If a third format arrives and two of the three then
   demonstrate real common mechanism, that is the moment shared structure
   gets built — from observed variation, not anticipated variation.

The README's "add a backend by subclassing `BaseExporter`" section is
rewritten to "add a function and one dict entry".

All four existing test files pass untouched.
