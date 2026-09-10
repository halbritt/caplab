"""Execute the original Driver on disposable graphs with a virtual test witness."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

import reviewer_scheduler_witness as scheduler
from reviewer_timeout_witness import sha, write_json, write_new

CAPLAB = Path(__file__).resolve().parents[1]
PRIOR = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/scheduler-witness-2')
PRIOR_PLAN = '5da0a78a262415eacdfd9cfb82cc7629f4d88b6b2491403a138f2bdbfd8eb50a'
PROBE = CAPLAB / 'docs/product/studies/reviewer-ranking-001/development-witnesses/striatum-scheduler/graph_probe_test.go'
AUTH = CAPLAB / 'docs/records/authorization-2026-09-10-reviewer-scheduler-graph-witness-2.md'
ROOT = PRIOR.parent / 'scheduler-graph-witness-2'
CONDITIONS = ['ordinary', 'local-fallback', 'supervised-fallback', 'unrecognized-terminal', 'expired-observation']
SUPPORT = [Path(scheduler.__file__), CAPLAB / 'scripts/reviewer_timeout_witness.py']


def verify_inputs(root, plan):
    if str(root.resolve()) != str(ROOT):
        raise ValueError('unauthorized custody root')
    if sha((PRIOR / 'plan.json').read_bytes()) != PRIOR_PLAN:
        raise ValueError('prior custody plan changed')
    scheduler.verify_inputs(PRIOR, json.loads((PRIOR / 'plan.json').read_text()))
    for key, path in [('probe', root / 'witness/graph_probe_test.go'), ('overlay', root / 'witness/overlay.json'),
                      ('criteria', root / 'criteria.json'), ('authorization', AUTH), ('runner', Path(__file__))]:
        if sha(path.read_bytes()) != plan[key + '_sha256']:
            raise ValueError(key + ' drift')
    if sha(PROBE.read_bytes()) != plan['probe_sha256']:
        raise ValueError('tracked witness drift')
    for row in plan['support']:
        if sha(Path(row['path']).read_bytes()) != row['sha256']:
            raise ValueError('runner dependency drift')
    # Prior verification checks bytes; also forbid extra files in source snapshots.
    prior = json.loads((PRIOR / 'plan.json').read_text())
    for role in ('base', 'repair'):
        expected = {row['path'] for row in prior['snapshots'][role]['files']}
        observed = {row['path'] for row in scheduler.inventory(PRIOR / role)}
        if expected != observed:
            raise ValueError('source membership drift')


def prepare(root):
    if root.resolve() != ROOT or time.time() >= 1789084800:
        raise ValueError('unauthorized root or expired authorization')
    root.mkdir(mode=0o700)
    (root / 'witness').mkdir()
    write_new(root / 'witness/graph_probe_test.go', PROBE.read_bytes())
    write_json(root / 'witness/overlay.json', {'Replace': {
        '/source/internal/driver/caplab_graph_witness_test.go': '/witness/graph_probe_test.go'}})
    write_json(root / 'criteria.json', {
        'schema': 'caplab.scheduler-graph-criteria/v1', 'conditions': CONDITIONS, 'repetitions': 2,
        'expected_selected': {'ordinary': 'capture', 'local-fallback': 'fallback', 'supervised-fallback': 'fallback',
                              'unrecognized-terminal': 'capture', 'expired-observation': 'capture'},
        'expected_active_observations': {'ordinary': 0, 'local-fallback': 1, 'supervised-fallback': 1,
                                         'unrecognized-terminal': 0, 'expired-observation': 0},
        'expected_folded_observations': {'ordinary': 0, 'local-fallback': 1, 'supervised-fallback': 1,
                                         'unrecognized-terminal': 0, 'expired-observation': 1},
        'properties': [
            'Source setup must pass original manifest, declaration, classifier and graph checks; setup failure is unmeasured.',
            'Active recognized exhaustion excludes capture; unrelated terminal text and expired exhaustion do not.',
            'Decision creation, binding, graph reopen and fresh Session fold must preserve the selected backend.',
            'A repeated decision and binding request appends no record and reports no creation.',
            'A causally relevant observation must be in the complete decision input preimage under predating D0008.C1/C11.',
            'Original graph bytes and repository identity are retained; capture adapter dispatch count must be zero.',
            'Compare semantic properties across repetitions; graph paths and content hashes can differ.'],
        'hypotheses': {'base_local_fallback': 'Driver refuses v5 envelope versus v2 evaluation before append.',
                       'repair_local_fallback': 'Driver may accept, bind and reopen v2 decision omitting the causal observation.'},
        'limits': ['Historical fixture builders supply setup, not correctness labels.',
                   'Observation removal is a counterfactual, not a general record-to-input reconstruction.',
                   'No backend execution, real provider exhaustion, corpus admission or reviewer ranking.']})
    plan = {'schema': 'caplab.scheduler-graph-plan/v1', 'prior_root': str(PRIOR), 'prior_plan_sha256': PRIOR_PLAN,
            'roles': ['base', 'repair'], 'repetitions': 2, 'build_seconds': 180, 'execution_seconds': 90,
            'total_seconds': 900, 'ranking_eligible': False,
            'support': [{'path': str(path), 'sha256': sha(path.read_bytes())} for path in SUPPORT]}
    for key, path in [('probe', PROBE), ('overlay', root / 'witness/overlay.json'), ('criteria', root / 'criteria.json'),
                      ('authorization', AUTH), ('runner', Path(__file__))]:
        plan[key + '_sha256'] = sha(path.read_bytes())
    verify_inputs(root, plan)
    write_new(root / 'runner.py', Path(__file__).read_bytes())
    write_json(root / 'plan.json', plan)
    print(json.dumps({'root': str(root), 'plan_sha256': sha((root / 'plan.json').read_bytes())}))


def run(root, expected):
    if sha((root / 'plan.json').read_bytes()) != expected:
        raise ValueError('plan hash mismatch')
    plan = json.loads((root / 'plan.json').read_text())
    if time.time() >= 1789084800:
        raise ValueError('authorization expired')
    verify_inputs(root, plan)
    write_json(root / 'run-started.json', {'plan_sha256': expected, 'time': time.time()})
    start = time.monotonic()
    failures = []
    prior = json.loads((PRIOR / 'plan.json').read_text())
    (root / 'build-cache').mkdir()
    (root / 'builds').mkdir()

    def remaining(limit):
        seconds = min(limit, plan['total_seconds'] - (time.monotonic() - start), 1789084800 - time.time())
        if seconds <= 0:
            raise RuntimeError('execution or authorization budget exhausted')
        return seconds

    for role in plan['roles']:
        output = root / 'builds' / role
        output.mkdir()
        command = scheduler.namespace() + [
            '--ro-bind', str(scheduler.GO), '/go', '--ro-bind', str(PRIOR / role), '/source',
            '--ro-bind', str(root / 'witness'), '/witness', '--bind', str(root / 'build-cache'), '/cache',
            '--bind', str(output), '/output', '--chdir', '/source']
        for dep in prior['dependencies']:
            command += ['--ro-bind', dep['source'], dep['destination']]
        for key, value in {'GOROOT': '/go', 'GOMODCACHE': '/gomod', 'GOCACHE': '/cache', 'GOPROXY': 'off',
                           'GOSUMDB': 'off', 'GOTOOLCHAIN': 'local', 'GOENV': 'off', 'GOWORK': 'off',
                           'CGO_ENABLED': '0', 'GOTELEMETRY': 'off'}.items():
            command += ['--setenv', key, value]
        command += ['--', '/go/bin/go', 'test', '-c', '-vet=off', '-mod=readonly', '-trimpath',
                    '-overlay=/witness/overlay.json', '-o', '/output/probe', './internal/driver']
        result = scheduler.execute(root / (role + '-compile'), command, remaining(plan['build_seconds']))
        if result['returncode'] or result['timed_out']:
            failures.append({'role': role, 'phase': 'compile'})
            break
        binary_hash = sha((output / 'probe').read_bytes())
        write_json(output / 'binary.json', {'sha256': binary_hash})
        for repetition in range(1, plan['repetitions'] + 1):
            name = f'{role}-execution-{repetition}'
            capture = root / (name + '-capture')
            capture.mkdir()
            if sha((output / 'probe').read_bytes()) != binary_hash:
                raise ValueError('compiled binary drift')
            command = scheduler.namespace() + [
                '--ro-bind', str(output / 'probe'), '/probe', '--bind', str(capture), '/capture',
                '--setenv', 'CAPLAB_GRAPH_CAPTURE', '/capture', '--chdir', '/tmp', '--', '/probe',
                '-test.run=^TestCAPLABGraphWitness$', '-test.v', '-test.count=1', '-test.timeout=60s']
            result = scheduler.execute(root / name, command, remaining(plan['execution_seconds']))
            write_json(root / (name + '-inventory.json'), scheduler.inventory(capture))
            if result['returncode'] or result['timed_out']:
                failures.append({'role': role, 'phase': name})
                break
        if failures:
            break
    verify_inputs(root, plan)
    write_json(root / 'completion.json', {'plan_sha256': expected, 'failures': failures,
        'elapsed_seconds': time.monotonic() - start, 'inputs_rechecked': True, 'ranking_eligible': False})
    print(json.dumps({'root': str(root), 'failures': failures}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['prepare', 'run'])
    parser.add_argument('root', type=Path)
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    os.umask(0o077)
    prepare(args.root) if args.operation == 'prepare' else run(args.root, args.plan_sha256)
