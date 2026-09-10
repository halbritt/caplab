"""Execute a real-duration recovery witness for the selected large change."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import ssl
import subprocess
import sys
import sysconfig
import time

from reviewer_scheduler_witness import execute, inventory, namespace
from reviewer_timeout_witness import sha, write_json, write_new

CAPLAB = Path(__file__).resolve().parents[1]
SOURCE = Path('/home/halbritt/git/ai-newsroom')
ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/reddit-recovery-witness-2')
PROBE = CAPLAB / 'docs/product/studies/reviewer-ranking-001/development-witnesses/reddit-recovery'
AUTH = CAPLAB / 'docs/records/authorization-2026-09-10-reviewer-reddit-recovery-witness-2.md'
COMMITS = {'base': '1bfe5a656bcb2c663891afd5f980211a3ef144a8', 'change': '544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f'}


def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(SOURCE), *args])


def materialize(role, commit):
    root = ROOT / role
    root.mkdir()
    files = []
    for row in git('ls-tree', '-rz', commit, '--', 'newsroom', 'config', 'README.md', 'pyproject.toml').split(b'\0'):
        if not row:
            continue
        header, name = row.split(b'\t', 1)
        mode, kind, blob = header.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('unsupported source entry')
        body = git('cat-file', 'blob', blob)
        if hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() != blob:
            raise ValueError('Git blob mismatch')
        path = root / name.decode()
        path.parent.mkdir(parents=True, exist_ok=True)
        write_new(path, body)
        path.chmod(0o500 if mode == '100755' else 0o400)
        files.append({'path': name.decode(), 'git_blob': blob, 'sha256': sha(body)})
    return {'commit': commit, 'tree': git('rev-parse', commit + '^{tree}').decode().strip(), 'files': files}


def runtime():
    paths = [Path('/usr/bin/python3').resolve(), Path('/usr/bin/bwrap'), Path('/usr/bin/openssl'),
             Path('/usr/lib/x86_64-linux-gnu/libssl.so.3'), Path('/usr/lib/x86_64-linux-gnu/libcrypto.so.3')]
    paths += [p for p in sorted(Path(sysconfig.get_path('stdlib')).rglob('*'))
              if p.is_file() and p.suffix in ('.py', '.so') and '__pycache__' not in p.parts]
    return [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in paths]


def verify_inputs(plan):
    if runtime() != plan['runtime'] or sys.version != plan['python_version'] or ssl.OPENSSL_VERSION != plan['ssl_version']:
        raise ValueError('runtime drift')
    if inventory(ROOT / 'witness') != plan['witness']:
        raise ValueError('witness drift')
    for row in plan['support']:
        if sha(Path(row['path']).read_bytes()) != row['sha256']:
            raise ValueError('administration or authorization drift')
    for role, snapshot in plan['snapshots'].items():
        if snapshot['commit'] != COMMITS[role] or {r['path'] for r in inventory(ROOT / role)} != {r['path'] for r in snapshot['files']}:
            raise ValueError('source identity or membership drift')
        for row in snapshot['files']:
            if sha((ROOT / role / row['path']).read_bytes()) != row['sha256']:
                raise ValueError('source bytes changed')


def prepare():
    if sys.version_info[:2] != (3, 12) or time.time() >= 1789084800:
        raise ValueError('runtime or authorization outside scope')
    ROOT.mkdir(mode=0o700)
    (ROOT / 'witness').mkdir()
    for name in ('probe.py', 'feed.xml'):
        write_new(ROOT / 'witness' / name, (PROBE / name).read_bytes())
    write_new(ROOT / 'witness/hosts', b'127.0.0.1 localhost www.reddit.com\n')
    write_new(ROOT / 'witness/nsswitch.conf', b'hosts: files\n')
    result = execute(ROOT / 'certificate', ['/usr/bin/openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
        '-keyout', str(ROOT / 'witness/key.pem'), '-out', str(ROOT / 'witness/cert.pem'), '-days', '2',
        '-subj', '/CN=www.reddit.com', '-addext', 'subjectAltName=DNS:www.reddit.com'], 15)
    if result['returncode'] or result['timed_out']:
        raise RuntimeError('test certificate setup failed')
    write_json(ROOT / 'witness/criteria.json', {'conditions': ['ordinary', 'drip'], 'drip_seconds': 190,
        'recovery_seconds': 180, 'timing_tolerance_seconds': 2, 'socket_timeout_seconds': 30,
        'expected_urls': ['https://www.reddit.com/r/MachineLearning/comments/fresh/model/'],
        'properties': ['Ordinary harvest succeeds, filters stale/future posts and persists the fresh candidate.',
                       'A refresh stops within its 180-second recovery budget, including an active response body.',
                       'The drip response is valid Atom with byte gaps below the unchanged socket timeout.',
                       'Fresh adapter reads the persisted pool without another HTTP request.'],
        'limits': ['One part of a selected large change, not full-change verification or a whole-patch clean label.',
                   'New provider module absent in base; no comparable base execution is fabricated.',
                   'No real Reddit, model or Slack call, no case admission or ranking.']})
    snapshots = {role: materialize(role, commit) for role, commit in COMMITS.items()}
    if (ROOT / 'base/newsroom/sources/reddit_state.py').exists():
        raise ValueError('assumed introduction is not new')
    support = [Path(__file__), AUTH, PROBE / 'probe.py', PROBE / 'feed.xml',
               CAPLAB / 'scripts/reviewer_scheduler_witness.py', CAPLAB / 'scripts/reviewer_timeout_witness.py']
    plan = {'schema': 'caplab.reddit-recovery-plan/v1', 'snapshots': snapshots, 'runtime': runtime(),
        'python_version': sys.version, 'ssl_version': ssl.OPENSSL_VERSION, 'witness': inventory(ROOT / 'witness'),
        'support': [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in support],
        'repetitions': 2, 'execution_seconds': 215, 'total_seconds': 500, 'ranking_eligible': False}
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
    start, failures = time.monotonic(), []
    for repetition in (1, 2):
        for condition in ('ordinary', 'drip'):
            name = f'{condition}-{repetition}'
            capture = ROOT / (name + '-capture')
            capture.mkdir()
            command = namespace() + ['--uid', '0', '--gid', '0', '--cap-drop', 'ALL', '--cap-add', 'CAP_NET_BIND_SERVICE',
                '--ro-bind', str(ROOT / 'change'), '/source',
                '--ro-bind', str(ROOT / 'witness'), '/witness', '--bind', str(capture), '/capture',
                '--ro-bind', str(ROOT / 'witness/hosts'), '/etc/hosts',
                '--ro-bind', str(ROOT / 'witness/nsswitch.conf'), '/etc/nsswitch.conf',
                '--setenv', 'SSL_CERT_FILE', '/witness/cert.pem', '--chdir', '/source',
                '--', '/usr/bin/python3', '-I', '-B', '/witness/probe.py', condition]
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
    print(json.dumps({'root': str(ROOT), 'failures': failures}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('prepare', 'run'))
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    os.umask(0o077)
    prepare() if args.operation == 'prepare' else run(args.plan_sha256)
