from ledgerline.cli import main
from ledgerline.importer import run_import
from ledgerline.store import LedgerStore

VALID_EXPORT = """date,account,amount,memo
2026-03-14,coastal-checking,42.50,coffee
2026-03-15,coastal-checking,(12.00),refund reversal
2026-03-15,harbor-savings,"1,000.00",transfer
"""

EXPORT_WITH_FOOTER = """date,account,amount,memo
2026-03-14,coastal-checking,42.50,coffee
2026-03-15,harbor-savings,"1,000.00",transfer
TOTAL,,2 items,
"""


def _incoming(tmp_path, **files):
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    for name, text in files.items():
        (incoming / f"{name}.csv").write_text(text, encoding="utf-8")
    return incoming


def test_imports_every_row_of_a_valid_export(tmp_path):
    incoming = _incoming(tmp_path, export_a=VALID_EXPORT)
    store = LedgerStore(tmp_path / "ledger.db")
    try:
        run_import(incoming, store)
        assert store.count() == 3
        coastal = store.transactions_for("coastal-checking")
        assert sorted(t.amount_cents for t in coastal) == [-1200, 4250]
    finally:
        store.close()


def test_footer_row_does_not_block_real_rows(tmp_path):
    incoming = _incoming(tmp_path, export_a=EXPORT_WITH_FOOTER)
    store = LedgerStore(tmp_path / "ledger.db")
    try:
        run_import(incoming, store)
        assert store.count() == 2
    finally:
        store.close()


def test_cli_clean_run_reports_summary(tmp_path, capsys):
    incoming = _incoming(tmp_path, export_a=VALID_EXPORT)
    exit_code = main([str(incoming), "--db", str(tmp_path / "ledger.db")])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Imported 3 transactions from 1 files" in out
