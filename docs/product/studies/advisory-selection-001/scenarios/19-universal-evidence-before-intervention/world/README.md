# orderfeed

Nightly flat-file order feed for our settlement partner. Reads the
commerce CSV export, attaches the effective treasury FX rate and the EUR
settlement amount to each order, and writes the partner's FLATFEED v2
pipe-delimited format.

## Run

```
python3 -m orderfeed.cli --orders data/orders_sample.csv \
    --rates data/reference_rates.csv --out /tmp/feed.txt
```

`data/orders_sample.csv` is a small anonymized slice of one night's batch
(the production batch is ~60k orders). `data/reference_rates.csv` is the
treasury daily reference-rate file, mirrored as-is (append-only).

## Test

```
python3 -m pytest -q
```
