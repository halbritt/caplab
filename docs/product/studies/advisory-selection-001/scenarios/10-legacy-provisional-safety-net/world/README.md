# meterflow

Generates monthly residential billing statements from the meter-reading CSV
export the AMI vendor drops each month.  Writes one plain-text statement per
account plus a `summary.txt` for the run.

## Usage

```
python -m meterflow.cli <tariff.json> <readings.csv> <out_dir> [--as-of YYYY-MM-DD]
```

`--as-of` sets the statement date (and the due date, 21 days later).  It
defaults to today; ops passes an explicit date when re-running a past month.

A sample tariff and a trimmed June export live in `sample_data/`.

## Tests

```
python3 -m pytest -q
```

## Notes

- The tariff's `tiers` field is a list of `[cumulative_cap_kwh, rate_cents]`
  pairs; the last tier's cap is `null`.
- Statement wording in the payment-terms line is regulator-approved
  (docket 19-0442); do not reword it.
- The ops dashboard scrapes `statement._LAST_RUN` from the worker process;
  keep those keys stable.
