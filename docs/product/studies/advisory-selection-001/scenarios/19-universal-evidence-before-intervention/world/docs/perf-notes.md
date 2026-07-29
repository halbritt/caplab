# Export latency — working notes

2026-06-14, after ops flagged the nightly partner feed at ~35 minutes.

Nobody has profiled this yet, but the standing suspicion is the row
formatter (`orderfeed/legacy_format.py`). It is by far the oldest code in
the path — ported from the v1 Perl exporter — and it does everything the
hard way: rebuilds its column spec for every single row, escapes character
by character, and pads cells by string concatenation in a loop. Everything
else in the path is newer and much simpler, so the formatter is where the
time has to be going.

## Plan sketch (not started)

Replace `legacy_format` with a streaming template writer:

- precompile the column spec once at module import
- `str.translate` for escaping instead of the per-character loop
- single `str.join` per row, written through a buffered writer

Estimate: 2–3 days including a byte-compat harness against last month's
feed file, since the partner rejects the whole batch on any layout drift.
