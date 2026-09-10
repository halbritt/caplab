"""Compare original Go formatting and execute the unchanged affected tests."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import reviewer_scheduler_witness as scheduler
from reviewer_timeout_witness import sha, write_json, write_new

REPO = Path(__file__).resolve().parents[1]
SOURCE = Path('/home/halbritt/git/striatum-next')
ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/formatting-witness-1')
COMMITS = {'base': '03f0cc39b02c7882674ca2706398560e986b1032',
           'change': '98759de9d5f1bfa855cc8d7ff43456be243db7db'}
TARGET = 'internal/scheduler/glm_activation_test.go'
TESTS = ['TestRepositoryGLMReviewDeactivationContract', 'TestClaudeHarmFamilyTracksExactAvailabilityPosture']
AUTH = REPO / 'docs/records/authorization-2026-09-10-reviewer-formatting-witness.md'


def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(SOURCE), *args])


def materialize(role, commit):
    destination = ROOT / role
    destination.mkdir()
    files = []
    for row in git('ls-tree', '-rz', commit, '--', 'internal', 'backends', 'policy', 'go.mod', 'go.sum', 'Makefile').split(b'\0'):
        if not row:
            continue
        header, name = row.split(b'\t', 1)
        mode, kind, blob = header.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('unsupported source member')
        body = git('cat-file', 'blob', blob)
        if hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() != blob:
            raise ValueError('Git blob mismatch')
        path = destination / name.decode()
        path.parent.mkdir(parents=True, exist_ok=True)
        write_new(path, body)
        path.chmod(0o500 if mode == '100755' else 0o400)
        files.append({'path': name.decode(), 'mode': mode, 'git_blob': blob, 'sha256': sha(body)})
    return {'commit': commit, 'tree': git('rev-parse', commit + '^{tree}').decode().strip(), 'files': files}


def verify_inputs(plan):
    if scheduler.inventory(scheduler.GO) != plan['toolchain'] or scheduler.dependencies() != plan['dependencies']:
        raise ValueError('toolchain or locked dependency drift')
    for role in COMMITS:
        if scheduler.inventory(ROOT / role) != plan['source_inventories'][role]:
            raise ValueError('original source drift')
    for entry in plan['support']:
        if sha(Path(entry['path']).read_bytes()) != entry['sha256']:
            raise ValueError('support drift')


def prepare():
    if time.time() >= 1789084800:
        raise ValueError('authorization expired')
    ROOT.mkdir(mode=0o700)
    snapshots = {role: materialize(role, commit) for role, commit in COMMITS.items()}
    if git('rev-parse', COMMITS['change'] + '^').decode().strip() != COMMITS['base']:
        raise ValueError('base mismatch')
    paths = git('diff', '--name-only', '-z', COMMITS['base'], COMMITS['change']).decode().split('\0')[:-1]
    if paths != [TARGET]:
        raise ValueError('change is not confined to the named original file')
    write_new(ROOT / 'change.diff', git('diff', COMMITS['base'], COMMITS['change']))
    support = [Path(__file__), AUTH, REPO / 'scripts/verify_reviewer_formatting_witness.py',
               REPO / 'scripts/reviewer_scheduler_witness.py', REPO / 'scripts/reviewer_timeout_witness.py', Path('/usr/bin/bwrap')]
    version = subprocess.check_output([str(scheduler.GO / 'bin/go'), 'version']).decode().strip()
    if version != 'go version go1.23.4 linux/amd64':
        raise ValueError('unexpected Go version')
    plan = {'schema': 'caplab.formatting-witness-plan/v1', 'snapshots': snapshots,
        'source_inventories': {role: scheduler.inventory(ROOT / role) for role in COMMITS},
        'changed_paths': paths, 'diff_sha256': sha((ROOT / 'change.diff').read_bytes()),
        'go_version': version, 'toolchain': scheduler.inventory(scheduler.GO), 'dependencies': scheduler.dependencies(),
        'support': [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in support],
        'tests': TESTS, 'repetitions': 2, 'build_seconds': 240, 'execution_seconds': 60,
        'total_seconds': 900, 'ranking_eligible': False,
        'criteria': ['Only the named file changes in the complete Git diff.',
                     'Canonical gofmt output is identical across the two original files; the changed file equals that output.',
                     'Both original named tests run and pass without skips in each original tree, twice.',
                     'Historical declaration assertions are not current capability evidence.']}
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
    (ROOT / 'cache').mkdir()
    (ROOT / 'builds').mkdir()
    start, failures = time.monotonic(), []

    def remaining(limit):
        seconds = min(limit, 900 - (time.monotonic() - start), 1789084800 - time.time())
        if seconds <= 0:
            raise RuntimeError('execution deadline expired')
        return seconds

    for role in COMMITS:
        prefix = scheduler.namespace() + ['--ro-bind', str(scheduler.GO), '/go',
                  '--ro-bind', str(ROOT / role), '/source', '--chdir', '/source/internal/scheduler']
        result = scheduler.execute(ROOT / (role + '-format'), prefix + ['--', '/go/bin/gofmt', '/source/' + TARGET], remaining(10))
        if result['returncode'] or result['timed_out']:
            failures.append(role + '-format')
            break
        build = ROOT / 'builds' / role
        build.mkdir()
        command = prefix + ['--bind', str(ROOT / 'cache'), '/cache', '--bind', str(build), '/output']
        for dep in plan['dependencies']:
            command += ['--ro-bind', dep['source'], dep['destination']]
        for key, value in {'GOROOT': '/go', 'GOMODCACHE': '/gomod', 'GOCACHE': '/cache', 'GOPROXY': 'off',
                           'GOSUMDB': 'off', 'GOTOOLCHAIN': 'local', 'GOENV': 'off', 'GOWORK': 'off',
                           'CGO_ENABLED': '0', 'GOTELEMETRY': 'off'}.items():
            command += ['--setenv', key, value]
        command += ['--', '/go/bin/go', 'test', '-c', '-vet=off', '-mod=readonly', '-trimpath', '-o', '/output/tests', '.']
        result = scheduler.execute(ROOT / (role + '-compile'), command, remaining(240))
        if result['returncode'] or result['timed_out']:
            failures.append(role + '-compile')
            break
        binary_hash = sha((build / 'tests').read_bytes())
        write_json(build / 'binary.json', {'sha256': binary_hash})
        for repetition in (1, 2):
            name = f'{role}-test-{repetition}'
            command = prefix + ['--ro-bind', str(build / 'tests'), '/tests', '--', '/tests',
                '-test.run=^(' + '|'.join(TESTS) + ')$', '-test.v', '-test.count=1', '-test.timeout=45s']
            result = scheduler.execute(ROOT / name, command, remaining(60))
            if sha((build / 'tests').read_bytes()) != binary_hash:
                raise ValueError('compiled binary drift')
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
