"""Retained version custody: real fixture capture, tampering and source removal."""

import copy
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

from caplab.native_version_capture import NativeVersionCaptureLimits
from caplab.native_version_verify import verify_native_version
from caplab.task_capture_verify import CaptureVerificationError
import test_native_version_capture as fixtures


@unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'requires Linux bubblewrap for fixture capture')
class NativeVersionVerifyTests(unittest.TestCase):
    def build(self, *, codex=False, code=None, limits=fixtures.LIMITS):
        fixture = fixtures.NativeVersionCaptureTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        fixture.prepare(codex=codex, code=code)
        fixture.capture(limits=limits)
        self.fixture = fixture
        self.custody = fixture.output
        self.anchor = fixture.digest(self.custody / 'version.json')
        return fixture

    def verify(self, **kwargs):
        options = dict(expected_version_sha256=self.anchor, max_receipt_bytes=200000, max_stream_bytes=10000)
        options.update(kwargs)
        return verify_native_version(fixtures.POLICY, self.custody, **options)

    def read(self, name):
        return json.loads((self.custody / name).read_bytes())

    def write(self, name, document):
        (self.custody / name).write_text(json.dumps(document, sort_keys=True) + '\n')

    def relink(self, name, document):
        """Tamper only a newly generated fixture, updating its enclosing hash links."""
        self.write(name, document)
        digest = self.fixture.digest(self.custody / name)
        if name == 'invocation.json':
            parent = self.read('preparation.json'); parent['invocation_file_sha256'] = digest
            self.relink('preparation.json', parent)
        elif name == 'preparation.json':
            parent = self.read('intent.json'); parent['preparation_sha256'] = digest
            version = self.read('version.json'); version['preparation_sha256'] = digest
            self.write('version.json', version); self.relink('intent.json', parent)
        elif name in ('intent.json', 'process/capture.json'):
            parent = self.read('version.json')
            parent['intent_sha256' if name == 'intent.json' else 'process_capture_sha256'] = digest
            if name == 'process/capture.json': parent['process'] = document
            self.relink('version.json', parent)
        else:
            self.anchor = digest

    def test_both_harness_bundles_verify_after_original_sources_are_removed(self):
        for codex in (False, True):
            with self.subTest(codex=codex):
                fixture = self.build(codex=codex)
                shutil.rmtree(fixture.preparation); shutil.rmtree(fixture.task)
                if codex: shutil.rmtree(fixture.harness)
                else: fixture.harness.unlink()
                before = {str(p.relative_to(self.custody)): p.read_bytes()
                          for p in self.custody.rglob('*') if p.is_file()}
                with patch('subprocess.Popen', side_effect=AssertionError('verification executed a process')):
                    report = self.verify()
                self.assertTrue(report['integrity_verified'])
                self.assertTrue(report['recorded_version_command_agrees'])
                self.assertTrue(report['process_capture_complete'])
                self.assertEqual(report['return_code'], 0)
                self.assertIs(report['native_identity_verified'], False)
                self.assertIs(report['binding_complete'], False)
                self.assertEqual(report['entrypoint_sha256'], fixture.entry_hash)
                self.assertEqual(before, {str(p.relative_to(self.custody)): p.read_bytes()
                                         for p in self.custody.rglob('*') if p.is_file()})

    def test_raw_non_utf8_output_is_hashed_without_version_guessing(self):
        self.build(code="import os;os.write(1,b'version \\xff\\n')\n")
        report = self.verify()
        self.assertEqual(report['streams']['stdout']['sha256'], self.fixture.digest(self.custody / 'process/native.stdout'))
        self.assertEqual(report['streams']['stdout']['bytes'], 10)
        self.assertNotIn('version_text', report)

    def test_process_failures_remain_observations_in_integrity_verified_bundles(self):
        cases = [('import sys;sys.exit(3)\n', fixtures.LIMITS, 'exited', 3, True),
                 ('import time;print("prefix",flush=True);time.sleep(2)\n', NativeVersionCaptureLimits(100000,100000,10000,0.2), 'timeout', None, False),
                 ('import os;os.write(1,b"x"*10000)\n', NativeVersionCaptureLimits(100000,100000,19,3), 'byte-limit', None, False)]
        for code, limits, termination, return_code, complete in cases:
            with self.subTest(termination=termination):
                self.build(code=code, limits=limits); report = self.verify()
                self.assertTrue(report['integrity_verified'])
                self.assertEqual(report['termination'], termination)
                self.assertEqual(report['process_capture_complete'], complete)
                if return_code is not None: self.assertEqual(report['return_code'], return_code)

    def test_independent_anchor_and_every_linked_receipt_are_checked(self):
        self.build()
        with self.assertRaisesRegex(CaptureVerificationError, 'hash mismatch'):
            self.verify(expected_version_sha256='0'*64)
        for name in ('version.json','intent.json','preparation.json','invocation.json','process/capture.json'):
            with self.subTest(name=name):
                path = self.custody / name; original = path.read_bytes()
                try:
                    path.write_bytes(original + b' ')
                    with self.assertRaisesRegex(CaptureVerificationError, 'hash mismatch'): self.verify()
                finally: path.write_bytes(original)

    def test_stream_tampering_and_symlink_replacement_fail(self):
        self.build()
        path = self.custody / 'process/native.stdout'; original = path.read_bytes()
        path.write_bytes(b'x' * len(original))
        with self.assertRaisesRegex(CaptureVerificationError, 'hash mismatch'): self.verify()
        outside = self.fixture.root / 'outside'; outside.write_bytes(original)
        path.unlink(); path.symlink_to(outside)
        with self.assertRaises(OSError): self.verify()

    def test_all_five_receipts_share_one_budget_and_streams_have_an_external_cap(self):
        self.build(); report = self.verify()
        receipt_bytes = report['verified_receipt_bytes']; stream_bytes = report['retained_stream_bytes']
        self.assertEqual(self.verify(max_receipt_bytes=receipt_bytes, max_stream_bytes=stream_bytes), report)
        with self.assertRaisesRegex(CaptureVerificationError, 'byte allowance'):
            self.verify(max_receipt_bytes=receipt_bytes - 1)
        with patch('caplab.native_version_verify._process', side_effect=AssertionError('stream read before cap')):
            with self.assertRaisesRegex(CaptureVerificationError, 'verification allowance'):
                self.verify(max_stream_bytes=stream_bytes - 1)

    def test_recorded_argv_environment_and_access_cannot_be_relabelled(self):
        self.build(); original = self.read('intent.json')
        changes = [('command', original['command'] + ['model prompt']),
                   ('environment', original['environment'] | {'SYNTHETIC_SECRET': 'fixture'}),
                   ('network', 'shared'), ('task_access', 'read-write'), ('purpose', 'model execution')]
        for field, value in changes:
            with self.subTest(field=field):
                changed = copy.deepcopy(original); changed[field] = value; self.relink('intent.json', changed)
                with self.assertRaises(CaptureVerificationError): self.verify()
        self.relink('intent.json', original)

    def test_reanchored_subject_or_positive_identity_claim_is_rejected(self):
        self.build(); original = self.read('version.json')
        changes = [('configured_tuple_id','another-tuple'), ('entrypoint_sha256','0'*64),
                   ('preparation_sha256','0'*64), ('invocation_sha256','0'*64),
                   ('native_identity_verified',True), ('binding_complete',True), ('binding_complete',0)]
        for field,value in changes:
            with self.subTest(field=field):
                changed = copy.deepcopy(original); changed[field] = value; self.relink('version.json', changed)
                with self.assertRaises(CaptureVerificationError): self.verify()

    def test_source_path_contradictions_fail_without_source_reads(self):
        self.build(); original = self.read('preparation.json')
        for field,value in [('runtime_root','/another/runtime'), ('custody_root','/bad/../root'),
                            ('mounts',{})]:
            with self.subTest(field=field):
                changed = copy.deepcopy(original); changed[field] = value; self.relink('preparation.json', changed)
                with self.assertRaises(CaptureVerificationError): self.verify()

    def test_invocation_must_rebuild_under_the_canonical_policy(self):
        self.build(); invocation = self.read('invocation.json')
        invocation['command'] += ['injected option']; self.relink('invocation.json', invocation)
        with self.assertRaisesRegex(CaptureVerificationError, 'invalid version invocation'): self.verify()

    def test_embedded_process_cannot_disagree_with_linked_receipt(self):
        self.build(); version = self.read('version.json'); version['process']['return_code'] = 9
        self.relink('version.json', version)
        with self.assertRaisesRegex(CaptureVerificationError, 'embedded process'): self.verify()

    def test_reanchored_process_still_needs_consistent_limits_and_outcomes(self):
        self.build(); original = self.read('process/capture.json')
        changes = [('max_stream_bytes',1), ('timeout_seconds',99), ('return_code',True),
                   ('streams_complete',False), ('termination','byte-limit'), ('retained_stream_bytes',0)]
        for field,value in changes:
            with self.subTest(field=field):
                changed = copy.deepcopy(original); changed[field] = value; self.relink('process/capture.json', changed)
                with self.assertRaises(CaptureVerificationError): self.verify()

    def test_recorded_input_and_entrypoint_allowances_are_enforced(self):
        self.build(); original = self.read('intent.json')
        for field,value in [('max_receipt_bytes',1), ('max_entrypoint_bytes',1), ('timeout_seconds',True)]:
            with self.subTest(field=field):
                changed = copy.deepcopy(original); changed['limits'][field] = value; self.relink('intent.json', changed)
                with self.assertRaises(CaptureVerificationError): self.verify()

    def test_partial_or_symlinked_final_receipt_is_not_a_completed_bundle(self):
        self.build(); path = self.custody / 'version.json'
        outside = self.fixture.root / 'outside'; path.rename(outside)
        with self.assertRaises(FileNotFoundError): self.verify()
        path.symlink_to(outside)
        with self.assertRaises(OSError): self.verify()


class NativeVersionVerificationInputTests(unittest.TestCase):
    def test_invalid_verification_limits_fail_before_custody_access(self):
        for receipt,stream in [(True,1),(0,1),(1,False),(1,-1)]:
            with self.subTest(receipt=receipt,stream=stream):
                with self.assertRaisesRegex(CaptureVerificationError, 'positive integers'):
                    verify_native_version(fixtures.POLICY,Path('/nonexistent-custody'),
                        expected_version_sha256='0'*64,max_receipt_bytes=receipt,max_stream_bytes=stream)


if __name__ == '__main__': unittest.main()
