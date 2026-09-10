"""Compile pinned historical scheduler packages and run local record witnesses."""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import tarfile
import time

from reviewer_timeout_witness import sha, write_json, write_new

REPO = Path('/home/halbritt/git/striatum-next')
CAPLAB = Path(__file__).resolve().parents[1]
GO = Path('/home/halbritt/.local/go')
MODULES = Path('/home/halbritt/go/pkg/mod')
PROBE = CAPLAB / 'docs/product/studies/reviewer-ranking-001/development-witnesses/striatum-scheduler/probe.go'
COMMITS = {
    'precursor': '58ff7ce58e58b0cd5ea7719c5826fa3716bfbb68',
    'partial': '147775a0047a1219e241ae4798813a50b35f32fc',
    'base': '0a7aa730f164e98a705dfe27c5db2ec8f20cc8a5',
    'repair': 'b9325d547fa8fc4f8df38ddef274ca9eae6a95f4',
}
DEPS = [('gopkg.in/yaml.v3', 'v3.0.1'), ('github.com/klauspost/compress', 'v1.17.11'),
        ('gopkg.in/check.v1', 'v0.0.0-20161208181325-20d25e280405')]
CONDITIONS = ['ordinary-local', 'local-unrelated-active', 'exhausted-fallback-local', 'supervised-failover',
              'all-supervised-exhausted', 'expired-observation', 'malformed-observation']


def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(REPO), *args])


