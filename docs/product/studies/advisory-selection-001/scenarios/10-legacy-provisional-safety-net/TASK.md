# Wrong totals on high-usage June statements

Billing ops flagged the June run. Account 1042 metered 312 kWh, but its statement's rate lines read 100 + 250 + 62 kWh — 412 kWh, 100 more than the meter recorded — and the amount due prints as $79.32 where our rate-sheet check says $63.42. Every spot-checked account above 250 kWh is off the same way; those at or below 250 kWh match to the cent.

Reproduce:

    python -m meterflow.cli sample_data/tariff.json sample_data/readings_2026-06.csv /tmp/june --as-of 2026-06-30

then open `/tmp/june/1042.txt`.

Expected: rate lines that sum to the metered usage and a total of $63.42. Actual: 412 kWh across the rate lines and $79.32.
