# OrderDesk

Pilot order-tracking service for the KeebSupply storefront. OrderDesk keeps
customer orders in a small local store, applies the distributor's MERC
warehouse feed to them, emails customers on shipment milestones, and prints
a nightly operations summary.

## Layout

- `orderdesk/models.py` — orders, lines, statuses
- `orderdesk/store.py` — flat-file order store (`data/orders.json`)
- `orderdesk/merc_client.py` — reads the MERC drop file
- `orderdesk/sync.py` — applies a feed to the store, queues customer emails
- `orderdesk/notifications.py` — email templates
- `orderdesk/reports.py` — nightly ops summary
- `docs/merc_feed_notes.md` — field notes on the MERC feed

## Running

From the repo root:

    python3 -m orderdesk.sync data/merc_feed_2026-07-28.json
    python3 -m orderdesk.reports data/merc_feed_2026-07-28.json

## Tests

    python3 -m pytest -q
