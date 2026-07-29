"""Fetch the MERC warehouse shipment feed.

MERC is the distributor's warehouse management system, an AS/400-era
package. It exports shipment lines as a JSON array, one object per order
line, dropped for us over SFTP. In the pilot we read the drop file
directly.

Fields, per the vendor integration sheet (rev 14) — see also
docs/merc_feed_notes.md:

    ord_ref     order reference (matches our order_id)
    sku         item code, same catalogue as ours
    qty_ord     units ordered
    qty_shp     units shipped so far (cumulative)
    stat_cd     O = open, P = picking, C = closed
    dispo       disposition note, set when a record is closed
    carrier_cd  MERC carrier code (FDX, UPS, USPS, LTL)
    upd_ts      last update, warehouse local time (US/Central)
"""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_FIELDS = ("ord_ref", "sku", "qty_ord", "qty_shp", "stat_cd")


def fetch_feed(path: str | Path) -> list[dict]:
    """Read a MERC drop file and return its shipment-line records."""
    records = json.loads(Path(path).read_text())
    if not isinstance(records, list):
        raise ValueError("MERC feed must be a JSON array of shipment lines")
    for i, rec in enumerate(records):
        missing = [f for f in REQUIRED_FIELDS if f not in rec]
        if missing:
            raise ValueError(f"record {i} is missing {', '.join(missing)}")
    return records
