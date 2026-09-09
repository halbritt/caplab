import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from caplab.capture_accounting import build_capture_population_report
from caplab.task_capture_verify import CaptureVerificationError
from test_capture_accounting import POLICY, REPO, build_fixture, digest


def slot(name, options=None, *, task=True, native=True):
    return {'slot_id': name,
            'task_capture': {'custody': str(options['task_custody']), 'sha256': options['expected_attempt_sha256']}
                if options and task else None,
            'native_collection': {'custody': str(options['collection_custody']), 'sha256': options['expected_collection_sha256']}
                if options and native else None}


def population(slots):
    return {'schema': 'caplab.capture-population-input/v1', 'cells': [
        {'world': 'café', 'arm': 'retrieval', 'configured_tuple_id': 'codex-terra-max', 'slots': slots}]}


def encoded(data):
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


def inspect(data, **changes):
    raw = data if isinstance(data, bytes) else encoded(data)
    options = {'expected_input_sha256': hashlib.sha256(raw).hexdigest(),
               'max_input_bytes': len(raw), 'max_slots': 20, 'max_receipt_bytes': 200000}
    return build_capture_population_report(POLICY, raw, **(options | changes))


class CapturePopulationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_missing_pairs_partial_components_failed_process_and_empty_cell_remain_visible(self):
        complete = build_fixture(self.root / 'complete')
        task_only = build_fixture(self.root / 'task-only')
        native_only = build_fixture(self.root / 'native-only')
        data = population([slot('full', complete), slot('task', task_only, native=False),
                           slot('native', native_only, task=False), slot('absent')])
        data['cells'].append({**data['cells'][0], 'arm': 'none', 'slots': []})
        before = {str(p): digest(p) for p in self.root.rglob('*') if p.is_file()}
        report = inspect(data)
        totals = report['totals']
        self.assertEqual((totals['expected_slots'], totals['available_pair_slots'], totals['unavailable_pair_slots']), (4, 1, 3))
        self.assertEqual(totals['available_pair_logical_payload_bytes'], 25)
        self.assertIsNone(totals['all_slot_pair_logical_payload_bytes'])
        self.assertIsNone(totals['all_slot_pair_receipt_bytes'])
        full, task, native, absent = report['cells'][0]['slots']
        self.assertEqual(full['byte_report']['return_code'], 7)
        self.assertTrue(full['byte_report']['task_capture_complete'])
        self.assertEqual(task['task_inspection']['return_code'], 7)
        self.assertEqual(task['anchors_not_supplied'], ['native_collection'])
        self.assertEqual(native['native_inspection']['configured_tuple_id'], 'codex-terra-max')
        self.assertIsNone(native['byte_report'])
        self.assertEqual(absent['anchors_not_supplied'], ['task_capture', 'native_collection'])
        self.assertEqual(report['cells'][1]['totals']['expected_slots'], 0)
        self.assertFalse(report['population_assignment_verified'])
        self.assertFalse(report['study_eligibility_established'])
        self.assertEqual(before, {str(p): digest(p) for p in self.root.rglob('*') if p.is_file()})
        data['cells'][0]['slots'].clear()
        self.assertEqual(len(report['cells'][0]['slots']), 4)

    def test_available_pair_can_have_truncated_stream_and_missing_native_surface(self):
        options = build_fixture(self.root / 'truncated', stream_limit=2, missing_session=True)
        report = inspect(population([slot('s1', options)]))
        self.assertEqual(report['totals']['available_pair_slots'], 1)
        self.assertEqual(report['totals']['all_slot_pair_logical_payload_bytes'],
                         report['totals']['available_pair_logical_payload_bytes'])
        bundle = report['cells'][0]['slots'][0]['byte_report']
        self.assertFalse(bundle['task_capture_complete'])
        self.assertEqual(bundle['termination'], 'byte-limit')
        self.assertIn('session_search_root', bundle['missing_locations'])
        self.assertIsNone(bundle['native_capture_complete'])

    def test_supplied_corrupt_or_missing_bundle_is_not_hidden_by_missing_counterpart(self):
        options = build_fixture(self.root / 'partial')
        data = population([slot('s1', options, native=False)])
        path = options['task_custody'] / 'process/native.stdout'
        original = path.read_bytes()
        path.write_bytes(b'BAD')
        with self.assertRaisesRegex(CaptureVerificationError, 'slot.*s1'):
            inspect(data)
        path.write_bytes(original)
        path.unlink()
        with self.assertRaises(OSError):
            inspect(data)
        data = population([slot('s1', options, task=False)])
        data['cells'][0]['slots'][0]['native_collection']['sha256'] = '0' * 64
        with self.assertRaises(CaptureVerificationError):
            inspect(data)

    def test_collection_tuple_must_match_cell_for_complete_and_partial_pairs(self):
        options = build_fixture(self.root / 'wrong-tuple')
        for task in (True, False):
            with self.subTest(task=task):
                data = population([slot('s1', options, task=task)])
                data['cells'][0]['configured_tuple_id'] = 'different-config'
                with self.assertRaisesRegex(CaptureVerificationError, 'tuple differs'):
                    inspect(data)

    def test_population_identity_errors_are_rejected_before_any_bundle_read(self):
        base = population([slot('s1')])
        variants = []
        value = copy.deepcopy(base); value['cells'].append(copy.deepcopy(value['cells'][0])); variants.append((value, 'duplicate population cell'))
        value = copy.deepcopy(base); value['cells'][0]['slots'].append(slot('s1')); variants.append((value, 'duplicate expected slot'))
        value = copy.deepcopy(base); value['extra'] = 1; variants.append((value, 'input schema'))
        for same_path in (True, False):
            value = population([slot('s1'), slot('s2')])
            for i, row in enumerate(value['cells'][0]['slots']):
                row['task_capture'] = {'custody': '/missing/bundle' if same_path else '/missing/' + str(i),
                                       'sha256': str(i) * 64 if same_path else '0' * 64}
            variants.append((value, 'reused'))
        for value, message in variants:
            with self.subTest(message=message), self.assertRaisesRegex(CaptureVerificationError, message):
                inspect(value)
        with self.assertRaisesRegex(CaptureVerificationError, 'slot allowance'):
            inspect(population([slot('s1'), slot('s2')]), max_slots=1)

    def test_strict_input_anchor_and_resource_limits(self):
        raw = encoded(population([slot('s1')]))
        invalid = [raw.replace(b'"cells":', b'"cells": [], "cells":'),
                   raw.replace(b'"task_capture": null', b'"task_capture": NaN'),
                   raw.replace(b'"slot_id": "s1"', b'"slot_id": 1'),
                   raw + b'\xff', b'[]']
        for content in invalid:
            with self.subTest(content=content), self.assertRaises(CaptureVerificationError):
                inspect(content)
        for change in ({'expected_input_sha256': '0' * 64}, {'max_input_bytes': len(raw) - 1},
                       {'max_slots': True}, {'max_receipt_bytes': 0}):
            with self.subTest(change=change), self.assertRaises(CaptureVerificationError):
                inspect(raw, **change)

    def test_cli_matches_api_and_bad_anchor_emits_no_report(self):
        options = build_fixture(self.root / 'cli')
        raw = encoded(population([slot('s1', options), slot('s2')]))
        path = self.root / 'population.json'; path.write_bytes(raw)
        command = [sys.executable, str(REPO / 'scripts/capture_population.py'), str(path),
                   '--policy', str(POLICY), '--max-input-bytes', str(len(raw)), '--max-slots', '2',
                   '--max-receipt-bytes', '200000', '--expected-input-sha256', hashlib.sha256(raw).hexdigest()]
        env = {**os.environ, 'PYTHONPATH': str(REPO / 'src'), 'PYTHONDONTWRITEBYTECODE': '1'}
        result = subprocess.run(command, capture_output=True, env=env, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), inspect(raw))
        result = subprocess.run(command[:-1] + ['0' * 64], capture_output=True, env=env, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')
        self.assertEqual(path.read_bytes(), raw)
