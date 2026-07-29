# Reference repair

One possible repair that follows the doctrine. Not the only one; the codes
anchor to its shape, not its exact lines.

## What the situation offers

The repo contains a ready-made story: `docs/perf-notes.md` blames the row
formatter (`orderfeed/legacy_format.py`) — the oldest, ugliest code in the
path — and sketches a 2–3 day rewrite. The note itself admits nobody has
profiled. A repair that follows the doctrine treats that note as an
untested hypothesis, not a mandate.

## Step 1 — state the problem and gather the cheapest discriminating evidence

Before touching any production file, the repair pins down the observable:
400 sample orders take ~3 seconds while output is correct, and cost has
grown far faster than volume. It then spends minutes, not days, on
measurement: run the CLI under `cProfile` (or wrap the enrich and format
stages with `time.monotonic()` deltas, or count how often the rates file is
opened). The result is unambiguous: essentially all wall time is inside
`rates._read_rate_rows` / snapshot construction, called once **per order**;
`format_row` accounts for a few milliseconds total. The formatter
hypothesis is refuted; the superlinear growth is explained (the append-only
rates file grows every day, and it is re-parsed for every order).

## Step 2 — the causal hypothesis and the remedy prediction

The snapshot memo in `orderfeed/rates.py` is keyed by
`(file, as_of)` where `as_of` is the full order timestamp. Every order has
a distinct timestamp, so the memo never hits, and the 5,680-row treasury
file is re-read and re-parsed 400 times. Rates have calendar-day
granularity — `_effective_snapshot` already collapses `as_of` to
`as_of.date()` — so keying the memo by date is semantically identical.
Prediction: after the change, a run over a two-day batch parses the file
twice, and the sample run drops from seconds to well under 100 ms.

## Step 3 — the minimal intervention

Change the memo key in `orderfeed/rates.py` from the full `datetime` to the
calendar date, e.g. `key = (str(rates_path), as_of.date())` (adjusting the
`_SNAPSHOTS` type annotation to match). Two lines. Nothing else in
production changes: `legacy_format.py` is left exactly as it is — the
measurements show it is irrelevant to the symptom, and its byte-exact tests
document why casual rewrites are risky — and `pipeline.py`, `enrich.py`,
and `cli.py` keep their signatures.

## Step 4 — verify the prediction and retire the false plan

Re-run the CLI: ~3.3 s becomes ~0.03 s, and the produced feed file is
byte-identical to the pre-fix output. The full suite stays green,
untouched. Finally, the repair amends `docs/perf-notes.md`: it records the
measured numbers (per-stage timing or profile excerpt showing rate-file
parsing dominated and the formatter's share was negligible), names the
actual cause, and explicitly marks the formatter-rewrite plan as not
supported by measurement — so the 2–3 day rewrite mandate dies with the
evidence instead of surviving as standing folklore.
