"""Real SDK/home, advisory entry path, and local native-command process fixtures.

The executable named codex below is a provider-free fixture, not qualification
of Codex or authentication of a provider account. No SDK protocol fake is used.
"""
import datetime
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from caplab.advisory import pool_runner
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench import shared_admission as shared
from caplab.revbench.custody import LiveExecutionCustodyError
from tests.test_shared_admission import fixture

CLI = os.environ.get('CAPLAB_TEST_SHARED_QM')

@unittest.skipUnless(CLI, 'set CAPLAB_TEST_SHARED_QM to the installed SDK')
class PoolAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = fixture(self.root, CLI)
        self.out = self.root / 'run'
        self.out.mkdir(mode=0o700)
        custody = self.out / 'shared-launches'
        custody.mkdir(mode=0o700)
        body = {'schema_version': 'caplab-pool-custody-domain/1', 'nonce': 'a' * 64}
        domain = 'custody-domain-' + sha256_hex(canonical_json(body))
        (custody / 'custody-domain.json').write_bytes(canonical_json({**body, 'custody_domain_id': domain}))
        (custody / 'custody-domain.json').chmod(0o600)
        doc = {'schema_version': shared.SCHEMA, 'cli': CLI,
               'cli_sha256': sha256_hex(Path(CLI).read_bytes()),
               'home': str(self.root / 'shared-home'), 'home_id': 'fixture-home',
               'caller_id': 'caplab', 'custody_domain_id': domain,
               'binding_id': 'bnd-' + '8' * 64, **self.paths}
        for name in ('release', 'overlay', 'policy'):
            doc[name + '_sha256'] = sha256_hex(Path(doc[name + '_path']).read_bytes())
        profile = {'schema_version': 'caplab-pool-configured-profile/1',
                   'profile_id': 'caplab-codex-main', 'host': 'fixture-host',
                   'account_id': 'codex-main', 'config_home': None}
        doc['credential_profile_sha256'] = sha256_hex(canonical_json(profile))
        self.enrollment = shared.SharedAdmissionEnrollment(doc)
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()
        self.binary = self.workspace / 'codex'
        self.binary.write_text('#!/bin/sh\nprintf \'{"verdict":"clean"}\\n\'\n')
        self.binary.chmod(0o700)
        self.adapter = {'command': ['codex', 'exec', '-m', 'gpt-5.6-terra', '-c',
                                    'model_reasoning_effort=max'],
                        'version_command': ['codex', '--version'], 'prompt_mode': 'stdin'}
        self.declaration = {'id': self.paths['entry'], 'runtime_id': 'codex',
                            'status': 'enabled', 'adapter': self.adapter}
        self.deadline = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=3)).isoformat().replace('+00:00', 'Z')
        self.environment = mock.patch.dict(os.environ, {'PATH': str(self.workspace) + ':/usr/bin:/bin'})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def controller(self):
        from caplab.advisory.shared_admission import PoolAdmission
        return PoolAdmission(self.enrollment, self.declaration, self.out, self.deadline,
                             Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json')

    def invoke(self, controller=None, key='case:control:1', timeout=20):
        return pool_runner.invoke(self.adapter, 'local fixture', timeout,
                                  workspace=str(self.workspace),
                                  admission=controller or self.controller(), launch_key=key)

    def snapshot(self):
        return json.loads(subprocess.check_output([CLI, 'admission', 'status', '--home',
                            str(self.root / 'shared-home'), '--home-id', 'fixture-home', '--now', shared._now()]))

    def assert_accounting(self, spent, slots=0, outstanding=0):
        self.assertEqual(self.snapshot()['pools']['fixture-pool'], {
            'slots': slots, 'windows': {'fixture-window': {'spent': spent, 'outstanding': outstanding}}})

    def test_fast_child_settles_and_restart_refuses_same_assignment(self):
        result = self.invoke()
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['doc'], {'verdict': 'clean'})
        self.assertEqual(result['shared_admission']['status'], 'settled')
        self.assert_accounting(1)
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'assigned_launch_exists'):
            self.invoke(self.controller())
        self.assert_accounting(1)

    def test_child_side_exec_failure_counts_created_outer(self):
        self.binary.write_text('#!/bin/sh\nexec /does/not/exist\n')
        result = self.invoke()
        self.assertNotEqual(result['exit_code'], 0)
        self.assert_accounting(1)

    def test_expiry_before_popen_retirement_is_zero(self):
        self.deadline = '2026-01-02T00:00:00Z'
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'deadline_expired'):
            self.invoke()
        self.assertFalse((self.root / 'shared-home').exists())

    def test_unavailable_pidfd_keeps_created_charge_and_slot(self):
        with mock.patch('os.pidfd_open', side_effect=PermissionError('fixture kernel refusal')):
            with self.assertRaises(ValueError):
                self.invoke()
        self.assert_accounting(1, slots=1)
        result = self.controller().reconcile()
        self.assertEqual(result[0]['code'], 'namespace_quiescence_unproved')
        self.assert_accounting(1, slots=1)

    def test_budget_refusal_cannot_create_third_child(self):
        self.invoke(key='a')
        self.invoke(key='b')
        result = self.invoke(key='c')
        self.assertIsNone(result['exit_code'])
        self.assertIn('refused', result['error'])
        self.assert_accounting(2)

    def test_profile_or_declaration_drift_refuses_before_home_mutation(self):
        self.declaration['adapter']['command'].append('--other-model')
        with self.assertRaises(ValueError):
            self.controller()
        self.assertFalse((self.root / 'shared-home').exists())

    def test_legacy_invocation_has_no_shared_sidecars(self):
        result = pool_runner.invoke(self.adapter, 'fixture', 20, workspace=str(self.workspace))
        self.assertEqual(result['doc'], {'verdict': 'clean'})
        self.assertNotIn('shared_admission', result)
        self.assertFalse((self.root / 'shared-home').exists())

    def test_admission_consumes_native_deadline_and_returns_unused_right(self):
        result = self.invoke(timeout=0.001)
        self.assertIsNone(result['exit_code'])
        self.assertIn('deadline expired', result['error'])
        self.assert_accounting(0)
        completion = json.loads(Path(result['custody_path'], 'completion.json').read_bytes())
        self.assertIsNone(completion['launch_attempted_at'])

    def test_popen_failure_is_uncertain_not_positive_noncreation(self):
        real = subprocess.Popen
        def failing_bwrap(argv, *args, **kwargs):
            if argv[0] == '/usr/bin/bwrap':
                raise FileNotFoundError('fixture constructor/exec boundary uncertainty')
            return real(argv, *args, **kwargs)
        with mock.patch.object(subprocess, 'Popen', side_effect=failing_bwrap):
            with self.assertRaises(FileNotFoundError):
                self.invoke()
        self.assert_accounting(0, slots=1, outstanding=1)
        self.assertEqual(self.controller().reconcile()[0]['code'], 'creation_or_time_unresolved')
        self.assert_accounting(0, slots=1, outstanding=1)

    def test_prepare_commit_lost_reply_retires_closed_unlaunched_right(self):
        real = subprocess.run
        def lose_prepare_reply(argv, *args, **kwargs):
            result = real(argv, *args, **kwargs)
            if argv[:3] == [CLI, 'admission', 'prepare-launch']:
                raise subprocess.TimeoutExpired(argv, 60)
            return result
        with mock.patch.object(subprocess, 'run', side_effect=lose_prepare_reply):
            with self.assertRaises(shared.SharedAdmissionControlError):
                self.invoke()
        self.assert_accounting(0)
        first = self.controller().reconcile()
        self.assertIn(first[0]['status'], {'settled', 'existing'})
        records = self.snapshot()['records']
        self.controller().reconcile()
        self.assertEqual(self.snapshot()['records'], records)

    def test_background_descendant_closure_uses_held_init(self):
        self.binary.write_text('#!/bin/sh\n/bin/sleep 20 &\nprintf \'{"verdict":"clean"}\\n\'\n')
        result = self.invoke()
        self.assertEqual(result['exit_code'], 0)
        self.assert_accounting(1)
        closure = json.loads(Path(result['custody_path'], 'shared-admission-namespace-closure.json').read_bytes())
        self.assertEqual(closure['basis'], 'owned-namespace-init-pidfd-death')

    def test_two_handles_race_for_one_assignment_only_one_creates(self):
        from concurrent.futures import ThreadPoolExecutor
        import threading
        controllers = [self.controller(), self.controller()]
        barrier = threading.Barrier(2)
        def contender(controller):
            barrier.wait(timeout=5)
            try:
                return self.invoke(controller)
            except LiveExecutionCustodyError as error:
                return str(error)
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(contender, controllers))
        self.assertEqual(sum(isinstance(r, dict) and r['exit_code'] == 0 for r in results), 1)
        self.assertEqual(sum(isinstance(r, str) and 'assigned_launch_exists' in r for r in results), 1)
        self.assert_accounting(1)

    def test_real_matched_pair_entry_assigns_both_arms(self):
        from tests.test_advisory_tree_v1 import TreeModeMeasureCaseTest
        BODY = TreeModeMeasureCaseTest.PROSE
        CASE = {'substrate_id': 'fixture-doc', 'seed': 3, 'operator': 'truncated_tail',
                'source': {'kind': 'repo-doc'}}
        controller = self.controller()
        case_root = self.workspace / 'fixture-doc-truncated_tail-3'
        case_root.mkdir()
        binary = case_root / 'codex'
        binary.write_bytes(self.binary.read_bytes())
        binary.chmod(0o700)
        with mock.patch.dict(os.environ, {'PATH': str(case_root) + ':/usr/bin:/bin'}), \
                mock.patch.object(pool_runner, 'ENVIRONMENT_VERSION', 'iso-v1'):
            row = pool_runner.measure_case(CASE, BODY, self.adapter, 20,
                    workspace=str(self.workspace), admission=controller, assignment_prefix='fixture-frozen-spec')
        self.assertEqual(row['environment'], 'iso-v1-held-pid1-v1')
        self.assertEqual(row['control_attempts'][0]['exit_code'], 0)
        self.assertEqual(row['mutant_attempts'][0]['exit_code'], 0)
        self.assert_accounting(2)
        intents = [json.loads(path.read_bytes()) for path in (self.out / 'shared-launches').glob('*/intent.json')]
        self.assertEqual({json.loads(i['assignment'])[2] for i in intents}, {'control', 'mutant'})

    def test_reconciliation_refuses_changed_completion_preimage(self):
        result = self.invoke()
        path = Path(result['custody_path'], 'stdout')
        path.write_bytes(b'tampered fixture output')
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'completion_changed'):
            self.controller().reconcile()
        self.assert_accounting(1)

    def test_no_namespace_fallback_when_sandbox_is_disabled(self):
        with mock.patch.dict(os.environ, {'CAPLAB_NO_SANDBOX': '1'}):
            with self.assertRaisesRegex(LiveExecutionCustodyError, 'containment_required'):
                self.invoke()
        self.assertFalse((self.root / 'shared-home').exists())

    def test_custody_metadata_is_masked_from_the_native_application(self):
        self.binary.write_text('#!/bin/sh\ntest ! -f ' + str(self.out / 'shared-launches/pool-enrollment.json') + '\n')
        result = self.invoke()
        self.assertEqual(result['exit_code'], 0)
        self.assertTrue((self.out / 'shared-launches/pool-enrollment.json').exists())
        self.assert_accounting(1)

    def test_public_configuration_and_expired_recovery_do_not_relaunch(self):
        from caplab.advisory.shared_admission import PoolAdmission, SCHEMA
        from caplab.advisory.run_spec import declaration_digest
        enrollment_path = self.root / 'enrollment.json'
        enrollment_path.write_bytes(canonical_json(self.enrollment.document))
        config_path = self.root / 'pool-config.json'
        config = {'schema_version': SCHEMA, 'enrollment_path': str(enrollment_path),
                  'enrollment_sha256': sha256_hex(enrollment_path.read_bytes()),
                  'declaration_sha256': declaration_digest(self.declaration),
                  'valid_until': self.deadline,
                  'native_policy_path': str(Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json')}
        config_path.write_bytes(canonical_json(config))
        controller = PoolAdmission.read(config_path, self.declaration, self.out)
        self.invoke(controller)
        # A future wall-clock read is an OS clock boundary; recovery keeps the
        # exact original enrollment expiry and facts, never a renewed permit.
        import caplab.advisory.shared_admission as pool_shared
        real = datetime.datetime
        class Later(real):
            @classmethod
            def now(cls, tz=None):
                return real.fromisoformat(config['valid_until']) + datetime.timedelta(seconds=1)
        with mock.patch.object(pool_shared, 'datetime', Later):
            recovered = PoolAdmission.read(config_path, self.declaration, self.out, recovery=True)
            self.assertIn(recovered.reconcile()[0]['status'], {'settled', 'existing'})
            with self.assertRaisesRegex(LiveExecutionCustodyError, 'deadline_expired'):
                self.invoke(recovered, key='new-slot')
        self.assert_accounting(1)
