# Morning digest is unreadable

The nightly digest posted to the on-call channel has become useless. Yesterday's ran to roughly 1,400 lines. Nearly all of it was the same disk-latency warning from storage-03 and app-02, repeated once per check for the whole night. The one line that mattered, the failed database backup on db-01, sat near line 900, and on-call didn't spot it until midday.

Reproduce: from the repo root, run `python3 scripts/simulate_night.py` and open the digest file it names.

Expected: something on-call can scan in under a minute, with anything urgent impossible to miss. Actual: a wall of repeated warnings with the real failure lost in the middle.
