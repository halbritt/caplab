"""Actual local executables, namespace custody and private deployed SDK homes.

The local codex-named executable is not a model subject or native qualification.
"""
import datetime
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench import shared_admission as sdk
import test_shared_admission as sdk_fixture

CLI = os.environ.get('CAPLAB_TEST_SHARED_QM')

@unittest.skipUnless(CLI, 'requires explicit deployed SDK')
class ArtifactRaterAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.output = self.root / 'output'; self.output.mkdir(mode=0o700)
        self.home = self.root / 'native-home'; self.home.mkdir(); (self.home / '.codex').mkdir()
        self.program = self.root / 'codex'
        self.program.write_text('#!/usr/bin/python3\nimport pathlib,sys\np=pathlib.Path('+repr(str(self.output/'calls'))+')\np.write_text(p.read_text()+"x" if p.exists() else "x")\nprint("local fixture version")\n')
        self.program.chmod(0o700)
        self.manifest = self.root / 'manifest.json'; self.manifest.write_bytes(canonical_json({'entries': []}))
        from caplab.runtime.native_admission import initialize_domain
        domain = initialize_domain(self.output)
        paths = sdk_fixture.fixture(self.root, CLI)
        profile = {'schema_version': 'caplab-artifact-rater-declared-profile/1',
            'profile_id': 'caplab-codex-main', 'host': 'fixture-host', 'account_id': 'codex-main',
            'config_home': None, 'native_home': str(self.home)}
        doc = {'schema_version': sdk.PINNED_SCHEMA, 'cli': CLI,
            'cli_sha256': sha256_hex(Path(CLI).read_bytes()),
            'sdk_source_tree_sha256': 'sha256:af3621e6ddd0062cbc46ec5e37bb3c31f8321dd88a4024a8495055aac6bfa247',
            'home': str(self.root / 'shared-home'), 'home_id': 'fixture-home',
            'caller_id': 'caplab', 'custody_domain_id': domain, 'binding_id': 'artifact-fixture',
            **paths, 'credential_profile_sha256': sha256_hex(canonical_json(profile))}
        for key in ('release', 'overlay', 'policy'):
            doc[key + '_sha256'] = sha256_hex(Path(doc[key + '_path']).read_bytes())
        self.enrollment = self.root / 'enrollment.json'; self.enrollment.write_bytes(canonical_json(doc))
        self.config = self.root / 'rater-enrollment.json'
        self.config.write_bytes(canonical_json({'schema_version': 'caplab-artifact-rater-shared-admission/1',
            'manifest_sha256': sha256_hex(self.manifest.read_bytes()), 'output_root': str(self.output),
            'model': 'gpt-5.6-terra', 'effort': 'max',
            'expires_at': (datetime.datetime.now(datetime.UTC)+datetime.timedelta(minutes=3)).isoformat(),
            'native_home': str(self.home), 'codex_executable': str(self.program),
            'codex_sha256': sha256_hex(self.program.read_bytes()),
            'native_policy_path': str(Path(__file__).resolve().parents[1]/'docs/product/contracts/native-agent-systems.json'),
            'native_policy_sha256': sha256_hex((Path(__file__).resolve().parents[1]/'docs/product/contracts/native-agent-systems.json').read_bytes()),
            'enrollment_path': str(self.enrollment), 'enrollment_sha256': sha256_hex(self.enrollment.read_bytes())}))
    def controller(self):
        from caplab.runtime.artifact_admission import ArtifactRaterAdmission
        return ArtifactRaterAdmission.read(self.config, self.manifest, self.output, 'gpt-5.6-terra', 'max')
    def status(self):
        return json.loads(subprocess.check_output([CLI,'admission','status','--home',str(self.root/'shared-home'),
            '--home-id','fixture-home','--now',sdk._now()]))
    def test_version_helper_is_counted_once_and_replay_creates_no_child_or_event(self):
        from caplab import artifact_rater_cli as rater
        result = rater._rater_metadata(self.output, 'gpt-5.6-terra', 'max', shared_admission=self.controller())
        self.assertEqual(result['version'], 'local fixture version')
        self.assertEqual((self.output/'calls').read_text(), 'x')
        state=self.status()
        self.assertEqual(state['pools']['fixture-pool'], {'slots':0,'windows':{'fixture-window':{'spent':1,'outstanding':0}}})
        self.assertEqual(rater._rater_metadata(self.output,'gpt-5.6-terra','max',shared_admission=self.controller()),result)
        self.assertEqual((self.output/'calls').read_text(),'x')
        self.assertEqual(self.status()['records'],state['records'])

    def score_fixture(self):
        from caplab import artifact_rater_cli as rater
        diff = self.root/'campaign/attempts/slot-1/diff.patch'; diff.parent.mkdir(parents=True); diff.write_bytes(b'+changed\n')
        codes = self.root/'scenarios/scenario-1/codes.json'; codes.parent.mkdir(parents=True)
        codes.write_text(json.dumps({'codes':[{'id':'C1','positive':'fixture','negative_space':'fixture'},
            {'id':'SCOPE','positive':'fixture','negative_space':'fixture'}]}))
        entry={'slot':'slot-1','scenario':'scenario-1','code_ids':['C1','SCOPE'],'diff_sha256':sha256_hex(diff.read_bytes())}
        manifest={'campaign_root':str(self.root/'campaign'),'scenario_root':str(self.root/'scenarios'),'entries':[entry]}
        self.repin_program("import pathlib,sys\np=pathlib.Path("+repr(str(self.output/'calls'))+")\np.write_text(p.read_text()+'x' if p.exists() else 'x')\nif '--version' in sys.argv: print('local fixture version')\nelse:\n pathlib.Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text('local invalid judgment')\n pathlib.Path('prompt-received').write_bytes(sys.stdin.buffer.read())\n print('local process outcome, not native qualification')\n")
        self.manifest.write_bytes(canonical_json(manifest)); d=json.loads(self.config.read_bytes())
        d['manifest_sha256']=sha256_hex(self.manifest.read_bytes()); self.config.write_bytes(canonical_json(d))
        return rater,entry,manifest

    def test_lost_capture_publication_projects_retained_trial_without_second_child(self):
        from unittest import mock
        rater,entry,manifest=self.score_fixture()
        real=rater._write_new
        def fail_events(path,data):
            if path.name=='events.jsonl':
                raise OSError('lost artifact publication')
            return real(path,data)
        with mock.patch.object(rater,'_write_new',side_effect=fail_events):
            with self.assertRaisesRegex(OSError,'lost artifact publication'):
                rater._score_entry(entry,manifest,self.output,'gpt-5.6-terra','max',20,shared_admission=self.controller())
        state=self.status(); self.assertEqual((self.output/'calls').read_text(),'x')
        self.assertEqual(state['pools']['fixture-pool']['windows']['fixture-window'],{'spent':1,'outstanding':0})
        result=rater._score_entry(entry,manifest,self.output,'gpt-5.6-terra','max',20,shared_admission=self.controller())
        self.assertFalse(result[1])  # local fixture is deliberately not a native judgment
        self.assertEqual((self.output/'calls').read_text(),'x')
        self.assertEqual(self.status()['records'],state['records'])
        self.assertEqual(len(list((self.output/'scores/slot-1').glob('attempt-*'))),1)
        attempt=self.output/'scores/slot-1/attempt-001'
        self.assertTrue((attempt/'record.json').exists())
        self.assertEqual((attempt/'workspace/prompt-received').read_bytes(),(attempt/'prompt.txt').read_bytes())
        completion=self.controller().completion_for('rater','trial:slot-1:attempt-001')
        record=json.loads((attempt/'record.json').read_bytes())
        self.assertEqual((record['started_at'],record['finished_at']),(completion['started_at'],completion['finished_at']))
        self.assertEqual(record['shared_admission']['process_id'],completion['process_id'])

    def repin_program(self, source):
        self.program.write_text('#!/usr/bin/python3\n'+source)
        d=json.loads(self.config.read_bytes());d['codex_sha256']=sha256_hex(self.program.read_bytes())
        self.config.write_bytes(canonical_json(d))

    def test_child_exec_failure_counts_once_with_retained_stderr_and_replay(self):
        self.repin_program("import os; os.execv('/definitely-absent-rater',['/definitely-absent-rater'])\n")
        c=self.controller(); workspace=self.output/'version-workspace';workspace.mkdir()
        result=c.run_native(['codex','--version'],cwd=workspace,assignment='helper:codex-version',timeout=20)
        self.assertNotEqual(result.returncode,0);self.assertIn(b'FileNotFoundError',result.stderr)
        state=self.status();self.assertEqual(state['pools']['fixture-pool'],{'slots':0,'windows':{'fixture-window':{'spent':1,'outstanding':0}}})
        replay=self.controller().run_native(['codex','--version'],cwd=workspace,assignment='helper:codex-version',timeout=20)
        self.assertEqual((replay.stdout,replay.stderr,replay.returncode),(result.stdout,result.stderr,result.returncode))
        self.assertEqual(self.status()['records'],state['records'])

    def test_constructor_exception_holds_both_resources_on_restart(self):
        from unittest import mock
        from caplab.revbench.custody import LiveExecutionCustodyError
        c=self.controller();workspace=self.output/'version-workspace';workspace.mkdir()
        original=subprocess.Popen
        def unknown(command,*a,**kw):
            if command[0]=='/usr/bin/bwrap':
                raise OSError('creation cannot be proven absent')
            return original(command,*a,**kw)
        with mock.patch.object(subprocess,'Popen',side_effect=unknown):
            with self.assertRaisesRegex(OSError,'cannot be proven absent'):
                c.run_native(['codex','--version'],cwd=workspace,assignment='helper:codex-version',timeout=20)
        state=self.status();self.assertEqual(state['pools']['fixture-pool'],{'slots':1,'windows':{'fixture-window':{'spent':0,'outstanding':1}}})
        self.assertFalse((self.output/'calls').exists())
        with self.assertRaisesRegex(LiveExecutionCustodyError,'unresolved_no_retry'):
            self.controller().run_native(['codex','--version'],cwd=workspace,assignment='helper:codex-version',timeout=20)
        self.assertEqual(self.status()['records'],state['records'])

    def test_quota_refusal_before_creation_returns_closed_unused_permit(self):
        from caplab.revbench.custody import LiveExecutionCustodyError
        obs=self.root/'observations.json';rows=json.loads(obs.read_bytes());rows[0]['payload']['windows'][0]['value_state']='unknown'
        row=rows[0];row.pop('_content_hash');row['_content_hash']='sha256:'+sha256_hex(canonical_json(row));obs.write_bytes(canonical_json(rows))
        c=self.controller();workspace=self.output/'version-workspace';workspace.mkdir()
        with self.assertRaisesRegex(LiveExecutionCustodyError,'shared_admission_refused'):
            c.run_native(['codex','--version'],cwd=workspace,assignment='helper:codex-version',timeout=20)
        state=self.status();self.assertEqual(state['pools']['fixture-pool'],{'slots':0,'windows':{'fixture-window':{'spent':0,'outstanding':0}}})
        self.assertFalse((self.output/'calls').exists())

    def test_enrolled_output_cannot_be_reopened_unenrolled(self):
        from caplab import artifact_rater_cli as rater
        from caplab.artifact_rater import CalibrationError
        self.controller()
        from unittest import mock
        with mock.patch.object(subprocess,'run',side_effect=AssertionError('unenrolled native helper must not run')), self.assertRaisesRegex(CalibrationError,'retained enrollment'):
            rater._rater_metadata(self.output,'gpt-5.6-terra','max')
        self.assertFalse((self.output/'calls').exists())

    def test_parent_death_before_explicit_release_does_not_execute_fixture(self):
        import sys,time,signal
        signal_path=self.root/'observer-entered'
        source='''import sys,time
from pathlib import Path
from caplab.runtime.artifact_admission import ArtifactRaterAdmission
from caplab.revbench.process_tree import SandboxReadiness
config,manifest,output,ready=sys.argv[1:]
c=ArtifactRaterAdmission.read(config,manifest,output,'gpt-5.6-terra','max')
w=Path(output)/'version-workspace';w.mkdir()
def stop_before_release(self,*a,**kw):
    Path(ready).write_text('outer creation already recorded')
    time.sleep(60)
SandboxReadiness.observe=stop_before_release
c.run_native(['codex','--version'],cwd=w,assignment='helper:codex-version',timeout=30)
'''
        p=subprocess.Popen([sys.executable,'-c',source,str(self.config),str(self.manifest),str(self.output),str(signal_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            until=time.monotonic()+15
            while not signal_path.exists() and p.poll() is None and time.monotonic()<until:
                time.sleep(.02)
            self.assertTrue(signal_path.exists(),'supervisor did not reach observed creation cut point')
            p.send_signal(signal.SIGTERM);_,stderr=p.communicate(timeout=5)
            self.assertEqual(p.returncode,-signal.SIGTERM,stderr)
            time.sleep(.3)
            self.assertFalse((self.output/'calls').exists())
            state=self.status();self.assertEqual(state['pools']['fixture-pool'],{'slots':1,'windows':{'fixture-window':{'spent':1,'outstanding':0}}})
            result=self.controller().reconcile()
            self.assertTrue(result)
            self.assertEqual(self.status()['pools'],state['pools'])
        finally:
            if p.poll() is None:
                p.kill()
            p.communicate(timeout=5)

    def test_tampered_input_or_program_refuses_replay_without_extra_charge(self):
        from caplab.revbench.custody import LiveExecutionCustodyError
        c=self.controller();w=self.output/'version-workspace';w.mkdir()
        c.run_native(['codex','--version'],cwd=w,assignment='helper:codex-version',timeout=20)
        state=self.status();self.program.write_text('changed executable')
        with self.assertRaisesRegex(LiveExecutionCustodyError,'executable_changed'):
            c.run_native(['codex','--version'],cwd=w,assignment='helper:codex-version',timeout=20)
        self.assertEqual(self.status()['records'],state['records'])

    def test_public_cli_describes_reconciles_and_runs_native_paths(self):
        import sys
        from caplab import artifact_rater_cli as rater
        # The manifest has zero trials; this isolates actual public helper routing.
        args=['--manifest',str(self.manifest),'--output-root',str(self.output),'--model','gpt-5.6-terra',
              '--effort','max','--shared-admission',str(self.config)]
        for action in ('admission-describe','run','admission-reconcile','run'):
            result=subprocess.run([sys.executable,'-m','caplab.artifact_rater_cli',action]+args,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            if action=='admission-describe':
                self.assertEqual(json.loads(result.stdout)['identity_basis'],'operator-declared-account-domain')
        self.assertEqual((self.output/'calls').read_text(),'x')
        self.assertEqual(self.status()['pools']['fixture-pool']['windows']['fixture-window']['spent'],1)

    def test_changed_prompt_refuses_same_assignment_without_new_child(self):
        from caplab.revbench.custody import LiveExecutionCustodyError
        rater,entry,manifest=self.score_fixture();c=self.controller()
        rater._score_entry(entry,manifest,self.output,'gpt-5.6-terra','max',20,shared_admission=c)
        attempt=self.output/'scores/slot-1/attempt-001';record=json.loads((attempt/'record.json').read_bytes())
        # The genuine command and held assignment are recovered from its artifact record.
        command=record['command'][:-1]+['-'];state=self.status()
        with self.assertRaisesRegex(LiveExecutionCustodyError,'retained_intent_changed'):
            c.run_native(command,cwd=attempt/'workspace',assignment='trial:slot-1:attempt-001',timeout=20,input=b'changed request')
        self.assertEqual((self.output/'calls').read_text(),'x')
        self.assertEqual(self.status()['records'],state['records'])

    def test_parallel_callers_share_one_version_assignment(self):
        import concurrent.futures
        from caplab.revbench.custody import LiveExecutionCustodyError
        c=self.controller();w=self.output/'version-workspace';w.mkdir()
        def run():
            try:
                return self.controller().run_native(['codex','--version'],cwd=w,assignment='helper:codex-version',timeout=20)
            except LiveExecutionCustodyError as error:
                return error
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as workers:
            results=list(workers.map(lambda _:run(),range(2)))
        self.assertTrue(any(isinstance(r,subprocess.CompletedProcess) and r.returncode==0 for r in results),results)
        for r in results:
            if isinstance(r,LiveExecutionCustodyError):
                self.assertRegex(str(r),'incomplete_no_retry|unresolved_no_retry')
        self.assertEqual((self.output/'calls').read_text(),'x')
        state=self.status();self.assertEqual(state['pools']['fixture-pool'],{'slots':0,'windows':{'fixture-window':{'spent':1,'outstanding':0}}})
        c.run_native(['codex','--version'],cwd=w,assignment='helper:codex-version',timeout=20)
        self.assertEqual(self.status()['records'],state['records'])
