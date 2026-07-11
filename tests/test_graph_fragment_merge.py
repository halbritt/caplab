"""Behavioral tests for merging curated graph fragments after projection."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "doctrine" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import merge_graph_fragments  # noqa: E402


class GraphFragmentCompatibilityTests(unittest.TestCase):
    def test_projected_synthesis_audit_fields_do_not_create_fragment_collision(self):
        fragment = {
            "id": "E-test",
            "from": "concept-a",
            "relation": "enables",
            "to": "concept-b",
            "claim": "A enables B.",
            "conditions": ["condition"],
            "derivation": "synthesized",
            "confidence": "contextual",
            "provenance": ["F-a", "F-b"],
        }
        canonical = {
            **fragment,
            "synthesis": {
                "rationale": "The cited premises support this relation.",
                "rivals": ["The relation is coincidental."],
                "falsifiers": ["A does not affect B under the condition."],
                "origin": "projected",
            },
        }

        self.assertTrue(
            merge_graph_fragments.fragment_matches_canonical(fragment, canonical)
        )
        self.assertFalse(
            merge_graph_fragments.fragment_matches_canonical(
                {**fragment, "claim": "Changed claim."}, canonical
            )
        )


if __name__ == "__main__":
    unittest.main()
