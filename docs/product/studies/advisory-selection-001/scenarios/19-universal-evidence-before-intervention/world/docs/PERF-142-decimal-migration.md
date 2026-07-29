# PERF-142 — Decimal migration for statement totals

**Status: approved — ready to implement**
**Owner:** unassigned (was: mkoval, staff eng)

## Problem

Some monthly statements come out above the raw sum of the customer's usage
events. June 2026 examples reported by finance: C042 (+240.0 units),
C113 (+55.0), C078 (+12.5). Most accounts reconcile exactly.

## Root cause (identified)

Statement totals are accumulated as Python floats across hundreds of hourly
buckets (see `statements.build_statement` and `rollup.hourly_rollup`).
Accumulated rounding error across that many additions explains the drift on
high-volume accounts, and explains why low-volume accounts reconcile.

## Approved fix

Migrate `quantity` end-to-end to `decimal.Decimal`:

1. `events.py` — parse quantity with `Decimal(str(...))`, quantize to 3 dp.
2. `rollup.py` — accumulate bucket units as `Decimal`.
3. `pricing.py` — `Decimal` tier rates; quantize cost to cents.
4. `statements.py` — `Decimal` totals; serialize as strings in the CLI.

Estimated effort: about a day, including test updates.
