# worklog

Tiny time-entry logger. Entries live in a JSON Lines file; `report` aggregates
them per project and prints the table in one of the export formats.

## Usage

```bash
python3 -m worklog add --input sample/worklog.jsonl --project acme --hours 2.5 --note "pairing"
python3 -m worklog report --input sample/worklog.jsonl --format csv
python3 -m worklog report --input sample/worklog.jsonl --format jsonl
```

## Export backends

Backends live in `worklog/export/`. To add one, subclass `BaseExporter`,
implement `format_cell` / `format_row` (plus optional `begin` / `end`), and
decorate the class with `@register`. The shared `render()` pipeline handles
iteration, the header, and line assembly, so most backends fit on a screen.
Planned backends on the roadmap: TSV, XML, fixed-width.