def inventory(root: Path) -> list[dict]:
    result = []
    for path in sorted(root.rglob('*')):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            if not path.resolve().is_relative_to(root.resolve()):
                raise ValueError('inventory symlink escapes root')
            result.append({'path': relative, 'symlink': os.readlink(path)})
        elif path.is_file():
            result.append({'path': relative, 'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes())})
    return result


def dependencies() -> list[dict]:
    result = []
    for module, version in DEPS:
        directory = MODULES / (module + '@' + version)
        cache = MODULES / 'cache/download' / module / '@v'
        result.append({'source': str(directory), 'destination': '/gomod/' + module + '@' + version,
                       'files': inventory(directory)})
        if not result[-1]['files']:
            raise ValueError('required cached dependency missing')
        for suffix in ('mod', 'info', 'zip', 'ziphash'):
            path = cache / (version + '.' + suffix)
            result.append({'source': str(path), 'destination': '/gomod/' + str(path.relative_to(MODULES)),
                           'sha256': sha(path.read_bytes())})
    return result


def materialize(destination: Path, commit: str) -> dict:
    import hashlib
    entries = {}
    for row in git('ls-tree', '-rz', commit).split(b'\0'):
        if row:
            header, name = row.split(b'\t', 1)
            mode, kind, blob = header.decode().split()
            entries[name.decode()] = {'mode': mode, 'kind': kind, 'git_blob': blob}
    destination.mkdir(mode=0o700)
    retained, omitted = [], []
    with tarfile.open(fileobj=io.BytesIO(git('archive', '--format=tar', commit))) as archive:
        for member in archive:
            if member.isdir():
                continue
            name = member.name
            if Path(name).is_absolute() or '..' in Path(name).parts or name not in entries:
                raise ValueError('unexpected archive path')
            entry = entries.pop(name)
            if member.issym() and name == 'CLAUDE.md' and entry['mode'] == '120000':
                payload = member.linkname.encode()
                omitted.append({'path': name, **entry, 'target': member.linkname, 'sha256': sha(payload)})
            elif member.isfile() and entry['mode'] in ('100644', '100755'):
                payload = archive.extractfile(member).read()
                path = destination / name
                path.parent.mkdir(parents=True, exist_ok=True)
                write_new(path, payload)
                path.chmod(0o500 if entry['mode'] == '100755' else 0o400)
                retained.append({'path': name, **entry, 'bytes': len(payload), 'sha256': sha(payload)})
            else:
                raise ValueError('unsupported historical tree entry')
            identity = hashlib.sha1(b'blob ' + str(len(payload)).encode() + b'\0' + payload).hexdigest()
            if identity != entry['git_blob']:
                raise ValueError('original blob mismatch')
    if entries:
        raise ValueError('archive omitted tracked content')
    (destination / 'caplab-probe').mkdir()
    return {'commit': commit, 'parent': git('rev-parse', commit + '^').decode().strip(),
            'tree': git('rev-parse', commit + '^{tree}').decode().strip(),
            'files': retained, 'omitted_symlinks': omitted}


def prepare(root: Path) -> None:
    root.mkdir(mode=0o700)
    (root / 'witness').mkdir()
    write_new(root / 'witness/probe.go', PROBE.read_bytes())
    snapshots = {role: materialize(root / role, commit) for role, commit in COMMITS.items()}
    criteria = {
        'conditions': CONDITIONS, 'repetitions': 2,
        'properties': ['Valid scenarios evaluate and choose the eligible backend, or explicitly defer when all supervised candidates are exhausted.',
                       'DecisionSchemaVersion agrees with Evaluate for fixed input.',
                       'The stamped original record encoder and decoder accept the evaluation payload.',
                       'A capacity observation that changes the selected backend is represented in the complete durable input preimage.',
                       'Repeated identical executions preserve the complete observation bytes. Malformed observations are rejected.'],
        'expected_selected': {'ordinary-local': ['local'], 'local-unrelated-active': ['local'],
                              'exhausted-fallback-local': ['local'], 'supervised-failover': ['survivor'],
                              'all-supervised-exhausted': [], 'expired-observation': ['local']},
        'hypotheses': {'precursor': 'active observations can demand an unencodable supervised binding shape for local placement',
                       'partial_and_base': 'local active-observation evaluation can be v2 while the envelope prediction remains v5',
                       'repair': 'version agreement may restore serialization while dropping observation inputs needed to explain fallback'},
        'scope': 'Record boundary and counterfactual placement only; no production driver, full graph recovery, source acceptance or ranking.',
    }
    write_json(root / 'criteria.json', criteria)
    plan = {'schema': 'caplab.scheduler-witness-plan/v1', 'snapshots': snapshots,
            'criteria_sha256': sha((root / 'criteria.json').read_bytes()), 'probe_sha256': sha(PROBE.read_bytes()),
            'go_version': subprocess.check_output([str(GO / 'bin/go'), 'version']).decode().strip(),
            'toolchain': inventory(GO), 'dependencies': dependencies(),
            'bwrap_sha256': sha(Path('/usr/bin/bwrap').read_bytes()),
            'authorization_sha256': sha((CAPLAB / 'docs/records/authorization-2026-09-10-reviewer-scheduler-witness-2.md').read_bytes()),
            'runner_sha256': sha(Path(__file__).read_bytes()), 'build_seconds': 180, 'execution_seconds': 30,
            'total_seconds': 900, 'repetitions': 2, 'ranking_eligible': False}
    if plan['go_version'] != 'go version go1.23.4 linux/amd64':
        raise ValueError('unauthorized toolchain version')
    write_new(root / 'runner.py', Path(__file__).read_bytes())
    write_json(root / 'plan.json', plan)
    print(json.dumps({'custody': str(root), 'plan_sha256': sha((root / 'plan.json').read_bytes())}))


def verify_inputs(root, plan):
    if (sha((root / 'criteria.json').read_bytes()) != plan['criteria_sha256']
            or sha((root / 'witness/probe.go').read_bytes()) != plan['probe_sha256']
            or sha(Path(__file__).read_bytes()) != plan['runner_sha256']
            or sha(Path('/usr/bin/bwrap').read_bytes()) != plan['bwrap_sha256']
            or inventory(GO) != plan['toolchain'] or dependencies() != plan['dependencies']):
        raise ValueError('witness, runtime or dependency drift')
    for role, snapshot in plan['snapshots'].items():
        if snapshot['commit'] != COMMITS[role]:
            raise ValueError('unauthorized snapshot')
        for row in snapshot['files']:
            if sha((root / role / row['path']).read_bytes()) != row['sha256']:
                raise ValueError('source drift')


def namespace():
    return ['/usr/bin/bwrap', '--die-with-parent', '--unshare-all', '--new-session',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64',
            '--symlink', 'usr/bin', '/bin', '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
            '--dir', '/home/witness', '--clearenv', '--setenv', 'HOME', '/home/witness',
            '--setenv', 'PATH', '/go/bin:/usr/bin:/bin']


def execute(slot, command, seconds):
    slot.mkdir(mode=0o700)
    write_json(slot / 'launch.json', {'command': command, 'timeout_seconds': seconds, 'started_at': time.time()})
    start = time.monotonic()
    with (slot / 'stdout').open('xb') as out, (slot / 'stderr').open('xb') as err:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
        timed_out = False
        try:
            process.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=10)
    result = {'returncode': process.returncode, 'timed_out': timed_out, 'elapsed_seconds': time.monotonic() - start,
              'stdout_sha256': sha((slot / 'stdout').read_bytes()), 'stderr_sha256': sha((slot / 'stderr').read_bytes())}
    write_json(slot / 'completion.json', result)
    return result


def run(root, expected):
    if sha((root / 'plan.json').read_bytes()) != expected:
        raise ValueError('plan mismatch')
    plan = json.loads((root / 'plan.json').read_text())
    if time.time() >= 1789084800:
        raise ValueError('authorization expired')
    verify_inputs(root, plan)
    write_json(root / 'run-started.json', {'plan_sha256': expected, 'time': time.time()})
    start = time.monotonic()
    (root / 'build-cache').mkdir()
    (root / 'builds').mkdir()
    failures = []
    for role in COMMITS:
        if time.monotonic() - start >= plan['total_seconds']:
            raise RuntimeError('total budget exhausted')
        output = root / 'builds' / role
        output.mkdir()
        build = namespace() + ['--ro-bind', str(GO), '/go', '--ro-bind', str(root / role), '/source',
            '--ro-bind', str(root / 'witness'), '/source/caplab-probe',
            '--bind', str(root / 'build-cache'), '/cache', '--bind', str(output), '/output', '--chdir', '/source']
        for dep in plan['dependencies']:
            build += ['--ro-bind', dep['source'], dep['destination']]
        for key, value in {'GOROOT': '/go', 'GOMODCACHE': '/gomod', 'GOCACHE': '/cache', 'GOPROXY': 'off',
                           'GOSUMDB': 'off', 'GOTOOLCHAIN': 'local', 'GOENV': 'off', 'GOWORK': 'off',
                           'CGO_ENABLED': '0', 'GOTELEMETRY': 'off'}.items():
            build += ['--setenv', key, value]
        commands = [('verify-modules', ['/go/bin/go', 'mod', 'verify']),
                    ('compile', ['/go/bin/go', 'build', '-mod=readonly', '-trimpath', '-o', '/output/probe', './caplab-probe'])]
        ready = True
        role_start = time.monotonic()
        for name, suffix in commands:
            result = execute(root / f'{role}-{name}', build + ['--', *suffix],
                             max(1, min(180 - (time.monotonic() - role_start), 900 - (time.monotonic() - start))))
            if result['returncode'] or result['timed_out']:
                failures.append({'role': role, 'phase': name})
                ready = False
                break
        if not ready:
            continue
        binary_hash = sha((output / 'probe').read_bytes())
        for repetition in (1, 2):
            if sha((output / 'probe').read_bytes()) != binary_hash:
                raise ValueError('built binary drift')
            command = namespace() + ['--ro-bind', str(output / 'probe'), '/probe', '--chdir', '/tmp', '--', '/probe']
            result = execute(root / f'{role}-execution-{repetition}', command,
                             max(1, min(30, 900 - (time.monotonic() - start))))
            if result['returncode'] or result['timed_out']:
                failures.append({'role': role, 'phase': f'execution-{repetition}'})
        write_json(output / 'binary.json', {'sha256': binary_hash})
    verify_inputs(root, plan)
    write_json(root / 'completion.json', {'plan_sha256': expected, 'elapsed_seconds': time.monotonic() - start,
                                        'failures': failures, 'inputs_rechecked': True, 'ranking_eligible': False})
    print(json.dumps({'custody': str(root), 'failures': failures}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('prepare', 'run'))
    parser.add_argument('root', type=Path)
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    os.umask(0o077)
    prepare(args.root) if args.operation == 'prepare' else run(args.root, args.plan_sha256)
