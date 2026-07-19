import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "doctrine" / "tools"))

import entailment_eval  # noqa: E402

CHAPTER = """# Chapter 1: Widgets

Intro paragraph.

## Assembling Widgets

Assembly starts here.

## WARNING

Do not overtighten.

## Sub-step detail

Flattened child content.

## Painting Widgets

Painting starts here.
"""


def roles_for(
    chapter_text: str, embedded_lines: set[int], depths: dict[int, int] | None = None
) -> dict[int, tuple[str, int]]:
    roles: dict[int, tuple[str, int]] = {}
    for number, line in enumerate(chapter_text.splitlines(), start=1):
        if line.startswith("#"):
            role = "embedded" if number in embedded_lines else "section"
            level = len(line) - len(line.lstrip("#"))
            roles[number] = (role, (depths or {}).get(number, level))
    return roles


class MapAwareExtractionTests(unittest.TestCase):
    def test_embedded_headings_do_not_terminate_section(self):
        # WARNING (line 9) and the flattened child (line 13) are embedded.
        roles = roles_for(CHAPTER, {9, 13})
        section = entailment_eval.extract_section(
            CHAPTER, "Assembling Widgets", roles
        )
        self.assertIn("Assembly starts here.", section)
        self.assertIn("Do not overtighten.", section)
        self.assertIn("Flattened child content.", section)
        self.assertNotIn("Painting starts here.", section)

    def test_without_roles_behavior_is_unchanged(self):
        section = entailment_eval.extract_section(CHAPTER, "Assembling Widgets")
        self.assertEqual("Assembly starts here.", section)

    def test_unmapped_heading_conservatively_terminates(self):
        roles = roles_for(CHAPTER, {9, 13})
        del roles[17]  # "Painting Widgets" missing from map
        section = entailment_eval.extract_section(
            CHAPTER, "Assembling Widgets", roles
        )
        self.assertNotIn("Painting starts here.", section)

    def test_nested_subsection_depth_does_not_terminate_parent(self):
        # "Painting Widgets" is a genuine section but a nested child of
        # "Assembling Widgets" (flattened to the same markdown level).
        roles = roles_for(CHAPTER, {9, 13}, depths={17: 3})
        section = entailment_eval.extract_section(
            CHAPTER, "Assembling Widgets", roles
        )
        self.assertIn("Painting starts here.", section)
        # Citing the nested child directly still yields its own section.
        child = entailment_eval.extract_section(CHAPTER, "Painting Widgets", roles)
        self.assertEqual("Painting starts here.", child)

    def test_stale_map_falls_back_to_level_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chapter_rel = "books/mini/chapters/001-chapter-1-widgets.md"
            chapter_path = root / chapter_rel
            chapter_path.parent.mkdir(parents=True)
            chapter_path.write_text(CHAPTER, encoding="utf-8")
            map_dir = root / "doctrine" / "section-maps"
            map_dir.mkdir(parents=True)
            map_dir.joinpath("mini.yaml").write_text(
                "schema_version: section-map/1\n"
                "book: mini\n"
                "chapters:\n"
                f"  - path: {chapter_rel}\n"
                "    chapter_sha256: " + "0" * 64 + "\n"
                "    headings:\n"
                "      - {line: 9, level: 2, text: WARNING, role: embedded,"
                " classified_by: 'rule:callout'}\n",
                encoding="utf-8",
            )
            resolution = entailment_eval.resolve_locator(
                root, f"{chapter_rel} :: Assembling Widgets"
            )
            self.assertIsNone(resolution.error)
            # stale sha -> plain level-based extraction
            self.assertEqual("Assembly starts here.", resolution.section_text)

    def test_current_map_bounds_resolution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chapter_rel = "books/mini/chapters/001-chapter-1-widgets.md"
            chapter_path = root / chapter_rel
            chapter_path.parent.mkdir(parents=True)
            chapter_path.write_text(CHAPTER, encoding="utf-8")
            sha = hashlib.sha256(CHAPTER.encode("utf-8")).hexdigest()
            map_dir = root / "doctrine" / "section-maps"
            map_dir.mkdir(parents=True)
            headings = []
            for number, line in enumerate(CHAPTER.splitlines(), start=1):
                if not line.startswith("#"):
                    continue
                role = "embedded" if number in (9, 13) else "section"
                headings.append(
                    f"      - {{line: {number}, level: 2, text: h{number},"
                    f" role: {role}, classified_by: 'rule:test'}}"
                )
            map_dir.joinpath("mini.yaml").write_text(
                "schema_version: section-map/1\nbook: mini\nchapters:\n"
                f"  - path: {chapter_rel}\n"
                f"    chapter_sha256: {sha}\n"
                "    headings:\n" + "\n".join(headings) + "\n",
                encoding="utf-8",
            )
            resolution = entailment_eval.resolve_locator(
                root, f"{chapter_rel} :: Assembling Widgets"
            )
            self.assertIsNone(resolution.error)
            self.assertIn("Do not overtighten.", resolution.section_text)
            self.assertIn("Flattened child content.", resolution.section_text)
            self.assertNotIn("Painting starts here.", resolution.section_text)


class QuoteNormalizationTests(unittest.TestCase):
    def check(self, quote: str, section: str) -> str:
        outcome = {"verdict": "supported", "evidence_quote": quote}
        return entailment_eval.verify_evidence_quote(outcome, section)["verdict"]

    def test_pdf_hyphenation_is_bridged(self):
        self.assertEqual(
            "supported",
            self.check("distributed architecture", "dis‐ tributed architecture"),
        )

    def test_markdown_emphasis_and_spans_are_ignored(self):
        section = 'Use <span id="page-1"></span>*Sprout Method* here.'
        self.assertEqual("supported", self.check("Use Sprout Method here.", section))

    def test_curly_quotes_match_straight(self):
        self.assertEqual(
            "supported", self.check('the "entity trap"', "the “entity trap”")
        )

    def test_ellipsis_fragments_each_checked(self):
        section = "First idea sentence. Middle noise. Second idea sentence."
        self.assertEqual(
            "supported",
            self.check("First idea sentence... Second idea sentence.", section),
        )

    def test_true_paraphrase_still_flagged(self):
        self.assertEqual(
            "quote_not_found",
            self.check("a completely invented quotation", "unrelated section text"),
        )


if __name__ == "__main__":
    unittest.main()
