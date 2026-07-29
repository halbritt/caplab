"""Partner flat-file row formatting (FLATFEED v2).

This is the oldest code in the export path: ported line-by-line from the v1
Perl exporter in 2019 and deliberately kept bug-for-bug compatible with it.
It rebuilds the column spec for every row, escapes character by character,
and pads by string concatenation.  See docs/perf-notes.md for the standing
plan to replace it with a streaming template writer.
"""

from __future__ import annotations

from orderfeed.models import EnrichedOrder


def _column_spec() -> list[dict]:
    # Column layout for FLATFEED v2 (partner spec rev. 2019-04).
    # NOTE: rebuilt for every row.  Do not "tidy" this piecemeal — the v1
    # exporter had subtle column-ordering bugs whenever this drifted; any
    # replacement should come with the byte-compat harness described in
    # docs/perf-notes.md.
    spec = []
    for name, width in [
        ("order_id", 12),
        ("sku", 16),
        ("qty", 5),
        ("currency", 3),
        ("fx_rate", 10),
        ("amount", 14),
        ("placed", 19),
    ]:
        spec.append({"name": name, "width": width})
    return spec


def _escape(value: str) -> str:
    # Char-by-char to match v1 semantics exactly (pipes and backslashes are
    # escaped; embedded newlines become spaces).
    out = ""
    for ch in value:
        if ch == "|":
            out = out + "\\|"
        elif ch == "\\":
            out = out + "\\\\"
        elif ch == "\n" or ch == "\r":
            out = out + " "
        else:
            out = out + ch
    return out


def format_row(enriched: EnrichedOrder) -> str:
    """Render one pipe-delimited, fixed-width FLATFEED v2 row."""
    order = enriched.order
    values = {
        "order_id": order.order_id,
        "sku": order.sku,
        "qty": str(order.quantity),
        "currency": order.currency,
        "fx_rate": str(enriched.fx_rate),
        "amount": str(enriched.settlement_amount),
        "placed": order.placed_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    row = ""
    for col in _column_spec():
        cell = _escape(values[col["name"]])
        if len(cell) > col["width"]:
            cell = cell[: col["width"]]
        while len(cell) < col["width"]:  # pad by concatenation, v1-compatible
            cell = cell + " "
        if row:
            row = row + "|" + cell
        else:
            row = cell
    return row
