"""Exercise original delivery, pool rows and aggregate denominator accounting."""
import hashlib
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, '/source/src')
from caplab.advisory import pool_runner, corpus


def sha(body):
    return hashlib.sha256(body.encode()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


criteria = json.loads(Path('/witness/criteria.json').read_text())
for condition in criteria['conditions']:
    directory = Path('/capture') / condition
    directory.mkdir()
    direct = condition.startswith('direct-')
    mode = 'stdin' if condition == 'direct-stdin-over' else 'arg'
    config = {'direct': direct, 'mode': mode, 'behavior': 'healthy', 'expected_bodies': {}}
    adapter = {'command': ['/usr/bin/python3', '-I', '-B', '/witness/receiver.py', str(directory / 'config.json')],
               'prompt_mode': mode}
    if direct:
        size = 100000 if condition == 'direct-arg-limit' else 100001
        body = 'x' * size
        config['expected_bodies'] = {'direct': sha(body)}
        write(directory / 'config.json', config)
        result = pool_runner.invoke(adapter, body, timeout=5)
        write(directory / 'observation.json', {'condition': condition, 'kind': 'invoke', 'result': result})
        continue
    body_path = 'large.md' if condition == 'pair-spill' else 'small.md'
    body = (Path('/fixtures') / body_path).read_text()
    substrate = {'record': 'caplab-substrate/1', 'substrate_id': 'fixture-body', 'sha256': sha(body),
                 'bytes': len(body.encode()), 'partition': 'open', 'applicable_operators': ['requirement_inversion'],
                 'source': {'kind': 'repo-doc', 'repo': 'caplab', 'path': body_path,
                            'commit': 'synthetic-transport-fixture'}}
    cases = corpus.sample_cases([substrate], sweep_seed=77, per_operator=1)
    if len(cases) != 1:
        raise ValueError('original sampler did not select exactly one fixture')
    case = cases[0]
    injection = pool_runner.BY_NAME[case['operator']](body, random.Random(case['seed']))
    if not pool_runner.check_present(injection, injection.body) or pool_runner.check_present(injection, body):
        raise ValueError('original pair preparation is not ready')
    config['contract'] = pool_runner.CALIBRATION_PROFILES['v1']
    config['expected_bodies'] = {'control': sha(body), 'mutant': sha(injection.body)}
    if condition == 'pair-empty-control':
        config.update(behavior='empty', affected_arm='control')
    elif condition == 'pair-empty-mutant':
        config.update(behavior='empty', affected_arm='mutant')
    elif condition == 'pair-timeout-mutant':
        config.update(behavior='timeout', affected_arm='mutant')
    elif condition == 'pair-invalid-mutant':
        config.update(behavior='invalid', affected_arm='mutant')
    write(directory / 'config.json', config)
    write(directory / 'registry.jsonl', substrate)
    # The original registry is JSONL, so emit its single record on one line.
    (directory / 'registry.jsonl').write_text(json.dumps(substrate) + '\n')
    backend = directory / 'backends/fixture'
    backend.mkdir(parents=True)
    write(backend / 'backend.yaml', {'id': 'fixture', 'adapter': adapter})
    result = pool_runner.run_pool(backend='fixture', backends_root=str(directory / 'backends'),
        registry_path=str(directory / 'registry.jsonl'), out_dir=str(directory / 'pool'),
        sweep_seed=77, per_operator=1, max_cases=1,
        timeout=0.5 if config['behavior'] == 'timeout' else 5)
    rows = [json.loads(line) for line in (directory / 'pool/results.jsonl').read_text().splitlines()]
    if len(rows) != 1:
        raise ValueError('original pool did not retain exactly one result row')
    write(directory / 'observation.json', {'condition': condition, 'kind': 'pool', 'summary': result, 'row': rows[0]})

# Record the original modules actually loaded; no target implementation is patched.
loaded = []
for module in list(sys.modules.values()):
    name = getattr(module, '__file__', None)
    if name and name.startswith('/source/'):
        path = Path(name)
        loaded.append({'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
write(Path('/capture/loaded-source.json'), sorted(loaded, key=lambda item: item['path']))
