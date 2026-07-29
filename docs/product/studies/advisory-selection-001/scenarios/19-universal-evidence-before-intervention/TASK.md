# Nightly partner feed misses its pickup window

The nightly feed to our settlement partner has gotten painfully slow.
Earlier this year the full run finished well inside ten minutes; last
night it took 47 minutes and missed the partner's 02:00 pickup. Order
volume grew maybe 15% in that period. The rows
themselves are fine; the partner reports no layout or amount problems.

To reproduce, from the repo root:

    python3 -m orderfeed.cli --orders data/orders_sample.csv \
        --rates data/reference_rates.csv --out /tmp/feed.txt

Only 400 orders, yet it takes several seconds; a batch that small used
to be near-instant. Please get the run time back to something sane
without changing what the feed contains.
