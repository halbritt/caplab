"""Prospective argv contracts and a local observer through bounded task capture."""

import dataclasses
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.subject_identity import NativeAgentSystemContractError, load_native_agent_system_policy, validate_native_agent_systems
from caplab.task_capture import TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import verify_task_capture

POLICY = Path(__file__).parents[1] / "docs/product/contracts/native-agent-systems.json"
SESSION = "d82c1f85-f336-41d9-bd85-13953846867b"


class NativeCaptureInvocationTests(unittest.TestCase):
    def context(self, **kwargs):
        return NativeCaptureContext('/work', '/episode', '--model evil\nRead résumé; $(touch BAD) `echo bad`'.encode(), **kwargs)

    def plan(self, harness='codex', context=None):
        return build_native_capture_invocation(POLICY, 'codex-terra-max' if harness=='codex' else 'claude-fable-5-max',
            context=context or self.context(**({} if harness=='codex' else {'session_id':SESSION})))

    def test_profiles_preserve_native_tuple_and_have_distinct_identifiers(self):
        ids = []
        for harness in ('codex','claude'):
            with self.subTest(harness=harness):
                plan = self.plan(harness)
                validate_native_agent_systems(load_native_agent_system_policy(POLICY), {'subject':plan['base_subject']})
                self.assertFalse(plan['execution_authorized'])
                self.assertFalse(plan['binding_complete'])
                self.assertTrue(plan['profile']['external_containment_required'])
                self.assertEqual(plan['command'][-2:], ['--',self.context().prompt.decode()])
                self.assertEqual(plan['prompt_sha256'],hashlib.sha256(self.context().prompt).hexdigest())
                self.assertNotIn('--ephemeral',plan['command'])
                self.assertNotIn('--no-session-persistence',plan['command'])
                self.assertEqual(plan['version_command'],[plan['command'][0],'--version'])
                ids.append(plan['profile_sha256'])
        self.assertNotEqual(*ids)
        codex=self.plan();claude=self.plan('claude')
        self.assertIn('model_reasoning_effort=max',codex['command'])
        self.assertIn('hide_agent_reasoning=false',codex['command'])
        self.assertIn('model_reasoning_summary="detailed"',codex['command'])
        self.assertEqual(codex['capture_locations']['final_message'],'/episode/final-message.txt')
        self.assertEqual(claude['command'][claude['command'].index('--session-id')+1],SESSION)
        for option in ('--include-partial-messages','--include-hook-events','--debug-file'):
            self.assertIn(option,claude['command'])

    def test_old_validator_still_rejects_new_suffixes(self):
        policy=load_native_agent_system_policy(POLICY)
        for harness in ('codex','claude'):
            plan=self.plan(harness)
            subject=dict(plan['base_subject'], command=plan['command'][:-2])
            with self.assertRaisesRegex(NativeAgentSystemContractError,'command_identity_override'):
                validate_native_agent_systems(policy,{'subject':subject})

    def test_plan_hash_covers_context_and_returned_profiles_do_not_share_state(self):
        initial=self.plan()
        for context in (self.context(),dataclasses.replace(self.context(),prompt=b'different'),
                        dataclasses.replace(self.context(),runtime_root='/new-runtime')):
            plan=self.plan(context=context)
            canonical=dict(plan);claimed=canonical.pop('invocation_sha256')
            self.assertEqual(claimed,hashlib.sha256(json.dumps(canonical,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode()).hexdigest())
            if context!=self.context():self.assertNotEqual(plan['invocation_sha256'],initial['invocation_sha256'])
            self.assertEqual(plan['profile_sha256'],initial['profile_sha256'])
        initial['profile']['arguments'].append('altered')
        initial['environment']['HOME']='altered'
        self.assertNotEqual(initial,self.plan())
        self.assertNotIn('altered',self.plan()['profile']['arguments'])

    def test_invalid_paths_prompts_sessions_and_policy_fail_before_execution(self):
        invalid=[dataclasses.replace(self.context(),**{key:value})
                 for key in ('task_root','runtime_root') for value in ('relative','/','//work','/a/../b','/a/./b','/a/','/a\0b')]
        invalid += [dataclasses.replace(self.context(),runtime_root=path) for path in ('/work','/work/nested')]
        invalid += [dataclasses.replace(self.context(),task_root='/episode/task')]
        invalid += [dataclasses.replace(self.context(),prompt=p) for p in (b'',b'\xff',b'\0','text')]
        invalid += [self.context(session_id=SESSION)]
        for context in invalid:
            with self.subTest(context=context),self.assertRaises(NativeAgentSystemContractError):self.plan(context=context)
        for session in (None,'bad',SESSION.upper(),1):
            with self.subTest(session=session),self.assertRaises(NativeAgentSystemContractError):
                self.plan('claude',self.context(session_id=session))
        with tempfile.TemporaryDirectory() as directory:
            policy=Path(directory)/'policy.json';policy.write_bytes(POLICY.read_bytes()+b' ')
            with self.assertRaisesRegex(NativeAgentSystemContractError,'policy_digest_mismatch'):
                build_native_capture_invocation(policy,'codex-terra-max',context=self.context())
        with self.assertRaisesRegex(NativeAgentSystemContractError,'unknown_capture_native_tuple'):
            build_native_capture_invocation(POLICY,'proxy',context=self.context())

    def test_environment_is_explicit_and_builder_does_not_touch_runtime_paths(self):
        with patch.dict('os.environ',{'OPENROUTER_API_KEY':'synthetic-ambient','CODEX_HOME':'/wrong'}):
            for harness in ('codex','claude'):
                plan=self.plan(harness)
                self.assertEqual(set(plan['environment']),{'HOME','PATH','LANG','CODEX_HOME' if harness=='codex' else 'CLAUDE_CONFIG_DIR'})
                self.assertNotIn('synthetic-ambient',json.dumps(plan))
                self.assertEqual(plan['environment']['HOME'],'/episode/home')
        with patch.object(Path,'mkdir',side_effect=AssertionError('no filesystem preparation')):
            self.plan()

    def test_argument_observer_connects_plan_to_capture_and_inspection_without_native_execution(self):
        # The Python observer receives the planned native argv as data. It is not a harness substitute.
        plan=self.plan()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);task=root/'task';task.mkdir();out=root/'capture'
            code='import json,sys; print(json.dumps(sys.argv[1:]))'
            receipt=capture_task_attempt([sys.executable,'-c',code,*plan['command']],task_root=task,
                environment={'LANG':'C.UTF-8'},output_dir=out,limits=TaskCaptureLimits(10000,1000,10,3))
            observed=json.loads((out/'process/native.stdout').read_bytes())
            self.assertEqual(observed,plan['command'])
            self.assertEqual(observed[-1].encode(),self.context().prompt)
            digest=hashlib.sha256((out/'attempt.json').read_bytes()).hexdigest()
            report=verify_task_capture(out,expected_attempt_sha256=digest,max_receipt_bytes=100000)
            self.assertTrue(report['integrity_verified'])
            self.assertTrue(receipt['capture_complete'])
            self.assertEqual(report['changes'],[])
            self.assertFalse((task/'BAD').exists())


if __name__=='__main__':unittest.main()
