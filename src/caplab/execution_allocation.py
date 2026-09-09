"""Propose complete cyclic arm allocations over declared account/lane pairs."""

from __future__ import annotations

import hashlib
import json
import platform
import random


def _names(values: object, field: str, minimum: int = 1) -> list[str]:
    if not isinstance(values, list) or not minimum <= len(values) <= 10_000:
        raise ValueError(f'{field} must be a list of {minimum} to 10000 distinct names')
    if any(not isinstance(v, str) or not v.strip() or len(v) > 128 for v in values):
        raise ValueError(f'{field} names must be nonblank strings of at most 128 characters')
    if len(set(values)) != len(values):
        raise ValueError(f'{field} names must be distinct')
    return sorted(values)


def _canonical_input(document: object) -> dict:
    fields = {'schema_version', 'seed', 'cycles', 'worlds', 'arms', 'resources'}
    if not isinstance(document, dict) or set(document) != fields:
        raise ValueError('allocation requires exactly schema_version, seed, cycles, worlds, arms, resources')
    if document['schema_version'] != 'caplab-execution-allocation-input/1':
        raise ValueError('unsupported execution allocation schema')
    if type(document['seed']) is not int or not 0 <= document['seed'] < 2**64:
        raise ValueError('seed must be an unsigned 64-bit integer')
    if type(document['cycles']) is not int or not 1 <= document['cycles'] <= 10_000:
        raise ValueError('cycles must be an integer from 1 to 10000')
    worlds = _names(document['worlds'], 'worlds')
    arms = _names(document['arms'], 'arms', minimum=2)
    declared = document['resources']
    if (not isinstance(declared, list) or not 1 <= len(declared) <= 10_000
            or any(not isinstance(r, dict) or set(r) != {'account', 'lane'} for r in declared)):
        raise ValueError('resources must be a nonempty list of account/lane objects, at most 10000')
    _names([r['account'] for r in declared], 'accounts')
    _names([r['lane'] for r in declared], 'lanes')
    resources = sorted((r['account'], r['lane']) for r in document['resources'])
    if len(resources) < len(arms):
        raise ValueError('complete parallel cycles require at least as many resources as arms')
    if len(worlds) * len(arms) * len(resources) * document['cycles'] > 10_000:
        raise ValueError('allocation exceeds 10000 proposed slots')
    return {**document, 'worlds': worlds, 'arms': arms,
            'resources': [{'account': a, 'lane': l} for a, l in resources]}


def plan_execution_allocation(document: object) -> dict:
    """Return proposed slots, without reading or reserving execution resources."""
    canonical = _canonical_input(document)
    worlds, arms = canonical['worlds'], canonical['arms']
    resources = [(r['account'], r['lane']) for r in canonical['resources']]
    canonical_bytes = json.dumps(canonical, sort_keys=True, separators=(',', ':'),
                                ensure_ascii=False, allow_nan=False).encode('utf-8')
    rng = random.Random(canonical['seed'])
    batches = []
    for world in worlds:
        for cycle in range(1, canonical['cycles'] + 1):
            pairs = list(resources)
            order = list(arms)
            rng.shuffle(pairs)
            rng.shuffle(order)
            rotations = list(range(len(pairs)))
            rng.shuffle(rotations)
            for rotation in rotations:
                batch = []
                for offset, arm in enumerate(order):
                    account, lane = pairs[(rotation + offset) % len(pairs)]
                    batch.append({'world': world, 'cycle': cycle, 'arm': arm,
                                  'account': account, 'lane': lane})
                rng.shuffle(batch)
                batches.append(batch)
    rng.shuffle(batches)
    rows = []
    for number, batch in enumerate(batches, 1):
        for position, row in enumerate(batch, 1):
            rows.append({**row, 'batch': number, 'launch_order': position,
                         'proposed_slot': f'slot-{len(rows) + 1:05d}'})
    return {
        'schema_version': 'caplab-execution-allocation-report/1',
        'method': 'randomized-complete-cycles/1',
        'basis': 'declared-metadata-only',
        'execution_authorized': False,
        'canonical_input_sha256': hashlib.sha256(canonical_bytes).hexdigest(),
        'seed': canonical['seed'],
        'rng': {'implementation': platform.python_implementation(),
                'python_version': platform.python_version(), 'generator': 'random.Random'},
        'batch_count': len(batches),
        'slot_count': len(rows),
        'proposed_slots': rows,
    }
