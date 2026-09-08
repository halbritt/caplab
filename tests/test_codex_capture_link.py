"""New synthetic native-format bytes exercise linkage, never native execution."""

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from caplab.codex_capture_link import link_codex_root
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import collect_native_outputs
from caplab.native_runtime import prepare_native_runtime
from caplab.task_capture import TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import CaptureVerificationError

POLICY=Path(__file__).resolve().parents[1]/'docs/product/contracts/native-agent-systems.json'
NAME='rollout-2026-09-08T12-00-00-root-A.jsonl'


def jsonl(events):
    return ('\n'.join(json.dumps(event,ensure_ascii=False) for event in events)+'\n').encode()


def rollout(thread='root-A',model='gpt-5.6-terra',effort='max'):
    return jsonl([{'type':'session_meta','payload':{'id':thread,'cli_version':'synthetic-cli-1'}},
                  {'type':'turn_context','payload':{'model':model,'effort':effort}},
                  {'type':'event_msg','payload':{'type':'agent_message','message':'synthetic résumé\u2028only'}}])


class CodexCaptureLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def build(self, *, files=None, stdout=None, return_code=0, timeout=False, different_task=False, claude=False):
        self.task=self.root/'task';self.task.mkdir()
        self.prepared=self.root/'prepared'
        plan=build_native_capture_invocation(POLICY,'claude-fable-5-max' if claude else 'codex-terra-max',
            context=NativeCaptureContext('/work','/episode',b'Synthetic linkage fixture only.',
                '11111111-2222-4333-8444-555555555555' if claude else None))
        prep=prepare_native_runtime(POLICY,plan,expected_invocation_sha256=plan['invocation_sha256'],
                                     task_root=self.task,output_dir=self.prepared)
        session_root=Path(prep['capture_paths']['session_search_root'])
        for name,content in ({NAME:rollout()} if files is None else files).items():
            target=session_root/name;target.parent.mkdir(parents=True,exist_ok=True)
            if content is None:target.symlink_to('/synthetic-outside')
            else:target.write_bytes(content)
        stdout=jsonl([{'type':'thread.started','thread_id':'root-A'},{'type':'turn.started'}]) if stdout is None else stdout
        task=self.task
        if different_task:task=self.root/'other-task';task.mkdir()
        self.attempt=self.root/'attempt'
        code='import sys,time;sys.stdout.buffer.write(bytes.fromhex(sys.argv[1]));sys.stdout.flush();time.sleep(float(sys.argv[2]));sys.exit(int(sys.argv[3]))'
        capture_task_attempt([sys.executable,'-c',code,stdout.hex(),'2' if timeout else '0',str(return_code)],
            task_root=task,environment={'PATH':'/usr/bin:/bin'},output_dir=self.attempt,
            limits=TaskCaptureLimits(200000,1000,100,0.2 if timeout else 3))
        self.collection=self.root/'collection'
        self.collection_receipt=collect_native_outputs(POLICY,self.prepared,
            expected_preparation_sha256=self.digest(self.prepared/'preparation.json'),output_dir=self.collection,
            max_receipt_bytes=100000,max_artifact_bytes=1000000,max_entries=100)
        self.attempt_anchor=self.digest(self.attempt/'attempt.json')
        self.collection_anchor=self.digest(self.collection/'collection.json')

    @staticmethod
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

    def link(self, **kwargs):
        options=dict(expected_attempt_sha256=self.attempt_anchor,expected_collection_sha256=self.collection_anchor,
                     max_receipt_bytes=200000,max_identity_bytes=200000)
        options.update(kwargs)
        return link_codex_root(POLICY,self.attempt,self.collection,**options)

    def test_real_capture_to_collection_link_is_read_only_and_bounded_in_claim(self):
        self.build(files={NAME:rollout(),'nested/rollout-2026-09-08T12-00-00-child-B.jsonl':b'unparsed synthetic child bytes'})
        shutil.rmtree(self.task);shutil.rmtree(self.prepared)
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        report=self.link()
        self.assertTrue(report['root_id_agrees']);self.assertTrue(report['reported_tuple_agrees'])
        self.assertEqual(report['rollout']['thread_id'],'root-A')
        self.assertEqual(report['rollout']['cli_version'],'synthetic-cli-1')
        self.assertEqual(report['rollout']['model'],'gpt-5.6-terra')
        self.assertEqual(report['rollout']['effort'],'max')
        self.assertEqual(report['rollout']['rollout_path'],'session_search_root/'+NAME)
        self.assertEqual(report['other_session_files'],1)
        self.assertIs(report['executed_invocation_bound'],False)
        self.assertIs(report['child_linkage_verified'],False)
        self.assertIsNone(report['native_capture_complete'])
        self.assertNotIn('Synthetic linkage fixture',json.dumps(report))
        self.assertEqual(before,{str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_filename_does_not_override_body_thread(self):
        self.build(files={NAME:rollout(thread='another-root')})
        with self.assertRaisesRegex(CaptureVerificationError,'tuple attestation'):self.link()

    def test_reported_model_must_match_plan(self):
        self.build(files={NAME:rollout(model='other')})
        with self.assertRaisesRegex(CaptureVerificationError,'configured invocation'):self.link()

    def test_duplicate_exact_candidates_are_rejected(self):
        self.build(files={NAME:rollout(),'nested/'+NAME:rollout()})
        with self.assertRaisesRegex(CaptureVerificationError,'exactly one'):self.link()

    def test_substring_filename_and_matching_symlink_do_not_link(self):
        self.build(files={'rollout-2026-09-08T12-00-00-prefix-root-A.jsonl':rollout(),NAME:None})
        with self.assertRaisesRegex(CaptureVerificationError,'regular file'):self.link()

    def test_missing_turn_context_is_rejected(self):
        self.build(files={NAME:jsonl([{'type':'session_meta','payload':{'id':'root-A','cli_version':'synthetic'}}])})
        with self.assertRaisesRegex(CaptureVerificationError,'tuple attestation'):self.link()

    def test_reported_effort_must_match_plan(self):
        self.build(files={NAME:rollout(effort='low')})
        with self.assertRaisesRegex(CaptureVerificationError,'configured invocation'):self.link()

    def test_missing_exact_filename_is_not_replaced_by_substring(self):
        self.build(files={'rollout-2026-09-08T12-00-00-prefix-root-A.jsonl':rollout()})
        with self.assertRaisesRegex(CaptureVerificationError,'exactly one'):self.link()

    def test_partial_rollout_is_not_attested(self):
        self.build(files={NAME:rollout()[:-1]})
        with self.assertRaisesRegex(CaptureVerificationError,'tuple attestation'):self.link()

    def test_payload_changed_after_bundle_verification_is_rechecked(self):
        self.build()
        from caplab.codex_capture_link import verify_task_capture
        entry=next(e for e in self.collection_receipt['entries'] if e['kind']=='file')
        def verify_then_change(*args,**kwargs):
            result=verify_task_capture(*args,**kwargs)
            (self.collection/'objects'/entry['object']).write_bytes(b'x'*entry['bytes'])
            return result
        with patch('caplab.codex_capture_link.verify_task_capture',side_effect=verify_then_change):
            with self.assertRaisesRegex(CaptureVerificationError,'identity payload differs'):self.link()

    def test_ambiguous_stdout_ids_are_not_used(self):
        self.build(stdout=jsonl([{'type':'thread.started','thread_id':'root-A'},{'type':'thread.started','thread_id':'root-A'}]))
        with self.assertRaisesRegex(CaptureVerificationError,'unambiguous'):self.link()

    def test_bad_anchors_and_payload_mutation_are_rejected(self):
        self.build()
        for field in ('expected_attempt_sha256','expected_collection_sha256'):
            with self.subTest(field=field),self.assertRaises(CaptureVerificationError):self.link(**{field:'0'*64})
        entry=next(e for e in self.collection_receipt['entries'] if e['kind']=='file')
        (self.collection/'objects'/entry['object']).write_bytes(b'changed')
        with self.assertRaises(CaptureVerificationError):self.link()

    def test_identity_allowance_covers_stdout_and_rollout_together(self):
        self.build()
        report=self.link();amount=report['identity_bytes']
        self.assertEqual(self.link(max_identity_bytes=amount)['identity_bytes'],amount)
        for limit in (amount-1,1,0,True):
            with self.subTest(limit=limit),self.assertRaises(CaptureVerificationError):self.link(max_identity_bytes=limit)
        with self.assertRaises(CaptureVerificationError):self.link(max_receipt_bytes=1)

    def test_different_prepared_and_captured_tasks_are_rejected(self):
        self.build(different_task=True)
        with self.assertRaisesRegex(CaptureVerificationError,'captured task differs'):self.link()

    def test_claude_collection_cannot_be_linked_as_codex(self):
        self.build(claude=True)
        with self.assertRaisesRegex(CaptureVerificationError,'Codex collection'):self.link()

    def test_nonzero_exit_remains_separate_from_root_agreement(self):
        self.build(return_code=3)
        report=self.link();self.assertTrue(report['root_id_agrees'])
        self.assertEqual(report['process_return_code'],3)
        self.assertTrue(report['process_capture_complete'])
        self.assertIsNone(report['native_capture_complete'])

    def test_timeout_remains_incomplete_even_with_root_agreement(self):
        self.build(timeout=True)
        report=self.link();self.assertTrue(report['root_id_agrees'])
        self.assertEqual(report['process_termination'],'timeout')
        self.assertFalse(report['process_capture_complete'])


if __name__=='__main__':unittest.main()
