"""Cosmetic formatting helpers shared by statements and the run summary."""


def money(cents):
    """Render an integer number of cents as a currency string."""
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents) / 100:,.2f}"


def per_kwh(rate_cents):
    """Render a per-kWh rate given in cents, e.g. 10.0 -> '$0.100'."""
    return f"${rate_cents / 100:.3f}"


def usage_bar(usage_kwh, width=20):
    """A crude ASCII gauge for the run summary. One '#' per 25 kWh."""
    filled = min(width, usage_kwh // 25)
    return "#" * filled + "." * (width - filled)
