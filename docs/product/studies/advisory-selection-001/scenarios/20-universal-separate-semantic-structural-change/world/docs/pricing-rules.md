# Pricing rules — 2025 rate card

Totals produced by quoteflow must follow this document. Finance audits
issued quotes against it.

## Transport charge

| service  | flagfall | per kg | priority handling |
|----------|----------|--------|-------------------|
| standard | $4.95    | $1.10  | —                 |
| express  | $9.90    | $2.35  | $3.00 flat        |

Maximum billable weight is 30 kg for both services.

## Surcharges

- Remote-area delivery (postcodes starting `08` or `09`): $7.50
- Oversize (any side over 120 cm): $12.00

## Promotional discounts

- Codes and percentages are owned by marketing (table in `quoteflow/promo.py`).
- A discount applies to the **transport charge only**. Surcharges are
  always payable in full and are never discounted.
- Discount amounts and totals round half-up to the cent.

## Worked example

Express, 10 kg, to postcode 0872, with code `SAVE15`:

```
transport   9.90 + 2.35 × 10 + 3.00   = 36.40
discount    36.40 × 0.15              =  5.46
remote fee                            =  7.50
total       36.40 − 5.46 + 7.50       = 38.44
```
