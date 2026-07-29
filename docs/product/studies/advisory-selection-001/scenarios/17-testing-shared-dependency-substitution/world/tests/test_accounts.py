import pytest

from ledgerlib.errors import DuplicateAccountError, UnknownAccountError


def test_open_account_round_trips(ledger, store):
    ledger.open_account("acct-legal", "Legal retainers")
    account = store.get_account("acct-legal")
    assert account.name == "Legal retainers"
    assert account.currency == "USD"


def test_duplicate_account_id_rejected(ledger):
    ledger.open_account("acct-dup", "First registration")
    with pytest.raises(DuplicateAccountError):
        ledger.open_account("acct-dup", "Second registration")


def test_lookup_of_missing_account_fails(store):
    with pytest.raises(UnknownAccountError):
        store.get_account("acct-never-created")
