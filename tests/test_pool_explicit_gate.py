"""Real pool/SDK/bwrap controls. Local codex fixture is not model qualification."""
import json
import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

from tests import test_pool_shared_admission as fixture
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench import process_tree


@unittest.skipUnless(fixture.CLI, 'set CAPLAB_TEST_SHARED_QM to installed SDK')
class PoolExplicitGateTests(unittest.TestCase):
    setUp = fixture.PoolAdmissionTests.setUp
    controller = fixture.PoolAdmissionTests.controller
    invoke = fixture.PoolAdmissionTests.invoke
    snapshot = fixture.PoolAdmissionTests.snapshot
    assert_accounting = fixture.PoolAdmissionTests.assert_accounting

    def worker(self, name, mode):
        """Stop an actual supervisor after SDK creation recording, before readiness."""
        marker = self.workspace / ('marker-' + name)
        self.binary.write_text('#!/bin/sh\ntouch ' + str(marker) +
                               '\n/bin/sleep 0.2\nprintf \'{"verdict":"clean"}\\n\'\n')
        cut = self.root / (name + '-cut')
        resume = self.root / (name + '-resume')
        configuration = self.root / (name + '.json')
        configuration.write_bytes(canonical_json({'enrollment': self.enrollment.document,
            'declaration': self.declaration, 'out': str(self.out), 'deadline': self.deadline,
            'native_policy': str(Path(fixture.__file__).resolve().parents[1] /
                'docs/product/contracts/native-agent-systems.json')}))
        script = self.root / (name + '.py')
        script.write_text('''import json,os,pathlib,subprocess,sys,time
from caplab.advisory.shared_admission import PoolAdmission
from caplab.advisory import pool_runner
from caplab.revbench.shared_admission import SharedAdmissionEnrollment
from caplab.revbench import process_tree
config=json.loads(pathlib.Path(sys.argv[1]).read_bytes())
real_run=subprocess.run
def paused(argv,*a,**kw):
    result=real_run(argv,*a,**kw)
    if argv[1:3]==['admission','record-launch']:
        pathlib.Path(sys.argv[3]).touch()
        end=time.monotonic()+20
        while not pathlib.Path(sys.argv[4]).exists():
            if time.monotonic()>end: raise TimeoutError('test cut-point not resumed')
            time.sleep(.01)
    return result
subprocess.run=paused
mode=sys.argv[5]
if mode=='pidfd':
    def refused(*a,**kw): raise PermissionError('actual observer pidfd capability unavailable')
    os.pidfd_open=refused
elif mode=='corrupt-info':
    observe=process_tree.SandboxReadiness.observe
    def corrupt(self,*a,**kw):
        real_read=os.read
        def damaged(fd,n):
            data=real_read(fd,n)
            return b'not-json' if fd==self.info_reader and data else data
        os.read=damaged
        try: return observe(self,*a,**kw)
        finally: os.read=real_read
    process_tree.SandboxReadiness.observe=corrupt
c=PoolAdmission(SharedAdmissionEnrollment(config['enrollment']),config['declaration'],
    pathlib.Path(config['out']),config['deadline'],pathlib.Path(config['native_policy']))
try:
    pool_runner.invoke(config['declaration']['adapter'],'local fixture',20,
        workspace=sys.argv[2],admission=c,launch_key=sys.argv[6])
except BaseException as error:
    print(json.dumps({'type':type(error).__name__,'error':str(error),
        'notes':getattr(error,'__notes__',[])}),flush=True)
    raise
''')
        child = subprocess.Popen([sys.executable, str(script), str(configuration),
            str(self.workspace), str(cut), str(resume), mode, name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: self.reap(child))
        deadline = time.monotonic() + 15
        while not cut.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertTrue(cut.exists(), child.poll())
        key = sha256_hex(canonical_json({'domain': self.enrollment.document['custody_domain_id'],
                                        'assignment': name}))
        root = self.out / 'shared-launches' / key
        creation = json.loads((root / 'shared-admission-creation.json').read_bytes())
        witness = process_tree.namespace_init(creation['pid'], deadline=time.monotonic() + 2)
        self.assertIsNotNone(witness)
        self.addCleanup(lambda: self.close_fixture_witness(witness))
        return child, resume, marker, witness, root

    @staticmethod
    def reap(child):
        if child.poll() is None:
            child.kill()
        child.communicate(timeout=5)

    @staticmethod
    def close_fixture_witness(witness):
        try:
            if not witness.dead():
                signal.pidfd_send_signal(witness.descriptor, signal.SIGKILL)
        finally:
            witness.close()

    def test_supervisor_term_and_kill_before_release_never_exec_application(self):
        for sig in (signal.SIGTERM, signal.SIGKILL):
            with self.subTest(signal=sig.name):
                child, resume, marker, witness, root = self.worker(sig.name, 'normal')
                os.kill(child.pid, sig)
                child.communicate(timeout=5)
                self.assertTrue(witness.dead(3000))
                self.assertFalse(marker.exists(), 'block EOF executed unapproved native application')
                self.assertFalse((root / 'completion.json').exists())
        self.assert_accounting(2, slots=2)
        before = self.snapshot()['records']
        self.controller().reconcile()
        self.assertEqual(self.snapshot()['records'], before)

    def test_no_witness_refusals_survive_supervisor_exit_without_application(self):
        for mode in ('pidfd', 'corrupt-info'):
            with self.subTest(mode=mode):
                child, resume, marker, witness, root = self.worker(mode, mode)
                resume.touch()
                stdout, stderr = child.communicate(timeout=5)
                self.assertNotEqual(child.returncode, 0, stderr)
                self.assertEqual(json.loads(stdout)['type'], 'ProcessProofUnavailable')
                self.assertTrue(json.loads(stdout)['notes'])
                self.assertTrue(witness.dead(3000))
                self.assertFalse(marker.exists(), 'refusal/cleanup EOF executed application')
                completion = json.loads((root / 'completion.json').read_bytes())
                self.assertFalse(completion['outputs_complete'])
                self.assertTrue(completion['cleanup_errors'])
        self.assert_accounting(2, slots=2)

    def test_stdin_payload_including_release_byte_and_unicode_is_unchanged(self):
        from caplab.advisory import pool_runner
        self.binary.write_text('#!/usr/bin/python3\nimport json,sys\n'
            'print(json.dumps({"payload":sys.stdin.buffer.read().decode("utf-8")}))\n')
        prompt = 'alpha\x01\n雪\n'
        result = pool_runner.invoke(self.adapter, prompt, 20, workspace=str(self.workspace),
                                    admission=self.controller(), launch_key='stdin')
        self.assertEqual(result['doc'], {'payload': prompt})
        self.assert_accounting(1)

    def test_arg_transport_keeps_native_argv_and_empty_stdin(self):
        self.adapter['prompt_mode'] = 'arg'
        self.binary.write_text('#!/usr/bin/python3\nimport json,sys\n'
            'print(json.dumps({"last":sys.argv[-1],"stdin":list(sys.stdin.buffer.read())}))\n')
        result = self.invoke()
        self.assertEqual(result['doc'], {'last': 'local fixture', 'stdin': []})
        self.assert_accounting(1)

    def test_gate_bytes_and_interpreter_are_pinned_and_drift_refuses_replay(self):
        from caplab.retrieval import exec_gate
        from caplab.revbench.custody import LiveExecutionCustodyError
        result = self.invoke()
        intent = json.loads(Path(result['custody_path'], 'intent.json').read_bytes())
        self.assertEqual(intent['exec_gate_sha256'], sha256_hex(Path(exec_gate.__file__).read_bytes()))
        self.assertEqual(intent['gate_interpreter_sha256'], sha256_hex(Path('/usr/bin/python3').read_bytes()))
        original = Path(exec_gate.__file__)
        changed = self.root / 'changed-gate.py'
        changed.write_bytes(original.read_bytes() + b'\n# changed\n')
        before = self.snapshot()['records']
        with mock.patch.object(exec_gate, '__file__', str(changed)):
            with self.assertRaisesRegex(LiveExecutionCustodyError, 'retained_intent_changed'):
                from caplab.advisory import pool_runner
                pool_runner.invoke(self.adapter, 'local fixture', 20, workspace=str(self.workspace),
                    admission=self.controller(), launch_key='case:control:1', recover_assigned=True)
        self.assertEqual(self.snapshot()['records'], before)

    @unittest.skipUnless(os.environ.get('CAPLAB_TEST_POOL_PREDECESSOR'), 'set immutable predecessor source')
    def test_real_predecessor_custody_reconciles_only_and_refuses_new_administration(self):
        child_source = Path(os.environ['CAPLAB_TEST_POOL_PREDECESSOR']).resolve(strict=True)
        config = self.root / 'old-config.json'
        config.write_bytes(canonical_json({'enrollment': self.enrollment.document,
            'declaration': self.declaration, 'out': str(self.out), 'deadline': self.deadline,
            'native_policy': str(Path(fixture.__file__).resolve().parents[1] /
                'docs/product/contracts/native-agent-systems.json')}))
        script = '''import json,pathlib,sys
from caplab.advisory.shared_admission import PoolAdmission
from caplab.revbench.shared_admission import SharedAdmissionEnrollment
from caplab.advisory import pool_runner
x=json.loads(pathlib.Path(sys.argv[1]).read_bytes())
c=PoolAdmission(SharedAdmissionEnrollment(x['enrollment']),x['declaration'],pathlib.Path(x['out']),x['deadline'],pathlib.Path(x['native_policy']))
r=pool_runner.invoke(x['declaration']['adapter'],'old fixture',20,workspace=sys.argv[2],admission=c,launch_key='historical')
assert r['exit_code']==0 and r['shared_admission']['status']=='settled',r
'''
        done = subprocess.run([sys.executable, '-c', script, str(config), str(self.workspace)],
            env={**os.environ, 'PYTHONPATH': str(child_source)}, capture_output=True, timeout=30)
        self.assertEqual(done.returncode, 0, done.stderr)
        files = {str(x.relative_to(self.out)): sha256_hex(x.read_bytes())
                 for x in self.out.rglob('*') if x.is_file()}
        before = self.snapshot()['records']
        from caplab.advisory.shared_admission import PoolAdmission
        from caplab.revbench.custody import LiveExecutionCustodyError
        recovery = PoolAdmission(self.enrollment, self.declaration, self.out, self.deadline,
            Path(fixture.__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json',
            recovery=True)
        self.assertIn(recovery.reconcile()[0]['status'], {'existing', 'settled'})
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'reconciliation_only'):
            self.invoke(recovery, key='not-a-legacy-retry')
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'custody_conflict'):
            self.controller()
        self.assertEqual(self.snapshot()['records'], before)
        # Authentic reconciliation can append new transport evidence. Every
        # original byte and authoritative SDK event remains unchanged.
        for name, digest in files.items():
            self.assertEqual(sha256_hex((self.out / name).read_bytes()), digest, name)
        self.assert_accounting(1)

    def test_setup_refusal_preserves_original_stderr_and_does_not_score_it(self):
        from caplab.advisory import pool_runner
        from caplab.revbench.process_tree import ProcessProofUnavailable
        argv = pool_runner.sandbox_argv(self.adapter['command'], str(self.workspace),
            extra_ro=['/caplab-fixture-path-does-not-exist'])
        with self.assertRaises(ProcessProofUnavailable):
            self.controller().run(self.adapter, argv, launch_key='mount-refused',
                timeout=20, cwd=str(self.workspace), stdin=b'original prompt')
        root = next(x for x in (self.out / 'shared-launches').iterdir() if x.is_dir())
        stderr = (root / 'stderr').read_bytes()
        self.assertIn(b'bwrap:', stderr)
        self.assertIn(b'caplab-fixture-path-does-not-exist', stderr)
        completion = json.loads((root / 'completion.json').read_bytes())
        self.assertFalse(completion['outputs_complete'])
        self.assertEqual(completion['stderr_sha256'], sha256_hex(stderr))
        self.assertIsNotNone(completion['exit_code'])
        self.assert_accounting(1, slots=1)
