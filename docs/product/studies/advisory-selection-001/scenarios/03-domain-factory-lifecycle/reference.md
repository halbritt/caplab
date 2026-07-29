# Reference repair — one possible doctrine-following solution

This is one good repair, not the only one. It anchors the codes.

## Diagnosis

The root cause is that rehydrating a stored voucher is routed through the
same construction path that creates a brand-new one. `VoucherStore.load`
calls `VoucherFactory.build`, which unconditionally mints a fresh
`voucher_id`, stamps `issued_at = now`, records a new `"issued"` audit
event, and re-runs issuance-only checks (positive balance). Every
load–mutate–save cycle therefore inserts a second row under a new primary
key (the upsert never conflicts) and appends a second issuance entry —
which is exactly the finance symptom. A fully redeemed voucher cannot even
be reloaded, because the zero balance fails the "issued with a positive
balance" rule: a creation-time invariant misapplied to an object that is
merely being brought back from storage. Two further problems sit in the
same seam: `Voucher()` starts blank and is patched field by field, so a
half-initialised, invalid instance exists on every construction path until
the factory's trailing `_check`; and the trivial `Money` value is only
valid if callers remember to go through `MoneyFactory.create`, since
`Money(...)` itself accepts anything.

## The repair

**1. Make the constructor establish the complete valid whole.**
`Voucher.__init__` takes the full state — `voucher_id`, `code`, `balance`,
`status`, `issued_at`, `expires_at` — and enforces the invariants that must
hold for *any* voucher (well-formed code, non-negative balance, expiry
after issue). The blank-`Voucher()`-then-assign-then-`_check` assembly is
deleted. Nothing can hold a partially built voucher. Note the constructor
allows a zero balance: "issued with a positive balance" is an issuance
rule, not a lifetime rule, so it moves to the creation path.

**2. Separate new creation from bringing-back-from-storage.** A named
creation entry point — e.g. classmethod `Voucher.issue(code, amount,
currency, valid_days)` — is now the *only* place a fresh `voucher_id` and
`issued_at` are generated and the `"issued"` event is recorded. Identity
generation is explicit and lives in exactly one spot. `VoucherStore.load`
stops calling any build routine: it invokes the constructor directly with
the row's stored `voucher_id`, `issued_at`, `expires_at`, `status`, and
balance, and records no event. Reloading is now a no-op with respect to
identity, timestamps, and audit.

**3. Retire the ceremony.** With a validating constructor plus one named
creation method, the `VoucherFactory` class no longer earns its layer.
`Money` likewise gains a validating constructor (normalise, reject
negatives and unknown currencies) and production code constructs `Money`
directly; `MoneyFactory` is deleted or kept only as a deprecated one-line
alias delegating to the constructor, because the existing tests import
`MoneyFactory.create` and `VoucherFactory.build` and must not be edited.
`VoucherFactory.build` similarly survives at most as a thin delegate to
`Voucher.issue`. Neither shim assembles anything itself.

## Effect

`save`'s upsert now actually conflicts on the stable `voucher_id` and
updates in place: one row per voucher, liability falls after redemption,
one issuance entry forever, original issue date preserved, exhausted
vouchers reload fine. No report, ledger query, or test changes — the
`ORDER BY rowid DESC` crutch in `load` becomes dead weight that may be
dropped but doesn't have to be. What must *not* happen: threading stored
ids through the new-issuance build via flags or post-build overwrites, or
deduplicating rows/audit entries downstream in `Ledger` or `save` while
reloading still runs creation.
