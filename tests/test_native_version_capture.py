"""Real bubblewrap with new Python fixture executables, never native inference."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_runtime import prepare_native_runtime
from caplab.native_version_capture import NativeVersionCaptureLimits, capture_native_version

POLICY = Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'
LIMITS = NativeVersionCaptureLimits(100000, 100000, 10000, 3)


class NativeVersionCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @staticmethod
    def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

    def prepare(self, *, codex=False, code=None, namespace='/work'):
        self.task = self.root / 'task'; self.task.mkdir()
        (self.task / 'must-stay').write_text('original')
        self.preparation = self.root / 'prepared'
        plan = build_native_capture_invocation(POLICY, 'codex-terra-max' if codex else 'claude-fable-5-max',
            context=NativeCaptureContext(namespace, '/episode', b'NEVER SENT AS VERSION ARGV',
                None if codex else '11111111-2222-4333-8444-555555555555'))
        prepare_native_runtime(POLICY, plan, expected_invocation_sha256=plan['invocation_sha256'],
            task_root=self.task, output_dir=self.preparation)
        self.harness = self.root / 'harness'
        self.entry = self.harness / 'bin/codex.js' if codex else self.harness
        self.entry.parent.mkdir(parents=True, exist_ok=True)
        self.entry.write_text('#!/usr/bin/python3\n' + (code or "import sys;print('synthetic version');assert sys.argv[1:]==['--version']\n"))
        self.entry.chmod(0o700)
        self.prep_hash = self.digest(self.preparation / 'preparation.json')
        self.entry_hash = self.digest(self.entry)
        self.output = self.root / 'output'

    def capture(self, **kwargs):
        options = dict(expected_preparation_sha256=self.prep_hash, expected_entrypoint_sha256=self.entry_hash,
                       output_dir=self.output, limits=LIMITS)
        options.update(kwargs)
        return capture_native_version(POLICY, self.preparation, self.harness, **options)

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'requires Linux bubblewrap')
    def test_real_namespace_excludes_ambient_home_and_network_and_preserves_runtime_writes(self):
        host_network = Path('/proc/self/ns/net').readlink().as_posix()
        code = '''import json,os,sys
from pathlib import Path
assert sys.argv[1:]==['--version']
assert os.getcwd()=='/work'
assert not Path('/home/halbritt').exists()
assert not Path('/episode/preparation.json').exists()
assert not Path('/episode/prompt.bin').exists()
assert 'SYNTHETIC_AMBIENT_SECRET' not in os.environ
assert 'LD_PRELOAD' not in os.environ
assert os.environ['HOME']=='/episode/home'
try:
    Path('/work/must-stay').write_text('changed')
except OSError:
    pass
else:
    raise AssertionError('task was writable')
Path('/episode/claude/version-marker').write_bytes(b'caf\\xc3\\xa9')
print(json.dumps({'environment':dict(os.environ),'network':os.readlink('/proc/self/ns/net')}))
'''
        self.prepare(code=code)
        with patch.dict('os.environ', {'SYNTHETIC_AMBIENT_SECRET': 'fixture-only'}): report = self.capture()
        self.assertEqual(report['process']['return_code'], 0)
        observed = json.loads((self.output / 'process/native.stdout').read_bytes())
        self.assertNotEqual(observed['network'], host_network)
        self.assertEqual(observed['environment'], {'HOME': '/episode/home', 'PATH': '/toolbin:/usr/bin:/bin',
            'LANG': 'C.UTF-8', 'CLAUDE_CONFIG_DIR': '/episode/claude', 'PWD': '/work'})
        self.assertEqual((self.task / 'must-stay').read_text(), 'original')
        self.assertEqual((self.preparation / 'runtime/claude/version-marker').read_bytes(), 'café'.encode())
        self.assertIs(report['binding_complete'], False); self.assertIs(report['native_identity_verified'], False)
        self.assertEqual(report['process_capture_sha256'], self.digest(self.output / 'process/capture.json'))
        self.assertEqual(report['intent_sha256'], self.digest(self.output / 'intent.json'))
        self.assertEqual((self.output / 'preparation.json').read_bytes(), (self.preparation / 'preparation.json').read_bytes())
        intent = json.loads((self.output / 'intent.json').read_bytes())
        self.assertEqual(intent['environment'], {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'})
        self.assertEqual(intent['command'][intent['command'].index('--') + 1:], ['claude', '--version'])
        self.assertNotIn('NEVER SENT AS VERSION ARGV', intent['command'])
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'requires Linux bubblewrap')
    def test_codex_package_layout_is_mounted_and_only_version_is_run(self):
        self.prepare(codex=True, code="import os,sys;assert sys.argv[1:]==['--version'];assert os.environ['CODEX_HOME']=='/episode/codex';print('synthetic codex')\n")
        report = self.capture()
        self.assertEqual(report['process']['return_code'], 0)
        self.assertEqual((self.output / 'process/native.stdout').read_bytes(), b'synthetic codex\n')

    def test_bad_independent_anchors_refuse_before_creation_or_launch(self):
        self.prepare()
        for field in ('expected_preparation_sha256', 'expected_entrypoint_sha256'):
            with self.subTest(field=field), patch('caplab.native_version_capture.capture_process') as launch:
                with self.assertRaises(ValueError): self.capture(**{field: '0' * 64})
                launch.assert_not_called(); self.assertFalse(self.output.exists())

    def test_unsupported_namespace_is_not_silently_rewritten(self):
        self.prepare(namespace='/other')
        with self.assertRaisesRegex(ValueError, 'namespace paths'): self.capture()
        self.assertFalse(self.output.exists())

    def test_receipt_and_entrypoint_budgets_apply_before_launch(self):
        self.prepare()
        for limits in (NativeVersionCaptureLimits(1, 100000, 10000, 3), NativeVersionCaptureLimits(100000, 1, 10000, 3)):
            with self.subTest(limits=limits), patch('caplab.native_version_capture.capture_process') as launch:
                with self.assertRaises(ValueError): self.capture(limits=limits)
                launch.assert_not_called(); self.assertFalse(self.output.exists())

    def test_writable_source_or_output_overlap_is_rejected(self):
        self.prepare()
        for output in (self.task / 'output', self.preparation / 'output', self.harness / 'output', self.root):
            with self.subTest(output=output), self.assertRaises((ValueError, FileExistsError)):
                self.capture(output_dir=output)
        self.assertFalse(self.output.exists())

    def test_symlink_source_and_nonexecutable_entry_are_rejected(self):
        self.prepare()
        link = self.root / 'linked'; link.symlink_to(self.harness)
        original = self.harness; self.harness = link
        with self.assertRaisesRegex(ValueError, 'resolved'): self.capture()
        self.harness = original; self.entry.chmod(0o600)
        with self.assertRaisesRegex(ValueError, 'executable'): self.capture()

    def test_existing_output_is_not_reused(self):
        self.prepare(); self.output.mkdir(); (self.output / 'keep').write_text('keep')
        with self.assertRaises(FileExistsError): self.capture()
        self.assertEqual(list(self.output.iterdir()), [self.output / 'keep'])

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'requires Linux bubblewrap')
    def test_entrypoint_change_after_process_prevents_final_receipt(self):
        self.prepare()
        from caplab.native_version_capture import capture_process
        def execute_then_change(*args, **kwargs):
            result = capture_process(*args, **kwargs)
            self.entry.write_text('#!/usr/bin/python3\nprint("changed")\n')
            return result
        with patch('caplab.native_version_capture.capture_process', side_effect=execute_then_change):
            with self.assertRaisesRegex(ValueError, 'changed during'): self.capture()
        self.assertTrue((self.output / 'process/capture.json').exists())
        self.assertFalse((self.output / 'version.json').exists())

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'requires Linux bubblewrap')
    def test_timeout_retains_partial_outcome(self):
        self.prepare(code='import time;print("prefix",flush=True);time.sleep(2)\n')
        report = self.capture(limits=NativeVersionCaptureLimits(100000, 100000, 10000, 0.2))
        self.assertEqual(report['process']['termination'], 'timeout')
        self.assertFalse(report['process']['streams_complete'])

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'requires Linux bubblewrap')
    def test_byte_limit_stops_capture_without_a_success_claim(self):
        self.prepare(code='import os;os.write(1,b"x"*10000)\n')
        report = self.capture(limits=NativeVersionCaptureLimits(100000, 100000, 19, 3))
        self.assertEqual(report['process']['termination'], 'byte-limit')
        self.assertEqual(report['process']['retained_stream_bytes'], 19)
        self.assertFalse(report['process']['streams_complete'])

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'requires Linux bubblewrap')
    def test_nonzero_version_process_is_preserved(self):
        self.prepare(code='import sys;sys.stderr.write("synthetic refusal");sys.exit(3)\n')
        report = self.capture()
        self.assertEqual(report['process']['return_code'], 3)
        self.assertTrue(report['process']['streams_complete'])

    def test_invalid_limit_types_fail(self):
        for limits in ((True, 1, 1, 1), (1, 0, 1, 1), (1, 1, -1, 1), (1, 1, 1, True),
                       (1, 1, 1, float('nan')), (1, 1, 1, float('inf'))):
            with self.subTest(limits=limits), self.assertRaises(ValueError): NativeVersionCaptureLimits(*limits)


if __name__ == '__main__': unittest.main()
