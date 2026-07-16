"""Pincite locator parsing used by CAPLAB's evaluation harness."""

from __future__ import annotations

import re


def plain_heading(markup: str) -> str:
    value = markup.strip().rstrip("#").strip()
    value = re.sub(r"^(?:\*\*|__)?<sup>\d+</sup>(?:\*\*|__)?\s*", "", value)
    value = re.sub(r"^(?:\*\*|__)\d+(?:\*\*|__)\s*", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = value.replace("\\_", "_")
    while len(value) >= 2:
        changed = re.sub(
            r"^(?:\*\*|__|\*|_)(.*?)(?:\*\*|__|\*|_)$", r"\1", value
        )
        if changed == value:
            break
        value = changed
    return value.replace("*", "").strip()


def parse_heading_selector(expected: str) -> tuple[str, dict[str, str]]:
    if " @@ " not in expected:
        return expected, {}
    heading, raw_selectors = expected.rsplit(" @@ ", 1)
    selectors: dict[str, str] = {}
    for selector in raw_selectors.split(";"):
        if "=" not in selector:
            return heading, {"invalid": raw_selectors}
        key, value = selector.split("=", 1)
        selectors[key.strip()] = value.strip()
    return heading, selectors
