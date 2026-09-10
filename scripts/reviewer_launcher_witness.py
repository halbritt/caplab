"""Freeze and exercise a selected original launcher's dispatch contract."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from reviewer_reddit_recovery_witness import runtime
from reviewer_scheduler_witness import execute, inventory, namespace
from reviewer_timeout_witness import sha, write_json, write_new

REPO = Path(__file__).resolve().parents[1]
ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/launcher-witness-1')
COMMIT = '51a7698535f065604337f5c1d54f20267e8be2a0'
BASE = '170fdf488df959ac503d5d419924caf5fec7bd8a'
LAUNCHER = 'scripts/launch_tree_v1_sweep.sh'
REQUIREMENT = 'docs/records/probe-2026-09-06-tree-v1-stage-b.md'
PROBES = REPO / 'docs/product/studies/reviewer-ranking-001/development-witnesses/launcher'
AUTH = REPO / 'docs/records/authorization-2026-09-10-reviewer-launcher-witness.md'
CONDITIONS = ('both-files', 'neither-file', 'zai-only', 'openrouter-only',
              'malformed-file', 'downstream-failure', 'spaced-path', 'missing-backend')


def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(REPO), *args])


def verify_inputs(plan):
    if inventory(ROOT / 'source') != plan['source_inventory'] or inventory(ROOT / 'witness') != plan['witness']:
        raise ValueError('source or fixture drift')
    if runtime() != plan['runtime']:
        raise ValueError('runtime drift')
    for entry in plan['support']:
        if sha(Path(entry['path']).read_bytes()) != entry['sha256']:
            raise ValueError('support drift')


def prepare():
    if time.time() >= 1789084800:
        raise ValueError('authorization expired')
    ROOT.mkdir(mode=0o700)
    source = ROOT / 'source'
    (source / 'advisory').mkdir(parents=True)
    files = []
    for row in git('ls-tree', '-rz', COMMIT, '--', LAUNCHER, 'scripts/supervise_sweep.py', REQUIREMENT).split(b'\0'):
        if not row:
            continue
        header, name = row.split(b'\t', 1)
        mode, kind, blob = header.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('unsupported original entry')
        body = git('cat-file', 'blob', blob)
        if hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() != blob:
            raise ValueError('Git blob mismatch')
        path = source / name.decode()
        path.parent.mkdir(parents=True, exist_ok=True)
        write_new(path, body)
        path.chmod(0o500 if mode == '100755' else 0o400)
        files.append({'path': name.decode(), 'mode': mode, 'git_blob': blob, 'sha256': sha(body)})
    if len(files) != 3 or git('rev-parse', COMMIT + '^').decode().strip() != BASE:
        raise ValueError('unexpected source identity')
    if git('ls-tree', BASE, '--', LAUNCHER):
        raise ValueError('launcher unexpectedly exists in base')
    if git('show', BASE + ':' + REQUIREMENT) != (source / REQUIREMENT).read_bytes():
        raise ValueError('requirement does not predate change')
    witness = ROOT / 'witness'
    witness.mkdir()
    write_new(witness / 'probe.py', (PROBES / 'probe.py').read_bytes())
    recorder = (PROBES / 'recorder.py').read_bytes()
    criteria = {}
    for condition in CONDITIONS:
        directory = witness / condition
        home = directory / 'home'
        envdir = home / '.config/striatum'
        envdir.mkdir(parents=True)
        for path in (home / '.npm-global/bin/python3', directory / 'fallback-bin/python3'):
            path.parent.mkdir(parents=True, exist_ok=True)
            write_new(path, recorder)
            path.chmod(0o500)
        has_zai = condition not in ('neither-file', 'openrouter-only')
        has_openrouter = condition not in ('neither-file', 'zai-only')
        if has_zai:
            write_new(envdir / 'zai.env', b"ZAI_API_KEY='synthetic zai token'\n")
        if has_openrouter:
            write_new(envdir / 'openrouter.env', b'if then\n' if condition == 'malformed-file' else b"OPENROUTER_API_KEY='synthetic openrouter token'\n")
        prefix = '/case/repo space' if condition == 'spaced-path' else '/case/repo'
        argv = [] if condition == 'missing-backend' else ['fixture-backend', '--attempts', '2', '--label', 'two words']
        criteria[condition] = {'prefix': prefix, 'arguments': argv,
            'dispatch_expected': condition not in ('missing-backend', 'malformed-file'),
            'downstream_exit': 17 if condition == 'downstream-failure' else 0,
            'zai': 'synthetic zai token' if has_zai else 'synthetic inherited zai',
            'openrouter': 'synthetic openrouter token' if has_openrouter else 'synthetic inherited openrouter'}
    write_json(witness / 'criteria.json', criteria)
    support = [Path(__file__), AUTH, PROBES / 'probe.py', PROBES / 'recorder.py',
        REPO / 'scripts/verify_reviewer_launcher_witness.py', REPO / 'scripts/reviewer_scheduler_witness.py',
        REPO / 'scripts/reviewer_reddit_recovery_witness.py', REPO / 'scripts/reviewer_timeout_witness.py',
        Path('/usr/bin/bash'), Path('/usr/bin/env'), Path('/usr/bin/mkdir'), Path('/usr/bin/dirname')]
    plan = {'schema': 'caplab.launcher-witness-plan/v1', 'commit': COMMIT, 'base': BASE,
        'tree': git('rev-parse', COMMIT + '^{tree}').decode().strip(), 'source_files': files,
        'base_launcher_absent': True, 'requirement_unchanged_from_base': True,
        'source_inventory': inventory(source), 'witness': inventory(witness), 'runtime': runtime(),
        'support': [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in support],
        'repetitions': 2, 'per_execution_seconds': 10, 'total_seconds': 300,
        'ranking_eligible': False, 'supervisor_or_native_execution': False}
    verify_inputs(plan)
    write_new(ROOT / 'runner.py', Path(__file__).read_bytes())
    write_json(ROOT / 'plan.json', plan)
    print(json.dumps({'root': str(ROOT), 'plan_sha256': sha((ROOT / 'plan.json').read_bytes())}))


def run(expected):
    if sha((ROOT / 'plan.json').read_bytes()) != expected or time.time() >= 1789084800:
        raise ValueError('plan mismatch or expired authorization')
    plan = json.loads((ROOT / 'plan.json').read_text())
    verify_inputs(plan)
    write_json(ROOT / 'run-started.json', {'plan_sha256': expected, 'time': time.time()})
    criteria = json.loads((ROOT / 'witness/criteria.json').read_text())
    failures = []
    start = time.monotonic()
    for repetition in (1, 2):
        for condition in CONDITIONS:
            name = f'{condition}-{repetition}'
            capture = ROOT / (name + '-capture')
            (capture / 'output').mkdir(parents=True)
            item = criteria[condition]
            prefix = item['prefix']
            command = namespace() + ['--dir', '/case', '--ro-bind', str(ROOT / 'source'), prefix,
                '--ro-bind', str(ROOT / 'witness'), '/witness', '--bind', str(capture), '/capture',
                '--bind', str(capture / 'output'), prefix + '/advisory',
                '--setenv', 'HOME', '/witness/' + condition + '/home',
                '--setenv', 'PATH', '/witness/' + condition + '/fallback-bin:/usr/bin:/bin',
                '--setenv', 'ZAI_API_KEY', 'synthetic inherited zai',
                '--setenv', 'OPENROUTER_API_KEY', 'synthetic inherited openrouter',
                '--setenv', 'WITNESS_EXIT', str(item['downstream_exit']),
                '--chdir', '/tmp', '--', '/usr/bin/python3', '-I', '-B', '/witness/probe.py',
                prefix + '/' + LAUNCHER, *item['arguments']]
            result = execute(ROOT / name, command, min(10, 300 - (time.monotonic() - start), 1789084800 - time.time()))
            write_json(ROOT / (name + '-inventory.json'), inventory(capture))
            if result['returncode'] or result['timed_out']:
                failures.append(name)
                break
        if failures:
            break
    verify_inputs(plan)
    write_json(ROOT / 'completion.json', {'plan_sha256': expected, 'failures': failures,
        'elapsed_seconds': time.monotonic() - start, 'ranking_eligible': False})
    print(json.dumps({'root': str(ROOT), 'failures': failures}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('prepare', 'run'))
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    os.umask(0o077)
    prepare() if args.operation == 'prepare' else run(args.plan_sha256)
