# walletd

Prepaid customer credit wallets for the Solstice billing sandbox. Balances are
integers in cents; every movement is mirrored into an append-only ledger so
statements can be rebuilt. This tree is the in-memory reference
implementation; the production deployment swaps `WalletStore` and `Ledger` for
the Postgres-backed versions and mounts `api.py` behind FastAPI routes.

## Layout

| module | what |
|---|---|
| `walletd/models.py` | wallet and ledger-entry records |
| `walletd/services.py` | wallet operations: top-up, charge, adjustment, transfer |
| `walletd/store.py` | in-memory wallet repository |
| `walletd/ledger.py` | append-only movement log and statement rendering |
| `walletd/promotions.py` | promotional credit grants and the expiry clawback batch |
| `walletd/api.py` | payload-to-response handlers for the sandbox HTTP layer |
| `walletd/errors.py` | failure types the API layer knows how to render |

## Tests

```bash
python3 -m pytest -q
```
