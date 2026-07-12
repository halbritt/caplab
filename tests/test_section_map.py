"""Hermetic tests for the per-book section-map builder.

No real network: model classification goes to an in-process ``http.server``
returning canned OpenAI-style responses on the loopback interface, exactly as
``tests/test_entailment_eval.py`` stubs its judge server.
"""

import json
import re
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "doctrine" / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import build_section_map  # noqa: E402


CHAPTER_TEXT = """# Chapter One

Intro text under the chapter title.

## WARNING

Callout content that belongs to the enclosing section.

## Example 1-2. A caption

Caption content.

## Plain Ambiguous Heading

Body of the ambiguous heading.
Second body line.

## CHECKLIST: Cited Things

This callout-looking heading is cited by doctrine.

## Second Ambiguous Heading

More prose.
"""

TOC_TEXT = """# Table of Contents

| Deep Waters 42          |    |  |
|-------------------------|----|--|
| 3.<br>Rising<br>Tide 57 |    |  |
"""

TOC_BOOK_CHAPTER = """# Chapter Three

Opening prose.

## Deep Waters

Prose about deep waters.

## Rising Tide

Prose about the tide.

## Uncharted Heading

Prose the rules cannot decide.
"""


class FakeClassifierHandler(BaseHTTPRequestHandler):
    """Answers every undecided line with a configurable role."""

    chat_requests = []
    roles_by_line = {}
    default_role = "embedded"
    raw_content = None

    def _send(self, document):
        body = json.dumps(document).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.endswith("/models"):
            self._send({"object": "list", "data": [{"id": "fake-classifier"}]})
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        type(self).chat_requests.append(payload)
        if type(self).raw_content is not None:
            content = type(self).raw_content
        else:
            prompt = payload["messages"][0]["content"]
            match = re.search(r"undecided line number: ([\d, ]+)\.?$", prompt)
            numbers = re.findall(r"\d+", match.group(1)) if match else []
            mapping = {
                number: type(self).roles_by_line.get(
                    number, type(self).default_role
                )
                for number in numbers
            }
            content = "The classification follows:\n" + json.dumps(mapping)
        self._send(
            {
                "model": "fake-classifier",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "reasoning_content": "thinking tokens to ignore",
                            "content": content,
                        },
                    }
                ],
            }
        )

    def log_message(self, *args):
        pass


def write_concepts(root: Path, locators) -> None:
    concepts = root / "doctrine" / "concepts"
    concepts.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_version": "agent-doctrine-concepts/1",
        "concepts": [
            {
                "id": "test-concept",
                "claim": "A claim.",
                "source_support": [
                    {
                        "source_id": "SRC-FAKE",
                        "locator": locator,
                        "contribution": "A contribution.",
                        "relationship": "direct_support",
                    }
                    for locator in locators
                ],
            }
        ],
    }
    (concepts / "mini.yaml").write_text(json.dumps(document), encoding="utf-8")


class SectionMapTestCase(unittest.TestCase):
    def setUp(self):
        FakeClassifierHandler.chat_requests = []
        FakeClassifierHandler.roles_by_line = {}
        FakeClassifierHandler.default_role = "embedded"
        FakeClassifierHandler.raw_content = None
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeClassifierHandler)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.endpoint = f"http://127.0.0.1:{self.server.server_address[1]}/v1"
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        write_concepts(
            self.root,
            ["books/fake-book/chapters/001-one.md :: CHECKLIST: Cited Things"],
        )
        self.chapter = self.root / "books" / "fake-book" / "chapters" / "001-one.md"
        self.chapter.parent.mkdir(parents=True)
        self.chapter.write_text(CHAPTER_TEXT, encoding="utf-8")
        self.map_path = (
            self.root / "doctrine" / "section-maps" / "fake-book.yaml"
        )

    def run_tool(self, *extra):
        argv = ["--repo-root", str(self.root), "--endpoint", self.endpoint, *extra]
        return build_section_map.main(argv)

    def load_map(self, path=None):
        return yaml.safe_load((path or self.map_path).read_text(encoding="utf-8"))

    def entries_by_text(self, document=None):
        document = document or self.load_map()
        entries = {}
        for record in document["chapters"]:
            for entry in record["headings"]:
                entries[entry["text"]] = entry
        return entries


