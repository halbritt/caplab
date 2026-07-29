# Voucher liability report inflates after redemptions

Finance flagged our month-end numbers: the outstanding gift-voucher liability total goes up after customers redeem, and the audit trail shows the same voucher being issued a second time.

To reproduce: issue a voucher for 50.00 EUR, redeem 20.00 against it, then run the ledger's outstanding total and that voucher's issuance history.

Expected: outstanding total 30.00 and a single issuance entry with the original date. Actual: outstanding total 80.00 and two issuance entries, the second stamped at redemption time.

Customer-facing balance checks still show the right amount, so nothing alerted. Please make the finance numbers and the audit trail trustworthy again.
