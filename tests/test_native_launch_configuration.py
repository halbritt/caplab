"""Effective launch identity preserves its canonical base and explicit differences."""
from copy import deepcopy
from dataclasses import replace
import hashlib
from pathlib import Path
import unittest
import tempfile

from caplab.native_capture_invocation import NativeCaptureContext, _digest, build_native_capture_invocation
from caplab.native_launch_configuration import (NativeLaunchContext, NativeLaunchTraceEvidence,
    build_native_launch_configuration, inspect_native_launch_trace)
from test_exec_trace import string, array

POLICY=Path(__file__).resolve().parents[1]/'docs/product/contracts/native-agent-systems.json'

class NativeLaunchConfigurationTests(unittest.TestCase):
    def plan(self, harness='codex-terra-max'):
        return build_native_capture_invocation(POLICY,harness,context=NativeCaptureContext('/work','/episode',
            'Fixed café diagnostic.\n'.encode(),None if harness=='codex-terra-max' else '11111111-2222-4333-8444-555555555555'))

    def build(self, plan, profile='canonical-native/v1', port=None):
        return build_native_launch_configuration(POLICY,plan,expected_invocation_sha256=plan['invocation_sha256'],
            context=NativeLaunchContext(profile,port))

    def test_canonical_launch_preserves_exact_command_environment_and_cwd(self):
        for harness in ('codex-terra-max','claude-fable-5-max'):
            with self.subTest(harness=harness):
                plan=self.plan(harness);before=deepcopy(plan)
                launch=self.build(plan)
                for field in ('command','environment','cwd'):self.assertEqual(launch[field],plan[field])
                self.assertEqual(launch['invocation_sha256'],plan['invocation_sha256'])
                self.assertTrue(launch['canonical_invocation_agrees'])
                self.assertFalse(launch['execution_authorized']);self.assertFalse(launch['binding_complete'])
                self.assertEqual(plan,before)
                launch['command'].append('mutated');launch['environment']['HOME']='mutated'
                self.assertEqual(plan,before)
                self.assertEqual(self.build(plan),self.build(before))

    def test_local_scripted_launch_has_a_distinct_identity_and_fixed_settings(self):
        plan=self.plan();before=deepcopy(plan)
        launch=self.build(plan,'codex-scripted-local/v1',43129)
        self.assertFalse(launch['canonical_invocation_agrees'])
        self.assertEqual(launch['purpose'],'scripted-protocol-diagnostic')
        self.assertEqual(launch['command'][-2:],plan['command'][-2:])
        self.assertEqual(launch['command'][:-8],plan['command'][:-2])
        self.assertEqual(launch['command'][-8:-2],['-c','chatgpt_base_url="http://127.0.0.1:43129"',
            '-c','openai_base_url="http://127.0.0.1:43129"','-c','check_for_update_on_startup=false'])
        self.assertEqual(launch['environment']['CODEX_REFRESH_TOKEN_URL_OVERRIDE'],'http://127.0.0.1:43129/oauth/token')
        self.assertEqual(set(launch['environment'])-set(plan['environment']),{'CODEX_REFRESH_TOKEN_URL_OVERRIDE','RUST_LOG'})
        for key,value in plan['environment'].items():self.assertEqual(launch['environment'][key],value)
        self.assertNotEqual(launch['launch_configuration_sha256'],self.build(plan)['launch_configuration_sha256'])
        self.assertNotEqual(launch['launch_configuration_sha256'],self.build(plan,'codex-scripted-local/v1',43130)['launch_configuration_sha256'])
        self.assertFalse(launch['study_eligible']);self.assertEqual(plan,before)

    def test_exec_inspection_binds_the_effective_configuration_without_erasing_its_difference(self):
        plan=self.plan();launch=self.build(plan,'codex-scripted-local/v1',43129)
        raw=('73 execve('+string('/toolbin/codex')+', '+array(launch['command'])+', '+
             array([k+'='+v for k,v in launch['environment'].items()])+') = 0\n73 +++ exited with 1 +++\n').encode()
        with tempfile.TemporaryDirectory() as temporary:
            trace=Path(temporary)/'exec.trace';trace.write_bytes(raw)
            evidence=NativeLaunchTraceEvidence(plan['invocation_sha256'],launch['launch_configuration_sha256'],
                hashlib.sha256(raw).hexdigest(),73,len(raw))
            report=inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=evidence)
            self.assertTrue(report['entrypoint_argv_environment_agree'])
            self.assertFalse(report['canonical_invocation_agrees'])
            self.assertFalse(report['binding_complete']);self.assertFalse(report['study_eligible'])
            self.assertFalse(report['exec_trace']['trace_provenance_verified'])
            self.assertNotIn('Fixed café',str(report))

    def test_profile_boundary_rejects_arbitrary_amendments_and_ambiguous_ports(self):
        plan=self.plan()
        for port in (None,True,False,0,-1,65536,1.0,'43129',[],{}):
            with self.subTest(port=port),self.assertRaises(ValueError):self.build(plan,'codex-scripted-local/v1',port)
        for port in (1,65535):self.assertEqual(self.build(plan,'codex-scripted-local/v1',port)['fixture_port'],port)
        for profile,port in (('canonical-native/v1',1),('arbitrary',None),(None,None)):
            with self.subTest(profile=profile),self.assertRaises(ValueError):self.build(plan,profile,port)
        with self.assertRaisesRegex(ValueError,'requires Codex'):
            self.build(self.plan('claude-fable-5-max'),'codex-scripted-local/v1',43129)
        with self.assertRaisesRegex(ValueError,'invalid native launch context'):
            build_native_launch_configuration(POLICY,plan,expected_invocation_sha256=plan['invocation_sha256'],context={})

    def trace_fixture(self, plan, launch):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        trace=Path(temporary.name)/'exec.trace'
        raw=('73 execve('+string('/toolbin/'+launch['command'][0])+', '+array(launch['command'])+', '+
             array([k+'='+v for k,v in launch['environment'].items()])+') = 0\n').encode()
        trace.write_bytes(raw)
        evidence=NativeLaunchTraceEvidence(plan['invocation_sha256'],launch['launch_configuration_sha256'],
            hashlib.sha256(raw).hexdigest(),73,len(raw))
        return trace,evidence

    def test_canonical_trace_link_supports_both_native_harness_configurations(self):
        for harness in ('codex-terra-max','claude-fable-5-max'):
            with self.subTest(harness=harness):
                plan=self.plan(harness);launch=self.build(plan);trace,evidence=self.trace_fixture(plan,launch)
                before=deepcopy((plan,launch));raw=trace.read_bytes()
                report=inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=evidence)
                self.assertTrue(report['canonical_invocation_agrees'])
                self.assertEqual((plan,launch),before);self.assertEqual(trace.read_bytes(),raw)

    def test_required_termination_reports_entrypoint_exit_separately_from_wrapper(self):
        plan=self.plan();launch=self.build(plan);trace,evidence=self.trace_fixture(plan,launch)
        raw=trace.read_bytes()+b'73 +++ exited with 0 +++\n72 +++ exited with 1 +++\n'
        trace.write_bytes(raw)
        evidence=replace(evidence,expected_trace_sha256=hashlib.sha256(raw).hexdigest(),max_trace_bytes=len(raw))
        legacy=inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=evidence)
        report=inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=evidence,require_termination=True)
        self.assertEqual(report['schema'],'caplab.native-launch-exec-link/v2')
        self.assertEqual(report['exec_trace'],legacy['exec_trace'])
        self.assertEqual(report['entrypoint_termination']['termination']['exit_code'],0)
        self.assertFalse(report['entrypoint_termination']['task_success_verified'])
        self.assertFalse(report['binding_complete']);self.assertFalse(report['study_eligible'])
        self.assertIsNone(report['native_capture_complete'])
        self.assertNotIn('entrypoint_termination',legacy)

    def test_malformed_requirement_cannot_select_or_skip_termination_checks(self):
        plan=self.plan();launch=self.build(plan);trace,evidence=self.trace_fixture(plan,launch)
        for value in (None,0,1,'false','true',[],{}):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'termination requirement'):
                inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=evidence,require_termination=value)

    def test_required_termination_keeps_failure_outcomes_and_refuses_missing_evidence(self):
        for harness,profile,port in (('codex-terra-max','canonical-native/v1',None),
                                    ('claude-fable-5-max','canonical-native/v1',None),
                                    ('codex-terra-max','codex-scripted-local/v1',43129)):
            plan=self.plan(harness);launch=self.build(plan,profile,port)
            trace,evidence=self.trace_fixture(plan,launch);execution=trace.read_bytes()
            for terminal,kind,code,signal in ((b'73 +++ exited with 137 +++\n','exited',137,None),
                                              (b'73 +++ killed by SIGKILL +++\n','signaled',None,'SIGKILL')):
                with self.subTest(harness=harness,profile=profile,terminal=terminal):
                    raw=execution+terminal;trace.write_bytes(raw)
                    current=replace(evidence,expected_trace_sha256=hashlib.sha256(raw).hexdigest(),max_trace_bytes=len(raw))
                    report=inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=current,require_termination=True)
                    outcome=report['entrypoint_termination']['termination']
                    self.assertEqual((outcome['kind'],outcome['exit_code'],outcome['signal']),(kind,code,signal))
                    self.assertFalse(report['study_eligible'])
            for terminal in (b'',b'74 +++ exited with 0 +++\n',b'73 +++ exited with 0 +++\n'*2):
                raw=execution+terminal;trace.write_bytes(raw)
                current=replace(evidence,expected_trace_sha256=hashlib.sha256(raw).hexdigest(),max_trace_bytes=len(raw))
                with self.subTest(terminal=terminal),self.assertRaises(ValueError):
                    inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=current,require_termination=True)

    def test_termination_mode_does_not_bypass_launch_profile_or_trace_anchors(self):
        plan=self.plan();launch=self.build(plan);trace,evidence=self.trace_fixture(plan,launch)
        raw=trace.read_bytes()+b'73 +++ exited with 0 +++\n';trace.write_bytes(raw)
        evidence=replace(evidence,expected_trace_sha256=hashlib.sha256(raw).hexdigest(),max_trace_bytes=len(raw))
        for changes in ({'expected_invocation_sha256':'0'*64},{'expected_launch_sha256':'0'*64},
                        {'expected_trace_sha256':'0'*64},{'expected_pid':74},{'max_trace_bytes':1}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=replace(evidence,**changes),require_termination=True)
        altered=deepcopy(launch);altered['environment']['HOME']='/other'
        altered['launch_configuration_sha256']=_digest({k:v for k,v in altered.items() if k!='launch_configuration_sha256'})
        with self.assertRaisesRegex(ValueError,'declared profile'):
            inspect_native_launch_trace(POLICY,plan,altered,trace,
                evidence=replace(evidence,expected_launch_sha256=altered['launch_configuration_sha256']),require_termination=True)

    def test_wrong_anchors_pid_or_trace_bounds_refuse(self):
        plan=self.plan();launch=self.build(plan);trace,evidence=self.trace_fixture(plan,launch)
        for changes in ({'expected_invocation_sha256':'0'*64},{'expected_launch_sha256':'0'*64},
                        {'expected_trace_sha256':'0'*64},{'expected_pid':74},{'expected_pid':True},
                        {'max_trace_bytes':1},{'max_trace_bytes':True}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                inspect_native_launch_trace(POLICY,plan,launch,trace,evidence=replace(evidence,**changes))

    def test_rehashed_configuration_edits_cannot_change_the_declared_profile(self):
        plan=self.plan();launch=self.build(plan);trace,evidence=self.trace_fixture(plan,launch)
        edits=[{'command':launch['command'][:-2]+['--model','other']+launch['command'][-2:]},
               {'environment':launch['environment']|{'HOME':'/other'}},{'cwd':'/other'},
               {'canonical_invocation_agrees':1},{'study_eligible':True},
               {'invocation_sha256':'0'*64},{'extra':'unregistered'}]
        for edit in edits:
            changed=deepcopy(launch)|edit
            changed['launch_configuration_sha256']=_digest({k:v for k,v in changed.items() if k!='launch_configuration_sha256'})
            with self.subTest(edit=edit),self.assertRaisesRegex(ValueError,'declared profile'):
                inspect_native_launch_trace(POLICY,plan,changed,trace,
                    evidence=replace(evidence,expected_launch_sha256=changed['launch_configuration_sha256']))
        altered=deepcopy(plan);altered['command'][4]='other'
        altered['invocation_sha256']=_digest({k:v for k,v in altered.items() if k!='invocation_sha256'})
        with self.assertRaisesRegex(ValueError,'invalid_native_capture_invocation'):
            self.build(altered)

    def test_canonical_configuration_cannot_verify_a_diagnostic_or_changed_environment(self):
        plan=self.plan();local=self.build(plan,'codex-scripted-local/v1',43129);trace,evidence=self.trace_fixture(plan,local)
        canonical=self.build(plan)
        with self.assertRaisesRegex(ValueError,'argv or environment differs'):
            inspect_native_launch_trace(POLICY,plan,canonical,trace,
                evidence=replace(evidence,expected_launch_sha256=canonical['launch_configuration_sha256']))
        altered=deepcopy(local);altered['environment']['LANG']='C'
        trace,evidence=self.trace_fixture(plan,altered)
        with self.assertRaisesRegex(ValueError,'argv or environment differs'):
            inspect_native_launch_trace(POLICY,plan,local,trace,evidence=evidence)
