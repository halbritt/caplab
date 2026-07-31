"""Verify the materialized runtime input tree."""

from __future__ import annotations

import argparse
from pathlib import Path

from .contract import load_input_manifest, verify_input_tree
from .runtime import input_dir_from_env


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_root", type=Path, nargs="?", default=input_dir_from_env()
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("input-manifest.json"),
    )
    args = parser.parse_args()
    entries = load_input_manifest(args.manifest)
    verify_input_tree(args.input_root, entries)
    print(
        f"verified {len(entries)} SFT files ({sum(entry.size for entry in entries)} bytes)"
    )


if __name__ == "__main__":
    main()
