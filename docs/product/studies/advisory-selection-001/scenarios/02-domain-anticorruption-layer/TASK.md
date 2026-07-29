# "Order complete" emails going out for short shipments

Since the July 28 warehouse drop, customers whose orders only partly shipped
are being told their order is complete. Ticket #4821: ORD-1042 ordered 12 of
SKU KB-0442, the warehouse sent 4 and stopped, yet the portal shows the order
as fulfilled and the completion email went out. The nightly summary counted
that line as completed too, so ops never flagged it.

Reproduce from the repo root:

    python3 -m orderdesk.sync data/merc_feed_2026-07-28.json
    python3 -m orderdesk.reports data/merc_feed_2026-07-28.json

Expected: ORD-1042 is not marked fulfilled, no completion email is queued, and
the summary reflects the shortfall. Actual: fulfilled, completion email queued,
line counted as completed.
