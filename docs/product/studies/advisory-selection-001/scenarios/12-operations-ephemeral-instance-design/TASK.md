# Usage totals frozen for about half our customers

Since last Tuesday's maintenance, when one of the two metering workers
was swapped for a freshly imaged VM, nightly usage totals for roughly
half of our customers have stopped moving — dashboards still show
Tuesday's numbers. The new machine looks healthy — the run logs
"cycle complete" and exits zero. Restarting and redeploying changed
nothing. To reproduce, bring up a fresh worker and run a nightly cycle.

Possibly related: a May in-place worker rebuild produced a day of
doubled totals for its customers, hand-corrected by billing.

Expected: every customer's totals advance nightly. Actual: half
are stuck, and past rebuilds have double-counted.
