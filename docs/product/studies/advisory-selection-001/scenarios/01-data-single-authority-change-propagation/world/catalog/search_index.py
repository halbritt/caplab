"""Word index over item text, saved to disk so restarts keep search warm."""

from __future__ import annotations

import json
import os

from .text import tokenize


class SearchIndex:
    """Maps word -> item ids. Saves after every mutation when given a path."""

    def __init__(self, path: str | None = None):
        self._path = path
        self._postings: dict[str, set[str]] = {}
        self._doc_words: dict[str, set[str]] = {}
        if path and os.path.exists(path):
            self._load()

    def upsert(self, item: dict) -> None:
        item_id = item["id"]
        self._unlink(item_id)
        words = set(
            tokenize(" ".join((item["name"], item["description"], " ".join(item["tags"]))))
        )
        self._doc_words[item_id] = words
        for word in words:
            self._postings.setdefault(word, set()).add(item_id)
        self._save()

    def remove(self, item_id: str) -> None:
        self._unlink(item_id)
        self._save()

    def lookup(self, query: str) -> list[str]:
        """Item ids matching any query word, best matches first."""
        words = set(tokenize(query))
        if not words:
            return []
        hits: dict[str, int] = {}
        for word in words:
            for item_id in self._postings.get(word, ()):
                hits[item_id] = hits.get(item_id, 0) + 1
        return [i for i, _ in sorted(hits.items(), key=lambda kv: (-kv[1], kv[0]))]

    def known_ids(self) -> set[str]:
        return set(self._doc_words)

    def _unlink(self, item_id: str) -> None:
        for word in self._doc_words.pop(item_id, set()):
            ids = self._postings.get(word)
            if ids:
                ids.discard(item_id)
                if not ids:
                    del self._postings[word]

    def _save(self) -> None:
        if not self._path:
            return
        payload = {item_id: sorted(words) for item_id, words in self._doc_words.items()}
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        os.replace(tmp, self._path)  # swap the whole file so a crash mid-save never leaves a torn index

    def _load(self) -> None:
        with open(self._path, encoding="utf-8") as fh:
            payload = json.load(fh)
        self._doc_words = {item_id: set(words) for item_id, words in payload.items()}
        self._postings = {}
        for item_id, words in self._doc_words.items():
            for word in words:
                self._postings.setdefault(word, set()).add(item_id)