class RuleLadderTests(SectionMapTestCase):
    def test_rule_ladder_and_cited_override(self):
        self.assertEqual(0, self.run_tool("--write"))
        document = self.load_map()
        self.assertEqual("section-map/1", document["schema_version"])
        self.assertEqual("fake-book", document["book"])
        entries = self.entries_by_text(document)

        title = entries["Chapter One"]
        self.assertEqual(("section", "rule:chapter-title"), (title["role"], title["classified_by"]))
        self.assertEqual((1, 1), (title["line"], title["level"]))

        callout = entries["WARNING"]
        self.assertEqual(("embedded", "rule:callout"), (callout["role"], callout["classified_by"]))

        caption = entries["Example 1-2. A caption"]
        self.assertEqual(("embedded", "rule:caption"), (caption["role"], caption["classified_by"]))

        cited = entries["CHECKLIST: Cited Things"]
        self.assertEqual(("section", "rule:cited"), (cited["role"], cited["classified_by"]))
        self.assertEqual("overrides rule:callout", cited["note"])

        ambiguous = entries["Plain Ambiguous Heading"]
        self.assertEqual(("embedded", "model"), (ambiguous["role"], ambiguous["classified_by"]))
        self.assertEqual(1, len(FakeClassifierHandler.chat_requests))
        prompt = FakeClassifierHandler.chat_requests[0]["messages"][0]["content"]
        self.assertIn("Body of the ambiguous heading.", prompt)
        self.assertIn("already classified", prompt)

    def test_numbered_book_rule(self):
        book = self.root / "books" / "numbered-book" / "chapters"
        book.mkdir(parents=True)
        lines = ["# Chapter N", ""]
        for index in range(1, 51):
            lines += [f"#### 1.{index} Numbered Section", "", "Prose.", ""]
        lines += [
            "#### Flat Unnumbered Child",
            "",
            "Prose.",
            "",
            "## Oddly Levelled Heading",
            "",
            "Prose.",
            "",
        ]
        (book / "001-n.md").write_text("\n".join(lines), encoding="utf-8")
        FakeClassifierHandler.default_role = "section"

        self.assertEqual(0, self.run_tool("--write", "--book", "numbered-book"))

        document = self.load_map(
            self.root / "doctrine" / "section-maps" / "numbered-book.yaml"
        )
        entries = {
            entry["text"]: entry
            for record in document["chapters"]
            for entry in record["headings"]
        }
        numbered = entries["1.7 Numbered Section"]
        self.assertEqual(("section", "rule:numbered-book"), (numbered["role"], numbered["classified_by"]))
        flat = entries["Flat Unnumbered Child"]
        self.assertEqual(("embedded", "rule:numbered-book"), (flat["role"], flat["classified_by"]))
        odd = entries["Oddly Levelled Heading"]
        self.assertEqual("model", odd["classified_by"])

    def test_toc_rule_promotes_listed_headings(self):
        book = self.root / "books" / "toc-book" / "chapters"
        book.mkdir(parents=True)
        (book / "001-table-of-contents.md").write_text(TOC_TEXT, encoding="utf-8")
        (book / "002-three.md").write_text(TOC_BOOK_CHAPTER, encoding="utf-8")

        self.assertEqual(0, self.run_tool("--write", "--book", "toc-book"))

        document = self.load_map(
            self.root / "doctrine" / "section-maps" / "toc-book.yaml"
        )
        entries = {
            entry["text"]: entry
            for record in document["chapters"]
            for entry in record["headings"]
        }
        self.assertEqual(("section", "rule:toc"), (entries["Deep Waters"]["role"], entries["Deep Waters"]["classified_by"]))
        self.assertEqual(("section", "rule:toc"), (entries["Rising Tide"]["role"], entries["Rising Tide"]["classified_by"]))
        self.assertEqual("model", entries["Uncharted Heading"]["classified_by"])

    def test_unparseable_model_reply_defaults_to_section(self):
        FakeClassifierHandler.raw_content = "I refuse to emit JSON."

        self.assertEqual(0, self.run_tool("--write"))

        # One retry, then the safe default.
        self.assertEqual(2, len(FakeClassifierHandler.chat_requests))
        entries = self.entries_by_text()
        ambiguous = entries["Plain Ambiguous Heading"]
        self.assertEqual(("section", "model"), (ambiguous["role"], ambiguous["classified_by"]))
        self.assertEqual("unparseable-default-section", ambiguous["note"])


