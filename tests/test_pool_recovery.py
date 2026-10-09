"""Real supervisor-exit and retained-output controls for Opus310 P1/P2.

The SDK and process tree are real; refusal is injected only at OS read/pidfd
boundaries. No provider is called. The fixture marker outlives the supervisor.
"""
import json
import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

import tests.test_pool_shared_admission as pool_fixture

CLI = pool_fixture.CLI


REFUSAL_SUPERVISOR = r'''
import json, os, sys
from pathlib import Path
from unittest import mock
from caplab.advisory import pool_runner
from caplab.advisory.shared_admission import PoolAdmission
from caplab.revbench.shared_admission import SharedAdmissionEnrollment
d = json.loads(Path(sys.argv[1]).read_text())
def invoke():
    if d.get('route') != 'native':
        c = PoolAdmission(SharedAdmissionEnrollment(d['enrollment']), d['declaration'],
                         Path(d['out']), d['deadline'], Path(d['policy']))
        return pool_runner.invoke(d['declaration']['adapter'], 'fixture', 20,
                                 workspace=d['workspace'], admission=c, launch_key='refusal-slot')
    # Real native custody, not a pool right masquerading as a Revbench capture.
    from caplab.revbench.codex import _run_owned_process
    from caplab.revbench.process_tree import SandboxReadiness
    from tests.test_shared_admission import SharedAdmissionTests
    from caplab.runtime.canonical import sha256_hex, canonical_json
    t = SharedAdmissionTests()
    t.setUp()
    t.clocks.close()
    logical = ['/bin/sh', '-c', 'touch ' + d['marker']]
    original, _, _ = t.plan(logical, bind_root=True)
    with SandboxReadiness() as readiness:
        normalized = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session',
            '--block-fd', '{sandbox_block_fd}', '--info-fd', '{sandbox_info_fd}',
            '--ro-bind', '/', '/', '--bind', d['workspace'], d['workspace'], '--', *logical]
        plan = {**original, 'containment_argv_sha256': sha256_hex(canonical_json(normalized))}
        session, capture = t.claim(plan)
        capture.shared_admission = t.enrollment.capture(capture)
        fds = dict(zip(('{sandbox_block_fd}', '{sandbox_info_fd}'), readiness.pass_fds))
        actual = [str(fds[token]) if token in fds else token for token in normalized]
        return _run_owned_process(actual, normalized, logical, b'', contained_environment={},
            runtime_ref_sha256='d' * 64, apparatus_sha256='4' * 64, command_ref_sha256='e' * 64,
            credential_profile_id='caplab-openai-revbench', credential_profile_sha256='f' * 64,
            pass_fds=readiness.pass_fds, capture=capture, credential=None,
            monotonic_deadline=__import__('time').monotonic() + 20, sandbox_readiness=readiness)
real_read = os.read
real_link = os.link
def cut_completion(src, dst, **kwargs):
    if dst == 'completion.json':
        os._exit(71)  # outputs fsynced, native completion not yet published
    return real_link(src, dst, **kwargs)
def refused_read(fd, count):
    value = real_read(fd, count)
    if b'"child-pid"' in value:
        if d['fault'] == 'interrupt':
            raise KeyboardInterrupt('fixture-read-interrupt')
        return b'invalid info bytes'
    return value
patch = (mock.patch('os.link', side_effect=cut_completion) if d['fault'] == 'cut-completion'
         else mock.patch('os.pidfd_open', side_effect=PermissionError('fixture pidfd refusal'))
         if d['fault'] == 'pidfd' else mock.patch('os.read', side_effect=refused_read))
with patch:
    try:
        invoke()
    except BaseException as e:
        print(json.dumps({'type': type(e).__name__, 'message': str(e),
                          'notes': getattr(e, '__notes__', [])}), flush=True)
    else:
        raise AssertionError('expected actual readiness refusal')
'''


