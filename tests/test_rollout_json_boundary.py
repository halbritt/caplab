"""Native rollout identity must not depend on permissive JSON decoding."""

import hashlib
import json
import unittest

from caplab.artifact_rater import CalibrationError, read_rollout_attestation
import test_native_capture_custody as fixtures


class RolloutJsonBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.NativeCaptureCustodyTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.path = self.fixture.source

    def test_duplicate_identity_fields_and_nested_keys_are_rejected(self):
        base = fixtures.rollout()
        cases = [
            base.replace(b'"model":', b'"model":"another-model","model":'),
            base.replace(b'"effort":', b'"effort":"high","effort":'),
            base.replace(b'"id":', b'"id":"another-thread","id":'),
            base.replace(b'"cli_version":', b'"cli_version":"another-version","cli_version":'),
            base.replace(b'"type": "turn_context"', b'"type":"ignored","type":"turn_context"'),
            base.replace(b'"payload": {"model"', b'"payload":{"model":"another-model","effort":"low"},"payload": {"model"'),
            base + b'{"type":"event_msg","payload":{"type":"note","value":1,"value":1}}\n',
        ]
        for raw in cases:
            with self.subTest(raw=raw):
                self.path.write_bytes(raw)
                with self.assertRaisesRegex(CalibrationError, 'malformed rollout JSON'):
                    read_rollout_attestation(self.path, 'thread-123')
                self.assertEqual(self.path.read_bytes(), raw)

    def test_non_json_constants_are_rejected_even_outside_identity_fields(self):
        for constant in (b'NaN', b'Infinity', b'-Infinity'):
            with self.subTest(constant=constant):
                self.path.write_bytes(fixtures.rollout() + b'{"type":"event_msg","payload":{"type":"note","value":' + constant + b'}}\n')
                with self.assertRaisesRegex(CalibrationError, 'malformed rollout JSON'):
                    read_rollout_attestation(self.path, 'thread-123')

    def test_blank_or_unterminated_records_cannot_attest(self):
        for raw in (fixtures.rollout().rstrip(b'\n'), fixtures.rollout()+b'\n', b'\n'+fixtures.rollout(), fixtures.rollout()+b' \t\n'):
            with self.subTest(raw=raw):
                self.path.write_bytes(raw)
                with self.assertRaises(CalibrationError):
                    read_rollout_attestation(self.path, 'thread-123')

    def test_unicode_inside_strings_and_crlf_preserve_original_hash(self):
        for delimiter in (b'\n', b'\r\n'):
            with self.subTest(delimiter=delimiter):
                note = json.dumps({'type':'event_msg','payload':{'type':'note','text':'résumé\u2028second\u2029third'}}, ensure_ascii=False).encode()+b'\n'
                raw = (fixtures.rollout()+note).replace(b'\n', delimiter)
                self.path.write_bytes(raw)
                attestation = read_rollout_attestation(self.path, 'thread-123')
                self.assertEqual(attestation['model'], 'gpt-5.6-luna')
                self.assertEqual(attestation['effort'], 'low')
                self.assertEqual(attestation['rollout_sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(self.path.read_bytes(), raw)

    def test_ambiguous_rollout_is_retained_without_judgment_publication(self):
        raw = fixtures.rollout().replace(b'"model":', b'"model":"another-model","model":')
        self.path.write_bytes(raw)
        self.assertFalse(self.fixture.score()[1])
        slot = self.fixture.root / 'out/scores/slot-1'
        attempt = slot / 'attempt-001'
        self.assertEqual((attempt/'rollout.jsonl').read_bytes(), raw)
        self.assertFalse((slot/'accepted.json').exists())
        record = json.loads((attempt/'record.json').read_text())
        self.assertFalse(record['validated'])
        self.assertNotIn('attestation', record)


if __name__ == '__main__':
    unittest.main()
