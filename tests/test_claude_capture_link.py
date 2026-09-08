"""Synthetic bytes test field agreement; a Python producer is never a native run."""

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from caplab.claude_capture_link import claude_root_session_fields, link_claude_root
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import collect_native_outputs
from caplab.native_runtime import prepare_native_runtime
from caplab.task_capture import TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import CaptureVerificationError

POLICY = Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'
SESSION = '11111111-2222-4333-8444-555555555555'
NAME = '-work/' + SESSION + '.jsonl'


def jsonl(events):
    return ('\n'.join(json.dumps(e, ensure_ascii=False) for e in events) + '\n').encode()


def stdout_events():
    return [{'type': 'system', 'subtype': 'init', 'session_id': SESSION},
            {'type': 'assistant', 'session_id': SESSION, 'parent_tool_use_id': None,
             'message': {'content': 'synthetic café\u2028text'}},
            {'type': 'result', 'session_id': SESSION, 'subtype': 'success', 'is_error': False}]


def transcript_events():
    return [{'type': 'user', 'uuid': 'message-A', 'parentUuid': None, 'sessionId': SESSION,
             'message': {'role': 'user', 'content': 'synthetic question'}},
            {'type': 'assistant', 'uuid': 'message-B', 'parentUuid': 'message-A', 'sessionId': SESSION,
             'message': {'role': 'assistant', 'content': 'synthetic café\u2028answer'}}]


