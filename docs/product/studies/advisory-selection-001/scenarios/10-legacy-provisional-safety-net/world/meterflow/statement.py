"""Monthly statement generation.

This module has grown by accretion since the 2019 Fairfield migration.  The
whole run -- tariff load, meter arithmetic, plan discounts, rendering, file
output, run summary -- lives in generate_statements(); ops calls it from cron
through meterflow.cli on the 30th of each month.

Change log kept here because nobody reads the wiki:
  2021-04  fuel surcharge added (PUC docket 21-0117)
  2022-11  ebill plan discount
  2024-02  mechanical meter rollover handling, after the Grady & Sons dispute
"""

import csv
import json
import os
from datetime import date, timedelta

from .formats import money, per_kwh, usage_bar

# Five-digit mechanical meters wrap past 99999 back to 00000.
METER_MODULUS = 100_000

PAYMENT_TERMS_DAYS = 21

# Filled in by the most recent run.  The ops dashboard scrapes this out of a
# long-lived worker process; do not rename the keys without telling ops.
_LAST_RUN = {}


def generate_statements(tariff_path, readings_path, out_dir, as_of=None):
    """Read a tariff file and a monthly readings export, write one statement
    text file per account plus a run summary, and return run totals.

    ``as_of`` is the statement date; it defaults to today.  Ops passes an
    explicit date when re-running a past month.
    """
    if as_of is None:
        as_of = date.today()

    with open(tariff_path) as fh:
        tariff = json.load(fh)

    tiers = tariff["tiers"]
    tax_rate = tariff["tax_rate"]
    service_cents = tariff["service_charge_cents"]
    fuel_cents_per_kwh = tariff["fuel_surcharge_cents_per_kwh"]
    plans = tariff.get("plans", {})

    os.makedirs(out_dir, exist_ok=True)
    due = as_of + timedelta(days=PAYMENT_TERMS_DAYS)

    grand_total = 0
    summary_rows = []

    with open(readings_path, newline="") as fh:
        for row in csv.DictReader(fh):
            if not row.get("account_id"):
                continue  # blank line in the export; the vendor pads files
            account = row["account_id"].strip()
            name = row["name"].strip()
            plan_name = (row["plan"].strip() or "standard")
            start = int(row["meter_start"])
            end = int(row["meter_end"])

            if end >= start:
                usage = end - start
            else:
                # Mechanical rollover: the register passed 99999 mid-cycle.
                usage = (METER_MODULUS - start) + end

            # Tiered energy charge.  Tariff tiers are cumulative caps in kWh
            # with per-kWh rates in cents; the last tier has a null cap.
            blocks = []
            prev_cap = 0
            for cap, rate_cents in tiers:
                if cap is None or usage <= cap:
                    blocks.append((usage - prev_cap, rate_cents))
                    break
                blocks.append((cap, rate_cents))
                prev_cap = cap

            energy = 0
            for qty, rate_cents in blocks:
                energy += round(qty * rate_cents)

            plan = plans.get(plan_name, {})
            discount = round(energy * plan.get("energy_discount", 0.0))
            fuel = round(usage * fuel_cents_per_kwh)
            subtotal = energy - discount + fuel + service_cents
            tax = round(subtotal * tax_rate)
            total = subtotal + tax
            grand_total += total

            lines = []
            lines.append("METERFLOW ENERGY - MONTHLY STATEMENT")
            lines.append("")
            lines.append(f"Account: {account}   {name}")
            lines.append(f"Plan: {plan_name}")
            lines.append(f"Statement date: {as_of.isoformat()}")
            lines.append(f"Due date: {due.isoformat()}")
            lines.append(f"Meter: {start:05d} -> {end:05d}   Usage: {usage} kWh")
            lines.append("")
            for i, (qty, rate_cents) in enumerate(blocks, start=1):
                amount = round(qty * rate_cents)
                lines.append(
                    f"  Tier {i}: {qty} kWh @ {per_kwh(rate_cents)}/kWh"
                    f"{money(amount):>12}"
                )
            if discount:
                lines.append(f"  {plan_name} plan discount{money(-discount):>12}")
            lines.append(f"  Fuel surcharge ({usage} kWh){money(fuel):>12}")
            lines.append(f"  Service charge{money(service_cents):>12}")
            lines.append(f"  Sales tax ({tax_rate:.0%}){money(tax):>12}")
            lines.append("")
            lines.append(f"  TOTAL DUE{money(total):>16}")
            lines.append("")
            # Regulator-approved wording (docket 19-0442); do not edit.
            lines.append("Payment is due within 21 days of the statement date.")

            out_path = os.path.join(out_dir, f"{account}.txt")
            with open(out_path, "w") as out:
                out.write("\n".join(lines) + "\n")

            summary_rows.append(
                f"{account}  {usage:>6} kWh  {usage_bar(usage)}  {money(total):>12}"
            )

    with open(os.path.join(out_dir, "summary.txt"), "w") as out:
        out.write(f"Run date: {as_of.isoformat()}\n")
        out.write(f"Accounts: {len(summary_rows)}\n")
        out.write(f"Billed: {money(grand_total)}\n\n")
        out.write("\n".join(summary_rows) + "\n")

    _LAST_RUN.clear()
    _LAST_RUN.update(
        {
            "as_of": as_of.isoformat(),
            "accounts": len(summary_rows),
            "grand_total_cents": grand_total,
        }
    )
    print(
        f"meterflow: wrote {len(summary_rows)} statements to {out_dir} "
        f"({money(grand_total)} billed)"
    )
    return dict(_LAST_RUN)
