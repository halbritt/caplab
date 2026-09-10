"""Preserve a selected date repair and run real RSS producer/consumer witnesses."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
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
SOURCE = Path('/home/halbritt/git/ai-newsroom')
ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/publication-witness-1')
PROBES = CAPLAB / 'docs/product/studies/reviewer-ranking-001/development-witnesses/newsroom-publication'
AUTH = CAPLAB / 'docs/records/authorization-2026-09-10-reviewer-publication-witness.md'
BLOGWATCHER = Path('/usr/local/bin/blogwatcher')
COMMITS = {'base': '00efadb0c5bdd2fc6d939793e7d372bf3c69ea73', 'repair': 'e4d5293910614ead24a9f7599f7d12050d5c64cf'}


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
            raise ValueError('source blob mismatch')
        path = root / name.decode()
        path.parent.mkdir(parents=True, exist_ok=True)
        write_new(path, body)
        path.chmod(0o500 if mode == '100755' else 0o400)
        files.append({'path': name.decode(), 'git_blob': blob, 'mode': mode, 'sha256': sha(body)})
    return {'commit': commit, 'parent': git('rev-parse', commit + '^').decode().strip(),
            'tree': git('rev-parse', commit + '^{tree}').decode().strip(), 'files': files}


def runtime():
    paths = [Path('/usr/bin/python3').resolve(), Path('/usr/bin/bwrap'), BLOGWATCHER]
    paths += [p for p in sorted(Path(sysconfig.get_path('stdlib')).rglob('*'))
              if p.is_file() and p.suffix in ('.py', '.so') and '__pycache__' not in p.parts]
    return [{'path': str(path), 'sha256': sha(path.read_bytes())} for path in paths]


def verify_inputs(plan):
    if sys.version != plan['python_version'] or runtime() != plan['runtime']:
        raise ValueError('runtime drift')
    if inventory(ROOT / 'witness') != plan['witness']:
        raise ValueError('fixture or criteria drift')
    for row in plan['support']:
        if sha(Path(row['path']).read_bytes()) != row['sha256']:
            raise ValueError('administration code or authorization drift')
    for role, snapshot in plan['snapshots'].items():
        if snapshot['commit'] != COMMITS[role]:
            raise ValueError('source revision mismatch')
        observed = inventory(ROOT / role)
        if {r['path'] for r in observed} != {r['path'] for r in snapshot['files']}:
            raise ValueError('source membership drift')
        for row in snapshot['files']:
            if sha((ROOT / role / row['path']).read_bytes()) != row['sha256']:
                raise ValueError('historical source drift')


def prepare():
    if sys.version_info[:2] != (3, 12) or datetime.now(timezone.utc).date().isoformat() != '2026-09-10':
        raise ValueError('runtime or date outside authorization')
    ROOT.mkdir(mode=0o700)
    (ROOT / 'witness').mkdir()
    for name in ('probe.py', 'feed.xml'):
        write_new(ROOT / 'witness' / name, (PROBES / name).read_bytes())
    write_new(ROOT / 'witness/blogwatcher-build.txt', subprocess.check_output(
        ['/home/halbritt/.local/go/bin/go', 'version', '-m', str(BLOGWATCHER)]))
    write_new(ROOT / 'witness/blogwatcher-version.txt', subprocess.check_output([str(BLOGWATCHER), '--version']))
    write_json(ROOT / 'witness/criteria.json', {
        'schema': 'caplab.publication-criteria/v1', 'window_hours': 24, 'utc_date': '2026-09-10',
        'producer_entries': ['today', 'yesterday-early', 'yesterday-late', 'stale', 'future', 'undated', 'non-ai'],
        'known_dates': {'today': '2026-09-10', 'yesterday-early': '2026-09-09', 'yesterday-late': '2026-09-09',
                        'stale': '2026-09-01', 'future': '2026-09-11', 'non-ai': '2026-09-10'},
        'expected_rss_candidates': ['today', 'undated', 'yesterday-early', 'yesterday-late'],
        'instant_kept': {'stale': False, 'inside': True, 'future': False, 'offset-inside': True},
        'expected_paths': {'default': '/home/witness/.local/share/ai-newsroom',
                           'xdg': '/home/witness/.cache/publication-xdg/ai-newsroom',
                           'explicit': '/home/witness/publication-history'},
        'properties': ['Real producer must retain all seven input article identities before consumer measurements.',
                       'Known displayed calendar dates remain available without invented publication instants.',
                       'Known days outside the window are excluded; overlapping calendar days and unknown dates remain candidates.',
                       'Timezone rendering must identify the same instant as the original aware datetime.',
                       'Preview fetch leaves all producer items unread.',
                       'Configured tilde history paths resolve under the private home.'],
        'limits': ['Pinned installed producer reports modified source; no verified historical deployed-binary identity.',
                   'No editor/model execution or freshness judgment on unknown dates.',
                   'Date-overlap candidates are not proof of exact publication within the 24-hour window.',
                   'Development evidence only; no case admission, scorer acceptance or reviewer ranking.']})
    snapshots = {role: materialize(role, commit) for role, commit in COMMITS.items()}
    support = [Path(__file__), AUTH, PROBES / 'probe.py', PROBES / 'feed.xml',
               CAPLAB / 'scripts/reviewer_scheduler_witness.py', CAPLAB / 'scripts/reviewer_timeout_witness.py']
    plan = {'schema': 'caplab.publication-plan/v1', 'snapshots': snapshots, 'runtime': runtime(),
            'python_version': sys.version, 'witness': inventory(ROOT / 'witness'),
            'support': [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in support],
            'repetitions': 2, 'execution_seconds': 60, 'total_seconds': 240, 'ranking_eligible': False}
    verify_inputs(plan)
    write_new(ROOT / 'runner.py', Path(__file__).read_bytes())
    write_json(ROOT / 'plan.json', plan)
    print(json.dumps({'root': str(ROOT), 'plan_sha256': sha((ROOT / 'plan.json').read_bytes())}))


def run(expected):
    if sha((ROOT / 'plan.json').read_bytes()) != expected or time.time() >= 1789084800:
        raise ValueError('plan mismatch or authorization expired')
    plan = json.loads((ROOT / 'plan.json').read_text())
    verify_inputs(plan)
    write_json(ROOT / 'run-started.json', {'plan_sha256': expected, 'time': time.time()})
    start, failures = time.monotonic(), []
    for role in COMMITS:
        for repetition in range(1, plan['repetitions'] + 1):
            name = f'{role}-{repetition}'
            capture = ROOT / (name + '-capture')
            capture.mkdir()
            (capture / 'home').mkdir()
            (capture / 'work').mkdir()
            command = namespace() + ['--ro-bind', str(ROOT / role), '/source',
                '--ro-bind', str(ROOT / 'witness'), '/witness', '--bind', str(capture), '/capture',
                '--bind', str(capture / 'home'), '/home/witness', '--chdir', '/capture/work',
                '--setenv', 'PATH', '/usr/local/bin:/usr/bin:/bin', '--', '/usr/bin/python3', '-I', '-B', '/witness/probe.py']
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
