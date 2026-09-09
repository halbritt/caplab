"""Synthetic task trees and real local child processes exercise guarded custody."""

import hashlib
import base64
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from caplab.process_capture import capture_process
from caplab.revbench.codex import ExactSecretStreamQuarantine
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureError, TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import verify_task_capture


SECRET = b'fabricated-task-secret-only'


class Gate(ExactSecretStreamQuarantine):
    def __init__(self):
        super().__init__((SECRET,))
        self.abandoned = False

    def abandon(self):
        super().abandon()
        self.abandoned = True


class TaskCaptureQuarantineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.task = self.root / 'task'
        self.task.mkdir()
        self.gates = []
        self.limits = TaskCaptureLimits(200000, 400000, 100, 3)

    def factory(self):
        gate = Gate()
        self.gates.append(gate)
        return gate

    def command(self, code='pass'):
        return [sys.executable, '-B', '-c', code]

    def host(self, code='pass', name='host', **changes):
        options = dict(task_root=self.task, environment={}, output_dir=self.root / name,
                       limits=self.limits, quarantine_factory=self.factory)
        options.update(changes)
        return capture_task_attempt(self.command(code), **options)

    def recorder(self, code='pass', name='supervised', **changes):
        options = dict(task_root=self.task, namespace_root='/work', environment={},
                       output_dir=self.root / name, limits=self.limits,
                       max_process_receipt_bytes=100000, quarantine_factory=self.factory)
        options.update(changes)
        return SupervisedTaskCapture(self.command(code), **options)

    def before(self, recorder):
        descriptor = os.open(self.task, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, descriptor)
        info = os.fstat(descriptor)
        recorder.capture_before(descriptor, expected_device=info.st_dev, expected_inode=info.st_ino)
        return descriptor

    def process(self, code='pass', name='supervised'):
        root = self.root / name / 'process'
        capture_process(self.command(code), cwd=self.task, environment={}, output_dir=root,
                        max_stream_bytes=self.limits.max_stream_bytes,
                        timeout_seconds=self.limits.timeout_seconds, quarantine_factory=self.factory)
        return hashlib.sha256((root / 'capture.json').read_bytes()).hexdigest()

    def assert_no_secret(self, output):
        self.assertFalse((output / 'attempt.json').exists())
        for path in output.rglob('*'):
            self.assertNotIn(SECRET, os.fsencode(path))
            if path.is_file():
                self.assertNotIn(SECRET, path.read_bytes())
        self.assertTrue(all(gate.abandoned for gate in self.gates))

    def test_host_before_secret_prevents_process_launch(self):
        (self.task / 'input').write_bytes(b'a' * 65530 + SECRET)
        with patch('caplab.task_capture.capture_process') as launch:
            with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                self.host()
            launch.assert_not_called()
        self.assert_no_secret(self.root / 'host')

    def test_supervised_before_secret_prevents_release_and_recorder_reuse(self):
        (self.task / 'input').write_bytes(b'prefix ' + SECRET)
        descriptor = os.open(self.task, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, descriptor)
        info = os.fstat(descriptor)
        before = set(os.listdir('/proc/self/fd'))
        with self.assertRaisesRegex(TaskCaptureError, 'exited-without-finish'):
            with self.recorder() as recorder:
                with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                    recorder.capture_before(descriptor, expected_device=info.st_dev, expected_inode=info.st_ino)
                with self.assertRaisesRegex(TaskCaptureError, 'before-out-of-order'):
                    recorder.capture_before(descriptor, expected_device=info.st_dev, expected_inode=info.st_ino)
                with self.assertRaisesRegex(TaskCaptureError, 'finish-out-of-order'):
                    recorder.finish(expected_process_sha256='0' * 64)
        self.assertEqual(before, set(os.listdir('/proc/self/fd')))
        self.assertEqual(os.fstat(descriptor).st_ino, info.st_ino)
        self.assert_no_secret(self.root / 'supervised')

    def test_intent_secrets_are_rejected_before_custody_for_both_facades(self):
        for mode in ('host', 'supervised'):
            for surface in ('command', 'environment', 'raw-environment'):
                secret = SECRET if surface != 'raw-environment' else b'fabricated-env-\xff'
                factory = lambda: ExactSecretStreamQuarantine((secret,))
                name = mode + '-' + surface
                code = 'pass # ' + secret.decode() if surface == 'command' else 'pass'
                options = {'quarantine_factory': factory}
                if surface != 'command':
                    options['environment'] = {'FIXTURE': os.fsdecode(secret)}
                with self.subTest(mode=mode, surface=surface), self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                    if mode == 'host':
                        self.host(code, name, **options)
                    else:
                        with self.recorder(code, name, **options):
                            self.fail('secret-bearing intent was published')
                self.assertFalse((self.root / name).exists())

    def test_host_forwards_stream_policy_and_stops_before_after_snapshot(self):
        code = f'import os; os.write(1,bytes.fromhex({SECRET.hex()!r}))'
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            self.host(code)
        self.assertTrue((self.root / 'host/before/inventory.json').exists())
        self.assertFalse((self.root / 'host/process/capture.json').exists())
        self.assertFalse((self.root / 'host/after').exists())
        self.assert_no_secret(self.root / 'host')

    def test_process_receipt_is_checked_before_publication(self):
        secret = b'caplab.process-capture/v1'
        output = self.root / 'process'
        with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
            capture_process(self.command('print("safe output")'), cwd=self.task, environment={},
                            output_dir=output, max_stream_bytes=1000, timeout_seconds=3,
                            quarantine_factory=lambda: ExactSecretStreamQuarantine((secret,)))
        self.assertFalse((output / 'capture.json').exists())
        self.assertFalse((output / '.capture.pending').exists())
        self.assertEqual((output / 'native.stdout').read_bytes(), b'safe output\n')

    def test_after_secret_stops_both_facades_without_altering_task_source(self):
        code = f'from pathlib import Path; Path("result").write_bytes(bytes.fromhex({SECRET.hex()!r}))'
        for mode in ('host', 'supervised'):
            result = self.task / 'result'
            result.unlink(missing_ok=True)
            with self.subTest(mode=mode), self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                if mode == 'host':
                    self.host(code)
                else:
                    with self.recorder(code) as recorder:
                        descriptor = self.before(recorder)
                        recorder.finish(expected_process_sha256=self.process(code))
            self.assertEqual(result.read_bytes(), SECRET)
            self.assertTrue((self.root / mode / 'process/capture.json').exists())
            self.assertFalse((self.root / mode / 'after/inventory.json').exists())
            self.assert_no_secret(self.root / mode)
            if mode == 'supervised':
                self.assertEqual(os.fstat(descriptor).st_ino, self.task.stat().st_ino)
                with self.assertRaisesRegex(TaskCaptureError, 'cannot-be-reentered'):
                    recorder.__enter__()

    def test_safe_exact_budget_round_trips_through_both_verifier_versions(self):
        old = b'\x00\xffraw' + SECRET[:-1]
        new = b'\xffchanged' + SECRET[:-1]
        target = b'/missing-\xff'
        stdout, stderr = b'\x00\xff' + SECRET[:-1], b'failed-safe\n'
        self.limits = TaskCaptureLimits(len(stdout) + len(stderr), len(old) + len(new) + 2 * len(target), 6, 3)
        code = (f'from pathlib import Path; import os; Path("r\u00e9sum\u00e9").write_bytes({new!r}); '
                f'os.write(1,{stdout!r}); os.write(2,{stderr!r}); raise SystemExit(7)')
        os.symlink(target, self.task / 'link')
        for mode, version in (('host', 1), ('supervised', 2)):
            (self.task / 'r\u00e9sum\u00e9').write_bytes(old)
            with self.subTest(mode=mode):
                if mode == 'host':
                    receipt = self.host(code)
                else:
                    with self.recorder(code) as recorder:
                        descriptor = self.before(recorder)
                        process_anchor = self.process(code)
                        self.task.rename(self.root / 'moved-task')
                        receipt = recorder.finish(expected_process_sha256=process_anchor)
                    self.assertEqual(os.fstat(descriptor).st_ino, (self.root / 'moved-task').stat().st_ino)
                output = self.root / mode
                self.assertEqual(receipt['schema'], f'caplab.task-attempt-capture/v{version}')
                self.assertEqual(receipt['retained_task_bytes'], self.limits.max_task_bytes)
                self.assertEqual(receipt['retained_task_entries'], 6)
                report = verify_task_capture(output,
                    expected_attempt_sha256=hashlib.sha256((output / 'attempt.json').read_bytes()).hexdigest(),
                    max_receipt_bytes=100000)
                self.assertTrue(report['integrity_verified'])
                self.assertTrue(report['capture_complete'])
                self.assertEqual(report['return_code'], 7)
                self.assertEqual((output / 'process/native.stdout').read_bytes(), stdout)
                self.assertEqual((output / 'process/native.stderr').read_bytes(), stderr)
                for phase, expected in (('before', old), ('after', new)):
                    inventory = json.loads((output / phase / 'inventory.json').read_bytes())
                    entry, = [e for e in inventory['entries'] if e['kind'] == 'file']
                    self.assertEqual((output / phase / entry['object']).read_bytes(), expected)
                    link, = [e for e in inventory['entries'] if e['kind'] == 'symlink']
                    self.assertEqual(base64.b64decode(link['target_base64']), target)
                for path in output.rglob('*'):
                    self.assertEqual(path.stat().st_mode & 0o777, 0o700 if path.is_dir() else 0o600)
        self.assertTrue(all(gate.abandoned for gate in self.gates))

    def test_inventory_and_final_metadata_are_checked_for_both_facades(self):
        (self.task / 'safe').write_bytes(b'raw fixture')
        for mode, version in (('host', 1), ('supervised', 2)):
            for phase in ('inventory', 'attempt'):
                secret = (f'caplab.task-inventory/v{version}'.encode() if phase == 'inventory' else
                          b'observed final task changes' if mode == 'host' else
                          b'observed task changes through a retained descriptor')
                name = mode + '-' + phase
                factory = lambda: ExactSecretStreamQuarantine((secret,))
                with self.subTest(mode=mode, phase=phase), self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                    if mode == 'host':
                        self.host(name=name, quarantine_factory=factory)
                    else:
                        with self.recorder(name=name, quarantine_factory=factory) as recorder:
                            self.before(recorder)
                            recorder.finish(expected_process_sha256=self.process(name=name))
                output = self.root / name
                self.assertFalse((output / 'attempt.json').exists())
                self.assertFalse((output / '.attempt.pending').exists())
                self.assertEqual((output / 'before/inventory.json').exists(), phase == 'attempt')
                for path in output.rglob('*'):
                    if path.is_file():
                        self.assertNotIn(secret, path.read_bytes())

    def test_generated_paths_and_invalid_policy_refuse_before_custody(self):
        for mode in ('host', 'supervised'):
            for index, factory in enumerate((False, lambda: object(),
                    lambda: ExactSecretStreamQuarantine((b'.inventory.pending',)),
                    lambda: ExactSecretStreamQuarantine((b'process/native.stdout',)))):
                name = mode + str(index)
                recorder = None
                with self.subTest(mode=mode, index=index), self.assertRaises((ValueError, RuntimeError)):
                    if mode == 'host':
                        self.host(name=name, quarantine_factory=factory)
                    else:
                        recorder = self.recorder(name=name, quarantine_factory=factory)
                        with recorder:
                            self.fail('invalid policy or custody path was accepted')
                self.assertFalse((self.root / name).exists())
                if recorder is not None:
                    with self.assertRaisesRegex(TaskCaptureError, 'cannot-be-reentered'):
                        recorder.__enter__()

    def test_failure_reason_cannot_copy_a_secret_into_failure_receipt(self):
        (self.task / 'input').write_bytes(b'fail-fixture')
        read = os.read

        def failing_read(fd, count):
            raw = read(fd, count)
            if raw == b'fail-fixture':
                raise TaskCaptureError(SECRET.decode())
            return raw

        with patch('caplab.task_capture.os.read', side_effect=failing_read):
            with self.assertRaisesRegex(RuntimeError, '^capture output quarantined$'):
                self.host()
        self.assertFalse((self.root / 'host/failure.json').exists())
        self.assertFalse((self.root / 'host/.failure.pending').exists())
        self.assert_no_secret(self.root / 'host')

    def test_safe_quota_failure_keeps_phase_and_discards_incomplete_overlap(self):
        (self.task / 'input').write_bytes(b'1234')
        for phase, budget in (('before', 2), ('after', 6)):
            with self.subTest(phase=phase), self.assertRaisesRegex(TaskCaptureError, 'task-byte-limit'):
                self.host(name=phase, limits=TaskCaptureLimits(1000, budget, 100, 3))
            output = self.root / phase
            failure = json.loads((output / 'failure.json').read_bytes())
            self.assertEqual(failure['phase'], phase)
            self.assertTrue(failure['truncated'])
            self.assertEqual(next((output / phase).glob('object-*')).read_bytes(), b'')
            self.assert_no_secret(output)

    def test_incomplete_guarded_process_never_produces_after_or_attempt(self):
        for reason in ('timeout', 'byte-limit'):
            limit = TaskCaptureLimits(3 if reason == 'byte-limit' else 100, 100, 100, .2)
            code = 'import os,time; os.write(1,b"safe"); time.sleep(30)' if reason == 'timeout' else 'print("safe")'
            with self.subTest(reason=reason), self.assertRaisesRegex(RuntimeError, '^guarded capture incomplete: ' + reason):
                self.host(code, name=reason, limits=limit)
            self.assertFalse((self.root / reason / 'after').exists())
            self.assertFalse((self.root / reason / 'process/capture.json').exists())
            self.assert_no_secret(self.root / reason)

    def test_final_policy_cleanup_failure_poisoned_supervised_lifecycle(self):
        class CleanupGate(Gate):
            final = False

            def feed(self, raw):
                if raw.startswith(b'observed task changes through a retained descriptor'):
                    self.final = True
                return super().feed(raw)

            def abandon(self):
                super().abandon()
                if self.final:
                    raise OSError('synthetic policy cleanup failure')

        with self.assertRaisesRegex(TaskCaptureError, 'exited-without-finish'):
            with self.recorder(quarantine_factory=CleanupGate) as recorder:
                descriptor = self.before(recorder)
                anchor = self.process()
                with self.assertRaisesRegex(OSError, 'synthetic policy cleanup failure'):
                    recorder.finish(expected_process_sha256=anchor)
                with self.assertRaisesRegex(TaskCaptureError, 'finish-out-of-order'):
                    recorder.finish(expected_process_sha256=anchor)
        self.assertEqual(os.fstat(descriptor).st_ino, self.task.stat().st_ino)
        self.assertFalse((self.root / 'supervised/.attempt.pending').exists())
        self.assert_no_secret(self.root / 'supervised')


if __name__ == '__main__':
    unittest.main()
