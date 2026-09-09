"""Prospective arm allocation must not follow account or lane identity."""

from collections import Counter, defaultdict
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from caplab.execution_allocation import plan_execution_allocation


def example():
    return {
        'schema_version': 'caplab-execution-allocation-input/1',
        'seed': 37,
        'cycles': 2,
        'worlds': ['world-b', 'world-a'],
        'arms': ['retrieval', 'sham', 'none'],
        'resources': [{'account': f'account-{i}', 'lane': f'lane-{i}'} for i in range(4)],
    }


class ExecutionAllocationTests(unittest.TestCase):
    def test_reproducibility_ignores_input_order_and_preserves_borrowed_metadata(self):
        spec = example()
        before = copy.deepcopy(spec)
        first = plan_execution_allocation(spec)
        self.assertEqual(spec, before)
        for field in ('worlds', 'arms', 'resources'):
            spec[field].reverse()
        self.assertEqual(plan_execution_allocation(spec), first)
        self.assertEqual(first['basis'], 'declared-metadata-only')
        self.assertIs(first['execution_authorized'], False)
        self.assertEqual(len({r['proposed_slot'] for r in first['proposed_slots']}), 48)
        maps = {tuple((r['world'], r['arm'], r['account'], r['launch_order'])
                      for r in plan_execution_allocation(spec | {'seed': s})['proposed_slots'])
                for s in range(8)}
        self.assertGreater(len(maps), 1)

    def test_balance_survives_different_seeds_and_partial_resource_use(self):
        for seed in range(12):
            for arm_count in range(2, 5):
                for resource_count in range(arm_count, 6):
                    spec = example() | {'seed': seed, 'cycles': 1, 'worlds': ['w'],
                        'arms': [f'a-{i}' for i in range(arm_count)],
                        'resources': [{'account': f'p-{i}', 'lane': f'l-{i}'} for i in range(resource_count)]}
                    rows = plan_execution_allocation(spec)['proposed_slots']
                    with self.subTest(seed=seed, arms=arm_count, resources=resource_count):
                        self.assertEqual(Counter((r['arm'], r['account']) for r in rows),
                                         Counter((a, p['account']) for a in spec['arms'] for p in spec['resources']))
                        for batch in range(1, resource_count + 1):
                            selected = [r for r in rows if r['batch'] == batch]
                            self.assertEqual(len({r['account'] for r in selected}), arm_count)
                            self.assertEqual(len({r['arm'] for r in selected}), arm_count)

    def test_cli_emits_a_reproducible_plan_and_rejects_ambiguous_input(self):
        root = Path(__file__).resolve().parents[1]
        env = {**os.environ, 'PYTHONPATH': str(root / 'src'), 'PYTHONDONTWRITEBYTECODE': '1'}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'plan.json'
            raw = json.dumps(example()).encode()
            path.write_bytes(raw)
            command = ['python3', str(root / 'scripts/execution_allocation.py'), str(path)]
            result = subprocess.run(command, env=env, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report.pop('input_sha256'), hashlib.sha256(raw).hexdigest())
            self.assertEqual(report, plan_execution_allocation(example()))
            for invalid in (b'{"seed":1,"seed":2}', b'{"seed":NaN}', b'\xff', b' ' * (1024 * 1024 + 1)):
                path.write_bytes(invalid)
                refused = subprocess.run(command, env=env, capture_output=True, check=False)
                self.assertEqual(refused.returncode, 2, refused.stderr)
                self.assertEqual(refused.stdout, b'')
                self.assertEqual(path.read_bytes(), invalid)
            self.assertEqual([p.name for p in Path(temporary).iterdir()], ['plan.json'])

    def test_malformed_metadata_and_excess_slots_are_refused(self):
        mutations = [
            ('schema_version', 'unknown'), ('seed', True), ('seed', -1),
            ('seed', 2**64), ('cycles', False), ('cycles', 1.0), ('cycles', 0),
            ('cycles', 417), ('worlds', []), ('worlds', ['w', 'w']),
            ('worlds', [' ']), ('worlds', [None]), ('worlds', ['w' * 129]),
            ('arms', ['a']), ('arms', ['a', 'a']), ('arms', 'abc'),
            ('resources', []), ('resources', [None]),
            ('resources', [{'account': 'a', 'lane': 'l', 'extra': 1}]),
            ('extra', 'ignored'),
        ]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                with self.assertRaises(ValueError):
                    plan_execution_allocation(example() | {key: value})
        for key in ('account', 'lane'):
            spec = example()
            spec['resources'][1][key] = spec['resources'][0][key]
            with self.subTest(shared_resource=key), self.assertRaises(ValueError):
                plan_execution_allocation(spec)
        for spec in (None, [], {}, example() | {'resources': {'a': 'l'}}):
            with self.subTest(document=spec), self.assertRaises(ValueError):
                plan_execution_allocation(spec)

    def test_insufficient_resources_cannot_masquerade_as_parallel_allocation(self):
        spec = example()
        spec['resources'] = spec['resources'][:2]
        with self.assertRaisesRegex(ValueError, 'at least as many resources as arms'):
            plan_execution_allocation(spec)

    def test_every_arm_uses_each_resource_once_per_world_cycle(self):
        spec = example()
        report = plan_execution_allocation(spec)
        rows = report['proposed_slots']
        self.assertEqual(len(rows), 48)
        counts = Counter((r['world'], r['cycle'], r['arm'], r['account'], r['lane']) for r in rows)
        expected = Counter((w, c, a, p['account'], p['lane'])
                           for w in spec['worlds'] for c in (1, 2)
                           for a in spec['arms'] for p in spec['resources'])
        self.assertEqual(counts, expected)
        batches = defaultdict(list)
        for row in rows:
            batches[row['batch']].append(row)
        self.assertEqual(len(batches), 16)
        for batch in batches.values():
            self.assertEqual({r['arm'] for r in batch}, set(spec['arms']))
            self.assertEqual(len({r['account'] for r in batch}), 3)
            self.assertEqual(len({r['lane'] for r in batch}), 3)
            self.assertEqual(len({r['world'] for r in batch}), 1)
            self.assertEqual(len({r['cycle'] for r in batch}), 1)
            self.assertEqual(sorted(r['launch_order'] for r in batch), [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
