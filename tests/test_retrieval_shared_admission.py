"""Provider-free retrieval commands, real bwrap custody and deployed SDK homes."""
import datetime
import json
import os
import signal
import time
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from caplab.retrieval import contracts, runner
from caplab.revbench import shared_admission as shared
from caplab.runtime.canonical import canonical_json, sha256_hex
import test_shared_admission as sdk_fixture
from tests.retrieval_support import make_spec, command_arm

CLI = os.environ.get('CAPLAB_TEST_SHARED_QM')


@unittest.skipUnless(CLI and Path('/usr/bin/bwrap').exists(), 'requires deployed SDK and real bwrap')
class RetrievalAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.script = self.root / 'retriever.py'
        self.marker = self.root / 'marker'
        self.script.write_text("import json,sys\nr=json.load(sys.stdin)\nprint(json.dumps({'schema_version':'caplab-retrieval-response/1','ranked_ids':['n-restart'],'delivered_ids':['n-restart']}))\n")
        self.spec = contracts.validate_spec(make_spec([command_arm('local', self.script)],
                 queries=[{'id': 'q', 'text': 'restart worker', 'relevant_ids': ['n-restart']}]))
        self.spec_path = self.root / 'spec.json'
        self.spec_path.write_bytes(contracts.canonical_json(self.spec))
        paths = sdk_fixture.fixture(self.root, CLI)
        self.custody = self.root / 'custody'
        self.custody.mkdir(mode=0o700)
        result = subprocess.run([sys.executable, '-m', 'caplab', 'retrieval', 'admission-domain',
                                 '--custody', str(self.custody)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        domain = json.loads(result.stdout)['custody_domain_id']
        profile = {'schema_version': 'caplab-retrieval-declared-profile/1',
                   'profile_id': 'caplab-codex-main', 'host': 'fixture-host',
                   'account_id': 'codex-main', 'config_home': None}
        doc = {'schema_version': shared.PINNED_SCHEMA, 'cli': CLI,
               'cli_sha256': sha256_hex(Path(CLI).read_bytes()),
               'sdk_source_tree_sha256': 'sha256:af3621e6ddd0062cbc46ec5e37bb3c31f8321dd88a4024a8495055aac6bfa247',
               'home': str(self.root / 'shared-home'), 'home_id': 'fixture-home',
               'caller_id': 'caplab', 'custody_domain_id': domain,
               'binding_id': 'local-retrieval-fixture', **paths,
               'credential_profile_sha256': sha256_hex(canonical_json(profile))}
        for key in ('release', 'overlay', 'policy'):
            doc[key + '_sha256'] = sha256_hex(Path(doc[key + '_path']).read_bytes())
        self.enrollment = self.root / 'enrollment.json'
        self.enrollment.write_bytes(canonical_json(doc))
        self.config = self.root / 'config.json'
        self.deadline = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=3)).isoformat().replace('+00:00', 'Z')
        self.write_config()

    def write_config(self):
        self.config.write_bytes(canonical_json({'schema_version': 'caplab-retrieval-shared-admission/1',
            'custody_root': str(self.custody), 'valid_until': self.deadline,
            'spec_sha256': contracts.spec_digest(self.spec),
            'arms': [{'arm_id': 'local', 'enrollment_path': str(self.enrollment),
                      'enrollment_sha256': sha256_hex(self.enrollment.read_bytes())}]}))

    def status(self):
        return json.loads(subprocess.check_output([CLI, 'admission', 'status', '--home',
             str(self.root / 'shared-home'), '--home-id', 'fixture-home', '--now', shared._now()]))

    def assert_accounting(self, spent, slots=0, outstanding=0):
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': slots,
            'windows': {'fixture-window': {'spent': spent, 'outstanding': outstanding}}})

    def run_enrolled(self, name='run'):
        return runner.run_experiment(self.spec, self.root / name, shared_admission=self.config)

    def test_public_enrolled_run_replays_outputs_without_child_or_charge(self):
        result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'complete')
        self.assert_accounting(1)
        provenance = json.loads((self.root / 'run' / 'plan.json').read_bytes())['provenance']['runner']
        self.assertIn('exec_gate', provenance['subprocess_sources'])
        self.assertTrue(all(n in sys.modules for n in provenance['modules']))
        before = self.status()['records']
        self.run_enrolled('read-again')
        self.assert_accounting(1)
        self.assertEqual(self.status()['records'], before)
        from caplab.retrieval.artifacts import verify_run
        verify_run(self.root / 'run')
        attempts = [json.loads(x) for x in (self.root / 'read-again' / 'attempts.jsonl').read_text().splitlines()]
        self.assertEqual(attempts[0]['observation']['shared_admission']['recovery_basis'], 'retained-completion')

    def test_exec_failure_counts_outer_and_preserves_retrieval_failure(self):
        self.script.write_text("import os\nos.execv('/does/not/exist', ['/does/not/exist'])\n")
        result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        self.assert_accounting(1)
        attempts = [json.loads(x) for x in (self.root / 'run' / 'attempts.jsonl').read_text().splitlines()]
        self.assertEqual(attempts[0]['error']['code'], 'nonzero_exit')
        self.assertIn(b'FileNotFoundError', next((self.custody / 'shared-launches' / 'assignments').iterdir()).joinpath('stderr').read_bytes())

    def test_three_assignments_budget_refuses_third_without_creation(self):
        self.spec['seeds'] = [0, 1, 2]
        self.write_config()
        result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        self.assert_accounting(2)
        roots = list((self.custody / 'shared-launches' / 'assignments').iterdir())
        self.assertEqual(sum((p / 'possible-creation.json').exists() for p in roots), 2)
        rows = [json.loads(x) for x in (self.root / 'run' / 'attempts.jsonl').read_text().splitlines()]
        self.assertEqual(rows[2]['error']['code'], 'shared_admission_refused')

    def test_lost_prepare_reply_closes_unused_right_without_child(self):
        real = subprocess.run
        def lost(argv, *args, **kwargs):
            result = real(argv, *args, **kwargs)
            if argv[:3] == [CLI, 'admission', 'prepare-launch']:
                raise subprocess.TimeoutExpired(argv, 60)
            return result
        with mock.patch.object(subprocess, 'run', side_effect=lost):
            result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        self.assert_accounting(0)
        root = next((self.custody / 'shared-launches' / 'assignments').iterdir())
        self.assertFalse((root / 'possible-creation.json').exists())
        self.assertIsNone(json.loads((root / 'completion.json').read_bytes())['launch_attempted_at'])

    def test_constructor_uncertainty_holds_and_replay_cannot_relaunch(self):
        real = subprocess.Popen
        def unavailable(argv, *args, **kwargs):
            if argv[0] == '/usr/bin/bwrap':
                raise FileNotFoundError('constructor/preexec boundary cannot prove no child')
            return real(argv, *args, **kwargs)
        with mock.patch.object(subprocess, 'Popen', side_effect=unavailable):
            self.run_enrolled()
        self.assert_accounting(0, 1, 1)
        before = self.status()['records']
        self.run_enrolled('resume')
        self.assert_accounting(0, 1, 1)
        self.assertEqual(self.status()['records'], before)

    def test_modified_retained_output_refuses_before_accounting_replay(self):
        self.run_enrolled()
        root = next((self.custody / 'shared-launches' / 'assignments').iterdir())
        (root / 'stdout').write_bytes(b'changed')
        before = self.status()['records']
        result = self.run_enrolled('changed')
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        self.assertEqual(self.status()['records'], before)
        row = json.loads((self.root / 'changed' / 'attempts.jsonl').read_text())
        self.assertIn('retained_output_changed', row['error']['message'])

    def test_timeout_terminates_descendant_and_settles_actual_launch(self):
        self.spec['timeout_seconds'] = 4
        self.write_config()
        self.script.write_text("import subprocess,time\nsubprocess.Popen(['/bin/sleep','60'])\ntime.sleep(60)\n")
        result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        row = json.loads((self.root / 'run' / 'attempts.jsonl').read_text())
        self.assertEqual(row['status'], 'timeout')
        self.assert_accounting(1)

    def test_expired_config_creates_no_shared_home(self):
        self.deadline = '2026-01-02T00:00:00Z'
        self.write_config()
        result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        self.assertFalse((self.root / 'shared-home').exists())

    def test_unenrolled_command_keeps_original_protocol_without_custody(self):
        result = runner.run_experiment(self.spec, self.root / 'legacy')
        self.assertEqual(result['report']['run']['status'], 'complete')
        self.assertFalse((self.root / 'shared-home').exists())
        self.assertFalse((self.custody / 'shared-launches' / 'assignments').exists())

    def test_cli_run_describe_and_reconcile_are_real_public_routes(self):
        for command in ('admission-describe', 'run', 'admission-reconcile'):
            argv = [sys.executable, '-m', 'caplab', 'retrieval', command,
                    '--spec', str(self.spec_path), '--shared-admission', str(self.config)]
            if command == 'run':
                argv += ['--output', str(self.root / 'cli-run')]
            result = subprocess.run(argv, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            response = json.loads(result.stdout)
            if command == 'admission-describe':
                self.assertEqual(response['local']['declared_account_id'], 'codex-main')
                self.assertFalse(response['local']['authenticated_provider_identity'])
        self.assert_accounting(1)

    def test_separate_processes_share_single_native_assignment(self):
        children = [subprocess.Popen([sys.executable, '-m', 'caplab', 'retrieval', 'run',
             '--spec', str(self.spec_path), '--shared-admission', str(self.config),
             '--output', str(self.root / ('caller-' + str(i)))], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    for i in range(2)]
        for child in children:
            self.addCleanup(lambda p=child: p.kill() if p.poll() is None else None)
        results = [p.communicate(timeout=30) for p in children]
        self.assertTrue(all(p.returncode in (0, 1) for p in children), results)
        self.assertGreaterEqual(sum(p.returncode == 0 for p in children), 1)
        self.assert_accounting(1)
        roots = list((self.custody / 'shared-launches' / 'assignments').iterdir())
        self.assertEqual(len(roots), 1)
        self.assertEqual(sum((p / 'shared-admission-creation.json').exists() for p in roots), 1)

    def test_pidfd_refusal_counts_child_but_keeps_concurrency(self):
        with mock.patch('os.pidfd_open', side_effect=PermissionError('local kernel refusal')):
            result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        self.assert_accounting(1, 1)
        root = next((self.custody / 'shared-launches' / 'assignments').iterdir())
        self.assertEqual(json.loads((root / 'completion.json').read_bytes())['invocation_state'], 'invoked')
        self.assertEqual(json.loads((root / 'stdout').read_bytes() or b'null'), None)
        before = self.status()['records']
        self.run_enrolled('refused-resume')
        self.assert_accounting(1, 1)
        self.assertEqual(self.status()['records'], before)

    def test_slow_admission_consumes_original_timeout_without_child(self):
        self.spec['timeout_seconds'] = 1
        self.write_config()
        real = subprocess.run
        def slow(argv, *args, **kwargs):
            result = real(argv, *args, **kwargs)
            if argv[:3] == [CLI, 'admission', 'capabilities']:
                time.sleep(1.1)
            return result
        with mock.patch.object(subprocess, 'run', side_effect=slow):
            self.run_enrolled()
        self.assert_accounting(0)
        root = next((self.custody / 'shared-launches' / 'assignments').iterdir())
        self.assertFalse((root / 'possible-creation.json').exists())

    def test_missing_arm_mapping_and_changed_spec_refuse_without_admission(self):
        config = json.loads(self.config.read_bytes())
        for replacement in ({**config, 'arms': []}, {**config, 'spec_sha256': 'sha256:' + '0' * 64}):
            self.config.write_bytes(canonical_json(replacement))
            with self.assertRaises(ValueError):
                self.run_enrolled()
            self.assertFalse((self.root / 'shared-home').exists())

    def test_sigkill_before_readiness_release_keeps_consumed_assignment_held(self):
        # Actual SDK record-launch commits; delay its reply in the supervisor,
        # while the real application is blocked. No protocol result is fabricated.
        self.script.write_text("from pathlib import Path\nPath('executed').write_text('actual application')\n")
        cut = self.root / 'cut'
        worker = self.root / 'worker.py'
        worker.write_text("import json,pathlib,subprocess,time\n"
            + "from caplab.retrieval.runner import run_experiment\n"
            + "real=subprocess.run\n"
            + "def delayed(argv,*a,**kw):\n"
            + " r=real(argv,*a,**kw)\n"
            + " if argv[1:3]==['admission','record-launch']:\n"
            + "  pathlib.Path(" + repr(str(cut)) + ").write_text('committed')\n  time.sleep(60)\n"
            + " return r\nsubprocess.run=delayed\n"
            + "run_experiment(json.loads(pathlib.Path(" + repr(str(self.spec_path)) + ").read_bytes()),"
            + "pathlib.Path(" + repr(str(self.root / 'crashed')) + "),shared_admission=pathlib.Path(" + repr(str(self.config)) + "))\n")
        child = subprocess.Popen([sys.executable, str(worker)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: child.kill() if child.poll() is None else None)
        deadline = time.monotonic() + 20
        while not cut.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(cut.exists(), child.poll())
        root = next((self.custody / 'shared-launches' / 'assignments').iterdir())
        creation = json.loads((root / 'shared-admission-creation.json').read_bytes())
        outer_fd = os.pidfd_open(creation['pid'])
        self.addCleanup(os.close, outer_fd)
        from caplab.revbench.process_tree import namespace_init
        init = namespace_init(creation['pid'], deadline=time.monotonic() + 2)
        self.assertIsNotNone(init, 'real blocked namespace init not observed')
        def cleanup_init():
            try:
                if not init.dead():
                    signal.pidfd_send_signal(init.descriptor, signal.SIGKILL)
            finally:
                init.close()
        self.addCleanup(cleanup_init)
        scratch = Path('/proc') / str(creation['pid']) / 'cwd'
        application_marker = scratch.resolve() / 'executed'
        child.kill()
        child.communicate(timeout=5)
        import select
        poller = select.poll(); poller.register(outer_fd, select.POLLIN)
        self.assertTrue(poller.poll(2000), 'owned outer survived actual supervisor SIGKILL')
        self.assertTrue(init.dead(2000), 'actual blocked namespace init survived supervisor death')
        self.assertFalse(application_marker.exists(), 'application released after supervisor death')
        self.assertFalse((root / 'completion.json').exists())
        self.assert_accounting(1, 1)
        before = self.status()['records']
        result = self.run_enrolled('crash-recovery')
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        self.assertEqual(self.status()['records'], before)
        self.assert_accounting(1, 1)

    def test_distinct_arms_aggregate_in_declared_shared_account_pool(self):
        second = {**self.spec['arms'][0], 'id': 'second'}
        self.spec['arms'].append(second)
        self.write_config()
        config = json.loads(self.config.read_bytes())
        config['arms'].append({**config['arms'][0], 'arm_id': 'second'})
        self.config.write_bytes(canonical_json(config))
        result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'complete')
        self.assert_accounting(2)
        allocations = list(self.status()['allocations'].values())
        self.assertEqual(len(allocations), 2)
        self.assertEqual({a['request']['account_id'] for a in allocations}, {'codex-main'})
        self.assertEqual(len({a['holder_id'] for a in allocations}), 2)

    def test_output_cap_preserves_native_error_and_counted_outer(self):
        self.script.write_text("import sys\nsys.stdout.buffer.write(b'x'*(17<<20))\n")
        result = self.run_enrolled()
        self.assertEqual(result['report']['run']['status'], 'completed_with_failures')
        row = json.loads((self.root / 'run' / 'attempts.jsonl').read_text())
        self.assertEqual(row['error']['code'], 'output_too_large')
        self.assertEqual(row['observation']['stdout_bytes'], runner.MAX_OUTPUT_BYTES)
        self.assert_accounting(1)
