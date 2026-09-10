import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from codex_rollout_projection import project_rollout, verify_projection


class RolloutProjectionTest(unittest.TestCase):
    def test_only_opaque_field_is_omitted_with_exact_custody(self):
        message = b'{"type":"response_item","payload":{"type":"message","content":[{"text":"kid in ordinary prose"}]}}\n'
        opaque = 'AbC-kid_opaque-ciphertext-0123456789'
        reasoning = {'type': 'response_item', 'payload': {'type': 'reasoning',
                     'summary': [{'text': 'A readable summary'}], 'encrypted_content': opaque}}
        original = message + (json.dumps(reasoning) + '\n').encode()
        projected, receipt = project_rollout(original)
        self.assertTrue(projected.startswith(message))
        result = json.loads(projected.splitlines()[1])
        expected = json.loads(json.dumps(reasoning))
        del expected['payload']['encrypted_content']
        self.assertEqual(result, expected)
        self.assertEqual(receipt['original_sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(receipt['omissions'][0]['sha256'], hashlib.sha256(opaque.encode()).hexdigest())
        self.assertNotIn(opaque.encode(), projected)
        verify_projection(projected, receipt)
        with self.assertRaises(ValueError):
            verify_projection(projected + b' ', receipt)
        receipt['omissions'][0]['row'] = 1
        with self.assertRaises(ValueError):
            verify_projection(projected, receipt)

    def test_tool_and_final_values_are_never_interpreted_as_opaque_reasoning(self):
        rows = [{'type': 'response_item', 'payload': {'type': 'function_call_output',
                 'output': '{"encrypted_content":"a credential"}'}},
                {'type': 'response_item', 'payload': {'type': 'message', 'encrypted_content': 'must remain'}}]
        raw = ('\n'.join(json.dumps(row) for row in rows) + '\n').encode()
        self.assertEqual(project_rollout(raw)[0], raw)
        self.assertEqual(project_rollout(raw)[1]['omissions'], [])

    def test_unexpected_shapes_and_duplicate_keys_fail(self):
        for raw in (b'{"type":"response_item","payload":{"type":"reasoning","encrypted_content":{}}}\n',
                    b'{"type":"response_item","type":"other"}\n', b'{truncated\n',
                    b'{"value":NaN}\n'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                project_rollout(raw)

    def test_missing_or_null_opaque_field_preserves_original_bytes(self):
        for payload in ({'type': 'reasoning'}, {'type': 'reasoning', 'encrypted_content': None}):
            raw = (json.dumps({'type': 'response_item', 'payload': payload}, indent=None) + '\n').encode()
            self.assertEqual(project_rollout(raw)[0], raw)


if __name__ == '__main__':
    unittest.main()
