"""Local commands in genuine namespaces and private deployed SDK homes.

These controls verify launch administration, not model/harness qualification.
"""
import datetime
import contextlib
import json
import os
import subprocess
import signal
import sys
import time
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from caplab.revbench import shared_admission as sdk
from caplab.runtime.canonical import canonical_json, sha256_hex
import test_shared_admission as sdk_fixture

CLI = os.environ.get('CAPLAB_TEST_SHARED_QM')


@unittest.skipUnless(CLI, 'requires deployed interval/reconciliation SDK')
class NativeCalibrationAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.custody = self.root / 'custody'
        self.custody.mkdir(mode=0o700)
        from caplab.runtime.native_admission import initialize_domain
        domain = initialize_domain(self.custody)
        paths = sdk_fixture.fixture(self.root, CLI)
        self.deadline = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=3)).isoformat()
        self.manifest = {'manifest_sha256': '1' * 64, '_verified_manifest_sha256': '1' * 64,
            'campaign_id': 'private-native-administration-fixture', 'expires_at': self.deadline,
            'storage': {'raw_custody_root': str(self.custody)},
            '_instrument': {'agent_systems': {'fable': {'tuple_id': 'local-fable'},
                                            'gpt': {'tuple_id': 'local-gpt'}}}}
        mappings = []
        from caplab.preference.native_live import _CLAUDE_CONFIG, _CODEX_CONFIG
        homes = {'fable': str(_CLAUDE_CONFIG), 'gpt': str(_CODEX_CONFIG), 'platform': None}
        for subject in ('fable', 'gpt', 'platform'):
            profile = {'schema_version': 'caplab-native-declared-profile/1',
                       'profile_id': 'caplab-codex-main', 'host': 'fixture-host',
                       'account_id': 'codex-main', 'config_home': None,
                       'native_config_home': homes[subject]}
            doc = {'schema_version': sdk.PINNED_SCHEMA, 'cli': CLI,
                   'cli_sha256': sha256_hex(Path(CLI).read_bytes()),
                   'sdk_source_tree_sha256': 'sha256:af3621e6ddd0062cbc46ec5e37bb3c31f8321dd88a4024a8495055aac6bfa247',
                   'home': str(self.root / 'shared-home'), 'home_id': 'fixture-home',
                   'caller_id': 'caplab', 'custody_domain_id': domain,
                   'binding_id': 'platform' if subject == 'platform' else 'local-' + subject,
                   **paths, 'credential_profile_sha256': sha256_hex(canonical_json(profile))}
            for key in ('release', 'overlay', 'policy'):
                doc[key + '_sha256'] = sha256_hex(Path(doc[key + '_path']).read_bytes())
            path = self.root / (subject + '.json')
            path.write_bytes(canonical_json(doc))
            mappings.append({'subject_id': subject, 'native_config_home': homes[subject],
                             'enrollment_path': str(path), 'enrollment_sha256': sha256_hex(path.read_bytes())})
        self.config = self.root / 'config.json'
        self.config.write_bytes(canonical_json({'schema_version': 'caplab-native-shared-admission/1',
            'family': 'preference', 'manifest_sha256': self.manifest['manifest_sha256'], 'subjects': mappings}))
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()

    def budget(self, limit):
        path = self.root / 'policy.json'
        d = json.loads(path.read_bytes())
        w = d['launch_budgets'][0]['windows'][0]
        w['limit'] = w['caller_limits']['caplab'] = w['caller_limits']['other'] = limit
        path.write_bytes(canonical_json(d))
        self.repin()

    def repin(self):
        c = json.loads(self.config.read_bytes())
        for row in c['subjects']:
            p = Path(row['enrollment_path'])
            d = json.loads(p.read_bytes())
            d['policy_sha256'] = sha256_hex(Path(d['policy_path']).read_bytes())
            p.write_bytes(canonical_json(d))
            row['enrollment_sha256'] = sha256_hex(p.read_bytes())
        self.config.write_bytes(canonical_json(c))

    def controller(self):
        from caplab.runtime.native_admission import NativeCalibrationAdmission
        return NativeCalibrationAdmission.read(self.config, self.manifest, family='preference')

    def command(self, program):
        return ['/usr/bin/bwrap', '--unshare-all', '--new-session', '--die-with-parent',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/bin', '/bin', '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev',
            '--tmpfs', '/tmp', '--bind', str(self.workspace), '/work', '--chdir', '/work',
            '--', '/usr/bin/python3', '-c', program]

    def status(self):
        return json.loads(subprocess.check_output([CLI, 'admission', 'status', '--home',
            str(self.root / 'shared-home'), '--home-id', 'fixture-home', '--now', sdk._now()]))

    def test_completed_helper_replays_exact_bytes_without_child_or_ledger_event(self):
        command = self.command("from pathlib import Path; p=Path('/work/marker'); p.write_text(p.read_text()+'x' if p.exists() else 'x'); print('native output')")
        result = self.controller().run(command, cwd=self.workspace, subject='fable', assignment='helper:version', timeout=30)
        self.assertEqual(result.stdout, b'native output\n')
        self.assertEqual((self.workspace / 'marker').read_text(), 'x')
        state = self.status()
        self.assertEqual(state['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 1, 'outstanding': 0}}})
        replay = self.controller().run(command, cwd=self.workspace, subject='fable', assignment='helper:version', timeout=30)
        self.assertEqual(replay.stdout, result.stdout)
        self.assertEqual((self.workspace / 'marker').read_text(), 'x')
        self.assertEqual(self.status()['records'], state['records'])

    def test_child_side_exec_failure_is_counted_and_exact_stderr_retained(self):
        result = self.controller().run(self.command("import os; os.execv('/absent', ['/absent'])"),
            cwd=self.workspace, subject='gpt', assignment='trial:exec-failure', timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'FileNotFoundError', result.stderr)
        self.assertEqual(self.status()['pools']['fixture-pool']['windows']['fixture-window'],
                         {'spent': 1, 'outstanding': 0})
        self.assertEqual(self.status()['pools']['fixture-pool']['slots'], 0)

    def test_constructor_uncertainty_retains_both_resources_and_refuses_retry(self):
        from caplab.revbench.custody import LiveExecutionCustodyError
        real = subprocess.Popen
        def uncertain(argv, *a, **kw):
            if argv[0] == '/usr/bin/bwrap':
                raise OSError('constructor outcome cannot prove noncreation')
            return real(argv, *a, **kw)
        command = self.command("print('never authorized')")
        with mock.patch.object(subprocess, 'Popen', side_effect=uncertain):
            with self.assertRaisesRegex(OSError, 'constructor outcome'):
                self.controller().run(command, cwd=self.workspace, subject='gpt', assignment='unknown', timeout=30)
        state = self.status()
        self.assertEqual(state['pools']['fixture-pool'], {'slots': 1,
            'windows': {'fixture-window': {'spent': 0, 'outstanding': 1}}})
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'unresolved_no_retry'):
            self.controller().run(command, cwd=self.workspace, subject='gpt', assignment='unknown', timeout=30)
        self.assertEqual(self.status()['records'], state['records'])

    def test_lost_prepare_reply_truthfully_retires_never_launched_right(self):
        from caplab.revbench.custody import LiveExecutionCustodyError
        real = subprocess.run
        def lost(argv, *a, **kw):
            result = real(argv, *a, **kw)
            if argv[:3] == [CLI, 'admission', 'prepare-launch']:
                raise subprocess.TimeoutExpired(argv, 60)
            return result
        with mock.patch.object(subprocess, 'run', side_effect=lost):
            with self.assertRaisesRegex(LiveExecutionCustodyError, 'transport_uncertain'):
                self.controller().run(self.command("print('not launched')"), cwd=self.workspace,
                    subject='gpt', assignment='lost-reply', timeout=30)
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 0, 'outstanding': 0}}})
        right = next((self.custody / 'shared-launches' / 'assignments').iterdir())
        self.assertFalse((right / 'possible-creation.json').exists())
        self.assertIsNone(json.loads((right / 'completion.json').read_bytes())['launch_attempted_at'])

    def test_budget_aggregates_declared_subjects_and_platform_refuses_third_child(self):
        from caplab.revbench.custody import LiveExecutionCustodyError
        for s in ('fable', 'gpt'):
            self.controller().run(self.command("print('local')"), cwd=self.workspace,
                subject=s, assignment='version', timeout=30)
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'shared_admission_refused'):
            self.controller().run(self.command("from pathlib import Path; Path('/work/third').touch()"),
                cwd=self.workspace, subject='platform', assignment='version', timeout=30)
        self.assertFalse((self.workspace / 'third').exists())
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 2, 'outstanding': 0}}})

    def test_retained_output_and_changed_command_refuse_before_ledger_mutation(self):
        from caplab.revbench.custody import LiveExecutionCustodyError
        command = self.command("print('original')")
        self.controller().run(command, cwd=self.workspace, subject='gpt', assignment='fixed', timeout=30)
        before = self.status()['records']
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'intent_changed'):
            self.controller().run(self.command("print('changed')"), cwd=self.workspace,
                subject='gpt', assignment='fixed', timeout=30)
        right = next((self.custody / 'shared-launches' / 'assignments').iterdir())
        (right / 'stdout').write_bytes(b'changed')
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'output_changed'):
            self.controller().run(command, cwd=self.workspace, subject='gpt', assignment='fixed', timeout=30)
        self.assertEqual(self.status()['records'], before)

    def test_native_preflight_covers_all_five_helpers_and_replays_across_scratch_paths(self):
        from caplab.preference import native_live as native
        self.budget(8)
        version = subprocess.check_output(['/usr/bin/bwrap', '--version']).decode().strip()
        self.manifest['runtime_versions'] = {'claude-code': 'local-claude-version',
            'codex': 'local-codex-version', 'bubblewrap': version}
        # Only the native harness command boundary is substituted: real local
        # processes/SDK/custody prove administration, never native qualification.
        def command_at(root, program):
            return [x.replace(str(self.workspace), str(root)) for x in self.command(program)]
        def version_probe(instrument, subject, root):
            value = 'local-claude-version' if subject == 'fable' else 'local-codex-version'
            return {'command': command_at(root, 'print(' + repr(value) + ')')}
        def auth(root, command):
            if 'claude' in command:
                program = "print('{\"loggedIn\":true,\"authMethod\":\"claude.ai\",\"apiProvider\":\"firstParty\",\"subscriptionType\":\"max\"}')"
            else:
                program = "import sys; print('Logged in using ChatGPT', file=sys.stderr)"
            return command_at(root, program)
        with mock.patch.object(native, 'build_contained_version_probe', side_effect=version_probe), \
             mock.patch.object(native, '_contained_command', side_effect=auth):
            first = native.preflight_native_runtime(self.manifest, shared_admission=self.controller())
            before = self.status()['records']
            second = native.preflight_native_runtime(self.manifest, shared_admission=self.controller())
        self.assertEqual(first, second)
        self.assertEqual(set(first), {'claude-code', 'codex', 'bubblewrap', 'claude-code-auth', 'codex-auth'})
        self.assertEqual(self.status()['records'], before)
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 5, 'outstanding': 0}}})

    def native_fixture(self, family):
        """Fresh local administration fixture; historical manifests stay untouched."""
        from caplab.preference import native_live as pref
        from caplab.review_dissent import native_live as review
        repo = Path(__file__).parents[1]
        study = repo / 'docs/product/studies' / ('preference-001' if family == 'preference' else 'review-dissent-001')
        d = json.loads((study / 'native-live-manifest.json').read_bytes())
        d.update(status='active', campaign_id='local-process-native-administration-' + family,
                 expires_at=self.deadline)
        d['storage']['raw_custody_root'] = str(self.custody)
        d['runtime_versions']['bubblewrap'] = subprocess.check_output(['/usr/bin/bwrap', '--version']).decode().strip()
        if family == 'preference':
            d['authority'] = 'adr-0041'
            d['containment']['source_sha256'] = sha256_hex(Path(pref.__file__).read_bytes())
            loader, module = pref.load_native_live_manifest, pref
        else:
            for key in ('runner_source', 'runtime_source'):
                d['containment'][key]['sha256'] = sha256_hex((repo / d['containment'][key]['path']).read_bytes())
            loader, module = review.load_native_review_live_manifest, review
        d.pop('manifest_sha256')
        d['manifest_sha256'] = module._digest(d)
        path = self.root / 'manifest.json'
        path.write_text(json.dumps(d))
        self.manifest = loader(path, study / 'native-instrument.json', source_root=repo)
        # Actual catalog joins for both native tuples, conservatively aggregated
        # into the same private finite pool; no provider identity is inferred.
        source = json.loads((self.root / 'source.json').read_bytes())
        source['accounts'].append({'id': 'claude-main', 'provider': 'anthropic',
            'billing': 'subscription', 'quota_pool_ids': ['fixture-pool']})
        source['routes'].append({'id': 'fable', 'provider': 'anthropic', 'harness': 'claude',
            'model': 'claude-fable-5', 'family': 'claude', 'efforts': ['max'],
            'billing': 'subscription', 'account_ids': ['claude-main']})
        source['profiles'].append({'id': 'caplab-claude-main', 'host': 'fixture-host',
            'consumer': 'caplab', 'account_id': 'claude-main', 'config_home': None, 'credential_ref': None})
        (self.root / 'source.json').write_bytes(canonical_json(source))
        release = json.loads(subprocess.check_output([CLI, 'catalog', 'publish', str(self.root / 'source.json'),
            '--releases', str(self.root / 'releases'), '--publisher', 'local-fixture']))['path']
        overlay = json.loads((self.root / 'overlay.json').read_bytes())
        overlay['harnesses']['claude'] = {'efforts': ['max'], 'native': {'native_harness_id': 'claude-code',
            'executable': 'claude', 'required_command_tokens': ['-p', '--model', '@model@', '--effort', '@effort@'],
            'version_command': ['claude', '--version'], 'config_home': None}}
        overlay['selections'].append({'id': 'fixture-fable', 'route': 'fable', 'account': 'claude-main',
            'effort': 'max', 'profile': 'caplab-claude-main', 'release': None, 'enabled': True,
            'roles': [], 'controls': {'reason': 'provider-free native administration fixture'}})
        (self.root / 'overlay.json').write_bytes(canonical_json(overlay))
        entries = json.loads(subprocess.check_output([CLI, 'catalog', 'project', release,
            str(self.root / 'overlay.json')]))['entries']
        observed = json.loads((self.root / 'observations.json').read_bytes())
        added = json.loads(canonical_json(observed[0]))
        added['subject']['source_id'] = 'agent-usage:claude-main'
        added['payload']['catalog_account_id'] = 'claude-main'
        for row in [*observed, added]:
            row['payload']['catalog_release_id'] = json.loads(Path(release).read_bytes())['release_id']
            row.pop('_content_hash')
            row['_content_hash'] = 'sha256:' + sha256_hex(canonical_json(row))
        (self.root / 'observations.json').write_bytes(canonical_json([*observed, added]))
        policy = json.loads((self.root / 'policy.json').read_bytes())
        policy['pools'][0]['scope']['account_ids'].append('claude-main')
        (self.root / 'policy.json').write_bytes(canonical_json(policy))
        config = json.loads(self.config.read_bytes())
        config.update(family=family, manifest_sha256=d['manifest_sha256'])
        for row in config['subjects']:
            p = Path(row['enrollment_path'])
            e = json.loads(p.read_bytes())
            e['release_path'] = release
            e['release_sha256'] = sha256_hex(Path(release).read_bytes())
            e['overlay_sha256'] = sha256_hex((self.root / 'overlay.json').read_bytes())
            if row['subject_id'] != 'platform':
                e['binding_id'] = self.manifest['_instrument']['agent_systems'][row['subject_id']]['tuple_id']
            if row['subject_id'] == 'fable':
                e['entry'] = next(x['key'] for x in entries if x['route_id'] == 'fable')
                profile = {'schema_version': 'caplab-native-declared-profile/1',
                    'profile_id': 'caplab-claude-main', 'host': 'fixture-host',
                    'account_id': 'claude-main', 'config_home': None,
                    'native_config_home': row['native_config_home']}
                e['credential_profile_sha256'] = sha256_hex(canonical_json(profile))
            p.write_bytes(canonical_json(e))
            row['enrollment_sha256'] = sha256_hex(p.read_bytes())
        self.config.write_bytes(canonical_json(config))
        self.budget(20)
        return module

    @contextlib.contextmanager
    def local_harness_boundary(self, module):
        from caplab.preference import native_live as pref
        def at(root, program):
            return [x.replace(str(self.workspace), str(root)) for x in self.command(program)]
        def version(instrument, subject, root):
            key = 'claude-code' if subject == 'fable' else 'codex'
            return {'command': at(root, 'print(' + repr(self.manifest['runtime_versions'][key]) + ')')}
        def auth(root, command):
            program = ("print('{\"loggedIn\":true,\"authMethod\":\"claude.ai\",\"apiProvider\":\"firstParty\",\"subscriptionType\":\"max\"}')"
                       if 'claude' in command else "import sys; print('Logged in using ChatGPT', file=sys.stderr)")
            return at(root, program)
        def trial(instrument, subject, task, root):
            return {'tuple_id': instrument['agent_systems'][subject]['tuple_id'],
                    'command': at(root, "import sys; print('local process failure'); sys.exit(7)")}
        name = 'build_contained_invocation' if module is pref else 'build_contained_review_invocation'
        with mock.patch.object(pref, 'build_contained_version_probe', side_effect=version), \
             mock.patch.object(pref, '_contained_command', side_effect=auth), \
             mock.patch.object(module, name, side_effect=trial):
            yield

    def test_preference_trial_recovers_crash_between_sdk_completion_and_native_publication(self):
        from caplab.preference import native_live as pref
        module = self.native_fixture('preference')
        real = pref._exclusive_bytes
        def cut(path, data):
            if path.name == 'native.stdout':
                raise OSError('native publication cut after genuine process completion')
            return real(path, data)
        with self.local_harness_boundary(module), mock.patch.object(pref, '_exclusive_bytes', side_effect=cut):
            with self.assertRaisesRegex(OSError, 'publication cut'):
                pref.execute_native_trial(self.manifest, slot_index=0, attempt_kind='primary',
                    prior_attempts=[], shared_admission=self.config)
        state = self.status()
        self.assertEqual(state['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 6, 'outstanding': 0}}})
        # Recovery has no substituted harness boundary; using the retained
        # command/output is necessary to avoid launching the real native agent.
        root = pref.execute_native_trial(self.manifest, slot_index=0, attempt_kind='primary',
            prior_attempts=[], shared_admission=self.config)
        self.assertEqual((root / 'native.stdout').read_bytes(), b'local process failure\n')
        completion = json.loads((root / 'completion.json').read_bytes())
        self.assertEqual(completion['return_code'], 7)
        self.assertEqual(json.loads((root / 'observation.json').read_bytes())['status'], 'harness_failure')
        self.assertEqual(self.status()['records'], state['records'])
        before = {p.name: p.read_bytes() for p in root.glob('*.json')}
        pref.execute_native_trial(self.manifest, slot_index=0, attempt_kind='primary',
            prior_attempts=[], shared_admission=self.config)
        self.assertEqual({p.name: p.read_bytes() for p in root.glob('*.json')}, before)
        self.assertEqual(self.status()['records'], state['records'])

    def test_review_trial_retains_unverified_model_stop_and_replays_native_failure(self):
        module = self.native_fixture('review-dissent')
        with self.local_harness_boundary(module):
            root = module.execute_native_review_trial(self.manifest, slot_index=0, attempt_kind='primary',
                prior_attempts=[], shared_admission=self.config)
        attempts = module.load_native_review_attempts(self.manifest)
        self.assertEqual(module.assess_native_review_attempts(self.manifest, attempts)['stop_reason'],
                         'native_review_model_identity_unavailable')
        self.assertEqual(json.loads((root / 'completion.json').read_bytes())['return_code'], 7)
        state = self.status()
        module.execute_native_review_trial(self.manifest, slot_index=0, attempt_kind='primary',
            prior_attempts=[], shared_admission=self.config)
        self.assertEqual(self.status()['records'], state['records'])
        from caplab.revbench.custody import LiveExecutionCustodyError
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'next_action_mismatch'):
            module.execute_native_review_trial(self.manifest, slot_index=0, attempt_kind='replacement',
                prior_attempts=attempts, shared_admission=self.config)
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 6, 'outstanding': 0}}})

    def test_missing_pidfd_witness_refuses_application_and_retains_unclosed_charge(self):
        from caplab.revbench.process_tree import ProcessProofUnavailable
        def refused(pid, *a):
            raise PermissionError('native pidfd observer refused')
        command = self.command("from pathlib import Path; Path('/work/refused-app').touch()")
        with mock.patch.object(os, 'pidfd_open', side_effect=refused):
            with self.assertRaisesRegex(ProcessProofUnavailable, 'readiness_identity_unavailable') as caught:
                self.controller().run(command, cwd=self.workspace, subject='gpt', assignment='pidfd-refused', timeout=30)
        self.assertIsInstance(caught.exception.__cause__, PermissionError)
        self.assertTrue(any('native_readiness_abort' in note for note in caught.exception.__notes__))
        self.assertFalse((self.workspace / 'refused-app').exists())
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 1,
            'windows': {'fixture-window': {'spent': 1, 'outstanding': 0}}})

    def test_supervisor_term_and_kill_before_release_cannot_run_application_or_replay(self):
        from caplab.revbench.process_tree import namespace_init
        from caplab.revbench.custody import LiveExecutionCustodyError
        manifest_path = self.root / 'worker-manifest.json'
        manifest_path.write_bytes(canonical_json(self.manifest))
        for sig in (signal.SIGTERM, signal.SIGKILL):
            with self.subTest(signal=sig.name):
                name = 'crash-' + sig.name
                cut = self.root / (name + '-cut')
                marker = self.workspace / name
                command = self.command("from pathlib import Path; Path('/work/" + name + "').touch()")
                worker = self.root / (name + '.py')
                worker.write_text('import json,pathlib,subprocess,time\n'
                    'from caplab.runtime.native_admission import NativeCalibrationAdmission\n'
                    'real=subprocess.run\n'
                    'def delayed(argv,*a,**kw):\n'
                    ' r=real(argv,*a,**kw)\n'
                    " if argv[1:3]==['admission','record-launch']:\n"
                    f'  pathlib.Path({str(cut)!r}).touch(); time.sleep(60)\n'
                    ' return r\nsubprocess.run=delayed\n'
                    f'c=NativeCalibrationAdmission.read(pathlib.Path({str(self.config)!r}),'
                    f'json.loads(pathlib.Path({str(manifest_path)!r}).read_bytes()),family="preference")\n'
                    f'c.run({command!r},cwd=pathlib.Path({str(self.workspace)!r}),subject="gpt",assignment={name!r},timeout=30)\n')
                child = subprocess.Popen([sys.executable, str(worker)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.addCleanup(lambda p=child: p.kill() if p.poll() is None else None)
                deadline = time.monotonic() + 20
                while not cut.exists() and child.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(cut.exists(), child.poll())
                control = self.controller()
                root = control.root / control._key('gpt', name)
                creation = json.loads((root / 'shared-admission-creation.json').read_bytes())
                init = namespace_init(creation['pid'], deadline=time.monotonic() + 2)
                self.assertIsNotNone(init)
                def cleanup(witness=init):
                    try:
                        if not witness.dead():
                            signal.pidfd_send_signal(witness.descriptor, signal.SIGKILL)
                    finally:
                        witness.close()
                self.addCleanup(cleanup)
                os.kill(child.pid, sig)
                child.communicate(timeout=5)
                self.assertTrue(init.dead(2000), 'owned namespace outlived actual supervisor death')
                self.assertFalse(marker.exists(), 'application released by block-writer EOF')
                self.assertFalse((root / 'completion.json').exists())
                before = self.status()['records']
                with self.assertRaisesRegex(LiveExecutionCustodyError, 'outcome_unresolved_no_retry'):
                    control.run(command, cwd=self.workspace, subject='gpt', assignment=name, timeout=30)
                self.assertEqual(self.status()['records'], before)
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 2,
            'windows': {'fixture-window': {'spent': 2, 'outstanding': 0}}})

    def test_review_public_cli_describes_and_reconciles_expired_without_launch_permission(self):
        module = self.native_fixture('review-dissent')
        repo = Path(__file__).parents[1]
        manifest = self.root / 'manifest.json'
        d = json.loads(manifest.read_bytes())
        d['expires_at'] = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=1)).isoformat()
        d.pop('manifest_sha256')
        d['manifest_sha256'] = module._digest(d)
        manifest.write_text(json.dumps(d))
        c = json.loads(self.config.read_bytes())
        c['manifest_sha256'] = d['manifest_sha256']
        self.config.write_bytes(canonical_json(c))
        prefix = [sys.executable, '-m', 'caplab.review_dissent.native_live', '--manifest', str(manifest),
            '--instrument', str(repo / 'docs/product/studies/review-dissent-001/native-instrument.json'),
            '--source-root', str(repo), '--shared-admission', str(self.config)]
        describe = subprocess.run([*prefix, 'admission-describe'], capture_output=True)
        self.assertEqual(describe.returncode, 0, describe.stderr)
        self.assertFalse(json.loads(describe.stdout)['authenticated_provider_identity'])
        reconcile = subprocess.run([*prefix, 'admission-reconcile'], capture_output=True)
        self.assertEqual(reconcile.returncode, 0, reconcile.stderr)
        self.assertEqual(json.loads(reconcile.stdout), [])
        run = subprocess.run([*prefix, 'run', '--slot-index', '0', '--attempt-kind', 'primary'], capture_output=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn(b'authorization_expired', run.stderr)
        self.assertFalse((self.root / 'shared-home').exists())
        self.assertFalse((self.custody / 'attempts').exists())

    def test_catalog_native_model_mismatch_refuses_before_any_account_reservation(self):
        from caplab.runtime.native_admission import load_native_admission
        from caplab.revbench.custody import LiveExecutionCustodyError
        self.native_fixture('preference')
        self.manifest['_instrument']['agent_systems']['gpt']['model_id'] = 'wrong-native-model'
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'native_catalog_tuple_mismatch'):
            load_native_admission(self.config, self.manifest, family='preference')
        self.assertFalse((self.root / 'shared-home').exists())

    def test_timeout_preserves_output_and_closes_real_namespace_descendant(self):
        command = self.command("import subprocess,sys,time; print('before timeout', flush=True); "
            "subprocess.Popen([sys.executable,'-c',\"import time; from pathlib import Path; time.sleep(30); Path('/work/late-child').touch()\"]); time.sleep(60)")
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            self.controller().run(command, cwd=self.workspace, subject='gpt', assignment='timeout', timeout=6)
        self.assertEqual(caught.exception.stdout, b'before timeout\n')
        self.assertFalse((self.workspace / 'late-child').exists())
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 1, 'outstanding': 0}}})
        c = self.controller().completion_for('gpt', 'timeout')
        self.assertTrue(c['timed_out'])
        self.assertTrue(c['outputs_complete'])

    def test_separate_handle_refuses_inflight_same_key_then_replays_completed_output(self):
        from caplab.revbench.custody import LiveExecutionCustodyError
        manifest = self.root / 'worker-manifest.json'
        manifest.write_bytes(canonical_json(self.manifest))
        command = self.command("import time; from pathlib import Path; "
            "p=Path('/work/one'); p.write_text(p.read_text()+'x' if p.exists() else 'x'); "
            "exec(\"while not Path('/work/finish').exists(): time.sleep(.01)\"); print('one launch')")
        worker = self.root / 'inflight-worker.py'
        worker.write_text('import json,pathlib\nfrom caplab.runtime.native_admission import NativeCalibrationAdmission\n'
            f'c=NativeCalibrationAdmission.read(pathlib.Path({str(self.config)!r}),'
            f'json.loads(pathlib.Path({str(manifest)!r}).read_bytes()),family="preference")\n'
            f'c.run({command!r},cwd=pathlib.Path({str(self.workspace)!r}),subject="gpt",assignment="inflight",timeout=30)\n')
        child = subprocess.Popen([sys.executable, str(worker)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: child.kill() if child.poll() is None else None)
        deadline = time.monotonic() + 20
        while not (self.workspace / 'one').exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue((self.workspace / 'one').exists(), child.poll())
        with self.assertRaisesRegex(LiveExecutionCustodyError, 'outcome_unresolved_no_retry'):
            self.controller().run(command, cwd=self.workspace, subject='gpt', assignment='inflight', timeout=30)
        self.assertEqual((self.workspace / 'one').read_text(), 'x')
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 1,
            'windows': {'fixture-window': {'spent': 1, 'outstanding': 0}}})
        (self.workspace / 'finish').touch()
        out, err = child.communicate(timeout=20)
        self.assertEqual(child.returncode, 0, (out, err))
        before = self.status()['records']
        result = self.controller().run(command, cwd=self.workspace, subject='gpt', assignment='inflight', timeout=30)
        self.assertEqual(result.stdout, b'one launch\n')
        self.assertEqual(self.status()['records'], before)
        self.assertEqual((self.workspace / 'one').read_text(), 'x')
        self.assertEqual(self.status()['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 1, 'outstanding': 0}}})

    def test_native_offset_expiry_preserves_instant_in_sdk_utc_deadline(self):
        # Native manifests accept aware ISO offsets. The SDK request must be
        # UTC Z without moving that accepted native deadline.
        expiry = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=20)).astimezone(
            datetime.timezone(datetime.timedelta(hours=1)))
        self.manifest['expires_at'] = expiry.isoformat()
        result = self.controller().run(self.command("print('offset accepted')"), cwd=self.workspace,
            subject='gpt', assignment='offset-expiry', timeout=30)
        self.assertEqual(result.stdout, b'offset accepted\n')
        state = self.status()
        allocation = next(iter(state['allocations'].values()))
        self.assertEqual(datetime.datetime.fromisoformat(allocation['request']['valid_until']), expiry)
        self.assertTrue(allocation['request']['valid_until'].endswith('Z'))
        self.assertEqual(state['pools']['fixture-pool'], {'slots': 0,
            'windows': {'fixture-window': {'spent': 1, 'outstanding': 0}}})
