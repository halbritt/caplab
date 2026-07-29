# Reference repair (one possible shape, not the only one)

The immediate symptom is that a negative adjustment can push a wallet below
zero: `WalletService.apply_adjustment` rebinds `wallet.balance_cents` directly
and is the only money-moving path without a funds check. The deeper problem is
where the rules live. `Wallet` is a passive record; every rule about its
balance is written into `WalletService`, once per entry point. That is exactly
why `charge` and `transfer` each carry their own private copy of the
insufficient-funds check and `apply_adjustment` simply never got one — the
rule has no owner, so each new entry point must remember to restate it.

A repair that follows the doctrine puts the balance behaviour on the object
that owns the balance:

- `Wallet` gains `deposit(amount_cents)` and `withdraw(amount_cents)` (names
  vary; `credit`/`debit` is equally good). `withdraw` refuses — raising
  `InsufficientFunds` — whenever the requested amount exceeds
  `balance_cents`; both refuse non-positive amounts. The wallet's balance is
  now changed only by the wallet itself.
- `WalletService.top_up`, `charge`, and `apply_adjustment` stop doing balance
  arithmetic. Each fetches the wallet, decides whether the operation is
  allowed in the wallet's current status (charges need ACTIVE; adjustments
  still run on frozen wallets), invokes `wallet.deposit(...)` or
  `wallet.withdraw(...)`, and records the ledger entry. A negative adjustment
  becomes `wallet.withdraw(-amount_cents)`, so a clawback that exceeds the
  balance is refused exactly the way an oversized charge is, and the promo
  batch surfaces that refusal instead of writing a negative balance.
- `transfer` stays where it is. A movement between two wallets belongs to
  neither wallet, so it rightly remains a standalone operation outside the
  `Wallet` class — but its body becomes `source.withdraw(amount)` followed by
  `dest.deposit(amount)`, and its private copy of the funds check disappears.
- After the repair the amount-versus-balance decision exists in exactly one
  place, inside `Wallet`. `services.py` no longer compares amounts against
  balances and no longer assigns to `balance_cents` anywhere.
- No test changes are needed. Existing tests still pass: the exception types
  and return values are unchanged, and no existing test pinned the
  negative-balance behaviour.

What this repair is **not**: it does not add a third copy of the funds check
inside `apply_adjustment` or the promo batch; it does not clamp balances to
zero; it does not fold the two-wallet transfer into `Wallet`; and it does not
touch the ledger, store, API, or test layers beyond what the new call shape
requires (which, here, is nothing).
