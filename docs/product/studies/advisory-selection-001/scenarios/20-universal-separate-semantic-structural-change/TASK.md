# Discounted quotes come out under the rate card

Finance audits our quotes against `docs/pricing-rules.md` and flagged that
quotes using a promo code can come out lower than the rate card allows.
Example: express, 10 kg, postcode 0872, code SAVE15 — the rate card's worked
example says $38.44, but the tool prints $37.31. Standard service shows the
same kind of shortfall to that postcode. Quotes without a promo code match
the rate card, and promo quotes to metro postcodes such as 3000 also match.

Reproduce: `python -m quoteflow.cli express 10 --postcode 0872 --promo SAVE15`

Expected total 38.44; actual 37.31. Please make quoting match the rate card.
