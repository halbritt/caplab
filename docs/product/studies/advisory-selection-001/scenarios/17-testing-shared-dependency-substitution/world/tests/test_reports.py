from datetime import date

from ledgerlib.models import Money
from ledgerlib.reports import ReportBuilder


def test_account_activity_totals_one_month(ledger, store):
    ledger.open_account("acct-cafe", "Staff cafe")
    ledger.post("acct-cafe", Money(1200), "meals", date(2026, 3, 6))
    ledger.post("acct-cafe", Money(1800), "meals", date(2026, 3, 19))
    builder = ReportBuilder(store)
    assert builder.account_activity("acct-cafe", 2026, 3) == Money(3000)


def test_activity_excludes_neighbouring_months(ledger, store):
    ledger.open_account("acct-print", "Print shop")
    ledger.post("acct-print", Money(700), "office", date(2026, 8, 31))
    ledger.post("acct-print", Money(950), "office", date(2026, 9, 1))
    builder = ReportBuilder(store)
    assert builder.account_activity("acct-print", 2026, 9) == Money(950)


def test_category_totals_scoped_to_requested_accounts(ledger, store):
    ledger.open_account("acct-studio", "Studio hire")
    ledger.open_account("acct-darkroom", "Darkroom supplies")
    ledger.post("acct-studio", Money(5000), "travel", date(2026, 5, 4))
    ledger.post("acct-studio", Money(2500), "meals", date(2026, 5, 12))
    ledger.post("acct-darkroom", Money(1100), "office", date(2026, 5, 18))
    builder = ReportBuilder(store)
    totals = builder.category_totals(2026, 5, account_ids={"acct-studio"})
    assert totals == {"travel": Money(5000), "meals": Money(2500)}


def test_activity_for_quiet_month_is_zero(ledger, store):
    ledger.open_account("acct-cold", "Cold storage")
    builder = ReportBuilder(store)
    assert builder.account_activity("acct-cold", 2026, 6) == Money(0, "USD")