class HumanPreservationTests(SectionMapTestCase):
    def test_human_entries_survive_rewrite_unchanged(self):
        self.assertEqual(0, self.run_tool("--write"))
        document = self.load_map()
        for record in document["chapters"]:
            for entry in record["headings"]:
                if entry["text"] == "Plain Ambiguous Heading":
                    entry["role"] = "section"
                    entry["classified_by"] = "human"
                    entry["note"] = "reviewed against the printed book"
        self.map_path.write_text(
            build_section_map.dump_map(document), encoding="utf-8"
        )
        FakeClassifierHandler.chat_requests = []

        self.assertEqual(0, self.run_tool("--write"))

        entries = self.entries_by_text()
        preserved = entries["Plain Ambiguous Heading"]
        self.assertEqual("section", preserved["role"])
        self.assertEqual("human", preserved["classified_by"])
        self.assertEqual("reviewed against the printed book", preserved["note"])
        self.assertEqual(0, len(FakeClassifierHandler.chat_requests))

    def test_human_entries_survive_chapter_sha_change(self):
        self.assertEqual(0, self.run_tool("--write"))
        document = self.load_map()
        for record in document["chapters"]:
            for entry in record["headings"]:
                if entry["text"] == "Second Ambiguous Heading":
                    entry["role"] = "embedded"
                    entry["classified_by"] = "human"
        self.map_path.write_text(
            build_section_map.dump_map(document), encoding="utf-8"
        )
        self.chapter.write_text(
            CHAPTER_TEXT.replace("Intro text", "Rewritten intro text"),
            encoding="utf-8",
        )
        FakeClassifierHandler.chat_requests = []
        FakeClassifierHandler.default_role = "section"

        self.assertEqual(0, self.run_tool("--write"))

        entries = self.entries_by_text()
        preserved = entries["Second Ambiguous Heading"]
        self.assertEqual(("embedded", "human"), (preserved["role"], preserved["classified_by"]))
        # Non-human entries of the changed chapter were rebuilt via the model.
        self.assertEqual(1, len(FakeClassifierHandler.chat_requests))
        rebuilt = entries["Plain Ambiguous Heading"]
        self.assertEqual(("section", "model"), (rebuilt["role"], rebuilt["classified_by"]))


class CheckTests(SectionMapTestCase):
    def test_check_passes_after_write(self):
        self.assertEqual(0, self.run_tool("--write"))
        self.assertEqual(0, self.run_tool("--check"))

    def test_check_fails_on_stale_sha(self):
        self.assertEqual(0, self.run_tool("--write"))
        self.chapter.write_text(
            CHAPTER_TEXT + "\nAppended paragraph.\n", encoding="utf-8"
        )
        self.assertEqual(1, self.run_tool("--check"))

    def test_check_fails_when_cited_heading_is_embedded(self):
        self.assertEqual(0, self.run_tool("--write"))
        document = self.load_map()
        for record in document["chapters"]:
            for entry in record["headings"]:
                if entry["text"] == "CHECKLIST: Cited Things":
                    entry["role"] = "embedded"
                    entry["classified_by"] = "human"
        self.map_path.write_text(
            build_section_map.dump_map(document), encoding="utf-8"
        )
        self.assertEqual(1, self.run_tool("--check"))

    def test_check_fails_on_uncovered_chapter_and_missing_book(self):
        self.assertEqual(0, self.run_tool("--write"))
        extra = self.chapter.parent / "002-two.md"
        extra.write_text("# Chapter Two\n\nProse.\n", encoding="utf-8")
        self.assertEqual(1, self.run_tool("--check"))
        extra.unlink()
        self.assertEqual(0, self.run_tool("--check"))

        other = self.root / "books" / "other-book" / "chapters"
        other.mkdir(parents=True)
        (other / "001-x.md").write_text("# X\n", encoding="utf-8")
        self.assertEqual(1, self.run_tool("--check"))

    def test_check_fails_on_heading_map_drift(self):
        self.assertEqual(0, self.run_tool("--write"))
        document = self.load_map()
        document["chapters"][0]["headings"].pop()
        self.map_path.write_text(
            build_section_map.dump_map(document), encoding="utf-8"
        )
        self.assertEqual(1, self.run_tool("--check"))


class DeterminismTests(SectionMapTestCase):
    def test_second_write_is_byte_identical_without_model_calls(self):
        self.assertEqual(0, self.run_tool("--write"))
        first = self.map_path.read_bytes()
        first_calls = len(FakeClassifierHandler.chat_requests)

        self.assertEqual(0, self.run_tool("--write"))

        self.assertEqual(first, self.map_path.read_bytes())
        self.assertEqual(first_calls, len(FakeClassifierHandler.chat_requests))


class StatsTests(SectionMapTestCase):
    def test_stats_reports_roles_and_provenance(self):
        self.assertEqual(0, self.run_tool("--write"))
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(0, self.run_tool("--stats"))
        output = buffer.getvalue()
        self.assertIn("fake-book: headings=6", output)
        self.assertIn("rule:cited=1", output)
        self.assertIn("model=2", output)
        self.assertIn("TOTAL: headings=6", output)


if __name__ == "__main__":
    unittest.main()
