"""Fabricated values exercise every retained surface; no native harness executes."""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from caplab.revbench.codex import ExactSecretStreamQuarantine
from caplab.task_capture import TaskCaptureError
from test_supervised_task_capture import retained_fixture


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/probe_cgroup_resource_limits.py'
spec = importlib.util.spec_from_file_location('guarded_mount_probe', SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
SECRET = b'fabricated-full-mount-secret-only'


class MountCaptureQuarantineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.descriptor = os.open(self.source, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, self.descriptor)
        info = os.fstat(self.descriptor)
        self.identity = {'source_root': '/scratch', 'source_dev': info.st_dev, 'source_ino': info.st_ino}

    def retain(self, name='retained', *, bytes_left=200000, **changes):
        options = dict(quarantine_factory=lambda: ExactSecretStreamQuarantine((SECRET,)))
        options.update(changes)
        return probe.retain_mount(self.descriptor, self.root / name, self.identity, bytes_left, 100, **options)

    def test_split_secret_cannot_be_retained_through_the_full_mount_path(self):
        raw = b'a' * 65530 + SECRET + b'trailer'
        (self.source / 'raw').write_bytes(raw)
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.retain()
        output = self.root / 'retained'
        self.assertFalse((output / 'inventory.json').exists())
        for path in output.iterdir():
            self.assertNotIn(SECRET, path.read_bytes())
        self.assertEqual((self.source / 'raw').read_bytes(), raw)
        self.assertEqual(os.fstat(self.descriptor).st_ino, self.identity['source_ino'])

    def test_identity_and_generated_names_are_checked_before_output_creation(self):
        (self.source / 'raw').write_bytes(b'safe')
        for index, secret in enumerate((SECRET, b'.inventory.pending')):
            self.identity['source_root'] = '/' + SECRET.decode() if index == 0 else '/scratch'
            name = str(index)
            with self.subTest(index=index), self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                self.retain(name, quarantine_factory=lambda: ExactSecretStreamQuarantine((secret,)))
            self.assertFalse((self.root / name).exists())

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'Bubblewrap required for isolated fixtures')
    def test_one_policy_covers_complete_safe_fixture_custody_for_both_layouts(self):
        for harness in ('codex', 'claude'):
            root = self.root / harness
            with self.subTest(harness=harness):
                report = retained_fixture(root, harness, 7,
                    quarantine_factory=lambda: ExactSecretStreamQuarantine((SECRET,)),
                    mount_retainer=probe.retain_mount)
                self.assertFalse(report['native_execution'])
                self.assertTrue(report['pairs']['tool_pairs_available'])
                probe.verify_retention(root, {'reports': [report['full_retention']]})
                self.assertEqual([i['source_root'] for i in report['full_retention']['inventories']], list(probe.MOUNTS))
                for path in root.rglob('*'):
                    if path.is_file():
                        self.assertNotIn(SECRET, path.read_bytes())

    @unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'Bubblewrap required for isolated fixtures')
    def test_each_capture_path_stops_without_secret_bytes_in_earlier_custody(self):
        for harness in ('codex', 'claude'):
            native_path = '/episode/codex/sessions/secret.bin' if harness == 'codex' else '/episode/claude/projects/secret.bin'
            cases = {'process': None, 'task': '/work/secret.bin', 'native': native_path,
                     'scratch': '/scratch/secret.bin', 'tmp': '/tmp/secret.bin',
                     'shm': '/dev/shm/secret.bin', 'unselected-runtime': '/episode/unselected.bin'}
            for stage, target in cases.items():
                root = self.root / (harness + '-' + stage)
                before = set(os.listdir('/proc/self/fd'))
                with self.subTest(harness=harness, stage=stage), self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                    retained_fixture(root, harness, 0,
                        quarantine_factory=lambda: ExactSecretStreamQuarantine((SECRET,)),
                        mount_retainer=probe.retain_mount,
                        extra_files={} if target is None else {target: b'prefix ' + SECRET + b' trailer'},
                        stdout_suffix=SECRET if target is None else b'')
                self.assertEqual(before, set(os.listdir('/proc/self/fd')))
                self.assertEqual((root / 'attempt/attempt.json').exists(), stage not in ('process', 'task'))
                self.assertEqual((root / 'collection/collection.json').exists(), stage not in ('process', 'task', 'native'))
                for name in ('attempt', 'collection', 'fixture-retained'):
                    for path in (root / name).rglob('*'):
                        self.assertNotIn(SECRET, os.fsencode(path))
                        if path.is_file():
                            self.assertNotIn(SECRET, path.read_bytes())

    def test_literal_names_and_symlink_targets_do_not_escape_through_metadata(self):
        for kind in ('name', 'link'):
            path = self.source / (SECRET.decode() if kind == 'name' else 'link')
            if kind == 'name':
                path.write_bytes(b'safe')
            else:
                path.symlink_to(SECRET.decode())
            with self.subTest(kind=kind), self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                self.retain(kind)
            self.assertFalse((self.root / kind / 'inventory.json').exists())
            path.unlink()

    def test_identity_is_snapshotted_before_policy_callbacks(self):
        original = dict(self.identity)
        (self.source / 'raw').write_bytes(b'\x00\xff' + SECRET[:-1])

        def factory():
            self.identity['source_root'] = '/' + SECRET.decode()
            return ExactSecretStreamQuarantine((SECRET,))

        self.retain(quarantine_factory=factory)
        receipt = json.loads((self.root / 'retained/inventory.json').read_bytes())
        self.assertEqual(receipt['descriptor_identity'], original)
        self.assertEqual(receipt['source_root'], original['source_root'])
        entry, = [e for e in receipt['entries'] if e['kind'] == 'file']
        self.assertEqual((self.root / 'retained' / entry['object']).read_bytes(), b'\x00\xff' + SECRET[:-1])

    def test_quota_abandons_overlap_and_preserves_borrowed_descriptor(self):
        (self.source / 'raw').write_bytes(b'123456')
        gates = []

        class Gate(ExactSecretStreamQuarantine):
            abandoned = False

            def abandon(self):
                super().abandon()
                self.abandoned = True

        def factory():
            gate = Gate((SECRET,))
            gates.append(gate)
            return gate

        before = set(os.listdir('/proc/self/fd'))
        with self.assertRaisesRegex(TaskCaptureError, 'task-byte-limit'):
            self.retain(bytes_left=4, quarantine_factory=factory)
        self.assertFalse((self.root / 'retained/inventory.json').exists())
        self.assertEqual(next((self.root / 'retained').glob('object-*')).read_bytes(), b'')
        self.assertTrue(all(gate.abandoned and gate.finish() == b'' for gate in gates))
        self.assertEqual(before, set(os.listdir('/proc/self/fd')))

    def test_receipt_policy_cleanup_failure_cannot_publish(self):
        (self.source / 'raw').write_bytes(b'safe')

        class Gate(ExactSecretStreamQuarantine):
            receipt = False

            def feed(self, raw):
                if raw == b'fixture namespace; not a host path':
                    self.receipt = True
                return super().feed(raw)

            def abandon(self):
                super().abandon()
                if self.receipt:
                    raise OSError('synthetic policy cleanup failure')

        before = set(os.listdir('/proc/self/fd'))
        with self.assertRaisesRegex(OSError, 'synthetic policy cleanup failure'):
            self.retain(quarantine_factory=lambda: Gate((SECRET,)))
        self.assertFalse((self.root / 'retained/inventory.json').exists())
        self.assertFalse((self.root / 'retained/.inventory.pending').exists())
        self.assertEqual(next((self.root / 'retained').glob('object-*')).read_bytes(), b'safe')
        self.assertEqual(before, set(os.listdir('/proc/self/fd')))


if __name__ == '__main__':
    unittest.main()
