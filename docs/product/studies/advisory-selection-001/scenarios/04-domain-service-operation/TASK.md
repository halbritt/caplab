# Wallets going negative after the promo expiry run

Support escalated four wallets that went below zero after Monday's
promotional-credit expiry run. Wallets are prepaid: checkout already refuses a
charge when credit is short, and that still works. But reclaiming an expired
promotional grant from a wallet whose credit was partly spent leaves the
wallet negative (one reads -200 cents), and the statement then shows the
customer owing us money.

To reproduce in the sandbox: top up 500, charge 400, then run the expiry batch
for a 300-cent grant. Expected: the reclaim is refused, the same way an
oversized charge is. Actual: it goes through and the balance reads -200.
