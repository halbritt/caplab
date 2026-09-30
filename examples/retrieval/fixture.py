"""Provider-free toy retrievers; inputs contain corpus/query text, never gold labels."""
from __future__ import annotations

import argparse
import json
import re
import sys

STOP_WORDS = frozenset("a an and are as at by cairn does for from how in is it of on or the to uses what with".split())
SYNONYMS = {"opening": "startup", "initial": "startup", "fetch": "pull", "fetching": "pull",
            "remembered": "memory", "reminders": "memory", "launch": "startup"}


def terms(text: str) -> set[str]:
    return {SYNONYMS.get(word, word) for word in re.findall(r"\w+", text.casefold())
            if word not in STOP_WORDS}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("mode", choices=("good", "bad", "empty", "failing", "malformed"))
    parser.add_argument("--project", default="cairn")
    args = parser.parse_args(argv)
    if args.mode == "failing":
        print("intentional command-fixture failure", file=sys.stderr)
        return 17
    if args.mode == "malformed":
        print("intentional non-JSON response")
        return 0
    try:
        request = json.load(sys.stdin)
        if request["schema_version"] != "caplab-retrieval-request/1":
            raise ValueError("request_schema")
        if set(request) != {"schema_version", "query_id", "query", "seed", "corpus", "cutoff"}:
            raise ValueError("request_fields")
        corpus, cutoff = request["corpus"], request["cutoff"]
        if type(cutoff) is not int or cutoff < 1:
            raise ValueError("request_cutoff")
        if args.mode == "good":
            query_terms = terms(request["query"])
            eligible = [note for note in corpus if note.get("shareable", True)
                        and note.get("repo", args.project) == args.project
                        and not note.get("supersede_with")]
            ranked = sorted(((len(query_terms & terms(note["body"])), note["id"]) for note in eligible),
                            key=lambda pair: (-pair[0], pair[1]))
            ids = [nid for score, nid in ranked if score > 0][:cutoff]
        elif args.mode == "bad":
            ids = [note["id"] for note in reversed(corpus)][:cutoff]
        else:
            ids = []
    except (ValueError, KeyError, TypeError) as error:
        print(json.dumps({"code": "fixture_invalid_request", "error_type": type(error).__name__}), file=sys.stderr)
        return 2
    print(json.dumps({"schema_version": "caplab-retrieval-response/1", "ranked_ids": ids,
                      "observation": {"provider_free_fixture": True, "strategy": args.mode,
                                      "body_delivery_observed": False}}, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
