"""Text normalization shared by the search index and query parsing."""

import re

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {"a", "an", "and", "for", "in", "of", "on", "or", "the", "to", "with"}


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens, with stopwords and single characters dropped."""
    tokens = _WORD.findall(text.lower())
    return [t for t in tokens if len(t) > 1 and t not in _STOPWORDS]
