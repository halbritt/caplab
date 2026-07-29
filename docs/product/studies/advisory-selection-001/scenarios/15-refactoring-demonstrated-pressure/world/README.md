# shipq

Internal parcel-pricing library: checkout quoting and post-delivery invoicing.

- `shipq.quotes` — the price shown to the customer at checkout
- `shipq.invoicing` — the final amount charged after the delivery scan-in
- `shipq.carriers` — carrier metadata (service labels, tracking links, transit)
- `shipq.rate_tables` — negotiated base rates and minimum charges
- `shipq.surcharges` — fuel and remote-area surcharges (shared by both paths)

## Running the tests

```
python3 -m pytest -q
```
