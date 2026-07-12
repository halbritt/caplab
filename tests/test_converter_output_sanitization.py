from pathlib import Path
import runpy
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONVERTER_MODULE = runpy.run_path(str(REPOSITORY_ROOT / "scripts" / "convert-books"))


class ConverterOutputSanitizationTests(unittest.TestCase):
    def test_terminal_controls_are_removed_only_from_markdown_presentation(self) -> None:
        warning = (
            "WARN: could not unload ollama: "
            "\x1b[?25l\x1b[?2026h\x1b[1G\x1b[K\x1b[?25h\x07"
        )

        rendered = CONVERTER_MODULE["markdown_safe_diagnostic"](warning)

        self.assertEqual("WARN: could not unload ollama:", rendered)
        self.assertNotRegex(rendered, r"[\x00-\x1f\x7f]")


if __name__ == "__main__":
    unittest.main()
