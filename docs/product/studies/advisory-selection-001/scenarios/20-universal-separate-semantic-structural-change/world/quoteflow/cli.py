"""Sales-desk CLI.

Usage: python -m quoteflow.cli <service> <weight-kg> [--postcode P]
       [--promo CODE] [--dims LxWxH]
"""

import argparse
import sys
from decimal import Decimal

from .express import quote_express
from .models import Parcel
from .promo import UnknownPromoCode
from .standard import quote_standard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quoteflow")
    parser.add_argument("service", choices=("standard", "express"))
    parser.add_argument("weight_kg", type=Decimal)
    parser.add_argument("--postcode", default="")
    parser.add_argument("--promo")
    parser.add_argument("--dims", metavar="LxWxH", help="dimensions in cm")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    length = width = height = 0
    if args.dims:
        length, width, height = (int(part) for part in args.dims.lower().split("x"))
    parcel = Parcel(
        weight_kg=args.weight_kg,
        length_cm=length,
        width_cm=width,
        height_cm=height,
        destination_postcode=args.postcode,
    )
    quote_fn = quote_standard if args.service == "standard" else quote_express
    try:
        quote = quote_fn(parcel, promo_code=args.promo)
    except (UnknownPromoCode, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(quote.breakdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
