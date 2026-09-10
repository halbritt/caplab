"""Preserve original pool-runner revisions and exercise real subprocess delivery."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
import time

from reviewer_scheduler_witness import execute, inventory, namespace
from reviewer_timeout_witness import sha, write_json, write_new

CAPLAB = Path(__file__).resolve().parents[1]
ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/pool-transport-witness-2')
PROBES = CAPLAB / 'docs/product/studies/reviewer-ranking-001/development-witnesses/caplab-pool-transport'
AUTH = CAPLAB / 'docs/records/authorization-2026-09-10-reviewer-pool-transport-witness-2.md'
COMMITS = {'introduction': '9cb8d6561176e9d3d7b530eae3f40954744d1766',
           'base': '1517d426afbced67422a4097c0d5fd92d7200287', 'repair': 'c8f097a0934bfa380e7c9c5cda4f11ea4ac2b454'}
PATHS = ['src/caplab', 'pyproject.toml', 'docs/product/specs/spec-agent-capability-lab.md']
CONDITIONS = ['direct-arg-limit', 'direct-arg-over', 'direct-stdin-over', 'pair-inline', 'pair-spill',
              'pair-empty-control', 'pair-empty-mutant', 'pair-timeout-mutant', 'pair-invalid-mutant']


def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(CAPLAB), *args])


def materialize(role, commit):
    root = ROOT / role
    root.mkdir()
    expected = {}
    for row in git('ls-tree', '-rz', commit, '--', *PATHS).split(b'\0'):
        if row:
            header, name = row.split(b'\t', 1)
            mode, kind, blob = header.decode().split()
            if kind != 'blob' or mode not in ('100644', '100755'):
                raise ValueError('unsupported historical source entry')
            expected[name.decode()] = {'mode': mode, 'git_blob': blob}
    retained = []
    for name, entry in expected.items():
        body = git('cat-file', 'blob', entry['git_blob'])
        if hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() != entry['git_blob']:
            raise ValueError('Git blob mismatch')
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        write_new(path, body)
        path.chmod(0o500 if entry['mode'] == '100755' else 0o400)
        retained.append({'path': name, **entry, 'sha256': sha(body)})
    return {'commit': commit, 'tree': git('rev-parse', commit + '^{tree}').decode().strip(),
            'parent': git('rev-parse', commit + '^').decode().strip(), 'files': retained}


def runtime():
    paths = [Path('/usr/bin/python3').resolve(), Path('/usr/bin/bwrap')]
    for root in (Path(sysconfig.get_path('stdlib')), Path('/usr/lib/python3/dist-packages/yaml')):
        paths += [p for p in sorted(root.rglob('*')) if p.is_file() and p.suffix in ('.py', '.so') and '__pycache__' not in p.parts]
    return [{'path': str(path), 'sha256': sha(path.read_bytes())} for path in paths]


def verify_inputs(plan):
    if sys.version != plan['python_version'] or runtime() != plan['runtime']:
        raise ValueError('Python runtime or dependency drift')
    for row in plan['support']:
        if sha(Path(row['path']).read_bytes()) != row['sha256']:
            raise ValueError('administration code or authorization drift')
    if inventory(ROOT / 'witness') != plan['witness'] or inventory(ROOT / 'fixtures') != plan['fixtures']:
        raise ValueError('frozen witness or fixture drift')
    for role, snapshot in plan['snapshots'].items():
        if snapshot['commit'] != COMMITS[role]:
            raise ValueError('source revision mismatch')
        observed = inventory(ROOT / role)
        if {row['path'] for row in observed} != {row['path'] for row in snapshot['files']}:
            raise ValueError('source membership drift')
        for row in snapshot['files']:
            if sha((ROOT / role / row['path']).read_bytes()) != row['sha256']:
                raise ValueError('historical source drift')


def prepare():
    if sys.version_info[:2] != (3, 12) or time.time() >= 1789084800:
        raise ValueError('runtime outside authorization or authorization expired')
    ROOT.mkdir(mode=0o700)
    (ROOT / 'witness').mkdir()
    (ROOT / 'fixtures').mkdir()
    for name in ('probe.py', 'receiver.py'):
        write_new(ROOT / 'witness' / name, (PROBES / name).read_bytes())
    body = '# Delivery fixture {#el:delivery}\n\n## Constraint {#el:constraint}\n\nThe receiver must not change payload bytes.\n'
    write_new(ROOT / 'fixtures/small.md', body.encode())
    write_new(ROOT / 'fixtures/large.md', (body + '\n' + 'fixture payload. ' * 8000).encode())
    write_json(ROOT / 'witness/criteria.json', {'conditions': CONDITIONS, 'repetitions': 2,
        'delivery': 'The declared argument or stdin endpoint receives every intended byte, or invocation is explicitly refused before launch.',
        'pair': 'Both configured responses must contain a contract-valid verdict before the original pool may include the pair in a score denominator.',
        'basis': 'Predating product specification requires valid attempts and failure/missingness accounting; original prompt enumerates valid verdicts.',
        'expected': {'healthy': ['pair-inline', 'pair-spill'],
                     'invalid': ['pair-empty-control', 'pair-empty-mutant', 'pair-timeout-mutant', 'pair-invalid-mutant']},
        'hypotheses': ['Introduction/base silently reroute oversized argv prompts to unread stdin.',
                       'Repair refuses direct oversize and spills pool bodies while preserving delivery.',
                       'Introduction/base count a pair with an absent arm; repair excludes it.',
                       'A parseable object without a verdict may still enter the denominator after repair.'],
        'limits': ['Receiver supplies scripted transport outcomes, not reviewer judgments.',
                   'Original injection helpers prepare distinct bodies, not independent reviewer-quality truth.',
                   'No native subject measured, case admitted or ranking accepted.']})
    snapshots = {role: materialize(role, commit) for role, commit in COMMITS.items()}
    support = [Path(__file__), AUTH, CAPLAB / 'scripts/reviewer_scheduler_witness.py', CAPLAB / 'scripts/reviewer_timeout_witness.py']
    support += [PROBES / name for name in ('probe.py', 'receiver.py')]
    plan = {'schema': 'caplab.pool-transport-plan/v1', 'snapshots': snapshots,
            'python_version': sys.version, 'runtime': runtime(), 'witness': inventory(ROOT / 'witness'),
            'fixtures': inventory(ROOT / 'fixtures'), 'repetitions': 2, 'execution_seconds': 60, 'total_seconds': 360,
            'support': [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in support], 'ranking_eligible': False}
    verify_inputs(plan)
    write_new(ROOT / 'runner.py', Path(__file__).read_bytes())
    write_json(ROOT / 'plan.json', plan)
    print(json.dumps({'plan_sha256': sha((ROOT / 'plan.json').read_bytes()), 'root': str(ROOT)}))


def run(expected):
    if sha((ROOT / 'plan.json').read_bytes()) != expected or time.time() >= 1789084800:
        raise ValueError('plan mismatch or authorization expired')
    plan = json.loads((ROOT / 'plan.json').read_text())
    verify_inputs(plan)
    write_json(ROOT / 'run-started.json', {'plan_sha256': expected, 'time': time.time()})
    start = time.monotonic()
    failures = []
    for role in COMMITS:
        for repetition in range(1, plan['repetitions'] + 1):
            name = f'{role}-{repetition}'
            capture = ROOT / (name + '-capture')
            capture.mkdir()
            command = namespace() + ['--ro-bind', str(ROOT / role), '/source',
                '--ro-bind', str(ROOT / 'witness'), '/witness', '--ro-bind', str(ROOT / 'fixtures'), '/fixtures',
                '--ro-bind', str(ROOT / 'fixtures'), '/home/witness/git/caplab', '--bind', str(capture), '/capture',
                '--chdir', '/tmp', '--', '/usr/bin/python3', '-I', '-B', '/witness/probe.py']
            remaining = min(plan['execution_seconds'], plan['total_seconds'] - (time.monotonic() - start), 1789084800 - time.time())
            if remaining <= 0:
                raise RuntimeError('execution budget exhausted')
            result = execute(ROOT / name, command, remaining)
            write_json(ROOT / (name + '-inventory.json'), inventory(capture))
            if result['returncode'] or result['timed_out']:
                failures.append(name)
                break
        if failures:
            break
    verify_inputs(plan)
    write_json(ROOT / 'completion.json', {'plan_sha256': expected, 'failures': failures,
        'elapsed_seconds': time.monotonic() - start, 'inputs_rechecked': True, 'ranking_eligible': False})
    print(json.dumps({'failures': failures, 'root': str(ROOT)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('prepare', 'run'))
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    os.umask(0o077)
    prepare() if args.operation == 'prepare' else run(args.plan_sha256)