class ClaudeRootFieldsTests(unittest.TestCase):
    def fields(self, stdout=None, transcript=None):
        return claude_root_session_fields(jsonl(stdout_events() if stdout is None else stdout),
            jsonl(transcript_events() if transcript is None else transcript), session_id=SESSION)

    def test_root_fields_and_unicode_are_retained_without_a_model_claim(self):
        report = self.fields()
        self.assertEqual(report['session_id'], SESSION)
        self.assertEqual(report['stdout_root_observations'], 3)
        self.assertEqual(report['persisted_root_messages'], 2)
        self.assertNotIn('model', report)

    def test_root_stdout_conflicts_fail_even_when_init_and_result_match(self):
        events = stdout_events(); events[1]['session_id'] = 'other'
        with self.assertRaisesRegex(CaptureVerificationError, 'conflicting stdout'): self.fields(stdout=events)

    def test_initialization_is_unique_first_and_configured(self):
        events = stdout_events()
        variants = [events[1:], events + [events[0]], [events[1], events[0], events[2]],
                    [dict(events[0], session_id='other')]]
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(CaptureVerificationError): self.fields(stdout=variant)

    def test_missing_root_stdout_ids_fail(self):
        for index in range(3):
            events = stdout_events(); del events[index]['session_id']
            with self.subTest(index=index), self.assertRaises(CaptureVerificationError): self.fields(stdout=events)

    def test_valid_child_stdout_does_not_supply_or_contradict_root(self):
        events = stdout_events()
        events.insert(2, {'type': 'assistant', 'session_id': 'child', 'parent_tool_use_id': 'tool-A'})
        self.assertEqual(self.fields(stdout=events)['stdout_nonroot_observations'], 1)
        with self.assertRaises(CaptureVerificationError): self.fields(stdout=[events[2]])

    def test_invalid_stdout_child_scopes_are_not_ignored(self):
        for parent in ('', ' ', 0, False, [], {}):
            events = stdout_events(); events[1]['parent_tool_use_id'] = parent
            with self.subTest(parent=parent), self.assertRaises(CaptureVerificationError): self.fields(stdout=events)
        events = stdout_events(); events[2]['parent_tool_use_id'] = 'tool-A'
        with self.assertRaises(CaptureVerificationError): self.fields(stdout=events)

    def test_body_session_id_is_required_and_exact(self):
        for value in (None, '', ' ', 3, 'other', SESSION + ' '):
            events = transcript_events(); events[1]['sessionId'] = value
            with self.subTest(value=value), self.assertRaises(CaptureVerificationError): self.fields(transcript=events)
        events = transcript_events(); del events[1]['sessionId']
        with self.assertRaises(CaptureVerificationError): self.fields(transcript=events)

    def test_metadata_conflicts_are_not_hidden_by_matching_messages(self):
        events = transcript_events() + [{'type': 'tag', 'sessionId': 'other', 'tag': 'synthetic'}]
        with self.assertRaisesRegex(CaptureVerificationError, 'persisted root'): self.fields(transcript=events)

    def test_nonroot_persisted_scopes_cannot_supply_root_evidence(self):
        for scope in ({'isSidechain': True}, {'isMeta': True}, {'teamName': 'team-A'}):
            child = dict(transcript_events()[1], sessionId='child', **scope)
            report = self.fields(transcript=transcript_events() + [child])
            self.assertEqual(report['persisted_root_messages'], 2)
            self.assertEqual(report['persisted_nonroot_messages'], 1)
            with self.subTest(scope=scope), self.assertRaisesRegex(CaptureVerificationError, 'no root'):
                self.fields(transcript=[child])

    def test_scope_type_errors_fail_instead_of_using_truthiness(self):
        for field, values in [('isSidechain', [None, 0, 'false', []]), ('isMeta', [None, 1, '']),
                              ('teamName', [False, 0, [], '', ' '])]:
            for value in values:
                events = transcript_events(); events[1][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(CaptureVerificationError):
                    self.fields(transcript=events)

    def test_no_root_message_or_missing_uuid_fails(self):
        for events in ([{'type': 'tag', 'sessionId': SESSION}],
                       [dict(transcript_events()[0], uuid=None)], [dict(transcript_events()[0], uuid=' ')]):
            with self.subTest(events=events), self.assertRaises(CaptureVerificationError): self.fields(transcript=events)

    def test_strict_jsonl_rejects_invalid_bytes_and_partial_records_on_both_inputs(self):
        invalid = [b'', b'\xff\n', b'{}', b'\n', b'[]\n', b'{}\n', b'{"type":"user","type":"assistant"}\n',
                   b'{"type":"tag","value":NaN}\n', b'{"type":"tag"}\n\n', b'{"type":3}\n']
        for content in invalid:
            for field in ('stdout', 'transcript'):
                inputs = {'stdout': jsonl(stdout_events()), 'transcript': jsonl(transcript_events())}
                inputs[field] = content
                with self.subTest(field=field, content=content), self.assertRaises(CaptureVerificationError):
                    claude_root_session_fields(**inputs, session_id=SESSION)

    def test_nested_text_and_tool_ids_are_not_session_evidence(self):
        events = transcript_events()
        events[1]['message'] = {'sessionId': 'other', 'content': 'sessionId: forged'}
        self.assertEqual(self.fields(transcript=events)['persisted_root_messages'], 2)

    def test_parent_links_are_not_reconstructed_or_used_to_claim_completeness(self):
        events = transcript_events(); events[1]['parentUuid'] = 'unretained-parent'
        self.assertEqual(self.fields(transcript=events)['persisted_root_messages'], 2)


class ClaudeCaptureLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @staticmethod
    def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

    def build(self, *, files=None, output=None, different_task=False, codex=False, timeout=False, return_code=0):
        self.task = self.root / 'task'; self.task.mkdir()
        self.prepared = self.root / 'prepared'
        plan = build_native_capture_invocation(POLICY, 'codex-terra-max' if codex else 'claude-fable-5-max',
            context=NativeCaptureContext('/work', '/episode', b'Synthetic linkage fixture only.', None if codex else SESSION))
        prep = prepare_native_runtime(POLICY, plan, expected_invocation_sha256=plan['invocation_sha256'],
            task_root=self.task, output_dir=self.prepared)
        session_root = Path(prep['capture_paths']['session_search_root'])
        for name, content in ({NAME: jsonl(transcript_events())} if files is None else files).items():
            path = session_root / name; path.parent.mkdir(parents=True, exist_ok=True)
            if content is None: path.symlink_to('/synthetic-outside')
            else: path.write_bytes(content)
        task = self.task
        if different_task: task = self.root / 'other-task'; task.mkdir()
        self.attempt = self.root / 'attempt'
        output = jsonl(stdout_events()) if output is None else output
        code = 'import sys,time;sys.stdout.buffer.write(bytes.fromhex(sys.argv[1]));sys.stdout.flush();time.sleep(float(sys.argv[2]));sys.exit(int(sys.argv[3]))'
        capture_task_attempt([sys.executable, '-c', code, output.hex(), '2' if timeout else '0', str(return_code)],
            task_root=task, environment={'PATH': '/usr/bin:/bin'}, output_dir=self.attempt,
            limits=TaskCaptureLimits(200000, 1000, 100, 0.2 if timeout else 3))
        self.collection = self.root / 'collection'
        self.receipt = collect_native_outputs(POLICY, self.prepared,
            expected_preparation_sha256=self.digest(self.prepared / 'preparation.json'), output_dir=self.collection,
            max_receipt_bytes=100000, max_artifact_bytes=1000000, max_entries=100)
        self.attempt_anchor = self.digest(self.attempt / 'attempt.json')
        self.collection_anchor = self.digest(self.collection / 'collection.json')

    def link(self, **kwargs):
        options = dict(expected_attempt_sha256=self.attempt_anchor, expected_collection_sha256=self.collection_anchor,
                       max_receipt_bytes=200000, max_identity_bytes=200000)
        options.update(kwargs)
        return link_claude_root(POLICY, self.attempt, self.collection, **options)

    def test_retained_link_works_without_sources_and_preserves_bytes_and_claims(self):
        self.build(files={NAME: jsonl(transcript_events()), '-work/' + SESSION + '/subagents/agent-child.jsonl': b'unparsed'})
        shutil.rmtree(self.task); shutil.rmtree(self.prepared)
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        report = self.link()
        self.assertEqual(report['session_fields']['session_id'], SESSION)
        self.assertTrue(report['root_id_agrees']); self.assertTrue(report['recorded_task_root_agrees'])
        self.assertEqual(report['transcript_path'], 'session_search_root/' + NAME)
        self.assertEqual(report['other_session_files'], 1)
        for field in ('executed_invocation_bound', 'conversation_chain_verified', 'child_linkage_verified'):
            self.assertIs(report[field], False)
        for field in ('reported_tuple_agrees', 'native_capture_complete'): self.assertIsNone(report[field])
        self.assertNotIn('synthetic question', json.dumps(report))
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_matching_filename_does_not_override_conflicting_body(self):
        events = transcript_events(); events[1]['sessionId'] = 'other'
        self.build(files={NAME: jsonl(events)})
        with self.assertRaisesRegex(CaptureVerificationError, 'persisted root'): self.link()

    def test_duplicate_exact_candidates_are_ambiguous(self):
        self.build(files={NAME: jsonl(transcript_events()), 'other/' + SESSION + '.jsonl': jsonl(transcript_events())})
        with self.assertRaisesRegex(CaptureVerificationError, 'exactly one'): self.link()

    def test_missing_exact_candidate_is_not_replaced_by_substring(self):
        self.build(files={'-work/prefix-' + SESSION + '.jsonl': jsonl(transcript_events())})
        with self.assertRaisesRegex(CaptureVerificationError, 'exactly one'): self.link()

    def test_nested_child_path_cannot_supply_root_transcript(self):
        self.build(files={'-work/child/' + SESSION + '.jsonl': jsonl(transcript_events())})
        with self.assertRaisesRegex(CaptureVerificationError, 'project directory'): self.link()

    def test_matching_symlink_is_not_followed(self):
        self.build(files={NAME: None})
        with self.assertRaisesRegex(CaptureVerificationError, 'regular file'): self.link()

    def test_anchors_and_changed_payload_are_rejected(self):
        self.build()
        for field in ('expected_attempt_sha256', 'expected_collection_sha256'):
            with self.subTest(field=field), self.assertRaises(CaptureVerificationError): self.link(**{field: '0' * 64})
        entry = next(e for e in self.receipt['entries'] if e['kind'] == 'file')
        (self.collection / 'objects' / entry['object']).write_bytes(b'changed')
        with self.assertRaises(CaptureVerificationError): self.link()

    def test_payload_is_rechecked_after_initial_bundle_verification(self):
        self.build()
        from caplab.claude_capture_link import verify_task_capture
        entry = next(e for e in self.receipt['entries'] if e['kind'] == 'file')
        def verify_then_change(*args, **kwargs):
            result = verify_task_capture(*args, **kwargs)
            (self.collection / 'objects' / entry['object']).write_bytes(b'x' * entry['bytes'])
            return result
        with patch('caplab.claude_capture_link.verify_task_capture', side_effect=verify_then_change):
            with self.assertRaisesRegex(CaptureVerificationError, 'identity payload differs'): self.link()

    def test_shared_identity_budget_exact_boundary_and_invalid_limits(self):
        self.build(); amount = self.link()['identity_bytes']
        self.assertEqual(self.link(max_identity_bytes=amount)['identity_bytes'], amount)
        for limit in (amount - 1, 1, 0, True):
            with self.subTest(limit=limit), self.assertRaises(CaptureVerificationError): self.link(max_identity_bytes=limit)
        with self.assertRaises(CaptureVerificationError): self.link(max_receipt_bytes=1)

    def test_different_recorded_tasks_fail(self):
        self.build(different_task=True)
        with self.assertRaisesRegex(CaptureVerificationError, 'captured task differs'): self.link()

    def test_codex_collection_is_not_a_claude_collection(self):
        self.build(codex=True)
        with self.assertRaisesRegex(CaptureVerificationError, 'Claude collection'): self.link()

    def test_nonzero_process_does_not_become_success_by_root_agreement(self):
        self.build(return_code=3); report = self.link()
        self.assertTrue(report['root_id_agrees']); self.assertEqual(report['process_return_code'], 3)
        self.assertTrue(report['process_capture_complete']); self.assertIsNone(report['native_capture_complete'])

    def test_timeout_is_separate_from_root_field_agreement(self):
        self.build(timeout=True); report = self.link()
        self.assertTrue(report['root_id_agrees']); self.assertEqual(report['process_termination'], 'timeout')
        self.assertFalse(report['process_capture_complete'])


if __name__ == '__main__': unittest.main()
