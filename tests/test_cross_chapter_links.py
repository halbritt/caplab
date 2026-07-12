from pathlib import Path
import runpy
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONVERTER_MODULE = runpy.run_path(str(REPOSITORY_ROOT / "scripts" / "convert-books"))


class CrossChapterLinkTests(unittest.TestCase):
    def test_bare_textual_html_hrefs_become_local_markdown_links(self) -> None:
        current_filename = "020-chapter-13-design-for-deployment.md"
        markdown = (
            'See <a href="Processes on Machines">Processes on Machines</a>.\n\n'
            'Return to <a href="Chapter 8.">Chapter 8.</a>.\n\n'
            'Compare <a href="Integration Points">Integration Points</a>.\n\n'
            "In "
            '<a href="Why People Believe Weird Things">'
            "Why People Believe Weird Things</a>.\n"
        )
        anchor_owners = {
            "processes-on-machines": "010-chapter-8-foundations.md",
            "chapter-8-foundations": "010-chapter-8-foundations.md",
            "chapter-4-integration-points": "006-chapter-4-stability-antipatterns.md",
        }

        rewritten, degraded_links = CONVERTER_MODULE[
            "rewrite_cross_chapter_links"
        ](markdown, current_filename, anchor_owners)

        self.assertIn(
            "[Processes on Machines](010-chapter-8-foundations.md#processes-on-machines)",
            rewritten,
        )
        self.assertIn(
            "[Chapter 8.](010-chapter-8-foundations.md#chapter-8-foundations)",
            rewritten,
        )
        self.assertIn(
            "[Integration Points](006-chapter-4-stability-antipatterns.md#chapter-4-integration-points)",
            rewritten,
        )
        self.assertIn("In Why People Believe Weird Things.", rewritten)
        self.assertNotIn("href=", rewritten)

        unmatched = [
            link
            for link in degraded_links
            if link["original_target"] == "Why People Believe Weird Things"
        ]
        self.assertEqual(len(unmatched), 1)
        self.assertEqual(unmatched[0]["source_file"], current_filename)
        self.assertEqual(unmatched[0]["replacement_anchor"], "")
        self.assertIn("preserved", unmatched[0]["reason"])


if __name__ == "__main__":
    unittest.main()
