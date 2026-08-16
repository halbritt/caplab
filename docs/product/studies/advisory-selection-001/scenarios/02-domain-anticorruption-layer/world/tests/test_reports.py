from orderdesk.reports import summarize


def rec(stat_cd, qty_ord, qty_shp, dispo=""):
    return {
        "ord_ref": "ORD-5001",
        "sku": "KB-0100",
        "qty_ord": qty_ord,
        "qty_shp": qty_shp,
        "stat_cd": stat_cd,
        "dispo": dispo,
        "carrier_cd": "",
        "upd_ts": "2026-07-27 09:15:00",
    }


def test_counts_by_stage():
    records = [
        rec("O", 2, 0),
        rec("P", 5, 0),
        rec("C", 4, 4, dispo="OK"),
    ]
    summary = summarize(records)
    assert summary["total_lines"] == 3
    assert summary["open_lines"] == 1
    assert summary["picking_lines"] == 1
    assert summary["completed_lines"] == 1


def test_fill_rate_uses_units():
    records = [rec("C", 4, 4, dispo="OK"), rec("P", 6, 2)]
    summary = summarize(records)
    assert summary["units_ordered"] == 10
    assert summary["units_shipped"] == 6
    assert summary["fill_rate"] == 0.6