@unittest.skipUnless(CLI, 'set CAPLAB_TEST_SHARED_QM to the installed SDK')
class PoolRecoveryTests(unittest.TestCase):
    setUp = pool_fixture.PoolAdmissionTests.setUp
    controller = pool_fixture.PoolAdmissionTests.controller
    invoke = pool_fixture.PoolAdmissionTests.invoke
    snapshot = pool_fixture.PoolAdmissionTests.snapshot
    assert_accounting = pool_fixture.PoolAdmissionTests.assert_accounting

    def refused_supervisor(self, route):
        # Separate homes/assignments per refusal so all paths test a fresh child.
        for fault in ('pidfd', 'corrupt', 'interrupt'):
            with self.subTest(fault=fault):
                self.setUp()
                marker = self.workspace / 'application-marker'
                self.binary.write_text('#!/bin/sh\ntouch ' + str(marker) + '\n')
                config = self.root / 'supervisor.json'
                config.write_text(json.dumps({
                    'enrollment': self.enrollment.document, 'declaration': self.declaration,
                    'out': str(self.out), 'deadline': self.deadline,
                    'policy': str(Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'),
                    'workspace': str(self.workspace), 'fault': fault, 'route': route,
                    'marker': str(marker),
                }))
                supervisor = subprocess.Popen([sys.executable, '-c', REFUSAL_SUPERVISOR, str(config)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
                try:
                    out, err = supervisor.communicate(timeout=40)
                    self.assertEqual(supervisor.returncode, 0, err.decode())
                    observed = json.loads(out)
                    # EOF from process exit is the actual cut point, not a mock.
                    time.sleep(1.5)
                    self.assertFalse(marker.exists(), 'application ran after refused supervisor exited')
                    expected = 'KeyboardInterrupt' if fault == 'interrupt' else 'ProcessProofUnavailable'
                    self.assertEqual(observed['type'], expected)
                    message = 'fixture-read-interrupt' if fault == 'interrupt' else 'sandbox_readiness_identity_unavailable'
                    self.assertEqual(observed['message'], message)
                    self.assertTrue(any('sandbox_abort_init_unproved' in n for n in observed['notes']))
                    if route == 'pool':
                        self.assert_accounting(1, slots=1)
                finally:
                    # Only our real, separately created supervisor's group. A
                    # predecessor may still own the blocked init until exit.
                    self.assertGreater(supervisor.pid, 1)
                    try:
                        os.killpg(supervisor.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    if supervisor.poll() is None:
                        supervisor.wait(timeout=3)

    def test_no_witness_refusal_cannot_run_app_after_supervisor_exit(self):
        self.refused_supervisor('pool')

    def test_native_refusals_preserve_original_error_and_never_run_after_exit(self):
        self.refused_supervisor('native')

    def test_interrupted_case_rebuilds_retained_outputs_without_launch_or_charge(self):
        from caplab.advisory import pool_runner
        from tests.test_advisory_tree_v1 import TreeModeMeasureCaseTest
        case = {'substrate_id': 'fixture-doc', 'seed': 3, 'operator': 'truncated_tail',
                'source': {'kind': 'repo-doc'}}
        case_root = self.workspace / 'fixture-doc-truncated_tail-3'
        case_root.mkdir()
        binary = case_root / 'codex'
        binary.write_bytes(self.binary.read_bytes())
        binary.chmod(0o700)
        with mock.patch.dict(os.environ, {'PATH': str(case_root) + ':/usr/bin:/bin'}), \
                mock.patch.object(pool_runner, 'ENVIRONMENT_VERSION', 'iso-v1'):
            def measured():
                return pool_runner.measure_case(case, TreeModeMeasureCaseTest.PROSE, self.adapter, 20,
                    workspace=str(self.workspace), admission=self.controller(), assignment_prefix='frozen-spec')
            # Losing the returned row after both native completions is the actual
            # P2 cut point: results.jsonl has not committed a row yet.
            original = measured()
            records = self.snapshot()['records']
            for _ in range(2):
                recovered = measured()
                for arm in ('control', 'mutant'):
                    before = original[arm + '_attempts'][0]
                    after = recovered[arm + '_attempts'][0]
                    for name in ('doc', 'exit_code', 'raw_head', 'error'):
                        self.assertEqual(after[name], before[name])
                    self.assertEqual(after['recovery_basis'], 'retained-completion')
                self.assertEqual(self.snapshot()['records'], records)
                self.assert_accounting(2)

    def test_uncertain_constructor_recovers_unscored_without_replaying(self):
        from caplab.advisory import pool_runner
        real = subprocess.Popen
        def failing_bwrap(argv, *args, **kwargs):
            if argv[0] == '/usr/bin/bwrap':
                raise FileNotFoundError('fixture uncertain constructor')
            return real(argv, *args, **kwargs)
        with mock.patch.object(subprocess, 'Popen', side_effect=failing_bwrap):
            with self.assertRaises(FileNotFoundError):
                self.invoke()
        records = self.snapshot()['records']
        recovered = pool_runner.invoke(self.adapter, 'local fixture', 20,
            workspace=str(self.workspace), admission=self.controller(),
            launch_key='case:control:1', recover_assigned=True)
        self.assertIsNone(recovered['doc'])
        self.assertIn('FileNotFoundError', recovered['error'])
        self.assertEqual(recovered['recovery_basis'], 'retained-completion')
        self.assertEqual(self.snapshot()['records'], records)
        self.assert_accounting(0, slots=1, outstanding=1)

    def test_recovery_refuses_changed_prompt_and_output_preimages(self):
        from caplab.advisory import pool_runner
        from caplab.revbench.custody import LiveExecutionCustodyError
        result = self.invoke()
        records = self.snapshot()['records']
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'intent_changed'):
            pool_runner.invoke(self.adapter, 'changed prompt', 20,
                workspace=str(self.workspace), admission=self.controller(),
                launch_key='case:control:1', recover_assigned=True)
        Path(result['custody_path'], 'stdout').write_bytes(b'changed output')
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'completion_changed'):
            pool_runner.invoke(self.adapter, 'local fixture', 20,
                workspace=str(self.workspace), admission=self.controller(),
                launch_key='case:control:1', recover_assigned=True)
        self.assertEqual(self.snapshot()['records'], records)
        self.assert_accounting(1)

    def test_crash_before_completion_reports_unscored_assigned_outcome_and_holds(self):
        from caplab.advisory import pool_runner
        config = self.root / 'crash-supervisor.json'
        config.write_text(json.dumps({
            'enrollment': self.enrollment.document, 'declaration': self.declaration,
            'out': str(self.out), 'deadline': self.deadline,
            'policy': str(Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'),
            'workspace': str(self.workspace), 'fault': 'cut-completion',
        }))
        run = subprocess.run([sys.executable, '-c', REFUSAL_SUPERVISOR, str(config)],
            capture_output=True, timeout=40, start_new_session=True)
        self.assertEqual(run.returncode, 71, run.stderr.decode())
        records = self.snapshot()['records']
        recovered = pool_runner.invoke(self.adapter, 'fixture', 20,
            workspace=str(self.workspace), admission=self.controller(),
            launch_key='refusal-slot', recover_assigned=True)
        self.assertIsNone(recovered['doc'])
        self.assertIsNone(recovered['exit_code'])
        self.assertEqual(recovered['recovery_basis'], 'assigned-output-unavailable')
        self.assertIn('no completion', recovered['error'])
        self.assertEqual(self.snapshot()['records'], records)
        self.assert_accounting(1, slots=1)

    def test_public_cli_declared_domain_mapping_is_pinned_and_acquires_no_rights(self):
        import yaml
        from caplab.advisory.shared_admission import SCHEMA
        from caplab.advisory.run_spec import declaration_digest
        from caplab.runtime.canonical import canonical_json, sha256_hex
        declaration_dir = self.root / self.declaration['id']
        declaration_dir.mkdir()
        declaration = declaration_dir / 'backend.yaml'
        declaration.write_text(yaml.safe_dump(self.declaration))
        enrollment_path = self.root / 'enrollment.json'
        enrollment_path.write_bytes(canonical_json(self.enrollment.document))
        config = self.root / 'pool-config.json'
        config.write_bytes(canonical_json({
            'schema_version': SCHEMA, 'enrollment_path': str(enrollment_path),
            'enrollment_sha256': sha256_hex(enrollment_path.read_bytes()),
            'declaration_sha256': declaration_digest(self.declaration), 'valid_until': self.deadline,
            'native_policy_path': str(Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'),
        }))
        command = [sys.executable, '-m', 'caplab.advisory', 'admission-describe',
                   '--out', str(self.out), '--backend', self.declaration['id'],
                   '--backends-root', str(self.root), '--shared-admission', str(config)]
        run = subprocess.run(command, capture_output=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr.decode())
        result = json.loads(run.stdout)
        self.assertEqual(result['declared_account_id'], 'codex-main')
        self.assertEqual(result['pool_ids'], ['fixture-pool'])
        self.assertEqual(result['profile']['id'], 'caplab-codex-main')
        self.assertFalse(result['authenticated_provider_identity'])
        self.assertEqual(result['release_sha256'], self.enrollment.document['release_sha256'])
        self.assertFalse((self.root / 'shared-home').exists())

    def test_capability_latency_consumes_original_invocation_timeout(self):
        # Genuine SDK reply delayed at its subprocess boundary. Constructing
        # enrollment precedes invocation; its next pin check belongs to it.
        controller = self.controller()
        real = subprocess.run
        delayed = False
        def delayed_capabilities(argv, *args, **kwargs):
            nonlocal delayed
            result = real(argv, *args, **kwargs)
            if argv == [CLI, 'admission', 'capabilities'] and not delayed:
                delayed = True
                time.sleep(5.1)
            return result
        with mock.patch.object(subprocess, 'run', side_effect=delayed_capabilities):
            result = self.invoke(controller, timeout=5)
        self.assertIsNone(result['exit_code'])
        self.assertIn('deadline expired', result['error'])
        self.assert_accounting(0)

