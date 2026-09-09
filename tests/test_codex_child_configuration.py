"""Child expectations come from source preparation before any execution trace."""

from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import tempfile
import unittest

from caplab.codex_child_configuration import CodexChildSourceEvidence, prepare_codex_child_configuration
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation, _digest
from caplab.native_launch_configuration import NativeLaunchContext, build_native_launch_configuration


REPO = Path(__file__).resolve().parents[1]
POLICY = REPO / 'docs/product/contracts/native-agent-systems.json'
FIXTURES = REPO / 'tests/fixtures/codex-launcher-0.153.4'
PLATFORM = 'node_modules/@openai/codex-linux-x64'
BINARY = PLATFORM + '/vendor/x86_64-unknown-linux-musl/bin/codex'
OBSERVER = b'#!/usr/bin/python3\nimport json,os,sys\nprint(json.dumps({"command":sys.argv,"environment":dict(os.environ)}))\n'


class CodexChildConfigurationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'installation'
        for name, relative in [('codex.js', 'bin/codex.js'), ('package.json', 'package.json'),
                               ('platform-package.json', PLATFORM + '/package.json')]:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(FIXTURES / name, path)
        binary = self.root / BINARY
        binary.parent.mkdir(parents=True)
        binary.write_bytes(OBSERVER)
        binary.chmod(0o755)
        self.plan = build_native_capture_invocation(POLICY, 'codex-terra-max',
            context=NativeCaptureContext('/work', '/episode', 'Fixed café diagnostic.\n'.encode()))
        self.launch = build_native_launch_configuration(POLICY, self.plan,
            expected_invocation_sha256=self.plan['invocation_sha256'],
            context=NativeLaunchContext('codex-scripted-local/v1', 43129))
        self.evidence = CodexChildSourceEvidence(self.plan['invocation_sha256'],
            self.launch['launch_configuration_sha256'], hashlib.sha256(OBSERVER).hexdigest(), 1024 * 1024)

    def prepare(self, **changes):
        return prepare_codex_child_configuration(POLICY, self.plan, self.launch, self.root,
            evidence=replace(self.evidence, **changes))

    def test_prepares_independent_child_expectation_and_identifies_exact_source_bytes(self):
        before = deepcopy((self.plan, self.launch))
        prepared = self.prepare()
        executable = '/opt/native/' + BINARY
        self.assertEqual(prepared['executable'], executable)
        self.assertEqual(prepared['command'], [executable] + self.launch['command'][1:])
        self.assertEqual(prepared['environment'], self.launch['environment'] | {
            'CODEX_MANAGED_PACKAGE_ROOT': '/opt/native', 'CODEX_MANAGED_BY_NPM': '1'})
        self.assertEqual(prepared['source_files'][-1]['sha256'], hashlib.sha256(OBSERVER).hexdigest())
        self.assertTrue(prepared['selected_source_bytes_verified'])
        for key in ('namespace_assumptions_verified', 'execution_authorized', 'binding_complete', 'study_eligible'):
            self.assertFalse(prepared[key])
        self.assertEqual((self.plan, self.launch), before)
        self.assertEqual(self.prepare(), prepared)
        prepared['command'].append('mutated'); prepared['environment']['HOME'] = 'mutated'
        self.assertEqual((self.plan, self.launch), before)

    def test_real_launcher_agrees_with_preparation_for_both_launch_profiles(self):
        for profile, port in [('canonical-native/v1', None), ('codex-scripted-local/v1', 43129)]:
            with self.subTest(profile=profile):
                self.launch = build_native_launch_configuration(POLICY, self.plan,
                    expected_invocation_sha256=self.plan['invocation_sha256'],
                    context=NativeLaunchContext(profile, port))
                self.evidence = replace(self.evidence, expected_launch_sha256=self.launch['launch_configuration_sha256'])
                prepared = self.prepare()
                command = ['bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--cap-drop', 'ALL',
                    '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
                    '--symlink', 'usr/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
                    '--dir', '/opt', '--ro-bind', str(self.root), '/opt/native', '--dir', '/toolbin',
                    '--symlink', '/opt/native/bin/codex.js', '/toolbin/codex', '--dir', '/work', '--chdir', '/work',
                    '--clearenv']
                handoff = 'import json,os,sys;os.execvpe(sys.argv[2],sys.argv[2:],json.loads(sys.argv[1]))'
                command += ['/usr/bin/python3', '-c', handoff, json.dumps(self.launch['environment']),
                    '/usr/bin/node', '--max-old-space-size=64', '/toolbin/codex', *self.launch['command'][1:]]
                def limits():
                    resource.setrlimit(resource.RLIMIT_AS, (16 * 1024**3, 16 * 1024**3))
                    resource.setrlimit(resource.RLIMIT_FSIZE, (65536, 65536))
                    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                    completed = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=10, preexec_fn=limits)
                    stdout.seek(0); stderr.seek(0)
                    self.assertEqual(completed.returncode, 0, stderr.read(65537).decode())
                    raw = stdout.read(65537)
                    self.assertLessEqual(len(raw), 65536)
                    observed = json.loads(raw)
                self.assertEqual(observed['command'], prepared['command'])
                self.assertEqual(observed['environment'], prepared['environment'])

    def test_changed_sources_and_wrong_binary_anchor_refuse_without_leaking_descriptors(self):
        descriptors = set(os.listdir('/proc/self/fd'))
        for relative in ('bin/codex.js', 'package.json', PLATFORM + '/package.json', BINARY):
            path = self.root / relative
            original = path.read_bytes()
            with self.subTest(relative=relative):
                path.write_bytes(original + b' ')
                try:
                    with self.assertRaisesRegex(ValueError, 'unsupported or changed Codex source'):
                        self.prepare()
                finally:
                    path.write_bytes(original)
                self.assertEqual(set(os.listdir('/proc/self/fd')), descriptors)
        with self.assertRaisesRegex(ValueError, 'unsupported or changed Codex source'):
            self.prepare(expected_binary_sha256='0' * 64)
        self.assertEqual(set(os.listdir('/proc/self/fd')), descriptors)

    def test_source_reads_enforce_total_allowance_and_refuse_unsupported_objects(self):
        total = sum(row['bytes'] for row in self.prepare()['source_files'])
        self.assertEqual(self.prepare(max_installation_bytes=total)['source_files'][-1]['bytes'], len(OBSERVER))
        for allowance in (0, -1, True, 1.5, None, 1024**3 + 1, total - 1):
            with self.subTest(allowance=allowance), self.assertRaises(ValueError):
                self.prepare(max_installation_bytes=allowance)
        descriptors = set(os.listdir('/proc/self/fd'))
        for relative in ('bin', PLATFORM, BINARY):
            path = self.root / relative
            saved = path.with_name(path.name + '.saved')
            path.rename(saved)
            path.symlink_to(saved)
            try:
                with self.subTest(relative=relative), self.assertRaises(OSError):
                    self.prepare()
            finally:
                path.unlink(); saved.rename(path)
            self.assertEqual(set(os.listdir('/proc/self/fd')), descriptors)
        binary = self.root / BINARY
        binary.unlink(); os.mkfifo(binary)
        with self.assertRaisesRegex(ValueError, 'unsupported type'):
            self.prepare()
        self.assertEqual(set(os.listdir('/proc/self/fd')), descriptors)
        binary.unlink()
        with self.assertRaises(FileNotFoundError):
            self.prepare()
        self.assertEqual(set(os.listdir('/proc/self/fd')), descriptors)

    def test_launch_anchors_and_supported_profile_cannot_be_bypassed_by_rehashing(self):
        for changes in ({'expected_invocation_sha256': '0' * 64}, {'expected_launch_sha256': '0' * 64},
                        {'expected_binary_sha256': 'BAD'}, {'expected_binary_sha256': None}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.prepare(**changes)
        self.launch['environment']['NODE_OPTIONS'] = '--require=/tmp/other.js'
        self.launch['launch_configuration_sha256'] = _digest({
            k: v for k, v in self.launch.items() if k != 'launch_configuration_sha256'})
        with self.assertRaisesRegex(ValueError, 'declared profile'):
            self.prepare(expected_launch_sha256=self.launch['launch_configuration_sha256'])
        plan = build_native_capture_invocation(POLICY, 'claude-fable-5-max',
            context=NativeCaptureContext('/work', '/episode', b'Fixed diagnostic.',
                                         '11111111-2222-4333-8444-555555555555'))
        launch = build_native_launch_configuration(POLICY, plan,
            expected_invocation_sha256=plan['invocation_sha256'], context=NativeLaunchContext('canonical-native/v1'))
        with self.assertRaisesRegex(ValueError, 'requires Codex'):
            prepare_codex_child_configuration(POLICY, plan, launch, self.root,
                evidence=replace(self.evidence, expected_invocation_sha256=plan['invocation_sha256'],
                                 expected_launch_sha256=launch['launch_configuration_sha256']))

    def test_package_manager_metadata_and_unresolved_roots_refuse(self):
        marker = self.root / 'node_modules/.modules.yaml'
        marker.write_bytes(b'fabricated marker\n')
        with self.assertRaisesRegex(ValueError, 'ownership metadata'):
            self.prepare()
        marker.unlink(); marker.symlink_to('/does-not-exist')
        with self.assertRaisesRegex(ValueError, 'ownership metadata'):
            self.prepare()
        alias = self.root.with_name('alias'); alias.symlink_to(self.root)
        for root in (Path('relative'), Path('/'), alias):
            with self.subTest(root=root), self.assertRaisesRegex(ValueError, 'resolved absolute'):
                prepare_codex_child_configuration(POLICY, self.plan, self.launch, root, evidence=self.evidence)

    def test_explicit_binary_selection_changes_preparation_identity_without_claiming_native_execution(self):
        first = self.prepare()
        changed = OBSERVER + b'# separately selected fixture bytes\n'
        (self.root / BINARY).write_bytes(changed)
        second = self.prepare(expected_binary_sha256=hashlib.sha256(changed).hexdigest())
        self.assertNotEqual(first['child_configuration_sha256'], second['child_configuration_sha256'])
        self.assertEqual(first['command'], second['command'])
        self.assertFalse(second['executed_bytes_verified'])
        self.assertEqual(second['child_configuration_sha256'], _digest({
            key: value for key, value in second.items() if key != 'child_configuration_sha256'}))
