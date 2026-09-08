"""Final-file agreement over new synthetic bundles, with native owners reused."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from caplab.codex_capture_link import link_codex_final_message
from caplab.native_collection import collect_native_outputs
from caplab.task_capture_verify import CaptureVerificationError
import test_codex_capture_link as fixtures
from test_codex_capture_link import POLICY, jsonl


def events(text='café\u2028answer\n'):
    return [{'type': 'thread.started', 'thread_id': 'root-A'}, {'type': 'turn.started'},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'earlier', 'text': 'earlier'}},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'final', 'text': text}},
            {'type': 'item.completed', 'item': {'type': 'command_execution', 'text': 'tool output'}},
            {'type': 'turn.completed'}]


class CodexFinalMessageLinkTests(unittest.TestCase):
    digest = staticmethod(fixtures.CodexCaptureLinkTests.digest)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def build(self, *, final=b'caf\xc3\xa9\xe2\x80\xa8answer\n', stdout=None, **kwargs):
        fixtures.CodexCaptureLinkTests.build(self, stdout=jsonl(events()) if stdout is None else stdout, **kwargs)
        if final is not None:
            (self.prepared / 'runtime/final-message.txt').write_bytes(final)
        self.collection = self.root / 'collection-final'
        self.collection_receipt = collect_native_outputs(POLICY, self.prepared,
            expected_preparation_sha256=self.digest(self.prepared / 'preparation.json'), output_dir=self.collection,
            max_receipt_bytes=100000, max_artifact_bytes=1000000, max_entries=100)
        self.collection_anchor = self.digest(self.collection / 'collection.json')

    def link(self, **kwargs):
        options = dict(expected_attempt_sha256=self.attempt_anchor, expected_collection_sha256=self.collection_anchor,
                       max_receipt_bytes=200000, max_identity_bytes=200000)
        options.update(kwargs)
        return link_codex_final_message(POLICY, self.attempt, self.collection, **options)

    def test_exact_nonascii_message_is_linked_after_sources_removed(self):
        self.build(); shutil.rmtree(self.prepared); shutil.rmtree(self.task)
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        report = self.link()
        self.assertTrue(report['final_message_agrees'])
        self.assertEqual(report['message_item_id'], 'final'); self.assertEqual(report['message_event_index'], 3)
        self.assertEqual(report['final_message_bytes'], len('café\u2028answer\n'.encode()))
        self.assertIsNone(report['root_link']['native_capture_complete'])
        self.assertIs(report['root_link']['executed_invocation_bound'], False)
        self.assertNotIn('café', json.dumps(report, ensure_ascii=False))
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_matching_earlier_message_cannot_replace_final_message(self):
        self.build(final=b'earlier')
        with self.assertRaisesRegex(CaptureVerificationError, 'bytes differ'): self.link()

    def test_final_file_is_not_trimmed_or_newline_repaired(self):
        self.build(final=b'answer\n', stdout=jsonl(events('answer')))
        with self.assertRaisesRegex(CaptureVerificationError, 'bytes differ'): self.link()

    def test_empty_explicit_agent_message_can_match_empty_file(self):
        self.build(final=b'', stdout=jsonl(events('')))
        self.assertEqual(self.link()['final_message_bytes'], 0)

    def test_empty_file_without_agent_message_is_not_evidence(self):
        self.build(final=b'', stdout=jsonl([events()[0], events()[1], events()[-1]]))
        with self.assertRaisesRegex(CaptureVerificationError, 'completed agent message'): self.link()

    def test_missing_file_prevents_final_comparison_but_root_link_still_works(self):
        self.build(final=None)
        from caplab.codex_capture_link import link_codex_root
        root = link_codex_root(POLICY, self.attempt, self.collection,
            expected_attempt_sha256=self.attempt_anchor, expected_collection_sha256=self.collection_anchor,
            max_receipt_bytes=200000, max_identity_bytes=200000)
        self.assertTrue(root['root_id_agrees'])
        with self.assertRaisesRegex(CaptureVerificationError, 'retained regular file'): self.link()

    def test_unfinished_native_turn_cannot_supply_final_message(self):
        self.build(stdout=jsonl(events()[:-1]))
        with self.assertRaisesRegex(CaptureVerificationError, 'completed agent message'): self.link()

    def test_failure_event_is_not_erased_by_matching_file(self):
        stream = events(); stream.insert(-1, {'type': 'turn.failed'})
        self.build(stdout=jsonl(stream))
        with self.assertRaisesRegex(CaptureVerificationError, 'completed agent message'): self.link()

    def test_total_identity_budget_covers_stdout_rollout_and_file(self):
        self.build(); amount = self.link()['identity_bytes']
        self.assertEqual(self.link(max_identity_bytes=amount)['identity_bytes'], amount)
        with self.assertRaises(CaptureVerificationError): self.link(max_identity_bytes=amount - 1)
        with self.assertRaises(CaptureVerificationError): self.link(max_receipt_bytes=1)

    def test_final_payload_is_rechecked_after_root_verification(self):
        self.build()
        from caplab.codex_capture_link import link_codex_root
        entry = next(e for e in self.collection_receipt['entries'] if e['path'] == 'final_message')
        def link_then_change(*args, **kwargs):
            result = link_codex_root(*args, **kwargs)
            (self.collection / 'objects' / entry['object']).write_bytes(b'x' * entry['bytes'])
            return result
        with patch('caplab.codex_capture_link.link_codex_root', side_effect=link_then_change):
            with self.assertRaisesRegex(CaptureVerificationError, 'identity payload differs'): self.link()

    def test_nonzero_process_exit_remains_visible(self):
        self.build(return_code=3); report = self.link()
        self.assertTrue(report['final_message_agrees']); self.assertEqual(report['root_link']['process_return_code'], 3)

    def test_timeout_remains_visible_even_with_completed_native_events(self):
        self.build(timeout=True); report = self.link()
        self.assertTrue(report['final_message_agrees']); self.assertFalse(report['root_link']['process_capture_complete'])
        self.assertEqual(report['root_link']['process_termination'], 'timeout')


if __name__ == '__main__': unittest.main()
