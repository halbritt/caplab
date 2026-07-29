# Changelog

## 0.5.0 — 2026-04-17
- Applied DPX rate notice #713: volumetric divisor cut from 5000 to 4000.
  Checkout quoting picks up the new divisor.
- Refreshed ARO zone rates in the rate card.

## 0.4.1 — 2025-11-03
- Fix: the remote-area surcharge was included in checkout quotes but missing
  from invoices, so remote deliveries under-billed for months. Surcharge math
  now lives in `shipq/surcharges.py` and both paths call it.

## 0.4.0 — 2025-09-20
- Cash-on-delivery fee support on invoices.

## 0.3.0 — 2025-02-11
- Per-carrier minimum-charge floors.

## 0.2.0 — 2024-06-02
- Carrier metadata module (`shipq/carriers.py`): service labels, tracking
  links, transit estimates, depot cutoffs.

## 0.1.0 — 2024-03-15
- Initial extraction from the monolith: checkout quoting and invoice totals.
