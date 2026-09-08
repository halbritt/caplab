"""Serialization compatibility of installed YAML declaration shapes."""
import unittest

import yaml

from caplab.advisory.run_spec import declaration_digest


class DeclarationDigestTest(unittest.TestCase):
    def test_yaml_dates_are_hashable_without_collapsing_them_into_strings(self):
        typed = yaml.safe_load("id: fixture\nas_of: 2026-09-08\nadapter: {command: [fixture]}\n")
        reordered = {key: typed[key] for key in reversed(typed)}
        text = {**typed, "as_of": "2026-09-08"}
        self.assertEqual(declaration_digest(typed), declaration_digest(reordered))
        self.assertNotEqual(declaration_digest(typed), declaration_digest(text))
        self.assertNotEqual(declaration_digest(typed), declaration_digest({
            **typed, "adapter": {"command": ["different-fixture"]}}))
